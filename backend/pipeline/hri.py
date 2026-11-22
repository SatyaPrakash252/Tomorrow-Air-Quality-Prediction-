"""
hri.py
──────
Health Risk Index (HRI) module.

Formula (adapted from Kashyap et al., 2025):
    HRI = Σ (pollutant_concentration / CPCB_safety_limit) × vulnerability_factor

Tier cutoffs use the General Public's own quartiles (P25/P75/P90)
as a SHARED baseline scale for ALL groups. This ensures the vulnerability
multiplier has real effect on tier assignment.
"""

import numpy as np
import pandas as pd

from .data_ingestion import POLLUTANTS

# ── CPCB Safety Limits ("Good" category upper bounds) ────────────────
SAFETY_LIMITS = {
    "PM2.5": 30.0,   # µg/m³
    "PM10": 50.0,    # µg/m³
    "NO2": 40.0,     # µg/m³
    "SO2": 40.0,     # µg/m³
    "CO": 1.0,       # mg/m³
    "O3": 50.0,      # µg/m³
}

# ── Vulnerability Multipliers ────────────────────────────────────────
VULNERABILITY_GROUPS = {
    "General Public": 1.0,
    "Children/Elderly": 1.3,
    "Respiratory Patients": 1.6,
}

# ── Tier Labels ──────────────────────────────────────────────────────
TIER_ORDER = ["LOW", "MODERATE", "HIGH", "SEVERE"]

# ── Plain-language guidance per tier ─────────────────────────────────
TIER_GUIDANCE = {
    "LOW": "Air quality is acceptable. Enjoy outdoor activities normally.",
    "MODERATE": "Sensitive groups should consider reducing prolonged outdoor exertion.",
    "HIGH": "Limit outdoor activities. Wear N95 masks if going outside. Keep windows closed.",
    "SEVERE": "Avoid ALL outdoor exposure. Keep windows sealed. Use air purifiers indoors. Seek medical help if symptomatic.",
}


def compute_base_hri(data: pd.DataFrame) -> pd.Series:
    """
    Compute the base HRI (unweighted by vulnerability) for each row.
    HRI_base = Σ (pollutant / safety_limit)
    """
    hri = pd.Series(0.0, index=data.index)
    for pollutant, limit in SAFETY_LIMITS.items():
        if pollutant in data.columns:
            hri += data[pollutant] / limit
    return hri


def compute_hri_for_groups(data: pd.DataFrame) -> pd.DataFrame:
    """
    Compute HRI for all vulnerability groups and assign tiers.

    IMPORTANT: Tier cutoffs are computed from the General Public's HRI ONLY,
    then applied as a SHARED baseline to ALL groups. This prevents the
    multiplier from being cancelled out by group-specific percentile scaling.
    """
    result = data.copy()

    # Base HRI
    result["HRI_base"] = compute_base_hri(result)

    # Apply vulnerability multipliers
    for group, factor in VULNERABILITY_GROUPS.items():
        result[f"HRI_{group}"] = result["HRI_base"] * factor

    # Compute shared cutoffs from General Public ONLY
    gp_hri = result["HRI_General Public"]
    cutoffs = {
        "p25": float(gp_hri.quantile(0.25)),
        "p75": float(gp_hri.quantile(0.75)),
        "p90": float(gp_hri.quantile(0.90)),
    }

    # Tier assignment function using SHARED cutoffs
    def assign_tier(val):
        if val <= cutoffs["p25"]:
            return "LOW"
        elif val <= cutoffs["p75"]:
            return "MODERATE"
        elif val <= cutoffs["p90"]:
            return "HIGH"
        else:
            return "SEVERE"

    # Assign tiers to ALL groups using the SAME shared cutoffs
    for group in VULNERABILITY_GROUPS:
        result[f"Tier_{group}"] = result[f"HRI_{group}"].apply(assign_tier)

    return result, cutoffs


def get_tier_distributions(data: pd.DataFrame) -> dict:
    """Get tier distribution percentages per group."""
    distributions = {}
    for group in VULNERABILITY_GROUPS:
        tier_col = f"Tier_{group}"
        if tier_col in data.columns:
            dist = data[tier_col].value_counts(normalize=True)
            dist = dist.reindex(TIER_ORDER, fill_value=0) * 100
            distributions[group] = {tier: round(v, 1) for tier, v in dist.items()}
    return distributions


def get_high_severe_rates(data: pd.DataFrame) -> dict:
    """Get HIGH + SEVERE alert rates per group."""
    rates = {}
    for group in VULNERABILITY_GROUPS:
        tier_col = f"Tier_{group}"
        if tier_col in data.columns:
            hs = data[tier_col].isin(["HIGH", "SEVERE"]).mean() * 100
            rates[group] = round(hs, 1)
    return rates


def compute_hri_for_single_day(pollutant_values: dict) -> dict:
    """
    Compute HRI for a single day's pollutant values.
    Returns HRI and tier per group.

    Parameters
    ----------
    pollutant_values : dict like {'PM2.5': 60, 'PM10': 120, ...}
    """
    base_hri = sum(pollutant_values.get(p, 0) / limit
                   for p, limit in SAFETY_LIMITS.items())

    results = {}
    for group, factor in VULNERABILITY_GROUPS.items():
        hri = base_hri * factor
        results[group] = {
            "hri_value": round(hri, 2),
            "factor": factor,
        }

    return results


def print_hri_summary(data: pd.DataFrame, cutoffs: dict):
    """Print a summary of HRI tier distributions."""
    print("\n📊 Health Risk Tier Distribution:")
    print(f"   Cutoffs (from General Public): "
          f"LOW ≤ {cutoffs['p25']:.2f} | "
          f"MODERATE ≤ {cutoffs['p75']:.2f} | "
          f"HIGH ≤ {cutoffs['p90']:.2f}")
    print("─" * 58)

    for group, factor in VULNERABILITY_GROUPS.items():
        tier_col = f"Tier_{group}"
        dist = data[tier_col].value_counts(normalize=True)
        dist = dist.reindex(TIER_ORDER, fill_value=0) * 100
        print(f"\n  {group}  (×{factor}):")
        for tier in TIER_ORDER:
            bar = "█" * int(dist[tier] / 2)
            print(f"    {tier:10s} {dist[tier]:5.1f}%  {bar}")

    # Print HIGH+SEVERE rates
    print("\n  ⚠️ HIGH + SEVERE alert rates:")
    rates = get_high_severe_rates(data)
    for group, rate in rates.items():
        print(f"    {group:25s} → {rate:.1f}%")


if __name__ == "__main__":
    from .data_ingestion import load_and_merge
    data = load_and_merge()
    result, cutoffs = compute_hri_for_groups(data)
    print_hri_summary(result, cutoffs)
