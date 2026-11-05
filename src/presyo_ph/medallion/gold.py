from pyspark.sql import DataFrame, SparkSession

from presyo_ph.config import (
    ENV,
    GOLD_PATH,
    GOLD_TABLES,
)


def load_gold_table(spark: SparkSession, name: str) -> DataFrame:
    if name not in GOLD_TABLES:
        raise ValueError(f"Unknown Gold table: {name}")

    if ENV == "databricks":
        df = spark.read.table(GOLD_TABLES[name])
    elif ENV == "local":
        df = spark.read.format("delta").load(str(GOLD_PATH / name))
    else:
        raise ValueError(f"Unsupported environment: {ENV}")

    print(f"Gold table loaded: {name} ({ENV})")

    return df


def save_gold_tables(tables: dict[str, DataFrame]) -> None:
    for name, df in tables.items():
        if name not in GOLD_TABLES:
            raise ValueError(f"Unknown Gold table: {name}")

        writer = (
            df.write
            .format("delta")
            .mode("overwrite")
            .option("overwriteSchema", "true")
        )

        if ENV == "databricks":
            writer.saveAsTable(GOLD_TABLES[name])
        elif ENV == "local":
            writer.save(str(GOLD_PATH / name))
        else:
            raise ValueError(f"Unsupported environment: {ENV}")

        print(f"Gold table saved: {name} ({ENV})")
