"""
test_advanced_pipeline.py
─────────────────────────
Automated tests for advanced literature differentiation and rigor components:
1. Live ML Ensemble inference with 90% confidence intervals
2. Native XGBoost TreeSHAP explainability
3. Weather data cache integrity
4. Ablation study & statistical significance outputs
5. Leave-One-City-Out generalization outputs
"""

import os
import sys
import json
import pytest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


def test_weather_cache_files():
    weather_dir = BACKEND_DIR / "data" / "weather"
    assert weather_dir.exists(), "Weather directory should exist"
    cities = ["delhi", "mumbai", "bangalore", "chennai", "hyderabad"]
    for city in cities:
        p = weather_dir / f"{city}_weather.csv"
        assert p.exists(), f"Weather cache for {city} must exist"
        assert p.stat().st_size > 50000, f"Weather cache for {city} must not be empty"


def test_live_ml_inference_delhi():
    from api.live_inference import run_live_ml_inference
    res = run_live_ml_inference("Delhi")
    assert res is not None
    assert res["status"] == "ok"
    assert res["is_ml_tier"] is True
    assert "forecast_aqi" in res
    assert res["forecast_aqi"] > 0
    assert "Ensemble ML" in res["model_used"]
    assert "confidence_interval_90" in res
    ci = res["confidence_interval_90"]
    assert ci["lower"] <= res["forecast_aqi"] <= ci["upper"]
    assert "top_contributing_factors" in res
    assert len(res["top_contributing_factors"]) >= 1


def test_explainability_treeshap():
    from pipeline.explainability import explain_prediction
    import joblib
    xgb_path = BACKEND_DIR / "models" / "xgb_model.joblib"
    assert xgb_path.exists()
    model = joblib.load(xgb_path)
    names = list(model.feature_names_in_)
    sample = {c: 10.0 for c in names}
    sample["AQI"] = 180.0
    res = explain_prediction(model, names, sample, top_k=3)
    assert "base_value" in res
    assert "top_factors" in res
    assert len(res["top_factors"]) == 3
    assert all("impact" in f and "direction" in f for f in res["top_factors"])


def test_ablation_study_json_exists():
    p = BACKEND_DIR / "outputs" / "ablation_study.json"
    assert p.exists()
    with open(p, "r") as f:
        data = json.load(f)
    assert "ablation_matrix" in data
    assert len(data["ablation_matrix"]) >= 6
    assert "significance_testing" in data
    assert data["significance_testing"]["t_test_significant_p05"] is True
    assert data["significance_testing"]["wilcoxon_significant_p01"] is True
    assert "multi_horizon" in data
    assert len(data["multi_horizon"]) == 3


def test_cross_city_generalization_json_exists():
    p = BACKEND_DIR / "outputs" / "cross_city_generalization.json"
    assert p.exists()
    with open(p, "r") as f:
        data = json.load(f)
    assert "results" in data
    assert len(data["results"]) == 5
    assert "average_metrics" in data
