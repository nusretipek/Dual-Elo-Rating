#!/usr/bin/env python3
import argparse
import ast
from pathlib import Path
from typing import List, Dict, Sequence, Tuple, Optional

import numpy as np


def read_rank_series(path: Path, max_lines: Optional[int] = None) -> List[np.ndarray]:
    """Reads one Python list per line, e.g. [0.0, 3.0, 1.0, ...]."""
    series: List[np.ndarray] = []
    with path.open("r", encoding="utf-8", errors="replace") as f:
        for i, line in enumerate(f):
            if max_lines is not None and i >= max_lines:
                break
            line = line.strip()
            if not line:
                continue
            try:
                series.append(np.array(ast.literal_eval(line), dtype=float))
            except Exception as e:
                raise ValueError(f"{path}: failed to parse line {i+1}: {e}") from e
    return series


def rankdata_average(a: np.ndarray) -> np.ndarray:
    """Average ranks for ties, ranks start at 1."""
    a = np.asarray(a)
    n = a.size
    order = np.argsort(a, kind="mergesort")
    ranks = np.empty(n, dtype=float)
    ranks[order] = np.arange(1, n + 1, dtype=float)

    sorted_a = a[order]
    change = np.concatenate(([True], sorted_a[1:] != sorted_a[:-1], [True]))
    idx = np.flatnonzero(change)
    for start, end in zip(idx[:-1], idx[1:]):
        if end - start > 1:
            avg_rank = 0.5 * ((start + 1) + end)
            ranks[order[start:end]] = avg_rank
    return ranks


def spearman_corr(x: np.ndarray, y: np.ndarray) -> float:
    # Spearman = Pearson correlation of ranks
    rx = rankdata_average(x)
    ry = rankdata_average(y)
    sx = rx.std()
    sy = ry.std()
    if sx == 0.0 or sy == 0.0:
        return float("nan")
    return float(np.corrcoef(rx, ry)[0, 1])


def hierarchy_by_time(t: int) -> List[Sequence[int]]:
    # tiers are best -> worst (mixture case, 8 animals: 0..7)
    if 0 <= t < 200:
        return [[0], [4, 1], [6, 5, 2], [3], [7]]
    if 200 <= t < 400:
        return [[0], [4, 2], [6, 5, 1], [3], [7]]
    if 400 <= t < 600:
        return [[4], [0, 2], [6, 5, 1], [7], [3]]
    return [[4], [0, 2], [6, 1], [5], [7], [3]]


def truth_values_from_tiers(tiers_best_to_worst: List[Sequence[int]], n_items: int) -> np.ndarray:
    num_tiers = len(tiers_best_to_worst)
    val: Dict[int, float] = {}
    for tier_idx, items in enumerate(tiers_best_to_worst):
        v = float((num_tiers - 1) - tier_idx)  # higher is better
        for it in items:
            val[int(it)] = v

    missing = [i for i in range(n_items) if i not in val]
    if missing:
        raise ValueError(f"Truth hierarchy missing item ids: {missing} (n_items={n_items})")

    return np.array([val[i] for i in range(n_items)], dtype=float)


def compute_avg_spearman(series: List[np.ndarray], T: int) -> Tuple[float, Dict[str, float]]:
    if not series:
        return float("nan"), {}

    T_eff = min(T, len(series))
    n_items = int(series[0].shape[0])

    corrs: List[float] = []
    buckets = {"0-199": [], "200-399": [], "400-599": [], "600+": []}

    for t in range(T_eff):
        pred = series[t]
        if pred.shape[0] != n_items:
            raise ValueError(f"Inconsistent vector length at t={t}: expected {n_items}, got {pred.shape[0]}")

        truth = truth_values_from_tiers(hierarchy_by_time(t), n_items)
        c = spearman_corr(truth, pred)
        corrs.append(c)

        if t < 200:
            buckets["0-199"].append(c)
        elif t < 400:
            buckets["200-399"].append(c)
        elif t < 600:
            buckets["400-599"].append(c)
        else:
            buckets["600+"].append(c)

    overall = float(np.nanmean(np.array(corrs, dtype=float)))
    interval_avgs = {
        k: round(float(np.nanmean(np.array(v, dtype=float))), 3) if v else float("nan")
        for k, v in buckets.items()
    }
    return overall, interval_avgs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--opt", required=True, help="optimizedEloRatings ranks TXT (one list per line)")
    ap.add_argument("--dual", required=True, help="DualEloRatings ranks TXT (one list per line)")
    ap.add_argument("--timepoints", type=int, default=800)
    args = ap.parse_args()

    opt_series = read_rank_series(Path(args.opt), max_lines=args.timepoints)
    dual_series = read_rank_series(Path(args.dual), max_lines=args.timepoints)

    opt_avg, opt_intervals = compute_avg_spearman(opt_series, args.timepoints)
    dual_avg, dual_intervals = compute_avg_spearman(dual_series, args.timepoints)

    print("=== Spearman rank correlation vs true tiered hierarchy (mixture) ===")
    print(f"OptimizedEloRatings overall avg (T<= {args.timepoints}): {np.round(opt_avg, 3)}")
    print(f"  intervals: {opt_intervals}")
    print(f"DualEloRatings      overall avg (T<= {args.timepoints}): {np.round(dual_avg, 3)}")
    print(f"  intervals: {dual_intervals}")


if __name__ == "__main__":
    main()