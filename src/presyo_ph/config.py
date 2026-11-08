from pathlib import Path

# =========================
# Environment Configuration
# =========================

ENV = "local"  # "local" | "databricks"

# =========================
# Source Configuration
# =========================

SOURCE_URL = "https://microdata.worldbank.org/catalog/6172/download/354968"

# =========================
# Project Paths
# =========================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if ENV == "databricks":
    DATA_DIR = Path("/Volumes/workspace/bronze/raw")
else:
    DATA_DIR = PROJECT_ROOT / "data" / "raw"

RAW_FILE = DATA_DIR / "food_prices_ph.zip"
EXTRACTED_DIR = DATA_DIR / "extracted"
EXTRACTED_FILE = EXTRACTED_DIR / "food_prices_ph.csv"

# =========================
# Bronze Layer Configuration
# =========================

BRONZE_PATH = PROJECT_ROOT / "data" / "delta" / "bronze" / "food_prices"

BRONZE_TABLE = "workspace.bronze.food_prices"

# =========================
# Silver Layer Configuration
# =========================

SILVER_PATH = PROJECT_ROOT / "data" / "delta" / "silver" / "food_prices"

SILVER_TABLE = "workspace.silver.food_prices"

# =========================
# Gold Layer Configuration
# =========================

GOLD_PATH = PROJECT_ROOT / "data" / "delta" / "gold"

GOLD_TABLES = {
    "market_monthly_prices": "workspace.gold.market_monthly_prices",
    "regional_monthly_prices": "workspace.gold.regional_monthly_prices",
    "national_monthly_prices": "workspace.gold.national_monthly_prices",
    "national_commodity_growth": "workspace.gold.national_commodity_growth",
    "rice_forecasts": "workspace.gold.rice_forecasts",
    "beans_forecasts": "workspace.gold.beans_forecasts",
    "cabbage_forecasts": "workspace.gold.cabbge_forecasts",
    "carrots_forecasts": "workspace.gold.carrots_forecasts",
    "eggs_forecasts": "workspace.gold.eggs_forecasts",
    "garlic_forecasts": "workspace.gold.garlic_forecasts",
    "onions_forecasts": "workspace.gold.onions_forecasts",
    "potatoes_forecasts": "workspace.gold.potatoes_forecasts",
    "tomatoes_forecasts": "workspace.gold.tomatoes_forecasts",
}
