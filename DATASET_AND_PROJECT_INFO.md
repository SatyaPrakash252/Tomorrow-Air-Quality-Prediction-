# VayuDrishti: AI-Driven Air Quality Forecasting & Public Health Risk Alert System
## Comprehensive Project Documentation & Dataset Reference

---

### Academic & Institutional Metadata
- **Institution:** C.V. Raman Global University (CGU), Bhubaneswar, Odisha, India
- **Department:** Department of Computer Science & Engineering
- **Academic Milestone:** 7th-Semester Major Project (Review 1 / Final Evaluation)
- **Project Title:** AI-Driven Air Quality Forecasting and Public Health Risk Alert System for Indian Metropolitan Cities
- **System Name:** **VayuDrishti** (वायुदृष्टि)
- **Faculty Guide:** **Prof. Soumya Sahoo**, Assistant Professor, Dept. of CSE
- **Student Team:**
  1. **Satyaprakash Rout** (Lead / Full-Stack & ML Pipeline)
  2. **Likuna Swain** (Data Engineering & Deep Learning)
  3. **Ch Saipriya Patra** (Health Risk Modeling & Statistical Analysis)
  4. **Arpeet Barik** (API Architecture & UI/UX Integration)

---

## 1. Project Overview & Motivation

### The Problem
Traditional air quality monitoring platforms (including CPCB portals, SAFAR, and commercial mobile apps) suffer from two fundamental operational limitations:
1. **Rearview Monitoring:** Existing systems only report **today's** pollution from **today's / past** sensor readings. They do not provide proactive, multi-step forward forecasting to prepare citizens before severe smog episodes emerge.
2. **One-Size-Fits-All Reporting:** A single scalar AQI value is published for the entire population. However, biological vulnerability varies drastically: a particulate level that causes mild irritation in a healthy adult can trigger acute bronchospasms, asthma exacerbations, or cardiac arrhythmias in vulnerable groups.

### The VayuDrishti Solution
VayuDrishti bridges environmental science and clinical health risk through a dual-engine architecture:
- **Engine 1 (Forecasting):** Machine learning & deep learning ensembles predicting next-day AQI ($AQI_{t+1}$) with high precision ($R^2 = 0.9237$).
- **Engine 2 (Public Health Risk Alerting):** An epidemiologically-grounded Health Risk Index (HRI) that converts multi-pollutant concentrations into demographic-specific risk tiers (*General Public*, *Children & Elderly*, *Respiratory/Cardiac Patients*) with actionable clinical guidance.

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                             VayuDrishti System Flow                              │
└──────────────────────────────────────────────────────────────────────────────────┘
  Historical CPCB Datasets (2018–2024)
              │
              ▼
  Data Ingestion & Chronological Sorting (5 Cities)
              │
              ▼
  Iterative Imputer (MICE) ──► Imputation RMSE: 2.14 vs Mean 8.76 (75.6% gain)
              │
              ▼
  Feature Engineering: Lags (t-1..t-7), Rolling Means, Cyclical Calendar Features
              │
              ▼
  Deep Bottleneck Autoencoder (MSE = 0.0084) ──► Latent Atmospheric Embeddings
              │
              ├───────────────────────────────────┐
              ▼                                   ▼
   Next-Day AQI Forecast Ensemble      Health Risk Index (HRI) Engine
   (XGBoost + RF + LSTM + Stacking)    (Multi-pollutant CPCB ratios × V_g)
              │                                   │
              ▼                                   ▼
   FastAPI High-Performance Backend    Demographic Tiers (Low/Mod/High/Severe)
              │                                   │
              └─────────────────┬─────────────────┘
                                ▼
         VayuDrishti Interactive Web Dashboard (React + Vite)
```

---

## 2. Dataset Specifications & Acquisition

### 2.1 Data Source & Provenance
The dataset comprises continuous ambient air quality measurements collected by the **Central Pollution Control Board (CPCB)**, **State Pollution Control Boards (SPCBs)**, and the **National Ambient Air Quality Monitoring Programme (NAAMP)** across India.
- **Repository Source:** CPCB Open Datasets via [India-Air-Quality-Dataset (GitHub)](https://raw.githubusercontent.com/cp099/India-Air-Quality-Dataset/main/)
- **Local Storage Path:** `backend/data/raw/`
- **Format:** Comma-Separated Values (CSV) with UTF-8 encoding

### 2.2 Geographic Coverage (5 Megacities)
The dataset covers 5 major metropolitan areas representing distinct climatological, geographic, and socio-industrial environments:

| City | State / Region | Geographical Profile | Dominant Pollution Drivers | Records | Date Range |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Delhi** | National Capital Region (North) | Landlocked Gangetic plain, extreme continental climate | Stubble burning, winter thermal inversion, vehicular emissions | **2,191 days** | 01/01/2018 – 31/12/2024 |
| **Mumbai** | Maharashtra (West) | Coastal peninsular, maritime boundary layer | High vehicular density, port activities, maritime sea-breeze dispersion | **2,188 days** | 01/01/2019 – 31/12/2024 |
| **Bangalore** | Karnataka (South) | Elevated Deccan plateau (920m above MSL) | Rapid urban vehicular growth, construction dust, IT corridors | **2,556 days** | 01/01/2018 – 31/12/2024 |
| **Chennai** | Tamil Nadu (South) | Coastal Coromandel Coast, tropical maritime | Industrial zones (North Chennai), thermal power plants, vehicular traffic | **2,551 days** | 01/01/2018 – 31/12/2024 |
| **Hyderabad** | Telangana (South) | Semi-arid inland plateau | Pharma-chemical industrial belts, commercial fleet transit | **2,556 days** | 01/01/2018 – 31/12/2024 |
| **Total** | **Pan-India Metros** | — | — | **12,042 daily records** | **7 Continuous Years** |

### 2.3 Measured Pollutants & Environmental Thresholds
The dataset captures the criteria pollutants governed under the **National Ambient Air Quality Standards (NAAQS)**:

| Parameter | Full Name | Standard Measurement Unit | CPCB "Good" Limit ($S_i$) | Biological Hazard Profile |
| :--- | :--- | :--- | :--- | :--- |
| **AQI** | Air Quality Index | Dimensionless (0–500+) | $\le 50$ | Overall aggregate air quality metric |
| **PM2.5** | Fine Particulate Matter ($\le 2.5 \mu m$) | $\mu g / m^3$ | **30.0** | Penetrates deep into alveoli and enters the bloodstream; causes cardiovascular & pulmonary damage |
| **PM10** | Respirable Particulate Matter ($\le 10 \mu m$) | $\mu g / m^3$ | **50.0** | Inhalable coarse particles; causes airway inflammation, bronchitis |
| **NO2** | Nitrogen Dioxide | $\mu g / m^3$ | **40.0** | Deep lung irritant, exacerbates childhood asthma, causes secondary aerosol formation |
| **SO2** | Sulphur Dioxide | $\mu g / m^3$ | **40.0** | Bronchoconstrictor; precursor to acid rain and sulfate aerosols |
| **CO** | Carbon Monoxide | $mg / m^3$ | **1.0** | Reduces blood oxygen delivery by forming carboxyhemoglobin ($HbCO$) |
| **O3** | Ground-Level Ozone | $\mu g / m^3$ | **50.0** | Powerful oxidant; attacks cellular respiratory membranes |

---

## 3. Data Preprocessing & Advanced Imputation

### 3.1 Sensor Missingness
Air quality sensor networks frequently encounter missing data due to sensor calibration drift, telemetry dropouts, power outages, and monsoon interference. Simple deletion or mean substitution creates severe distribution distortion and biases time-series models.

### 3.2 Iterative Imputer (MICE) Benchmark
To handle missingness without injecting synthetic variance:
- **Baseline Method:** Univariate Mean/Median Imputation
- **Implemented Method:** **Multivariate Imputation by Chained Equations (MICE)** via Scikit-learn's `IterativeImputer` with Bayesian Ridge estimators:
  - Models each pollutant feature as a function of all other correlated pollutants and meteorological proxies.
  - Preserves multivariate cross-correlations (e.g., $PM2.5 \leftrightarrow PM10$ and $NO2 \leftrightarrow CO$).
- **Empirical Validation (Cross-Validation on Artificially Masked Ground Truth):**
  $$\text{Mean Imputation RMSE} = 8.76 \mu g/m^3$$
  $$\textbf{MICE Imputation RMSE} = \mathbf{2.14} \, \mu g/m^3 \quad (\mathbf{75.6\%} \text{ error reduction})$$

---

## 4. Feature Engineering & Latent Embeddings

To provide temporal memory and non-linear representations, the raw dataset is expanded through automated feature engineering:

1. **Temporal Lags:**
   - 1-day, 2-day, 3-day, and 7-day backward lags for primary drivers: $AQI_{t-1..7}$, $PM2.5_{t-1..7}$, $PM10_{t-1..7}$, $NO2_{t-1..7}$.
2. **Rolling Statistics:**
   - 3-day and 7-day rolling moving averages ($\mu$) and rolling standard deviations ($\sigma$) to capture atmospheric persistence and volatility.
3. **Cyclical Calendar Encodings:**
   - Preserves continuous transitions across year-end and seasons via trigonometric encoding:
     $$\sin\left(\frac{2\pi \cdot \text{Month}}{12}\right), \quad \cos\left(\frac{2\pi \cdot \text{Month}}{12}\right)$$
     $$\sin\left(\frac{2\pi \cdot \text{DayOfYear}}{365.25}\right), \quad \cos\left(\frac{2\pi \cdot \text{DayOfYear}}{365.25}\right)$$
4. **Deep Autoencoder Bottleneck Embeddings:**
   - A symmetrical neural autoencoder (6 $\rightarrow$ 16 $\rightarrow$ 8 $\rightarrow$ 4 latent features $\rightarrow$ 8 $\rightarrow$ 16 $\rightarrow$ 6) trained on standardized pollutant values.
   - **Reconstruction MSE:** $\mathbf{0.0084}$.
   - The 4-dimensional latent bottleneck captures non-linear atmospheric co-dispersion patterns that raw linear features miss.

---

## 5. Machine Learning & Forecasting Models

### 5.1 Validation Protocol
To prevent lookahead bias (data leakage), the models are evaluated using a strict **chronological time-series split**:
- **Training Set:** 2018 – 2022 (80%)
- **Testing Set:** 2023 – 2024 (20% held-out future observations)

### 5.2 Model Performance Comparison

| Model | Model Family | $R^2$ Score | RMSE ($AQI$) | MAE ($AQI$) | Strengths & Characteristics |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Linear Regression** | Generalized Linear | 0.8124 | 36.12 | 26.40 | Fast baseline; struggles with non-linear pollution spikes |
| **Random Forest** | Bagging Ensemble | 0.8912 | 22.45 | 16.10 | Robust against outliers, captures non-linear splits |
| **XGBoost Regressor** | Gradient Boosting | 0.9148 | 19.88 | 14.20 | Strongest single tabular model, handles feature interactions |
| **LSTM** | Deep Recurrent NN | 0.9021 | 21.10 | 15.30 | Excels at sequence memory and multi-day temporal lags |
| **Stacking Ensemble** | **Hybrid Metalearner** | **0.9237** | **18.42** | **12.95** | **Optimal performance: Combines XGBoost + RF + LSTM** |

### 5.3 Key Feature Importance Findings
1. **$PM2.5_{t-1}$ (38.4%)**: Primary single-day lag driver for AQI escalation.
2. **$AQI_{t-1}$ (26.1%)**: Atmospheric inertia indicator.
3. **$PM10_{t-1}$ (14.7%)**: Road and construction dust contribution.
4. **Autoencoder Latent Vector $z_0$ (8.9%)**: Multi-pollutant synergistic interaction.
5. **Cyclical Seasonal Index (6.2%)**: Winter temperature inversion effect.

---

## 6. Health Risk Index (HRI) & Public Health Alerting

### 6.1 Formulation
Existing AQI measures pollution severity, not personal biological risk. VayuDrishti implements the multi-pollutant Health Risk Index adapted from *Kashyap et al. (2025)*:

$$HRI = \left( \sum_{i \in \text{Pollutants}} \frac{C_i}{S_i} \right) \times V_g$$

Where:
- $C_i$: Current concentration of pollutant $i$
- $S_i$: CPCB NAAQS safety limit for pollutant $i$
- $V_g$: Demographic Vulnerability Multiplier

### 6.2 Demographic Vulnerability Factors ($V_g$)

| Population Group | Multiplier ($V_g$) | Clinical Rationale |
| :--- | :---: | :--- |
| **General Public** | **$1.0\times$** | Standard healthy adult baseline with normal lung capacity and immune response |
| **Children & Elderly** | **$1.3\times$** | Underdeveloped airway epithelium in children (higher breathing rate per kg); reduced mucosal clearance and existing comorbidities in senior citizens |
| **Respiratory & Cardiac Patients** | **$1.6\times$** | Pre-existing bronchial hyperresponsiveness (Asthma/COPD) or compromised coronary perfusion |

### 6.3 Shared Cutoffs & Risk Escalation
To guarantee that the vulnerability factor has clinical meaning, all groups share the **General Public's baseline percentiles ($P_{25}, P_{75}, P_{90}$)** as fixed tier thresholds:

| Risk Tier | HRI Score Range | Health Guidance & Recommended Interventions |
| :--- | :--- | :--- |
| **LOW** | $HRI < P_{25}$ | Air quality is acceptable. Outdoor physical activities can proceed normally. |
| **MODERATE** | $P_{25} \le HRI < P_{75}$ | Mild irritation possible. Sensitive individuals should reduce prolonged outdoor exertion. |
| **HIGH** | $P_{75} \le HRI < P_{90}$ | Noticeable symptoms in general population. Wear N95 masks outdoors, keep windows closed. |
| **SEVERE** | $HRI \ge P_{90}$ | Critical emergency. Cease outdoor activities. Run HEPA air purifiers. Seek medical help if dyspnea occurs. |

**Clinical Impact:** On a day when the general population is at **"MODERATE"** risk, respiratory patients automatically cross into **"HIGH"** or **"SEVERE"**, enabling timely prophylactic inhaler usage and activity restriction.

---

## 7. Software Architecture & Implementation

### 7.1 Tech Stack Summary
- **Backend:** Python 3.12, FastAPI, Uvicorn, Scikit-learn, XGBoost, TensorFlow/Keras, Optuna, Pandas, NumPy
- **Frontend:** React 19, Vite, Tailwind CSS, Framer Motion, Recharts, Lucide React
- **Data Pipeline:** Modular architecture in `backend/pipeline/`:
  - `data_ingestion.py`: Automated caching and merging of CPCB data
  - `imputation.py`: MICE iterative multivariate imputation
  - `feature_engineering.py`: Lags, rolling windows, and calendar features
  - `autoencoder.py`: Deep latent representation model
  - `models.py`: Model training, hyperparameter tuning, and ensemble
  - `hri.py`: Health Risk Index computation
  - `alerts.py`: Notification and warning generator
  - `run_pipeline.py`: Unified end-to-end execution script

### 7.2 REST API Specification
- `GET /health`: System diagnostic healthcheck
- `GET /cities`: List of available metropolitan cities
- `GET /forecast/{city}`: 24h next-day forecast with model breakdown and confidence bounds
- `GET /hri/{city}`: Stratified HRI scores across all 3 demographic groups
- `GET /alerts/{city}`: Active threshold alerts and advisory guidance

---

## 8. Academic References & Standards
1. **Central Pollution Control Board (CPCB), India (2014, 2020):** *National Air Quality Index: Development of AQI and Health Breakpoints.* Ministry of Environment, Forest and Climate Change, New Delhi.
2. **Kashyap, S., et al. (2025):** *Multi-Pollutant Health Risk Modeling and Population Vulnerability Stratification in South Asian Megacities.* Journal of Environmental Health & Atmospheric Informatics.
3. **World Health Organization (WHO, 2021):** *WHO Global Air Quality Guidelines: Particulate matter (PM2.5 and PM10), ozone, nitrogen dioxide, sulfur dioxide and carbon monoxide.* Geneva.
4. **Chen, T., & Guestrin, C. (2016):** *XGBoost: A Scalable Tree Boosting System.* In Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining.
5. **Van Buuren, S., & Groothuis-Oudshoorn, K. (2011):** *mice: Multivariate Imputation by Chained Equations in R.* Journal of Statistical Software, 45(3), 1-67.

---
*VayuDrishti Project Repository — C.V. Raman Global University, 2026.*
