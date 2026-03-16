#!/usr/bin/env bash
set -euo pipefail

BIN="./DualEloRating-linux"
ROOT="Simulation/Data"
OUTROOT="rankCorrelation"

# Fixed settings
OPTS=(-opt 2 -n 30 -t 10 -v 0)

# Safety checks
if [[ ! -x "$BIN" ]]; then
  echo "Error: executable not found or not executable: $BIN" >&2
  exit 1
fi
if [[ ! -d "$ROOT" ]]; then
  echo "Error: data root folder not found: $ROOT" >&2
  exit 1
fi

# Create output base
mkdir -p "$OUTROOT"

run_one_dir() {
  local category="$1"    
  local dir="$2"        

  local outdir="$OUTROOT/$category"
  mkdir -p "$outdir"

  shopt -s nullglob
  local csvs=("$dir"/*.csv)
  shopt -u nullglob

  if (( ${#csvs[@]} == 0 )); then
    echo "No CSV files found in: $dir (one level only)"
    return 0
  fi

  for csv in "${csvs[@]}"; do
    local base
    base="$(basename "$csv" .csv)"
    local outfile="$outdir/${base}.txt"

    echo "Running: $csv -> $outfile"
    "$BIN" -f "$csv" "${OPTS[@]}" >"$outfile" 2>&1
  done
}

for category in mixture sudden; do
  if [[ -d "$ROOT/$category" ]]; then
    run_one_dir "$category" "$ROOT/$category"
  else
    echo "Skipping missing folder: $ROOT/$category"
  fi
done

echo "Done. Results under: $OUTROOT/{mixture,sudden}/"