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
