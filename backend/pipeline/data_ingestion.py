"""
data_ingestion.py
─────────────────
Download all city CSVs from the GitHub dataset repo, merge, parse dates,
and sort by City + Date. Caches raw CSVs locally.
"""

import os
import pandas as pd
import requests
import warnings

warnings.filterwarnings("ignore")

# ── Constants ────────────────────────────────────────────────────────
CITIES = ["Delhi", "Mumbai", "Chennai", "Hyderabad", "Bangalore"]
BASE_URL = "https://raw.githubusercontent.com/cp099/India-Air-Quality-Dataset/main/"
RAW_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "raw")
POLLUTANTS = ["PM2.5", "PM10", "NO2", "SO2", "CO", "O3"]
ALL_NUMERIC_COLS = ["AQI"] + POLLUTANTS


def download_city_csv(city: str, cache_dir: str = RAW_DATA_DIR) -> str:
    """Download a single city CSV if not already cached. Returns local path."""
    os.makedirs(cache_dir, exist_ok=True)
    local_path = os.path.join(cache_dir, f"{city}_AQI_Dataset.csv")

    if os.path.exists(local_path):
        print(f"  ✅ {city:12s} → cached ({os.path.getsize(local_path):,} bytes)")
        return local_path

    url = f"{BASE_URL}{city}_AQI_Dataset.csv"
    print(f"  ⬇️  {city:12s} → downloading from GitHub...")
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()

    with open(local_path, "wb") as f:
        f.write(resp.content)

    print(f"  ✅ {city:12s} → saved ({len(resp.content):,} bytes)")
    return local_path


def load_and_merge(cities: list[str] = CITIES) -> pd.DataFrame:
    """
    Download (or load cached) CSVs for all cities, merge into a single
    DataFrame with parsed dates, sorted by City + Date.
    """
    print("📥 Loading city datasets...")
    frames = []

    for city in cities:
        path = download_city_csv(city)
        df = pd.read_csv(path)
        frames.append(df)

    # Merge into one DataFrame
    data = pd.concat(frames, ignore_index=True)

    # Drop unnamed / empty trailing columns
    data = data.loc[:, ~data.columns.str.contains("^Unnamed")]

    # Parse dates — the dataset uses DD/MM/YY format
    data["Date"] = pd.to_datetime(data["Date"], format="%d/%m/%y", dayfirst=True)
    data = data.sort_values(["City", "Date"]).reset_index(drop=True)

    # Ensure numeric columns are actually numeric
    for col in ALL_NUMERIC_COLS:
        data[col] = pd.to_numeric(data[col], errors="coerce")

    print(f"\n📊 Combined shape      : {data.shape}")
    print(f"📅 Date range          : {data['Date'].min().date()} → {data['Date'].max().date()}")
    print(f"🏙️  Cities              : {', '.join(cities)}")
    print(f"🔍 Null counts:\n{data.isnull().sum()}")
    print(f"\n📈 Rows per city:\n{data['City'].value_counts().sort_index().to_string()}")

    return data


if __name__ == "__main__":
    df = load_and_merge()
    print(f"\n✅ Data ingestion complete. Shape: {df.shape}")
    print(df.head(10))
