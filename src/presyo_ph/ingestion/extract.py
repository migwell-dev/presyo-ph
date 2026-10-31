import zipfile

from presyo_ph.config import RAW_FILE, EXTRACTED_DIR, EXTRACTED_FILE


def extract_food_prices():
    EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(RAW_FILE, "r") as archive:
        csv_filename = archive.namelist()[0]

        with (
            archive.open(csv_filename) as source,
            EXTRACTED_FILE.open("wb") as target
        ):
            while chunk := source.read(1024 * 1024):
                _ = target.write(chunk)

    return EXTRACTED_FILE
