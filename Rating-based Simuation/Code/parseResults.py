#!/usr/bin/env python3
import os
import re
import json
import argparse
from typing import Any, Dict, Optional, Tuple


CRASH_PAT = re.compile(
    r"(core dumped|segmentation fault|abort|terminated|floating point exception|stack smashing|dumped core)",
    re.IGNORECASE
)

HDR_OPT_ELO = re.compile(r"Optimized\s+Elo:\s*Results", re.IGNORECASE)
HDR_FULL_ELO = re.compile(r"Optimized\s+Full\s+Model\s+Elo:\s*Results", re.IGNORECASE)

RE_BEST_COMBO = re.compile(
    r"Best\s+Combinational\s+k\(g\)\s+and\s+k\(c\)\s+Elo\s+Model",
    re.IGNORECASE
)

NUM = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?"
RE_LOSS = re.compile(rf"Loss:\s*({NUM})", re.IGNORECASE)
RE_ACC  = re.compile(rf"Accuracy:\s*({NUM})", re.IGNORECASE)
RE_KG   = re.compile(rf"Optimal\s+k\(g\):\s*({NUM})", re.IGNORECASE)
RE_KC   = re.compile(rf"Optimal\s+k\(c\):\s*({NUM})", re.IGNORECASE)

RE_INDICES = re.compile(r"Indices:\s*\{([^}]*)\}", re.IGNORECASE)
RE_INDEX_PAIR = re.compile(r"^\s*(\d+)\s*:\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)\s*$")

# PUT THIS HERE: regex for "Final Elo Scores" block lines
RE_FINAL_ELO_HDR = re.compile(r"^\s*Final\s+Elo\s+Scores\s*:\s*$", re.IGNORECASE)
RE_ELO_LINE = re.compile(rf"^\s*(\d+)\s*:\s*({NUM})\s*$")


def parse_one_output(text: str) -> Optional[Dict[str, Any]]:
    lines = text.splitlines()

    in_opt = False
    in_full = False
    in_full_best = False

    opt_loss = opt_acc = opt_kg = None
    full_kg = full_kc = None
    full_best_loss = full_best_acc = None
    full_best_indices_map: Optional[Dict[int, Tuple[int, int]]] = None

    # PUT THIS HERE: state to capture final elo scores lists
    in_opt_final_elo = False
    opt_final_elo_list = None  # type: Optional[list[float]]

    in_full_final_elo = False
    full_final_elo_list = None  # type: Optional[list[float]]

    for line in lines:
        if HDR_OPT_ELO.search(line):
            in_opt, in_full, in_full_best = True, False, False
            in_opt_final_elo = False
            in_full_final_elo = False
            continue
        if HDR_FULL_ELO.search(line):
            in_opt, in_full, in_full_best = False, True, False
            in_opt_final_elo = False
            in_full_final_elo = False
            continue

        # --------- Optimized Elo block parsing ----------
        if in_opt:
            # detect start of optimized "Final Elo Scores:" block
            if RE_FINAL_ELO_HDR.match(line):
                in_opt_final_elo = True
                opt_final_elo_list = []
                continue

            # capture optimized final elo lines until block ends
            if in_opt_final_elo:
                m = RE_ELO_LINE.match(line)
                if m:
                    opt_final_elo_list.append(float(m.group(2)))
                    continue
                if line.strip() == "" or line.strip().lower().startswith("final ranking") or line.strip().lower().startswith("time"):
                    in_opt_final_elo = False
                # fall through

            m = RE_LOSS.search(line)
            if m and opt_loss is None:
                opt_loss = float(m.group(1))
            m = RE_ACC.search(line)
            if m and opt_acc is None:
                opt_acc = float(m.group(1))
            m = RE_KG.search(line)
            if m and opt_kg is None:
                opt_kg = float(m.group(1))

            # Stop parsing Optimized Elo after its own "Time (s): ..." line
            if line.strip().lower().startswith("time"):
                in_opt = False
            continue  # don't let optimized section fall into full parsing

        # --------- Full model parsing ----------
        if in_full:
            # detect start of full-model "Final Elo Scores:" block
            if RE_FINAL_ELO_HDR.match(line):
                in_full_final_elo = True
                full_final_elo_list = []
                continue

            # capture full-model final elo lines until block ends
            if in_full_final_elo:
                m = RE_ELO_LINE.match(line)
                if m:
                    full_final_elo_list.append(float(m.group(2)))
                    continue
                if line.strip() == "" or line.strip().lower().startswith("final ranking") or line.strip().lower().startswith("best combinational"):
                    in_full_final_elo = False
                # fall through

            if RE_BEST_COMBO.search(line):
                in_full_best = True
                if full_best_indices_map is None:
                    full_best_indices_map = {}
                continue

            if not in_full_best:
                m = RE_KG.search(line)
                if m:
                    full_kg = float(m.group(1))
                m = RE_KC.search(line)
                if m:
                    full_kc = float(m.group(1))
            else:
                m = RE_LOSS.search(line)
                if m:
                    full_best_loss = float(m.group(1))
                m = RE_ACC.search(line)
                if m:
                    full_best_acc = float(m.group(1))

                m = RE_INDICES.search(line)
                if m and full_best_indices_map is not None:
                    inner = m.group(1).strip()
                    if inner:
                        for x in inner.split(","):
                            x = x.strip()
                            if x:
                                full_best_indices_map.setdefault(int(x), (-1, -1))

                m = RE_INDEX_PAIR.match(line)
                if m and full_best_indices_map is not None:
                    idx = int(m.group(1))
                    a = int(m.group(2))
                    b = int(m.group(3))
                    full_best_indices_map[idx] = (a, b)

                if line.strip().lower().startswith("time"):
                    in_full_best = False

    if opt_loss is None or opt_acc is None or opt_kg is None:
        return None
    if opt_final_elo_list is None or len(opt_final_elo_list) == 0:
        return None
    if full_kg is None or full_kc is None:
        return None
    if full_final_elo_list is None or len(full_final_elo_list) == 0:
        return None
    if full_best_loss is None or full_best_acc is None or full_best_indices_map is None:
        return None

    full_best_indices_map = {
        k: v for k, v in full_best_indices_map.items()
        if isinstance(v, tuple) and len(v) == 2 and v[0] >= 0 and v[1] >= 0
    }

    return {
        "optimized_elo": {
            "loss": opt_loss,
            "accuracy": opt_acc,
            "k_g": opt_kg,
            "final_elo_scores": opt_final_elo_list,  # <-- added
        },
        "full_model": {
            "k_g": full_kg,
            "k_c": full_kc,
            "final_elo_scores": full_final_elo_list,
            "best_combinational": {
                "loss": full_best_loss,
                "accuracy": full_best_acc,
                "indices": full_best_indices_map,
            },
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder", help="Folder containing *.txt outputs (e.g., G5_I500_Results)")
    args = ap.parse_args()

    results_dir = args.folder.rstrip("/")
    if not os.path.isdir(results_dir):
        raise SystemExit(f"Results folder not found: {results_dir}")

    out_json = os.path.join(results_dir, "results.json")
    out_txt = os.path.join(results_dir, "summary.txt")

    txt_files = sorted(f for f in os.listdir(results_dir) if f.lower().endswith(".txt"))

    error_count = 0
    parsed: Dict[str, Any] = {}

    for fn in txt_files:
        path = os.path.join(results_dir, fn)
        key = os.path.splitext(fn)[0]

        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except Exception:
            parsed[key] = {}
            error_count += 1
            continue

        if CRASH_PAT.search(content):
            parsed[key] = {}
            error_count += 1
            continue

        obj = parse_one_output(content)
        if obj is None:
            parsed[key] = {}
            error_count += 1
            continue

        parsed[key] = obj

    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(parsed, f, indent=2, sort_keys=True)

    with open(out_txt, "w", encoding="utf-8") as f:
        f.write(f"Error count: {error_count}\n")
        f.write(f"Parsed count: {len(parsed)}\n")

    print(f"Wrote: {out_json}")
    print(f"Wrote: {out_txt}")


if __name__ == "__main__":
    main()
