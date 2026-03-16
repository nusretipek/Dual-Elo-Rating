import os
import json
import argparse
import numpy as np


def main():
    ap = argparse.ArgumentParser(description="Summarize matching + metrics from meta.json and results.json.")
    ap.add_argument("data_dir", type=str, help="Folder containing meta.json (e.g., G9_I200_U5)")
    args = ap.parse_args()

    DATA_DIR = args.data_dir
    RESULTS_DIR = DATA_DIR.rstrip("/").rstrip("\\") + "_Results"

    meta_path = os.path.join(DATA_DIR, "meta.json")
    results_path = os.path.join(RESULTS_DIR, "results.json")

    with open(meta_path, "r") as f:
        metadata = json.load(f)

    with open(results_path, "r") as f:
        results = json.load(f)

    meta_dict = {
        str(item["seed"]): {
            "sudden_events": item["sudden_events"],
            "final_scores": item.get("final_scores"),
        }
        for item in metadata
    }

    total_true = 0
    total_tp = 0
    WIN_TOL = 10
    EPS = 1e-12

    opt_losses, opt_accs = [], []
    full_losses, full_accs = [], []
    opt_kgs, full_kgs, full_kcs = [], [], []
    opt_rel_err = []
    full_rel_err = []

    for seed, meta in meta_dict.items():
        model_out = results.get(seed)
        if not model_out:
            continue

        opt = model_out.get("optimized_elo")
        full = model_out.get("full_model")
        best = (full or {}).get("best_combinational")
        if not opt or not full or not best:
            continue

        opt_losses.append(float(opt["loss"]))
        opt_accs.append(float(opt["accuracy"]))
        full_losses.append(float(best["loss"]))
        full_accs.append(float(best["accuracy"]))

        opt_kgs.append(float(opt["k_g"]))
        full_kgs.append(float(full["k_g"]))
        full_kcs.append(float(full["k_c"]))

        # score comparison
        meta_scores = meta.get("final_scores")
        opt_scores = opt.get("final_elo_scores")
        full_scores = full.get("final_elo_scores")
        if meta_scores is not None and opt_scores is not None and full_scores is not None:
            m = np.asarray(meta_scores, dtype=float)
            o = np.asarray(opt_scores, dtype=float)
            fu = np.asarray(full_scores, dtype=float)
            if m.shape == o.shape and m.shape == fu.shape and m.size > 0:
                den = np.where(np.abs(m) < EPS, np.nan, np.abs(m))
                opt_rel_err.append(float(np.nanmean(np.abs(o - m) / den)))
                full_rel_err.append(float(np.nanmean(np.abs(fu - m) / den)))

        # matching
        true_events = meta["sudden_events"]
        true_list = [(int(t), int(low)) for (t, low, _high) in true_events]
        total_true += len(true_list)

        pred_map = best.get("indices", {}) or {}
        pred_list = sorted((int(k), int(v[0]), int(v[1])) for k, v in pred_map.items())

        true_by_time = {}
        for i, (t, low) in enumerate(true_list):
            true_by_time.setdefault(t, []).append(i)

        matched_true = set()
        used_pred = set()

        # exact idx matches
        for idx, a, b in pred_list:
            if idx in true_by_time:
                for i in true_by_time[idx]:
                    if i not in matched_true:
                        matched_true.add(i)
                        used_pred.add(idx)
                        break

        # relaxed +/- WIN_TOL and a==low
        for i, (t, low) in enumerate(true_list):
            if i in matched_true:
                continue
            candidates = [
                idx
                for (idx, a, b) in pred_list
                if idx not in used_pred and abs(idx - t) <= WIN_TOL and a == low
            ]
            if candidates:
                best_idx = min(candidates, key=lambda j: abs(j - t))
                matched_true.add(i)
                used_pred.add(best_idx)

        total_tp += len(matched_true)

    recall = total_tp / total_true if total_true > 0 else 0.0

    print("===== Matching Statistics =====")
    print(f"Total True Events: {total_true}")
    print(f"Total True Positives: {total_tp}")
    print(f"Recall: {recall:.4f}")

    print("\n===== Average Loss / Accuracy =====")
    print(
        f"Optimized Elo   - Avg Loss: {np.mean(opt_losses):.4f}, Avg Acc: {np.mean(opt_accs):.4f}"
        if opt_losses
        else "No optimized metrics"
    )
    print(
        f"Full Model Best - Avg Loss: {np.mean(full_losses):.4f}, Avg Acc: {np.mean(full_accs):.4f}"
        if full_losses
        else "No full-model metrics"
    )

    print("\n===== Average Parameters =====")
    print(f"Average Optimized k(g): {np.mean(opt_kgs):.4f}" if opt_kgs else "No optimized k(g)")
    print(f"Average Full Model k(g): {np.mean(full_kgs):.4f}" if full_kgs else "No full k(g)")
    print(f"Average Full Model k(c): {np.mean(full_kcs):.4f}" if full_kcs else "No full k(c)")

    print("\n===== Score Difference vs Meta (mean(|pred-meta|/meta), decimal) =====")
    print(f"Meta vs Optimized: {np.mean(opt_rel_err):.6f}" if opt_rel_err else "No meta-vs-optimized score comparisons")
    print(f"Meta vs Full:      {np.mean(full_rel_err):.6f}" if full_rel_err else "No meta-vs-full score comparisons")


if __name__ == "__main__":
    main()
