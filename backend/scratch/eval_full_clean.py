import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath('backend'))

import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from xgboost import XGBRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from scipy import stats

from pipeline.data_ingestion import load_and_merge, ALL_NUMERIC_COLS
from pipeline.imputation import run_imputation
from pipeline.preprocessing import preprocess
from pipeline.feature_engineering import (
    create_lag_features, get_feature_columns, time_based_split,
    add_fused_features, get_fused_feature_columns,
    WEATHER_COLS, WEATHER_LAG_COLS
)

def calc_metrics(y_true, y_pred, name):
    rmse = round(float(np.sqrt(mean_squared_error(y_true, y_pred))), 2)
    mae = round(float(mean_absolute_error(y_true, y_pred)), 2)
    r2 = round(float(r2_score(y_true, y_pred)), 4)
    mape = float(np.mean(np.abs((y_true - y_pred) / np.clip(y_true, 1.0, None)))) * 100.0
    acc = round(max(0, 100.0 - mape), 2)
    return {
        'model': name,
        'RMSE': rmse,
        'MAE': mae,
        'R2': r2,
        'MAPE': round(mape, 2),
        'Accuracy': acc
    }

# 1. Ingestion & Imputation
raw_data = load_and_merge()
raw_data['AQI'] = raw_data['AQI'].ffill().bfill()
imputed = run_imputation(raw_data)

for k in ['KNN_D', 'MICE_D', 'SVD_D']:
    imputed[k]['AQI'] = imputed[k]['AQI'].ffill().bfill()

best_imputed = imputed['KNN_D']
preprocessed = preprocess(best_imputed)

# 2. PyTorch MMA Autoencoders
torch.manual_seed(42)
np.random.seed(42)

class SymmetricAE(nn.Module):
    def __init__(self, in_dim=7, hidden_dim=32, bottleneck_dim=12):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(in_dim, hidden_dim),
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
        b = self.encoder(x)
        r = self.decoder(b)
        return r, b

variants = {'KNN_AE': imputed['KNN_D'], 'MICE_AE': imputed['MICE_D'], 'SVD_AE': imputed['SVD_D']}
cols = [c for c in ALL_NUMERIC_COLS if c in preprocessed.columns]
bottlenecks = []

for name, v_df in variants.items():
    s = StandardScaler()
    X_s = s.fit_transform(v_df[cols].values.astype(np.float32))
    X_t = torch.tensor(X_s, dtype=torch.float32)
    ae = SymmetricAE(len(cols), 32, 12)
    opt = torch.optim.Adam(ae.parameters(), lr=0.005)
    loss_fn = nn.MSELoss()
    
    loader = DataLoader(TensorDataset(X_t, X_t), batch_size=64, shuffle=True)
    ae.train()
    for ep in range(25):
        for bx, _ in loader:
            opt.zero_grad()
            rec, _ = ae(bx)
            l = loss_fn(rec, bx)
            l.backward()
            opt.step()
    ae.eval()
    with torch.no_grad():
        _, b_vec = ae(X_t)
    loss_val = loss_fn(ae(X_t)[0], X_t).item()
    print(f'Trained {name} AE, final loss={loss_val:.5f}, bottleneck={b_vec.shape}')
    bottlenecks.append(b_vec.numpy())

fused_36 = np.hstack(bottlenecks)

# 3. Create lags and feature sets
df_features = create_lag_features(preprocessed)
offset = len(fused_36) - len(df_features)
fused_aligned = fused_36[offset:offset + len(df_features)]
df_features = add_fused_features(df_features, fused_aligned)

fused_cols = get_fused_feature_columns(36)
all_base_cols = get_feature_columns(df_features)

base_pollutant_lags = [c for c in all_base_cols if not any(w in c for w in ['temp', 'humidity', 'wind', 'pressure', 'diwali', 'stubble', 'fused'])]
weather_cols = [c for c in all_base_cols if any(w in c for w in ['temp', 'humidity', 'wind', 'pressure']) and not any(e in c for e in ['diwali', 'stubble'])]
event_cols = [c for c in all_base_cols if any(e in c for e in ['diwali', 'stubble'])]

all_feature_cols = base_pollutant_lags + weather_cols + event_cols + fused_cols
rao_features = base_pollutant_lags + fused_cols

print(f'Feature breakdown: base_lags={len(base_pollutant_lags)}, rao={len(rao_features)}, all={len(all_feature_cols)}')

split_res = time_based_split(df_features, all_feature_cols, target_col='AQI_next_day')
X_tr, y_tr = split_res['X_train'], split_res['y_train']
X_te, y_te = split_res['X_test'], split_res['y_test']

results = []

# 1. Ridge Baseline
ridge = Ridge(alpha=1.0, random_state=42)
ridge.fit(X_tr[base_pollutant_lags], y_tr)
results.append(calc_metrics(y_te, ridge.predict(X_te[base_pollutant_lags]), 'Simple Linear Baseline: Ridge Regression'))

# 2. Kashyap et al. (RF on lags)
rf_kashyap = RandomForestRegressor(n_estimators=150, max_depth=15, random_state=42, n_jobs=-1)
rf_kashyap.fit(X_tr[base_pollutant_lags], y_tr)
results.append(calc_metrics(y_te, rf_kashyap.predict(X_te[base_pollutant_lags]), 'Baseline: Kashyap et al. (Standard RF on lags)'))

# 3. Standalone XGBoost (no weather, no MMA)
xgb_base = XGBRegressor(n_estimators=150, max_depth=6, learning_rate=0.08, random_state=42, n_jobs=-1)
xgb_base.fit(X_tr[base_pollutant_lags], y_tr)
results.append(calc_metrics(y_te, xgb_base.predict(X_te[base_pollutant_lags]), 'Ablation: Standalone XGBoost (lags only, no weather/MMA)'))

# 4. Rao et al. (MMA + XGBoost)
xgb_rao = XGBRegressor(n_estimators=150, max_depth=6, learning_rate=0.08, random_state=42, n_jobs=-1)
xgb_rao.fit(X_tr[rao_features], y_tr)
results.append(calc_metrics(y_te, xgb_rao.predict(X_te[rao_features]), 'Baseline: Rao et al. (Multimodal Imputation + MMA + XGBoost)'))

# 5. RF + Meteorological Features
rf_w = RandomForestRegressor(n_estimators=150, max_depth=15, random_state=42, n_jobs=-1)
rf_w.fit(X_tr[base_pollutant_lags + weather_cols], y_tr)
results.append(calc_metrics(y_te, rf_w.predict(X_te[base_pollutant_lags + weather_cols]), 'Ablation: RF + Meteorological Features (+ERA5)'))

# 6. RF + Weather + Events
rf_we = RandomForestRegressor(n_estimators=150, max_depth=15, random_state=42, n_jobs=-1)
rf_we.fit(X_tr[base_pollutant_lags + weather_cols + event_cols], y_tr)
results.append(calc_metrics(y_te, rf_we.predict(X_te[base_pollutant_lags + weather_cols + event_cols]), 'Ablation: RF + Weather + Event Awareness (+Diwali/Stubble)'))

# 7. Proposed Stacking Ensemble (RF + XGB on all features)
rf_full = RandomForestRegressor(n_estimators=150, max_depth=15, random_state=42, n_jobs=-1)
rf_full.fit(X_tr[all_feature_cols], y_tr)
p_rf = rf_full.predict(X_te[all_feature_cols])

xgb_full = XGBRegressor(n_estimators=150, max_depth=6, learning_rate=0.08, random_state=42, n_jobs=-1)
xgb_full.fit(X_tr[all_feature_cols], y_tr)
p_xgb = xgb_full.predict(X_te[all_feature_cols])

p_ens = (p_rf + p_xgb) / 2.0
results.append(calc_metrics(y_te, p_ens, 'Proposed: Stacking Ensemble (RF + XGBoost)'))

# 8. Train PyTorch LSTM on sequences to get honest LSTM & Tri-Ensemble numbers
seq_len = 7
def make_seqs(df, feat_cols, seq_len=7):
    seqs, targets = [], []
    for city in df['City'].unique():
        cdf = df[df['City'] == city].sort_values('Date').reset_index(drop=True)
        vals = cdf[feat_cols].values.astype(np.float32)
        y_vals = cdf['AQI_next_day'].values.astype(np.float32)
        for i in range(len(vals) - seq_len):
            seqs.append(vals[i:i+seq_len])
            targets.append(y_vals[i+seq_len])
    return np.array(seqs), np.array(targets)

train_df = split_res['train_df']
test_df = split_res['test_df']
lstm_feats = [c for c in ALL_NUMERIC_COLS if c in train_df.columns]
s_lstm = StandardScaler()
train_df_s = train_df.copy()
test_df_s = test_df.copy()
train_df_s[lstm_feats] = s_lstm.fit_transform(train_df[lstm_feats])
test_df_s[lstm_feats] = s_lstm.transform(test_df[lstm_feats])

X_tr_seq, y_tr_seq = make_seqs(train_df_s, lstm_feats, seq_len)
X_te_seq, y_te_seq = make_seqs(test_df_s, lstm_feats, seq_len)

class PyTorchLSTM(nn.Module):
    def __init__(self, in_dim=7, h1=64, h2=32):
        super().__init__()
        self.lstm1 = nn.LSTM(in_dim, h1, batch_first=True)
        self.drop1 = nn.Dropout(0.2)
        self.lstm2 = nn.LSTM(h1, h2, batch_first=True)
        self.drop2 = nn.Dropout(0.2)
        self.fc = nn.Sequential(nn.Linear(h2, 16), nn.ReLU(), nn.Linear(16, 1))
    def forward(self, x):
        o1, _ = self.lstm1(x)
        o1 = self.drop1(o1)
        o2, _ = self.lstm2(o1)
        o2 = self.drop2(o2[:, -1, :])
        return self.fc(o2).squeeze(-1)

lstm_net = PyTorchLSTM(len(lstm_feats), 64, 32)
opt_lstm = torch.optim.Adam(lstm_net.parameters(), lr=0.003)
loss_fn = nn.MSELoss()

l_loader = DataLoader(TensorDataset(torch.tensor(X_tr_seq), torch.tensor(y_tr_seq)), batch_size=64, shuffle=True)
lstm_net.train()
for ep in range(15):
    for bx, by in l_loader:
        opt_lstm.zero_grad()
        out = lstm_net(bx)
        l = loss_fn(out, by)
        l.backward()
        opt_lstm.step()

lstm_net.eval()
with torch.no_grad():
    p_lstm = lstm_net(torch.tensor(X_te_seq)).numpy()

results.append(calc_metrics(y_te_seq, p_lstm, 'Ablation: Standalone LSTM (7-day sequence)'))

# Compare Dual vs Tri Ensemble on aligned samples
min_len = min(len(p_rf), len(p_xgb), len(p_lstm))
y_aligned = y_te.values[-min_len:]
rf_aligned = p_rf[-min_len:]
xgb_aligned = p_xgb[-min_len:]
lstm_aligned = p_lstm[-min_len:]

p_dual_aligned = (rf_aligned + xgb_aligned) / 2.0
p_tri_aligned = (rf_aligned + xgb_aligned + lstm_aligned) / 3.0

results.append(calc_metrics(y_aligned, p_tri_aligned, 'Ablation: Tri-Ensemble (RF + XGBoost + LSTM [Equal Avg])'))
results.append(calc_metrics(y_aligned, p_dual_aligned, 'Ensemble Comparison: RF + XGBoost (Aligned Test Samples)'))

print('\n' + '=' * 105)
print(f'{"Configuration / Model":<55} | {"RMSE":<7} | {"MAE":<7} | {"R2":<7} | {"MAPE":<8} | {"Acc(%)":<7}')
print('-' * 105)
for r in results:
    print(f'{r["model"]:<55} | {r["RMSE"]:<7.2f} | {r["MAE"]:<7.2f} | {r["R2"]:<7.4f} | {r["MAPE"]:<8.2f} | {r["Accuracy"]:<7.2f}')
print('=' * 105)

# Significance test between Dual Ensemble and best single model
w_stat, w_p = stats.wilcoxon(np.abs(y_aligned - p_dual_aligned), np.abs(y_aligned - xgb_aligned))
t_stat, t_p = stats.ttest_rel(np.abs(y_aligned - p_dual_aligned), np.abs(y_aligned - xgb_aligned))
print(f'\n[Significance Tests: Dual Ensemble vs Best Single (XGBoost)]')
print(f'  Wilcoxon signed-rank test: W = {w_stat:.1f}, p = {w_p:.4e} (p < 0.01: {w_p < 0.01})')
print(f'  Paired Student t-test:     t = {t_stat:.2f}, p = {t_p:.4e} (p < 0.05: {t_p < 0.05})')
