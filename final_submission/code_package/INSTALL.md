# VayuDrishti: Complete Installation & Environment Setup Guide

This guide details instructions for deploying VayuDrishti on Windows, Linux (Ubuntu 22.04+), and macOS systems.

---

## 1. System Prerequisites

- **Python:** 3.11 or 3.12 (Recommended: Python 3.12.x 64-bit)
- **Node.js:** v18.0.0 or higher (Recommended: Node.js 20 LTS)
- **Package Managers:** `pip` (Python) and `npm` (Node)
- **Optional Services:** Redis server (for distributed caching; falls back gracefully to in-memory cache if not running).

---

## 2. Step-by-Step Installation

### Step 2.1: Clone or Extract the Code Package
```bash
unzip vayudrishti_v1.0_source.zip -d vayudrishti
cd vayudrishti
```

### Step 2.2: Setup Backend Python Environment
```bash
cd backend

# Create isolated virtual environment
python -m venv venv

# Activate virtual environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Windows Command Prompt:
.\venv\Scripts\activate.bat
# Linux / macOS:
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install pinned dependencies
pip install -r requirements.txt
```

### Step 2.3: Configure Environment Variables
Copy the `.env.example` template:
```bash
cp .env.example .env
```
Default `.env` configuration:
```ini
ENVIRONMENT=production
DEBUG=false
API_V1_STR=/api/v1
PROJECT_NAME="VayuDrishti AQI Platform"
HOST=127.0.0.1
PORT=8000
CORS_ORIGINS=["http://localhost:5173","http://127.0.0.1:5173"]

# Upstream Telemetry Sources
USE_COPIC_FALLBACK=true
CACHE_TTL_SECONDS=300
```
*(Note: No paid or external secret keys are required. All fallback telemetry sources and local model inferences run self-contained.)*

### Step 2.4: Setup Frontend Dashboard
Open a second terminal window:
```bash
cd frontend
npm install
```

---

## 3. Launching the Services

### Terminal 1: Backend API
```bash
cd backend
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000
```
- API Health Status: `http://127.0.0.1:8000/`
- Interactive OpenAPI Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc Documentation: `http://127.0.0.1:8000/redoc`

### Terminal 2: Frontend Client
```bash
cd frontend
npm run dev
```
- Open your browser to: `http://localhost:5173`

---

## 4. Verification and Sanity Testing

Run the automated verification test suite from the repository root:
```bash
pytest backend/tests -v
```
Expected output:
```text
============================== 14 passed in 3.42s ==============================
```
