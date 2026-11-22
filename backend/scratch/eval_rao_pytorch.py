import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath("backend"))

import torch
import torch.nn as nn
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score, mean_absolute_percentage_error
from xgboost import XGBRegressor
from sklearn.ensemble import RandomForestRegressor
from pipeline.data_ingestion import load_and_merge, ALL_NUMERIC_COLS
from pipeline.imputation import run_imputation
from pipeline.preprocessing import preprocess
from pipeline.feature_engineering import (
    create_lag_features, get_feature_columns, time_based_split,
    add_fused_features, get_fused_feature_columns
)

# 1. Load and impute
raw_data = load_and_merge()
imputed = run_imputation(raw_data)
best_imputed = imputed["KNN_D"]
preprocessed = preprocess(best_imputed)

# 2. PyTorch Autoencoder (7 -> 32 -> 12 -> 32 -> 7)
class Autoencoder(nn.Module):
    def __init__(self, in_dim=7, hidden_dim=32, bottleneck_dim=12):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(in_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, bottleneck_dim),
            nn.ReLU()
        )
        self.decoder = nn.Sequential(
            nn.Linear(bottleneck_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, in_dim)
        )
    def forward(self, x):
        bottleneck = self.encoder(x)
        recon = self.decoder(bottleneck)
        return recon, bottleneck

variants = {
    "KNN_AE": imputed["KNN_D"],
    "MICE_AE": imputed["MICE_D"],
    "SVD_AE": imputed["SVD_D"],
}

cols = [c for c in ALL_NUMERIC_COLS if c in preprocessed.columns]
bottlenecks = []

torch.manual_seed(42)
np.random.seed(42)

for name, v_df in variants.items():
    scaler = StandardScaler()
    X = scaler.fit_transform(v_df[cols].values.astype(np.float32))
    X_tensor = torch.tensor(X, dtype=torch.float32)
    
    ae = Autoencoder(in_dim=len(cols), hidden_dim=32, bottleneck_dim=12)
    opt = torch.optim.Adam(ae.parameters(), lr=0.005)
    criterion = nn.MSELoss()
    
    ae.train()
    for ep in range(40):
        opt.zero_grad()
        recon, _ = ae(X_tensor)
        loss = criterion(recon, X_tensor)
        loss.backward()
        opt.step()
        
    ae.eval()
    with torch.no_grad():
        _, b_vec = ae(X_tensor)
    bottlenecks.append(b_vec.numpy())
    print(f"Trained {name} AE, final loss={loss.item():.5f}, bottleneck shape={b_vec.shape}")

fused_36 = np.hstack(bottlenecks)
print(f"Fused 36-dim vector shape: {fused_36.shape}")

# 3. Create lags and attach fused features
df_features = create_lag_features(preprocessed)
offset = len(fused_36) - len(df_features)
fused_aligned = fused_36[offset:offset + len(df_features)]
df_features = add_fused_features(df_features, fused_aligned)

base_pollutant_lags = [c for c in get_feature_columns(df_features) if not any(w in c for w in ["temp", "humidity", "wind", "pressure", "diwali", "stubble", "fused"])]
weather_cols = [c for c in get_feature_columns(df_features) if any(w in c for w in ["temp", "humidity", "wind", "pressure"]) and not any(e in c for e in ["diwali", "stubble"])]
event_cols = [c for c in get_feature_columns(df_features) if any(e in c for e in ["diwali", "stubble"])]
fused_cols = get_fused_feature_columns(36)
all_feature_cols = base_pollutant_lags + weather_cols + event_cols + fused_cols
rao_features = base_pollutant_lags + fused_cols

print(f"Base lags count: {len(base_pollutant_lags)}")
print(f"Rao features (lags + 36 MMA): {len(rao_features)}")
print(f"All features count: {len(all_feature_cols)}")

split_res = time_based_split(df_features, all_feature_cols, target_col="AQI_next_day")
X_tr, y_tr = split_res["X_train"], split_res["y_train"]
X_te, y_te = split_res["X_test"], split_res["y_test"]

# A. Standalone XGBoost (no weather, no MMA)
xgb_base = XGBRegressor(n_estimators=150, max_depth=6, learning_rate=0.08, random_state=42, n_jobs=-1)
xgb_base.fit(X_tr[base_pollutant_lags], y_tr)
p_base = xgb_base.predict(X_te[base_pollutant_lags])
rmse_base = np.sqrt(mean_squared_error(y_te, p_base))
mae_base = mean_absolute_error(y_te, p_base)
r2_base = r2_score(y_te, p_base)
mape_base = mean_absolute_percentage_error(y_te, p_base) * 100
print("\n--- RESULTS ---")
print(f"1. Standalone XGBoost (lags only)       : RMSE={rmse_base:.2f}, MAE={mae_base:.2f}, R2={r2_base:.4f}, MAPE={mape_base:.2f}%")

# B. Rao et al. Baseline (lags + 36 MMA Autoencoder features + XGBoost)
xgb_rao = XGBRegressor(n_estimators=150, max_depth=6, learning_rate=0.08, random_state=42, n_jobs=-1)
xgb_rao.fit(X_tr[rao_features], y_tr)
p_rao = xgb_rao.predict(X_te[rao_features])
rmse_rao = np.sqrt(mean_squared_error(y_te, p_rao))
mae_rao = mean_absolute_error(y_te, p_rao)
r2_rao = r2_score(y_te, p_rao)
mape_rao = mean_absolute_percentage_error(y_te, p_rao) * 100
print(f"2. Baseline: Rao et al. (MMA + XGBoost) : RMSE={rmse_rao:.2f}, MAE={mae_rao:.2f}, R2={r2_rao:.4f}, MAPE={mape_rao:.2f}%")

# C. Standalone RF (Kashyap et al.)
rf_kashyap = RandomForestRegressor(n_estimators=150, max_depth=15, random_state=42, n_jobs=-1)
rf_kashyap.fit(X_tr[base_pollutant_lags], y_tr)
p_kashyap = rf_kashyap.predict(X_te[base_pollutant_lags])
rmse_kashyap = np.sqrt(mean_squared_error(y_te, p_kashyap))
mae_kashyap = mean_absolute_error(y_te, p_kashyap)
r2_kashyap = r2_score(y_te, p_kashyap)
mape_kashyap = mean_absolute_percentage_error(y_te, p_kashyap) * 100
print(f"3. Baseline: Kashyap et al. (RF on lags): RMSE={rmse_kashyap:.2f}, MAE={mae_kashyap:.2f}, R2={r2_kashyap:.4f}, MAPE={mape_kashyap:.2f}%")

# D. Stacking Ensemble (RF + XGBoost on full features)
rf_full = RandomForestRegressor(n_estimators=150, max_depth=15, random_state=42, n_jobs=-1)
rf_full.fit(X_tr[all_feature_cols], y_tr)
p_rf = rf_full.predict(X_te[all_feature_cols])

xgb_full = XGBRegressor(n_estimators=150, max_depth=6, learning_rate=0.08, random_state=42, n_jobs=-1)
xgb_full.fit(X_tr[all_feature_cols], y_tr)
p_xgb = xgb_full.predict(X_te[all_feature_cols])

p_ens = (p_rf + p_xgb) / 2.0
rmse_ens = np.sqrt(mean_squared_error(y_te, p_ens))
mae_ens = mean_absolute_error(y_te, p_ens)
r2_ens = r2_score(y_te, p_ens)
mape_ens = mean_absolute_percentage_error(y_te, p_ens) * 100
print(f"4. Proposed Stacking Ensemble (RF+XGB)  : RMSE={rmse_ens:.2f}, MAE={mae_ens:.2f}, R2={r2_ens:.4f}, MAPE={mape_ens:.2f}%")
