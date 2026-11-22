"""
run_pipeline.py
───────────────
Orchestrates the full ML pipeline end-to-end:
1. Data ingestion
2. Multimodal imputation (KNN, MICE, SVD)
3. Preprocessing (IQR outliers, AQI categories)
4. MI-MMA autoencoder feature extraction
5. Feature engineering (lags, temporal, fused)
6. Model training (RF, XGBoost, LSTM, Ensemble) with Optuna tuning
7. HRI computation & alert generation
8. Save models and output metrics
"""

import os
import sys
import json
import time
import joblib
import numpy as np
import pandas as pd

# Add parent dir to path so we can import pipeline modules
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from pipeline.data_ingestion import load_and_merge, CITIES, POLLUTANTS
from pipeline.imputation import run_imputation
from pipeline.preprocessing import preprocess
from pipeline.autoencoder import build_fused_features
from pipeline.feature_engineering import (
    create_lag_features, get_feature_columns, add_fused_features,
    get_fused_feature_columns, time_based_split, prepare_lstm_sequences
)
from pipeline.models import train_all_models, evaluate_model
from pipeline.hri import (
    compute_hri_for_groups, get_tier_distributions,
    get_high_severe_rates, print_hri_summary
)
from pipeline.alerts import generate_alerts, print_alert_summary

# ── Paths ────────────────────────────────────────────────────────────
BACKEND_DIR = os.path.dirname(os.path.dirname(__file__))
MODELS_DIR = os.path.join(BACKEND_DIR, "models")
OUTPUTS_DIR = os.path.join(BACKEND_DIR, "outputs")


def save_models(model_results: dict, ae_results: dict, lstm_scaler):
    """Save all trained models to disk."""
    os.makedirs(MODELS_DIR, exist_ok=True)

    # Save sklearn/xgboost models
    joblib.dump(model_results["models"]["rf"],
                os.path.join(MODELS_DIR, "rf_model.joblib"))
    joblib.dump(model_results["models"]["xgboost"],
                os.path.join(MODELS_DIR, "xgb_model.joblib"))
    joblib.dump(lstm_scaler,
                os.path.join(MODELS_DIR, "lstm_scaler.joblib"))

    # Save Keras models
    model_results["models"]["lstm"].save(
        os.path.join(MODELS_DIR, "lstm_model.keras"))

    # Save autoencoders
    for name, ae in ae_results["autoencoders"].items():
        ae.save(os.path.join(MODELS_DIR, f"{name.lower()}.keras"))

    # Save encoders
    for name, enc in ae_results["encoders"].items():
        enc.save(os.path.join(MODELS_DIR, f"{name.lower()}_encoder.keras"))

    # Save scalers
    for name, scaler in ae_results["scalers"].items():
        joblib.dump(scaler, os.path.join(MODELS_DIR, f"{name.lower()}_scaler.joblib"))

    print(f"\n💾 Models saved to {MODELS_DIR}/")


def build_dashboard_data(data: pd.DataFrame, test_df: pd.DataFrame,
                         model_results: dict, ae_results: dict,
                         hri_cutoffs: dict, feature_cols: list[str]) -> dict:
    """Build the dashboard data JSON for the frontend."""
    cities = sorted(data["City"].unique())
    rf_model = model_results["models"]["rf"]
    xgb_model = model_results["models"]["xgboost"]

    export = {}

    # 1. Model metrics
    export["model_metrics"] = model_results["metrics"]

    # 2. Per-city test-set predictions
    export["predictions"] = {}
    for city in cities:
        cdf = test_df[test_df["City"] == city].copy().sort_values("Date")
        available_features = [c for c in feature_cols if c in cdf.columns]

        if len(cdf) == 0:
            continue

        cdf_features = cdf[available_features]
        rf_pred = rf_model.predict(cdf_features)
        xgb_pred = xgb_model.predict(cdf_features)
        ens_pred = (rf_pred + xgb_pred) / 2  # 2-model ensemble for per-city display

        export["predictions"][city] = {
            "dates": cdf["Date"].dt.strftime("%Y-%m-%d").tolist(),
            "actual": cdf["AQI_next_day"].round(1).tolist(),
            "rf": rf_pred.round(1).tolist(),
            "xgb": xgb_pred.round(1).tolist(),
            "ensemble": ens_pred.round(1).tolist(),
        }

    # 3. City statistics
    export["city_stats"] = {}
    for city in cities:
        cdf = data[data["City"] == city]
        export["city_stats"][city] = {
            "avg_aqi": round(float(cdf["AQI"].mean()), 1),
            "max_aqi": round(float(cdf["AQI"].max()), 1),
            "min_aqi": round(float(cdf["AQI"].min()), 1),
            "rows": int(len(cdf)),
        }

    # 4. HRI tier distributions
    export["hri_tiers"] = get_tier_distributions(data)

    # 5. HRI cutoffs
    export["hri_cutoffs"] = {k: round(v, 2) for k, v in hri_cutoffs.items()}

    # 6. Feature importance (top 15 from RF)
    rf_imp = model_results["feature_importances"]["rf"]
    export["feature_importance"] = {
        "features": rf_imp.head(15).index.tolist(),
        "importance": rf_imp.head(15).round(4).tolist(),
    }

    # 7. Dataset info
    export["dataset_info"] = {
        "total_rows": int(len(data)),
        "cities": cities,
        "date_range": f"{data['Date'].min().date()} to {data['Date'].max().date()}",
        "num_features": len(feature_cols),
    }

    # 8. Best model
    export["best_model"] = model_results["best_model"]

    # 9. HIGH+SEVERE rates per group
    export["alert_rates"] = get_high_severe_rates(data)

    # 10. Autoencoder reconstruction MSE
    export["autoencoder_mse"] = ae_results["reconstruction_mse"]

    return export


def save_outputs(dashboard_data: dict, imputation_rmse: dict,
                 model_results: dict, ae_results: dict,
                 hri_cutoffs: dict, alert_rates: dict):
    """Save all output files."""
    os.makedirs(OUTPUTS_DIR, exist_ok=True)

    # Dashboard data JSON (for frontend)
    with open(os.path.join(OUTPUTS_DIR, "dashboard_data.json"), "w") as f:
        json.dump(dashboard_data, f, indent=2, default=str)

    # Also write as JS for backward compatibility with index.html
    with open(os.path.join(OUTPUTS_DIR, "dashboard_data.js"), "w") as f:
        f.write("// Auto-generated by run_pipeline.py\n")
        f.write("// Do not edit manually — re-run the pipeline to regenerate.\n")
        f.write("const DASHBOARD_DATA = ")
        json.dump(dashboard_data, f, indent=2, default=str)
        f.write(";\n")

    # Comprehensive metrics report
    metrics_report = {
        "model_metrics": model_results["metrics"],
        "best_model": model_results["best_model"],
        "hyperparameters": {
            k: {str(pk): pv for pk, pv in v.items()}
            for k, v in model_results["hyperparameters"].items()
        },
        "imputation_rmse": imputation_rmse,
        "autoencoder_reconstruction_mse": ae_results["reconstruction_mse"],
        "hri_cutoffs": {k: round(v, 4) for k, v in hri_cutoffs.items()},
        "alert_rates": alert_rates,
        "feature_importances": {
            name: imp.head(15).to_dict()
            for name, imp in model_results["feature_importances"].items()
        },
    }

    with open(os.path.join(OUTPUTS_DIR, "metrics_report.json"), "w") as f:
        json.dump(metrics_report, f, indent=2, default=str)

    print(f"\n📁 Outputs saved to {OUTPUTS_DIR}/")
    print(f"   → dashboard_data.json")
    print(f"   → dashboard_data.js")
    print(f"   → metrics_report.json")


def main(tune_models: bool = True):
    """Run the full pipeline."""
    start_time = time.time()

    print("=" * 70)
    print("  🌫️  AI-Driven AQI Forecasting & Health Risk Alert System")
    print("  Full Pipeline Execution")
    print("=" * 70)

    # 1. Data Ingestion
    print("\n\n" + "▶" * 35)
    print("  STEP 1: DATA INGESTION")
    print("▶" * 35)
    data = load_and_merge()

    # 2. Multimodal Imputation
    print("\n\n" + "▶" * 35)
    print("  STEP 2: MULTIMODAL IMPUTATION")
    print("▶" * 35)
    imputation_results = run_imputation(data)

    # 3. Preprocessing
    print("\n\n" + "▶" * 35)
    print("  STEP 3: PREPROCESSING")
    print("▶" * 35)
    data = preprocess(data)

    # Also preprocess the imputed variants
    for key in ["KNN_D", "MICE_D", "SVD_D"]:
        imputation_results[key] = preprocess(imputation_results[key])

    # 4. MI-MMA Autoencoder Feature Extraction
    print("\n\n" + "▶" * 35)
    print("  STEP 4: MI-MMA AUTOENCODERS")
    print("▶" * 35)
    ae_results = build_fused_features(imputation_results, data)

    # 5. Feature Engineering
    print("\n\n" + "▶" * 35)
    print("  STEP 5: FEATURE ENGINEERING")
    print("▶" * 35)
    data_with_lags = create_lag_features(data)

    # Add fused features — need to align indices
    fused = ae_results["fused_features"]
    # After lag creation, rows are dropped; align fused features
    # The lag creation drops the first 3 rows and last 1 row per city
    # We need to slice fused features to match
    if len(fused) > len(data_with_lags):
        # Compute how many rows were dropped and from where
        # Simple approach: take the last len(data_with_lags) rows of fused
        offset = len(fused) - len(data_with_lags)
        fused_aligned = fused[offset:]
    elif len(fused) < len(data_with_lags):
        # Pad with zeros if somehow fused is shorter
        padding = np.zeros((len(data_with_lags) - len(fused), fused.shape[1]))
        fused_aligned = np.vstack([padding, fused])
    else:
        fused_aligned = fused

    # Ensure exact alignment
    fused_aligned = fused_aligned[:len(data_with_lags)]
    data_with_features = add_fused_features(data_with_lags, fused_aligned)

    # Build feature column list (including fused features)
    base_feature_cols = get_feature_columns(data_with_features)
    fused_feature_cols = get_fused_feature_columns(fused_aligned.shape[1])
    all_feature_cols = base_feature_cols + fused_feature_cols

    # Train/test split
    split_data = time_based_split(data_with_features, all_feature_cols)

    # LSTM sequences (raw features, no fused)
    lstm_data = prepare_lstm_sequences(data_with_lags, base_feature_cols)

    # 6. Model Training
    print("\n\n" + "▶" * 35)
    print("  STEP 6: MODEL TRAINING")
    print("▶" * 35)
    model_results = train_all_models(split_data, lstm_data, tune=tune_models)

    # 7. HRI & Alerts
    print("\n\n" + "▶" * 35)
    print("  STEP 7: HEALTH RISK INDEX & ALERTS")
    print("▶" * 35)
    data_with_hri, hri_cutoffs = compute_hri_for_groups(data_with_features)
    print_hri_summary(data_with_hri, hri_cutoffs)

    alerts = generate_alerts(data_with_hri, hri_cutoffs)
    print_alert_summary(alerts)

    alert_rates = get_high_severe_rates(data_with_hri)

    # 8. Save Everything
    print("\n\n" + "▶" * 35)
    print("  STEP 8: SAVING MODELS & OUTPUTS")
    print("▶" * 35)
    save_models(model_results, ae_results, model_results.get("lstm_scaler"))

    dashboard_data = build_dashboard_data(
        data_with_hri, split_data["test_df"],
        model_results, ae_results, hri_cutoffs,
        all_feature_cols
    )
    save_outputs(
        dashboard_data, imputation_results["imputation_rmse"],
        model_results, ae_results, hri_cutoffs, alert_rates
    )

    # Final Summary
    elapsed = time.time() - start_time
    print("\n\n" + "=" * 70)
    print("  📋 PIPELINE COMPLETE — FINAL SUMMARY")
    print("=" * 70)
    print(f"\n  ⏱️  Total time: {elapsed:.1f}s ({elapsed/60:.1f} min)")
    print(f"\n  Dataset:")
    print(f"    Rows (cleaned)    : {len(data_with_features):,}")
    print(f"    Cities            : {', '.join(sorted(data['City'].unique()))}")
    print(f"    Features          : {len(all_feature_cols)} "
          f"({len(base_feature_cols)} base + {len(fused_feature_cols)} fused)")
    print(f"\n  Best Model: {model_results['best_model']['Model']}")
    print(f"    Accuracy : {model_results['best_model']['Accuracy(%)']}%")
    print(f"    RMSE     : {model_results['best_model']['RMSE']}")
    print(f"    R²       : {model_results['best_model']['R²']}")
    print(f"\n  HIGH + SEVERE Risk Days:")
    for group, rate in alert_rates.items():
        print(f"    {group:25s} → {rate:.1f}%")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run the full AQI forecasting pipeline")
    parser.add_argument("--no-tune", action="store_true",
                        help="Skip Optuna hyperparameter tuning (faster, default params)")
    args = parser.parse_args()

    main(tune_models=not args.no_tune)
