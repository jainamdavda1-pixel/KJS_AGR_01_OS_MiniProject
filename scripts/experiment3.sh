#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p logs outputs
echo '[LINUX] Checking which user is running the application:'
whoami
echo '[LINUX] Launching the sensor-to-advisory pipeline as a background process.'
echo '[LINUX] nice -n 10 gives it lower CPU scheduling priority than a default task.'
nice -n 10 python3 -u src/irrigation.py all >logs/experiment3.log 2>&1 &
pid=$!
echo "[PROCESS] Application started with PID $pid (parent shell PID $$)."
ps -p "$pid" -o pid,ppid,ni,stat,comm || true
printf '[PROCESS] Waiting for application to finish...\n'
wait "$pid"
echo '[PROCESS] Application finished normally.'
echo '[DATA] Live pipeline output captured from the application log:'
cat logs/experiment3.log
echo '[PIPES / FILTERS] Extracting the main milestone messages using grep:'
grep -E '^\[(SENSOR|MODEL|ADVISORY|FILE|TIME)' logs/experiment3.log | head -n 25 || true
echo '[FILES] Checking how many lines are in the prediction CSV (including header):'
wc -l outputs/predictions.csv
echo '[LINUX] Current CPU / memory snapshot (system-wide):'
top -b -n 1 | head -n 5 || true
echo "[NOTE] You can change a running process's nice value with: renice -n 15 -p PID"
