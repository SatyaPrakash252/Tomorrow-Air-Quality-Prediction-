# VayuDrishti: Final Presentation Defense Speaker Script

**Project Title:** AI-Driven Air Quality Forecasting and Public Health Risk Alert System for Indian Metropolitan Cities  
**Milestone:** 7th Semester Major Project Final Evaluation (Stage-1)  
**Total Allocated Time:** 15 Minutes (12 Minutes Presentation + 3 Minutes Demonstration) followed by Panel Defense  
**Slide Deck:** `VayuDrishti_Final_Presentation.pptx` (10 Slides using Official CGU Template)

---

## Team Speaker Roles & Time Allocations

| Speaker | Role | Allocated Slides | Time Window | Cumulative Time |
| :--- | :--- | :--- | :--- | :--- |
| **Satyaprakash Rout** (Lead) | Architecture & Introduction | Slides 1, 2, 5 | 0:00 – 4:00 | 4:00 |
| **Likuna Swain** | Data Engineering & DL Pipeline | Slides 3, 4 | 4:00 – 7:30 | 7:30 |
| **Ch Saipriya Patra** | Health Risk Index & Clinical Advisory | Slides 6, 7 | 7:30 – 10:30 | 10:30 |
| **Arpeet Barik** | Results, Production APIs & Conclusion | Slides 8, 9, 10 | 10:30 – 13:00 | 13:00 |
| **All Team Members** | Live Dashboard Demonstration | Live Web Platform | 13:00 – 15:00 | 15:00 |

---

## Slide-by-Slide Detailed Script

### SLIDE 1: Title & Administrative Cover (0:00 – 1:00)
**Speaker: Satyaprakash Rout**

> "Respected Chairman of the Evaluation Committee, honorable External Examiners, Head of Department, and our esteemed guide Prof. Soumya Sahoo: Good morning.
>
> I am Satyaprakash Rout, presenting along with my team members Likuna Swain, Ch Saipriya Patra, and Arpeet Barik. Today, we are proud to present our 7th Semester Major Project titled: **'AI-Driven Air Quality Forecasting and Public Health Risk Alert System for Indian Metropolitan Cities'**, manifested in our production-grade platform: **VayuDrishti (वायुदृष्टि)**.
>
> Urban air pollution in India is a catastrophic public health crisis, claiming over 1.6 million lives annually. Traditional static warning systems notify citizens after peak pollution has already poisoned the airshed. Our project transforms this paradigm: transitioning public health protection from reactive post-facto measurement to 72-hour forward-looking proactive defense.
>
> Let us begin by examining the exact engineering gaps we set out to resolve."

*(Transition: Click to Slide 2)*

---

### SLIDE 2: Problem Statement & Research Objectives (1:00 – 2:30)
**Speaker: Satyaprakash Rout**

> "If we examine the current state of ambient air quality monitoring in India, we identify four critical failure points:
> 
> 1. **High Sensor Missingness:** Ground-level Continuous Ambient Air Quality Monitoring Stations (CAAQMS) suffer up to 18.4% missing telemetry due to power interruptions and sensor calibration failures. Most existing portals rely on naive forward-fill, severely distorting temporal dynamics.
> 2. **Single-Pollutant Max Distortion:** The National Air Quality Index (NAQI) reports only the maximum sub-index of a single pollutant. If PM2.5, NO2, and Ozone are all simultaneously elevated, NAQI completely ignores the supra-additive toxic cocktail.
> 3. **Uniform Population Fallacy:** A 70-year-old asthmatic patient and a healthy 20-year-old athlete receive the identical static warning ('Moderate'), despite radically different clinical vulnerability thresholds.
> 4. **Lack of Uncertainty Quantification:** Point predictions fail to tell municipal decision-makers how confident the model is during catastrophic winter inversion episodes.
>
> To solve this, our project delivers four rigorous objectives: First, an end-to-end MICE imputation and Deep Autoencoder feature pipeline; Second, an Optuna-tuned Stacking Ensemble forecasting AQI up to 72 hours ahead with 90% conformalized prediction intervals; Third, a clinically grounded Health Risk Index with demographic stratification; and Fourth, a sub-10ms production API serving 38 Indian cities.
>
> I now hand over to Likuna Swain to explain our data engineering and model architecture."

*(Transition: Handover to Likuna Swain, Click to Slide 3)*

---

### SLIDE 3: Literature Survey & Research Gaps (2:30 – 4:00)
**Speaker: Likuna Swain**

> "Thank you, Satyaprakash. In conducting our literature survey across IEEE, Elsevier, and Springer venues, we surveyed foundational works including CPCB 2014, WHO 2021 guidelines, and recent deep learning studies such as Kashyap et al. 2025.
>
> While classical SARIMA and Holt-Winters models capture linear seasonality, they fail catastrophically during non-linear peak events like Diwali and crop residue burning. Conversely, pure Deep LSTM and GRU networks frequently overfit on daily tabular records and lack interpretability.
>
> Crucially, almost all published literature suffers from two fatal flaws: first, evaluating on single-station datasets with temporal data leakage; and second, failing to quantify prediction uncertainty. 
> 
> VayuDrishti addresses these exact gaps by pairing gradient-boosted trees and deep autoencoders within a strict time-series cross-validation harness."

*(Transition: Click to Slide 4)*

---

### SLIDE 4: Proposed Methodology & System Architecture (4:00 – 6:00)
**Speaker: Likuna Swain**

> "Moving to our technical methodology: our pipeline operates in four synchronized layers:
>
> 1. **Ingestion & Data Cleansing:** We ingest multi-year hourly CAAQMS telemetry spanning 12,042 validated records across 5 primary metropolitan centers (Delhi, Mumbai, Bengaluru, Chennai, Hyderabad) plus live telemetry for 33 regional centers. 
> 2. **Imputation:** We compare Mean, Forward Fill, KNN, and Multivariate Imputation by Chained Equations (MICE). MICE achieves an RMSE of 2.14, outperforming naive mean imputation by 75.6%.
> 3. **Nonlinear Compression:** A Deep Autoencoder compresses 6 criteria pollutants into a 4-dimensional latent representation with an MSE of 0.0084, capturing complex photochemical co-pollutant dynamics.
> 4. **Stacking Ensemble:** We combine XGBoost (capturing sharp non-linear gradient spikes) and Random Forest (stabilizing variance) under a Ridge regression meta-learner optimized via Optuna Bayesian search over 100 trials.
> 
> Furthermore, we generate Pinball-loss calibrated quantile regressors at the 5th and 95th percentiles to produce calibrated 90% prediction intervals."

*(Transition: Handover to Satyaprakash Rout, Click to Slide 5)*

---

### SLIDE 5: Hardware & Software Requirements (6:00 – 7:30)
**Speaker: Satyaprakash Rout**

> "To guarantee production readiness, our architecture is engineered for high throughput and zero cloud lock-in:
>
> - **Backend:** Python 3.12 with FastAPI serving asynchronous ASGI endpoints.
> - **In-Memory Cache:** Dual-layer caching with Redis and an in-process LRU cache, keeping average prediction latency at just 2.41 milliseconds.
> - **Frontend:** React 19, TypeScript, and Vite, delivering interactive 60fps charting via Recharts and an intuitive geographic view.
> - **Fault Resilience:** If primary CAAQMS sensors drop offline, our upstream circuit breaker falls back gracefully to Copernicus CAMS global atmospheric numerical models in under 45 milliseconds.
>
> I now invite Ch Saipriya Patra to present our Health Risk Index and clinical advisory engine."

*(Transition: Handover to Ch Saipriya Patra, Click to Slide 6)*

---

### SLIDE 6: Implementation Details — Health Risk Modeling (7:30 – 9:00)
**Speaker: Ch Saipriya Patra**

> "Thank you, Satyaprakash. A key contribution of VayuDrishti is the **Health Risk Index (HRI)**.
>
> Traditional NAQI uses a piecewise linear single-pollutant maximum. If PM2.5 is 150 and Ozone is 120, NAQI solely reports PM2.5. However, epidemiological studies (WHO 2021, Tiwary et al. 2021) demonstrate that multi-pollutant exposure produces supra-additive cellular oxidative stress.
>
> We mathematically formulate HRI as:
> $$\text{HRI} = \min\left(100, \, 100 \cdot \left[1 - \exp\left(-\sum_{p} w_p \left(\frac{C_p}{S_p}\right)^{\gamma_p}\right)\right] \cdot \beta_d\right)$$
>
> Where:
> - $C_p$ is pollutant concentration and $S_p$ is its NAAQS standard threshold.
> - $w_p$ are toxicological hazard weights ($0.35$ for PM2.5, $0.20$ for PM10 and NO2, $0.10$ for O3, $0.05$ for SO2 and CO).
> - $\beta_d$ represents the physiological vulnerability multiplier: $1.0\times$ for healthy adults, $1.3\times$ for children and elderly individuals with reduced respiratory volume, and $1.6\times$ for diagnosed asthma/COPD patients.
>
> As shown on the slide, this triggers four clear triage alert tiers: Normal, Caution, High Risk, and Severe Medical Hazard."

*(Transition: Click to Slide 7)*

---

### SLIDE 7: Work Carried Out & Milestones Completed (9:00 – 10:30)
**Speaker: Ch Saipriya Patra**

> "Over the course of the 7th semester, our team has executed 100% of our planned milestones:
>
> - **Phase 1 (Data Foundation):** Consolidated 12,042 records, conducted temporal leakage audits, and trained MICE imputation models.
> - **Phase 2 (Deep Learning & Feature Engineering):** Built and validated the PyTorch Deep Autoencoder and generated SHAP explainability matrices.
> - **Phase 3 (Ensemble & Quantile Regression):** Trained Ridge, RF, XGBoost, and the Stacking Ensemble across 24h, 48h, and 72h forecast horizons.
> - **Phase 4 (Full-Stack Deployment):** Completed the FastAPI backend with 9 comprehensive endpoints and built the React 19 responsive dashboard.
> - **Phase 5 (Academic Deliverables):** Prepared our 18,800-word IQAC report, 30-question defense ledger, and an IEEE conference manuscript.
>
> I now hand over to Arpeet Barik to present our experimental results and empirical benchmarks."

*(Transition: Handover to Arpeet Barik, Click to Slide 8)*

---

### SLIDE 8: Experimental Results & Ablation Analysis (10:30 – 11:45)
**Speaker: Arpeet Barik**

> "Thank you, Saipriya. Let us examine the empirical proof of our system's superiority:
>
> 1. **Model Ablation:** Our Dual Stacking Ensemble achieves a test $R^2$ of **0.8997** and an RMSE of **16.78**. It outperforms single Ridge regression ($R^2 = 0.8143$), standalone Random Forest ($R^2 = 0.8872$), and standalone XGBoost ($R^2 = 0.8924$).
> 2. **Honest Model Exclusion:** We openly tested a Deep LSTM ($R^2 = 0.8105, \text{RMSE} = 21.68$) and a Tri-Ensemble including LSTM ($R^2 = 0.8617$). The deep sequential network overfitted tabular meteorological lag features, confirming that the Dual Tree Ensemble is objectively superior.
> 3. **Statistical Significance:** Paired Student's $t$-test yields $t = -3.722, p = 0.0002 < 0.01$, and Wilcoxon signed-rank test yields $W = 1,263,583.0, p = 3.003 \times 10^{-5} < 0.01$, confirming the ensemble's improvement is statistically robust.
> 4. **Quantile Coverage:** Across 2,368 held-out test intervals, our 90% prediction intervals achieved an empirical coverage (PICP) of **90.01%** with a sharp Mean Prediction Interval Width (MPIW) of **43.91 AQI points**."

*(Transition: Click to Slide 9)*

---

### SLIDE 9: System Benchmarks, Live Validation & Honest Limitations (11:45 – 12:30)
**Speaker: Arpeet Barik**

> "On the operational and systems side:
>
> - **API Performance:** Under 50 concurrent requests, our `/forecast` endpoint delivers an average latency of **2.41 ms**, with 99th percentile latency of **5.82 ms**, and **zero dropped requests** ($0.0\%$ error rate).
> - **Live Validation:** Over 30 days of real-world live tracking, the system maintained an $R^2$ of **0.8712** and RMSE of **18.42**, showing minimal degradation from offline benchmarks.
> - **Academic Honesty & Limitations:** In our Leave-One-City-Out (LOCO) cross-validation, models trained on inland metros collapsed when predicting coastal Chennai ($R^2 = 0.5155$) due to maritime land-sea breeze inversions. Furthermore, extreme winter fog in Delhi reduced interval coverage to $87.64\%$. 
> 
> Rather than masking these drops, we use them to substantiate our Two-Tier operational architecture: using trained local models for metros and Copernicus CAMS global atmospheric telemetry for uncalibrated regional centers."

*(Transition: Click to Slide 10)*

---

### SLIDE 10: Conclusion, Future Scope & Team Contributions (12:30 – 13:00)
**Speaker: Arpeet Barik**

> "In conclusion, VayuDrishti bridges the gap between academic air quality modeling and operational public health protection. We have delivered a fully reproducible, statistically verified, and sub-10ms system ready for municipal adoption.
>
> In Stage-2, our roadmap targets:
> 1. Integration of INSAT-3D satellite aerosol optical depth imagery;
> 2. Automated SMS/WhatsApp multilingual alerts for vulnerable communities;
> 3. Wearable IoT synchronization for personalized real-time micro-exposure tracking.
>
> We now invite the panel to observe a brief 2-minute live demonstration of the operational platform."

*(Transition: Switch screen to browser on http://localhost:5173)*

---

## Live System Demonstration Script (13:00 – 15:00)
**Lead Demonstrator: Satyaprakash Rout with Team**

1. **Overview & National AQI Map (30s):** Show live status of 38 Indian cities, highlighting severe conditions in northern industrial corridors and moderate readings in coastal Odisha.
2. **72-Hour Forecast & Uncertainty Bands (45s):** Select Delhi, show the predicted AQI curve over 24h, 48h, and 72h horizons, and point out the shaded 90% prediction intervals reflecting weather volatility.
3. **Health Risk Index & Demographic Simulation (30s):** Open the HRI simulator, drag the PM2.5 slider from 80 to 220, and show how the demographic toggle immediately shifts children and asthmatic patients from 'Caution' into 'Severe Medical Hazard'.
4. **Alert Center & Verified Methodology (15s):** Showcase real-time triage alerts and the research tab linking verified ground-truth metrics.

> *"Thank you, honorable panel. We are now open for your questions."*
