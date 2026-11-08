import pandas as pd
import streamlit as st
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from presyo_ph.spark import get_spark_session

from presyo_ph.medallion.gold import load_gold_table


@st.cache_resource
def get_spark():
    return (
        SparkSession.builder
        .appName("PresyoPH-Dashboard")
        .getOrCreate()
    )


@st.cache_data(ttl=600)
def load_gold_pandas(table_name: str) -> pd.DataFrame:
    spark = get_spark_session()

    df = load_gold_table(spark, table_name)

    return df.toPandas()


def load_forecasts(commodity: str) -> pd.DataFrame:
    spark = get_spark_session()

    df = load_gold_table(
        spark,
        f"{commodity}_forecasts",
    )

    df = df.withColumn(
        "generated_at",
        F.date_format(
            F.col("generated_at"),
            "yyyy-MM-dd HH:mm:ss",
        ),
    )

    return df.toPandas()


def get_commodities() -> list[str]:
    df = load_gold_pandas("national_monthly_prices")

    return sorted(df["commodity"].dropna().unique().tolist())


def get_regions() -> list[str]:
    df = load_gold_pandas("regional_monthly_prices")

    return sorted(df["adm1_name"].dropna().unique().tolist())
