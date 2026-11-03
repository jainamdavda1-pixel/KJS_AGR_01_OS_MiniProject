# Sugarcane Irrigation Advisory — OS AI Use Case (KJS-AGR-01)

**Educational prototype** using fabricated sensor/weather values. It is not farm advice. No real farmers' data is collected.

## Experiments
- 3 — User and process commands, nice, monitoring, pipes and filters (`scripts/experiment3.sh`)
- 4 — POSIX file and process system calls: `open/read/write/close`, `fork/exec/wait` (`src/orchestrator.c`)
- 7 — Producer/consumer with `pthread`, semaphores and mutex (`src/buffer.c`)
- 9 — Banker's safe/unsafe state analysis for sensor, DB and pump resources (`src/banker.py`)

## Run (Ubuntu / Debian / WSL2 Linux)
```bash
sudo apt update && sudo apt install -y build-essential python3 make
cd OS_Sugarcane_Project
bash scripts/run_all.sh
```
No Python packages beyond the standard library are required. If already in the project directory, omit `cd`.

Individual stages:
```bash
make
python3 src/irrigation.py all
./bin/orchestrator
./bin/buffer
python3 src/banker.py
```

## Data and model
`data/sensor_readings.csv` has six **synthetic** records. The prototype validates them, trains a small linear regression via deterministic gradient descent on synthetic labels created by a heuristic baseline, and produces `outputs/predictions.csv` and `outputs/advisory.txt`. Synthetic training MAE measures agreement with the heuristic, **not real-world accuracy**. Estimated pump minutes assume an illustrative 100 m² plot and ignore real hydrology, actual pump hydraulics, calibration, evapotranspiration and local agronomic recommendations.

## Failure tests
```bash
python3 src/irrigation.py acquire --input data/invalid_readings.csv
./bin/orchestrator data/does_not_exist.csv
```
Both should fail (nonzero exit). The Banker's test explicitly prints SAFE and UNSAFE states.

## Report evidence
Run `bash scripts/run_all.sh` on the Linux machine, record terminal screenshots from its four experiment sections, and fill the report's screenshot placeholders. The provided report contains a separately labelled, environment-specific validation from the development container; it does not claim to be a screenshot from your Linux machine.

## Academic integrity
AI assistance was used to write the demonstration code/report. Read and verify all outputs and be ready to explain each experiment. The experiment manuals and official OS report template were not supplied; adapt the section layout if your instructor has a mandatory format.

## Presentation-friendly terminal narration (updated)
Run `bash scripts/run_all.sh` to see a guided demonstration with messages labelled
`[SENSOR]`, `[MODEL]`, `[ADVISORY]`, `[PARENT]`, `[CHILD]`, `[SHARED QUEUE]`,
`[RESOURCE MANAGER]`, `[SAFE]` and `[BLOCK]`. The console deliberately describes
what each operation does, rather than identifying the demonstrations by experiment number.
The underlying experiments remain 3, 4, 7 and 9. The output is saved to `logs/`.

The 12 readings passed between threads are numbered *simulation packets*, not actual
physical IoT readings; the ML training labels and plot dataset are synthetic.
The unsafe allocation scenario is a Banker's-algorithm demonstration and does not
represent an actual deadlock in the running application.
