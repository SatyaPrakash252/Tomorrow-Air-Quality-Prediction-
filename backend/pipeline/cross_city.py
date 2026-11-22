"""
cross_city.py
─────────────
Leave-One-City-Out (LOCO) Cross-City Generalization Evaluation.
Trains models on 4 metros and evaluates zero-shot generalization on the 5th
held-out metro across Delhi, Mumbai, Bangalore, Chennai, and Hyderabad.
"""

import os
import sys
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from pipeline.data_ingestion import load_and_merge, CITIES
from pipeline.imputation import run_imputation
from pipeline.preprocessing import preprocess
from pipeline.feature_engineering import create_lag_features, get_feature_columns

BACKEND_DIR = os.path.dirname(os.path.dirname(__file__))
OUTPUTS_DIR = os.path.join(BACKEND_DIR, "outputs")


def evaluate_preds(y_true, y_pred, city_name: str) -> dict:
    """Compute regression metrics."""
    rmse = round(float(np.sqrt(mean_squared_error(y_true, y_pred))), 2)
    mae = round(float(mean_absolute_error(y_true, y_pred)), 2)
    r2 = round(float(r2_score(y_true, y_pred)), 4)
    return {
        "city": city_name,
        "RMSE": rmse,
        "MAE": mae,
        "R²": r2,
    }


def run_leave_one_city_out():
    """
    Run Leave-One-City-Out evaluation across 5 Indian metros.
    """
    print("=" * 70)
    print("  LEAVE-ONE-CITY-OUT (LOCO) CROSS-CITY GENERALIZATION STUDY")
    print("=" * 70)

    # 1. Ingest, impute, preprocess
    raw_data = load_and_merge()
    imputed = run_imputation(raw_data)
    best_imputed = imputed["KNN_D"]
    preprocessed = preprocess(best_imputed)

    # 2. Feature engineering with real weather and events
    df_features = create_lag_features(preprocessed)
    feature_cols = get_feature_columns(df_features)

    print(f"\nTotal dataset size: {len(df_features)} rows across {len(CITIES)} cities")
    print(f"Features: {len(feature_cols)} (Pollutants, Weather, Lags, Events)")

    results = []

    print("\n" + "-" * 70)
    print(f"{'Held-Out City':<14} | {'Train Cities':<35} | {'RMSE':<8} | {'MAE':<8} | {'R²':<8}")
    print("-" * 70)

    for held_out in CITIES:
        train_cities = [c for c in CITIES if c != held_out]

        train_mask = df_features["City"].isin(train_cities)
        test_mask = df_features["City"] == held_out

        X_train = df_features.loc[train_mask, feature_cols]
        y_train = df_features.loc[train_mask, "AQI_next_day"]

        X_test = df_features.loc[test_mask, feature_cols]
        y_test = df_features.loc[test_mask, "AQI_next_day"]

        # Train models
        rf = RandomForestRegressor(n_estimators=100, max_depth=15, random_state=42, n_jobs=-1)
        rf.fit(X_train, y_train)
        rf_pred = rf.predict(X_test)

        xgb = XGBRegressor(n_estimators=100, max_depth=6, learning_rate=0.08, random_state=42, n_jobs=-1)
        xgb.fit(X_train, y_train, verbose=False)
        xgb_pred = xgb.predict(X_test)

        ens_pred = (rf_pred + xgb_pred) / 2.0
        metrics = evaluate_preds(y_test, ens_pred, held_out)
        metrics["train_cities"] = train_cities
        metrics["test_rows"] = int(len(X_test))
        results.append(metrics)

        train_str = ", ".join(train_cities)
        if len(train_str) > 33:
            train_str = train_str[:30] + "..."

        print(f"{held_out:<14} | {train_str:<35} | {metrics['RMSE']:<8.2f} | {metrics['MAE']:<8.2f} | {metrics['R²']:<8.4f}")

    print("-" * 70)

    avg_r2 = np.mean([r["R²"] for r in results])
    avg_rmse = np.mean([r["RMSE"] for r in results])
    avg_mae = np.mean([r["MAE"] for r in results])
    print(f"{'Mean (LOCO)':<14} | {'Average Across Metros':<35} | {avg_rmse:<8.2f} | {avg_mae:<8.2f} | {avg_r2:<8.4f}")
    print("=" * 70)

    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUTS_DIR, "cross_city_generalization.json")
    payload = {
        "study": "Leave-One-City-Out (LOCO) Cross-City Generalization",
        "description": "Zero-shot transfer of trained ensemble models to unseen geographic regions",
        "features_used": feature_cols,
        "results": results,
        "average_metrics": {
            "RMSE": round(float(avg_rmse), 2),
            "MAE": round(float(avg_mae), 2),
            "R²": round(float(avg_r2), 4),
        }
    }
    with open(out_path, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"\n[OK] Results successfully saved to {out_path}")
    return payload


if __name__ == "__main__":
    run_leave_one_city_out()
