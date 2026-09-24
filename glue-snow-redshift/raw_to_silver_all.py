# RAW -> SILVER. Reads ALL raw data of a table (or one day) and writes silver
# in the same layout as the existing silver job: silver/<table>/year=/month=/day=/hour=/
# Params: --TABLE_NAME  --GLOBAL_CONFIG_PATH  --RUN_DATE (YYYY-MM-DD or ALL)
import sys, json, boto3
from urllib.parse import urlparse
from datetime import datetime, timezone

from awsglue.utils import getResolvedOptions
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, year, month, dayofmonth, hour, to_timestamp, coalesce, current_timestamp
)
from pyspark.sql.types import StructType, TimestampType


def log(m):
    print(f"[SILVER-ALL] {m}", flush=True)


def load_json(s3, path):
    p = urlparse(path)
    return json.loads(s3.get_object(Bucket=p.netloc, Key=p.path.lstrip("/"))["Body"].read())


def s3_exists(s3, bucket, prefix):
    return "Contents" in s3.list_objects_v2(Bucket=bucket, Prefix=prefix, MaxKeys=1)


def flatten_structs(df):
    # flatten ALL top-level struct columns (one level)
    out = []
    for f in df.schema.fields:
        if isinstance(f.dataType, StructType):
            log(f"Flattening struct column: {f.name}")
            out += [col(f"`{f.name}`.`{s.name}`").alias(s.name) for s in f.dataType.fields]
        else:
            out.append(col(f"`{f.name}`"))
    return df.select(*out)


def dedupe_lower(df):
    seen, keep = set(), []
    for c in df.columns:
        if c.lower() not in seen:
            seen.add(c.lower()); keep.append(c)
    return df.select([col(f"`{c}`").alias(c.lower()) for c in keep])


def main():
    args = getResolvedOptions(sys.argv, ["JOB_NAME", "TABLE_NAME", "GLOBAL_CONFIG_PATH", "RUN_DATE"])
    TABLE = args["TABLE_NAME"].strip()
    RUN_DATE = args["RUN_DATE"].strip()[:10]
    log(f"START table={TABLE} date={RUN_DATE}")

    spark = SparkSession.builder.appName(args["JOB_NAME"]).getOrCreate()
    spark.conf.set("spark.sql.adaptive.enabled", "true")
    spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")
    spark.conf.set("spark.sql.sources.partitionOverwriteMode", "dynamic")
    spark.conf.set("spark.sql.parquet.datetimeRebaseModeInRead", "CORRECTED")
    spark.conf.set("spark.sql.parquet.int96RebaseModeInRead", "CORRECTED")
    spark.conf.set("spark.sql.parquet.datetimeRebaseModeInWrite", "CORRECTED")
    spark.conf.set("spark.sql.parquet.int96RebaseModeInWrite", "CORRECTED")

    s3 = boto3.client("s3")
    G = load_json(s3, args["GLOBAL_CONFIG_PATH"].strip())
    log(f"Config: raw=s3://{G['raw_bucket']}/{G['raw_prefix']}  silver=s3://{G['silver_bucket']}/{G['silver_prefix']}")

    # ---------------- READ RAW ----------------
    if RUN_DATE.upper() == "ALL":
        raw_prefix = f"{G['raw_prefix']}/{TABLE}/"
    else:
        yyyy, mm, dd = RUN_DATE.split("-")
        raw_prefix = f"{G['raw_prefix']}/{TABLE}/{yyyy}/{mm}/{dd}/"
    raw_path = f"s3://{G['raw_bucket']}/{raw_prefix}"
    log(f"Reading RAW: {raw_path}")

    if not s3_exists(s3, G["raw_bucket"], raw_prefix):
        log(f"No RAW data at {raw_prefix}. Safe exit.")
        spark.stop(); return

    df = (spark.read
          .option("recursiveFileLookup", "true")
          .option("mergeSchema", "true")
          .option("pathGlobFilter", "*")
          .option("datetimeRebaseMode", "CORRECTED")
          .option("int96RebaseMode", "CORRECTED")
          .parquet(raw_path))

    row_count = df.count()
    log(f"RAW rows: {row_count}")
    if row_count == 0:
        log("RAW empty. Safe exit.")
        spark.stop(); return
    df.printSchema()

    # ---------------- NORMALIZE ----------------
    df = flatten_structs(df)
    df = dedupe_lower(df)
    df = df.drop(*[c for c in ("year", "month", "day", "hour") if c in df.columns])

    # ---------------- TIMESTAMP ----------------
    ts_candidates = [c.lower() for c in G.get("timestamp_priority", ["sys_updated_on", "sys_created_on"])]
    ts_present = [c for c in ts_candidates if c in df.columns]
    if not ts_present:
        ts_present = [f.name for f in df.schema.fields if isinstance(f.dataType, TimestampType)]
    if not ts_present:
        raise Exception(f"No timestamp column found. Columns: {df.columns}")
    ts_col = ts_present[0]
    log(f"Partition timestamp column: {ts_col} (fallbacks: {ts_present[1:]})")

    for c in ts_present:
        df = df.withColumn(c, to_timestamp(col(c)))

    # partition ts: first non-null of priority columns; if all null -> load time (row is NOT dropped)
    df = df.withColumn("_pts", coalesce(*[col(c) for c in ts_present]))
    bad = df.filter(col("_pts").isNull()).count()
    if bad:
        log(f"WARNING: {bad} rows with no timestamp -> partitioned by load time")
    df = df.withColumn("_pts", coalesce(col("_pts"), current_timestamp()))

    df = (df.withColumn("year", year("_pts"))
            .withColumn("month", month("_pts"))
            .withColumn("day", dayofmonth("_pts"))
            .withColumn("hour", hour("_pts"))
            .drop("_pts"))

    # ---------------- WRITE SILVER ----------------
    n_parts = max(4, min(500, int(row_count / 500_000) + 1))
    spark.conf.set("spark.sql.shuffle.partitions", str(n_parts))
    df = df.repartition(n_parts, "year", "month", "day")

    silver_path = f"s3://{G['silver_bucket']}/{G['silver_prefix']}/{TABLE}/"
    log(f"Writing SILVER: {silver_path}")
    # dynamic overwrite: re-runs replace the same partitions, no duplicates
    (df.write.mode("overwrite")
       .partitionBy("year", "month", "day", "hour")
       .option("compression", "snappy")
       .parquet(silver_path))

    s3.put_object(
        Bucket=G["silver_bucket"],
        Key=f"{G['silver_prefix']}/_SUCCESS/{TABLE}/run_{RUN_DATE}.json",
        Body=json.dumps({"status": "SUCCESS", "table": TABLE, "run_date": RUN_DATE,
                         "rows": row_count,
                         "timestamp": datetime.now(timezone.utc).isoformat()}))

    log(f"SILVER rows written: {row_count}")
    log("JOB COMPLETE")
    spark.stop()


if __name__ == "__main__":
    main()
