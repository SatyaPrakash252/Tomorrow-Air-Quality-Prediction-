# VayuDrishti: Comprehensive Technical Reference Manual
## Complete Guide to AI, Machine Learning, Deep Learning, and Statistical Terms

**Project Title:** AI-Driven Air Quality Forecasting and Public Health Risk Alert System for Indian Metropolitan Cities  
**Platform Name:** VayuDrishti (वायुदृष्टि)  
**Academic Milestone:** 7th Semester Major Project Final Evaluation (Stage-1)  
**Institution:** Department of Computer Science & Engineering, C.V. Raman Global University (CGU), Bhubaneswar, Odisha  
**Team Members:** Satyaprakash Rout (2301020206), Likuna Swain (2301020252), Ch Saipriya Patra (2301020205), Arpeet Barik (2301020228)  
**Supervisor:** Prof. Soumya Sahoo, Assistant Professor, Dept. of CSE  

---

## Table of Contents
1. [Executive Architecture Map](#1-executive-architecture-map)
2. [Pillar 1: Data Preprocessing, Imputation & Leakage Prevention](#2-pillar-1-data-preprocessing-imputation--leakage-prevention)
3. [Pillar 2: Feature Engineering & Atmospheric Dynamics](#3-pillar-2-feature-engineering--atmospheric-dynamics)
4. [Pillar 3: Deep Representation Learning (Autoencoders)](#4-pillar-3-deep-representation-learning-autoencoders)
5. [Pillar 4: Supervised Learning & Ensemble Architectures](#5-pillar-4-supervised-learning--ensemble-architectures)
6. [Pillar 5: Hyperparameter Optimization & Search Mechanics](#6-pillar-5-hyperparameter-optimization--search-mechanics)
7. [Pillar 6: Uncertainty Quantification & Probabilistic Calibration](#7-pillar-6-uncertainty-quantification--probabilistic-calibration)
8. [Pillar 7: Model Interpretability & Explainable AI (XAI)](#8-pillar-7-model-interpretability--explainable-ai-xai)
9. [Pillar 8: Model Validation & Cross-Regional Transferability](#9-pillar-8-model-validation--cross-regional-transferability)
10. [Pillar 9: Epidemiological Risk Modeling & Health Informatics](#10-pillar-9-epidemiological-risk-modeling--health-informatics)
11. [Pillar 10: Production Architecture & Systems Resilience](#11-pillar-10-production-architecture--systems-resilience)
12. [Master AI/ML Terms Quick-Reference Matrix](#12-master-aiml-terms-quick-reference-matrix)
13. [Panel Examination & Viva Defense Q&A Cheat Sheet](#13-panel-examination--viva-defense-qa-cheat-sheet)

---

## 1. Executive Architecture Map

VayuDrishti combines physical atmospheric modeling with data-driven artificial intelligence. The end-to-end mathematical data pipeline flows through six distinct machine learning stages:

```
[Raw CAAQMS Telemetry + ERA5 Reanalysis]
                 │
                 ▼
  [Stage 1: Multi-Modal Imputation (MICE / KNN / SVD)]
                 │
                 ▼
  [Stage 2: 36-D Autoencoder Latent Compression (MI-MMA)]
                 │
                 ▼
  [Stage 3: 81-D Feature Vector Assembly (Lags + Weather + Events)]
                 │
                 ▼
  [Stage 4: Optuna-Tuned Dual Stacking Ensemble (RF + XGBoost + Ridge)]
                 │
                 ├──────────────────────────────┐
                 ▼                              ▼
  [Stage 5: Pinball Quantile Regressors]   [Stage 6: TreeSHAP Attribution]
        (90% Prediction Intervals)            (Global/Local Explanations)
                 │                              │
                 └──────────────┬───────────────┘
                                ▼
         [Stage 7: Demographic Epidemiological HRI Engine]
              (V_g Multipliers & 4-Tier Clinical Triage)
```

---

## 2. Pillar 1: Data Preprocessing, Imputation & Leakage Prevention

### 2.1 Multivariate Imputation by Chained Equations (MICE) / Fully Conditional Specification (FCS)
- **Why is it used?**  
  Ambient telemetry from Central Pollution Control Board (CPCB) continuous monitoring stations (CAAQMS) suffers from frequent sensor dropouts, calibration lapses, and power outages (missingness averages 8.4% and reaches 18.4% during peak episodes). Simple mean/median imputation destroys natural variance and cross-pollutant covariance. Standard single-pass regression underestimates standard errors. MICE treats missingness as a series of univariate conditional distributions, preserving the complex joint probability distribution across all criteria pollutants.
- **Where is it used?**  
  - Codebase: `final_submission/scripts/generate_ground_truth.py` (`impute_mice()` function), `backend/ml/data_loader.py`.
  - Thesis: Chapter 3, Section 3.4; Table 3.2; Algorithm 3.1.
  - Results: `final_submission/results/imputation_metrics.csv`.
- **How is it used?**  
  MICE models each pollutant $Y_j$ with missing values as a function of all other pollutants $Y_{-j}$ using Bayesian Ridge regression:
  $$Y_j^{(t)} \sim \mathcal{N}\left(X_{-j} \hat{\beta}_j + \epsilon,\, \sigma_j^2\right)$$
  Executed across $T=10$ imputation cycles. Under a seeded 7% synthetic masking benchmark (5,057 values), MICE achieved an overall Mean RMSE of **0.0061**, outperforming KNN (0.6975) by **75.6%** and SVD (40.1903).

---

### 2.2 K-Nearest Neighbors (KNN) Imputation
- **Why is it used?**  
  Used as a non-parametric, distance-based local imputation benchmark and as the first branch of the Multi-Imputation Multi-Modal Autoencoder (MI-MMA). It exploits geometric similarity in local pollutant-meteorological state spaces.
- **Where is it used?**  
  - Codebase: `final_submission/scripts/generate_ground_truth.py`, `backend/ml/data_loader.py`.
  - Thesis: Chapter 3, Section 3.3.
- **How is it used?**  
  For each missing observation $x_i$, the $k=5$ nearest complete samples are identified in normalized Euclidean space:
  $$\hat{x}_{ij} = \sum_{m \in \mathcal{N}_k(i)} \frac{w_m}{\sum w} x_{mj}, \quad w_m = \frac{1}{d(x_i, x_m)}$$
  In our benchmark, KNN yielded an RMSE of 0.6975. Its output feeds Branch 1 of the MI-MMA autoencoder.

---

### 2.3 Truncated Singular Value Decomposition (SVD) Imputation
- **Why is it used?**  
  Employed as a global linear algebraic low-rank matrix approximation benchmark and the third branch of the MI-MMA pipeline. It captures dominant spectral energy modes across the multi-station sensor matrix.
- **Where is it used?**  
  - Codebase: `final_submission/scripts/generate_ground_truth.py`.
  - Thesis: Chapter 3, Section 3.3; Table 3.2.
- **How is it used?**  
  The data matrix $X \in \mathbb{R}^{N \times P}$ is factorized into singular vectors:
  $$X_r = U_r \Sigma_r V_r^T, \quad \text{rank } r = 4$$
  Missing cells are iteratively updated until reconstruction convergence ($\epsilon < 10^{-4}$). In benchmarks, SVD produced RMSE = 40.1903 due to its sensitivity to extreme episodic spikes, confirming why non-linear autoencoder fusion is necessary.

---

### 2.4 Missing at Random (MAR) Assumption
- **Why is it used?**  
  To formally validate the statistical validity of MICE and autoencoder imputation. Under Missing Completely at Random (MCAR), dropouts are completely independent of values; under Missing Not at Random (MNAR), missingness depends on the unobserved value itself (e.g., sensor saturation). Analysis of CAAQMS logs revealed dropouts correlate with power failures and maintenance intervals (observed auxiliary variables), confirming the MAR condition.
- **Where is it used?**  
  - Thesis: Chapter 3, Section 3.4.1.
- **How is it used?**  
  Little's MCAR test was executed, yielding $p < 0.001$, rejecting MCAR and validating the Fully Conditional Specification (FCS) framework of MICE:
  $$P(M \mid Y_{\text{obs}}, Y_{\text{mis}}) = P(M \mid Y_{\text{obs}})$$

---

### 2.5 Chronological Time-Series Train/Test Split (Zero Future Leakage)
- **Why is it used?**  
  Standard random $k$-fold cross-validation is **invalid** for time series because randomly shuffling records allows future samples to train models that predict past events ("lookahead bias" or "data leakage"). This artificially inflates $R^2$ to unrealistic numbers ($>0.98$) that collapse in production.
- **Where is it used?**  
  - Codebase: `final_submission/scripts/generate_ground_truth.py`, `backend/ml/train.py`.
  - Thesis: Chapter 3, Section 3.2.3; Chapter 4, Section 4.1.
  - Audit File: `final_submission/results/leakage_audit.md`.
- **How is it used?**  
  A strict 80/20 chronological split was enforced independently across each city's time series:
  - **Training Partition:** 2018-01-01 to mid-2023 (9,609 records; exactly 80.0%).
  - **Held-Out Test Partition:** mid-2023 to 2024-12-31 (2,403 records; exactly 20.0%).
  All scalers (StandardScaler, MinMaxScaler) and imputation parameters were fit **strictly on the training partition** and only applied (via `.transform()`) to the test partition.

---

### 2.6 Interquartile Range (IQR) Outlier Clamping
- **Why is it used?**  
  Environmental sensors occasionally generate non-physical spikes due to electrical surges or insect intrusion. Truncating extreme values using Gaussian $\pm 3\sigma$ fails because pollution distributions are highly right-skewed (log-normal). IQR clamping removes non-physical artifacts while preserving true episodic pollution surges (such as Diwali firecracker spikes).
- **Where is it used?**  
  - Codebase: `backend/ml/data_loader.py`.
  - Thesis: Chapter 3, Section 3.2.2.
- **How is it used?**  
  For each pollutant, upper and lower fence thresholds are calculated:
  $$Q_1 = P_{25}, \quad Q_3 = P_{75}, \quad \text{IQR} = Q_3 - Q_1$$
  $$\text{Upper Fence} = Q_3 + 3.0 \times \text{IQR}, \quad \text{Lower Fence} = \max(0,\, Q_1 - 3.0 \times \text{IQR})$$
  Values exceeding the fence are clamped to the boundary rather than deleted, maintaining unbroken temporal continuity.

---

## 3. Pillar 2: Feature Engineering & Atmospheric Dynamics

### 3.1 Autoregressive Lag Features ($t-1, t-2, t-3$)
- **Why is it used?**  
  Ambient air pollution exhibits high temporal autocorrelation (atmospheric inertia). What happened yesterday ($t-1$) and two days prior ($t-2$) strongly dictates baseline particulate concentrations.
- **Where is it used?**  
  - Codebase: `backend/ml/data_loader.py` (`build_features()` function).
  - Thesis: Chapter 3, Section 3.6; Table 3.4.
- **How is it used?**  
  For each pollutant $p \in \{\text{PM}_{2.5}, \text{PM}_{10}, \text{NO}_2, \text{SO}_2, \text{CO}, \text{O}_3\}$ and target $\text{AQI}$:
  $$X_{\text{lag}, k} = y_{t-k}, \quad k \in \{1, 2, 3\}$$
  This adds 21 autoregressive lag features. SHAP analysis confirms same-day $\text{AQI}_t$ and $\text{AQI}_{t-3}$ rank among the top 5 most important features.

---

### 3.2 Rolling Temporal Window Statistics (7-Day & 14-Day Means & Stds)
- **Why is it used?**  
  Captures mid-term synoptic trends and weather regimes (e.g., prolonged winter stagnation vs. active monsoon washout) while damping high-frequency daily sensor jitter.
- **Where is it used?**  
  - Codebase: `backend/ml/data_loader.py`.
  - Thesis: Chapter 3, Section 3.6.
- **How is it used?**  
  Computed strictly backwards (closed on left, open on right to prevent leakage):
  $$\mu_{7, t} = \frac{1}{7} \sum_{i=1}^7 y_{t-i}, \quad \sigma_{7, t} = \sqrt{\frac{1}{6} \sum_{i=1}^7 (y_{t-i} - \mu_{7, t})^2}$$
  Computed across 7-day and 14-day horizons for $\text{PM}_{2.5}$, $\text{PM}_{10}$, and overall $\text{AQI}$.

---

### 3.3 Planetary Boundary Layer Height (PBLH / BLH)
- **Why is it used?**  
  PBLH represents the vertical depth of the troposphere where surface emissions mix. In Indian winters, thermal radiation inversions cause PBLH to collapse from 2,000 meters (summer afternoon) to below 150 meters (winter midnight). This physically traps pollutants in a shallow surface layer, triggering severe smog crises regardless of emission rate changes.
- **Where is it used?**  
  - Codebase: ERA5 weather ingestion in `final_submission/scripts/generate_ground_truth.py`.
  - Thesis: Chapter 1, Section 1.3; Chapter 3, Section 3.2.1.
- **How is it used?**  
  Extracted from European Centre for Medium-Range Weather Forecasts (ECMWF) ERA5 reanalysis at 0.25° gridded resolution. Ingested as instantaneous values and lagged inputs ($t-1$).

---

### 3.4 Ventilation Index (VI)
- **Why is it used?**  
  Neither wind speed nor boundary layer height alone governs dispersion; their product dictates the total volumetric rate at which pollutants are swept downwind. A low Ventilation Index ($< 2,000 \text{ m}^2/\text{s}$) indicates stagnant dispersal conditions and imminent AQI surges.
- **Where is it used?**  
  - Codebase: `backend/ml/data_loader.py`.
  - Thesis: Chapter 3, Section 3.6; Equation (3.12).
- **How is it used?**  
  Formulated as:
  $$\text{VI}_t = \text{PBLH}_t \times U_{10, t} \quad \left[\text{m}^2/\text{s}\right]$$
  where $U_{10}$ is horizontal wind speed at 10m height. Added as a composite feature in the 81-dimensional vector.

---

### 3.5 India-Specific Episodic Shock Indicators
- **Why is it used?**  
  Standard Western ML forecasting models fail in India because they do not account for massive, culturally specific non-stationary emission pulses:
  1. **Diwali Festive Window:** Unregulated firecracker discharges cause multi-pollutant spikes of 400–800 AQI points within 6 hours.
  2. **Stubble Burning Season:** Post-monsoon agricultural crop residue burning in Punjab and Haryana transports thick smoke plumes across the Indo-Gangetic Plain.
- **Where is it used?**  
  - Codebase: `backend/ml/data_loader.py`.
  - Thesis: Chapter 3, Section 3.6; Chapter 4, Section 4.8.
- **How is it used?**  
  - **Diwali Indicator:** Binary indicator $\mathbb{I}_{\text{Diwali}} \in \{0, 1\}$ active during the $\pm 2$ day window around the lunar calendar Diwali date.
  - **Stubble Season Indicator:** Gaussian decayed seasonal bell function peaking between October 15 and November 25:
    $$f_{\text{stubble}}(t) = \exp\left( - \frac{(d_t - d_{\text{peak}})^2}{2 \sigma_{\text{season}}^2} \right)$$
  Ablation studies show adding these indicators improved test RMSE from 17.04 to 16.97.

---

### 3.6 Cyclic Sine/Cosine Calendar Encodings
- **Why is it used?**  
  Ordinal integers (e.g., month $1 \dots 12$, day-of-week $0 \dots 6$) introduce false numerical discontinuities: December (12) and January (1) are numerically distant (difference of 11) despite being temporally adjacent.
- **Where is it used?**  
  - Codebase: `backend/ml/data_loader.py`.
  - Thesis: Chapter 3, Section 3.6.
- **How is it used?**  
  Mapped onto unit circular coordinates:
  $$x_{\sin} = \sin\left(\frac{2\pi \cdot t}{T}\right), \quad x_{\cos} = \cos\left(\frac{2\pi \cdot t}{T}\right)$$
  for $T=365.25$ (day of year) and $T=7$ (day of week).

---

## 4. Pillar 3: Deep Representation Learning (Autoencoders)

### 4.1 Multi-Imputation Multi-Modal Autoencoder (MI-MMA)
- **Why is it used?**  
  Six criteria pollutants exhibit strong non-linear collinearity (e.g., photochemical ozone formation consumes $\text{NO}_x$ under UV radiation; $\text{SO}_2$ oxidizes into sulfate aerosols). Feeding raw imputed variables directly into tree ensembles leads to suboptimal splits. The MI-MMA network compresses the output of all three imputation pathways (KNN, MICE, SVD) into a non-linear latent bottleneck representation.
- **Where is it used?**  
  - Codebase: `final_submission/scripts/generate_ground_truth.py` (`Autoencoder` class), `backend/ml/autoencoder.py`.
  - Thesis: Chapter 3, Section 3.5; Figure 3.3; Table 3.3.
- **How is it used?**  
  Three identical, parallel PyTorch autoencoders are trained on the KNN, MICE, and SVD imputed streams. Each network extracts a 12-dimensional bottleneck vector. The vectors are concatenated into a 36-dimensional multimodal embedding:
  $$\mathbf{Z}_{\text{MMA}} = \left[ \mathbf{z}_{\text{KNN}} \,\|\, \mathbf{z}_{\text{MICE}} \,\|\, \mathbf{z}_{\text{SVD}} \right] \in \mathbb{R}^{36}$$

---

### 4.2 Symmetrical Dense Bottleneck Neural Architecture
- **Why is it used?**  
  Forces the neural network to learn an efficient, lossy compression that eliminates high-frequency measurement noise while retaining low-dimensional manifolds.
- **Where is it used?**  
  - Codebase: PyTorch module in `generate_ground_truth.py`.
  - Thesis: Chapter 3, Section 3.5.1; Figure 3.3.
- **How is it used?**  
  - **Input Layer:** 7 dimensions (6 normalized criteria pollutants + raw AQI).
  - **Encoder:** Dense($7 \to 32$, ReLU) $\to$ Dense($32 \to 12$, ReLU).
  - **Latent Bottleneck:** $\mathbf{z} \in \mathbb{R}^{12}$.
  - **Decoder:** Dense($12 \to 32$, ReLU) $\to$ Dense($32 \to 7$, Linear).
  - **Optimizer:** Adam (learning rate $= 10^{-3}$, weight decay $= 10^{-5}$, 100 epochs, batch size $= 64$).

---

### 4.3 Reconstruction Mean Squared Error (MSE Loss)
- **Why is it used?**  
  Serves as the unsupervised objective function to ensure that the latent vector $\mathbf{z}$ preserves maximum information for reconstructing the original pollutant profile.
- **Where is it used?**  
  - Codebase: Training loop in `generate_ground_truth.py`.
  - Thesis: Chapter 3, Section 3.5.2; Equation (3.7).
- **How is it used?**  
  $$\mathcal{L}_{\text{recon}}(\theta, \phi) = \frac{1}{N} \sum_{i=1}^N \sum_{j=1}^7 \left( x_{ij} - g_\phi(f_\theta(x_i))_j \right)^2$$
  Trained autoencoders achieved near-zero reconstruction loss:
  - $\text{KNN\_AE MSE} = 4.0 \times 10^{-6}$
  - $\text{MICE\_AE MSE} = 1.0 \times 10^{-5}$
  - $\text{SVD\_AE MSE} = 1.6 \times 10^{-5}$

---

## 5. Pillar 4: Supervised Learning & Ensemble Architectures

### 5.1 Random Forest Regressor (Bagging / Bootstrap Aggregation)
- **Why is it used?**  
  Random Forest creates an ensemble of decorrelated decision trees, providing high resistance to overfitting, handling multicollinear features gracefully, and reducing predictive variance.
- **Where is it used?**  
  - Codebase: Base Forecaster 1 in `final_submission/scripts/generate_ground_truth.py` and `backend/ml/forecaster.py`.
  - Thesis: Chapter 3, Section 3.7.1; Chapter 4, Table 4.2.
- **How is it used?**  
  Trained with 200 estimators, max depth $= 12$, min samples split $= 5$, and bootstrap sampling with feature subset selection ($m = \sqrt{D}$). In standalone ablation, Random Forest achieved test $R^2 = 0.8904$ and $\text{RMSE} = 17.54$.

---

### 5.2 Extreme Gradient Boosting (XGBoost / GBDT)
- **Why is it used?**  
  Unlike Random Forest (which builds independent trees to reduce variance), XGBoost builds trees sequentially to minimize residual bias. It optimizes a second-order Taylor expansion of the loss function and incorporates explicit $L_1$ and $L_2$ leaf regularization, making it the strongest single model for tabular time series.
- **Where is it used?**  
  - Codebase: Base Forecaster 2 in `final_submission/scripts/generate_ground_truth.py` and `backend/ml/forecaster.py`.
  - Thesis: Chapter 3, Section 3.7.2; Chapter 4, Table 4.2.
- **How is it used?**  
  Trained with 300 estimators, learning rate $\eta = 0.03$, max depth $= 6$, subsample $= 0.8$, colsample_bytree $= 0.8$, and $\lambda = 1.0$. Standalone XGBoost achieved test $R^2 = 0.8931$ and $\text{RMSE} = 17.33$.

---

### 5.3 Stacked Generalization (Dual Stacking Ensemble)
- **Why is it used?**  
  Simple averaging ($0.5 \times \text{RF} + 0.5 \times \text{XGB}$) assumes both models perform equally well across all pollution regimes. Stacking uses a secondary **meta-learner** that learns optimal weighting dynamically: when Random Forest performs better (high-variance transition regimes) vs. when XGBoost performs better (sharp episodic peaks).
- **Where is it used?**  
  - Codebase: `final_submission/scripts/generate_ground_truth.py` (`StackingEnsemble` class) and `backend/ml/forecaster.py`.
  - Thesis: Chapter 3, Section 3.8; Algorithm 3.2; Figure 3.1.
- **How is it used?**  
  1. Base models (RF, XGBoost) generate out-of-fold predictions $\hat{y}_{\text{RF}}, \hat{y}_{\text{XGB}}$ on training folds.
  2. A Ridge meta-regressor ($\alpha = 1.0$) fits the final prediction:
     $$\hat{y}_{\text{stack}} = w_0 + w_1 \hat{y}_{\text{RF}} + w_2 \hat{y}_{\text{XGB}}$$
  3. **Baseline Stacking:** achieved test $R^2 = 0.9014$, $\text{RMSE} = 16.64$, and accuracy $= 87.02\%$.
  4. **Optuna Production Stacking:** achieved test **$R^2 = 0.9248$, $\text{RMSE} = 13.84$, $\text{MAE} = 9.12$, and $\text{Accuracy} = 91.42\%$**.

---

### 5.4 Long Short-Term Memory (LSTM) (Evaluated & Excluded Finding)
- **Why is it used & Why was it excluded?**  
  Deep recurrent LSTMs were evaluated to test whether recurrent hidden state gates ($\mathbf{h}_t, \mathbf{c}_t$) could outperform tree-based tabular models on continuous multi-day sequences.  
  **Empirical Finding:** Standalone LSTM performed poorly ($\text{RMSE} = 21.68$, $R^2 = 0.8312$, $\text{MAPE} = 17.77\%$). When forced into a Tri-Ensemble with RF and XGBoost, performance degraded from $\text{RMSE} = 16.64$ down to $18.55$ ($R^2$ dropped from $0.9014$ to $0.8782$). Recurrent backpropagation through time overfits tabular daily aggregates and lacks the orthogonal threshold splits needed for meteorological regimes.  
  **Honesty Disclosure:** Deep LSTM is openly documented in the thesis as **evaluated and rejected**, establishing scientific rigor.
- **Where is it used?**  
  - Codebase: `final_submission/scripts/generate_ground_truth.py` (`train_lstm()` function).
  - Thesis: Chapter 2, Section 2.4; Chapter 4, Section 4.3; Table 4.2; Chapter 5, Section 5.2.
- **How is it used?**  
  PyTorch 2-layer LSTM ($T=7$ lookback window, hidden size $= 64$, dropout $= 0.2$), trained with Adam optimizer over 50 epochs.

---

## 6. Pillar 5: Hyperparameter Optimization & Search Mechanics

### 6.1 Tree-structured Parzen Estimator (TPE) Bayesian Optimization
- **Why is it used?**  
  Manual tuning or brute-force Grid Search is computationally intractable across an 81-dimensional feature space with dozens of interacting hyperparameters. Standard Random Search is inefficient because it does not learn from past trials. TPE constructs a probabilistic model of the objective function, selecting candidate parameters that maximize Expected Improvement (EI).
- **Where is it used?**  
  - Codebase: `backend/ml/tune.py`, Optuna metadata in `final_metrics.json`.
  - Thesis: Chapter 3, Section 3.8.2; Appendix B.
- **How is it used?**  
  TPE splits trial parameter observations into two probability density functions:
  $$p(\theta \mid y) = \begin{cases} \ell(\theta) & \text{if } y < y^* \text{ (top 15\% best trials)} \\ g(\theta) & \text{if } y \ge y^* \text{ (remaining trials)} \end{cases}$$
  Candidates are sampled to maximize the ratio $\ell(\theta) / g(\theta)$. Executed across 100 trials, tuning learning rates, subsample ratios, maximum tree depths, regularizations, and meta-weights. This boosted model accuracy from **87.02% to 91.42%** and lowered RMSE from **16.64 to 13.84 AQI points**.

---

### 6.2 Early Stopping Strategy
- **Why is it used?**  
  Prevents over-optimizing gradient boosting trees on late-stage iterations where training loss continues decreasing while validation error begins rising.
- **Where is it used?**  
  - Codebase: XGBoost configuration in `backend/ml/forecaster.py`.
  - Thesis: Chapter 3, Section 3.7.2.
- **How is it used?**  
  Evaluation loss on out-of-fold validation sets is monitored. If validation RMSE fails to improve for 25 consecutive boosting rounds, training halts automatically and weights roll back to the optimal checkpoint.

---

## 7. Pillar 6: Uncertainty Quantification & Probabilistic Calibration

### 7.1 Quantile Regression & Asymmetric Pinball Loss ($\mathcal{L}_\tau$)
- **Why is it used?**  
  Point forecasts ($\hat{y} = 185$) provide no measure of risk or uncertainty. For public health decisions, underpredicting a hazardous smog spike is far more harmful than a minor overprediction. Quantile regression estimates specific conditional quantiles of the predictive distribution without assuming Gaussian errors.
- **Where is it used?**  
  - Codebase: `backend/ml/forecaster.py` (`QuantileForecaster` class).
  - Thesis: Chapter 3, Section 3.10; Figure 3.1; Table 4.6.
- **How is it used?**  
  Trained using the asymmetric piecewise linear Pinball Loss function:
  $$\mathcal{L}_\tau(y, \hat{y}) = \begin{cases} \tau (y - \hat{y}) & \text{if } y \ge \hat{y} \\ (1 - \tau)(\hat{y} - y) & \text{if } y < \hat{y} \end{cases}$$
  Two distinct gradient boosted models are fit at $\tau = 0.05$ (5th percentile lower bound $\hat{L}$) and $\tau = 0.95$ (95th percentile upper bound $\hat{U}$), forming a 90% prediction interval $[\hat{L}, \hat{U}]$.

---

### 7.2 Prediction Interval Coverage Probability (PICP)
- **Why is it used?**  
  Measures whether empirical observations fall within the predicted uncertainty bounds at the theoretical nominal level (90.0%).
- **Where is it used?**  
  - Codebase: `final_submission/scripts/generate_ground_truth.py`.
  - Thesis: Chapter 4, Section 4.7; Table 4.6; Figure 4.7.
  - Results: `final_submission/results/interval_coverage.csv`.
- **How is it used?**  
  $$\text{PICP} = \frac{1}{N} \sum_{i=1}^N \mathbb{I}\left( y_i \in [\hat{L}_i, \hat{U}_i] \right) \times 100\%$$
  Across all 2,403 held-out test days, VayuDrishti achieved **$\text{PICP} = 90.01\%$**, matching the nominal 90.0% target.

---

### 7.3 Mean Prediction Interval Width (MPIW)
- **Why is it used?**  
  A wide, trivial interval ($[-\infty, +\infty]$) achieves 100% coverage but offers zero practical utility. MPIW measures the sharpness and informativeness of the uncertainty bounds.
- **Where is it used?**  
  - Thesis: Chapter 4, Section 4.7.
- **How is it used?**  
  $$\text{MPIW} = \frac{1}{N} \sum_{i=1}^N \left( \hat{U}_i - \hat{L}_i \right)$$
  VayuDrishti achieved an average MPIW of **43.91 AQI points** (sharp interval bounds of $\pm 27.37$ AQI points pan-India).

---

## 8. Pillar 7: Model Interpretability & Explainable AI (XAI)

### 8.1 SHAP (SHapley Additive exPlanations)
- **Why is it used?**  
  Machine learning models are often criticized as "black boxes." In medical alert systems, clinicians and municipal authorities require transparent attribution: *why* did the system predict an AQI surge tomorrow? Grounded in cooperative game theory, SHAP provides the only local attribution method with proven mathematical properties of local accuracy, missingness, and consistency.
- **Where is it used?**  
  - Codebase: `final_submission/scripts/generate_ground_truth.py`, `backend/ml/explainer.py`.
  - Thesis: Chapter 3, Section 3.9; Chapter 4, Section 4.6; Table 4.5; Figure 4.6.
  - Results: `final_submission/results/shap_importance.csv`.
- **How is it used?**  
  Computes the marginal contribution of feature $i$ across all possible feature subsets $S \subseteq F \setminus \{i\}$:
  $$\phi_i = \sum_{S \subseteq F \setminus \{i\}} \frac{|S|! (|F| - |S| - 1)!}{|F|!} \left[ f(S \cup \{i\}) - f(S) \right]$$

---

### 8.2 TreeSHAP Algorithm
- **Why is it used?**  
  Calculating exact Shapley values across 81 features has exponential complexity $\mathcal{O}(2^{|F|})$ (intractable for production). TreeSHAP exploits decision tree structures to calculate exact Shapley values in polynomial time $\mathcal{O}(T \cdot L \cdot D^2)$ (sub-millisecond execution).
- **Where is it used?**  
  - Codebase: `backend/ml/explainer.py`.
  - Thesis: Chapter 3, Section 3.9.1.
- **How is it used?**  
  Replaces exponential feature dropping with conditional expectations tracked through tree branch weights. Global analysis revealed top predictive drivers:
  1. Same-Day AQI ($\text{SHAP} = 19.54$)
  2. Same-Day $\text{PM}_{2.5}$ concentration ($\text{SHAP} = 6.44$)
  3. Surface Relative Humidity ($\text{SHAP} = 3.67$)
  4. 10m Horizontal Wind Speed ($\text{SHAP} = 1.92$)
  5. 3-Day Lagged AQI ($\text{SHAP} = 1.69$)

---

## 9. Pillar 8: Model Validation & Cross-Regional Transferability

### 9.1 Leave-One-City-Out (LOCO) Cross-Validation
- **Why is it used?**  
  Tests whether a model trained on several cities can generalize "zero-shot" to a new, unseen city without retraining. It detects geographic overfitting and assesses cross-regional spatial transferability.
- **Where is it used?**  
  - Codebase: `final_submission/scripts/generate_ground_truth.py` (`evaluate_loco()` function).
  - Thesis: Chapter 3, Section 3.11; Chapter 4, Section 4.5; Table 4.4; Figure 4.5.
  - Results: `final_submission/results/loco_metrics.csv`.
- **How is it used?**  
  For each city $c \in \{1 \dots 5\}$:
  - Train on remaining 4 metropolitan centers.
  - Evaluate zero-shot on the held-out city $c$.
  - **Empirical Result:** Mean zero-shot $R^2$ dropped from $0.9014$ to **$0.7054$** ($\text{RMSE} = 20.77$).
  - **Critical Finding:** Coastal Chennai collapsed to $R^2 = 0.5155$ due to maritime boundary layer interactions and diurnal sea breeze cycles that inland models cannot extrapolate. This justified VayuDrishti's Two-Tier Architecture.

---

### 9.2 Inferential Hypothesis Testing (Parametric & Non-Parametric)
- **Why is it used?**  
  To formally prove that error reductions from the Stacking Ensemble over standalone XGBoost are statistically significant and not random chance.
- **Where is it used?**  
  - Codebase: `final_submission/scripts/generate_ground_truth.py`.
  - Thesis: Chapter 4, Section 4.4; Table 4.3.
  - Results: `final_submission/results/significance_tests.csv`.
- **How is it used?**  
  Evaluated on $N = 2,368$ aligned absolute test residuals:
  - **Paired Student's $t$-test (Parametric):**
    $$t = \frac{\bar{d}}{s_d / \sqrt{N}} = -3.722, \quad p = 0.000202 \quad (p < 0.05 \implies \text{Reject } H_0)$$
  - **Wilcoxon Signed-Rank Test (Non-Parametric):**
    $$W = 1,263,583.0, \quad p = 3.003 \times 10^{-5} \quad (p < 0.01 \implies \text{Reject } H_0)$$
  Both tests confirm superiority with $> 99.98\%$ statistical confidence.

---

### 9.3 Continuous Bounded Regression Accuracy ($1 - \text{MAPE}$)
- **Why is it used?**  
  In academic and industrial reporting, stakeholders require an accuracy percentage. However, AQI forecasting is a continuous regression problem, not discrete classification. Standard classification accuracy forces continuous values into arbitrary bins, masking real errors. Continuous accuracy evaluates exact numerical fidelity.
- **Where is it used?**  
  - Codebase: `final_metrics.json`, `FACTS.md`, all chapter ablation tables.
  - Thesis: Chapter 4, Section 4.3; Table 4.2.
- **How is it used?**  
  Defined as bounded continuous fidelity:
  $$\text{MAPE} = \frac{1}{N} \sum_{i=1}^N \left| \frac{y_i - \hat{y}_i}{y_i} \right| \times 100\% = 8.58\%$$
  $$\text{Accuracy} = \max\left(0,\, 100\% - \text{MAPE}\right) = 100\% - 8.58\% = \mathbf{91.42\%}$$

---

## 10. Pillar 9: Epidemiological Risk Modeling & Health Informatics

### 10.1 Epidemiological Health Risk Index (HRI) Formulation
- **Why is it used?**  
  The official Indian CPCB National Air Quality Index (NAQI) uses a "piecewise maximum operator":
  $$\text{AQI}_{\text{official}} = \max\left( I_{\text{PM2.5}},\, I_{\text{PM10}},\, I_{\text{NO2}},\, I_{\text{SO2}},\, I_{\text{CO}},\, I_{\text{O3}} \right)$$
  This formulation creates severe toxicological distortions:
  1. **Co-Exposure Ignorance:** If $\text{PM}_{2.5}$ AQI is 150 and $\text{NO}_2$ AQI is 149, the reported AQI is 150—completely ignoring the toxic chemical cocktail of breathing both simultaneously.
  2. **Uniform Vulnerability Fallacy:** It assumes a healthy 25-year-old athlete and an 8-year-old asthmatic child face identical physiological risk.
- **Where is it used?**  
  - Codebase: `backend/ml/hri_engine.py` (`calculate_hri()` function).
  - Thesis: Chapter 3, Section 3.11; Equations (3.14)–(3.18); Chapter 4, Section 4.8.
- **How is it used?**  
  Formulated as a supra-additive exponential risk model:
  $$\text{HRI}_g = V_g \times \sum_{p=1}^P w_p \left( \frac{C_p}{S_p} \right)^{\beta_p}$$
  where:
  - $C_p$: Forecasted concentration of pollutant $p$.
  - $S_p$: CPCB NAAQS statutory 24-hour limit ($\text{PM}_{2.5}: 60, \text{PM}_{10}: 100, \text{NO}_2: 80, \text{SO}_2: 80, \text{CO}: 2000, \text{O}_3: 100 \ \mu\text{g/m}^3$).
  - $w_p$: Toxicological weights summing to 1.0 ($\text{PM}_{2.5}: 0.35, \text{PM}_{10}: 0.20, \text{O}_3: 0.15, \text{NO}_2: 0.15, \text{SO}_2: 0.10, \text{CO}: 0.05$).
  - $\beta_p$: Epidemiological concentration-response curvature ($\beta=1.0$ linear baseline; $\beta=1.15$ supra-additive).
  - $V_g$: Demographic vulnerability multiplier.

---

### 10.2 Demographic Vulnerability Multipliers ($V_g$)
- **Why is it used?**  
  Clinical and epidemiological literature confirms children have higher minute-ventilation rates per kilogram of body weight, the elderly suffer reduced cardiovascular clearance, and respiratory patients exhibit hyper-reactive airway spasms.
- **Where is it used?**  
  - Codebase: `backend/ml/hri_engine.py`.
  - Thesis: Chapter 3, Section 3.11.2; Table 3.5.
- **How is it used?**  
  Stratified into three evidence-based tiers:
  - **General Public ($V_{\text{GP}} = 1.0\times$):** Baseline healthy adult population.
  - **Children & Elderly ($V_{\text{CE}} = 1.3\times$):** 30% risk escalation for pediatric and geriatric cohorts.
  - **Respiratory & Cardiac Patients ($V_{\text{RP}} = 1.6\times$):** 60% risk escalation for asthmatic and COPD cohorts.

---

### 10.3 Shared-Cutoff Percentile Threshold Principle
- **Why is it used?**  
  *Critical Mathematical Discovery:* If percentiles were calculated separately within each group, the vulnerability multiplier would cancel out mathematically:
  $$P_{75}^{(g)} = \text{Quantile}(V_g \cdot \text{HRI}_{\text{GP}},\, 0.75) = V_g \cdot P_{75}^{(\text{GP})}$$
  $$\text{Alert Check:} \quad \text{HRI}_g > P_{75}^{(g)} \iff V_g \cdot \text{HRI}_{\text{GP}} > V_g \cdot P_{75}^{(\text{GP})} \iff \text{HRI}_{\text{GP}} > P_{75}^{(\text{GP})}$$
  The multiplier $V_g$ cancels out completely, producing an identical 25% alert rate for all groups and destroying clinical differentiation.
- **Where is it used?**  
  - Codebase: `backend/ml/hri_engine.py`.
  - Thesis: Chapter 3, Section 3.11.3; Mathematical Proof in Section 3.11.3.
- **How is it used?**  
  A **single shared scale** derived from the General Public distribution is locked for all cohorts:
  - **Low Risk:** $\text{HRI} \le P_{25} \ (7.121)$
  - **Moderate Risk:** $P_{25} < \text{HRI} \le P_{75} \ (14.715)$
  - **High Risk (Alert Active):** $P_{75} < \text{HRI} \le P_{90} \ (23.855)$
  - **Severe Risk (Emergency Active):** $\text{HRI} > P_{90} \ (23.855)$
  This produces clinically differentiated alert activation rates (High + Severe):
  - General Public: **24.93%**
  - Children & Elderly: **39.91%**
  - Respiratory Patients: **55.72%**

---

### 10.4 Natural Language Generation (NLG) Clinical Advisory Engine
- **Why is it used?**  
  Raw numbers ($\text{AQI}=214, \text{HRI}=28.4$) do not tell a citizen or school administrator what medical actions to take. Automated NLG converts complex model state into actionable, clinical text advisories.
- **Where is it used?**  
  - Codebase: `backend/ml/hri_engine.py` (`generate_clinical_advisory()` function).
  - Thesis: Chapter 3, Section 3.11.4.
- **How is it used?**  
  Rules condition on the combination of HRI risk tier, demographic persona, and the dominant pollutant identified by TreeSHAP. For example, during high ozone days, asthmatic cohorts receive afternoon outdoor activity restrictions, whereas high $\text{PM}_{2.5}$ triggers N95 mask and HEPA filtration advisories.

---

## 11. Pillar 10: Production Architecture & Systems Resilience

### 11.1 Two-Tier Regional Hybrid Dispatch Architecture
- **Why is it used?**  
  India has over 4,000 cities, but only ~50 possess continuous CAAQMS monitoring networks. Building local machine learning models for unmonitored cities is impossible due to lack of training data, and LOCO tests proved inland models cannot be transferred zero-shot to coastal cities.
- **Where is it used?**  
  - Codebase: `backend/routes.py`, `backend/ml/regional_router.py`.
  - Thesis: Chapter 3, Section 3.1; Figure 3.1.
- **How is it used?**  
  - **Tier-1 (5 Primary Metros):** Delhi, Mumbai, Bengaluru, Chennai, Hyderabad. Routed to locally trained Stacking Ensembles ($R^2 = 0.9248$).
  - **Tier-2 (33 Regional Airsheds):** Bhubaneswar, Cuttack, Rourkela, Patna, etc. Routed to Copernicus Atmosphere Monitoring Service (CAMS) gridded reanalysis with regional bias calibration.

---

### 11.2 Circuit-Breaker Fault Tolerance Pattern
- **Why is it used?**  
  Upstream environmental APIs (CPCB, OpenAQ) suffer periodic outages and connection timeouts. A public health alert API must never crash or block user requests.
- **Where is it used?**  
  - Codebase: `backend/api/`, `backend/main.py`.
  - Thesis: Chapter 3, Section 3.12; Figure 3.6; Figure 3.7.
  - Audit File: `final_submission/results/api_resilience.md`.
- **How is it used?**  
  Tracks consecutive network failures to external APIs. If failures exceed threshold $\tau = 3$, the circuit trips to `OPEN` state, instantly bypassing live fetch and serving cached rolling observations or Copernicus CAMS fallback data within **42 ms**, maintaining 100% uptime SLA.

---

### 11.3 Warm-Start In-Memory Explainer Cache
- **Why is it used?**  
  Running TreeSHAP explainer initialization from disk on every incoming HTTP request takes 150–250 ms, violating real-time sub-10ms API SLAs.
- **Where is it used?**  
  - Codebase: `backend/ml/forecaster.py`, `backend/ml/explainer.py`.
  - Thesis: Chapter 3, Section 3.12.1.
- **How is it used?**  
  During FastAPI server startup (`@app.on_event("startup")`), all serialized scikit-learn, XGBoost, and SHAP TreeExplainer objects are pre-loaded into RAM. Inbound requests query the in-memory graph, achieving a median response latency of **2.41 ms** (p95 = **5.82 ms**) under 50 concurrent virtual users.

---

## 12. Master AI/ML Terms Quick-Reference Matrix

| Technical Term | Category / Pillar | Why is it Used? (Motivation) | Where is it Used? (Code & Thesis) | How is it Used? (Formulation / Metric) |
| :--- | :--- | :--- | :--- | :--- |
| **MICE / FCS** | Imputation | Sensor missingness (8.4% avg) destroys tabular training; MAR condition | `generate_ground_truth.py`, Chap 3 Sec 3.4 | Chained Bayesian Ridge regression ($T=10$); RMSE = **0.0061** |
| **MI-MMA Autoencoder** | Representation Learning | Compresses multi-pollutant cocktail into latent manifold | `autoencoder.py`, Chap 3 Sec 3.5 | PyTorch $7 \to 32 \to 12 \to 32 \to 7$; $\mathbf{Z}_{\text{MMA}} \in \mathbb{R}^{36}$; Loss = $10^{-5}$ |
| **Random Forest** | Bagging Ensemble | Non-parametric variance reduction; resilient to noise | `forecaster.py`, Chap 3 Sec 3.7.1 | 200 trees, depth 12; $R^2 = 0.8904$, $\text{RMSE} = 17.54$ |
| **XGBoost** | Boosting Ensemble | Second-order gradient optimization; minimizes bias | `forecaster.py`, Chap 3 Sec 3.7.2 | 300 trees, lr 0.03, depth 6; $R^2 = 0.8931$, $\text{RMSE} = 17.33$ |
| **Stacking Ensemble** | Meta-Learning | Blends orthogonal strengths of bagging & boosting | `forecaster.py`, Chap 3 Sec 3.8 | Ridge meta-learner; Base $R^2 = 0.9014$, Tuned $R^2 = \mathbf{0.9248}$ |
| **Optuna (TPE)** | Hyperparameter Tuning | Explores complex 81-D space far faster than Grid Search | `tune.py`, Chap 3 Sec 3.8.2 | 100 trials; boosted accuracy from 87.02% to **91.42%** |
| **Deep LSTM** | Model Evaluation | Evaluated for recurrent memory; overfit on daily tabular series | Chap 2 Sec 2.4, Chap 4 Sec 4.3 | 2-layer LSTM; $R^2 = 0.8312$, $\text{RMSE} = 21.68$ (**Excluded**) |
| **Pinball Loss** | Uncertainty Modeling | Distribution-free prediction intervals for asymmetric risk | `forecaster.py`, Chap 3 Sec 3.10 | $\mathcal{L}_\tau$ at $\tau=0.05, 0.95$; $\text{PICP} = \mathbf{90.01\%}$, width 43.91 |
| **TreeSHAP** | Explainable AI (XAI) | Transparent factor attribution grounded in game theory | `explainer.py`, Chap 3 Sec 3.9 | Polynomial-time tree traversal; top feature: AQI (19.54) |
| **LOCO Cross-Validation** | Spatial Validation | Assesses zero-shot geographic transfer to unmonitored cities | Chap 4 Sec 4.5, Table 4.4 | Mean LOCO $R^2 = 0.7054$; Coastal Chennai drops to $0.5155$ |
| **Paired $t$-test & Wilcoxon** | Inferential Statistics | Validates statistical significance of model improvements | Chap 4 Sec 4.4, Table 4.3 | $t = -3.722 \ (p = 0.0002)$, $W = 1.26\times 10^6 \ (p = 3.00\times 10^{-5})$ |
| **Continuous Accuracy** | Performance Metric | Percentage accuracy without artificial classification binning | `final_metrics.json`, Chap 4 Sec 4.3 | $\text{Accuracy} = \max(0, 100\% - \text{MAPE}) = \mathbf{91.42\%}$ |
| **Health Risk Index (HRI)** | Health Informatics | Replaces flawed single-pollutant piecewise maximum | `hri_engine.py`, Chap 3 Sec 3.11 | $\text{HRI}_g = V_g \sum w_p (C_p / S_p)^\beta$; Shared cutoffs scale |
| **Vulnerability Multiplier** | Epidemiological Stratification | Models elevated risks in children, elderly, asthmatics | `hri_engine.py`, Chap 3 Sec 3.11.2 | $V_g \in \{1.0\times, 1.3\times, 1.6\times\}$; Alerts: 24.9% to 55.7% |
| **Ventilation Index** | Atmospheric Physics | Captures vertical mixing depth $\times$ horizontal dispersion | `data_loader.py`, Chap 3 Sec 3.6 | $\text{VI} = \text{PBLH} \times U_{10} \ [\text{m}^2/\text{s}]$ |
| **Two-Tier Architecture** | System Engineering | Handles unmonitored cities where local ML cannot train | `routes.py`, Chap 3 Sec 3.1 | Tier-1: ML Metros; Tier-2: Copernicus CAMS Reanalysis |
| **Circuit Breaker** | Production Engineering | Prevents system hangs during sensor API outages | `backend/api/`, Chap 3 Sec 3.12 | Tripped state fallbacks to cache or CAMS in **42 ms** |

---

## 13. Panel Examination & Viva Defense Q&A Cheat Sheet

### Q1: Why did you choose a Stacking Ensemble instead of simply picking XGBoost or Random Forest?
> **Answer:** "Random Forest is a bagging ensemble that reduces variance by averaging decorrelated trees, while XGBoost is a boosting ensemble that iteratively reduces residual bias using second-order gradients. Neither model dominates across all meteorological regimes. Stacking uses a Ridge meta-regressor trained on out-of-fold predictions that learns optimal weighting dynamically. In our 10-model ablation study, standalone Random Forest achieved $R^2 = 0.8904$ and XGBoost achieved $R^2 = 0.8931$, whereas our Dual Stacking Ensemble achieved $R^2 = 0.9014$ (baseline) and $R^2 = 0.9248$ (Optuna-tuned), reducing RMSE from 17.33 down to 13.84 AQI points. Formal paired hypothesis testing confirms this improvement is statistically significant ($p = 0.0002$ on Student's $t$-test; $p = 3.003 \times 10^{-5}$ on Wilcoxon signed-rank test)."

### Q2: Why did you reject Deep LSTM networks when LSTMs are so popular in recent air quality papers?
> **Answer:** "This was one of our key empirical findings and honest scientific disclosures. We implemented a 2-layer PyTorch LSTM with a 7-day lookback window. It achieved an $R^2$ of only 0.8312 and an RMSE of 21.68 AQI points—significantly worse than tree-based models. Furthermore, when we created a Tri-Ensemble blending Random Forest, XGBoost, and LSTM, the ensemble's performance degraded from $R^2 = 0.9014$ down to $0.8782$. This occurs because daily environmental time series with episodic shocks (such as Diwali firecracker bursts or sudden stubble burning plumes) require sharp, orthogonal step splits rather than recurrent gradient descent across temporal sequences. LSTMs overfit high-frequency noise in tabular aggregates, so we openly documented and excluded LSTM from production."

### Q3: How do you define your headline accuracy of 91.42%? Is it classification or regression?
> **Answer:** "It is strictly a continuous regression accuracy, defined as $\text{Accuracy} = \max(0,\, 100\% - \text{MAPE})$, where MAPE is the Mean Absolute Percentage Error. For our Optuna-tuned production model on the held-out test set (2,403 samples), the MAPE is exactly $8.58\%$, yielding an accuracy of $100\% - 8.58\% = 91.42\%$. We avoided discretizing AQI into classification bins because predicting 199 as Moderate and 201 as Poor creates an artificial boundary penalty, whereas continuous regression evaluates the exact numerical fidelity across all concentrations."

### Q4: Why is a shared cutoff scale mandatory in your Health Risk Index (HRI)?
> **Answer:** "Our HRI incorporates demographic vulnerability multipliers: $V_g = 1.0$ for the General Public, $1.3$ for Children/Elderly, and $1.6$ for Respiratory Patients ($\text{HRI}_g = V_g \cdot \text{HRI}_{\text{GP}}$). If cutoffs were calculated using group-specific percentiles, $P_{75}^{(g)} = \text{Quantile}(V_g \cdot \text{HRI}_{\text{GP}}, 0.75) = V_g \cdot P_{75}^{(\text{GP})}$. The test condition for an alert would be $V_g \cdot \text{HRI}_{\text{GP}} > V_g \cdot P_{75}^{(\text{GP})}$, where $V_g$ cancels out mathematically on both sides. This would force every demographic group to have an identical 25% alert rate. By locking a single shared scale derived from the General Public baseline, our system produces clinically differentiated alert rates: 24.93% for the general public, 39.91% for children, and 55.72% for respiratory patients."

### Q5: What is data leakage and how did you mathematically prove your pipeline is leakage-free?
> **Answer:** "Data leakage occurs when information from outside the training dataset (such as future observations) contaminates model training, producing artificially inflated test scores that collapse in production. We enforced four strict invariants: (1) an 80/20 chronological time-series split per city with zero random shuffling; (2) fitting all imputers, scalers, and encoders strictly on the training partition (2018–mid 2023) and only transforming the test set; (3) computing rolling statistics strictly backwards ($t-1 \dots t-7$); and (4) out-of-fold cross-validation for stacking meta-features. We verified this with an automated leakage test script that confirmed zero timestamp overlap and immutable SHA-256 hashes."

### Q6: What did your Leave-One-City-Out (LOCO) experiment reveal about spatial transferability?
> **Answer:** "LOCO cross-validation evaluated zero-shot transfer by training on four metros and testing on the fifth without local retraining. The mean $R^2$ dropped from $0.9014$ to $0.7054$. Chennai experienced the sharpest collapse, falling to $R^2 = 0.5155$. This happens because Chennai's coastal maritime boundary layer, diurnal sea breezes, and humidity dynamics differ fundamentally from the inland Gangetic plain of Delhi. This empirical breakdown directly justifies VayuDrishti's Two-Tier Architecture: 5 monitored metros use local ML models, while 33 unmonitored cities use Copernicus CAMS numerical atmospheric reanalysis with calibrated bias scaling."

---
*Manual compiled and audited for the Department of Computer Science & Engineering, C.V. Raman Global University, Bhubaneswar.*
