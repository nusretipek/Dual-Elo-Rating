import argparse
import csv
import os
import re
import subprocess
from typing import Dict, Optional, Tuple, List


RE_OPT = re.compile(r"Optimized Elo\s+-\s+Avg Loss:\s*([-0-9.]+),\s*Avg Acc:\s*([0-9.]+)")
RE_FULL = re.compile(r"Full Model Best\s+-\s+Avg Loss:\s*([-0-9.]+),\s*Avg Acc:\s*([0-9.]+)")
RE_OPT_KG = re.compile(r"Average Optimized k\(g\):\s*([-0-9.]+)")
RE_FULL_KG = re.compile(r"Average Full Model k\(g\):\s*([-0-9.]+)")
RE_FULL_KC = re.compile(r"Average Full Model k\(c\):\s*([-0-9.]+)")
RE_RECALL = re.compile(r"Recall:\s*([0-9.]+)")


def fmt(x: Optional[float], nd: int) -> str:
    return "" if x is None else f"{x:.{nd}f}"


def fmt_pct(x: Optional[float], nd: int = 2) -> str:
    return "" if x is None else f"{(100.0 * x):.{nd}f}"


def parse_evaluate_output(text: str) -> Dict[str, Optional[float]]:
    out: Dict[str, Optional[float]] = {
        "opt_loss": None,
        "opt_acc": None,
        "opt_kg": None,
        "dual_loss": None,
        "dual_acc": None,
        "dual_kg": None,
        "dual_kc": None,
        "recall": None,
    }

    m = RE_OPT.search(text)
    if m:
        out["opt_loss"] = float(m.group(1))
        out["opt_acc"] = float(m.group(2))

    m = RE_FULL.search(text)
    if m:
        out["dual_loss"] = float(m.group(1))
        out["dual_acc"] = float(m.group(2))

    m = RE_OPT_KG.search(text)
    if m:
        out["opt_kg"] = float(m.group(1))

    m = RE_FULL_KG.search(text)
    if m:
        out["dual_kg"] = float(m.group(1))

    m = RE_FULL_KC.search(text)
    if m:
        out["dual_kc"] = float(m.group(1))

    m = RE_RECALL.search(text)
    if m:
        out["recall"] = float(m.group(1))

    return out


def dataset_params(folder_name: str) -> Tuple[int, int, int, int]:
    """
    Returns (N, C, init_dev, s_flag)
    Expected folder patterns:
      - G{N}_I{C}_S0
      - G{N}_I{C}_S50
    """
    m = re.match(r"^G(\d+)_I(\d+)_S(0|50)$", folder_name)
    if not m:
        raise ValueError(f"Folder name does not match expected pattern: {folder_name}")
    N = int(m.group(1))
    C = int(m.group(2))
    s_flag = int(m.group(3))
    init_dev = s_flag
    return N, C, init_dev, s_flag


def run_evaluate(python_exe: str, evaluate_py: str, data_dir: str) -> Tuple[int, str]:
    p = subprocess.run(
        [python_exe, evaluate_py, data_dir],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    return p.returncode, p.stdout


def main() -> None:
    ap = argparse.ArgumentParser(description="Run evaluate.py over datasets and build a structured table.")
    ap.add_argument("--root", type=str, default=".", help="Root directory containing dataset folders.")
    ap.add_argument("--evaluate", type=str, default="evaluate.py", help="Path to evaluate.py.")
    ap.add_argument("--python", type=str, default="python3", help="Python executable to run evaluate.py.")
    ap.add_argument("--out", type=str, default="eval_table", help="Output basename (no extension).")
    args = ap.parse_args()

    root = args.root.rstrip("/")
    evaluate_py = args.evaluate
    python_exe = args.python

    Ns = [6, 8, 10]
    Cs = [200, 400, 600]

    # ORDER: S0 first, then S50; within each: N then C
    folder_names: List[str] = []
    for s_flag in [0, 50]:
        for N in Ns:
            for C in Cs:
                folder_names.append(f"G{N}_I{C}_S{s_flag}")

    rows: List[List[str]] = []

    for fname in folder_names:
        data_dir = os.path.join(root, fname)
        N, C, init_dev, _s_flag = dataset_params(fname)

        metrics = {
            "opt_loss": None,
            "opt_acc": None,
            "opt_kg": None,
            "dual_loss": None,
            "dual_acc": None,
            "dual_kg": None,
            "dual_kc": None,
            "recall": None,
        }

        if os.path.isdir(data_dir):
            rc, out = run_evaluate(python_exe, evaluate_py, data_dir)
            if rc == 0:
                metrics = parse_evaluate_output(out)

        rows.append(
            [
                str(N),
                str(C),
                str(init_dev),
                fmt(metrics["opt_loss"], 1),
                fmt_pct(metrics["opt_acc"], 2),   
                fmt(metrics["opt_kg"], 1),
                fmt(metrics["dual_loss"], 1),
                fmt_pct(metrics["dual_acc"], 2),    
                fmt_pct(metrics["recall"], 2),      
                fmt(metrics["dual_kg"], 1),
                fmt(metrics["dual_kc"], 1),
            ]
        )

    header1 = [
        "Dataset", "Dataset", "Dataset",
        "Optimized Elo", "Optimized Elo", "Optimized Elo",
        "Dual Elo", "Dual Elo", "Dual Elo", "Dual Elo", "Dual Elo",
    ]
    header2 = [
        "Group size", "Interaction count", "Initial score deviation",
        "Loss", "Acc (%)", "k_g",
        "Loss", "Acc (%)", "Change detection (Recall, %)", "k_g", "k_c",
    ]

    out_csv = args.out + ".csv"
    out_txt = args.out + ".txt"

    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header1)
        w.writerow(header2)
        w.writerows(rows)

    with open(out_txt, "w", encoding="utf-8") as f:
        f.write("\t".join(header1) + "\n")
        f.write("\t".join(header2) + "\n")
        for r in rows:
            f.write("\t".join(r) + "\n")

    print(f"Wrote: {out_csv}")
    print(f"Wrote: {out_txt}")
    print(f"Total rows: {len(rows)}")


if __name__ == "__main__":
    main()
