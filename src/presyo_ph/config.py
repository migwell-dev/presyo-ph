import os
from pathlib import Path

from dotenv import load_dotenv

_ = load_dotenv()

ENV = os.getenv("PRESYO_ENV", "local")

SOURCE_URL = os.getenv(
    "SOURCE_URL",
    "https://microdata.worldbank.org/catalog/6172/download/354968"
)

if ENV == "databricks":
    DATA_DIR = Path("/Volumes/workspace/bronze/raw")
else:
    DATA_DIR = Path(os.getenv("DATA_DIR", "./data")) / "raw"

# Source files
RAW_FILE = DATA_DIR / "food_prices_ph.zip"
EXTRACTED_DIR = DATA_DIR / "extracted"
EXTRACTED_FILE = EXTRACTED_DIR / "food_prices_ph.csv"

# Bronze storage
BRONZE_TABLE = os.getenv(
    "BRONZE_TABLE",
    "workspace.bronze.food_prices"
)

BRONZE_PATH = Path(
    os.getenv("BRONZE_PATH", "./data/delta/bronze/food_prices")
)
