# VayuDrishti (वायुदृष्टि)
### AI-Driven Air Quality Forecasting & Public Health Risk Alert System for Indian Metropolitan Cities

> **7th-Semester Major Project (Review 1)**  
> **Institution:** C.V. Raman Global University (CGU), Bhubaneswar, India  
> **Faculty Guide:** Prof. Soumya Sahoo, Assistant Professor, Dept. of CSE  
> **Team:** Satyaprakash Rout, Likuna Swain, Ch Saipriya Patra, Arpeet Barik  

---

## 📄 Complete Project & Dataset Documentation
For the exhaustive technical specification, dataset breakdown, mathematical formulations, and citations, see:
👉 **[DATASET_AND_PROJECT_INFO.md](DATASET_AND_PROJECT_INFO.md)**

---

## 🌟 Key Highlights

1. **CPCB Indian Megacity Dataset (2018–2024):**
   - **12,042 daily records** across **5 key metropolitan hubs**: Delhi, Mumbai, Bangalore, Chennai, and Hyderabad.
   - Monitors 6 core criteria pollutants: $PM_{2.5}, PM_{10}, NO_2, SO_2, CO, O_3$ and continuous $AQI$.

2. **Advanced Data Pipeline:**
   - **MICE Iterative Imputation:** Solves sensor missingness with an RMSE of **2.14** vs **8.76** for standard mean imputation (**75.6% error reduction**).
   - **Deep Latent Autoencoder:** 4-layer symmetrical bottleneck neural network (Reconstruction MSE: **0.0084**) extracting multi-pollutant atmospheric interactions.
   - **Temporal Lags & Rolling Statistics:** Backward lags ($t-1$ through $t-7$), moving averages, and cyclical seasonal sine/cosine encodings.

3. **Multi-Model Next-Day Forecasting:**
   - Evaluates **Linear Regression**, **Random Forest**, **XGBoost**, **LSTM**, and a **Stacking Ensemble**.
   - **Best Model (Ensemble):** **$R^2 = 0.9237$**, **RMSE = 18.42**, **MAE = 12.95**.

4. **Population-Stratified Health Risk Index (HRI):**
   - Implements multi-pollutant exposure ratios scaled by clinical vulnerability factors:
     - **General Public ($1.0\times$)**
     - **Children & Elderly ($1.3\times$)**
     - **Respiratory & Cardiac Patients ($1.6\times$)**
   - Stratifies risks into 4 tiers (**Low, Moderate, High, Severe**) based on shared baseline quantiles.

5. **Full-Stack Implementation:**
   - **Backend:** FastAPI high-performance asynchronous REST API (`/forecast/{city}`, `/hri/{city}`, `/alerts/{city}`).
   - **Frontend:** Modern responsive web application built with React 19, Vite, Tailwind CSS, Framer Motion, and Recharts.

---

## 🚀 Quick Start Guide

### 1. Run the Frontend Dashboard
Navigate to the `frontend` directory:
```powershell
cd frontend
.\dev.ps1
```
*(Or use `npm run dev` if your profile is loaded).*
Open your browser at: **`http://localhost:5173/`**

### 2. Run the Backend API
In a separate terminal:
```powershell
cd backend
uvicorn api.main:app --reload
```
Interactive Swagger API documentation available at: **`http://localhost:8000/docs`**

### 3. Run the Full ML Pipeline
```powershell
python -m pipeline.run_pipeline
```
