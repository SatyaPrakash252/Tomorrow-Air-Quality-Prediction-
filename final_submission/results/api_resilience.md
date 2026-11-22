# API Upstream Resilience & Failure Behavior Audit

**System:** VayuDrishti FastAPI Web Service  
**Evaluated:** September 2026  

## 1. Upstream Outage Handling Protocol
VayuDrishti ingests live telemetry from third-party APIs:
- World Air Quality Index (WAQI) REST API
- OpenAQ v3 REST API
- Open-Meteo Atmospheric Forecast API

When an external provider experiences network latency, rate limits, or complete server outages:
1. **No Synthetic Backfilling:** The system strictly refuses to invent or extrapolate fake real-time numbers.
2. **Explicit Service Unavailable Response:** If no valid cached reading exists, endpoints return an explicit error state (`HTTP 503 Service Unavailable` or `status: error`) indicating sensor unavailability.
3. **Audit Simulation Result:**
   - Simulated Exception: `requests.RequestException("Simulated upstream WAQI/OpenAQ outage")`
   - Endpoint: `GET /live/Delhi`
   - Observed Status Code: `HTTP 200`
   - Response Payload: `{"city": "Delhi", "waqi": null, "open_meteo": {"value": 87.0, "source": "Open-Meteo (Copernicus CAMS)", "as_of": "2026-09-28T07:00", "dominant_pollutant": "pm25", "pollutants": {"pm25": 26.3, "pm10": 30.7, "no2": 12.2, "so2": 35.3, "co": 0.58, "o3": 161.0}, "station": "Atmospheric Grid (28.61\u00b0N, 77.21\u00b0E)", "pm25_raw": null}, "openaq": null, "primary_reading": {"value": 87.0, "source": "Open-Meteo (Copernicus CAMS)", "as_of": "2026-09-28T07:00", "dominant_pollutant": "pm25", "pollutants": {"pm25": 26.3, "pm10": 30.7, "no2": 12.2, "so2": 35.3, "co": 0.58, "o3": 161.0}, "station": "Atmospheric Grid (28.61\u00b0N, 77.21\u00b0E)", "pm25_raw": null}, "consensus_aqi": 87.0, "sources_available": 1, "fetched_at": "2026-09-28T12:53:03.786817+05:30"}`
   - Behavior: Transparently reports upstream unavailability to the client without hallucinating AQI metrics.
