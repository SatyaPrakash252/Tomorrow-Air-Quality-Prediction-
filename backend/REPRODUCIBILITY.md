# Academic Reproducibility & Verification Guide

## AI-Driven Air Quality Forecasting & Public Health Risk Alert System

This document provides a complete, step-by-step replication protocol for academic reviewers, evaluation committees, and external researchers to reproduce all dataset processing, baselines, ablation studies, and model evaluations reported in this work.

---

## 1. Raw Dataset Provenance & Cryptographic Checksums

The empirical foundation of this study consists of **12,042 validated continuous daily observation records** across 5 major Indian metropolitan areas collected by the Central Pollution Control Board (CPCB) from 2018 to 2024.

All raw data files reside in [`backend/data/raw/`](file:///backend/data/raw/):

| Metropolitan Area | Date Range | Total Records | File Name | SHA-256 Checksum |
|---|---|---|---|---|
| **Delhi** | 2018-01-01 to 2024-12-31 | 2,191 | `Delhi_AQI_Dataset.csv` | `3c68ba26f7b9fabba4906861b4a94ffb484fff81299dd2d5aafad79913baf44a` |
| **Mumbai** | 2019-01-01 to 2024-12-31 | 2,188 | `Mumbai_AQI_Dataset.csv` | `ed89c163fa25746544a7f1610b9e001485fa06ce9c4d11d8615cd27acabb3e99` |
| **Bangalore** | 2018-01-01 to 2024-12-31 | 2,556 | `Bangalore_AQI_Dataset.csv` | `04f27e17ee10deaf5c0e54af16b60d46d42934088456e407f77a4a173ea11cbd` |
| **Chennai** | 2018-01-01 to 2024-12-31 | 2,551 | `Chennai_AQI_Dataset.csv` | `be1fd6eb20417c2df10e54e913c23816f077a527aae82d0958b1a6b4191379b3` |
| **Hyderabad** | 2018-01-01 to 2024-12-31 | 2,556 | `Hyderabad_AQI_Dataset.csv` | `249efa9f58773959f2e99c08d40f20e34e0ac7522410dfaaba5257def7adb813` |
| **Total** | **2018 to 2024** | **12,042** | — | Verified Untampered |

### Target Chemical Pollutants
All records track the mandatory Indian National Air Quality Index (NAQI) criteria pollutants:
- Particulate Matter: $\text{PM}_{2.5}$ and $\text{PM}_{10}$ ($\mu\text{g/m}^3$)
- Gaseous Oxides: $\text{NO}_2$ and $\text{SO}_2$ ($\mu\text{g/m}^3$)
- Carbon Monoxide: $\text{CO}$ ($\text{mg/m}^3$)
- Photochemical Oxidants: $\text{O}_3$ ($\mu\text{g/m}^3$)
- Overall Ground-Truth AQI: India NAQI max-sub-index formulation.

---

## 2. Real Meteorological Data (Open-Meteo ERA5 / Copernicus Reanalysis)

To avoid superficial correlation and capture boundary-layer dynamics, 12,785 daily meteorological records were extracted from the **Open-Meteo ERA5 Reanalysis Archive** (Copernicus Atmosphere Monitoring Service / ECMWF):

- **Temperature ($2\text{m}$ mean)**: Thermal inversion and seasonal boundary effects.
- **Relative Humidity ($2\text{m}$ mean)**: Aerosol hygroscopic growth and secondary particulate formation.
- **Wind Speed ($10\text{m}$ max)**: Dispersion and stagnation indicator.
- **Wind Direction ($10\text{m}$ dominant)**: Transboundary transport vector.
- **Surface Atmospheric Pressure (mean)**: Synoptic anticyclonic high-pressure air trapping.

All meteorological datasets are cached locally in [`backend/data/weather/`](file:///backend/data/weather/) ensuring 100% offline reproducibility.

---

## 3. Train / Test Split Protocol & Leakage Prevention Guarantee

To guarantee rigorous evaluation without temporal leakage:
1. **Strict Chronological Split**: The earliest 80% of dates per city constitute the training set; the most recent 20% constitute the held-out test set.
2. **Zero Shuffling**: Random shuffling across time is strictly prohibited.
3. **No Target Leakage**:
   - Lag features ($t-1, t-2, t-3$) look exclusively backward.
   - Target variable $\text{AQI}_{t+1}$ (and multi-horizon $\text{AQI}_{t+2}, \text{AQI}_{t+3}$) is shifted strictly forward.
4. **Preprocessor Isolation**: All imputation, scaling, and hyperparameter tuning (walk-forward TimeSeriesSplit) are fitted solely on training partitions.

---

## 4. One-Command Execution & Replication

To reproduce the full pipeline from raw data to final models and audit outputs:

### Environment Setup
```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install pinned dependencies
pip install -r backend/requirements.txt
```

### Reproduce Ablation Study, Baselines & Significance Tests
```bash
python backend/pipeline/ablation_study.py
```
Outputs generated in `backend/outputs/ablation_study.json` and `backend/outputs/pinned_ensemble_metrics.json`:
- **Simple Linear Baseline: Ridge Regression**: L2 regularization on pollutant lags ($R^2 = 0.8964$, $\text{RMSE} = 17.06$)
- **Baseline: Kashyap et al.**: Standalone Random Forest on pollutant lags ($R^2 = 0.8906$, $\text{RMSE} = 17.53$)
- **Ablation: Standalone XGBoost (lags only)**: ($R^2 = 0.8927$, $\text{RMSE} = 17.35$)
- **Baseline: Rao et al. (Multimodal Imputation + MMA + XGBoost)**: 36 autoencoder bottleneck features + pollutant lags ($R^2 = 0.8948$, $\text{RMSE} = 17.19$)
- **Ablation: RF + Meteorological Features**: +ERA5 Reanalysis ($R^2 = 0.8969$, $\text{RMSE} = 17.01$)
- **Ablation: RF + Weather + Event Awareness**: +Diwali & Stubble flags ($R^2 = 0.8976$, $\text{RMSE} = 16.95$)
- **Proposed: Stacking Ensemble (RF + XGBoost)**: Full feature vector ($R^2 = 0.9010$, $\text{RMSE} = 16.67$)
- **Ablation: Standalone LSTM**: 7-day sequence modeling ($R^2 = 0.8312$, $\text{RMSE} = 21.68$)
- **Ablation: Tri-Ensemble (RF + XGBoost + LSTM Equal Avg)**: ($R^2 = 0.8772$, $\text{RMSE} = 18.63$) — proves why equal-weight LSTM inclusion degrades the dual ensemble ($0.9010 \rightarrow 0.8772$)
- **Statistical Significance**: Paired Wilcoxon Signed-Rank Test reaches $p < 0.01$ ($p = 3.55 \times 10^{-3}$); Paired Student's t-test reaches $p < 0.05$ ($p = 5.94 \times 10^{-3}$)
- **Multi-Horizon Forecasting**: Day+1 ($R^2 = 0.9008$) $\rightarrow$ Day+2 ($R^2 = 0.8561$) $\rightarrow$ Day+3 ($R^2 = 0.8376$)

### Reproduce Leave-One-City-Out (LOCO) Generalization
```bash
python backend/pipeline/cross_city.py
```
Evaluates cross-metro generalization transfer across 5 held-out cities.

### Run End-to-End Automated Test Suite
```bash
pytest backend/tests/ -v
```

---

## 5. Provenance Audit Matrix (Summary)

| Metric / Output | Location | Generation Method | Realness Guarantee |
|---|---|---|---|
| **Live AQI** | `/live-aqi/{city}` | WAQI ground station / CPCB / CAMS API | Live sensor reading with timestamp & source |
| **Yesterday Pred** | `/live-comparison/{city}` | Validation SQLite DB or verified test point | Actual model prediction made prior to date |
| **Tomorrow Forecast** | `/live-comparison/{city}` | `live_inference.py` (RF+XGB on 4d live lags) | Genuine ML model inference, zero static fallback |
| **Uncertainty Bounds** | `/live-comparison/{city}` | Calibrated 90% empirical test residuals | $y \pm 1.645 \cdot \text{RMSE}_{\text{city}}$ |
| **Explainability** | `/live-comparison/{city}` | Native XGBoost TreeSHAP | Exact game-theoretic Shapley attributions |

---

## 6. Software & Dependency Environment

- **Language**: Python 3.12.5 (64-bit)
- **Primary Libraries**: `scikit-learn==1.6.1`, `xgboost==3.1.1`, `torch==2.8.0`, `scipy==1.15.2`, `pandas>=2.0.0`, `optuna>=3.0.0`, `fastapi>=0.100.0`
- **Random Seed**: Fixed to `42` across all stochastic processes.
