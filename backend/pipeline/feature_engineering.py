"""
feature_engineering.py
──────────────────────
Create lag features, meteorological features, India-specific event flags,
multi-horizon forecasting targets (t+1, t+2, t+3), and combine with
multimodal features.
Time-based train/test split per city.
"""

import os
import numpy as np
import pandas as pd
from typing import Optional

from .data_ingestion import CITIES, POLLUTANTS

BACKEND_DIR = os.path.dirname(os.path.dirname(__file__))
WEATHER_DIR = os.path.join(BACKEND_DIR, "data", "weather")

# ── Feature Configuration ────────────────────────────────────────────
LAG_COLS = ["AQI"] + POLLUTANTS   # pollutant columns to create lags for
LAG_STEPS = [1, 2, 3]             # 1-day, 2-day, 3-day lookback
WEATHER_COLS = ["temp", "humidity", "wind_speed", "wind_dir", "pressure"]
WEATHER_LAG_COLS = ["temp", "humidity", "wind_speed", "pressure"]
TRAIN_FRACTION = 0.80             # 80/20 time-based split

# Diwali exact dates in India (2018-2026)
DIWALI_DATES = [
    pd.Timestamp("2018-11-07"),
    pd.Timestamp("2019-10-27"),
    pd.Timestamp("2020-11-14"),
    pd.Timestamp("2021-11-04"),
    pd.Timestamp("2022-10-24"),
    pd.Timestamp("2023-11-12"),
    pd.Timestamp("2024-11-01"),
    pd.Timestamp("2025-10-20"),
    pd.Timestamp("2026-11-08"),
]


def load_cached_weather() -> Optional[pd.DataFrame]:
    """Load cached daily meteorological records from backend/data/weather/."""
    if not os.path.exists(WEATHER_DIR):
        return None
    dfs = []
    for city in CITIES:
        p = os.path.join(WEATHER_DIR, f"{city.lower()}_weather.csv")
        if os.path.exists(p):
            df = pd.read_csv(p)
            df["Date"] = pd.to_datetime(df["Date"])
            dfs.append(df)
    if dfs:
        return pd.concat(dfs, ignore_index=True)
    return None


def add_india_events(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add India-specific environmental and cultural event indicators:
    1. is_diwali_window: 1 if within ±2 days of Diwali, else 0
    2. is_stubble_season: 1 if date is between Oct 15 and Nov 25, else 0
    """
    result = df.copy()
    dates = pd.to_datetime(result["Date"])

    # Diwali window: ±2 days
    is_diwali = pd.Series(False, index=result.index)
    for d_date in DIWALI_DATES:
        window_start = d_date - pd.Timedelta(days=2)
        window_end = d_date + pd.Timedelta(days=2)
        is_diwali |= (dates >= window_start) & (dates <= window_end)
    result["is_diwali_window"] = is_diwali.astype(int)

    # Stubble burning season in North India: Oct 15 - Nov 25
    month = dates.dt.month
    day = dates.dt.day
    is_stubble = ((month == 10) & (day >= 15)) | ((month == 11) & (day <= 25))
    result["is_stubble_season"] = is_stubble.astype(int)

    return result


def create_lag_features(data: pd.DataFrame, weather_df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """
    Create lag features (t-1, t-2, t-3) for AQI and all pollutants,
    grouped by city. Add meteorological features (temp, humidity, wind_speed,
    wind_dir, pressure) and their lags. Add India-specific event flags.
    Targets:
      - AQI_next_day (t+1)
      - AQI_day2     (t+2)
      - AQI_day3     (t+3)
    """
    print("\n[Feature Engineering] Creating lag, weather, and event features...")
    result = data.copy()
    result["Date"] = pd.to_datetime(result["Date"])

    # 1. Merge historical weather if available
    if weather_df is None:
        weather_df = load_cached_weather()

    if weather_df is not None:
        weather_df["Date"] = pd.to_datetime(weather_df["Date"])
        w_cols = [c for c in WEATHER_COLS if c in weather_df.columns]
        merge_cols = ["City", "Date"] + w_cols
        result = pd.merge(result, weather_df[merge_cols], on=["City", "Date"], how="left")
        # Forward/backward fill missing weather per city
        for c in w_cols:
            result[c] = result.groupby("City")[c].transform(lambda s: s.ffill().bfill())
        print(f"  Merged {len(w_cols)} real meteorological variables (Open-Meteo ERA5)")

    # 2. Lag features for pollutants per city
    for col in LAG_COLS:
        if col in result.columns:
            for lag in LAG_STEPS:
                result[f"{col}_lag{lag}"] = result.groupby("City")[col].shift(lag)

    # 3. Lag features for weather per city
    for col in WEATHER_LAG_COLS:
        if col in result.columns:
            for lag in [1, 2]:
                result[f"{col}_lag{lag}"] = result.groupby("City")[col].shift(lag)

    # 4. Temporal features
    result["day_of_week"] = result["Date"].dt.dayofweek   # 0=Monday
    result["month"] = result["Date"].dt.month             # 1-12

    # 5. India-specific events
    result = add_india_events(result)

    # 6. Targets: multi-horizon AQI
    result["AQI_next_day"] = result.groupby("City")["AQI"].shift(-1)
    result["AQI_day2"] = result.groupby("City")["AQI"].shift(-2)
    result["AQI_day3"] = result.groupby("City")["AQI"].shift(-3)

    # Drop rows with NaN from lagging/shifting
    before = len(result)
    result = result.dropna().reset_index(drop=True)
    after = len(result)

    lag_feature_cols = [c for c in result.columns if "lag" in c]
    print(f"  Lag features created: {len(lag_feature_cols)}")
    print(f"  Rows: {before} -> {after} (dropped {before - after} NaN rows)")

    return result


def get_feature_columns(data: pd.DataFrame) -> list[str]:
    """Get the full list of model input feature columns."""
    base_cols = ["AQI"] + [p for p in POLLUTANTS if p in data.columns]
    lag_cols = [f"{c}_lag{l}" for c in LAG_COLS for l in LAG_STEPS if f"{c}_lag{l}" in data.columns]

    w_cols = [c for c in WEATHER_COLS if c in data.columns]
    w_lag_cols = [f"{c}_lag{l}" for c in WEATHER_LAG_COLS for l in [1, 2] if f"{c}_lag{l}" in data.columns]

    temporal_cols = [c for c in ["day_of_week", "month"] if c in data.columns]
    event_cols = [c for c in ["is_diwali_window", "is_stubble_season"] if c in data.columns]

    feature_cols = base_cols + lag_cols + w_cols + w_lag_cols + temporal_cols + event_cols
    return [c for c in feature_cols if c in data.columns]


def get_fused_feature_columns(n_fused: int = 36) -> list[str]:
    """Get column names for the fused autoencoder features."""
    return [f"fused_{i}" for i in range(n_fused)]


def add_fused_features(data: pd.DataFrame, fused_features: np.ndarray) -> pd.DataFrame:
    """Add the fused features to the dataframe."""
    result = data.copy()
    if len(fused_features) != len(result):
        fused_features = fused_features[:len(result)]

    fused_cols = get_fused_feature_columns(fused_features.shape[1])
    for i, col_name in enumerate(fused_cols):
        result[col_name] = fused_features[:, i]

    return result


def time_based_split(data: pd.DataFrame, feature_cols: list[str],
                     target_col: str = "AQI_next_day",
                     train_fraction: float = TRAIN_FRACTION,
                     cities: list[str] = None) -> dict:
    """
    Time-based train/test split per city.
    Last (1 - train_fraction) of each city's chronological data = test set.
    """
    if cities is None:
        cities = sorted(data["City"].unique())

    print(f"\n[Split] Time-based {int(train_fraction*100)}/{int((1-train_fraction)*100)} split per city:")
    print("-" * 50)

    train_parts, test_parts = [], []
    split_info = {}

    for city in cities:
        cdf = data[data["City"] == city].sort_values("Date")
        n = len(cdf)
        cut = int(n * train_fraction)
        train_parts.append(cdf.iloc[:cut])
        test_parts.append(cdf.iloc[cut:])
        split_info[city] = {"train": cut, "test": n - cut, "total": n}
        print(f"  {city:12s}  train={cut:>4}   test={n - cut:>4}")

    train_df = pd.concat(train_parts).reset_index(drop=True)
    test_df = pd.concat(test_parts).reset_index(drop=True)

    available_features = [c for c in feature_cols if c in train_df.columns]

    X_train = train_df[available_features]
    y_train = train_df[target_col]
    X_test = test_df[available_features]
    y_test = test_df[target_col]

    print(f"\n[OK] Training set : {len(X_train):,} rows x {len(available_features)} features")
    print(f"[OK] Test set     : {len(X_test):,} rows x {len(available_features)} features")

    return {
        "X_train": X_train,
        "y_train": y_train,
        "X_test": X_test,
        "y_test": y_test,
        "train_df": train_df,
        "test_df": test_df,
        "feature_cols": available_features,
        "split_info": split_info,
    }
