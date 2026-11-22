# VayuDrishti Final Submission Package

## 7th Semester Major Project Final Evaluation (Stage-1)
- **Title:** AI-Driven Air Quality Forecasting and Public Health Risk Alert System for Indian Metropolitan Cities
- **Web Platform:** VayuDrishti (वायुदृष्टि)
- **Institution:** Department of Computer Science & Engineering, C.V. Raman Global University, Bhubaneswar, Odisha, 752054
- **Student Team:**
  1. Satyaprakash Rout (Reg No: 2301020206) — Lead / Full-Stack & ML Pipeline
  2. Likuna Swain (Reg No: 2301020252) — Data Engineering & Deep Learning Architecture
  3. Ch Saipriya Patra (Reg No: 2301020205) — Health Risk Modeling & Clinical Advisory
  4. Arpeet Barik (Reg No: 2301020228) — API Architecture, Systems Integration & Testing
- **Faculty Guide:** Prof. Soumya Sahoo, Assistant Professor, Dept. of CSE
- **Evaluation Date:** October 10, 2026

---

## Directory Structure

```text
final_submission/
├── inputs/           # Binding institutional formats (IQAC thesis format, Rubrics, MP PPT template, Interim-2 design)
├── results/          # Single source of truth: final_metrics.json, FACTS.md, leakage_audit.md, and all 13 CSV tables
├── report_assets/    # 300 DPI publication figures, application screenshots, ready-to-paste tables
├── thesis/           # Complete IQAC-compliant thesis (Project_Report.docx, PDF export, plagiarism pre-check)
├── ppt/              # Official PPT presentation (MP_ppt_format.pptx), speaker script, 30-question panel Q&A
├── demo/             # Complete demo storyboard, video script, recorded demonstration, voiceover audio
├── code_package/     # Cleaned submission source code zip with pinned dependencies and zero secrets
├── paper/            # IEEE conference-format manuscript (manuscript.pdf) and 5 verified publication venues
├── scripts/          # Reproduction scripts (generate_ground_truth.py, benchmark_api.py)
├── run_all.ps1       # One-click reproduction script (PowerShell)
├── run_all.sh        # One-click reproduction script (Bash)
├── AI_ML_TECHNICAL_TERMS_GUIDE.md # Authoritative Guide: 25+ AI/ML terms (Why, Where, How, Viva Q&A)
└── OPEN_QUESTIONS.md # Discrepancy report, audit trail, and manual administrative items for the student team
```

---

## One-Click Reproduction Instructions

### 1. Requirements
- Python 3.12 (with libraries: `torch`, `scikit-learn`, `xgboost`, `scipy`, `pandas`, `numpy`, `fastapi`, `uvicorn`, `python-docx`, `python-pptx`, `openpyxl`, `pytest`)
- Node.js 18+ (for frontend)

### 2. Run All Experiments & Verify
In PowerShell:
```powershell
.\final_submission\run_all.ps1
```
Or in Linux / Git Bash:
```bash
chmod +x final_submission/run_all.sh
./final_submission/run_all.sh
```

Every metric in the thesis, presentation, and manuscript matches `results/FACTS.md`.
