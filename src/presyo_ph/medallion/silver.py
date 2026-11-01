from pyspark.sql import DataFrame

from presyo_ph.config import (
    ENV,
    SILVER_PATH,
    SILVER_TABLE,
)


def save_silver(df: DataFrame) -> None:
    writer = (
        df.write
        .format("delta")
        .mode("overwrite")
    )

    if ENV == "databricks":
        writer.saveAsTable(SILVER_TABLE)
    elif ENV == "local":
        writer.save(str(SILVER_PATH))
    else:
        raise ValueError(f"Unsupported environment: {ENV}")

    print(f"Silver transformation completed: {ENV}")
