/**
 * api.js
 * ──────
 * Frontend API client connecting to the FastAPI backend.
 * Uses the Vite proxy configured at `/api`.
 * Falls back gracefully to mockData if backend is offline.
 */

import {
  CITY_STATS,
  MODEL_METRICS,
  BEST_MODEL,
  MOCK_ALERTS,
  PREDICTIONS,
  getAQICategory,
} from './mockData';

const BASE_URL = '/api';

/**
 * Helper to fetch with timeout and json parsing
 */
async function fetchJson(url, options = {}, timeoutMs = 10000) {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
      headers: {
        'Accept': 'application/json',
        ...(options.headers || {}),
      },
    });
    clearTimeout(id);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    return await response.json();
  } catch (err) {
    clearTimeout(id);
    throw err;
  }
}

// ── City Registry Config ──────────────────────────────────────────
export async function fetchCityConfig() {
  try {
    return await fetchJson(`${BASE_URL}/config/cities`);
  } catch (err) {
    console.warn('[API] /config/cities unavailable, using fallback:', err.message);
    const cities = Object.entries(CITY_STATS).map(([city, s]) => ({
      city,
      has_historical_model: s.hasHistoricalModel,
      status_label: s.hasHistoricalModel ? 'ML Ensemble Forecast' : 'Atmospheric AI Simulation',
      state: s.state,
      region: s.region,
    }));
    return {
      cities,
      total: cities.length,
      historical_count: cities.filter(c => c.has_historical_model).length,
      live_only_count: cities.filter(c => !c.has_historical_model).length,
    };
  }
}

// ── Live AQI from WAQI + OpenAQ ──────────────────────────────────
export async function fetchLiveAQI(city, bustCache = false) {
  try {
    const qs = bustCache ? `?t=${Date.now()}` : '';
    return await fetchJson(`${BASE_URL}/live/${encodeURIComponent(city)}${qs}`);
  } catch (err) {
    console.warn(`[API] /live/${city} unavailable:`, err.message);
    return null;
  }
}

// ── In-Memory Fast Cache for Live Comparison ──────────────────────
const _liveComparisonCache = new Map();
const CACHE_TTL_MS = 60000; // 60 seconds freshness

export function getCachedLiveComparison(city) {
  if (!city) return null;
  const entry = _liveComparisonCache.get(city.toLowerCase());
  if (entry && (Date.now() - entry.time) < CACHE_TTL_MS) {
    return entry.data;
  }
  return null;
}

// ── Live Comparison Triple (Live actual vs Yesterday pred vs Tomorrow forecast)
export async function fetchLiveComparison(city, bustCache = false) {
  if (!city) return null;
  const key = city.toLowerCase();

  if (!bustCache) {
    const cached = getCachedLiveComparison(city);
    if (cached) return cached;
  }

  try {
    const qs = bustCache ? `?t=${Date.now()}` : '';
    const data = await fetchJson(`${BASE_URL}/live-comparison/${encodeURIComponent(city)}${qs}`);
    if (data) {
      _liveComparisonCache.set(key, { data, time: Date.now() });
    }
    return data;
  } catch (err) {
    console.warn(`[API] /live-comparison/${city} unavailable:`, err.message);
    const stale = _liveComparisonCache.get(key);
    return stale ? stale.data : null;
  }
}

// ── Daily Validation Rolling Metrics ─────────────────────────────
export async function fetchValidation(city, days = 14) {
  try {
    return await fetchJson(`${BASE_URL}/validation/${encodeURIComponent(city)}?days=${days}`);
  } catch (err) {
    console.warn(`[API] /validation/${city} unavailable:`, err.message);
    return null;
  }
}

// ── Forecast ─────────────────────────────────────────────────────
export async function fetchForecast(city) {
  try {
    return await fetchJson(`${BASE_URL}/forecast/${encodeURIComponent(city)}`);
  } catch (err) {
    console.warn(`[API] /forecast/${city} unavailable:`, err.message);
    return null;
  }
}

// ── History ──────────────────────────────────────────────────────
export async function fetchHistory(city, days = 90) {
  try {
    return await fetchJson(`${BASE_URL}/history/${encodeURIComponent(city)}?days=${days}`);
  } catch (err) {
    console.warn(`[API] /history/${city} unavailable, using fallback:`, err.message);
    const mockCity = PREDICTIONS[city] || PREDICTIONS.Delhi;
    if (!mockCity || !mockCity.dates) return { city, days, history: [] };
    const start = Math.max(0, mockCity.dates.length - days);
    const history = mockCity.dates.slice(start).map((d, i) => ({
      date: d,
      actual: mockCity.actual[start + i],
      rf_prediction: mockCity.rf[start + i],
      xgb_prediction: mockCity.xgb[start + i],
      ensemble_prediction: mockCity.ensemble[start + i],
    }));
    return { city, days, history };
  }
}

// ── Health Risk Index ────────────────────────────────────────────
export async function fetchRisk(city) {
  try {
    return await fetchJson(`${BASE_URL}/risk/${encodeURIComponent(city)}`);
  } catch (err) {
    console.warn(`[API] /risk/${city} unavailable, using fallback:`, err.message);
    return null;
  }
}

// ── Alerts Feed ──────────────────────────────────────────────────
export async function fetchAlerts(city = null) {
  try {
    const isAll = !city || city.toLowerCase() === 'all';
    const url = isAll ? `${BASE_URL}/alerts` : `${BASE_URL}/alerts?city=${encodeURIComponent(city)}`;
    return await fetchJson(url);
  } catch (err) {
    console.warn('[API] /alerts unavailable, using fallback:', err.message);
    const isAll = !city || city.toLowerCase() === 'all';
    const alerts = !isAll ? MOCK_ALERTS.filter(a => a.city.toLowerCase() === city.toLowerCase()) : MOCK_ALERTS;
    return {
      city: isAll ? null : city,
      total: alerts.length,
      alerts,
    };
  }
}

// ── Cross-Model Metrics ──────────────────────────────────────────
export async function fetchMetrics() {
  try {
    return await fetchJson(`${BASE_URL}/metrics`);
  } catch (err) {
    console.warn('[API] /metrics unavailable, using fallback:', err.message);
    return {
      model_metrics: MODEL_METRICS,
      best_model: BEST_MODEL,
    };
  }
}
