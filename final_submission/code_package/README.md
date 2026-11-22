# VayuDrishti Code Package (v1.0-release)

**Project Title:** AI-Driven Air Quality Forecasting and Public Health Risk Alert System for Indian Metropolitan Cities  
**Milestone:** 7th Semester Major Project Final Evaluation (Stage-1)  
**Institution:** Department of Computer Science & Engineering, C.V. Raman Global University  
**Authors:** Satyaprakash Rout (Lead), Likuna Swain, Ch Saipriya Patra, Arpeet Barik  
**Supervisor:** Prof. Soumya Sahoo  
**Release Tag:** `v1.0-release` | **License:** MIT Open Academic License

---

## 1. Directory Overview

```text
code_package/
├── vayudrishti_v1.0_source.zip    # Pristine source zip (zero node_modules, zero pycache)
├── README.md                      # Architecture & execution summary (this file)
├── INSTALL.md                     # Step-by-step installation & environment setup guide
├── ENVIRONMENT.md                 # Pinned dependencies & hardware requirements
└── REPRODUCIBILITY.md             # Automated test execution & ground-truth verification
```

### Unpacked Source Code Structure
```text
vayudrishti_source/
├── backend/
│   ├── api/             # FastAPI asynchronous ASGI endpoints (main.py, routers, middleware)
│   ├── config.py        # Centralized settings with Pydantic validation
│   ├── models/          # Model inference engines & ensemble loaders
│   ├── pipelines/       # Data ingestion, MICE imputation & feature engineering
│   ├── tests/           # 14 Pytest verification suites
│   ├── requirements.txt # Pinned Python dependencies
│   └── .env.example     # Environment template with zero secrets
├── frontend/
│   ├── src/             # React 19 + TypeScript source (components, hooks, pages)
│   ├── public/          # Static logos & geospatial GeoJSON boundary assets
│   ├── package.json     # Node.js dependencies
│   └── vite.config.ts   # Vite bundler configuration
├── models/              # Pre-trained joblib & PyTorch model artifacts (XGBoost, RF, Autoencoder)
├── data/                # Ground-truth multi-city CAAQMS telemetry (12,042 records)
└── final_submission/    # Master reproduction scripts & generated submission artifacts
```

---

## 2. Quick-Start Commands

### Step 1: Backend API (FastAPI)
```bash
cd backend
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
```
API Documentation will be live at: `http://127.0.0.1:8000/docs`

### Step 2: Frontend Dashboard (React 19)
```bash
cd frontend
npm install
npm run dev
```
Dashboard will be live at: `http://localhost:5173`

### Step 3: Run Full Pipeline & Test Suite
```bash
pytest backend/tests -v
```
All 14 tests will pass.
