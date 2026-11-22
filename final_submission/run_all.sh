#!/usr/bin/env bash
# VayuDrishti Full Pipeline Reproduction Script (Bash)
# Reproduces all academic metrics, CSV tables, API benchmarks, and test suites.

set -e
echo "=========================================================="
echo " VAYUDRISHTI: REPRODUCING MASTER GROUND TRUTH METRICS"
echo "=========================================================="

echo -e "\n[1/4] Checking Python environment..."
python3 --version || python --version

echo -e "\n[2/4] Executing generate_ground_truth.py (Seed=42)..."
export PYTHONIOENCODING=utf-8
python3 final_submission/scripts/generate_ground_truth.py || python final_submission/scripts/generate_ground_truth.py

echo -e "\n[3/4] Benchmarking FastAPI endpoints & resilience..."
python3 final_submission/scripts/benchmark_api.py || python final_submission/scripts/benchmark_api.py

echo -e "\n[4/4] Running pytest suite..."
pytest backend/tests -v

echo -e "\n=========================================================="
echo " ALL METRICS REPRODUCED SUCCESSFULLY AND VERIFIED!"
echo " Results directory: final_submission/results/"
echo " Master Ledger: final_submission/results/FACTS.md"
echo "=========================================================="
