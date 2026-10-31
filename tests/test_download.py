import zipfile

import pandas as pd
import pytest

from presyo_ph.ingestion.download import download_food_prices
from presyo_ph.ingestion.extract import extract_food_prices


@pytest.fixture(scope="module")
def zip_path():
    return download_food_prices()


def test_download_food_prices(zip_path):
    assert zip_path.exists()
    assert zip_path.stat().st_size > 0
    assert zipfile.is_zipfile(zip_path)


def test_extract_food_prices(zip_path):
    csv_path = extract_food_prices(zip_path)

    assert csv_path.exists()
    assert csv_path.name == "food_prices_ph.csv"

    df = pd.read_csv(csv_path)

    assert df.shape == (24743, 88)
    assert "price_date" in df.columns
    assert "rice" in df.columns
