"""
schemas.py
──────────
Pydantic models for FastAPI response types.
"""

from pydantic import BaseModel
from typing import Optional


class HealthCheck(BaseModel):
    status: str
    version: str
    cities: list[str]


class PollutantBreakdown(BaseModel):
    PM25: float
    PM10: float
    NO2: float
    SO2: float
    CO: float
    O3: float


class ForecastResponse(BaseModel):
    city: str
    forecast_aqi: float
    aqi_category: str
    pollutant_breakdown: dict[str, float]
    model_used: str
    confidence: Optional[str] = None


class GroupRisk(BaseModel):
    group: str
    hri_value: float
    tier: str
    vulnerability_factor: float
    guidance: str


class RiskResponse(BaseModel):
    city: str
    date: str
    groups: list[GroupRisk]
    cutoffs: dict[str, float]
    dominant_pollutant: Optional[str] = None
    clinical_advisory: Optional[dict] = None


class AlertItem(BaseModel):
    city: str
    date: str
    group: str
    tier: str
    hri_value: float
    recommendation: str
    vulnerability_factor: float
    pollutant_breakdown: dict[str, float]


class AlertsResponse(BaseModel):
    city: Optional[str]
    total: int
    alerts: list[AlertItem]


class HistoryPoint(BaseModel):
    date: str
    actual: float
    rf_prediction: float
    xgb_prediction: float
    ensemble_prediction: float


class HistoryResponse(BaseModel):
    city: str
    days: int
    history: list[HistoryPoint]


class MetricsResponse(BaseModel):
    model_metrics: list[dict]
    best_model: dict
    imputation_rmse: Optional[dict] = None
    autoencoder_mse: Optional[dict] = None
    alert_rates: Optional[dict] = None


class CityStats(BaseModel):
    city: str
    avg_aqi: float
    max_aqi: float
    min_aqi: float
    rows: int


class CitiesResponse(BaseModel):
    cities: list[CityStats]


# ── New schemas for Interim Review-2 ────────────────────────────────

class CityConfigItem(BaseModel):
    city: str
    has_historical_model: bool
    status_label: str  # "ML Ensemble Forecast" or "Atmospheric AI Model Forecast"
    state: Optional[str] = None
    region: Optional[str] = None


class CityConfigResponse(BaseModel):
    cities: list[CityConfigItem]
    total: int
    historical_count: int
    live_only_count: int


class LiveAQISource(BaseModel):
    value: Optional[float] = None
    source: str
    as_of: str
    dominant_pollutant: Optional[str] = None
    pollutants: Optional[dict[str, float]] = None
    station: Optional[str] = None
    pm25_raw: Optional[float] = None


class LiveAQIResponse(BaseModel):
    city: str
    waqi: Optional[LiveAQISource] = None
    open_meteo: Optional[LiveAQISource] = None
    openaq: Optional[LiveAQISource] = None
    primary_reading: Optional[LiveAQISource] = None
    consensus_aqi: Optional[float] = None
    sources_available: int
    fetched_at: str


class ConfidenceInterval(BaseModel):
    lower: Optional[float] = None
    upper: Optional[float] = None
    margin: Optional[float] = None


class ShapFactor(BaseModel):
    feature: str
    display_name: str
    impact: float
    direction: str
    feature_value: Optional[float] = None


class ProvenanceValue(BaseModel):
    """A single number with its source and timestamp."""
    value: Optional[float] = None
    source: str
    as_of: str
    label: Optional[str] = None
    status: Optional[str] = "ok"
    reason: Optional[str] = None
    confidence_interval: Optional[ConfidenceInterval] = None
    top_factors: Optional[list[ShapFactor]] = None
    pollutants: Optional[dict[str, float]] = None
    station: Optional[str] = None


class LiveComparisonResponse(BaseModel):
    """The verification triple: live actual, yesterday's prediction, tomorrow's forecast."""
    city: str
    live_actual: Optional[ProvenanceValue] = None
    yesterday_prediction: Optional[ProvenanceValue] = None
    tomorrow_forecast: Optional[ProvenanceValue] = None
    has_historical_model: bool
    status_label: str
    top_contributing_factors: Optional[list[ShapFactor]] = None
    confidence_interval_90: Optional[ConfidenceInterval] = None
    percentage_error: Optional[float] = None
    agreement_status: Optional[str] = None
    audit_timestamp: Optional[str] = None


class ValidationEntry(BaseModel):
    date: str
    actual: float
    predicted: float
    abs_error: float
    source: Optional[str] = None


class ValidationResponse(BaseModel):
    city: str
    days_requested: int
    days_available: int
    rolling_rmse: Optional[float] = None
    rolling_mae: Optional[float] = None
    rolling_r2: Optional[float] = None
    entries: list[ValidationEntry]
    metrics_type: str  # "live_validation" — distinct from historical test-set
    note: str
