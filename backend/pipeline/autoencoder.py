"""
autoencoder.py
──────────────
MI-MMA (Multimodal Imputation - Multi-Modal Autoencoder) architecture.

Three autoencoders — one per imputed variant (KNN_AE, MICE_AE, SVD_AE) —
each with a bottleneck of 12 dims. Concatenate the three bottleneck
representations into one fused 36-dim feature vector.
"""

import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

from .data_ingestion import ALL_NUMERIC_COLS

# ── Constants ────────────────────────────────────────────────────────
BOTTLENECK_DIM = 12
HIDDEN_DIM = 32
EPOCHS = 100
BATCH_SIZE = 32
RANDOM_SEED = 42

# Feature columns for the autoencoders (AQI + 6 pollutants = 7)
AE_FEATURE_COLS = ALL_NUMERIC_COLS  # ['AQI', 'PM2.5', 'PM10', 'NO2', 'SO2', 'CO', 'O3']


def _build_autoencoder(input_dim: int, hidden_dim: int = HIDDEN_DIM,
                       bottleneck_dim: int = BOTTLENECK_DIM):
    """
    Build a simple symmetric autoencoder.
    Architecture: input_dim → hidden_dim → bottleneck_dim → hidden_dim → input_dim
    """
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers

    tf.random.set_seed(RANDOM_SEED)

    # Encoder
    encoder_input = keras.Input(shape=(input_dim,), name="encoder_input")
    x = layers.Dense(hidden_dim, activation="relu", name="enc_hidden")(encoder_input)
    x = layers.BatchNormalization(name="enc_bn")(x)
    bottleneck = layers.Dense(bottleneck_dim, activation="relu", name="bottleneck")(x)

    # Decoder
    x = layers.Dense(hidden_dim, activation="relu", name="dec_hidden")(bottleneck)
    x = layers.BatchNormalization(name="dec_bn")(x)
    decoder_output = layers.Dense(input_dim, activation="linear", name="decoder_output")(x)

    # Full autoencoder
    autoencoder = keras.Model(encoder_input, decoder_output, name="autoencoder")
    autoencoder.compile(optimizer="adam", loss="mse")

    # Encoder-only model (for extracting bottleneck features)
    encoder = keras.Model(encoder_input, bottleneck, name="encoder")

    return autoencoder, encoder


def train_autoencoder(data: pd.DataFrame, name: str,
                      epochs: int = EPOCHS, batch_size: int = BATCH_SIZE,
                      verbose: int = 0) -> tuple:
    """
    Train a single autoencoder on the given data.

    Returns
    -------
    autoencoder : trained autoencoder model
    encoder : encoder-only model for feature extraction
    scaler : fitted StandardScaler
    recon_mse : reconstruction MSE on the data
    """
    import tensorflow as tf

    cols = [c for c in AE_FEATURE_COLS if c in data.columns]
    X = data[cols].values.astype(np.float32)

    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Build and train
    autoencoder, encoder = _build_autoencoder(input_dim=len(cols))

    # Early stopping
    early_stop = tf.keras.callbacks.EarlyStopping(
        monitor="val_loss", patience=10, restore_best_weights=True
    )

    print(f"  🧠 Training {name} autoencoder ({len(cols)} → {BOTTLENECK_DIM} → {len(cols)})...")
    autoencoder.fit(
        X_scaled, X_scaled,
        epochs=epochs,
        batch_size=batch_size,
        validation_split=0.15,
        callbacks=[early_stop],
        verbose=verbose,
    )

    # Compute reconstruction MSE
    X_reconstructed = autoencoder.predict(X_scaled, verbose=0)
    recon_mse = float(np.mean((X_scaled - X_reconstructed) ** 2))
    print(f"  📊 {name} reconstruction MSE: {recon_mse:.6f}")

    return autoencoder, encoder, scaler, recon_mse


def build_fused_features(imputation_results: dict, data: pd.DataFrame) -> dict:
    """
    Build MI-MMA fused features:
    1. Train 3 autoencoders (KNN_AE, MICE_AE, SVD_AE)
    2. Extract bottleneck representations from each
    3. Concatenate into a 36-dim fused feature vector

    Parameters
    ----------
    imputation_results : dict with keys 'KNN_D', 'MICE_D', 'SVD_D'
    data : original clean data (for reference indices)

    Returns
    -------
    dict with:
        'fused_features' : np.ndarray of shape (n_samples, 36)
        'autoencoders' : dict of trained autoencoder models
        'encoders' : dict of encoder-only models
        'scalers' : dict of fitted scalers
        'reconstruction_mse' : dict of MSE per variant
    """
    print("\n" + "=" * 60)
    print("  MI-MMA AUTOENCODER PIPELINE")
    print("=" * 60)

    variants = {
        "KNN_AE": imputation_results["KNN_D"],
        "MICE_AE": imputation_results["MICE_D"],
        "SVD_AE": imputation_results["SVD_D"],
    }

    autoencoders = {}
    encoders = {}
    scalers = {}
    recon_mse = {}
    bottleneck_features = []

    for name, variant_data in variants.items():
        ae, enc, scaler, mse = train_autoencoder(variant_data, name)
        autoencoders[name] = ae
        encoders[name] = enc
        scalers[name] = scaler
        recon_mse[name] = round(mse, 6)

        # Extract bottleneck features
        cols = [c for c in AE_FEATURE_COLS if c in variant_data.columns]
        X = variant_data[cols].values.astype(np.float32)
        X_scaled = scaler.transform(X)
        features = enc.predict(X_scaled, verbose=0)
        bottleneck_features.append(features)

    # Concatenate all bottleneck features → fused vector
    fused = np.hstack(bottleneck_features)
    print(f"\n✅ Fused feature vector shape: {fused.shape} "
          f"({len(variants)} × {BOTTLENECK_DIM} = {fused.shape[1]} dims)")
    print(f"📊 Reconstruction MSE per autoencoder: {recon_mse}")

    return {
        "fused_features": fused,
        "autoencoders": autoencoders,
        "encoders": encoders,
        "scalers": scalers,
        "reconstruction_mse": recon_mse,
    }


if __name__ == "__main__":
    from .data_ingestion import load_and_merge
    from .imputation import run_imputation

    data = load_and_merge()
    imp_results = run_imputation(data)
    ae_results = build_fused_features(imp_results, data)
    print(f"\n✅ Autoencoder pipeline complete. Fused shape: {ae_results['fused_features'].shape}")
