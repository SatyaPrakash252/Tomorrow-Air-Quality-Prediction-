/**
 * mockData.js
 * ────────────
 * Mock data matching FastAPI response shapes.
 * Used for development before the backend is ready.
 * Derived from real pipeline output (dashboard_data.js).
 */

// ── Alert rate comparison (the project's centerpiece data) ──────────
export const ALERT_RATES = {
  "General Public": 25.2,
  "Children/Elderly": 39.9,
  "Respiratory Patients": 55.8,
};

// ── City stats (All-India Coverage: 35+ Major Cities across all regions) ──
export const CITY_STATS = {
  // Core Metros with Offline-Trained ML Ensemble (CPCB 2015-2020)
  Delhi: { avg_aqi: 207.3, max_aqi: 477.0, min_aqi: 32.0, rows: 2361, hasHistoricalModel: true, state: "Delhi", region: "North" },
  Mumbai: { avg_aqi: 127.8, max_aqi: 398.0, min_aqi: 18.0, rows: 2188, hasHistoricalModel: true, state: "Maharashtra", region: "West" },
  Bangalore: { avg_aqi: 85.2, max_aqi: 268.0, min_aqi: 19.0, rows: 2650, hasHistoricalModel: true, state: "Karnataka", region: "South" },
  Chennai: { avg_aqi: 78.4, max_aqi: 285.0, min_aqi: 15.0, rows: 2520, hasHistoricalModel: true, state: "Tamil Nadu", region: "South" },
  Hyderabad: { avg_aqi: 98.6, max_aqi: 312.0, min_aqi: 22.0, rows: 3292, hasHistoricalModel: true, state: "Telangana", region: "South" },

  // Odisha (CGU Evaluation Region)
  Bhubaneswar: { avg_aqi: 92.4, max_aqi: 245.0, min_aqi: 28.0, rows: 0, hasHistoricalModel: false, state: "Odisha", region: "East" },
  Cuttack: { avg_aqi: 96.1, max_aqi: 255.0, min_aqi: 30.0, rows: 0, hasHistoricalModel: false, state: "Odisha", region: "East" },

  // East & Central India
  Kolkata: { avg_aqi: 145.2, max_aqi: 338.0, min_aqi: 28.0, rows: 0, hasHistoricalModel: false, state: "West Bengal", region: "East" },
  Patna: { avg_aqi: 188.5, max_aqi: 420.0, min_aqi: 45.0, rows: 0, hasHistoricalModel: false, state: "Bihar", region: "East" },
  Ranchi: { avg_aqi: 108.0, max_aqi: 260.0, min_aqi: 32.0, rows: 0, hasHistoricalModel: false, state: "Jharkhand", region: "East" },
  Bhopal: { avg_aqi: 118.0, max_aqi: 280.0, min_aqi: 25.0, rows: 0, hasHistoricalModel: false, state: "Madhya Pradesh", region: "Central" },
  Indore: { avg_aqi: 112.5, max_aqi: 275.0, min_aqi: 24.0, rows: 0, hasHistoricalModel: false, state: "Madhya Pradesh", region: "Central" },
  Raipur: { avg_aqi: 125.0, max_aqi: 295.0, min_aqi: 30.0, rows: 0, hasHistoricalModel: false, state: "Chhattisgarh", region: "Central" },

  // North India
  Jaipur: { avg_aqi: 152.0, max_aqi: 350.0, min_aqi: 35.0, rows: 0, hasHistoricalModel: false, state: "Rajasthan", region: "North" },
  Lucknow: { avg_aqi: 175.4, max_aqi: 410.0, min_aqi: 42.0, rows: 0, hasHistoricalModel: false, state: "Uttar Pradesh", region: "North" },
  Kanpur: { avg_aqi: 182.0, max_aqi: 430.0, min_aqi: 40.0, rows: 0, hasHistoricalModel: false, state: "Uttar Pradesh", region: "North" },
  Varanasi: { avg_aqi: 168.0, max_aqi: 395.0, min_aqi: 38.0, rows: 0, hasHistoricalModel: false, state: "Uttar Pradesh", region: "North" },
  Agra: { avg_aqi: 162.0, max_aqi: 385.0, min_aqi: 35.0, rows: 0, hasHistoricalModel: false, state: "Uttar Pradesh", region: "North" },
  Chandigarh: { avg_aqi: 105.0, max_aqi: 265.0, min_aqi: 25.0, rows: 0, hasHistoricalModel: false, state: "Chandigarh", region: "North" },
  Amritsar: { avg_aqi: 138.0, max_aqi: 320.0, min_aqi: 30.0, rows: 0, hasHistoricalModel: false, state: "Punjab", region: "North" },
  Ludhiana: { avg_aqi: 146.0, max_aqi: 340.0, min_aqi: 32.0, rows: 0, hasHistoricalModel: false, state: "Punjab", region: "North" },
  Dehradun: { avg_aqi: 88.0, max_aqi: 210.0, min_aqi: 20.0, rows: 0, hasHistoricalModel: false, state: "Uttarakhand", region: "North" },
  Shimla: { avg_aqi: 48.0, max_aqi: 120.0, min_aqi: 12.0, rows: 0, hasHistoricalModel: false, state: "Himachal Pradesh", region: "North" },
  Srinagar: { avg_aqi: 56.0, max_aqi: 140.0, min_aqi: 15.0, rows: 0, hasHistoricalModel: false, state: "Jammu and Kashmir", region: "North" },

  // West India
  Pune: { avg_aqi: 106.5, max_aqi: 265.0, min_aqi: 24.0, rows: 0, hasHistoricalModel: false, state: "Maharashtra", region: "West" },
  Ahmedabad: { avg_aqi: 135.0, max_aqi: 325.0, min_aqi: 28.0, rows: 0, hasHistoricalModel: false, state: "Gujarat", region: "West" },
  Surat: { avg_aqi: 114.0, max_aqi: 270.0, min_aqi: 22.0, rows: 0, hasHistoricalModel: false, state: "Gujarat", region: "West" },
  Nagpur: { avg_aqi: 110.0, max_aqi: 260.0, min_aqi: 25.0, rows: 0, hasHistoricalModel: false, state: "Maharashtra", region: "West" },
  Nashik: { avg_aqi: 95.0, max_aqi: 230.0, min_aqi: 20.0, rows: 0, hasHistoricalModel: false, state: "Maharashtra", region: "West" },
  Vadodara: { avg_aqi: 118.0, max_aqi: 285.0, min_aqi: 26.0, rows: 0, hasHistoricalModel: false, state: "Gujarat", region: "West" },

  // South India
  Kochi: { avg_aqi: 62.0, max_aqi: 165.0, min_aqi: 15.0, rows: 0, hasHistoricalModel: false, state: "Kerala", region: "South" },
  Thiruvananthapuram: { avg_aqi: 58.0, max_aqi: 155.0, min_aqi: 14.0, rows: 0, hasHistoricalModel: false, state: "Kerala", region: "South" },
  Visakhapatnam: { avg_aqi: 88.0, max_aqi: 220.0, min_aqi: 22.0, rows: 0, hasHistoricalModel: false, state: "Andhra Pradesh", region: "South" },
  Coimbatore: { avg_aqi: 68.0, max_aqi: 175.0, min_aqi: 16.0, rows: 0, hasHistoricalModel: false, state: "Tamil Nadu", region: "South" },
  Madurai: { avg_aqi: 74.0, max_aqi: 190.0, min_aqi: 18.0, rows: 0, hasHistoricalModel: false, state: "Tamil Nadu", region: "South" },
  Mysuru: { avg_aqi: 64.0, max_aqi: 170.0, min_aqi: 15.0, rows: 0, hasHistoricalModel: false, state: "Karnataka", region: "South" },

  // North-East India
  Guwahati: { avg_aqi: 102.0, max_aqi: 250.0, min_aqi: 22.0, rows: 0, hasHistoricalModel: false, state: "Assam", region: "North-East" },
  Shillong: { avg_aqi: 45.0, max_aqi: 115.0, min_aqi: 10.0, rows: 0, hasHistoricalModel: false, state: "Meghalaya", region: "North-East" },
};

export const CITIES = Object.keys(CITY_STATS);
export const HISTORICAL_CITIES = CITIES.filter(c => CITY_STATS[c]?.hasHistoricalModel);
export const LIVE_ONLY_CITIES = CITIES.filter(c => !CITY_STATS[c]?.hasHistoricalModel);

// ── Model Metrics ───────────────────────────────────────────────────
export const MODEL_METRICS = [
  { Model: "Baseline: Kashyap et al. (RF)", "Accuracy(%)": 86.56, RMSE: 17.65, MAE: 11.67, "R²": 0.8890 },
  { Model: "Baseline: Rao et al. (XGBoost)", "Accuracy(%)": 86.65, RMSE: 17.29, MAE: 11.59, "R²": 0.8936 },
  { Model: "Linear Baseline (Ridge)", "Accuracy(%)": 86.71, RMSE: 17.05, MAE: 11.64, "R²": 0.8964 },
  { Model: "Proposed Stacking Ensemble", "Accuracy(%)": 91.42, RMSE: 13.84, MAE: 9.12, "R²": 0.9248 },
];

export const BEST_MODEL = {
  name: "Proposed Stacking Ensemble",
  accuracy: 91.42,
  rmse: 13.84,
  mae: 9.12,
  r2: 0.9248,
};


// ── HRI Tier Distributions ──────────────────────────────────────────
export const HRI_TIERS = {
  "General Public": { LOW: 25.0, MODERATE: 49.8, HIGH: 15.3, SEVERE: 9.9 },
  "Children/Elderly": { LOW: 11.2, MODERATE: 48.9, HIGH: 22.7, SEVERE: 17.2 },
  "Respiratory Patients": { LOW: 4.8, MODERATE: 39.4, HIGH: 28.5, SEVERE: 27.3 },
};

export const HRI_CUTOFFS = { p25: 3.28, p75: 7.14, p90: 10.52 };

// ── Autoencoder MSE ─────────────────────────────────────────────────
export const AUTOENCODER_MSE = {
  KNN_AE: 0.000142,
  MICE_AE: 0.000138,
  SVD_AE: 0.000156,
};

// ── Imputation RMSE ─────────────────────────────────────────────────
export const IMPUTATION_RMSE = {
  KNN: { "PM2.5": 4.21, PM10: 6.83, NO2: 2.14, SO2: 1.87, CO: 0.12, O3: 3.45 },
  MICE: { "PM2.5": 3.98, PM10: 6.52, NO2: 2.01, SO2: 1.76, CO: 0.11, O3: 3.22 },
  SVD: { "PM2.5": 5.12, PM10: 7.94, NO2: 2.85, SO2: 2.34, CO: 0.15, O3: 4.18 },
};

// ── Feature Importance (Top 15) ─────────────────────────────────────
export const FEATURE_IMPORTANCE = {
  features: [
    "AQI_lag1", "AQI", "PM2.5_lag1", "PM2.5", "PM10_lag1",
    "PM10", "AQI_lag2", "NO2_lag1", "CO_lag1", "O3_lag1",
    "NO2", "AQI_lag3", "SO2_lag1", "month", "day_of_week",
  ],
  importance: [
    0.3214, 0.1856, 0.0923, 0.0812, 0.0645,
    0.0534, 0.0421, 0.0318, 0.0267, 0.0198,
    0.0176, 0.0154, 0.0132, 0.0098, 0.0072,
  ],
};

// ── Generate mock forecast history ──────────────────────────────────
function generateHistory(city, days = 90) {
  const baseAQI = CITY_STATS[city]?.avg_aqi || 150;
  const dates = [];
  const actual = [];
  const rf = [];
  const xgb = [];
  const lstm = [];
  const ensemble = [];

  const startDate = new Date("2023-10-01");
  for (let i = 0; i < days; i++) {
    const date = new Date(startDate);
    date.setDate(startDate.getDate() + i);
    dates.push(date.toISOString().split("T")[0]);

    // Generate realistic-looking AQI with seasonality
    const seasonal = Math.sin((i / 30) * Math.PI) * 40;
    const noise = (Math.random() - 0.5) * 60;
    const trend = baseAQI + seasonal + noise;
    const actualVal = Math.max(20, Math.round(trend));
    actual.push(actualVal);

    // Model predictions with realistic error patterns
    rf.push(Math.max(20, Math.round(actualVal + (Math.random() - 0.5) * 35)));
    xgb.push(Math.max(20, Math.round(actualVal + (Math.random() - 0.5) * 38)));
    lstm.push(Math.max(20, Math.round(actualVal + (Math.random() - 0.5) * 40)));
    ensemble.push(Math.max(20, Math.round(actualVal + (Math.random() - 0.5) * 28)));
  }

  return { dates, actual, rf, xgb, lstm, ensemble };
}

export const PREDICTIONS = {};
CITIES.forEach((city) => {
  PREDICTIONS[city] = generateHistory(city);
});

// ── Mock Alerts ─────────────────────────────────────────────────────
export const MOCK_ALERTS = [
  {
    city: "Delhi",
    date: "2024-01-15",
    group: "Respiratory Patients",
    tier: "SEVERE",
    hri_value: 14.82,
    recommendation: "Avoid ALL outdoor exposure. Keep windows sealed. Use air purifiers indoors.",
    vulnerability_factor: 1.6,
    pollutant_breakdown: { "PM2.5": 185, PM10: 320, NO2: 68, SO2: 28, CO: 2.8, O3: 42 },
  },
  {
    city: "Delhi",
    date: "2024-01-15",
    group: "Children/Elderly",
    tier: "SEVERE",
    hri_value: 12.04,
    recommendation: "Avoid ALL outdoor exposure. Keep windows sealed. Use air purifiers indoors.",
    vulnerability_factor: 1.3,
    pollutant_breakdown: { "PM2.5": 185, PM10: 320, NO2: 68, SO2: 28, CO: 2.8, O3: 42 },
  },
  {
    city: "Delhi",
    date: "2024-01-15",
    group: "General Public",
    tier: "HIGH",
    hri_value: 9.26,
    recommendation: "Limit outdoor activities. Wear N95 masks if going outside.",
    vulnerability_factor: 1.0,
    pollutant_breakdown: { "PM2.5": 185, PM10: 320, NO2: 68, SO2: 28, CO: 2.8, O3: 42 },
  },
  {
    city: "Mumbai",
    date: "2024-01-14",
    group: "Respiratory Patients",
    tier: "HIGH",
    hri_value: 11.2,
    recommendation: "Limit outdoor activities. Wear N95 masks if going outside.",
    vulnerability_factor: 1.6,
    pollutant_breakdown: { "PM2.5": 120, PM10: 210, NO2: 52, SO2: 22, CO: 1.9, O3: 38 },
  },
  {
    city: "Hyderabad",
    date: "2024-01-13",
    group: "Respiratory Patients",
    tier: "HIGH",
    hri_value: 10.8,
    recommendation: "Limit outdoor activities. Wear N95 masks if going outside.",
    vulnerability_factor: 1.6,
    pollutant_breakdown: { "PM2.5": 95, PM10: 180, NO2: 48, SO2: 18, CO: 1.4, O3: 35 },
  },
  {
    city: "Delhi",
    date: "2024-01-12",
    group: "Respiratory Patients",
    tier: "SEVERE",
    hri_value: 15.6,
    recommendation: "Avoid ALL outdoor exposure. Keep windows sealed. Use air purifiers indoors.",
    vulnerability_factor: 1.6,
    pollutant_breakdown: { "PM2.5": 210, PM10: 380, NO2: 72, SO2: 32, CO: 3.2, O3: 48 },
  },
  {
    city: "Delhi",
    date: "2024-01-12",
    group: "Children/Elderly",
    tier: "HIGH",
    hri_value: 12.68,
    recommendation: "Limit outdoor activities. Wear N95 masks if going outside.",
    vulnerability_factor: 1.3,
    pollutant_breakdown: { "PM2.5": 210, PM10: 380, NO2: 72, SO2: 32, CO: 3.2, O3: 48 },
  },
  {
    city: "Chennai",
    date: "2024-01-11",
    group: "Respiratory Patients",
    tier: "MODERATE",
    hri_value: 6.2,
    recommendation: "Sensitive groups should consider reducing prolonged outdoor exertion.",
    vulnerability_factor: 1.6,
    pollutant_breakdown: { "PM2.5": 45, PM10: 80, NO2: 28, SO2: 12, CO: 0.8, O3: 25 },
  },
];

// ── Dataset Info ────────────────────────────────────────────────────
export const DATASET_INFO = {
  total_rows: 12042,
  cities: CITIES,
  date_range: "2018-01-01 to 2024-06-30",
  num_features: 65,
};

// ── Helper: Get AQI category ────────────────────────────────────────
export function getAQICategory(aqi) {
  if (aqi <= 50) return { label: "Good", color: "#10B981" };
  if (aqi <= 100) return { label: "Satisfactory", color: "#6EE7B7" };
  if (aqi <= 200) return { label: "Moderate", color: "#FBBF24" };
  if (aqi <= 300) return { label: "Poor", color: "#F97316" };
  if (aqi <= 400) return { label: "Very Poor", color: "#EF4444" };
  return { label: "Severe", color: "#991B1B" };
}

// ── Helper: Get tier class ──────────────────────────────────────────
export function getTierClass(tier) {
  return `tier-badge--${tier.toLowerCase()}`;
}

export function getTierColor(tier) {
  const colors = {
    LOW: "#10B981",
    MODERATE: "#F59E0B",
    HIGH: "#E8871E",
    SEVERE: "#EF4444",
  };
  return colors[tier] || "#94A3B8";
}
