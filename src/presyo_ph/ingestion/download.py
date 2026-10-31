import requests

from presyo_ph.config import RAW_FILE, SOURCE_URL


def download_food_prices():
    RAW_FILE.parent.mkdir(parents=True, exist_ok=True)

    temp_file = RAW_FILE.with_suffix(".tmp")

    try:
        with requests.get(SOURCE_URL, stream=True, timeout=(15, 120)) as response:
            response.raise_for_status()

            with temp_file.open("wb") as file:
                for chunk in response.iter_content(1024 * 1024):
                    if chunk:
                        _ = file.write(chunk)

        _ = temp_file.replace(RAW_FILE)

    except Exception:
        temp_file.unlink(missing_ok=True)
        raise

    print(f"Downloaded dataset to {RAW_FILE}")

    return RAW_FILE
