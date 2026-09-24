# SILVER -> GOLD (flat table format, NO payload struct) -> REDSHIFT (COPY + upsert)
# Silver job stays as-is. This replaces the payload-style gold job for Redshift loading.
import sys, json, re, time, boto3
from urllib.parse import urlparse
from datetime import datetime

from awsglue.utils import getResolvedOptions
from pyspark.sql import SparkSession, Window
from pyspark.sql.functions import (
    col, lit, from_json, coalesce, when, substring, octet_length,
    to_json, base64, row_number, desc
)
from pyspark.sql.types import *

REQUIRED = ["JOB_NAME", "TABLE_NAME", "GLOBAL_CONFIG_PATH", "RUN_DATE",
            "REDSHIFT_DATABASE", "REDSHIFT_SCHEMA", "REDSHIFT_IAM_ROLE"]
# Serverless -> REDSHIFT_WORKGROUP ; Provisioned -> REDSHIFT_CLUSTER_ID + (REDSHIFT_DB_USER or REDSHIFT_SECRET_ARN)
OPTIONAL = ["REDSHIFT_WORKGROUP", "REDSHIFT_CLUSTER_ID", "REDSHIFT_DB_USER",
            "REDSHIFT_SECRET_ARN", "GOLD_TABLE_PREFIX", "PRIMARY_KEY",
            "ORDER_COL", "LOAD_REDSHIFT"]

VARCHAR_MAX = 65535  # Redshift VARCHAR limit in BYTES


def log(m):
    print(f"[GOLD-TABLE] {m}", flush=True)


def get_args():
    present = [k for k in OPTIONAL if f"--{k}" in sys.argv]
    args = getResolvedOptions(sys.argv, REQUIRED + present)
    for k in OPTIONAL:
        args.setdefault(k, None)
    return args


def load_json(s3, path):
    p = urlparse(path)
    return json.loads(s3.get_object(Bucket=p.netloc, Key=p.path.lstrip("/"))["Body"].read())


def s3_exists(s3, bucket, prefix):
    return "Contents" in s3.list_objects_v2(Bucket=bucket, Prefix=prefix, MaxKeys=1)


def clean_name(c):
    n = re.sub(r"[^a-z0-9_]", "_", c.lower())
    if not n or n[0].isdigit():
        n = "_" + n
    return n[:127]


def rs_type(t):
    if isinstance(t, StringType):    return f"VARCHAR({VARCHAR_MAX})"
    if isinstance(t, IntegerType):   return "INTEGER"
    if isinstance(t, LongType):      return "BIGINT"
    if isinstance(t, DoubleType):    return "DOUBLE PRECISION"
    if isinstance(t, FloatType):     return "REAL"
    if isinstance(t, BooleanType):   return "BOOLEAN"
    if isinstance(t, DateType):      return "DATE"
    if isinstance(t, DecimalType):   return f"DECIMAL({t.precision},{t.scale})"
    if isinstance(t, TimestampType) or t.typeName() == "timestamp_ntz":
        return "TIMESTAMP"
    return f"VARCHAR({VARCHAR_MAX})"


def cap_bytes(c):
    # keep each string <= 65535 bytes (UTF-8 can be up to 4 bytes/char)
    return (when(octet_length(c) <= VARCHAR_MAX, c)
            .when(octet_length(substring(c, 1, VARCHAR_MAX)) <= VARCHAR_MAX, substring(c, 1, VARCHAR_MAX))
            .when(octet_length(substring(c, 1, 32767)) <= VARCHAR_MAX, substring(c, 1, 32767))
            .otherwise(substring(c, 1, 16383)))


def make_redshift_safe(df):
    """Clean column names + convert every column to a Redshift-COPY-compatible type.
    Returns (df, [(col_name, redshift_type), ...]) in file column order."""
    seen, exprs, cols = set(), [], []
    for f in df.schema.fields:
        name = clean_name(f.name)
        base, i = name, 1
        while name in seen:
            name = f"{base[:120]}_{i}"; i += 1
        seen.add(name)

        t, c = f.dataType, col(f"`{f.name}`")
        if isinstance(t, (StructType, ArrayType, MapType)):
            c, t = to_json(c), StringType()
        elif isinstance(t, BinaryType):
            c, t = base64(c), StringType()
        elif isinstance(t, NullType):
            c, t = c.cast("string"), StringType()
        elif isinstance(t, (ByteType, ShortType)):
            c, t = c.cast("int"), IntegerType()
        elif isinstance(t, DecimalType) and t.precision > 38:
            c, t = c.cast("double"), DoubleType()
        if isinstance(t, StringType):
            c = cap_bytes(c)
        exprs.append(c.alias(name))
        cols.append((name, rs_type(t)))
    return df.select(*exprs), cols


# ----------------------------------------------------------
# Redshift Data API
# ----------------------------------------------------------
class Redshift:
    def __init__(self, args):
        self.client = boto3.client("redshift-data")
        self.kw = {"Database": args["REDSHIFT_DATABASE"]}
        if args["REDSHIFT_WORKGROUP"]:
            self.kw["WorkgroupName"] = args["REDSHIFT_WORKGROUP"]
        else:
            self.kw["ClusterIdentifier"] = args["REDSHIFT_CLUSTER_ID"]
            if args["REDSHIFT_SECRET_ARN"]:
                self.kw["SecretArn"] = args["REDSHIFT_SECRET_ARN"]
            else:
                self.kw["DbUser"] = args["REDSHIFT_DB_USER"]
        if args["REDSHIFT_SECRET_ARN"] and "SecretArn" not in self.kw:
            self.kw["SecretArn"] = args["REDSHIFT_SECRET_ARN"]

    def _wait(self, sid, timeout=3600):
        start = time.time()
        while True:
            d = self.client.describe_statement(Id=sid)
            if d["Status"] == "FINISHED":
                return d
            if d["Status"] in ("FAILED", "ABORTED"):
                raise Exception(f"Redshift statement {d['Status']}: {d.get('Error')}")
            if time.time() - start > timeout:
                raise Exception("Redshift statement timeout")
            time.sleep(3)

    def run(self, sql):
        log(f"SQL: {sql[:300]}")
        return self._wait(self.client.execute_statement(Sql=sql, **self.kw)["Id"])

    def run_tx(self, sqls):
        """All statements in ONE session + ONE transaction."""
        for s in sqls:
            log(f"TX SQL: {s[:300]}")
        return self._wait(self.client.batch_execute_statement(Sqls=sqls, **self.kw)["Id"])

    def query(self, sql):
        sid = self.client.execute_statement(Sql=sql, **self.kw)["Id"]
        d = self._wait(sid)
        if not d.get("HasResultSet"):
            return []
        rows, token = [], None
        while True:
            r = self.client.get_statement_result(Id=sid, **({"NextToken": token} if token else {}))
            rows += [[list(v.values())[0] for v in rec] for rec in r["Records"]]
            token = r.get("NextToken")
            if not token:
                return rows


def load_to_redshift(rs, schema, table, cols, s3_day_path, iam_role, pk, order_col):
    q = lambda n: f'"{n}"'
    target = f"{q(schema)}.{q(table)}"
    ddl = ", ".join(f"{q(n)} {t}" for n, t in cols)

    rs.run(f"CREATE SCHEMA IF NOT EXISTS {q(schema)}")
    rs.run(f"CREATE TABLE IF NOT EXISTS {target} ({ddl})")

    # schema evolution: add new columns coming from ServiceNow
    existing = {r[0] for r in rs.query(
        f"SELECT column_name FROM information_schema.columns "
        f"WHERE table_schema = '{schema}' AND table_name = '{table}'")}
    for n, t in cols:
        if n not in existing:
            rs.run(f"ALTER TABLE {target} ADD COLUMN {q(n)} {t}")

    col_list = ", ".join(q(n) for n, _ in cols)
    stage = f"stg_{table}"[:127]
    sqls = [
        f"CREATE TEMP TABLE {q(stage)} ({ddl})",
        # Parquet COPY maps by column POSITION -> stage has exact file column order
        f"COPY {q(stage)} FROM '{s3_day_path}' IAM_ROLE '{iam_role}' FORMAT AS PARQUET",
    ]
    if pk and pk in {n for n, _ in cols}:
        sqls.append(f"DELETE FROM {target} USING {q(stage)} s WHERE {target}.{q(pk)} = s.{q(pk)}")
    sqls.append(f"INSERT INTO {target} ({col_list}) SELECT {col_list} FROM {q(stage)}")
    rs.run_tx(sqls)
    log(f"Redshift load done -> {schema}.{table}")


# ----------------------------------------------------------
# MAIN
# ----------------------------------------------------------
def main():
    args = get_args()
    TABLE = args["TABLE_NAME"]
    RUN_DATE = args["RUN_DATE"][:10]
    PK = (args["PRIMARY_KEY"] or "sys_id").lower()
    ORDER_COL = (args["ORDER_COL"] or "sys_updated_on").lower()
    LOAD_RS = (args["LOAD_REDSHIFT"] or "true").lower() == "true"
    log(f"START table={TABLE} date={RUN_DATE}")

    spark = SparkSession.builder.appName(args["JOB_NAME"]).getOrCreate()
    spark.conf.set("spark.sql.adaptive.enabled", "true")
    spark.conf.set("spark.sql.sources.partitionOverwriteMode", "dynamic")
    spark.conf.set("spark.sql.parquet.outputTimestampType", "TIMESTAMP_MICROS")  # Redshift-friendly
    spark.conf.set("spark.sql.parquet.datetimeRebaseModeInRead", "CORRECTED")
    spark.conf.set("spark.sql.parquet.int96RebaseModeInRead", "CORRECTED")
    spark.conf.set("spark.sql.parquet.datetimeRebaseModeInWrite", "CORRECTED")
    spark.conf.set("spark.sql.parquet.int96RebaseModeInWrite", "CORRECTED")
    spark.conf.set("spark.hadoop.mapreduce.fileoutputcommitter.marksuccessfuljobs", "false")

    s3 = boto3.client("s3")
    G = load_json(s3, args["GLOBAL_CONFIG_PATH"])
    gold_prefix = args["GOLD_TABLE_PREFIX"] or G.get("gold_table_prefix", "gold_table")

    yyyy, mm, dd = RUN_DATE.split("-")
    y, m, d = int(yyyy), int(mm), int(dd)

    silver_base = f"s3://{G['silver_bucket']}/{G['silver_prefix']}/{TABLE}/"
    silver_prefix = f"{G['silver_prefix']}/{TABLE}/year={y}/month={m}/day={d}/"
    if not s3_exists(s3, G["silver_bucket"], silver_prefix):
        log("No SILVER partition. Safe exit.")
        spark.stop(); return

    df = (spark.read.option("basePath", silver_base).option("mergeSchema", "true")
          .parquet(f"s3://{G['silver_bucket']}/{silver_prefix}"))

    # lower-case + dedupe column names
    seen, keep = set(), []
    for c in df.columns:
        if c.lower() not in seen:
            seen.add(c.lower()); keep.append(c)
    df = df.select([col(f"`{c}`").alias(c.lower()) for c in keep])
    df = df.drop(*[c for c in ("year", "month", "day", "hour") if c in df.columns])

    # ServiceNow reference {"link","value"} -> value  (single select, not a loop of withColumn)
    ref = StructType([StructField("link", StringType()), StructField("value", StringType())])
    df = df.select([
        coalesce(from_json(col(c), ref)["value"], col(c)).alias(c) if t == "string" else col(c)
        for c, t in df.dtypes
    ])
    df = df.drop(*[c for c in df.columns if c.endswith("_link")])

    # latest version per record (also removes duplicates from silver append re-runs)
    if PK in df.columns:
        order = desc(ORDER_COL) if ORDER_COL in df.columns else lit(1)
        w = Window.partitionBy(PK).orderBy(order)
        df = df.withColumn("_rn", row_number().over(w)).filter("_rn = 1").drop("_rn")

    df, cols = make_redshift_safe(df)
    df = df.withColumn("year", lit(y)).withColumn("month", lit(m)).withColumn("day", lit(d))

    rs_table = clean_name(TABLE)
    gold_base = f"s3://{G['gold_bucket']}/{gold_prefix}/{rs_table}/"
    day_path = f"{gold_base}year={y}/month={m}/day={d}/"
    log(f"Writing GOLD table format: {gold_base}")
    (df.coalesce(max(1, spark.sparkContext.defaultParallelism // 2))
       .write.mode("overwrite").partitionBy("year", "month", "day")
       .option("compression", "snappy").option("maxRecordsPerFile", 500000)
       .parquet(gold_base))

    if not s3_exists(s3, G["gold_bucket"], f"{gold_prefix}/{rs_table}/year={y}/month={m}/day={d}/"):
        log("Nothing written (empty day). Exit.")
        spark.stop(); return

    s3.put_object(
        Bucket=G["gold_bucket"],
        Key=f"{gold_prefix}/_SUCCESS/{rs_table}/year={y}/month={m}/day={d}/success.json",
        Body=json.dumps({"status": "SUCCESS", "table": TABLE, "day": RUN_DATE,
                         "columns": cols, "timestamp": datetime.utcnow().isoformat()}))

    if LOAD_RS:
        load_to_redshift(Redshift(args), args["REDSHIFT_SCHEMA"].lower(), rs_table, cols,
                         day_path, args["REDSHIFT_IAM_ROLE"], PK, ORDER_COL)

    log("JOB COMPLETE")
    spark.stop()


if __name__ == "__main__":
    main()
