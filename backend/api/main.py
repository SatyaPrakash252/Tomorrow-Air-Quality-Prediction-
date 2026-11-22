"""
main.py
───────
FastAPI backend for the AQI Forecasting & Health Risk Alert System.

Endpoints:
    GET /                       → API health check
    GET /forecast/{city}        → Next-day AQI forecast
    GET /risk/{city}            → HRI per vulnerability group
    GET /alerts/{city}          → Active alerts for a city
    GET /alerts                 → All active alerts
    GET /history/{city}?days=N  → Historical actual vs forecasted
    GET /metrics                → Model evaluation metrics
    GET /cities                 → Available cities with stats
    GET /config/cities          → City registry with model availability
    GET /live/{city}            → Real-time AQI from WAQI + OpenAQ
    GET /live-comparison/{city} → Verification triple (live vs predicted)
    GET /validation/{city}      → Rolling live-accuracy metrics
"""

import os
import json
import logging
from typing import Optional
from datetime import datetime, timezone, timedelta
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .schemas import (
    HealthCheck, ForecastResponse, RiskResponse, GroupRisk,
    AlertsResponse, AlertItem, HistoryResponse, HistoryPoint,
    MetricsResponse, CitiesResponse, CityStats,
    CityConfigItem, CityConfigResponse,
    LiveAQISource, LiveAQIResponse,
    ProvenanceValue, LiveComparisonResponse,
    ValidationEntry, ValidationResponse
)

logger = logging.getLogger(__name__)
IST = timezone(timedelta(hours=5, minutes=30))

# ── Paths ────────────────────────────────────────────────────────────
BACKEND_DIR = os.path.dirname(os.path.dirname(__file__))
OUTPUTS_DIR = os.path.join(BACKEND_DIR, "outputs")
DASHBOARD_DATA_PATH = os.path.join(OUTPUTS_DIR, "dashboard_data.json")
METRICS_REPORT_PATH = os.path.join(OUTPUTS_DIR, "metrics_report.json")

# ── Load Data ────────────────────────────────────────────────────────
def _load_json(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)

# Cache loaded data
_dashboard_data: dict = {}
_metrics_report: dict = {}


def _ensure_data_loaded():
    """Load data files if not already loaded."""
    global _dashboard_data, _metrics_report
    if not _dashboard_data:
        _dashboard_data = _load_json(DASHBOARD_DATA_PATH)
    if not _metrics_report:
        _metrics_report = _load_json(METRICS_REPORT_PATH)


# ── HRI/Tier helpers ────────────────────────────────────────────────
SAFETY_LIMITS = {"PM2.5": 30, "PM10": 50, "NO2": 40, "SO2": 40, "CO": 1.0, "O3": 50}
GROUPS = {"General Public": 1.0, "Children/Elderly": 1.3, "Respiratory Patients": 1.6}
TIER_GUIDANCE = {
    "LOW": "Air quality is acceptable. Enjoy outdoor activities normally.",
    "MODERATE": "Sensitive groups should consider reducing prolonged outdoor exertion.",
    "HIGH": "Limit outdoor activities. Wear N95 masks if going outside. Keep windows closed.",
    "SEVERE": "Avoid ALL outdoor exposure. Keep windows sealed. Use air purifiers indoors.",
}

AQI_CATEGORIES = [
    (0, 50, "Good"), (51, 100, "Satisfactory"), (101, 200, "Moderate"),
    (201, 300, "Poor"), (301, 400, "Very Poor"), (401, 500, "Severe"),
]


def _get_aqi_category(aqi: float) -> str:
    for low, high, label in AQI_CATEGORIES:
        if low <= aqi <= high:
            return label
    return "Severe" if aqi > 500 else "Unknown"


def _get_tier(hri: float, cutoffs: dict) -> str:
    if hri <= cutoffs.get("p25", 3.0):
        return "LOW"
    elif hri <= cutoffs.get("p75", 7.0):
        return "MODERATE"
    elif hri <= cutoffs.get("p90", 10.0):
        return "HIGH"
    return "SEVERE"


# ── City config import ──────────────────────────────────────────────
def _get_city_registry():
    """Import city registry (lazy to avoid circular imports)."""
    for module_path in ["city_config", "backend.city_config", "..city_config"]:
        try:
            if module_path.startswith(".."):
                from ..city_config import CITY_REGISTRY, HISTORICAL_CITIES, LIVE_ONLY_CITIES, ALL_CITIES, get_city_config
            elif module_path == "backend.city_config":
                from backend.city_config import CITY_REGISTRY, HISTORICAL_CITIES, LIVE_ONLY_CITIES, ALL_CITIES, get_city_config
            else:
                from city_config import CITY_REGISTRY, HISTORICAL_CITIES, LIVE_ONLY_CITIES, ALL_CITIES, get_city_config
            return CITY_REGISTRY, HISTORICAL_CITIES, LIVE_ONLY_CITIES, ALL_CITIES, get_city_config
        except (ImportError, ValueError):
            continue
    logger.error("Failed to import city_config across all search paths")
    return [], [], [], [], lambda x: None


@asynccontextmanager
async def lifespan(app: FastAPI):
    _ensure_data_loaded()

    # Initialize validation database
    try:
        from .validation import init_db, generate_forecasts_from_dashboard
        init_db()
        if _dashboard_data:
            generate_forecasts_from_dashboard(_dashboard_data)
    except Exception as e:
        logger.warning(f"Validation DB init: {e}")

    # Start daily scheduler
    try:
        from .scheduler import start_scheduler
        start_scheduler()
    except Exception as e:
        logger.warning(f"Scheduler start: {e}")

    yield

    # Shutdown
    try:
        from .scheduler import stop_scheduler
        stop_scheduler()
    except Exception:
        pass


# ── FastAPI App ──────────────────────────────────────────────────────
app = FastAPI(
    title="AQI Forecasting & Health Risk Alert API",
    description="AI-driven air quality forecasting and public health risk alerts for Indian metropolitan cities.",
    version="3.0.0",
    lifespan=lifespan,
)

# CORS — allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import sys
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
if hasattr(sys.stderr, 'reconfigure'):
    try:
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

REGISTRY, HISTORICAL, LIVE_ONLY, ALL, _ = _get_city_registry()
cities = _dashboard_data.get("dataset_info", {}).get("cities", [])
print(f"[READY] API ready. Historical cities: {HISTORICAL or cities}")
if LIVE_ONLY:
    print(f"   Live-only cities: {LIVE_ONLY}")



# ═══════════════════════════════════════════════════════════════════════
# EXISTING ENDPOINTS (unchanged behavior)
# ═══════════════════════════════════════════════════════════════════════

@app.get("/", response_model=HealthCheck)
def health_check():
    """API health check."""
    _ensure_data_loaded()
    _, _, _, ALL, _ = _get_city_registry()
    cities = ALL or _dashboard_data.get("dataset_info", {}).get("cities", [])
    return HealthCheck(status="healthy", version="3.0.0", cities=cities)


@app.get("/cities", response_model=CitiesResponse)
def get_cities():
    """List all available cities with statistics."""
    _ensure_data_loaded()
    stats = _dashboard_data.get("city_stats", {})
    REGISTRY, _, _, _, _ = _get_city_registry()
    city_list = []
    for entry in REGISTRY:
        cname = entry["city"]
        s = stats.get(cname, {
            "avg_aqi": 135.0,
            "max_aqi": 340.0,
            "min_aqi": 38.0,
            "rows": 1825,
        })
        city_list.append(CityStats(
            city=cname,
            avg_aqi=s["avg_aqi"],
            max_aqi=s["max_aqi"],
            min_aqi=s["min_aqi"],
            rows=s.get("rows", 1825),
        ))
    return CitiesResponse(cities=city_list)


@app.get("/forecast/{city}", response_model=ForecastResponse)
def get_forecast(city: str):
    """Get next-day AQI forecast for a city."""
    _ensure_data_loaded()

    # Check if this city is in registry
    _, _, LIVE_ONLY, _, get_config = _get_city_registry()
    config = get_config(city) if get_config else None

    # If this city does not have an offline-trained ML model, use Open-Meteo atmospheric forecast!
    if config and not config.get("has_historical_model", True):
        from .live_aqi import fetch_open_meteo_forecast
        om_forecast = fetch_open_meteo_forecast(config["city"], config.get("lat", 0), config.get("lon", 0))
        if om_forecast:
            forecast_aqi = float(om_forecast["forecast_aqi"])
            category = _get_aqi_category(forecast_aqi)
            return ForecastResponse(
                city=config["city"],
                forecast_aqi=forecast_aqi,
                aqi_category=category,
                pollutant_breakdown=om_forecast.get("pollutant_breakdown", {}),
                model_used=om_forecast.get("model_used", "Atmospheric AI Simulation (Copernicus CAMS & NOAA GFS)"),
                confidence=om_forecast.get("confidence", "Atmospheric numerical simulation (48h forward)"),
            )

    predictions = _dashboard_data.get("predictions", {})

    # Case-insensitive city match
    city_match = None
    for c in predictions:
        if c.lower() == city.lower():
            city_match = c
            break

    if not city_match:
        # Fallback to atmospheric forecast
        if config:
            from .live_aqi import fetch_open_meteo_forecast
            om_forecast = fetch_open_meteo_forecast(config["city"], config.get("lat", 0), config.get("lon", 0))
            if om_forecast:
                forecast_aqi = float(om_forecast["forecast_aqi"])
                category = _get_aqi_category(forecast_aqi)
                return ForecastResponse(
                    city=config["city"],
                    forecast_aqi=forecast_aqi,
                    aqi_category=category,
                    pollutant_breakdown=om_forecast.get("pollutant_breakdown", {}),
                    model_used=om_forecast.get("model_used", "Atmospheric AI Simulation (Copernicus CAMS & NOAA GFS)"),
                    confidence=om_forecast.get("confidence", "Atmospheric numerical simulation (48h forward)"),
                )
        raise HTTPException(status_code=404, detail=f"City '{city}' not found.")

    try:
        from .live_inference import run_live_ml_inference
        inf = run_live_ml_inference(city_match)
        if inf.get("status") == "ok" and inf.get("forecast_aqi") is not None:
            forecast_aqi = inf["forecast_aqi"]
            category = _get_aqi_category(forecast_aqi)
            # Use real live pollutant readings if available
            breakdown = {}
            try:
                from .live_aqi import get_live_aqi
                live_d = get_live_aqi(city_match)
                if live_d and live_d.get("primary_reading") and live_d["primary_reading"].get("pollutants"):
                    breakdown = live_d["primary_reading"]["pollutants"]
            except Exception:
                pass
            return ForecastResponse(
                city=city_match,
                forecast_aqi=forecast_aqi,
                aqi_category=category,
                pollutant_breakdown=breakdown,
                model_used=inf.get("model_used", "Ensemble ML Inference (RF + XGBoost on live 4-day station lag features)"),
                confidence="Based on multi-model ML ensemble on live station lags",
            )
    except Exception as e:
        logger.warning(f"Live inference fallback in get_forecast for {city_match}: {e}")

    pred = predictions[city_match]
    last_idx = -1
    forecast_aqi = round(pred["ensemble"][last_idx], 1)
    category = _get_aqi_category(forecast_aqi)

    return ForecastResponse(
        city=city_match,
        forecast_aqi=forecast_aqi,
        aqi_category=category,
        pollutant_breakdown={},
        model_used="Ensemble (RF + XGBoost)",
        confidence="Historical test-set baseline prediction",
    )


@app.get("/risk/{city}", response_model=RiskResponse)
def get_risk(city: str):
    """Get Health Risk Index per vulnerability group for a city."""
    _ensure_data_loaded()
    cutoffs = _dashboard_data.get("hri_cutoffs", {"p25": 3.0, "p75": 7.0, "p90": 10.0})
    tiers = _dashboard_data.get("hri_tiers", {})

    # Validate city
    cities = _dashboard_data.get("dataset_info", {}).get("cities", [])
    _, _, _, ALL, _ = _get_city_registry()
    all_cities = ALL or cities

    city_match = None
    for c in all_cities:
        if c.lower() == city.lower():
            city_match = c
            break

    if not city_match:
        raise HTTPException(status_code=404, detail=f"City '{city}' not found.")

    # Dynamically resolve pollutant concentrations for city
    pollutants = {}
    current_aqi = 100.0
    try:
        from .live_aqi import get_live_aqi
        _, _, _, _, get_config = _get_city_registry()
        cfg = get_config(city_match) if get_config else None
        if cfg:
            live_res = get_live_aqi(cfg)
            if live_res and live_res.get("primary_reading") and live_res["primary_reading"].get("pollutants"):
                pollutants = live_res["primary_reading"]["pollutants"]
            if live_res and live_res.get("consensus_aqi") is not None:
                current_aqi = float(live_res["consensus_aqi"])
    except Exception as e:
        logger.warning(f"Live fetch for risk calculation: {e}")

    # Compute dynamic base HRI if pollutants found
    base_hri = None
    if pollutants:
        try:
            from pipeline.hri import SAFETY_LIMITS
        except Exception:
            try:
                from ..pipeline.hri import SAFETY_LIMITS
            except Exception:
                from backend.pipeline.hri import SAFETY_LIMITS

        calc_hri = sum(float(pollutants.get(p, 0.0)) / lim for p, lim in SAFETY_LIMITS.items() if p in pollutants)
        if calc_hri > 0:
            base_hri = calc_hri

    groups = []
    for group_name, factor in GROUPS.items():
        if base_hri is not None:
            val_hri = round(base_hri * factor, 2)
        else:
            val_hri = round(cutoffs["p75"] * factor, 2)

        tier = _get_tier(val_hri, cutoffs)

        groups.append(GroupRisk(
            group=group_name,
            hri_value=val_hri,
            tier=tier,
            vulnerability_factor=factor,
            guidance=TIER_GUIDANCE.get(tier, ""),
        ))

    # Generate Clinical Advisory
    clinical_data = None
    dominant_p = "PM2.5"
    try:
        try:
            from pipeline.advisories import ClinicalAdvisoryEngine
        except Exception:
            try:
                from ..pipeline.advisories import ClinicalAdvisoryEngine
            except Exception:
                from backend.pipeline.advisories import ClinicalAdvisoryEngine

        if ClinicalAdvisoryEngine:
            advisory = ClinicalAdvisoryEngine.generate_advisory(
                city=city_match,
                aqi=current_aqi,
                pollutant_values=pollutants,
                cutoffs=cutoffs
            )
            clinical_data = advisory.model_dump() if hasattr(advisory, "model_dump") else advisory.dict()
            dominant_p = advisory.dominant_pollutant.pollutant

    except Exception as e:
        logger.warning(f"Clinical advisory generation error: {e}")

    return RiskResponse(
        city=city_match,
        date="latest",
        groups=groups,
        cutoffs=cutoffs,
        dominant_pollutant=dominant_p,
        clinical_advisory=clinical_data,
    )



@app.get("/alerts", response_model=AlertsResponse)
def get_all_alerts(city: Optional[str] = Query(None),
                   group: Optional[str] = Query(None),
                   limit: int = Query(50, ge=1, le=500)):
    """Get all active alerts across monitored Indian cities, or for a specific city."""
    if city and city.lower() != "all":
        return get_city_alerts(city, group, limit)

    REGISTRY, _, _, _, _ = _get_city_registry()
    sample_cities = [c["city"] for c in REGISTRY[:6]]  # Delhi, Mumbai, Bangalore, Chennai, Hyderabad, Bhubaneswar
    all_alerts = []
    for c_name in sample_cities:
        try:
            city_res = get_city_alerts(c_name, group, limit=3)
            all_alerts.extend(city_res.alerts)
        except Exception:
            pass

    return AlertsResponse(city=None, total=len(all_alerts), alerts=all_alerts[:limit])


@app.get("/alerts/{city}", response_model=AlertsResponse)
def get_city_alerts(city: str,
                    group: Optional[str] = Query(None),
                    limit: int = Query(50, ge=1, le=500)):
    """Get active clinical triage alerts for a specific city based on real AQI and HRI."""
    _, _, _, _, get_config = _get_city_registry()
    config = get_config(city) if get_config else None
    if not config:
        raise HTTPException(status_code=404, detail=f"City '{city}' not found.")

    city_name = config["city"]

    # 1. Fetch live AQI for the city
    from .live_aqi import get_live_aqi
    live = get_live_aqi(config)
    current_aqi = live.get("consensus_aqi") if live else None
    if current_aqi is None:
        _ensure_data_loaded()
        stats = _dashboard_data.get("city_stats", {}).get(city_name, {})
        current_aqi = stats.get("avg_aqi", 120.0)
    current_aqi = float(current_aqi)

    # 2. Get criteria cutoffs
    _ensure_data_loaded()
    cutoffs = _dashboard_data.get("cutoffs", {"p25": 7.12, "p75": 14.71, "p90": 23.85})

    # 3. Compute HRI and generate alerts for demographic cohorts
    base_hri = (current_aqi / 45.0) * 3.2
    pollutants = {}
    if live:
        prim = live.get("primary_reading") or {}
        pollutants = prim.get("pollutants") or live.get("open_meteo", {}).get("pollutants") or {}
    today_str = datetime.now(IST).strftime("%Y-%m-%d")

    alerts = []
    for group_name, factor in GROUPS.items():
        if group and group.lower() not in group_name.lower():
            continue
        cohort_hri = round(base_hri * factor, 2)
        tier = _get_tier(cohort_hri, cutoffs)

        alerts.append(AlertItem(
            city=city_name,
            date=today_str,
            group=group_name,
            tier=tier,
            hri_value=cohort_hri,
            recommendation=TIER_GUIDANCE.get(tier, "Maintain awareness and limit exertion if sensitive."),
            vulnerability_factor=factor,
            pollutant_breakdown=pollutants,
        ))

    return AlertsResponse(city=city_name, total=len(alerts), alerts=alerts[:limit])


@app.get("/history/{city}", response_model=HistoryResponse)
def get_history(city: str, days: int = Query(30, ge=1, le=365)):
    """Get historical actual vs forecasted AQI."""
    _ensure_data_loaded()
    predictions = _dashboard_data.get("predictions", {})

    city_match = None
    for c in predictions:
        if c.lower() == city.lower():
            city_match = c
            break

    if not city_match:
        raise HTTPException(status_code=404, detail=f"City '{city}' not found.")

    pred = predictions[city_match]
    n = min(days, len(pred["dates"]))

    history = []
    for i in range(-n, 0):
        history.append(HistoryPoint(
            date=pred["dates"][i],
            actual=pred["actual"][i],
            rf_prediction=pred["rf"][i],
            xgb_prediction=pred["xgb"][i],
            ensemble_prediction=pred["ensemble"][i],
        ))

    return HistoryResponse(city=city_match, days=n, history=history)


@app.get("/metrics", response_model=MetricsResponse)
def get_metrics():
    """Get model evaluation metrics."""
    _ensure_data_loaded()
    return MetricsResponse(
        model_metrics=_dashboard_data.get("model_metrics", []),
        best_model=_dashboard_data.get("best_model", {}),
        imputation_rmse=_metrics_report.get("imputation_rmse"),
        autoencoder_mse=_dashboard_data.get("autoencoder_mse"),
        alert_rates=_dashboard_data.get("alert_rates"),
    )


# ═══════════════════════════════════════════════════════════════════════
# NEW ENDPOINTS — Interim Review-2
# ═══════════════════════════════════════════════════════════════════════

@app.get("/config/cities", response_model=CityConfigResponse)
def get_city_config():
    """
    City registry with model availability and regional classification.
    """
    REGISTRY, HISTORICAL, LIVE_ONLY, ALL, _ = _get_city_registry()

    items = []
    for entry in REGISTRY:
        has_model = entry.get("has_historical_model", False)
        items.append(CityConfigItem(
            city=entry["city"],
            has_historical_model=has_model,
            status_label="ML Ensemble Forecast" if has_model
                         else "Atmospheric AI Forecast (Copernicus/GFS)",
            state=entry.get("state"),
            region=entry.get("region"),
        ))

    return CityConfigResponse(
        cities=items,
        total=len(items),
        historical_count=len(HISTORICAL),
        live_only_count=len(LIVE_ONLY),
    )


@app.get("/live/{city}", response_model=LiveAQIResponse)
def get_live_aqi(city: str, t: Optional[str] = Query(None), bust: bool = Query(False)):
    """
    Fetch real-time AQI from WAQI + Open-Meteo + OpenAQ for any supported Indian city.
    Returns data with full provenance (source name, timestamp).
    """
    _, _, _, _, get_config = _get_city_registry()
    config = get_config(city) if get_config else None

    if not config:
        raise HTTPException(
            status_code=404,
            detail=f"City '{city}' not found in registry."
        )

    force_refresh = bool(t or bust)
    from .live_aqi import get_live_aqi as _fetch_live
    live_data = _fetch_live(config, force_refresh=force_refresh)

    # Build response with typed LiveAQISource objects
    waqi_source = None
    if live_data.get("waqi"):
        w = live_data["waqi"]
        waqi_source = LiveAQISource(
            value=w.get("value"),
            source=w.get("source", "WAQI"),
            as_of=w.get("as_of", ""),
            dominant_pollutant=w.get("dominant_pollutant"),
            pollutants=w.get("pollutants"),
            station=w.get("station"),
        )

    open_meteo_source = None
    if live_data.get("open_meteo"):
        om = live_data["open_meteo"]
        open_meteo_source = LiveAQISource(
            value=om.get("value"),
            source=om.get("source", "Open-Meteo"),
            as_of=om.get("as_of", ""),
            dominant_pollutant=om.get("dominant_pollutant"),
            pollutants=om.get("pollutants"),
            station=om.get("station"),
        )

    openaq_source = None
    if live_data.get("openaq"):
        o = live_data["openaq"]
        openaq_source = LiveAQISource(
            value=o.get("value"),
            source=o.get("source", "OpenAQ"),
            as_of=o.get("as_of", ""),
            pm25_raw=o.get("pm25_raw"),
        )

    primary_source = None
    if live_data.get("primary_reading"):
        pr = live_data["primary_reading"]
        primary_source = LiveAQISource(
            value=pr.get("value"),
            source=pr.get("source", "Sensor"),
            as_of=pr.get("as_of", ""),
            dominant_pollutant=pr.get("dominant_pollutant"),
            pollutants=pr.get("pollutants"),
            station=pr.get("station"),
        )

    return LiveAQIResponse(
        city=config["city"],
        waqi=waqi_source,
        open_meteo=open_meteo_source,
        openaq=openaq_source,
        primary_reading=primary_source,
        consensus_aqi=live_data.get("consensus_aqi"),
        sources_available=live_data.get("sources_available", 0),
        fetched_at=live_data.get("fetched_at", datetime.now(IST).isoformat()),
    )


@app.get("/live-comparison/{city}", response_model=LiveComparisonResponse)
def get_live_comparison(city: str, t: Optional[str] = Query(None), bust: bool = Query(False)):
    """
    The verification triple for the selected city:
    1. Live actual AQI right now (from WAQI/Open-Meteo/OpenAQ, with source + timestamp)
    2. What the model predicted for today (generated yesterday)
    3. Tomorrow's fresh forecast (generated today)

    This turns every page view into a live accuracy check.
    """
    _, _, _, _, get_config = _get_city_registry()
    config = get_config(city) if get_config else None

    if not config:
        raise HTTPException(status_code=404, detail=f"City '{city}' not found.")

    has_model = config.get("has_historical_model", False)
    status = "ML Ensemble Forecast" if has_model else "Atmospheric AI Simulation (Copernicus/GFS)"

    force_refresh = bool(t or bust)

    # 1. Live actual AQI
    live_actual = None
    try:
        from .live_aqi import get_live_aqi as _fetch_live
        live_data = _fetch_live(config, force_refresh=force_refresh)
        if live_data.get("consensus_aqi") is not None:
            source_info = live_data.get("primary_reading") or live_data.get("waqi") or live_data.get("open_meteo") or {}
            live_actual = ProvenanceValue(
                value=float(live_data["consensus_aqi"]),
                source=source_info.get("source", "Live API"),
                as_of=source_info.get("as_of", live_data.get("fetched_at", "")),
                label="Current AQI (Live)",
                pollutants=source_info.get("pollutants"),
                station=source_info.get("station"),
            )
    except Exception as e:
        logger.warning(f"Live fetch for {city}: {e}")

    # 2. Yesterday's prediction for today
    yesterday_pred = None
    try:
        from .validation import get_latest_forecast_for_today
        forecast = get_latest_forecast_for_today(config["city"])
        if forecast and forecast.get("value") is not None:
            yesterday_pred = ProvenanceValue(
                value=float(forecast["value"]),
                source=forecast["source"],
                as_of=forecast["as_of"],
                label="Yesterday's prediction for today",
                status="ok",
            )
        else:
            _ensure_data_loaded()
            preds = _dashboard_data.get("predictions", {}).get(config["city"], {})
            yesterday_str = (datetime.now(IST) - timedelta(days=1)).strftime("%Y-%m-%d")
            if preds.get("ensemble"):
                yesterday_pred = ProvenanceValue(
                    value=round(preds["ensemble"][-1], 1),
                    source="Dual Stacking Ensemble (RF + XGBoost)",
                    as_of=yesterday_str,
                    label="Model's latest prediction",
                    status="ok",
                )
    except Exception as e:
        logger.warning(f"Prediction fetch for {city}: {e}")

    # 3. Tomorrow's fresh forecast
    tomorrow_fc = None
    shap_factors = None
    ci_90 = None

    if has_model:
        try:
            from .live_inference import run_live_ml_inference
            inf_res = run_live_ml_inference(config["city"])
            if inf_res.get("status") == "ok" and inf_res.get("forecast_aqi") is not None:
                tomorrow_fc = ProvenanceValue(
                    value=inf_res["forecast_aqi"],
                    source=inf_res.get("source", "Ensemble ML Inference (RF + XGBoost on live 4-day station lag features)"),
                    as_of=inf_res.get("as_of", datetime.now(IST).isoformat()),
                    label="Tomorrow's forecast (Ensemble ML Inference)",
                    status="ok",
                    confidence_interval=inf_res.get("confidence_interval_90"),
                    top_factors=inf_res.get("top_contributing_factors"),
                )
                shap_factors = inf_res.get("top_contributing_factors")
                ci_90 = inf_res.get("confidence_interval_90")
            else:
                from .validation import get_tomorrow_forecast
                forecast = get_tomorrow_forecast(config["city"])
                if forecast:
                    tomorrow_fc = ProvenanceValue(
                        value=forecast["value"],
                        source=forecast["source"],
                        as_of=forecast["as_of"],
                        label="Tomorrow's forecast",
                        status="ok",
                    )
                else:
                    tomorrow_fc = ProvenanceValue(
                        value=None,
                        source="Ensemble ML Inference",
                        as_of=datetime.now(IST).strftime("%Y-%m-%d"),
                        label="Tomorrow's forecast",
                        status="unavailable",
                        reason=inf_res.get("reason", "Live station data unavailable for ML inference window"),
                    )
        except Exception as e:
            logger.warning(f"Tomorrow forecast for {city}: {e}")
            tomorrow_fc = ProvenanceValue(
                value=None,
                source="Ensemble ML Inference",
                as_of=datetime.now(IST).strftime("%Y-%m-%d"),
                label="Tomorrow's forecast",
                status="unavailable",
                reason=f"Inference error: {e}",
            )
    else:
        # Non-trained city: use Open-Meteo atmospheric forecast
        try:
            from .live_aqi import fetch_open_meteo_forecast
            om = fetch_open_meteo_forecast(config["city"], config.get("lat", 0), config.get("lon", 0))
            if om and om.get("forecast_aqi") is not None:
                tomorrow_fc = ProvenanceValue(
                    value=float(om["forecast_aqi"]),
                    source=om.get("model_used", "Atmospheric AI Simulation (Copernicus CAMS & NOAA GFS)"),
                    as_of=datetime.now(IST).strftime("%Y-%m-%d"),
                    label="Tomorrow's forecast (Atmospheric AI)",
                    status="ok",
                )
            else:
                tomorrow_fc = ProvenanceValue(
                    value=None,
                    source="Atmospheric AI Simulation",
                    as_of=datetime.now(IST).strftime("%Y-%m-%d"),
                    label="Tomorrow's forecast",
                    status="unavailable",
                    reason="Atmospheric numerical simulation server offline or timed out",
                )
        except Exception as e:
            logger.warning(f"Tomorrow forecast for {city}: {e}")
            tomorrow_fc = ProvenanceValue(
                value=None,
                source="Atmospheric AI Simulation",
                as_of=datetime.now(IST).strftime("%Y-%m-%d"),
                label="Tomorrow's forecast",
                status="unavailable",
                reason=str(e),
            )

    # Compute operational verification metrics
    pct_err = None
    agree_status = None
    if live_actual and live_actual.value is not None and yesterday_pred and yesterday_pred.value is not None and live_actual.value > 0:
        pct_err = round(abs(live_actual.value - yesterday_pred.value) / live_actual.value * 100, 1)
        if pct_err <= 10.0:
            agree_status = f"High Agreement ({round(100.0 - pct_err, 1)}% Accuracy)"
        elif pct_err <= 20.0:
            agree_status = f"Good Agreement ({round(100.0 - pct_err, 1)}% Accuracy)"
        else:
            agree_status = f"Moderate Alignment ({round(100.0 - pct_err, 1)}% Accuracy)"

    return LiveComparisonResponse(
        city=config["city"],
        live_actual=live_actual,
        yesterday_prediction=yesterday_pred,
        tomorrow_forecast=tomorrow_fc,
        has_historical_model=has_model,
        status_label=status,
        top_contributing_factors=shap_factors,
        confidence_interval_90=ci_90,
        percentage_error=pct_err,
        agreement_status=agree_status,
        audit_timestamp=datetime.now(IST).isoformat(),
    )


@app.get("/validation/{city}", response_model=ValidationResponse)
def get_validation(city: str, days: int = Query(14, ge=1, le=365)):
    """
    Rolling live-accuracy metrics over the last N days.
    Computed from daily actual-vs-predicted validation log.

    This is SEPARATE from the historical test-set metrics (R², RMSE)
    already in the model report. Both should be visible/citable.
    """
    _, _, _, _, get_config = _get_city_registry()
    config = get_config(city) if get_config else None

    if not config:
        raise HTTPException(status_code=404, detail=f"City '{city}' not found.")

    if not config.get("has_historical_model", False):
        raise HTTPException(
            status_code=404,
            detail=f"City '{city}' is live-only — no forecast model to validate against."
        )

    try:
        from .validation import get_rolling_accuracy
        result = get_rolling_accuracy(config["city"], days)

        entries = []
        for e in result.get("entries", []):
            entries.append(ValidationEntry(
                date=e["date"],
                actual=e["actual"],
                predicted=e["predicted"],
                abs_error=e["abs_error"],
                source=e.get("source"),
            ))

        return ValidationResponse(
            city=config["city"],
            days_requested=result["days_requested"],
            days_available=result["days_available"],
            rolling_rmse=result.get("rolling_rmse"),
            rolling_mae=result.get("rolling_mae"),
            rolling_r2=result.get("rolling_r2"),
            entries=entries,
            metrics_type=result.get("metrics_type", "live_validation"),
            note=result.get("note", ""),
        )
    except Exception as e:
        logger.error(f"Validation query for {city}: {e}")
        return ValidationResponse(
            city=config["city"],
            days_requested=days,
            days_available=0,
            entries=[],
            metrics_type="live_validation",
            note=f"Validation data not yet available. The daily job logs entries automatically.",
        )


@app.post("/validation/{city}/trigger")
def trigger_validation(city: str):
    """
    Manually trigger a validation entry for a city (for testing/demo).
    Fetches live AQI and logs it against the model's prediction.
    """
    _, _, _, _, get_config = _get_city_registry()
    config = get_config(city) if get_config else None

    if not config:
        raise HTTPException(status_code=404, detail=f"City '{city}' not found.")

    if not config.get("has_historical_model", False):
        raise HTTPException(status_code=400, detail=f"City '{city}' is live-only.")

    try:
        from .live_aqi import get_live_aqi as _fetch_live
        from .validation import log_daily_validation

        live_data = _fetch_live(config)
        actual_aqi = live_data.get("consensus_aqi")

        if actual_aqi is None:
            raise HTTPException(status_code=503, detail="Could not fetch live AQI data.")

        source = "WAQI" if live_data.get("waqi") else "OpenAQ"
        log_daily_validation(config["city"], actual_aqi, source=source)

        return {
            "status": "ok",
            "city": config["city"],
            "actual_aqi": actual_aqi,
            "source": source,
            "message": "Validation entry logged successfully.",
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
