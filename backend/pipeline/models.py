"""
models.py
─────────
Train Random Forest, XGBoost, and LSTM models with Optuna hyperparameter
tuning and walk-forward cross-validation. Build the final ensemble.
"""

import numpy as np
import pandas as pd
import optuna
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score, mean_absolute_percentage_error
from xgboost import XGBRegressor
import warnings

warnings.filterwarnings("ignore")
optuna.logging.set_verbosity(optuna.logging.WARNING)

# ── Constants ────────────────────────────────────────────────────────
N_OPTUNA_TRIALS = 30
N_CV_SPLITS = 5
RANDOM_SEED = 42


def evaluate_model(y_true, y_pred, name: str) -> dict:
    """Compute regression metrics for a model."""
    mape = mean_absolute_percentage_error(y_true, y_pred)
    acc = round(max(0, (1 - mape) * 100), 2)
    rmse = round(float(np.sqrt(mean_squared_error(y_true, y_pred))), 2)
    mae = round(float(mean_absolute_error(y_true, y_pred)), 2)
    r2 = round(float(r2_score(y_true, y_pred)), 4)

    print(f"  {name:20s}  Acc={acc:>6.2f}%  RMSE={rmse:>7.2f}  MAE={mae:>7.2f}  R²={r2:.4f}")
    return {
        "Model": name,
        "Accuracy(%)": acc,
        "RMSE": rmse,
        "MAE": mae,
        "R²": r2,
    }


def _tune_rf(X_train, y_train, n_trials: int = N_OPTUNA_TRIALS) -> dict:
    """Optuna hyperparameter tuning for Random Forest with walk-forward CV."""
    tscv = TimeSeriesSplit(n_splits=N_CV_SPLITS)

    def objective(trial):
        params = {
            "n_estimators": trial.suggest_int("n_estimators", 100, 500, step=50),
            "max_depth": trial.suggest_int("max_depth", 5, 30),
            "min_samples_split": trial.suggest_int("min_samples_split", 2, 20),
            "min_samples_leaf": trial.suggest_int("min_samples_leaf", 1, 10),
            "max_features": trial.suggest_categorical("max_features", ["sqrt", "log2", None]),
        }
        scores = []
        for train_idx, val_idx in tscv.split(X_train):
            X_tr, X_val = X_train.iloc[train_idx], X_train.iloc[val_idx]
            y_tr, y_val = y_train.iloc[train_idx], y_train.iloc[val_idx]

            model = RandomForestRegressor(**params, random_state=RANDOM_SEED, n_jobs=-1)
            model.fit(X_tr, y_tr)
            pred = model.predict(X_val)
            scores.append(np.sqrt(mean_squared_error(y_val, pred)))

        return np.mean(scores)

    study = optuna.create_study(direction="minimize",
                                sampler=optuna.samplers.TPESampler(seed=RANDOM_SEED))
    study.optimize(objective, n_trials=n_trials, show_progress_bar=False)

    print(f"  🏆 Best RF params: {study.best_params}")
    print(f"     Best CV RMSE: {study.best_value:.2f}")
    return study.best_params


def _tune_xgb(X_train, y_train, n_trials: int = N_OPTUNA_TRIALS) -> dict:
    """Optuna hyperparameter tuning for XGBoost with walk-forward CV."""
    tscv = TimeSeriesSplit(n_splits=N_CV_SPLITS)

    def objective(trial):
        params = {
            "n_estimators": trial.suggest_int("n_estimators", 100, 500, step=50),
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
            "max_depth": trial.suggest_int("max_depth", 3, 12),
            "subsample": trial.suggest_float("subsample", 0.6, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
            "reg_alpha": trial.suggest_float("reg_alpha", 1e-8, 10.0, log=True),
            "reg_lambda": trial.suggest_float("reg_lambda", 1e-8, 10.0, log=True),
        }
        scores = []
        for train_idx, val_idx in tscv.split(X_train):
            X_tr, X_val = X_train.iloc[train_idx], X_train.iloc[val_idx]
            y_tr, y_val = y_train.iloc[train_idx], y_train.iloc[val_idx]

            model = XGBRegressor(**params, random_state=RANDOM_SEED, n_jobs=-1, verbosity=0)
            model.fit(X_tr, y_tr, verbose=False)
            pred = model.predict(X_val)
            scores.append(np.sqrt(mean_squared_error(y_val, pred)))

        return np.mean(scores)

    study = optuna.create_study(direction="minimize",
                                sampler=optuna.samplers.TPESampler(seed=RANDOM_SEED))
    study.optimize(objective, n_trials=n_trials, show_progress_bar=False)

    print(f"  🏆 Best XGBoost params: {study.best_params}")
    print(f"     Best CV RMSE: {study.best_value:.2f}")
    return study.best_params


def train_rf(X_train, y_train, X_test, tune: bool = True) -> tuple:
    """Train Random Forest with optional Optuna tuning."""
    print("\n🌲 Random Forest")
    print("─" * 40)

    if tune:
        best_params = _tune_rf(X_train, y_train)
    else:
        best_params = {"n_estimators": 200, "max_depth": None}

    model = RandomForestRegressor(**best_params, random_state=RANDOM_SEED, n_jobs=-1)
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)

    # Feature importance
    importances = pd.Series(model.feature_importances_, index=X_train.columns)
    importances = importances.sort_values(ascending=False)

    print(f"  ✅ Trained with {best_params.get('n_estimators', 200)} trees")

    return model, predictions, importances, best_params


def train_xgboost(X_train, y_train, X_test, tune: bool = True) -> tuple:
    """Train XGBoost with optional Optuna tuning."""
    print("\n🚀 XGBoost")
    print("─" * 40)

    if tune:
        best_params = _tune_xgb(X_train, y_train)
    else:
        best_params = {"n_estimators": 200, "learning_rate": 0.1, "max_depth": 6}

    model = XGBRegressor(**best_params, random_state=RANDOM_SEED, n_jobs=-1, verbosity=0)
    model.fit(X_train, y_train, verbose=False)
    predictions = model.predict(X_test)

    # Feature importance
    importances = pd.Series(model.feature_importances_, index=X_train.columns)
    importances = importances.sort_values(ascending=False)

    print(f"  ✅ Trained with {best_params.get('n_estimators', 200)} rounds")

    return model, predictions, importances, best_params


def train_lstm(lstm_data: dict) -> tuple:
    """
    Train LSTM model on raw sequence data.

    Architecture: LSTM(64) → Dropout(0.2) → LSTM(32) → Dense(16) → Dense(1)
    """
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers

    print("\n🧠 LSTM")
    print("─" * 40)

    tf.random.set_seed(RANDOM_SEED)

    X_train = lstm_data["X_train_seq"]
    y_train = lstm_data["y_train_seq"]
    X_test = lstm_data["X_test_seq"]
    y_test = lstm_data["y_test_seq"]

    n_timesteps = X_train.shape[1]
    n_features = X_train.shape[2]

    # Scale sequences
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()

    # Reshape for scaling: (samples * timesteps, features)
    X_train_flat = X_train.reshape(-1, n_features)
    X_test_flat = X_test.reshape(-1, n_features)

    scaler.fit(X_train_flat)
    X_train_scaled = scaler.transform(X_train_flat).reshape(X_train.shape)
    X_test_scaled = scaler.transform(X_test_flat).reshape(X_test.shape)

    # Build LSTM model
    model = keras.Sequential([
        layers.LSTM(64, return_sequences=True, input_shape=(n_timesteps, n_features)),
        layers.Dropout(0.2),
        layers.LSTM(32, return_sequences=False),
        layers.Dropout(0.2),
        layers.Dense(16, activation="relu"),
        layers.Dense(1),
    ], name="lstm_forecaster")

    model.compile(optimizer=keras.optimizers.Adam(learning_rate=0.001), loss="mse")

    # Callbacks
    early_stop = keras.callbacks.EarlyStopping(
        monitor="val_loss", patience=15, restore_best_weights=True
    )
    reduce_lr = keras.callbacks.ReduceLROnPlateau(
        monitor="val_loss", factor=0.5, patience=5, min_lr=1e-6
    )

    print(f"  Training LSTM ({n_timesteps} steps × {n_features} features)...")
    model.fit(
        X_train_scaled, y_train,
        epochs=100,
        batch_size=32,
        validation_split=0.15,
        callbacks=[early_stop, reduce_lr],
        verbose=0,
    )

    predictions = model.predict(X_test_scaled, verbose=0).flatten()
    print(f"  ✅ LSTM trained")

    return model, predictions, scaler


def build_ensemble(rf_pred, xgb_pred, lstm_pred, y_test) -> tuple:
    """Build ensemble by averaging all three model predictions."""
    print("\n🎯 Ensemble (Average)")
    print("─" * 40)

    # Align predictions — LSTM may have fewer samples due to sequence creation
    min_len = min(len(rf_pred), len(xgb_pred), len(lstm_pred))

    rf_aligned = rf_pred[-min_len:]
    xgb_aligned = xgb_pred[-min_len:]
    lstm_aligned = lstm_pred[-min_len:]
    y_aligned = y_test[-min_len:] if hasattr(y_test, '__len__') else y_test.values[-min_len:]

    ensemble_pred = (rf_aligned + xgb_aligned + lstm_aligned) / 3

    print(f"  ✅ Ensemble created (avg of 3 models, {min_len} aligned samples)")

    return ensemble_pred, y_aligned


def train_all_models(split_data: dict, lstm_data: dict, tune: bool = True) -> dict:
    """
    Train all models and build ensemble.

    Returns
    -------
    dict with all models, predictions, metrics, and importances.
    """
    print("\n" + "=" * 60)
    print("  MODEL TRAINING PIPELINE")
    print("=" * 60)

    X_train = split_data["X_train"]
    y_train = split_data["y_train"]
    X_test = split_data["X_test"]
    y_test = split_data["y_test"]

    # Train individual models
    rf_model, rf_pred, rf_imp, rf_params = train_rf(X_train, y_train, X_test, tune=tune)
    xgb_model, xgb_pred, xgb_imp, xgb_params = train_xgboost(X_train, y_train, X_test, tune=tune)
    lstm_model, lstm_pred, lstm_scaler = train_lstm(lstm_data)

    # Build ensemble
    ens_pred, y_aligned = build_ensemble(rf_pred, xgb_pred, lstm_pred, y_test)

    # Evaluate all models
    print("\n" + "=" * 60)
    print("  MODEL EVALUATION")
    print("=" * 60)

    metrics = []
    metrics.append(evaluate_model(y_test, rf_pred, "Random Forest"))
    metrics.append(evaluate_model(y_test, xgb_pred, "XGBoost"))

    # LSTM evaluation — align with its own test set
    lstm_y_test = lstm_data["y_test_seq"]
    metrics.append(evaluate_model(lstm_y_test, lstm_pred, "LSTM"))

    metrics.append(evaluate_model(y_aligned, ens_pred, "Ensemble (Avg)"))

    metrics_df = pd.DataFrame(metrics)
    best = metrics_df.loc[metrics_df["R²"].idxmax()]

    print(f"\n🏆 Best model: {best['Model']}  "
          f"(Acc={best['Accuracy(%)']}%, R²={best['R²']}, RMSE={best['RMSE']})")

    return {
        "models": {
            "rf": rf_model,
            "xgboost": xgb_model,
            "lstm": lstm_model,
        },
        "predictions": {
            "rf": rf_pred,
            "xgboost": xgb_pred,
            "lstm": lstm_pred,
            "ensemble": ens_pred,
        },
        "metrics": metrics,
        "metrics_df": metrics_df,
        "best_model": best.to_dict(),
        "feature_importances": {
            "rf": rf_imp,
            "xgboost": xgb_imp,
        },
        "hyperparameters": {
            "rf": rf_params,
            "xgboost": xgb_params,
        },
        "lstm_scaler": lstm_scaler,
        "y_test": y_test,
        "y_test_aligned": y_aligned,
    }
