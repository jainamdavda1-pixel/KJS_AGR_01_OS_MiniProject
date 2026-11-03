#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p outputs logs
export PYTHONUNBUFFERED=1
printf '\n============================================================\n'
printf '  SUGARCANE SMART IRRIGATION | LIVE LINUX DEMONSTRATION\n'
printf '============================================================\n'
printf 'Input: sensor readings and weather forecasts for sample plots\n'
printf 'Output: predicted water needs and irrigation suggestions\n'
printf 'All data and model labels are SYNTHETIC (educational demo).\n'
printf '\n[PREPARING] Compiling Linux C applications...\n'
make
printf '\n[1/5] Starting the irrigation application and monitoring Linux processes...\n'
bash scripts/experiment3.sh | tee logs/exp3_console.txt
printf '\n[2/5] Running the three-stage workflow using parent and child processes...\n'
./bin/orchestrator | tee logs/exp4_console.txt
printf '\n[3/5] Simulating sensor readings and synchronized processing...\n'
./bin/buffer | tee logs/exp7_console.txt
printf '\n[4/5] Checking if shared system resources can be allocated safely...\n'
python3 src/banker.py | tee logs/exp9_console.txt
printf '\n[5/5] Testing how the system responds to corrupted sensor data...\n'
if python3 src/irrigation.py acquire --input data/invalid_readings.csv > logs/invalid_test.txt 2>&1; then
  echo '[ERROR] Invalid data was accepted unexpectedly.';exit 1
else
  echo '[SUCCESS] Corrupted data was rejected before producing advisories.'
  cat logs/invalid_test.txt
fi
printf '\n============================================================\n'
printf '  COMPLETE: All workflow stages and safety checks passed.\n'
printf '============================================================\n'
printf 'Farmer-friendly advisory: outputs/advisory.txt\n'
printf 'Plot-wise results (CSV): outputs/predictions.csv\n'
printf 'Saved terminal logs: logs/\n\n'
printf '%s\n' '--- ADVISORY PREVIEW (synthetic demo) ---'
cat outputs/advisory.txt
