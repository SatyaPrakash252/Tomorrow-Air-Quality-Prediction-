"""
imputation.py
─────────────
Three-method multimodal imputation: KNN, MICE, SVD.

Since the real dataset has almost no missing values, we synthetically mask
~5-10% of pollutant values (seeded, documented) to demonstrate and evaluate
the methods against known ground truth.
"""

import numpy as np
import pandas as pd
from sklearn.impute import KNNImputer
from sklearn.experimental import enable_iterative_imputer  # noqa: F401
from sklearn.impute import IterativeImputer
from sklearn.metrics import mean_squared_error

from .data_ingestion import POLLUTANTS

# ── Constants ────────────────────────────────────────────────────────
MASK_FRACTION = 0.07  # ~7% of values masked
RANDOM_SEED = 42
SVD_RANK = 4          # truncated SVD rank
SVD_MAX_ITER = 30     # convergence iterations


def _create_synthetic_mask(data: pd.DataFrame, cols: list[str],
                           fraction: float = MASK_FRACTION,
                           seed: int = RANDOM_SEED) -> tuple[pd.DataFrame, pd.DataFrame, np.ndarray]:
    """
    Create a synthetic mask on pollutant columns.

    Returns
    -------
    masked_data : DataFrame with NaN injected
    ground_truth : original values (clean copy)
    mask : boolean array (True = was masked)
    """
    rng = np.random.RandomState(seed)
    ground_truth = data[cols].copy()
    masked_data = data.copy()

    n_total = ground_truth.shape[0] * ground_truth.shape[1]
    n_mask = int(n_total * fraction)

    # Build flat indices to mask
    flat_indices = rng.choice(n_total, size=n_mask, replace=False)
    row_idx = flat_indices // len(cols)
    col_idx = flat_indices % len(cols)

    mask = np.zeros(ground_truth.shape, dtype=bool)
    for r, c in zip(row_idx, col_idx):
        mask[r, c] = True
        masked_data.iloc[r, masked_data.columns.get_loc(cols[c])] = np.nan

    total_missing = mask.sum()
    pct = total_missing / n_total * 100
    print(f"🎭 Synthetic masking: {total_missing:,} values masked ({pct:.1f}%) across {len(cols)} pollutant columns")

    return masked_data, ground_truth, mask


def _impute_knn(data: pd.DataFrame, cols: list[str], n_neighbors: int = 5) -> pd.DataFrame:
    """KNN imputation using sklearn's KNNImputer."""
    print("  🔧 KNN Imputation (k={})...".format(n_neighbors))
    imputer = KNNImputer(n_neighbors=n_neighbors)
    result = data.copy()
    result[cols] = imputer.fit_transform(result[cols])
    return result


def _impute_mice(data: pd.DataFrame, cols: list[str],
                 max_iter: int = 10, seed: int = RANDOM_SEED) -> pd.DataFrame:
    """MICE (Multivariate Imputation by Chained Equations) via IterativeImputer."""
    print(f"  🔧 MICE Imputation (max_iter={max_iter})...")
    imputer = IterativeImputer(max_iter=max_iter, random_state=seed, sample_posterior=False)
    result = data.copy()
    result[cols] = imputer.fit_transform(result[cols])
    return result


def _impute_svd(data: pd.DataFrame, cols: list[str],
                rank: int = SVD_RANK, max_iter: int = SVD_MAX_ITER) -> pd.DataFrame:
    """
    SVD-based imputation via truncated SVD reconstruction loop.

    Algorithm:
    1. Fill NaN with column means
    2. Iterate:
       a. SVD decompose the matrix
       b. Truncate to rank k
       c. Reconstruct
       d. Replace only originally-missing positions
    3. Converge after max_iter iterations
    """
    print(f"  🔧 SVD Imputation (rank={rank}, max_iter={max_iter})...")
    result = data.copy()
    matrix = result[cols].values.astype(float)
    missing_mask = np.isnan(matrix)

    # Step 1: Fill NaN with column means
    col_means = np.nanmean(matrix, axis=0)
    for j in range(matrix.shape[1]):
        matrix[missing_mask[:, j], j] = col_means[j]

    # Step 2: Iterative SVD reconstruction
    prev_matrix = matrix.copy()
    for iteration in range(max_iter):
        U, S, Vt = np.linalg.svd(matrix, full_matrices=False)
        # Truncate to rank k
        S_trunc = np.zeros_like(S)
        S_trunc[:rank] = S[:rank]
        reconstructed = U @ np.diag(S_trunc) @ Vt

        # Only replace missing positions
        matrix[missing_mask] = reconstructed[missing_mask]

        # Check convergence
        diff = np.sqrt(np.mean((matrix - prev_matrix) ** 2))
        if diff < 1e-6:
            print(f"    → Converged at iteration {iteration + 1} (diff={diff:.2e})")
            break
        prev_matrix = matrix.copy()

    result[cols] = matrix
    return result


def _evaluate_imputation(imputed: pd.DataFrame, ground_truth: pd.DataFrame,
                         mask: np.ndarray, cols: list[str], method_name: str) -> dict:
    """Compute imputation RMSE per pollutant for masked positions."""
    results = {}
    for j, col in enumerate(cols):
        col_mask = mask[:, j]
        if col_mask.sum() == 0:
            results[col] = 0.0
            continue
        true_vals = ground_truth[col].values[col_mask]
        pred_vals = imputed[col].values[col_mask]
        rmse = np.sqrt(mean_squared_error(true_vals, pred_vals))
        results[col] = round(rmse, 4)

    avg_rmse = np.mean(list(results.values()))
    print(f"  📊 {method_name} RMSE per pollutant: {results}")
    print(f"     Average RMSE: {avg_rmse:.4f}")
    return results


def run_imputation(data: pd.DataFrame) -> dict:
    """
    Run all three imputation methods on synthetically masked data.

    Returns
    -------
    dict with keys:
        'KNN_D', 'MICE_D', 'SVD_D' : imputed DataFrames
        'imputation_rmse' : dict of {method: {pollutant: rmse}}
        'mask_info' : masking statistics
    """
    print("\n" + "=" * 60)
    print("  MULTIMODAL IMPUTATION PIPELINE")
    print("=" * 60)

    cols = [c for c in POLLUTANTS if c in data.columns]

    # Create synthetic mask
    masked_data, ground_truth, mask = _create_synthetic_mask(data, cols)

    # Run three imputation methods
    print("\n📌 Running imputation methods...")
    knn_data = _impute_knn(masked_data, cols)
    mice_data = _impute_mice(masked_data, cols)
    svd_data = _impute_svd(masked_data, cols)

    # Evaluate each method
    print("\n📊 Imputation Evaluation (RMSE against ground truth):")
    print("─" * 50)
    knn_rmse = _evaluate_imputation(knn_data, ground_truth, mask, cols, "KNN")
    mice_rmse = _evaluate_imputation(mice_data, ground_truth, mask, cols, "MICE")
    svd_rmse = _evaluate_imputation(svd_data, ground_truth, mask, cols, "SVD")

    return {
        "KNN_D": knn_data,
        "MICE_D": mice_data,
        "SVD_D": svd_data,
        "imputation_rmse": {
            "KNN": knn_rmse,
            "MICE": mice_rmse,
            "SVD": svd_rmse,
        },
        "mask_info": {
            "fraction": MASK_FRACTION,
            "total_masked": int(mask.sum()),
            "seed": RANDOM_SEED,
        },
    }


if __name__ == "__main__":
    from .data_ingestion import load_and_merge
    data = load_and_merge()
    results = run_imputation(data)
    print("\n✅ Imputation complete.")
    for key in ["KNN_D", "MICE_D", "SVD_D"]:
        print(f"  {key}: shape={results[key].shape}, nulls={results[key].isnull().sum().sum()}")
