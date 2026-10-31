import requests

BASE_URL = "https://microdata.worldbank.org/api/tables"

metadata_url = f"{BASE_URL}/info/fcv/wld_2021_rtfp_v02_m"

response = requests.get(
    metadata_url,
    params={"data_dictionary": "true"},
    timeout=30
)

response.raise_for_status()

metadata = response.json()["result"]

print("Total observations:", metadata["count"])

for feature in metadata["metadata"]["features"]:
    print(feature["feature_name"], "-", feature["feature_label"])
