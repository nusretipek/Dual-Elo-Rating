#!/usr/bin/env python3
import argparse
import re
from pathlib import Path
from typing import List, Tuple


OPT_RE = re.compile(r"OptimizedEloRatings overall avg.*?:\s*([-+0-9.eE]+)")
DUAL_RE = re.compile(r"DualEloRatings\s+overall avg.*?:\s*([-+0-9.eE]+)")


def extract_avgs(p: Path) -> Tuple[float, float]:
    text = p.read_text(encoding="utf-8", errors="replace")
    m1 = OPT_RE.search(text)
    m2 = DUAL_RE.search(text)
    if not m1 or not m2:
        raise ValueError(f"Could not find both averages in: {p}")
    return float(m1.group(1)), float(m2.group(1))


def collect_rows(folder: Path) -> List[Tuple[str, float, float]]:
    rows = []
    for p in sorted(folder.glob("*.txt")):
        opt, dual = extract_avgs(p)
        rows.append((p.stem, opt, dual))
    return rows


def print_table(title: str, rows: List[Tuple[str, float, float]]) -> None:
    if not rows:
        print(f"{title}: (no files found)")
        return

    name_w = max(len("dataset"), max(len(r[0]) for r in rows))
    opt_w = len("optimized_avg")
    dual_w = len("dual_avg")

    print(title)
    print(f"{'dataset':<{name_w}}  {'optimized_avg':>{opt_w}}  {'dual_avg':>{dual_w}}")
    print(f"{'-'*name_w}  {'-'*opt_w}  {'-'*dual_w}")
    for name, opt, dual in rows:
        print(f"{name:<{name_w}}  {opt:>{opt_w}.3f}  {dual:>{dual_w}.3f}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sudden", default="sudden/correlations", help="Folder containing sudden correlation TXT files")
    ap.add_argument("--mixture", default="mixture/correlations", help="Folder containing mixture correlation TXT files")
    args = ap.parse_args()

    sudden_rows = collect_rows(Path(args.sudden))
    mixture_rows = collect_rows(Path(args.mixture))

    print_table("SUDDEN", sudden_rows)
    print()
    print_table("MIXTURE", mixture_rows)


if __name__ == "__main__":
    main()