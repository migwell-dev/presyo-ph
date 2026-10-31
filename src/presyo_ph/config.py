import os
from pathlib import Path

from dotenv import load_dotenv

_ = load_dotenv()

ENV = os.getenv("PRESYO_ENV", "local")

SOURCE_URL = os.getenv(
    "SOURCE_URL",
    "https://microdata.worldbank.org/catalog/6172/download/354968"
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if ENV == "databricks":
    DATA_DIR = Path("/Volumes/workspace/bronze/raw")
else:
    DATA_DIR = Path(os.getenv("DATA_DIR", "data"))

    if not DATA_DIR.is_absolute():
        DATA_DIR = PROJECT_ROOT / DATA_DIR

    DATA_DIR = DATA_DIR.resolve()

    DATA_DIR = DATA_DIR / "raw"

RAW_FILE = DATA_DIR / "food_prices_ph.zip"
EXTRACTED_DIR = DATA_DIR / "extracted"
EXTRACTED_FILE = EXTRACTED_DIR / "food_prices_ph.csv"

BRONZE_TABLE = os.getenv(
    "BRONZE_TABLE",
    "workspace.bronze.food_prices"
)

BRONZE_PATH = Path(
    os.getenv(
        "BRONZE_PATH",
        str(PROJECT_ROOT / "data/delta/bronze/food_prices")
    )
)
