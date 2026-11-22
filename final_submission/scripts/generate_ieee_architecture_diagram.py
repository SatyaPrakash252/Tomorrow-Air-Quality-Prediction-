"""
generate_ieee_architecture_diagram.py
──────────────────────────────────────
Compact, high-contrast, publication-grade IEEE conference architecture diagram.
Designed specifically for single-column (3.10 in) IEEE layout:
- Aspect ratio ~ 1.55 : 1 (width 7.2 in, height 4.6 in)
- Scaling height: ~2.0 inches (preserves exact 5-page conference limit)
- Crystal-clear typography with bold headers and high contrast
- Zero microscopic paragraphs, zero fuzzy AI graphics
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT_PATH = r"D:\MP RERVIEW 1\final_submission\report_assets\fig_3_1_architecture.png"

def create_compact_ieee_architecture():
    # 7.2 x 4.65 inches canvas -> aspect ratio 1.55 (height in Word ~2.0 in)
    fig, ax = plt.subplots(figsize=(7.2, 4.65), dpi=300)
    ax.set_xlim(0, 7.2)
    ax.set_ylim(0, 4.65)
    ax.axis('off')

    c_title = '#0F172A'       # Slate 900
    c_text = '#1E293B'        # Slate 800
    c_arrow = '#475569'       # Slate 600

    stages = [
        {
            "tag": "STAGE 1",
            "name": "Data Ingestion & Quality Control",
            "line1": r"• CAAQMS Telemetry: 12,042 days $\mathrm{PM}_{2.5}, \mathrm{PM}_{10}, \mathrm{NO}_2, \mathrm{SO}_2, \mathrm{CO}, \mathrm{O}_3$",
            "line2": r"• ERA5 Weather Reanalysis | QA: [0, 1000] $\mu\mathrm{g/m}^3$ bounds, zero leakage",
            "border": "#2563EB",  # Blue
            "fill": "#F0F7FF",
            "badge_bg": "#DBEAFE",
            "badge_txt": "#1E40AF",
            "y": 3.75,
            "h": 0.78
        },
        {
            "tag": "STAGE 2",
            "name": "MICE Imputation & Latent Autoencoding (MI-MMA)",
            "line1": r"• MICE Chained Equations: Sensor dropouts ($\mathbf{RMSE = 0.0061}$ vs KNN 0.6975)",
            "line2": r"• Symmetrical Autoencoder: $7 \to 32 \to 12 \to 32 \to 7$ | 36-dim Fused Latent Manifold",
            "border": "#059669",  # Emerald
            "fill": "#F0FDF4",
            "badge_bg": "#D1FAE5",
            "badge_txt": "#065F46",
            "y": 2.82,
            "h": 0.78
        },
        {
            "tag": "STAGE 3",
            "name": "Optuna-Tuned Dual Stacking Forecasting Engine",
            "line1": r"• Base: XGBoost + CatBoost + Random Forest | Meta: Non-Negative Ridge",
            "line2": r"• SOTA Accuracy: $\mathbf{R^2 = 0.9248,\ RMSE = 13.84}$ | 90% Quantile PICP = 90.01%",
            "border": "#4F46E5",  # Indigo
            "fill": "#EEF2FF",
            "badge_bg": "#E0E7FF",
            "badge_txt": "#3730A3",
            "y": 1.89,
            "h": 0.78
        },
        {
            "tag": "STAGE 4",
            "name": "Multi-Pollutant Health Risk Engine (HRI)",
            "line1": r"• Epidemiological Index: $\mathrm{HRI}_g = \beta_g \sum_{p} (C_p / S_p)^{\gamma_p}$ (NAAQS Anchored)",
            "line2": r"• Demographic Multipliers: General ($1.0\times$) | Elderly ($1.3\times$) | Respiratory ($1.6\times$)",
            "border": "#D97706",  # Amber
            "fill": "#FFFBEB",
            "badge_bg": "#FEF3C7",
            "badge_txt": "#92400E",
            "y": 0.96,
            "h": 0.78
        },
        {
            "tag": "STAGE 5",
            "name": "Explainability & Public Health Alert Dispatch",
            "line1": r"• TreeSHAP Attribution: Game-theoretic global and local feature importance",
            "line2": r"• Production Delivery: Async FastAPI Microservice ($\mathbf{2.41\ ms}$ Latency) & Triage Alerts",
            "border": "#0D9488",  # Teal
            "fill": "#F0FDFA",
            "badge_bg": "#CCFBF1",
            "badge_txt": "#115E59",
            "y": 0.03,
            "h": 0.78
        }
    ]

    box_w = 6.8
    box_x = 0.2

    for s in stages:
        # Card outline
        card = FancyBboxPatch(
            (box_x, s["y"]), box_w, s["h"],
            boxstyle="round,pad=0.02,rounding_size=0.08",
            facecolor=s["fill"], edgecolor=s["border"], linewidth=1.4
        )
        ax.add_patch(card)

        # Stage Tag Pill
        pill = FancyBboxPatch(
            (box_x + 0.10, s["y"] + s["h"] - 0.23), 0.95, 0.18,
            boxstyle="round,pad=0.015,rounding_size=0.05",
            facecolor=s["badge_bg"], edgecolor=s["border"], linewidth=0.8
        )
        ax.add_patch(pill)
        ax.text(box_x + 0.575, s["y"] + s["h"] - 0.14, s["tag"],
                fontsize=7.8, fontweight='bold', color=s["badge_txt"], ha='center', va='center')

        # Stage Title
        ax.text(box_x + 1.15, s["y"] + s["h"] - 0.14, s["name"],
                fontsize=9.2, fontweight='bold', color=c_title, va='center')

        # Content Line 1 & Line 2 (Crisp & High Contrast)
        ax.text(box_x + 0.15, s["y"] + 0.33, s["line1"],
                fontsize=8.1, color=c_text, va='center')
        ax.text(box_x + 0.15, s["y"] + 0.12, s["line2"],
                fontsize=8.1, color=c_text, va='center')

    # Connecting Arrows
    for i in range(len(stages) - 1):
        s_curr = stages[i]
        s_next = stages[i+1]
        mid_x = box_x + box_w / 2.0
        arrow = FancyArrowPatch(
            (mid_x, s_curr["y"]), (mid_x, s_next["y"] + s_next["h"]),
            arrowstyle='-|>,head_width=2.5,head_length=3.5',
            color=c_arrow, linewidth=1.3
        )
        ax.add_patch(arrow)

    plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    fig.savefig(OUT_PATH, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close(fig)
    print(f"Generated compact IEEE architecture diagram -> {OUT_PATH}")

if __name__ == "__main__":
    create_compact_ieee_architecture()
