"""
alerts.py
─────────
Alert engine: fires when a group's HRI crosses into HIGH or SEVERE
on the shared scale. Outputs structured alert objects.
"""

from datetime import datetime
from typing import Optional

from .hri import (
    VULNERABILITY_GROUPS,
    TIER_GUIDANCE,
    SAFETY_LIMITS,
)
import pandas as pd


def generate_alerts(data: pd.DataFrame, cutoffs: dict,
                    city_filter: Optional[str] = None,
                    group_filter: Optional[str] = None,
                    limit: int = 100) -> list[dict]:
    """
    Generate alert objects for all HIGH and SEVERE tier events.

    Parameters
    ----------
    data : DataFrame with HRI and Tier columns
    cutoffs : shared cutoff dict from HRI module
    city_filter : optional, filter alerts for a specific city
    group_filter : optional, filter alerts for a specific group
    limit : maximum number of alerts to return

    Returns
    -------
    list of alert dicts, most recent first
    """
    alerts = []

    # Filter by city if specified
    df = data.copy()
    if city_filter:
        df = df[df["City"] == city_filter]

    for group in VULNERABILITY_GROUPS:
        if group_filter and group != group_filter:
            continue

        tier_col = f"Tier_{group}"
        hri_col = f"HRI_{group}"

        if tier_col not in df.columns or hri_col not in df.columns:
            continue

        # Find HIGH and SEVERE events
        alert_mask = df[tier_col].isin(["HIGH", "SEVERE"])
        alert_rows = df[alert_mask]

        for _, row in alert_rows.iterrows():
            tier = row[tier_col]
            alert = {
                "city": row["City"],
                "date": row["Date"].strftime("%Y-%m-%d") if isinstance(row["Date"], datetime) else str(row["Date"]),
                "group": group,
                "tier": tier,
                "hri_value": round(float(row[hri_col]), 2),
                "recommendation": TIER_GUIDANCE.get(tier, ""),
                "vulnerability_factor": VULNERABILITY_GROUPS[group],
                "pollutant_breakdown": {
                    p: round(float(row.get(p, 0)), 2)
                    for p in SAFETY_LIMITS.keys()
                    if p in row.index
                },
            }
            alerts.append(alert)

    # Sort by date (most recent first), then by severity
    tier_priority = {"SEVERE": 0, "HIGH": 1}
    alerts.sort(key=lambda a: (a["date"], tier_priority.get(a["tier"], 2)), reverse=True)

    # Apply limit
    return alerts[:limit]


def get_alert_summary(alerts: list[dict]) -> dict:
    """Get a summary of alert statistics."""
    if not alerts:
        return {"total": 0, "severe": 0, "high": 0, "cities": [], "groups": []}

    severe = sum(1 for a in alerts if a["tier"] == "SEVERE")
    high = sum(1 for a in alerts if a["tier"] == "HIGH")
    cities = list(set(a["city"] for a in alerts))
    groups = list(set(a["group"] for a in alerts))

    return {
        "total": len(alerts),
        "severe": severe,
        "high": high,
        "cities": sorted(cities),
        "groups": sorted(groups),
    }


def print_alert_summary(alerts: list[dict]):
    """Print alert summary to console."""
    summary = get_alert_summary(alerts)
    print(f"\n🚨 Alert Summary:")
    print(f"   Total alerts     : {summary['total']}")
    print(f"   SEVERE           : {summary['severe']}")
    print(f"   HIGH             : {summary['high']}")
    print(f"   Cities affected  : {', '.join(summary['cities'])}")
    print(f"   Groups at risk   : {', '.join(summary['groups'])}")

    if alerts:
        print(f"\n   Latest 5 alerts:")
        for alert in alerts[:5]:
            print(f"     [{alert['tier']:7s}] {alert['date']} | "
                  f"{alert['city']:12s} | {alert['group']:25s} | "
                  f"HRI={alert['hri_value']:.1f}")
