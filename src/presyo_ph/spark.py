import os

from pyspark.sql import SparkSession


def get_spark_session() -> SparkSession:
    env = os.getenv("PRESYO_ENV", "local")

    if env == "databricks":
        return SparkSession.builder.getOrCreate()

    from delta import configure_spark_with_delta_pip

    builder = (
        SparkSession.builder
        .appName("PresyoPH")
        .master("local[*]")
        .config(
            "spark.sql.extensions",
            "io.delta.sql.DeltaSparkSessionExtension"
        )
        .config(
            "spark.sql.catalog.spark_catalog",
            "org.apache.spark.sql.delta.catalog.DeltaCatalog"
        )
    )

    return configure_spark_with_delta_pip(builder).getOrCreate()
