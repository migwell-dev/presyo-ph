from presyo_ph.ingestion.download import download_food_prices
from presyo_ph.ingestion.load_bronze import load_bronze
from presyo_ph.spark import get_spark_session

spark = get_spark_session()

_ = download_food_prices()

df = load_bronze(spark)

print(f"Records ingested: {df.count()}")
