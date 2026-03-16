#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <folder_with_csvs>"
  exit 1
fi

IN_DIR="$1"
if [[ ! -d "$IN_DIR" ]]; then
  echo "Error: folder not found: $IN_DIR"
  exit 1
fi

OUT_DIR="${IN_DIR%/}_Results"
mkdir -p "$OUT_DIR"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN="$SCRIPT_DIR/../DualEloRating-linux"

if [[ ! -x "$BIN" ]]; then
  echo "Error: binary not found or not executable: $BIN"
  exit 1
fi

command -v parallel >/dev/null || { echo "Error: GNU parallel not installed"; exit 1; }

shopt -s nullglob

export BIN OUT_DIR
parallel -j 20 --halt now,fail=1 --joblog "$OUT_DIR/joblog.tsv" \
  '$BIN -f {} -opt 2 -n 30 -t 10 -v 0 >"$OUT_DIR"/{/.}.txt 2>&1' \
  ::: "$IN_DIR"/*.csv

echo "Done. Results in: $OUT_DIR"

PY_PARSE="$SCRIPT_DIR/parseResults.py"
PY_EVAL="$SCRIPT_DIR/evaluate.py"

if [[ ! -f "$PY_PARSE" ]]; then
  echo "Error: parseResults.py not found at: $PY_PARSE"
  exit 1
fi
if [[ ! -f "$PY_EVAL" ]]; then
  echo "Error: evaluate.py not found at: $PY_EVAL"
  exit 1
fi

echo "Running: python3 $(basename "$PY_PARSE") \"$OUT_DIR/\""
python3 "$PY_PARSE" "$OUT_DIR"

echo "Running: python3 $(basename "$PY_EVAL") \"$IN_DIR\""
python3 "$PY_EVAL" "$IN_DIR"
