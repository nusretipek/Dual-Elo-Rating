# Rating-based Simulation

This folder contains the rating-based simulation datasets, execution outputs, and scripts used to reproduce the  experiments.

## Folder Structure

### 1. Code

The `Code` folder contains the main Python scripts:

- `generateData.py`: Generates simulated interaction datasets.
- `parseResults.py`: Parses per-seed Dual Elo stdout (`*.txt`) into structured `results.json`.
- `evaluate.py`: Compares parsed outputs with metadata and reports aggregate metrics.
- `tabulize.py`: Runs `evaluate.py` over all dataset settings and creates summary tables.

### 2. Data

The `Data` folder stores generated datasets using:

- `N` in `{6, 8, 10}` (group size)
- `T` in `{200, 400, 600}` (interaction count)
- `S` in `{0, 50}` (initial score deviation)
- seeds from `0` to `99`

Each dataset folder follows:

- `G{N}_I{T}_S{S}`

Each folder contains:

- `0.csv` ... `99.csv`: interaction sequences (`Initiator, Receiver`)
- `meta.json`: generation metadata (including sudden events and final simulated scores)

Data generation command (used in this project):

```bash
python3 generateData.py --n N --T T --kl 100 --kh 500 --sudden 2 --u 0 --s S --out-dir DIRNAME --seed-start 0 --seed-end 99
```

### 3. Results

The `Results` folder contains the archived per-dataset execution outputs in this repository:

- `G{N}_I{T}_S{S}_Results`

Each results folder includes files such as:

- `0.txt` ... `99.txt`: raw Dual Elo stdout for each seed
- `joblog.tsv`: GNU parallel execution log
- `results.json`: parsed structured results (`parseResults.py` output)
- `summary.txt`: parsing summary
- `metrics.txt`: evaluation summary for that setting

## Reproducing Results

### 1. Run Dual Elo + parse + evaluate for one dataset

From this folder:

```bash
./dualRun.sh Data/G6_I200_S0
```

This script:

- runs `DualEloRating-linux` over all `*.csv` files in the input folder,
- writes raw outputs to `<input_folder>_Results` (for example, `Data/G6_I200_S0_Results`),
- runs `parseResults.py` to create `results.json` and `summary.txt`,
- runs `evaluate.py` for that dataset.

### 2. Evaluate all dataset settings and tabulate

From `Code/`:

```bash
python3 tabulize.py --root ../Data --evaluate evaluate.py --python python3 --out ../Results/eval_table
```
