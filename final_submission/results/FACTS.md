# VayuDrishti: Master Ground Truth Facts Ledger (FACTS.md)

**Project:** AI-Driven Air Quality Forecasting and Public Health Risk Alert System for Indian Metropolitan Cities  
**Academic Milestone:** 7th Semester Major Project Final Evaluation (Stage-1)  
**Evaluation Date:** October 10, 2026  
**Institution:** C.V. Raman Global University (CGU), Bhubaneswar, Odisha  
**Department:** Computer Science and Engineering  
**Authors:** Satyaprakash Rout (2301020206), Likuna Swain (2301020252), Ch Saipriya Patra (2301020205), Arpeet Barik (2301020228)  
**Supervisor:** Prof. Soumya Sahoo  

---

## 1. Ground Truth Generation Provenance

All numbers in this ledger are deterministically reproducible.
- **Master Execution Command:**
  ```powershell
  python final_submission/scripts/generate_ground_truth.py
  python final_submission/scripts/benchmark_api.py
  pytest backend/tests -v
  ```
- **Execution Runtime:** Python 3.12.5 (Windows AMD64), PyTorch 2.8.0, Scikit-Learn 1.6.1, XGBoost 3.1.1, SciPy 1.15.2, Pandas 2.3.3, NumPy 2.0.2.
- **Fixed Random Seed:** `42` (applied to NumPy, PyTorch, Scikit-Learn, and Optuna).
- **Zero Future Leakage:** 80/20 chronological time-series partition (Train: 2018–mid 2023 [9,609 records]; Test: mid 2023–end 2024 [2,403 records]).

---

## 2. Dataset Metadata & Cryptographic Checksums

**Source File:** `results/dataset_statistics.csv`

| Metric / Attribute | Delhi | Mumbai | Bangalore | Chennai | Hyderabad | Pan-India Total |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Raw Records (Days)** | 2,191 | 2,188 | 2,556 | 2,551 | 2,556 | **12,042** |
| **Start Date** | 2018-01-01 | 2019-01-01 | 2018-01-01 | 2018-01-01 | 2018-01-01 | **2018-01-01** |
| **End Date** | 2024-12-31 | 2024-12-31 | 2024-12-31 | 2024-12-31 | 2024-12-31 | **2024-12-31** |
| **Duration (Span)** | 7 Years | 6 Years | 7 Years | 7 Years | 7 Years | **7 Continuous Years** |
| **Missing Rate (%)** | 0.00% | 0.00% | 0.00% | 0.01% (1 cell) | 0.00% | **< 0.01% (1 cell / 84,294)** |
| **Raw CPCB CSV SHA-256** | `3c68ba26f7b9fabb` | `ed89c163fa257465` | `04f27e17ee10deaf` | `be1fd6eb20417c2d` | `249efa9f58773959` | *(Verified Immutable)* |
| **ERA5 Weather SHA-256** | `8f5cb598dc468dc0` | `432db5193630f555` | `b6807baec3eec7e1` | `6ae978f877c8651a` | `e2a563ecb4c7943c` | *(Verified Immutable)* |

---

## 3. Multimodal Imputation Benchmark (Seeded 7% Artificial Masking)

**Source File:** `results/imputation_metrics.csv`  
*Test Setup:* 5,057 values synthetically masked across 6 criteria pollutants (seed=42, fraction=0.07).

| Pollutant Parameter | Masked Entries | KNN ($k=5$) RMSE | MICE ($T=10$) RMSE | SVD (rank=4) RMSE | Best Method |
| :--- | :---: | :---: | :---: | :---: | :---: |
| $\text{PM}_{2.5}$ | 867 | 0.6867 | **0.0042** | 5.9357 | **MICE** |
| $\text{PM}_{10}$ | 823 | 0.8374 | **0.0066** | 50.6234 | **MICE** |
| $\text{NO}_2$ | 833 | 0.4886 | **0.0050** | 44.3287 | **MICE** |
| $\text{SO}_2$ | 836 | 1.0230 | **0.0088** | 70.2911 | **MICE** |
| $\text{CO}$ | 890 | 0.0104 | **0.0029** | 0.0420 | **MICE** |
| $\text{O}_3$ | 808 | 0.7042 | **0.0075** | 17.9827 | **MICE** |
| **Overall Mean RMSE** | **5,057** | **0.6975** | **0.0061** | **40.1903** | **MICE** |

---

## 4. MI-MMA Autoencoder Reconstruction Evaluation

**Source File:** `results/autoencoder_metrics.csv`  
*Architecture:* Symmetric Dense Bottleneck ($7 \rightarrow 32 \rightarrow 12 \rightarrow 32 \rightarrow 7$).

| Autoencoder Branch | Input Dimension | Latent Bottleneck | Reconstruction MSE Loss |
| :--- | :---: | :---: | :---: |
| **KNN_AE** | 7 | 12 | $4.00 \times 10^{-6}$ (0.000004) |
| **MICE_AE** | 7 | 12 | $1.00 \times 10^{-5}$ (0.000010) |
| **SVD_AE** | 7 | 12 | $1.60 \times 10^{-5}$ (0.000016) |
| **Fused MI-MMA Representation** | 21 | **36** | **$1.00 \times 10^{-5}$ (0.000010)** |

---

## 5. Master Ablation Matrix & Model Benchmarking

**Source File:** `results/ablation_matrix.csv`  
*Evaluation Period:* Held-Out Test Set (2,403 samples; July 2023 to December 2024).  
*Accuracy Definition:* $\text{Accuracy} = \max(0, 100\% - \text{MAPE})$. It is a bounded continuous regression accuracy, **not** classification accuracy.

| Model / Configuration Name | Features / Inputs Scope | RMSE | MAE | $R^2$ Score | MAPE (%) | Accuracy (%) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Simple Linear Baseline (Ridge)** | Autoregressive pollutant lags ($t-1 \dots t-3$) | 17.06 | 11.64 | 0.8964 | 13.31% | 86.69% |
| **Baseline: Kashyap et al. (2020)** | Standalone Random Forest on base lags | 17.54 | 11.63 | 0.8904 | 13.41% | 86.59% |
| **Ablation: Standalone XGBoost** | Standalone XGBoost on base lags | 17.33 | 11.60 | 0.8931 | 13.37% | 86.63% |
| **Baseline: Rao et al. (2023)** | Multimodal Imputation + 36 MMA + XGBoost | 17.08 | 11.53 | 0.8961 | 13.35% | 86.65% |
| **Ablation: RF + ERA5 Meteorology** | Base lags + 5 ERA5 weather variables + lags | 17.04 | 11.47 | 0.8966 | 13.50% | 86.50% |
| **Ablation: RF + Weather + Events** | Above + Diwali window & Stubble season flags | 16.97 | 11.41 | 0.8974 | 13.43% | 86.57% |
| **Proposed: Dual Stacking Ensemble (Base)** | **RF + XGBoost + Meteorology + Events (All 81)**| **16.64** | **11.12** | **0.9014** | **12.98%** | **87.02%** |
| **Proposed: Optuna-Tuned Production Ensemble** | **Base Stacking + 100-Trial TPE Optimization** | **13.84** | **9.12** | **0.9248** | **8.58%** | **91.42%** |
| **Ablation: Standalone LSTM** | 7-day recurrent sequence tensor ($T=7$) | 21.68 | 15.52 | 0.8312 | 17.77% | 82.23% |
| **Ablation: Tri-Ensemble (RF+XGB+LSTM)**| Equal weighted average ($1/3, 1/3, 1/3$) | 18.55 | 13.03 | 0.8782 | 14.94% | 85.06% |
| **Ensemble Comparison (Aligned)** | RF + XGBoost on strictly aligned LSTM samples | 16.68 | 11.14 | 0.9016 | 12.95% | 87.05% |

### Key Architectural Finding & Honesty Disclosure:
The Deep Recurrent LSTM Forecaster degraded performance ($\text{RMSE} = 21.68, R^2 = 0.8312$), and adding it into a Tri-Ensemble worsened the error ($\text{RMSE} = 18.55$ vs. $16.64$). Following the baseline ablation, Optuna Tree-structured Parzen Estimator (TPE) Bayesian hyperparameter tuning across 100 trials elevated the production model to **$\text{RMSE} = 13.84, \text{MAE} = 9.12, R^2 = 0.9248$, and $\text{Accuracy} = 91.42\%$ (MAPE = $8.58\%$)**. Therefore, **the proposed model is the Dual Stacking Ensemble (Random Forest + XGBoost)**, and LSTM is openly documented as evaluated-and-excluded.

---

## 6. Statistical Significance Hypothesis Testing

**Source File:** `results/significance_tests.csv`  
*Comparison:* Proposed Dual Ensemble vs. Best Single Model (XGBoost) on absolute per-sample test residuals ($N = 2,368$ aligned samples).

| Statistical Hypothesis Test | Sample Size ($N$) | Mean Difference ($\bar{d}$) | Std Dev ($s_d$) | Test Statistic | $p$-value | Significance Threshold | Result |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Paired Student's $t$-test (Parametric)** | 2,368 | -0.1982 | 2.5911 | $t = -3.722$ | **$p = 0.0002$** | $p < 0.05$ | **Statistically Significant ($p < 0.05$)** |
| **Paired Wilcoxon Signed-Rank (Non-Parametric)** | 2,368 | -0.1982 | 2.5911 | $W = 1,263,583.0$ | **$p = 3.003 \times 10^{-5}$** | $p < 0.01$ | **Highly Significant ($p < 0.01$)** |

---

## 7. Multi-Horizon Forecasting Degradation

**Source File:** `results/horizon_metrics.csv`

| Forecast Horizon | Physical Lead Time | Test RMSE | Test MAE | Test $R^2$ Score | Test MAPE (%) | Accuracy (1-MAPE, %) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Day+1 ($t+1$)** | 24 Hours Forward | **16.66** | **11.10** | **0.9012** | **12.97%** | **87.03%** |
| **Day+2 ($t+2$)** | 48 Hours Forward | 19.92 | 13.70 | 0.8584 | 16.54% | 83.46% |
| **Day+3 ($t+3$)** | 72 Hours Forward | 21.12 | 13.89 | 0.8406 | 17.36% | 82.64% |

---

## 8. Leave-One-City-Out (LOCO) Zero-Shot Cross-City Generalization

**Source File:** `results/loco_metrics.csv`  
*Protocol:* Model trained on 4 metropolitan centers and evaluated zero-shot on the 5th held-out city without localized retraining.

| Held-Out City | Training Metros | Zero-Shot Test Samples | RMSE | MAE | $R^2$ Score | MAPE (%) | Accuracy (%) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Delhi** | Mumbai, Chennai, Hyderabad, Bangalore | 2,185 | 30.14 | 24.15 | 0.7186 | 15.56% | 84.44% |
| **Mumbai** | Delhi, Chennai, Hyderabad, Bangalore | 2,182 | 22.27 | 15.57 | 0.8320 | 14.70% | 85.30% |
| **Chennai** | Delhi, Mumbai, Hyderabad, Bangalore | 2,545 | 21.48 | 14.51 | **0.5155** | 19.24% | 80.76% |
| **Hyderabad** | Delhi, Mumbai, Chennai, Bangalore | 2,550 | 14.64 | 10.92 | 0.8145 | 14.61% | 85.39% |
| **Bangalore** | Delhi, Mumbai, Chennai, Hyderabad | 2,550 | 15.33 | 11.37 | 0.6462 | 16.56% | 83.44% |
| **Pan-India LOCO Mean** | **4-Metro Leave-One-Out** | **12,012** | **20.77** | **15.30** | **0.7054** | **16.13%** | **83.87%** |

### Critical Finding & Honesty Disclosure:
Cross-city generalization degrades significantly from $R^2 = 0.9014$ to a mean of $R^2 = 0.7054$. **Chennai exhibits the sharpest collapse ($R^2 = 0.5155$)**, driven by coastal maritime boundary layer interactions and unique industrial emissions. This directly justifies VayuDrishti's Two-Tier Architecture: 5 metros use locally trained ML models; unmonitored cities use Copernicus CAMS / NOAA GFS atmospheric modeling.

---

## 9. Empirical Coverage of the 90% Prediction Interval

**Source File:** `results/interval_coverage.csv`  
*Formula:* $\hat{y}_{t+1} \in \left[ \hat{y} - 1.645 \times \text{RMSE}_{\text{city}},\, \hat{y} + 1.645 \times \text{RMSE}_{\text{city}} \right]$.

| Evaluated City | Test Samples | City RMSE | Margin of Error ($\pm$) | Inside Interval | Empirical Coverage (%) | Nominal Level | Real Figure Note |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Delhi** | 437 | 21.64 | $\pm 35.60$ | 383 | **87.64%** | 90.0% | Below 90% (winter smog tails) |
| **Mumbai** | 437 | 18.11 | $\pm 29.79$ | 387 | **88.56%** | 90.0% | Below 90% (coastal boundary layer) |
| **Chennai** | 509 | 18.30 | $\pm 30.10$ | 469 | **92.14%** | 90.0% | Above nominal |
| **Hyderabad** | 510 | 11.09 | $\pm 18.25$ | 465 | **91.18%** | 90.0% | Above nominal |
| **Bangalore** | 510 | 12.86 | $\pm 21.16$ | 459 | **90.00%** | 90.0% | Exactly nominal |
| **Overall Pan-India** | **2,403** | **16.64** | **$\pm 27.37$** | **2,163** | **90.01%** | **90.0%** | **Well-Calibrated** |

---

## 10. Granular Error Analysis by City, Season & Episodic Shock

**Source File:** `results/error_analysis.csv`

| Analysis Segment | Category / Value | Sample Count | RMSE | MAE | $R^2$ Score | Mean Actual AQI |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **City-Wise** | Delhi | 437 | 21.64 | 13.68 | 0.8403 | 178.3 |
| **City-Wise** | Mumbai | 437 | 18.11 | 13.22 | 0.8501 | 100.3 |
| **City-Wise** | Chennai | 509 | 18.30 | 12.36 | 0.4921 | 72.2 |
| **City-Wise** | Hyderabad | 510 | 11.09 | 7.92 | 0.7220 | 79.0 |
| **City-Wise** | Bangalore | 510 | 12.86 | 9.09 | 0.7229 | 73.6 |
| **Seasonal** | Winter (Dec–Feb) | 593 | **18.86** | 12.92 | 0.8784 | 121.4 |
| **Seasonal** | Summer (Mar–May) | 460 | 17.17 | 11.54 | 0.8733 | 102.4 |
| **Seasonal** | Monsoon (Jun–Sep) | 776 | **12.78** | 8.55 | 0.8155 | 65.8 |
| **Seasonal** | Post-Monsoon (Oct–Nov) | 574 | 18.29 | 12.38 | 0.9013 | 115.3 |
| **Episodic Event** | Diwali Window ($\pm 2$ days) | 50 | **35.17** | **26.13** | **0.5534** | **149.7** |
| **Episodic Event** | Non-Diwali Normal Days | 2,353 | **16.02** | **10.80** | **0.9068** | **97.3** |
| **Episodic Event** | Stubble Season (Oct 15–Nov 25) | 412 | **19.13** | **12.61** | **0.8942** | **124.8** |
| **Episodic Event** | Non-Stubble Season | 1,991 | **16.08** | **10.81** | **0.8966** | **92.9** |

---

## 11. Epidemiological Health Risk Index (HRI) & Sensitivity Analysis

### 11.1 Baseline Demographic Tier Rates on Test Set
**Source File:** `results/hri_tier_rates.csv`  
*Shared Baseline Cutoffs from General Public:* $P_{25} = 7.121,\, P_{75} = 14.715,\, P_{90} = 23.855$.

| Demographic Group | Multiplier ($V_g$) | LOW ($\le P_{25}$) | MODERATE ($P_{25}-P_{75}$) | HIGH ($P_{75}-P_{90}$) | SEVERE ($> P_{90}$) | Total Alert Rate (HIGH + SEVERE) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **General Public** | 1.0 | 25.63% | 49.44% | 14.90% | 10.03% | **24.93% ($\approx 25\%$)** |
| **Children & Elderly** | 1.3 | 7.49% | 52.60% | 23.47% | 16.44% | **39.91% ($\approx 40\%$)** |
| **Respiratory Patients** | 1.6 | 1.83% | 42.45% | 32.92% | 22.80% | **55.72% ($\approx 56\%$)** |

### 11.2 Sensitivity Analysis Across Multiplier Configurations
**Source File:** `results/hri_sensitivity.csv`

| Multiplier Regime Name | Child/Elderly $V_g$ | Child/Elderly Alert Rate (%) | Respiratory $V_g$ | Respiratory Alert Rate (%) | Clinical Interpretation |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Conservative** | 1.1 | 29.26% | 1.3 | 39.91% | Modest differentiation; risk under-alerting |
| **Moderate-Low** | 1.2 | 33.21% | 1.5 | 50.02% | Balanced clinical escalation |
| **Proposed Baseline** | **1.3** | **39.91%** | **1.6** | **55.72%** | **Optimal balance of sensitivity & alert fatigue** |
| **Moderate-High** | 1.4 | 44.78% | 1.8 | 65.83% | Heightened sensitivity for severe clinical cohorts |
| **Aggressive Precautionary** | 1.5 | 50.02% | 2.0 | 75.49% | Severe alert frequency; potential alarm fatigue |

### Mathematical Proof: Why Shared Cutoffs Are Mandatory
If group-specific percentiles $P_{75}^{(g)} = \text{Quantile}(HRI_g, 0.75)$ were used, then since $HRI_g = V_g \cdot HRI_{\text{GP}}$, we have:
$$P_{75}^{(g)} = \text{Quantile}(V_g \cdot HRI_{\text{GP}}, 0.75) = V_g \cdot \text{Quantile}(HRI_{\text{GP}}, 0.75) = V_g \cdot P_{75}^{(\text{GP})}$$
Therefore, the alert test condition becomes:
$$HRI_g > P_{75}^{(g)} \iff V_g \cdot HRI_{\text{GP}} > V_g \cdot P_{75}^{(\text{GP})} \iff HRI_{\text{GP}} > P_{75}^{(\text{GP})}$$
The multiplier $V_g$ cancels out mathematically, resulting in an identical 25% alert rate for all groups and completely destroying demographic differentiation. Hence, **a single shared cutoff scale derived from the General Public baseline is mathematically required.**

---

## 12. TreeSHAP Global Feature Importance Ranking (Top 15)

**Source File:** `results/shap_importance.csv`

| Rank | Feature Code | Feature Description | Mean Absolute SHAP ($\mu g/m^3$ Impact) | Physical Interpretation |
| :---: | :--- | :--- | :---: | :--- |
| **1** | `AQI` | Same-day observed AQI | **19.54** | Primary autoregressive persistence |
| **2** | `PM2.5` | Same-day fine particulate concentration | **6.44** | Dominant CPCB sub-index pollutant |
| **3** | `humidity` | Surface relative humidity (%) | **3.67** | Regulates hygroscopic particulate growth |
| **4** | `wind_speed` | 10m horizontal wind speed ($m/s$) | **1.92** | Controls mechanical ventilation & dispersion |
| **5** | `AQI_lag3` | AQI 3 days prior ($t-3$) | **1.69** | Multi-day atmospheric inertia |
| **6** | `pressure_lag1`| Surface pressure yesterday ($t-1$) | **1.65** | Synoptic frontal system transition |
| **7** | `wind_dir` | Dominant wind direction (degrees) | **1.45** | Plume transport azimuth (e.g. stubble smoke) |
| **8** | `fused_0` | KNN-Imputed Autoencoder Bottleneck dim 0 | **1.31** | Latent cross-pollutant manifold pattern |
| **9** | `AQI_lag1` | AQI yesterday ($t-1$) | **1.04** | Short-term temporal correlation |
| **10** | `humidity_lag1`| Humidity yesterday ($t-1$) | **0.95** | Moisture accumulation in boundary layer |
| **11** | `day_of_week` | Day of week index ($0 \dots 6$) | **0.77** | Anthropogenic weekday vs. weekend traffic |
| **12** | `humidity_lag2`| Humidity 2 days ago ($t-2$) | **0.75** | Multi-day moisture persistence |
| **13** | `AQI_lag2` | AQI 2 days prior ($t-2$) | **0.71** | Mid-term autoregression |
| **14** | `temp_lag2` | Temperature 2 days ago ($t-2$) | **0.61** | Thermal stability trend |
| **15** | `temp` | Ambient temperature (°C) | **0.58** | Photochemical reaction rate & inversion |

---

## 13. Live Operational Validation Log Performance

**Source File:** `results/live_validation_metrics.csv`  
*Persistence:* SQLite database (`backend/outputs/validation_log.db`).  
*History:* 60 genuine daily logs across 12 distinct dates (September 1 to September 15, 2026).

| Metropolitan City | Genuine Logged Days | Start Date | End Date | Live RMSE | Live MAE | Live MAPE (%) | Operational Accuracy (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Bangalore** | 12 | 2026-09-01 | 2026-09-15 | **9.44** | **7.51** | **10.21%** | **89.79%** |
| **Chennai** | 12 | 2026-09-01 | 2026-09-15 | **17.61** | **11.41** | **12.91%** | **87.09%** |
| **Delhi** | 12 | 2026-09-01 | 2026-09-15 | **48.01** | **23.42** | **12.43%** | **87.57%** |
| **Hyderabad** | 12 | 2026-09-01 | 2026-09-15 | **12.32** | **10.31** | **12.64%** | **87.36%** |
| **Mumbai** | 12 | 2026-09-01 | 2026-09-15 | **32.65** | **21.18** | **33.35%** | **66.65%** |
| **Overall Pan-India** | **12 Days (60 Logs)** | **2026-09-01** | **2026-09-15** | **28.01** | **14.76** | **16.31%** | **83.69%** |

---

## 14. FastAPI Endpoint Latency & Performance Benchmarks

**Source File:** `results/api_benchmarks.csv`  
*Measurement Protocol:* 10 warm requests per endpoint using HTTP TestClient under identical runtime.

| Endpoint URI | Method | Functional Scope | Median Latency | 95th Percentile ($p_{95}$) | HTTP Status |
| :--- | :---: | :--- | :---: | :---: | :---: |
| `/` | `GET` | System Health Check & Uptime | **2.24 ms** | 2.81 ms | `200 OK` |
| `/metrics` | `GET` | Frozen ML Evaluation Metrics Report | **2.23 ms** | 2.79 ms | `200 OK` |
| `/config/cities` | `GET` | 38-City Registry & Model Tier Mapping | **2.53 ms** | 2.75 ms | `200 OK` |
| `/cities` | `GET` | City Telemetry Summaries | **2.60 ms** | 2.77 ms | `200 OK` |
| `/forecast/{city}` | `GET` | Day+1 Stacking Ensemble Inference | **4.89 ms** | 5.82 ms | `200 OK` |
| `/risk/{city}` | `GET` | HRI Demographic Calculations | **3.25 ms** | 4.27 ms | `200 OK` |
| `/alerts/{city}` | `GET` | City-Specific Public Health Alerts | **2.57 ms** | 2.91 ms | `200 OK` |
| `/alerts` | `GET` | Pan-India Active Alert Feed | **2.37 ms** | 2.60 ms | `200 OK` |
| `/history/{city}` | `GET` | 30-Day Actual vs. Forecast History | **2.53 ms** | 2.61 ms | `200 OK` |
| `/validation/{city}` | `GET` | Live SQLite Rolling Verification Logs | **3.05 ms** | 3.51 ms | `200 OK` |
| `/live-comparison/{city}`| `GET` | Verification Triple (Live vs Pred) | **3.25 ms** | 4.79 ms | `200 OK` |

---

## 15. Unit & Integration Test Suite Verification

**Source File:** `results/pytest_output.txt`  
- **Test Runner:** `pytest 9.0.3` (Python 3.12.5)  
- **Total Test Cases Executed:** 17  
- **Total Test Cases Passed:** **17 (100% Pass Rate)**  
- **Total Test Cases Failed:** 0  
- **Execution Elapsed Time:** 11.40 seconds  
