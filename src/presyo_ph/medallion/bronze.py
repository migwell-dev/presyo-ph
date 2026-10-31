from pyspark.sql import SparkSession
from pyspark.sql import functions as F

from presyo_ph.config import (
    BRONZE_PATH,
    BRONZE_TABLE,
    ENV,
    EXTRACTED_FILE,
)


def load_bronze(spark: SparkSession):
    if not EXTRACTED_FILE.exists():
        raise FileNotFoundError(
            f"Extracted dataset not found: {EXTRACTED_FILE}"
        )

    df = (
        spark.read
        .option("header", True)
        .option("inferSchema", False)
        .csv(str(EXTRACTED_FILE))
    )

    bronze_df = (
        df
        .withColumn("_ingested_at", F.current_timestamp())
        .withColumn("_source_file", F.lit(str(EXTRACTED_FILE)))
    )

    writer = bronze_df.write.format("delta").mode("overwrite")

    if ENV == "databricks":
        writer.saveAsTable(BRONZE_TABLE)
    else:
        writer.save(str(BRONZE_PATH))

    print(f"Bronze ingestion completed: {ENV}")

    return bronze_df
