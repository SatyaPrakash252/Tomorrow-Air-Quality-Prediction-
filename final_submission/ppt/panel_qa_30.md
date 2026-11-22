# VayuDrishti: 30 Master Defense Panel Questions & Rigorous Answers

**Project Title:** AI-Driven Air Quality Forecasting and Public Health Risk Alert System for Indian Metropolitan Cities  
**Milestone:** 7th Semester Major Project Final Evaluation (Stage-1)  
**Institution:** Department of Computer Science & Engineering, C.V. Raman Global University  
**Student Team:** Satyaprakash Rout (Lead), Likuna Swain, Ch Saipriya Patra, Arpeet Barik  
**Supervisor:** Prof. Soumya Sahoo  
**Ground Truth Reference:** All answers are verified against `final_submission/results/FACTS.md`.

---

## Category 1: Data Engineering, Cleansing & Integrity (Q1 – Q6)

### Q1: CAAQMS stations frequently lose connection. How does your system handle missing telemetry, and why did you choose MICE over simple interpolation?
**Answer (Likuna Swain / Satyaprakash Rout):**  
"In our 12,042-record ground truth dataset, missingness averaged **8.4%** across primary pollutants, peaking at **18.4%** during power and calibration outages. Simple linear interpolation or forward-fill assumes that air pollution remains constant or changes linearly across outages; however, meteorological shifts (such as a sudden nocturnal boundary layer collapse or wind reversal) invalidate this assumption.  
We benchmarked four imputation techniques under controlled synthetic missingness:
- **Mean Imputation:** RMSE = 8.76
- **Forward-Fill (LOCF):** RMSE = 6.42
- **KNN ($k=5$):** RMSE = 3.89
- **MICE (Multivariate Imputation by Chained Equations):** **RMSE = 2.14** (an improvement of **75.6%** over mean imputation).  
MICE models each missing pollutant as a regression function of all other correlated criteria pollutants and meteorological variables (temperature, relative humidity, wind speed), preserving genuine covariance structures without introducing synthetic bias."

### Q2: How did you prevent temporal data leakage during train/validation/test splitting?
**Answer (Satyaprakash Rout):**  
"Standard random $k$-fold cross-validation is disastrous for time-series forecasting because it samples past and future points indiscriminately, allowing future information to leak into past predictions.  
To completely eliminate leakage, we implemented a strict chronological split:
- **Training Set (80%):** Earliest 9,674 records spanning Day 1 to Day 400.
- **Held-Out Test Set (20%):** Most recent 2,368 records spanning Day 401 to Day 500.  
All transformations—including feature scaling, MICE imputation models, and Autoencoder normalization weights—were fitted **strictly on the training partition only** and subsequently applied to the test partition. A complete leakage audit verifying zero feature contamination is documented in `final_submission/results/leakage_audit.md`."

### Q3: What is the purpose of the Deep Autoencoder when gradient-boosted trees already perform feature selection?
**Answer (Likuna Swain):**  
"Gradient-boosted decision trees split along orthogonal feature axes and struggle to capture continuous nonlinear manifold geometries formed by simultaneous photochemical interactions—such as the titration reaction between NO and Ozone under solar radiation ($\text{NO} + \text{O}_3 \rightarrow \text{NO}_2 + \text{O}_2$).  
We designed a 3-layer symmetrical PyTorch Autoencoder ($6 \rightarrow 8 \rightarrow 4 \rightarrow 8 \rightarrow 6$) with LeakyReLU activations and batch normalization. It compresses the 6 criteria pollutants into a 4-dimensional latent bottleneck vector with a reconstruction loss of **$\text{MSE} = 0.0084$**. Injecting these 4 latent dimensions into the tree ensemble improved the overall test $R^2$ by $+0.0073$, proving that the compressed latent representations provide valuable non-linear co-pollutant interaction signals."

### Q4: Which features contribute most to your predictions, and how do you guarantee model explainability?
**Answer (Likuna Swain / Arpeet Barik):**  
"We compute TreeSHAP (SHapley Additive exPlanations) values across the 2,368 test samples (`final_submission/results/shap_importance.csv`). The top 5 predictive features are:
1. **$\text{PM}_{2.5}$ Lag 1 Day (24h prior):** Mean $|\text{SHAP}| = 14.82$ AQI points ($34.1\%$ relative importance)
2. **$\text{PM}_{10}$ Lag 1 Day:** Mean $|\text{SHAP}| = 8.64$ AQI points ($19.9\%$)
3. **$\text{PM}_{2.5}$ 7-Day Rolling Mean:** Mean $|\text{SHAP}| = 5.21$ AQI points ($12.0\%$)
4. **Boundary Layer Height / Ventilation Index:** Mean $|\text{SHAP}| = 3.94$ AQI points ($9.1\%$)
5. **Relative Humidity:** Mean $|\text{SHAP}| = 2.87$ AQI points ($6.6\%$).  
Autoencoder latent features contribute $4.2\%$ combined importance. This confirms our model aligns with established atmospheric physics: immediate inertial persistence dominates 24h forecasts, while meteorological dispersion and synoptic trends dictate 48h and 72h horizons."

### Q5: Did you account for extreme outlier events like Diwali or seasonal crop burning?
**Answer (Likuna Swain / Satyaprakash Rout):**  
"Yes. We engineered explicit cyclical temporal features ($\sin/\cos$ encoding of Day of Year, Month, and Day of Week) alongside binary holiday/festival indicator flags. Furthermore, we conducted a seasonal error breakdown (`final_submission/results/error_analysis.csv`):
- **Monsoon:** $\text{RMSE} = 11.24, R^2 = 0.9241$ (washout effect stabilizes air)
- **Summer:** $\text{RMSE} = 14.86, R^2 = 0.9015$ (dust storm variability)
- **Winter / Festival Inversion:** $\text{RMSE} = 22.45, R^2 = 0.8412$.  
Even during severe winter episodes where peak AQI exceeded 400, our Huber-loss optimization prevented gradient explosion, maintaining a high correlation without catastrophic error spikes."

### Q6: How do you verify sensor data provenance and detect physical sensor drift?
**Answer (Arpeet Barik):**  
"Our ingestion microservice enforces automated data validation rules via Pydantic schemas:
1. Physical range bounds ($0 \le \text{PM}_{2.5} \le 1000\,\mu\text{g/m}^3$, $0 \le \text{RH} \le 100\%$).
2. Rate-of-change delta limits (flagging delta $> 250\,\mu\text{g/m}^3/\text{hour}$ as sensor malfunction unless confirmed by adjacent regional sensors).
3. Zero-variance stagnation detection (flagging sensors emitting identical values for $> 6$ consecutive hours as stuck sensors). Flagged sensors are automatically routed to our MICE imputation module."

---

## Category 2: Machine Learning Architecture & Model Selection (Q7 – Q13)

### Q7: Why did you choose a Stacking Ensemble over a pure Deep Learning architecture like LSTM or Transformer?
**Answer (Satyaprakash Rout / Likuna Swain):**  
"This was a critical empirical decision. In our Phase 2 exploration, we rigorously benchmarked an optimized 2-layer LSTM with 64 hidden units alongside our tree ensembles (`final_submission/results/ablation_matrix.csv`):
- **Standalone LSTM:** $R^2 = 0.8105, \text{RMSE} = 21.68$
- **Tri-Ensemble (RF + XGB + LSTM):** $R^2 = 0.8617, \text{RMSE} = 18.55$
- **Standalone Random Forest:** $R^2 = 0.8872, \text{RMSE} = 17.82$
- **Standalone XGBoost:** $R^2 = 0.8924, \text{RMSE} = 17.39$
- **Dual Stacking Ensemble (RF + XGBoost):** **$R^2 = 0.8997, \text{RMSE} = 16.78$**.  
Recurrent architectures such as LSTM require hundreds of thousands of sequential continuous states to learn without overfitting. On 12,042 daily tabular records characterized by strong non-linear meteorological threshold effects and tabular lag features, tree ensembles capture sharp step-function transitions far more effectively than backpropagation through time. Rather than forcing an inferior deep network, we honestly excluded LSTM from our production ensemble based on empirical evidence."

### Q8: Is your improvement over standalone XGBoost statistically significant, or is it just marginal random noise?
**Answer (Arpeet Barik / Satyaprakash Rout):**  
"It is statistically significant at $p < 0.01$. We conducted formal inferential statistical tests on the paired absolute errors of the Dual Stacking Ensemble versus standalone XGBoost across all 2,368 test predictions (`final_submission/results/significance_tests.csv`):
- **Paired Two-Tailed Student's $t$-test:** $t = -3.722, \, p = 0.000201 \ll 0.01$
- **Wilcoxon Signed-Rank Test (non-parametric):** $W = 1,263,583.0, \, p = 3.003 \times 10^{-5} \ll 0.01$.  
Both parametric and non-parametric tests firmly reject the null hypothesis of equal performance with $99.98\%$ confidence."

### Q9: How does prediction accuracy degrade across the 24h, 48h, and 72h forecast horizons?
**Answer (Likuna Swain):**  
"As expected in chaotic atmospheric modeling, error increases with horizon distance (`final_submission/results/horizon_metrics.csv`):
- **24-Hour Horizon:** $R^2 = 0.8997, \, \text{RMSE} = 16.78, \, \text{MAE} = 11.89$
- **48-Hour Horizon:** $R^2 = 0.8541, \, \text{RMSE} = 20.31, \, \text{MAE} = 14.62$
- **72-Hour Horizon:** $R^2 = 0.8118, \, \text{RMSE} = 23.95, \, \text{MAE} = 17.48$.  
Even at 72 hours, the system maintains an $R^2 > 0.81$ and an MAE under 18 AQI points, providing actionable lead time for hospital preparedness and municipal traffic rationing before hazardous smog episodes peak."

### Q10: How did you tune the hyperparameters of your models?
**Answer (Likuna Swain):**  
"We utilized Optuna with Tree-structured Parzen Estimators (TPE) over 100 trials, evaluating under 5-fold expanding-window time-series cross-validation. For XGBoost, the optimal hyperparameters found were: `max_depth = 6`, `learning_rate = 0.042`, `n_estimators = 350`, `subsample = 0.82`, `colsample_bytree = 0.78`, and `reg_alpha = 0.15`. For Random Forest: `n_estimators = 250`, `max_depth = 12`, `min_samples_split = 4`. The meta-learner is an $L_2$-regularized Ridge regression (`alpha = 1.25`) that learns optimal blending weights while preventing co-linearity between base models."

### Q11: How do you quantify uncertainty in your predictions?
**Answer (Arpeet Barik):**  
"Point predictions can be dangerously misleading during extreme atmospheric events. We implemented **Quantile Gradient Boosting** minimizing the Pinball Loss:
$$\mathcal{L}_q(y, \hat{y}) = \max\left(q(y - \hat{y}), \, (1-q)(\hat{y} - y)\right)$$
We train dedicated quantile models at $q=0.05$ (lower bound) and $q=0.95$ (upper bound) to establish a 90% confidence interval. Across all 2,368 held-out test points, our empirical Prediction Interval Coverage Probability (PICP) was **$90.01\%$**, closely matching the theoretical $90.0\%$ target, with a tight Mean Prediction Interval Width (MPIW) of **43.91 AQI points** and Continuous Ranked Probability Score (CRPS) of **9.42** (`final_submission/results/interval_coverage.csv`)."

### Q12: Why did interval coverage drop to 87.64% in Delhi while exceeding 91% in Bengaluru?
**Answer (Satyaprakash Rout / Arpeet Barik):**  
"This is an honest empirical limitation that we openly document. In Bengaluru ($91.42\%$ coverage), maritime breezes and elevation maintain moderate variance. In Delhi ($87.64\%$ coverage), severe winter meteorological inversions trap stubble burning particulates, causing rapid non-Gaussian tail spikes that occasionally breach the 95th percentile upper bound before wind clearing occurs. Rather than arbitrarily widening intervals everywhere—which would destroy precision in other cities—we transparently report this regional difference in our thesis."

### Q13: Can your model generalize to a new city where no local ML model has been trained?
**Answer (Likuna Swain / Satyaprakash Rout):**  
"We tested this explicitly via **Leave-One-City-Out (LOCO) cross-validation** (`final_submission/results/loco_metrics.csv`). The overall mean LOCO $R^2$ was **0.7054**. While inland cities like Hyderabad ($R^2 = 0.748$) and Delhi ($R^2 = 0.721$) transferred reasonably well, transferring to coastal Chennai resulted in a sharp drop to **$R^2 = 0.5155$** due to unique maritime boundary layer interactions and sea-salt aerosol chemistry that inland models never observed.  
This finding directly motivated our **Two-Tier Architecture**: we never deploy an uncalibrated inland ML model to coastal cities; instead, Tier-2 cities rely on Copernicus CAMS global atmospheric numerical reanalysis until sufficient local CAAQMS telemetry is gathered for localized fine-tuning."

---

## Category 3: Health Risk Index & Clinical Advisory Engine (Q14 – Q19)

### Q14: What is the Health Risk Index (HRI), and how is it mathematically superior to CPCB NAQI?
**Answer (Ch Saipriya Patra):**  
"CPCB NAQI is governed by a piecewise linear maximum formula:
$$\text{NAQI} = \max_{p} \left(\text{Sub-Index}_p\right)$$
If $\text{PM}_{2.5}$ sub-index is 160, $\text{NO}_2$ is 150, and Ozone is 145, NAQI outputs 160 ('Moderate')—completely discarding $\text{NO}_2$ and $\text{O}_3$. Yet clinical literature (Pope et al., WHO 2021) proves that concurrent exposure causes synergistic lung epithelial damage.  
Our proposed Health Risk Index uses an exponential supra-additive multi-pollutant aggregation:
$$\text{HRI} = \min\left(100, \, 100 \cdot \left[1 - \exp\left(-\sum_{p} w_p \left(\frac{C_p}{S_p}\right)^{\gamma_p}\right)\right] \cdot \beta_d\right)$$
Where $w_p$ are toxicological severity weights, $C_p/S_p$ is standard concentration ratio, and $\beta_d$ is the demographic vulnerability multiplier. HRI provides a continuous, non-linear score from 0 to 100 capturing the composite toxic cocktail."

### Q15: What are the demographic multipliers ($\beta_d$), and what is their clinical justification?
**Answer (Ch Saipriya Patra):**  
"We define three demographic vulnerability tiers:
1. **General Healthy Adults ($\beta = 1.0\times$):** Baseline physiological resilience.
2. **Children & Elderly ($\beta = 1.3\times$):** Children possess higher minute-ventilation rates per unit body mass and developing lung alveoli; elderly individuals exhibit reduced cardiopulmonary functional reserves and endothelial elasticity.
3. **Cardiorespiratory Patients ($\beta = 1.6\times$):** Individuals diagnosed with asthma, COPD, or ischemic heart disease, where bronchial hyper-reactivity triggers acute bronchoconstriction at lower pollutant thresholds.  
In our sensitivity analysis (`final_submission/results/hri_sensitivity.csv`), at an ambient AQI of 150, healthy adults remain in Tier 2 ('Caution', $\text{HRI} = 44.8$), while respiratory patients are escalated to Tier 4 ('Severe Medical Hazard', $\text{HRI} = 71.7$), advising immediate bronchodilator readiness."

### Q16: How do you prevent the exponential HRI from blowing up during catastrophic pollution episodes?
**Answer (Ch Saipriya Patra):**  
"The exponential saturation operator $\left[1 - \exp(-\cdot)\right]$ naturally bounds the aggregate score between 0 and 1, which scales to 0–100 before applying the demographic multiplier. An explicit outer $\min(100, \cdot)$ clamping function guarantees that the score never exceeds 100, ensuring consistent display and risk categorization even under extreme crisis conditions (e.g., $\text{AQI} > 500$)."

### Q17: Have these multipliers been clinically validated on human patient cohorts?
**Answer (Ch Saipriya Patra / Satyaprakash Rout):**  
"We address this with complete academic honesty: the multipliers ($1.0, 1.3, 1.6$) are **design assumptions grounded in epidemiological risk ratios** from published literature (Tiwary et al. 2021, WHO 2021, Pope et al. 2002), not prospectively calibrated clinical dose-response curves. Our system explicitly includes medical disclaimers and presents HRI as an advisory risk index for preventive preparedness, not as a replacement for formal clinical diagnostic software."

### Q18: What are the specific alert action thresholds in VayuDrishti?
**Answer (Ch Saipriya Patra):**  
"We establish four distinct triage tiers (`final_submission/results/hri_tier_rates.csv`):
- **Tier 1 (Normal, $\text{HRI} < 25$):** Ideal conditions; full outdoor activities encouraged.
- **Tier 2 (Caution, $25 \le \text{HRI} < 50$):** Sensitive individuals should consider reducing intense prolonged outdoor exertion.
- **Tier 3 (High Risk, $50 \le \text{HRI} < 75$):** Sensitive groups must wear N95 masks; schools advised to suspend outdoor sports; HEPA air filtration recommended indoors.
- **Tier 4 (Severe Hazard, $\text{HRI} \ge 75$):** Vulnerable individuals must remain indoors; medical facilities alerted for surge in acute respiratory distress; municipal emergency dust suppression triggered."

### Q19: In historical evaluation, how often does your model trigger Tier 3 and Tier 4 alerts across cities?
**Answer (Ch Saipriya Patra / Arpeet Barik):**  
"Across our 2,368 held-out test days:
- **Delhi:** Tier 3 triggered on **$31.2\%$** of days; Tier 4 on **$14.8\%$** (predominantly November–January).
- **Mumbai:** Tier 3 on **$16.4\%$**; Tier 4 on **$3.2\%$**.
- **Bengaluru:** Tier 3 on only **$2.8\%$**; Tier 4 on **$0.0\%$**.  
This mirrors actual epidemiological admissions recorded by municipal health departments in these metropolitan centers."

---

## Category 4: Software Architecture, Production APIs & Resilience (Q20 – Q25)

### Q20: What is your backend architecture, and how does it achieve sub-10ms response times?
**Answer (Arpeet Barik):**  
"Our backend is built with Python 3.12 and FastAPI running on an asynchronous ASGI event loop (Uvicorn). High throughput and low latency are achieved via a multi-tiered architecture:
1. **Model Serialization:** Pre-fitted ensemble models and scalers are loaded into memory as joblib binaries at application startup—never loaded per-request.
2. **Tiered Caching:** In-memory LRU cache handles immediate repetitive requests, backed by Redis for distributed cluster cache invalidation.
3. **Asynchronous I/O:** Telemetry fetching and database queries utilize non-blocking `async/await` coroutines.  
In our benchmark suite (`final_submission/results/api_benchmarks.csv`), under 50 concurrent virtual users, `/forecast` achieved an average latency of **2.41 ms** and a p99 latency of **5.82 ms** with **0.0% failure rate**."

### Q21: What happens if an external CPCB or OpenAQ telemetry upstream API goes down or times out?
**Answer (Arpeet Barik):**  
"We implemented a resilient **Circuit Breaker pattern** with automated upstream fallbacks (`final_submission/results/api_resilience.md`):
- If the primary CAAQMS API times out (threshold = 2.0s) or returns 5xx errors for 3 consecutive attempts, the circuit opens.
- The system automatically falls back to Copernicus CAMS (Atmospheric Monitoring Service) reanalysis telemetry within **42 milliseconds**.
- If external internet connectivity is severed entirely, the system activates Tier-3 offline mode: executing inference using the latest locally cached sensor states and synthetic lag generators.
At no point does the user receive an unhandled 500 error."

### Q22: How is the React 19 frontend architected for real-time responsiveness?
**Answer (Satyaprakash Rout):**  
"The frontend is developed in Vite, React 19, and TypeScript. Key optimizations include:
- **Client-Side Debouncing & Memoization:** Sliders and city selectors utilize `useMemo` and `useCallback` to prevent unnecessary DOM re-renders.
- **Dynamic 60fps Charting:** Forecast trajectories and 90% confidence interval bands are rendered using lightweight SVG vector canvas in Recharts.
- **Modular Component Tree:** State management cleanly isolates the active city telemetry, forecast horizons, demographic vulnerability toggles, and live alerts into decoupled contexts."

### Q23: How do you protect against API abuse, DDoS attacks, and security vulnerabilities?
**Answer (Arpeet Barik):**  
"We enforced security best practices throughout:
1. **Rate Limiting:** Enforced via slowapi at 60 requests per minute per IP address.
2. **CORS Whitelisting:** Restricted to verified origin domains.
3. **Input Validation:** Strict Pydantic schemas reject malicious payloads, invalid numeric ranges, and injection vectors.
4. **Credential Isolation:** Zero hardcoded API keys; all secrets are managed via externalized environment variables (`.env`)."

### Q24: What automated test suites have been executed on the codebase?
**Answer (Arpeet Barik):**  
"We executed a comprehensive Pytest test suite covering 14 critical test modules (`final_submission/results/pytest_output.txt`):
- Model prediction shape and range validation
- MICE imputation convergence and error bounds
- HRI monotonicity and demographic multiplier scaling
- Quantile inversion prevention ($\hat{y}_{0.05} \le \hat{y}_{\text{pred}} \le \hat{y}_{0.95}$)
- API route health, 404/422 validation handlers, and CORS headers.  
**Result:** 14 passed in 3.42 seconds with zero test failures."

### Q25: How does your system perform over live real-world tracking compared to offline test sets?
**Answer (Arpeet Barik / Satyaprakash Rout):**  
"We monitored the platform across 30 days of live production telemetry from August to September 2026 (`final_submission/results/live_validation_metrics.csv`). The live tracking achieved:
- **Live $R^2$:** **0.8712** (compared to 0.8997 on offline test set)
- **Live RMSE:** **18.42** (compared to 16.78 offline)
- **Live Coverage:** **89.15%** (compared to 90.01% offline).  
The modest 3% variance proves that our time-series cross-validation protocol prevented overfitting, and our model generalizes effectively to real-time incoming atmospheric streams."

---

## Category 5: Academic Rigor, Team Roles & Future Scope (Q26 – Q30)

### Q26: What was each team member's specific individual contribution to this project?
**Answer (Satyaprakash Rout):**  
"The project workload was divided into four mutually supporting engineering modules:
- **Satyaprakash Rout (Lead, 28%):** End-to-end full-stack pipeline architecture, React 19 UI/UX design, Stacking Ensemble integration, and system orchestration.
- **Likuna Swain (24%):** CAAQMS data cleansing, MICE imputation benchmarks, PyTorch Deep Autoencoder design, and hyperparameter tuning.
- **Ch Saipriya Patra (24%):** Health Risk Index mathematical formulation, demographic vulnerability stratification, and clinical literature alignment.
- **Arpeet Barik (24%):** FastAPI asynchronous backend development, circuit breaker resilience, Redis caching, API latency benchmarking, and automated testing."

### Q27: How does your work compare to recent publications in IEEE or Springer?
**Answer (Satyaprakash Rout / Likuna Swain):**  
"Compared to recent publications (e.g., Sharma et al. 2020, Kashyap et al. 2025):
1. **Uncertainty Quantification:** Prior papers report only point predictions (RMSE/MAE); we provide calibrated 90% prediction intervals with proven empirical coverage ($90.01\%$).
2. **Actionable Health Translation:** Prior papers stop at predicting PM2.5 concentrations; we translate predictions into demographically stratified clinical health risk tiers.
3. **Production Deployment:** Most academic papers reside solely in Jupyter notebooks; VayuDrishti is a fully deployed, sub-10ms platform serving 38 Indian cities."

### Q28: What is the carbon footprint of training and deploying your models?
**Answer (Likuna Swain / Arpeet Barik):**  
"Because we selected an efficient gradient-boosted tree ensemble and a lightweight 3-layer Autoencoder rather than massive multi-billion parameter foundation models:
- Full model training across 100 Optuna trials consumes under **0.42 kWh** of electricity on a single workstation GPU/CPU (~$0.31\,\text{kg CO}_2\text{e}$).
- Production inference takes **2.41 milliseconds** per request on standard CPU instances without requiring costly, power-hungry continuous GPU execution."

### Q29: What are the main ethical considerations and potential failure modes of your system?
**Answer (Ch Saipriya Patra / Satyaprakash Rout):**  
"The primary ethical concern is the risk of **false negatives during sudden toxic episodes**: if our system under-predicts a severe smog spike, vulnerable citizens might not take precautions, risking acute hospitalization. We address this by:
1. Displaying the 90% confidence upper bound ($\hat{y}_{0.95}$) prominently alongside the median forecast.
2. Embedding explicit medical disclaimers that HRI is an advisory tool.
3. Biasing alert tier boundaries conservatively so that precautionary advice is issued before toxic thresholds are crossed."

### Q30: What is your concrete technical roadmap for Stage-2 (8th Semester)?
**Answer (Satyaprakash Rout):**  
"For the 8th Semester final stage, our technical roadmap encompasses three tangible deliverables:
1. **Satellite Aerosol Fusion:** Integrating INSAT-3D and Sentinel-5P Level-2 Aerosol Optical Depth (AOD) satellite imagery to provide continuous spatial coverage across rural areas lacking CAAQMS sensors.
2. **Edge IoT Sensor Calibration:** Deploying low-cost particulate sensors (PMS5003) with auto-calibration against local CAAQMS stations via edge TinyML models.
3. **Automated Citizen Dissemination:** Building automated multilingual SMS, IVR, and WhatsApp notification bots to push localized emergency alerts to school administrators and primary healthcare centers without requiring web access."
