"""
test_api.py
───────────
Automated test suite for the All-India AQI Forecasting & Health Risk Alert API (Interim Review-2).
Tests both historical ML ensemble metros and expanded All-India atmospheric forecasting cities.
"""

import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Ensure backend directory is in sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from api.main import app

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_health_check(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "ok"]
    assert "version" in data
    assert len(data["cities"]) >= 30


def test_city_config(client):
    response = client.get("/config/cities")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 30
    assert data["historical_count"] == 5
    assert data["live_only_count"] >= 25

    city_names = [c["city"] for c in data["cities"]]
    # Core historical metros
    assert "Delhi" in city_names
    assert "Mumbai" in city_names
    assert "Chennai" in city_names
    assert "Hyderabad" in city_names
    assert "Bangalore" in city_names

    # Expanded cities across India
    assert "Bhubaneswar" in city_names
    assert "Cuttack" in city_names
    assert "Kolkata" in city_names
    assert "Jaipur" in city_names
    assert "Pune" in city_names
    assert "Ahmedabad" in city_names
    assert "Guwahati" in city_names


def test_forecast_historical_city(client):
    response = client.get("/forecast/Delhi")
    assert response.status_code == 200
    data = response.json()
    assert data["city"] == "Delhi"
    assert "forecast_aqi" in data
    assert data["forecast_aqi"] > 0
    assert "pollutant_breakdown" in data
    assert "Ensemble" in data["model_used"]


def test_forecast_atmospheric_city(client):
    """Expanded Indian cities receive real atmospheric numerical AI forecasts (Copernicus/GFS)."""
    response = client.get("/forecast/Bhubaneswar")
    assert response.status_code == 200
    data = response.json()
    assert data["city"] == "Bhubaneswar"
    assert "forecast_aqi" in data
    assert data["forecast_aqi"] > 0
    assert "pollutant_breakdown" in data
    assert "Atmospheric" in data["model_used"] or "Copernicus" in data["model_used"]


def test_live_comparison_historical(client):
    response = client.get("/live-comparison/Delhi")
    assert response.status_code == 200
    data = response.json()
    assert data["city"] == "Delhi"
    assert data["has_historical_model"] is True
    assert data["live_actual"] is not None or data["tomorrow_forecast"] is not None


def test_live_comparison_expanded_city(client):
    """Live comparison verification triple works for all expanded cities across India."""
    response = client.get("/live-comparison/Bhubaneswar")
    assert response.status_code == 200
    data = response.json()
    assert data["city"] == "Bhubaneswar"
    assert data["live_actual"] is not None or data["tomorrow_forecast"] is not None
    assert data["tomorrow_forecast"] is not None


def test_live_aqi_endpoint(client):
    """Test live AQI endpoint returns valid consensus and provenance."""
    response = client.get("/live/Delhi")
    assert response.status_code == 200
    data = response.json()
    assert data["city"] == "Delhi"
    assert data["sources_available"] >= 1
    assert data["consensus_aqi"] is not None


def test_validation_historical(client):
    response = client.get("/validation/Delhi?days=14")
    assert response.status_code == 200
    data = response.json()
    assert data["city"] == "Delhi"
    assert data["metrics_type"] == "live_validation"
    assert "entries" in data


def test_risk_endpoint(client):
    response = client.get("/risk/Delhi")
    assert response.status_code == 200
    data = response.json()
    assert data["city"] == "Delhi"
    assert len(data["groups"]) == 3
    group_names = [g["group"] for g in data["groups"]]
    assert "General Public" in group_names
    assert "Children/Elderly" in group_names
    assert "Respiratory Patients" in group_names


def test_risk_expanded_city(client):
    response = client.get("/risk/Bhubaneswar")
    assert response.status_code == 200
    data = response.json()
    assert data["city"] == "Bhubaneswar"
    assert len(data["groups"]) == 3


def test_alerts_endpoint(client):
    response = client.get("/alerts")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "alerts" in data


def test_metrics_endpoint(client):
    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "model_metrics" in data
    assert "best_model" in data
