import os
import json
import argparse
import numpy as np


class EloRatingBasedSimulationData:
    def __init__(
        self,
        n: int,
        T: int,
        kl: int,
        kh: int,
        uniform: bool,
        sudden: int,                          
        seed: int = 0):
        
        assert isinstance(n, int) and n > 0
        assert isinstance(T, int) and T > 0
        assert isinstance(kl, int) and kl > 0
        assert isinstance(kh, int) and kh > 0
        assert isinstance(uniform, bool)
        assert isinstance(sudden, int) and 0 <= sudden <= n

        self.n = n
        self.T = T
        self.kl = kl
        self.kh = kh
        self.uniform = uniform
        self.sudden = sudden
        self.seed = seed

        rng = np.random.default_rng(self.seed)
        r = rng.random()
        if r < 0.5:
            self.sudden = 1
            
        self.scores = None
        self.interactions = None
        self.sudden_report = []

    def sampleInitialScores(self, u: float, s: float) -> np.ndarray:
        np.random.seed(self.seed)
        if self.uniform:
            assert s >= u
            if self.n == 1:
                self.scores = np.array([u], dtype=float)
                return self.scores
            self.scores = np.linspace(u, s, num=self.n, dtype=float)
            np.random.shuffle(self.scores)
        else:
            mean, sigma = u, s
            assert sigma >= 0
            self.scores = np.random.normal(loc=mean, scale=sigma, size=self.n).astype(float)
        return self.scores

    def _expected_win_prob(self, sa: float, sb: float) -> float:
        return 1.0 / (1.0 + np.exp(-0.01 * (sa - sb)))

    def sampleInteractions(self):
        assert hasattr(self, "scores") and self.scores is not None
        rng = np.random.default_rng(self.seed)

        interactions = []
        self.sudden_report = []
        used_low = set()

        low_t = self.T // 10
        high_t = (2 * self.T) // 3

        if self.sudden > 0 and high_t >= low_t:
            window_len = high_t - low_t + 1

            min_sep = max(1, window_len // (2 * self.sudden)) if self.sudden > 1 else 0

            def pick_times(min_gap: int) -> list[int]:
                chosen = []
                attempts = 0
                max_attempts = 20000
                while len(chosen) < self.sudden and attempts < max_attempts:
                    t0 = int(rng.integers(low=low_t, high=high_t + 1))
                    if t0 in chosen:
                        attempts += 1
                        continue
                    if all(abs(t0 - t1) >= min_gap for t1 in chosen):
                        chosen.append(t0)
                    attempts += 1
                return chosen

            sudden_times_list = pick_times(min_sep)

            while len(sudden_times_list) < self.sudden and min_sep > 0:
                min_sep -= 1
                sudden_times_list = pick_times(min_sep)

            sudden_times = np.array(sudden_times_list, dtype=int)
        else:
            sudden_times = np.array([], dtype=int)

        sudden_counts = {}
        for t0 in sudden_times.tolist():
            sudden_counts[t0] = sudden_counts.get(t0, 0) + 1

        boost_idx = None
        boost_remaining = 0
        boost_weight = 2.0
        for t in range(self.T):
            if sudden_counts.get(t, 0) > 0:
                for _ in range(sudden_counts[t]):
                    order_asc = np.argsort(self.scores)
                    lower_k = max(1, self.n // 4)
                    top_k = max(1, (self.n + 1) // 3)

                    lower_half = order_asc[:lower_k].tolist()
                    top_third = order_asc[-top_k:].tolist()

                    low_pool = [i for i in lower_half if i not in used_low]
                    if not low_pool:
                        low_pool = [i for i in order_asc.tolist() if i not in used_low]
                    if not low_pool:
                        continue

                    low_idx = int(rng.choice(low_pool))

                    high_pool = [i for i in top_third if i != low_idx]
                    if not high_pool:
                        high_pool = [i for i in order_asc[::-1].tolist() if i != low_idx]
                    high_idx = int(rng.choice(high_pool))

                    p_low = self._expected_win_prob(float(self.scores[low_idx]), float(self.scores[high_idx]))
                    delta = self.kh * (1.0 - p_low)
                    self.scores[low_idx] += delta
                    self.scores[high_idx] -= delta
                    interactions.append([low_idx, high_idx])

                    used_low.add(low_idx)
                    self.sudden_report.append((int(t), int(low_idx), int(high_idx)))
                    boost_idx = low_idx
                    boost_remaining = self.T // 20
                continue

            if boost_remaining > 0 and boost_idx is not None and self.n >= 2:
                weights = np.ones(self.n, dtype=float)
                weights[int(boost_idx)] = boost_weight
                p_sel = weights / weights.sum()
                a, b = rng.choice(self.n, size=2, replace=False, p=p_sel)
            else:
                a, b = rng.choice(self.n, size=2, replace=False)

            sa, sb = float(self.scores[a]), float(self.scores[b])

            if boost_remaining > 0 and boost_idx is not None:
                boost_win_adv = float(self.scores.max() - self.scores[boost_idx])
                if int(a) == int(boost_idx):
                    sa += boost_win_adv
                elif int(b) == int(boost_idx):
                    sb += boost_win_adv

            p = self._expected_win_prob(sa, sb)
            r = rng.random()

            if r < p:
                delta = self.kl * (1.0 - p)
                self.scores[a] += delta
                self.scores[b] -= delta
                interactions.append([int(a), int(b)])
            else:
                delta = self.kl * p
                self.scores[b] += delta
                self.scores[a] -= delta
                interactions.append([int(b), int(a)])

            if boost_remaining > 0:
                boost_remaining -= 1
                if boost_remaining == 0:
                    boost_idx = None

        self.interactions = np.asarray(interactions, dtype=int)

    def saveData(self, path: str):
        assert hasattr(self, "interactions") and self.interactions is not None
        data = np.asarray(self.interactions, dtype=int)
        assert data.ndim == 2 and data.shape[1] == 2
        os.makedirs(os.path.dirname(path), exist_ok=True) if os.path.dirname(path) else None
        np.savetxt(path, data, fmt="%d", delimiter=",", header="Initiator,Receiver", comments="")

def generateData(
    n: int,
    T: int,
    kl: int,
    kh: int,
    uniform: bool,
    sudden: int,
    u: float,
    s: float,
    out_dir: str = "G5_I500",
    seed_start: int = 0,
    seed_end: int = 99,
):
    os.makedirs(out_dir, exist_ok=True)
    meta_path = os.path.join(out_dir, "meta.json")

    all_meta = []

    for seed in range(seed_start, seed_end + 1):
        sim = EloRatingBasedSimulationData(
            n=n,
            T=T,
            kl=kl,
            kh=kh,
            uniform=uniform,
            sudden=sudden,
            seed=seed,
        )
        sim.sampleInitialScores(u=u, s=s)
        sim.sampleInteractions()

        csv_path = os.path.join(out_dir, f"{seed}.csv")
        sim.saveData(csv_path)

        all_meta.append(
            {
                "seed": seed,
                "sudden_events": sim.sudden_report,
                "final_scores": sim.scores.tolist(),
            }
        )

    with open(meta_path, "w", encoding="utf-8") as mf:
        json.dump(all_meta, mf, indent=2)


def main():
    ap = argparse.ArgumentParser(description="Generate Elo-based simulation interaction CSVs.")

    ap.add_argument("--n", type=int, required=True, help="Number of players/entities.")
    ap.add_argument("--T", type=int, required=True, help="Number of interactions.")
    ap.add_argument("--kl", type=int, required=True, help="Low (regular) K-factor.")
    ap.add_argument("--kh", type=int, required=True, help="High K-factor (sudden event).")
    ap.add_argument("--sudden", type=int, default=0, help="Number of sudden events (0..n).")

    ap.add_argument(
        "--uniform",
        action="store_true",
        help="If set: initial scores uniform in [u,s]. If omitted: Normal(mean=u, sigma=s).",
    )

    ap.add_argument("--u", type=float, required=True, help="Uniform lower bound OR Normal mean.")
    ap.add_argument("--s", type=float, required=True, help="Uniform upper bound OR Normal sigma.")
    ap.add_argument("--out-dir", type=str, default="G5_I500", help="Output directory.")
    ap.add_argument("--seed-start", type=int, default=0, help="First seed (inclusive).")
    ap.add_argument("--seed-end", type=int, default=99, help="Last seed (inclusive).")

    args = ap.parse_args()

    generateData(
        n=args.n,
        T=args.T,
        kl=args.kl,
        kh=args.kh,
        uniform=args.uniform,
        sudden=args.sudden,
        u=args.u,
        s=args.s,
        out_dir=args.out_dir,
        seed_start=args.seed_start,
        seed_end=args.seed_end,
    )

if __name__ == "__main__":
    main()
    