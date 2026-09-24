# SILVER -> GOLD-REDSHIFT (flat table format, NO payload struct). Glue only, no Redshift.
# Params: --TABLE_NAME  --GLOBAL_CONFIG_PATH  --RUN_DATE (YYYY-MM-DD or ALL)
import sys, json, re, boto3
from urllib.parse import urlparse
from datetime import datetime

from awsglue.utils import getResolvedOptions
from pyspark.sql import SparkSession, Window
from pyspark.sql.functions import (
    col, lit, from_json, coalesce, when, substring, octet_length,
    to_json, base64, row_number, desc
)
from pyspark.sql.types import *

VARCHAR_MAX = 65535  # Redshift VARCHAR limit in BYTES


def log(m):
    print(f"[GOLD-REDSHIFT] {m}", flush=True)


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


def main():
    args = getResolvedOptions(sys.argv, ["JOB_NAME", "TABLE_NAME", "GLOBAL_CONFIG_PATH", "RUN_DATE"])
    TABLE = args["TABLE_NAME"].strip()
    RUN_DATE = args["RUN_DATE"].strip()[:10]
    PK, ORDER_COL = "sys_id", "sys_updated_on"
    log(f"START table={TABLE} date={RUN_DATE}")

    spark = SparkSession.builder.appName(args["JOB_NAME"]).getOrCreate()
    spark.conf.set("spark.sql.adaptive.enabled", "true")
    spark.conf.set("spark.sql.sources.partitionOverwriteMode", "dynamic")
    spark.conf.set("spark.sql.parquet.outputTimestampType", "TIMESTAMP_MICROS")
    spark.conf.set("spark.sql.parquet.datetimeRebaseModeInRead", "CORRECTED")
    spark.conf.set("spark.sql.parquet.int96RebaseModeInRead", "CORRECTED")
    spark.conf.set("spark.sql.parquet.datetimeRebaseModeInWrite", "CORRECTED")
    spark.conf.set("spark.sql.parquet.int96RebaseModeInWrite", "CORRECTED")
    spark.conf.set("spark.hadoop.mapreduce.fileoutputcommitter.marksuccessfuljobs", "false")

    s3 = boto3.client("s3")
    G = load_json(s3, args["GLOBAL_CONFIG_PATH"].strip())
    gold_prefix = G.get("gold_table_prefix", "gold-redshift")
    log(f"Config: silver=s3://{G['silver_bucket']}/{G['silver_prefix']}  "
        f"gold=s3://{G['gold_bucket']}/{gold_prefix}")

    # ---------------- READ SILVER ----------------
    silver_base = f"s3://{G['silver_bucket']}/{G['silver_prefix']}/{TABLE}/"

    if RUN_DATE.upper() == "ALL":
        # full silver table (small/dimension tables); gold partition = today
        now = datetime.utcnow()
        y, m, d = now.year, now.month, now.day
        silver_prefix = f"{G['silver_prefix']}/{TABLE}/"
        read_path = silver_base
    else:
        yyyy, mm, dd = RUN_DATE.split("-")
        y, m, d = int(yyyy), int(mm), int(dd)
        silver_prefix = f"{G['silver_prefix']}/{TABLE}/year={y}/month={m}/day={d}/"
        read_path = f"s3://{G['silver_bucket']}/{silver_prefix}"

    log(f"Reading SILVER: s3://{G['silver_bucket']}/{silver_prefix}")
    if not s3_exists(s3, G["silver_bucket"], silver_prefix):
        log(f"No SILVER data at {silver_prefix}. Safe exit.")
        spark.stop(); return

    df = (spark.read.option("basePath", silver_base).option("mergeSchema", "true")
          .parquet(read_path))
    log(f"SILVER rows: {df.count()}")

    # ---------------- NORMALIZE ----------------
    # lower-case + dedupe column names
    seen, keep = set(), []
    for c in df.columns:
        if c.lower() not in seen:
            seen.add(c.lower()); keep.append(c)
    df = df.select([col(f"`{c}`").alias(c.lower()) for c in keep])
    df = df.drop(*[c for c in ("year", "month", "day", "hour") if c in df.columns])

    # ServiceNow reference {"link","value"} -> value
    ref = StructType([StructField("link", StringType()), StructField("value", StringType())])
    df = df.select([
        coalesce(from_json(col(f"`{c}`"), ref)["value"], col(f"`{c}`")).alias(c) if t == "string" else col(f"`{c}`")
        for c, t in df.dtypes
    ])
    df = df.drop(*[c for c in df.columns if c.endswith("_link")])

    # latest version per record (removes silver append duplicates too)
    if PK in df.columns:
        order = desc(ORDER_COL) if ORDER_COL in df.columns else lit(1)
        w = Window.partitionBy(PK).orderBy(order)
        df = df.withColumn("_rn", row_number().over(w)).filter("_rn = 1").drop("_rn")

    df, cols = make_redshift_safe(df)
    df = df.withColumn("year", lit(y)).withColumn("month", lit(m)).withColumn("day", lit(d))

    # ---------------- WRITE GOLD-REDSHIFT ----------------
    out_table = clean_name(TABLE)
    gold_base = f"s3://{G['gold_bucket']}/{gold_prefix}/{out_table}/"
    log(f"Writing GOLD-REDSHIFT: {gold_base}")
    (df.coalesce(max(1, spark.sparkContext.defaultParallelism // 2))
       .write.mode("overwrite").partitionBy("year", "month", "day")
       .option("compression", "snappy").option("maxRecordsPerFile", 500000)
       .parquet(gold_base))

    s3.put_object(
        Bucket=G["gold_bucket"],
        Key=f"{gold_prefix}/_SUCCESS/{out_table}/year={y}/month={m}/day={d}/success.json",
        Body=json.dumps({"status": "SUCCESS", "table": TABLE, "run_date": RUN_DATE,
                         "columns": cols, "timestamp": datetime.utcnow().isoformat()}))

    log(f"Columns: {cols}")
    log("JOB COMPLETE")
    spark.stop()


if __name__ == "__main__":
    main()
