"""
live_aqi.py
───────────
Fetches real-time AQI and forecasts from multiple independent sources:
  1. WAQI (World Air Quality Index) — official CPCB ground monitoring stations
  2. Open-Meteo Air Quality — satellite & numerical atmospheric models (Copernicus CAMS & NOAA GFS)
     * 100% Free, ZERO API keys needed, works for all 35+ Indian cities
  3. OpenAQ v3 — open sensor network & US Embassy monitors (optional key)

Includes in-memory caching (15-min TTL), automatic zero-key fallback, and full data provenance.
"""

import os
import time
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

import requests
from dotenv import load_dotenv

# Load .env file automatically
load_dotenv()

logger = logging.getLogger(__name__)

# ── Config ───────────────────────────────────────────────────────────
WAQI_TOKEN = os.environ.get("WAQI_API_TOKEN", "demo").strip()
OPENAQ_KEY = os.environ.get("OPENAQ_API_KEY", "").strip()
CACHE_TTL_SECONDS = 120  # 2 minutes for real-time freshness
IST = timezone(timedelta(hours=5, minutes=30))

# ── In-memory cache ──────────────────────────────────────────────────
_cache: dict[str, dict] = {}


def _cache_key(city: str, source: str) -> str:
    return f"{city.lower()}:{source}"


def _get_cached(city: str, source: str) -> Optional[dict]:
    key = _cache_key(city, source)
    entry = _cache.get(key)
    if entry and (time.time() - entry.get("_fetched_at", 0)) < CACHE_TTL_SECONDS:
        return entry
    return None


def _set_cached(city: str, source: str, data: dict) -> dict:
    data["_fetched_at"] = time.time()
    _cache[_cache_key(city, source)] = data
    return data


# ── India NAQI Sub-Index Calculation (Official CPCB Technical Manual) ────
def pm25_to_aqi(pm25: float) -> int:
    """Convert PM2.5 concentration (µg/m³) to AQI sub-index (India NAQI scale)."""
    if pm25 is None or pm25 < 0:
        return 0
    breakpoints = [
        (0.0, 30.0, 0, 50),
        (30.1, 60.0, 51, 100),
        (60.1, 90.0, 101, 200),
        (90.1, 120.0, 201, 300),
        (120.1, 250.0, 301, 400),
        (250.1, 500.0, 401, 500),
    ]
    for bp_lo, bp_hi, i_lo, i_hi in breakpoints:
        if pm25 <= bp_hi:
            aqi = ((i_hi - i_lo) / (bp_hi - bp_lo)) * (pm25 - bp_lo) + i_lo
            return max(0, min(500, round(aqi)))
    return 500


def pm10_to_aqi(pm10: float) -> int:
    """Convert PM10 concentration (µg/m³) to AQI sub-index (India NAQI scale)."""
    if pm10 is None or pm10 < 0:
        return 0
    breakpoints = [
        (0.0, 50.0, 0, 50),
        (50.1, 100.0, 51, 100),
        (100.1, 250.0, 101, 200),
        (250.1, 350.0, 201, 300),
        (350.1, 430.0, 301, 400),
        (430.1, 600.0, 401, 500),
    ]
    for bp_lo, bp_hi, i_lo, i_hi in breakpoints:
        if pm10 <= bp_hi:
            aqi = ((i_hi - i_lo) / (bp_hi - bp_lo)) * (pm10 - bp_lo) + i_lo
            return max(0, min(500, round(aqi)))
    return 500


def no2_to_aqi(no2: float) -> int:
    """Convert NO2 concentration (µg/m³) to AQI sub-index (India NAQI scale)."""
    if no2 is None or no2 < 0:
        return 0
    breakpoints = [
        (0.0, 40.0, 0, 50),
        (40.1, 80.0, 51, 100),
        (80.1, 180.0, 101, 200),
        (180.1, 280.0, 201, 300),
        (280.1, 400.0, 301, 400),
        (400.1, 800.0, 401, 500),
    ]
    for bp_lo, bp_hi, i_lo, i_hi in breakpoints:
        if no2 <= bp_hi:
            aqi = ((i_hi - i_lo) / (bp_hi - bp_lo)) * (no2 - bp_lo) + i_lo
            return max(0, min(500, round(aqi)))
    return 500


def so2_to_aqi(so2: float) -> int:
    """Convert SO2 concentration (µg/m³) to AQI sub-index (India NAQI scale)."""
    if so2 is None or so2 < 0:
        return 0
    breakpoints = [
        (0.0, 40.0, 0, 50),
        (40.1, 80.0, 51, 100),
        (80.1, 380.0, 101, 200),
        (380.1, 800.0, 201, 300),
        (800.1, 1600.0, 301, 400),
    ]
    for bp_lo, bp_hi, i_lo, i_hi in breakpoints:
        if so2 <= bp_hi:
            aqi = ((i_hi - i_lo) / (bp_hi - bp_lo)) * (so2 - bp_lo) + i_lo
            return max(0, min(500, round(aqi)))
    return 500


def co_to_aqi(co: float) -> int:
    """Convert CO concentration (mg/m³) to AQI sub-index (India NAQI scale)."""
    if co is None or co < 0:
        return 0
    breakpoints = [
        (0.0, 1.0, 0, 50),
        (1.01, 2.0, 51, 100),
        (2.01, 10.0, 101, 200),
        (10.01, 17.0, 201, 300),
        (17.01, 34.0, 301, 400),
    ]
    for bp_lo, bp_hi, i_lo, i_hi in breakpoints:
        if co <= bp_hi:
            aqi = ((i_hi - i_lo) / (bp_hi - bp_lo)) * (co - bp_lo) + i_lo
            return max(0, min(500, round(aqi)))
    return 500


def o3_to_aqi(o3: float) -> int:
    """Convert O3 concentration (µg/m³) to AQI sub-index (India NAQI scale)."""
    if o3 is None or o3 < 0:
        return 0
    breakpoints = [
        (0.0, 50.0, 0, 50),
        (50.1, 100.0, 51, 100),
        (101.0, 168.0, 101, 200),
        (168.1, 208.0, 201, 300),
        (208.1, 748.0, 301, 400),
    ]
    for bp_lo, bp_hi, i_lo, i_hi in breakpoints:
        if o3 <= bp_hi:
            aqi = ((i_hi - i_lo) / (bp_hi - bp_lo)) * (o3 - bp_lo) + i_lo
            return max(0, min(500, round(aqi)))
    return 500


# ── 1. WAQI (CPCB Ground Stations) ───────────────────────────────────
def fetch_waqi(city_waqi_name: str) -> Optional[dict]:
    """
    Fetch current AQI from WAQI.
    Rejects demo redirects (station 1437 / Shanghai).
    """
    cached = _get_cached(city_waqi_name, "waqi")
    if cached:
        return {k: v for k, v in cached.items() if not k.startswith("_")}

    # If token is empty or demo, skip WAQI to prevent 8-10s timeout hangs
    if not WAQI_TOKEN or WAQI_TOKEN.lower() == "demo":
        return None

    url = f"https://api.waqi.info/feed/{city_waqi_name}/?token={WAQI_TOKEN}"
    try:
        resp = requests.get(url, timeout=4)
        resp.raise_for_status()
        data = resp.json()

        if data.get("status") != "ok":
            logger.warning(f"WAQI non-ok status for {city_waqi_name}: {data.get('data')}")
            return None

        feed = data.get("data", {})
        station_idx = feed.get("idx")

        # Guard against WAQI 'demo' token redirecting to Shanghai (station 1437)
        if station_idx == 1437 and "shanghai" not in city_waqi_name.lower():
            logger.warning(f"WAQI demo token redirected {city_waqi_name} to Shanghai (idx 1437). Ignoring.")
            return None

        aqi_val = feed.get("aqi")
        if aqi_val is None or not isinstance(aqi_val, (int, float)):
            return None

        # Extract timestamp
        time_info = feed.get("time", {})
        iso_time = time_info.get("iso", "")
        if not iso_time:
            iso_time = datetime.now(IST).isoformat()

        # Extract individual pollutant values
        iaqi = feed.get("iaqi", {})
        pollutants = {}
        for key in ["pm25", "pm10", "no2", "so2", "co", "o3"]:
            if key in iaqi and "v" in iaqi[key]:
                pollutants[key] = iaqi[key]["v"]

        station_name = feed.get("city", {}).get("name", f"{city_waqi_name.title()} CPCB Station")

        result = {
            "value": round(float(aqi_val)),
            "source": f"WAQI CPCB ({station_name})",
            "as_of": iso_time,
            "dominant_pollutant": feed.get("dominentpol", "pm25"),
            "pollutants": pollutants,
            "station": station_name,
        }

        _set_cached(city_waqi_name, "waqi", result)
        return result

    except Exception as e:
        logger.error(f"WAQI fetch failed for {city_waqi_name}: {e}")
        return None


# ── 2. Open-Meteo Air Quality (Zero-Key Copernicus CAMS & NOAA GFS) ───
def fetch_open_meteo(city_name: str, lat: float, lon: float) -> Optional[dict]:
    """
    Fetch live air quality for coordinates from Open-Meteo Air Quality API.
    Zero API key required. High reliability.
    """
    cached = _get_cached(city_name, "open_meteo")
    if cached:
        return {k: v for k, v in cached.items() if not k.startswith("_")}

    if not lat or not lon:
        return None

    try:
        url = (
            f"https://air-quality-api.open-meteo.com/v1/air-quality"
            f"?latitude={lat}&longitude={lon}"
            f"&current=pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone,us_aqi"
        )
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        current = data.get("current", {})

        pm25 = current.get("pm2_5")
        pm10 = current.get("pm10")

        # Compute official India NAQI sub-indices across all criteria pollutants
        sub_indices = {}
        if pm25 is not None:
            sub_indices["pm25"] = pm25_to_aqi(pm25)
        if pm10 is not None:
            sub_indices["pm10"] = pm10_to_aqi(pm10)
        if current.get("nitrogen_dioxide") is not None:
            sub_indices["no2"] = no2_to_aqi(current["nitrogen_dioxide"])
        if current.get("sulphur_dioxide") is not None:
            sub_indices["so2"] = so2_to_aqi(current["sulphur_dioxide"])
        if current.get("carbon_monoxide") is not None:
            sub_indices["co"] = co_to_aqi(current["carbon_monoxide"] / 1000)
        if current.get("ozone") is not None:
            sub_indices["o3"] = o3_to_aqi(current["ozone"])

        if not sub_indices:
            return None

        dominant_pol, final_aqi = max(sub_indices.items(), key=lambda x: x[1])

        pollutants = {}
        if pm25 is not None:
            pollutants["pm25"] = round(pm25, 1)
        if pm10 is not None:
            pollutants["pm10"] = round(pm10, 1)
        if current.get("nitrogen_dioxide") is not None:
            pollutants["no2"] = round(current["nitrogen_dioxide"], 1)
        if current.get("sulphur_dioxide") is not None:
            pollutants["so2"] = round(current["sulphur_dioxide"], 1)
        if current.get("carbon_monoxide") is not None:
            pollutants["co"] = round(current["carbon_monoxide"] / 1000, 2)  # µg/m³ to mg/m³
        if current.get("ozone") is not None:
            pollutants["o3"] = round(current["ozone"], 1)

        result = {
            "value": round(final_aqi),
            "source": "Open-Meteo (Copernicus CAMS)",
            "as_of": current.get("time", datetime.now(IST).isoformat()),
            "dominant_pollutant": dominant_pol,
            "pollutants": pollutants,
            "station": f"Atmospheric Grid ({round(lat, 2)}°N, {round(lon, 2)}°E)",
        }

        _set_cached(city_name, "open_meteo", result)
        return result

    except Exception as e:
        logger.error(f"Open-Meteo fetch failed for {city_name}: {e}")
        return None


def fetch_open_meteo_forecast(city_name: str, lat: float, lon: float, force_refresh: bool = False) -> Optional[dict]:
    """
    Fetch 24-48h forward air quality forecast from Open-Meteo.
    Returns tomorrow's predicted average AQI and pollutant breakdown using India NAQI.
    """
    if not force_refresh:
        cached = _get_cached(city_name, "open_meteo_forecast")
        if cached:
            return {k: v for k, v in cached.items() if not k.startswith("_")}

    if not lat or not lon:
        return None

    try:
        url = (
            f"https://air-quality-api.open-meteo.com/v1/air-quality"
            f"?latitude={lat}&longitude={lon}"
            f"&hourly=pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone,us_aqi"
            f"&forecast_days=2"
        )
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        hourly = data.get("hourly", {})

        times = hourly.get("time", [])
        if len(times) < 36:
            return None

        # Tomorrow is typically hours 24 to 48
        tmrw_slice = slice(24, min(48, len(times)))

        def _mean(arr):
            sub = [v for v in arr[tmrw_slice] if v is not None]
            return sum(sub) / len(sub) if sub else 0.0

        pm25_avg = _mean(hourly.get("pm2_5", []))
        pm10_avg = _mean(hourly.get("pm10", []))
        no2_avg = _mean(hourly.get("nitrogen_dioxide", []))
        so2_avg = _mean(hourly.get("sulphur_dioxide", []))
        co_avg = _mean(hourly.get("carbon_monoxide", [])) / 1000
        o3_avg = _mean(hourly.get("ozone", []))

        # Determine predicted AQI strictly via India NAQI sub-indices
        forecast_subs = [
            pm25_to_aqi(pm25_avg),
            pm10_to_aqi(pm10_avg),
            no2_to_aqi(no2_avg),
            so2_to_aqi(so2_avg),
            co_to_aqi(co_avg),
            o3_to_aqi(o3_avg),
        ]
        predicted_aqi = max(forecast_subs)

        breakdown = {
            "PM2.5": round(pm25_avg, 1),
            "PM10": round(pm10_avg, 1),
            "NO2": round(no2_avg, 1),
            "SO2": round(so2_avg, 1),
            "CO": round(co_avg, 2),
            "O3": round(o3_avg, 1),
        }

        result = {
            "city": city_name,
            "forecast_aqi": predicted_aqi,
            "pollutant_breakdown": breakdown,
            "model_used": "Atmospheric AI Simulation (Copernicus CAMS & NOAA GFS)",
            "confidence": "Atmospheric numerical simulation (48h forward)",
            "source": "Open-Meteo Air Quality Model",
        }

        _set_cached(city_name, "open_meteo_forecast", result)
        return result

    except Exception as e:
        logger.error(f"Open-Meteo forecast failed for {city_name}: {e}")
        return None


# ── 3. OpenAQ v3 (Open Station Network) ──────────────────────────────
def fetch_openaq(city_name: str, lat: float, lon: float) -> Optional[dict]:
    """
    Fetch latest AQI from OpenAQ v3.
    """
    if not OPENAQ_KEY:
        return None

    cached = _get_cached(city_name, "openaq")
    if cached:
        return {k: v for k, v in cached.items() if not k.startswith("_")}

    try:
        headers = {"X-API-Key": OPENAQ_KEY}
        params = {
            "coordinates": f"{lat},{lon}",
            "radius": 30000,  # 30km
            "limit": 5,
            "order_by": "distance",
        }
        resp = requests.get("https://api.openaq.org/v3/locations", params=params, headers=headers, timeout=10)
        resp.raise_for_status()
        locations = resp.json().get("results", [])

        if not locations:
            return None

        for loc in locations:
            loc_id = loc.get("id")
            resp2 = requests.get(f"https://api.openaq.org/v3/locations/{loc_id}/latest", headers=headers, timeout=10)
            resp2.raise_for_status()
            measurements = resp2.json().get("results", [])

            for m in measurements:
                param = m.get("parameter", {})
                if param.get("name", "").lower() in ("pm25", "pm2.5"):
                    pm25_val = m.get("value")
                    if pm25_val is None:
                        continue

                    aqi_val = pm25_to_aqi(pm25_val)
                    dt_str = m.get("datetime", {}).get("local", "")
                    if not dt_str:
                        dt_str = datetime.now(IST).isoformat()

                    station_name = loc.get("name", "OpenAQ station")

                    result = {
                        "value": aqi_val,
                        "source": f"OpenAQ ({station_name})",
                        "as_of": dt_str,
                        "pm25_raw": pm25_val,
                    }

                    _set_cached(city_name, "openaq", result)
                    return result

        return None

    except Exception as e:
        logger.error(f"OpenAQ fetch failed for {city_name}: {e}")
        return None


# ── Unified Live Fetch ───────────────────────────────────────────────
def get_live_aqi(city_config: dict, force_refresh: bool = False) -> dict:
    """
    Fetch live AQI from all available sources for a city.
    Order of preference:
      1. WAQI (official CPCB ground station) if valid token and non-Shanghai
      2. Open-Meteo (satellite + numerical CAMS/GFS) — always works, zero key
      3. OpenAQ v3 (if key provided)
    Returns consensus AQI and clear provenance.
    """
    city = city_config["city"]
    waqi_name = city_config.get("waqi_name", city.lower())
    lat = city_config.get("lat", 0.0)
    lon = city_config.get("lon", 0.0)

    if force_refresh:
        _cache.pop(_cache_key(waqi_name, "waqi"), None)
        _cache.pop(_cache_key(city, "open_meteo"), None)
        _cache.pop(_cache_key(city, "openaq"), None)

    waqi_data = fetch_waqi(waqi_name)
    open_meteo_data = fetch_open_meteo(city, lat, lon)
    openaq_data = fetch_openaq(city, lat, lon)

    # Collect valid numeric values
    values = []
    if waqi_data and waqi_data.get("value") is not None:
        values.append(waqi_data["value"])
    if open_meteo_data and open_meteo_data.get("value") is not None:
        values.append(open_meteo_data["value"])
    if openaq_data and openaq_data.get("value") is not None:
        values.append(openaq_data["value"])

    # If WAQI returned valid data, prioritize it or average with Open-Meteo
    consensus = round(sum(values) / len(values)) if values else None

    # Primary source data for display
    primary = waqi_data or open_meteo_data or openaq_data

    return {
        "city": city,
        "waqi": waqi_data,
        "open_meteo": open_meteo_data,
        "openaq": openaq_data,
        "primary_reading": primary,
        "consensus_aqi": consensus,
        "sources_available": len(values),
        "fetched_at": datetime.now(IST).isoformat(),
    }
