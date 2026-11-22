import sys
import os
sys.path.insert(0, os.path.abspath("backend"))

import numpy as np
import pandas as pd
from pipeline.data_ingestion import load_and_merge
from pipeline.imputation import run_imputation
from pipeline.preprocessing import preprocess
from pipeline.feature_engineering import (
    create_lag_features, get_feature_columns, time_based_split,
    add_fused_features, get_fused_feature_columns, prepare_lstm_sequences
)
from pipeline.models import train_lstm
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score, mean_absolute_percentage_error
from xgboost import XGBRegressor
from sklearn.ensemble import RandomForestRegressor
from tensorflow import keras
import joblib

print("Loading data...")
raw_data = load_and_merge()
imputed = run_imputation(raw_data)
best_imputed = imputed['KNN_D']
preprocessed = preprocess(best_imputed)
df_features = create_lag_features(preprocessed)

# Load existing trained autoencoders
knn_enc = keras.models.load_model('backend/models/knn_ae_encoder.keras')
mice_enc = keras.models.load_model('backend/models/mice_ae_encoder.keras')
svd_enc = keras.models.load_model('backend/models/svd_ae_encoder.keras')
knn_s = joblib.load('backend/models/knn_ae_scaler.joblib')
mice_s = joblib.load('backend/models/mice_ae_scaler.joblib')
svd_s = joblib.load('backend/models/svd_ae_scaler.joblib')

from pipeline.autoencoder import AE_FEATURE_COLS
cols = [c for c in AE_FEATURE_COLS if c in preprocessed.columns]
f_knn = knn_enc.predict(knn_s.transform(imputed['KNN_D'][cols].values.astype(np.float32)), verbose=0)
f_mice = mice_enc.predict(mice_s.transform(imputed['MICE_D'][cols].values.astype(np.float32)), verbose=0)
f_svd = svd_enc.predict(svd_s.transform(imputed['SVD_D'][cols].values.astype(np.float32)), verbose=0)
fused = np.hstack([f_knn, f_mice, f_svd])

offset = len(fused) - len(df_features)
fused_aligned = fused[offset:offset+len(df_features)]
df_features = add_fused_features(df_features, fused_aligned)

fused_cols = get_fused_feature_columns(fused_aligned.shape[1])
base_lags = [c for c in get_feature_columns(df_features) if not any(w in c for w in ['temp', 'humidity', 'wind', 'pressure', 'diwali', 'stubble', 'fused'])]
all_feature_cols = get_feature_columns(df_features) + fused_cols
rao_features = base_lags + fused_cols

print(f"Base pollutant lags: {len(base_lags)}")
print(f"Rao features (lags + 36 MMA features): {len(rao_features)}")
print(f"All features: {len(all_feature_cols)}")

split_res = time_based_split(df_features, all_feature_cols, target_col='AQI_next_day')
X_tr, y_tr = split_res['X_train'], split_res['y_train']
X_te, y_te = split_res['X_test'], split_res['y_test']

# 1. Standalone XGBoost (no weather, no MMA)
print("\n--- 1. Standalone XGBoost (lags only) ---")
xgb_base = XGBRegressor(n_estimators=150, max_depth=6, learning_rate=0.08, random_state=42, n_jobs=-1)
xgb_base.fit(X_tr[base_lags], y_tr)
p_base = xgb_base.predict(X_te[base_lags])
rmse_base = np.sqrt(mean_squared_error(y_te, p_base))
mae_base = mean_absolute_error(y_te, p_base)
r2_base = r2_score(y_te, p_base)
mape_base = mean_absolute_percentage_error(y_te, p_base) * 100
print(f"Standalone XGBoost: RMSE={rmse_base:.2f}, MAE={mae_base:.2f}, R2={r2_base:.4f}, MAPE={mape_base:.2f}%")

# 2. Rao et al. (MMA autoencoder features + XGBoost)
print("\n--- 2. Rao et al. (lags + 36 MMA Autoencoder features + XGBoost) ---")
xgb_rao = XGBRegressor(n_estimators=150, max_depth=6, learning_rate=0.08, random_state=42, n_jobs=-1)
xgb_rao.fit(X_tr[rao_features], y_tr)
p_rao = xgb_rao.predict(X_te[rao_features])
rmse_rao = np.sqrt(mean_squared_error(y_te, p_rao))
mae_rao = mean_absolute_error(y_te, p_rao)
r2_rao = r2_score(y_te, p_rao)
mape_rao = mean_absolute_percentage_error(y_te, p_rao) * 100
print(f"Rao et al. (MMA+XGBoost): RMSE={rmse_rao:.2f}, MAE={mae_rao:.2f}, R2={r2_rao:.4f}, MAPE={mape_rao:.2f}%")

# 3. Train RF on full features
print("\n--- 3. RF on full features ---")
rf_full = RandomForestRegressor(n_estimators=150, max_depth=15, random_state=42, n_jobs=-1)
rf_full.fit(X_tr[all_feature_cols], y_tr)
p_rf = rf_full.predict(X_te[all_feature_cols])
print(f"RF (all features): RMSE={np.sqrt(mean_squared_error(y_te, p_rf)):.2f}, R2={r2_score(y_te, p_rf):.4f}")

# 4. Train XGB on full features
print("\n--- 4. XGB on full features ---")
xgb_full = XGBRegressor(n_estimators=150, max_depth=6, learning_rate=0.08, random_state=42, n_jobs=-1)
xgb_full.fit(X_tr[all_feature_cols], y_tr)
p_xgb = xgb_full.predict(X_te[all_feature_cols])
print(f"XGB (all features): RMSE={np.sqrt(mean_squared_error(y_te, p_xgb)):.2f}, R2={r2_score(y_te, p_xgb):.4f}")

# 5. LSTM evaluation
print("\n--- 5. Evaluating LSTM ---")
lstm_data = prepare_lstm_sequences(df_features, base_lags)
# Load existing trained LSTM
lstm_model = keras.models.load_model('backend/models/lstm_model.keras')
lstm_scaler = joblib.load('backend/models/lstm_scaler.joblib')

X_te_scaled = lstm_scaler.transform(lstm_data["X_test_seq"].reshape(-1, lstm_data["X_test_seq"].shape[-1])).reshape(lstm_data["X_test_seq"].shape)
p_lstm = lstm_model.predict(X_te_scaled, verbose=0).flatten()
y_lstm_te = lstm_data["y_test_seq"]
rmse_lstm = np.sqrt(mean_squared_error(y_lstm_te, p_lstm))
mae_lstm = mean_absolute_error(y_lstm_te, p_lstm)
r2_lstm = r2_score(y_lstm_te, p_lstm)
mape_lstm = mean_absolute_percentage_error(y_lstm_te, p_lstm) * 100
print(f"Standalone LSTM: RMSE={rmse_lstm:.2f}, MAE={mae_lstm:.2f}, R2={r2_lstm:.4f}, MAPE={mape_lstm:.2f}%")

# Aligned length for comparing ensembles
min_len = min(len(p_rf), len(p_xgb), len(p_lstm))
y_aligned = y_te.values[-min_len:]
rf_aligned = p_rf[-min_len:]
xgb_aligned = p_xgb[-min_len:]
lstm_aligned = p_lstm[-min_len:]

# Dual Ensemble (RF + XGBoost)
p_dual = (rf_aligned + xgb_aligned) / 2.0
rmse_dual = np.sqrt(mean_squared_error(y_aligned, p_dual))
mae_dual = mean_absolute_error(y_aligned, p_dual)
r2_dual = r2_score(y_aligned, p_dual)
mape_dual = mean_absolute_percentage_error(y_aligned, p_dual) * 100
print(f"\nDual Ensemble (RF + XGBoost): RMSE={rmse_dual:.2f}, MAE={mae_dual:.2f}, R2={r2_dual:.4f}, MAPE={mape_dual:.2f}%")

# Tri-Ensemble (RF + XGBoost + LSTM Equal Average)
p_tri = (rf_aligned + xgb_aligned + lstm_aligned) / 3.0
rmse_tri = np.sqrt(mean_squared_error(y_aligned, p_tri))
mae_tri = mean_absolute_error(y_aligned, p_tri)
r2_tri = r2_score(y_aligned, p_tri)
mape_tri = mean_absolute_percentage_error(y_aligned, p_tri) * 100
print(f"Tri-Ensemble (RF + XGBoost + LSTM Equal Avg): RMSE={rmse_tri:.2f}, MAE={mae_tri:.2f}, R2={r2_tri:.4f}, MAPE={mape_tri:.2f}%")

# Stacking / Weighted Ensemble (Optimal Weights e.g. Ridge on predictions or 0.45 RF + 0.45 XGB + 0.10 LSTM)
from sklearn.linear_model import RidgeCV
meta_X_tr = np.column_stack([rf_aligned[:int(0.5*min_len)], xgb_aligned[:int(0.5*min_len)], lstm_aligned[:int(0.5*min_len)]])
meta_y_tr = y_aligned[:int(0.5*min_len)]
meta_X_te = np.column_stack([rf_aligned[int(0.5*min_len):], xgb_aligned[int(0.5*min_len):], lstm_aligned[int(0.5*min_len):]])
meta_y_te = y_aligned[int(0.5*min_len):]
meta = RidgeCV(positive=True)
meta.fit(meta_X_tr, meta_y_tr)
p_stack = meta.predict(meta_X_te)
print(f"Stacking Ensemble (RF + XGB + LSTM learned weights: {meta.coef_}): RMSE={np.sqrt(mean_squared_error(meta_y_te, p_stack)):.2f}, R2={r2_score(meta_y_te, p_stack):.4f}")
