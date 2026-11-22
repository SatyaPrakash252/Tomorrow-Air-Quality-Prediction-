"""
explainability.py
─────────────────
Native XGBoost TreeSHAP local and global explainability for AQI predictions.
Extracts top-k positive and negative drivers behind any individual forecast.
"""

import numpy as np
import pandas as pd
import xgboost as xgb
from typing import List, Dict, Any, Union


# Human-friendly feature display labels
FEATURE_DISPLAY_NAMES = {
    "AQI": "Current AQI",
    "PM2.5": "PM2.5 level",
    "PM10": "PM10 level",
    "NO2": "Nitrogen Dioxide (NO2)",
    "SO2": "Sulphur Dioxide (SO2)",
    "CO": "Carbon Monoxide (CO)",
    "O3": "Ozone (O3)",
    "AQI_lag1": "Yesterday's AQI (t-1)",
    "AQI_lag2": "AQI 2 days ago (t-2)",
    "AQI_lag3": "AQI 3 days ago (t-3)",
    "PM2.5_lag1": "Yesterday's PM2.5",
    "PM2.5_lag2": "PM2.5 (2 days ago)",
    "PM2.5_lag3": "PM2.5 (3 days ago)",
    "PM10_lag1": "Yesterday's PM10",
    "PM10_lag2": "PM10 (2 days ago)",
    "PM10_lag3": "PM10 (3 days ago)",
    "NO2_lag1": "Yesterday's NO2",
    "SO2_lag1": "Yesterday's SO2",
    "CO_lag1": "Yesterday's CO",
    "O3_lag1": "Yesterday's Ozone",
    "temp": "Ambient Temperature",
    "temp_lag1": "Yesterday's Temperature",
    "humidity": "Relative Humidity",
    "humidity_lag1": "Yesterday's Humidity",
    "wind_speed": "Wind Speed (10m)",
    "wind_speed_lag1": "Yesterday's Wind Speed",
    "wind_dir": "Wind Direction",
    "pressure": "Surface Atmospheric Pressure",
    "pressure_lag1": "Yesterday's Pressure",
    "day_of_week": "Day of the Week",
    "month": "Seasonal Month",
    "is_diwali_window": "Diwali Festival Period",
    "is_stubble_season": "Stubble Burning Season (Indo-Gangetic)",
}


def explain_prediction(xgb_model: Any,
                       feature_names: List[str],
                       feature_values: Union[pd.DataFrame, np.ndarray, dict],
                       top_k: int = 3) -> Dict[str, Any]:
    """
    Compute TreeSHAP attribution for a single input instance or batch.
    
    Parameters
    ----------
    xgb_model : trained XGBRegressor or Booster
    feature_names : list of feature names matching model training order
    feature_values : DataFrame, 2D array, or dict of feature values
    top_k : number of top positive and negative drivers to return

    Returns
    -------
    dict with:
        'base_value': float (expected value / bias)
        'prediction': float (sum of base + all SHAP values)
        'top_factors': list of dicts with feature, name, impact, direction, value
    """
    if isinstance(feature_values, dict):
        df = pd.DataFrame([{col: feature_values.get(col, 0.0) for col in feature_names}])
    elif isinstance(feature_values, pd.DataFrame):
        df = feature_values[feature_names].copy()
    else:
        df = pd.DataFrame(np.array(feature_values).reshape(1, -1), columns=feature_names)

    # Get booster
    booster = xgb_model.get_booster() if hasattr(xgb_model, "get_booster") else xgb_model
    dmat = xgb.DMatrix(df)
    
    # Calculate TreeSHAP contributions: returns (n_samples, n_features + 1)
    # The last column is the base_value (bias)
    contribs = booster.predict(dmat, pred_contribs=True)[0]
    base_value = float(contribs[-1])
    feature_contribs = contribs[:-1]
    prediction = float(base_value + np.sum(feature_contribs))

    factors = []
    for col, contrib in zip(feature_names, feature_contribs):
        # Filter out negligible or unassigned fused dimensions
        if "fused_" in col and abs(contrib) < 0.001:
            continue
        val = float(df[col].iloc[0]) if col in df.columns else 0.0
        factors.append({
            "feature": col,
            "display_name": FEATURE_DISPLAY_NAMES.get(col, col),
            "impact": round(float(contrib), 2),
            "abs_impact": abs(float(contrib)),
            "direction": "increasing" if contrib > 0 else "decreasing",
            "feature_value": round(val, 2),
        })

    # Sort by absolute impact
    factors.sort(key=lambda x: x["abs_impact"], reverse=True)
    top_factors = factors[:top_k]

    return {
        "base_value": round(base_value, 2),
        "predicted_aqi": round(prediction, 1),
        "top_factors": top_factors,
    }
