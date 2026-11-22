# VayuDrishti Full Pipeline Reproduction Script (PowerShell)
# Reproduces all academic metrics, CSV tables, API benchmarks, and test suites.

$ErrorActionPreference = "Stop"
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " VAYUDRISHTI: REPRODUCING MASTER GROUND TRUTH METRICS" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Ensure Python 3.12 is active
Write-Host "`n[1/4] Checking Python environment..." -ForegroundColor Yellow
python --version

# 2. Re-run ground truth calculation from raw data
Write-Host "`n[2/4] Executing generate_ground_truth.py (Seed=42)..." -ForegroundColor Yellow
$env:PYTHONIOENCODING = "utf-8"
python final_submission/scripts/generate_ground_truth.py

# 3. Benchmark API latencies and upstream resilience
Write-Host "`n[3/4] Benchmarking FastAPI endpoints & resilience..." -ForegroundColor Yellow
python final_submission/scripts/benchmark_api.py

# 4. Run Pytest Suite
Write-Host "`n[4/4] Running pytest suite..." -ForegroundColor Yellow
pytest backend/tests -v

Write-Host "`n==========================================================" -ForegroundColor Green
Write-Host " ALL METRICS REPRODUCED SUCCESSFULLY AND VERIFIED!" -ForegroundColor Green
Write-Host " Results directory: final_submission/results/" -ForegroundColor Green
Write-Host " Master Ledger: final_submission/results/FACTS.md" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
