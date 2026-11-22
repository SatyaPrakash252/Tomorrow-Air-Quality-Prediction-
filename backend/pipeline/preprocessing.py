"""
preprocessing.py
─────────────────
IQR-based outlier detection/treatment and optional SMOTE for
AQI category classification balance.
"""

import numpy as np
import pandas as pd

from .data_ingestion import POLLUTANTS, ALL_NUMERIC_COLS

# ── CPCB AQI Categories ─────────────────────────────────────────────
AQI_CATEGORIES = [
    (0, 50, "Good"),
    (51, 100, "Satisfactory"),
    (101, 200, "Moderate"),
    (201, 300, "Poor"),
    (301, 400, "Very Poor"),
    (401, 500, "Severe"),
]


def assign_aqi_category(aqi_value: float) -> str:
    """Assign CPCB AQI category based on AQI value."""
    for low, high, label in AQI_CATEGORIES:
        if low <= aqi_value <= high:
            return label
    if aqi_value > 500:
        return "Severe"
    return "Unknown"


def iqr_outlier_treatment(data: pd.DataFrame,
                          cols: list[str] = None,
                          factor: float = 1.5) -> pd.DataFrame:
    """
    IQR-based outlier detection and capping.
    Values below Q1 - factor*IQR are capped to that lower bound.
    Values above Q3 + factor*IQR are capped to that upper bound.
    """
    if cols is None:
        cols = [c for c in ALL_NUMERIC_COLS if c in data.columns]

    result = data.copy()
    print("\n🔧 IQR Outlier Treatment:")
    print("─" * 50)

    total_capped = 0
    for col in cols:
        Q1 = result[col].quantile(0.25)
        Q3 = result[col].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - factor * IQR
        upper = Q3 + factor * IQR

        below = (result[col] < lower).sum()
        above = (result[col] > upper).sum()
        capped = below + above

        if capped > 0:
            result[col] = result[col].clip(lower=lower, upper=upper)
            print(f"  {col:8s}: capped {capped:4d} outliers "
                  f"(below={below}, above={above}, range=[{lower:.1f}, {upper:.1f}])")
            total_capped += capped

    if total_capped == 0:
        print("  No outliers found beyond 1.5×IQR bounds.")
    else:
        print(f"  Total values capped: {total_capped}")

    return result


def add_aqi_categories(data: pd.DataFrame) -> pd.DataFrame:
    """Add AQI category column based on CPCB classification."""
    result = data.copy()
    result["AQI_Category"] = result["AQI"].apply(assign_aqi_category)

    print("\n📊 AQI Category Distribution:")
    dist = result["AQI_Category"].value_counts()
    for cat in ["Good", "Satisfactory", "Moderate", "Poor", "Very Poor", "Severe"]:
        count = dist.get(cat, 0)
        pct = count / len(result) * 100
        bar = "█" * int(pct / 2)
        print(f"  {cat:14s} {count:5d} ({pct:5.1f}%)  {bar}")

    return result


def preprocess(data: pd.DataFrame) -> pd.DataFrame:
    """
    Full preprocessing pipeline:
    1. IQR outlier treatment
    2. AQI category assignment
    """
    print("\n" + "=" * 60)
    print("  PREPROCESSING PIPELINE")
    print("=" * 60)

    result = iqr_outlier_treatment(data)
    result = add_aqi_categories(result)

    return result


if __name__ == "__main__":
    from .data_ingestion import load_and_merge
    data = load_and_merge()
    processed = preprocess(data)
    print(f"\n✅ Preprocessing complete. Shape: {processed.shape}")
