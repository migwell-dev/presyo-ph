from presyo_ph.spark import get_spark_session


def test_spark_session():
    spark = get_spark_session()

    assert spark is not None
    assert spark.sparkContext.master == "local[*]"

    df = spark.createDataFrame(
        [(1, "rice"), (2, "beans")],
        ["id", "commodity"]
    )

    assert df.count() == 2

    spark.stop()
