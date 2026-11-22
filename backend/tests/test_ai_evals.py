"""
test_ai_evals.py
────────────────
Automated evaluation test suite for AI pipeline upgrades:
1. Clinical NLG Advisory Engine (advisories.py)
   - Schema validation with Pydantic
   - Auto-repair resilience on malformed inputs
   - Demographic cohort monotonicity: HRI(Respiratory) > HRI(Children) > HRI(General)
   - Dominant pollutant attribution correctness across CPCB pollutants
2. Upstream Resilience & Circuit Breaker
   - Fallback cache retrieval when upstream is disconnected
   - Circuit breaker state transitions (CLOSED -> OPEN -> HALF_OPEN)
3. Model Inference & Stacking Ensemble
   - Atmospheric regime-aware dynamic blending
   - TreeSHAP factor attributions
   - Bounded prediction continuity: [10, 500]
4. FastAPI Endpoints
   - /risk/{city} dynamic HRI and clinical advisory response
   - /live-comparison/{city} telemetry and provenance
"""

import sys
from pathlib import Path
import pytest

# Ensure backend directory and root directory are in sys.path
test_dir = Path(__file__).resolve().parent
backend_dir = test_dir.parent
root_dir = backend_dir.parent

for p in [str(backend_dir), str(root_dir)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from pipeline.advisories import (
    ClinicalAdvisoryEngine,
    ClinicalAdvisoryOutput,
    CohortGuidance,
    DominantFactorClinicalNote,
    POLLUTANT_CLINICAL_PROFILES
)
from api.live_inference import (
    run_live_ml_inference,
    _calc_sub_index,
    calculate_cpcb_aqi,
    UpstreamCircuitBreaker,
    _generate_fallback_multiday_data,
    ML_TIER_CITIES
)
from fastapi.testclient import TestClient
from api.main import app

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client



# ── Test Suite 1: Clinical Advisory Engine & Schemas ─────────────────────
def test_clinical_advisory_pydantic_schema_validity():
    """Verify generated advisory strictly validates against Pydantic schema."""
    advisory = ClinicalAdvisoryEngine.generate_advisory(
        city="Delhi",
        aqi=285.0,
        pollutant_values={"PM2.5": 145.0, "PM10": 260.0, "NO2": 55.0, "SO2": 18.0, "CO": 1.8, "O3": 42.0}
    )
    assert isinstance(advisory, ClinicalAdvisoryOutput)
    assert advisory.city == "Delhi"
    assert advisory.assessment_tier in ["LOW", "MODERATE", "HIGH", "SEVERE"]
    assert advisory.dominant_pollutant.pollutant in ["PM2.5", "PM10", "NO2", "SO2", "CO", "O3"]
    assert len(advisory.cohort_plans) == 3
    assert len(advisory.mitigation_checklist) >= 2


def test_demographic_cohort_risk_monotonicity():
    """
    Ensure physiological vulnerability monotonicity:
    HRI(Respiratory Patients) > HRI(Children & Elderly) > HRI(General Public)
    """
    advisory = ClinicalAdvisoryEngine.generate_advisory(
        city="Mumbai",
        aqi=140.0,
        pollutant_values={"PM2.5": 65.0, "PM10": 110.0, "NO2": 35.0, "SO2": 12.0, "CO": 0.8, "O3": 30.0}
    )
    scores = {p.cohort: p.hri_score for p in advisory.cohort_plans}
    assert scores["Respiratory Patients"] > scores["Children & Elderly"]
    assert scores["Children & Elderly"] > scores["General Public"]


def test_dominant_pollutant_attribution_pm25():
    """Ensure PM2.5 is correctly flagged when it has the highest limit ratio."""
    pollutants = {"PM2.5": 150.0, "PM10": 60.0, "NO2": 20.0, "SO2": 10.0, "CO": 0.5, "O3": 20.0}
    dom = ClinicalAdvisoryEngine.identify_dominant_pollutant(pollutants)
    assert dom == "PM2.5"


def test_dominant_pollutant_attribution_no2():
    """Ensure NO2 is correctly flagged when traffic emissions dominate."""
    pollutants = {"PM2.5": 20.0, "PM10": 30.0, "NO2": 180.0, "SO2": 10.0, "CO": 0.5, "O3": 20.0}
    dom = ClinicalAdvisoryEngine.identify_dominant_pollutant(pollutants)
    assert dom == "NO2"


def test_dominant_pollutant_attribution_ozone():
    """Ensure O3 is correctly flagged during photochemical summer events."""
    pollutants = {"PM2.5": 25.0, "PM10": 40.0, "NO2": 20.0, "SO2": 10.0, "CO": 0.5, "O3": 210.0}
    dom = ClinicalAdvisoryEngine.identify_dominant_pollutant(pollutants)
    assert dom == "O3"


def test_clinical_advisory_auto_repair():
    """Verify that auto-repair constructor produces a valid object on edge inputs."""
    dom_note = DominantFactorClinicalNote(
        pollutant="PM2.5",
        concentration=80.0,
        physiological_impact="Alveolar penetration",
        targeted_intervention="HEPA filtration"
    )
    repaired = ClinicalAdvisoryEngine._auto_repair(
        city="Kolkata",
        tier="HIGH",
        dom=dom_note,
        plans=[],
        now_str="2026-10-06T18:00:00"
    )
    assert repaired.city == "Kolkata"
    assert repaired.assessment_tier == "HIGH"
    assert repaired.schema_version == "v3.2-clinical"


# ── Test Suite 2: Upstream Reliability & Circuit Breaker ─────────────────
def test_circuit_breaker_state_flow():
    """Verify Circuit Breaker transitions: CLOSED -> OPEN -> HALF_OPEN."""
    cb = UpstreamCircuitBreaker(failure_threshold=2, cooldown_seconds=0.1)
    assert cb.state == "CLOSED"
    assert cb.can_attempt() is True

    cb.record_failure()
    assert cb.state == "CLOSED"

    cb.record_failure()
    assert cb.state == "OPEN"
    assert cb.can_attempt() is False

    import time
    time.sleep(0.15)
    assert cb.can_attempt() is True
    assert cb.state == "HALF_OPEN"

    cb.record_success()
    assert cb.state == "CLOSED"


def test_fallback_reanalysis_data_generation_delhi():
    """Verify fallback data generator returns valid 4-day dataframe for Delhi."""
    df_fallback = _generate_fallback_multiday_data("delhi")
    assert df_fallback is not None
    assert len(df_fallback) >= 4
    for col in ["AQI", "PM2.5", "PM10", "temp", "humidity", "wind_speed"]:
        assert col in df_fallback.columns


def test_fallback_reanalysis_data_generation_bangalore():
    """Verify fallback data generator works for Bangalore."""
    df_fallback = _generate_fallback_multiday_data("bangalore")
    assert df_fallback is not None
    assert len(df_fallback) >= 4


# ── Test Suite 3: Model Inference & Dynamic Stacking ─────────────────────
def test_live_ml_inference_has_telemetry():
    """Verify live inference output includes observability telemetry."""
    res = run_live_ml_inference("delhi")
    if res.get("status") == "ok":
        assert "telemetry" in res
        assert "total_latency_ms" in res["telemetry"]
        assert "shap_latency_ms" in res["telemetry"]
        assert "stacking_weights" in res["telemetry"]
        assert "circuit_breaker_state" in res["telemetry"]


def test_live_ml_inference_bounded_forecast():
    """Verify forecast AQI stays within physical bounds [10, 500]."""
    for city in ["delhi", "mumbai", "bangalore"]:
        res = run_live_ml_inference(city)
        if res.get("status") == "ok":
            assert 10.0 <= res["forecast_aqi"] <= 500.0
            assert res["confidence_interval_90"]["lower"] <= res["forecast_aqi"]
            assert res["forecast_aqi"] <= res["confidence_interval_90"]["upper"]


def test_cpcb_sub_index_calculation_breakpoints():
    """Verify India NAQI sub-index breakpoints accuracy."""
    # PM2.5 = 30 -> 50 (Good upper bound)
    assert _calc_sub_index(30.0, [(0.0, 30.0, 0, 50)]) == 50.0
    # PM2.5 = 60 -> 100 (Satisfactory upper bound)
    p_dict = {"PM2.5": 60.0}
    assert calculate_cpcb_aqi(p_dict) == 100.0


# ── Test Suite 4: Endpoints Integration & Dynamic HRI ────────────────────
def test_risk_endpoint_includes_clinical_advisory(client):
    """Verify /risk/delhi returns dynamic HRI and structured clinical advisory."""
    resp = client.get("/risk/delhi")
    assert resp.status_code == 200
    data = resp.json()
    assert data["city"] == "Delhi"
    assert len(data["groups"]) == 3
    assert "clinical_advisory" in data
    assert "dominant_pollutant" in data
    if data["clinical_advisory"]:
        assert "assessment_tier" in data["clinical_advisory"]
        assert "cohort_plans" in data["clinical_advisory"]


def test_risk_endpoint_for_all_historical_cities(client):
    """Verify /risk endpoint works across all 5 historical metros."""
    for city in ["Delhi", "Mumbai", "Bangalore", "Chennai", "Hyderabad"]:
        resp = client.get(f"/risk/{city}")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["groups"]) == 3
        # Check tier validity
        for g in data["groups"]:
            assert g["tier"] in ["LOW", "MODERATE", "HIGH", "SEVERE"]
            assert g["hri_value"] > 0


def test_live_comparison_endpoint(client):
    """Verify /live-comparison/delhi returns valid verification triple."""
    resp = client.get("/live-comparison/delhi")
    assert resp.status_code == 200
    data = resp.json()
    assert data["city"] == "Delhi"
    assert data["has_historical_model"] is True

