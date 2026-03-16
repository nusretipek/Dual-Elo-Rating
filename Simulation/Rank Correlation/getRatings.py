#!/usr/bin/env python3
import re
import sys
import csv
from pathlib import Path
from typing import Dict, List, Any, Optional, Set

import numpy as np

SECTION_DEFAULT = "*** Optimized Elo (Default) ***"
SECTION_FULL = "*** Optimized Elo (Full Model) ***"


def parse_optimized_output(text: str) -> Dict[str, Any]:
    section = None

    default_kg: Optional[float] = None
    default_init: List[float] = []

    full_kg: Optional[float] = None
    full_kc: Optional[float] = None
    full_init: List[float] = []
    full_indices: List[int] = []

    in_init_default = False
    in_init_full = False

    for raw in text.splitlines():
        line = raw.strip()

        if SECTION_DEFAULT in line:
            section = "default"
            in_init_default = False
            in_init_full = False
            continue
        if SECTION_FULL in line:
            section = "full"
            in_init_default = False
            in_init_full = False
            continue

        m = re.match(r"^Optimal k\(g\):\s*([0-9.eE+-]+)\b", line)
        if m:
            if section == "default":
                default_kg = float(m.group(1))
            elif section == "full":
                full_kg = float(m.group(1))
            continue

        m = re.match(r"^Optimal k\(c\):\s*([0-9.eE+-]+)\b", line)
        if m and section == "full":
            full_kc = float(m.group(1))
            continue

        if line.startswith("Optimal Initial Elo Scores:"):
            if section == "default":
                in_init_default = True
                in_init_full = False
            elif section == "full":
                in_init_full = True
                in_init_default = False
            continue

        if line.startswith("Final Elo Scores:") or line.startswith("Final Ranking:"):
            in_init_default = False
            in_init_full = False

        m = re.match(r"^\s*\d+:\s*([0-9.eE+-]+)\s*$", raw)
        if m:
            val = float(m.group(1))
            if in_init_default:
                default_init.append(val)
                continue
            if in_init_full:
                full_init.append(val)
                continue

        # Indices under Full Model -> Best combinational section
        if section == "full":
            m = re.search(r"^Indices:\s*\{([^}]*)\}", line)
            if m:
                items = [x.strip() for x in m.group(1).split(",") if x.strip()]
                full_indices = [int(x) for x in items]
                continue

    return {
        "default": {"k_g": default_kg, "init_elos": default_init},
        "full": {"k_g": full_kg, "k_c": full_kc, "init_elos": full_init, "indices": full_indices},
    }


def expected_win_prob(sa: float, sb: float) -> float:
    return 1.0 / (1.0 + np.exp(-0.01 * (sa - sb)))


def _update(scores: np.ndarray, winner: int, loser: int, k: float) -> None:
    # winner gains, loser loses (symmetric)
    p_w = expected_win_prob(scores[winner], scores[loser])
    delta = k * (1.0 - p_w)
    scores[winner] += delta
    scores[loser] -= delta

def scores_to_ranks(scores: np.ndarray) -> np.ndarray:
    """
    Returns rank-values 0..n-1 where higher score => higher rank-value.
    Ties get the average rank (still 0-based).
    """
    scores = np.asarray(scores, dtype=float)
    n = scores.size

    order = np.argsort(scores, kind="mergesort")  # ascending scores
    ranks = np.empty(n, dtype=float)
    ranks[order] = np.arange(0, n, dtype=float)   # 0..n-1

    sorted_s = scores[order]
    change = np.concatenate(([True], sorted_s[1:] != sorted_s[:-1], [True]))
    idx = np.flatnonzero(change)

    for start, end in zip(idx[:-1], idx[1:]):
        if end - start > 1:  # tie block [start, end)
            avg = 0.5 * (start + (end - 1))       # 0-based average
            ranks[order[start:end]] = avg

    return ranks


def simulate_elo_from_csv(
    csv_path: Path,
    init_scores: List[float],
    k_g: float,
    *,
    winner_col: int = 0,
    loser_col: int = 1,
    has_header: bool = True,
) -> List[List[float]]:
    scores = np.array(init_scores, dtype=float)
    snapshots: List[List[float]] = []

    with csv_path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        if has_header:
            next(reader, None)

        for row_i, row in enumerate(reader):
            if not row or len(row) <= max(winner_col, loser_col):
                continue

            w = int(row[winner_col])
            l = int(row[loser_col])

            if w < 0 or l < 0 or w >= len(scores) or l >= len(scores):
                raise IndexError(
                    f"Row {row_i}: index out of range (w={w}, l={l}), scores length={len(scores)}"
                )

            _update(scores, w, l, k_g)
            snapshots.append(scores_to_ranks(scores).tolist())

    return snapshots


def simulate_dual_elo_from_csv(
    csv_path: Path,
    init_scores: List[float],
    k_g: float,
    k_c: float,
    special_indices: Set[int],
    *,
    winner_col: int = 0,
    loser_col: int = 1,
    has_header: bool = True,
    index_base: int = 0,  # indices interpreted as 0-based by default
) -> List[List[float]]:
    """
    Dual update:
      - use k_g for regular interactions
      - for interactions whose index is in special_indices, use k_c
    Interaction index = row number after header, adjusted by index_base:
      effective_index = row_i + index_base
    """
    scores = np.array(init_scores, dtype=float)
    snapshots: List[List[float]] = []

    with csv_path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        if has_header:
            next(reader, None)

        for row_i, row in enumerate(reader):
            if not row or len(row) <= max(winner_col, loser_col):
                continue

            w = int(row[winner_col])
            l = int(row[loser_col])

            if w < 0 or l < 0 or w >= len(scores) or l >= len(scores):
                raise IndexError(
                    f"Row {row_i}: index out of range (w={w}, l={l}), scores length={len(scores)}"
                )

            eff_idx = row_i + index_base
            k = k_c if eff_idx in special_indices else k_g

            _update(scores, w, l, k)
            snapshots.append(scores_to_ranks(scores).tolist())

    return snapshots


def _out_path(opt_output_path: Path, folder_name: str) -> Path:
    # sudden/switchedHierarchy_01_0.txt -> sudden/<folder_name>/switchedHierarchy_01_0.txt
    outdir = opt_output_path.parent / folder_name
    outdir.mkdir(parents=True, exist_ok=True)
    return outdir / opt_output_path.name


def write_snapshots(out_path: Path, snapshots):
    with out_path.open("w", encoding="utf-8") as f:
        for snap in snapshots:
            # snap is a Python list -> will include commas and never wrap for small n
            f.write(str(snap) + "\n")


def main():
    args = sys.argv[1:]

    def get_arg(flag: str) -> Optional[str]:
        if flag in args:
            i = args.index(flag)
            if i + 1 < len(args):
                return args[i + 1]
        return None

    opt_output = get_arg("--opt-output")
    csv_file = get_arg("--csv")
    index_base_s = get_arg("--index-base")

    if not opt_output or not csv_file:
        print(
            "Usage: python3 script.py --opt-output <results.txt> --csv <interactions.csv> [--index-base 0|1]",
            file=sys.stderr,
        )
        sys.exit(2)

    index_base = int(index_base_s) if index_base_s is not None else 0

    opt_path = Path(opt_output)
    csv_path = Path(csv_file)

    parsed = parse_optimized_output(opt_path.read_text(encoding="utf-8", errors="replace"))

    # Output 1: OptimizedEloRatings (Default model init + k(g))
    d_kg = parsed["default"]["k_g"]
    d_init = parsed["default"]["init_elos"]
    if d_kg is None or not d_init:
        raise RuntimeError("Default model Optimal k(g) or Optimal Initial Elo Scores not found.")

    snapshots_default = simulate_elo_from_csv(
        csv_path,
        init_scores=d_init,
        k_g=d_kg,
        winner_col=0,
        loser_col=1,
        has_header=True,
    )
    out1 = _out_path(opt_path, "optimizedEloRatings")
    write_snapshots(out1, snapshots_default)

    # Output 2: DualEloRatings (Full model init; k(g) regular; k(c) for special indices)
    f_kg = parsed["full"]["k_g"]
    f_kc = parsed["full"]["k_c"]
    f_init = parsed["full"]["init_elos"]
    f_indices = set(parsed["full"]["indices"] or [])

    if f_kg is None or f_kc is None or not f_init:
        raise RuntimeError("Full model Optimal k(g)/k(c) or Optimal Initial Elo Scores not found.")
    if not f_indices:
        # still produce output (all interactions use k(g))
        f_indices = set()

    snapshots_dual = simulate_dual_elo_from_csv(
        csv_path,
        init_scores=f_init,
        k_g=f_kg,
        k_c=f_kc,
        special_indices=f_indices,
        winner_col=0,
        loser_col=1,
        has_header=True,
        index_base=index_base,
    )
    out2 = _out_path(opt_path, "DualEloRatings")
    write_snapshots(out2, snapshots_dual)


if __name__ == "__main__":
    main()