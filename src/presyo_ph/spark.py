import os

from pyspark.sql import SparkSession


def get_spark_session():
    env = os.getenv("PRESYO_ENV", "local")

    if env == "databricks":
        return SparkSession.builder.getOrCreate()

    return (
        SparkSession.builder
        .appName("PresyoPH")
        .getOrCreate()
    )
