from presyo_ph.ingestion.download import download_food_prices
from presyo_ph.ingestion.extract import extract_food_prices


def run_ingestion():
    _ = download_food_prices()
    _ = extract_food_prices()


if __name__ == "__main__":
    run_ingestion()
