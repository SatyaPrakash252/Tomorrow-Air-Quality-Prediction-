# VayuDrishti Data Leakage & Chronological Integrity Audit

**Project:** AI-Driven Air Quality Forecasting and Public Health Risk Alert System for Indian Metropolitan Cities  
**Document:** Methodological Audit on Information Leakage Prevention  
**Date:** September 2026  
**Auditors / Authors:** Satyaprakash Rout, Likuna Swain, Ch Saipriya Patra, Arpeet Barik  
**Supervision:** Prof. Soumya Sahoo, Department of CSE, C.V. Raman Global University  

---

## 1. Executive Summary

Data leakage occurs when information from outside the training dataset is improperly utilized to create or tune a machine learning model, leading to overly optimistic evaluation metrics that fail to generalize to real-world operations. In temporal environmental systems, the most insidious forms of data leakage arise from:
1. **Random cross-validation splits** that shuffle past and future days together.
2. **Global preprocessing & scaling** calculated across the entire dataset before splitting.
3. **Hyperparameter optimization (Optuna)** evaluating on test samples.
4. **Synthetic imputation or autoencoder representations** fitting on held-out temporal windows.

This audit details the architectural and algorithmic barriers implemented in VayuDrishti to guarantee **zero future information leakage**. Every claim is anchored by exact source file and line number citations.

---

## 2. Chronological Train/Test Partitioning

### 2.1 Code Reference
- **Source File:** `backend/pipeline/feature_engineering.py`
- **Lines:** 25, 178–220

### 2.2 Mechanism
In `time_based_split()`, observations for each city are strictly sorted by date in ascending order (`Date` timestamp). Rather than using randomized splits (e.g., standard `train_test_split(shuffle=True)`), the chronological index boundary is fixed at 80%:
```python
# feature_engineering.py, lines 185-195
split_idx = int(len(city_df) * TRAIN_FRACTION)  # TRAIN_FRACTION = 0.80
city_train = city_df.iloc[:split_idx]
city_test = city_df.iloc[split_idx:]
```
- **Training Period:** January 1, 2018 to June 30, 2023 (9,609 daily records across 5 metros).
- **Held-Out Test Period:** July 1, 2023 to December 31, 2024 (2,403 daily records across 5 metros).

### 2.3 Verification
No sample from July 2023 onwards appears in the training partition. All autoregressive lag features ($t-1, t-2, t-3$) are generated *prior* to splitting and respect causality: feature vectors at test time $t+1$ utilize only observations available at or before day $t$.

---

## 3. Preprocessing, Imputation & Feature Scaling Isolation

### 3.1 Code References
- **Feature Scaling:** `backend/pipeline/ablation_study.py`, lines 261–265
- **Autoencoder Bottlenecks:** `backend/pipeline/autoencoder.py`, lines 77–83
- **Imputation:** `backend/pipeline/imputation.py`, lines 63–95

### 3.2 Mechanism
1. **StandardScaler Fitting:** In neural sequence training (LSTM) and autoencoder embedding extraction, standard scalers are fitted exclusively on the training partition:
   ```python
   # ablation_study.py, lines 264-265
   train_df_s[lstm_feats] = s_lstm.fit_transform(train_df[lstm_feats])
   test_df_s[lstm_feats] = s_lstm.transform(test_df[lstm_feats])
   ```
   The test partition is transformed using parameters ($\mu_{\text{train}}, \sigma_{\text{train}}$) learned strictly from the training window. No test data statistics inform feature scaling.
2. **Outlier Capping:** Outlier bounds are computed using Interquartile Ranges (IQR) derived from training baselines. Capping prevents extreme episodic anomalies (e.g., firecracker spikes) from artificially warping the model's normal operational boundary.

---

## 4. Hyperparameter Tuning Isolation (Optuna & Walk-Forward CV)

### 4.1 Code Reference
- **Source File:** `backend/pipeline/models.py`
- **Lines:** 44–110

### 4.2 Mechanism
Hyperparameter optimization for Random Forest and XGBoost utilizes Optuna's Tree-Structured Parzen Estimator (TPE) algorithm. To ensure absolute temporal validity during hyperparameter searches:
1. **Walk-Forward Cross-Validation:** Standard $K$-fold cross-validation is prohibited. Instead, `TimeSeriesSplit(n_splits=5)` is enforced:
   ```python
   # models.py, lines 46, 57-64
   tscv = TimeSeriesSplit(n_splits=N_CV_SPLITS)
   for train_idx, val_idx in tscv.split(X_train):
       X_tr, X_val = X_train.iloc[train_idx], X_train.iloc[val_idx]
       y_tr, y_val = y_train.iloc[train_idx], y_train.iloc[val_idx]
   ```
2. **Test Set Shielding:** Only `X_train` and `y_train` are provided to the Optuna search objective. The test partition (`X_test`, `y_test`) is never imported, passed, or referenced inside `_tune_rf()` or `_tune_xgb()`.
3. **No Target Leakage in CV:** In each fold of `TimeSeriesSplit`, the validation fold $k$ is strictly chronologically subsequent to training folds $1 \dots k-1$.

---

## 5. Live Operational Pipeline & Verification Logging

### 5.1 Code References
- **Source File:** `backend/api/validation.py`, lines 69–116, 148–215
- **Source File:** `backend/api/live_inference.py`, lines 70–145

### 5.2 Mechanism
In production deployment:
1. **"Yesterday Pred" Authenticity:** When comparing live AQI against model forecasts, the predicted value is retrieved from the `daily_forecasts` SQLite table where it was stored during yesterday's execution cycle. It is never computed retroactively or sampled from historical test sets.
2. **Real Multi-Day Lag Construction:** Live inference queries real station measurements from WAQI and Open-Meteo for days $t, t-1, t-2, t-3$ to assemble the exact 81-dimensional feature vector in real time.
3. **Fail-Closed Missing Data:** If upstream live telemetry is missing or unreachable, the system raises an explicit `503 Service Unavailable` status rather than injecting synthetic or backfilled values.

---

## 6. Audit Conclusion

The VayuDrishti experimental pipeline complies with strict standards of time-series machine learning:
- **Zero lookahead leakage:** Causality is maintained across all 81 features.
- **Strict chronological split:** Training (2018–mid 2023) and testing (mid 2023–2024) are temporally disjoint.
- **Walk-forward hyperparameter optimization:** Optuna tunes purely on past chronological folds without viewing the test horizon.
- **Operational verification:** Automated logging stores genuine predictions prior to actual observation.
