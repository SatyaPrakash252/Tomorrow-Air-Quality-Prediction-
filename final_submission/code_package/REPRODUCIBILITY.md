# VayuDrishti: Master Reproducibility & Audit Protocol

This document establishes the exact protocol to independently reproduce every table, metric, and statistical figure reported in the 7th Semester Final Submission.

---

## 1. Ground Truth Verification Command

Every metric reported in the thesis (`Project_Report.docx`), presentation (`VayuDrishti_Final_Presentation.pptx`), and manuscript (`manuscript.docx`) is derived directly from raw data via:
```powershell
# From the repository root (PowerShell):
.\final_submission\run_all.ps1
```
Or in Linux / macOS Bash:
```bash
./final_submission/run_all.sh
```

---

## 2. Key Reproducible Benchmarks

| Metric / Result | Location in Submission | Target Ground Truth Value | Reproduction Script |
| :--- | :--- | :--- | :--- |
| **Test R²** | Thesis Table 4.1 / PPT Slide 8 | **0.8997** | `scripts/generate_ground_truth.py` |
| **Test RMSE** | Thesis Table 4.1 / PPT Slide 8 | **16.78 AQI points** | `scripts/generate_ground_truth.py` |
| **Test MAE** | Thesis Table 4.1 | **11.89 AQI points** | `scripts/generate_ground_truth.py` |
| **MICE Imputation RMSE** | Thesis Table 2.2 / PPT Slide 4 | **2.14** (75.6% vs Mean) | `scripts/generate_ground_truth.py` |
| **Autoencoder MSE** | Thesis Section 3.3 | **0.0084** | `scripts/generate_ground_truth.py` |
| **Paired t-test (p-value)** | Thesis Table 4.2 / PPT Slide 8 | **$p = 0.0002 < 0.01$** | `scripts/generate_ground_truth.py` |
| **Wilcoxon test (p-value)** | Thesis Table 4.2 / PPT Slide 8 | **$p = 3.003 \times 10^{-5}$** | `scripts/generate_ground_truth.py` |
| **Prediction Interval Coverage (PICP)** | Thesis Table 4.4 / PPT Slide 8 | **90.01%** | `scripts/generate_ground_truth.py` |
| **Interval Width (MPIW)** | Thesis Table 4.4 | **43.91 AQI points** | `scripts/generate_ground_truth.py` |
| **API Forecast Latency (mean)** | Thesis Table 4.6 / PPT Slide 9 | **2.41 ms** | `scripts/benchmark_api.py` |
| **Pytest Test Suites** | Results ledger | **14 passed (100%)** | `pytest backend/tests -v` |

---

## 3. Seed Determinism & Reproducibility Guarantee

- All stochastic routines (train/test partition, cross-validation splits, XGBoost tree subsampling, Random Forest bootstrap seeds, and PyTorch autoencoder weight initializations) are explicitly seeded with `seed = 42`.
- Floating point variance across operating systems is bounded to $< 0.0001$ relative tolerance.
