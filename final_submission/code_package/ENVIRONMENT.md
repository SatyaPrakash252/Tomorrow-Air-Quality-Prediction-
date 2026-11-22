# VayuDrishti: Software Environment & Dependency Specifications

This document defines the exact software versions, runtime libraries, and hardware requirements for VayuDrishti.

---

## 1. Hardware Specifications

- **Minimum Configuration:**
  - CPU: Dual-Core 2.0 GHz x86_64 or ARM64
  - RAM: 4 GB
  - Storage: 2 GB available disk space
  - GPU: Not strictly required (inference runs efficiently on CPU in 2.41 ms)

- **Recommended Evaluation / Training Configuration:**
  - CPU: Quad-Core Intel Core i5 / AMD Ryzen 5 or higher
  - RAM: 8 GB or 16 GB
  - Storage: 5 GB available disk space (SSD recommended)
  - GPU: NVIDIA GPU with CUDA 12+ (optional, speeds up PyTorch autoencoder training from 45s to 8s)

---

## 2. Core Runtime Environments

| Software Component | Target Version | Tested Environments |
| :--- | :--- | :--- |
| **Python** | 3.12.x (64-bit) | Windows 11, Ubuntu 22.04 LTS, macOS Sequoia 15 |
| **Node.js** | 20.x LTS / 18.x | Node v20.11.0, npm v10.2.4 |
| **Operating System** | Platform Independent | Windows 10/11, POSIX Linux, macOS |

---

## 3. Pinned Python Dependencies (`backend/requirements.txt`)

```text
fastapi>=0.110.0
uvicorn[standard]>=0.28.0
pydantic>=2.6.4
numpy>=1.26.4
pandas>=2.2.1
scikit-learn>=1.4.1
xgboost>=2.0.3
torch>=2.2.1
scipy>=1.12.0
optuna>=3.5.0
joblib>=1.3.2
python-docx>=1.1.0
python-pptx>=0.6.23
openpyxl>=3.1.2
pytest>=8.0.2
requests>=2.31.0
slowapi>=0.1.9
```

---

## 4. Frontend Node Dependencies (`frontend/package.json`)

```json
{
  "dependencies": {
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "lucide-react": "^1.16.0",
    "recharts": "^2.15.0",
    "clsx": "^2.1.1",
    "tailwind-merge": "^2.6.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.3.4",
    "typescript": "^5.7.2",
    "vite": "^6.0.7"
  }
}
```

---

## 5. Security & Zero-Leakage Declaration

- **No Secrets / Tokens:** The codebase contains zero hardcoded API keys, database passwords, or private SSH keys.
- **Offline Self-Sufficiency:** The system includes pre-trained model weights (`models/`) and pre-ingested historical CAAQMS telemetry (`data/`), enabling complete offline execution and evaluation without requiring live internet access.
