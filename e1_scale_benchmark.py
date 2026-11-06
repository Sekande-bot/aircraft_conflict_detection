import csv
import math
import os
import random
import time

from aircraft import Aircraft, detect_conflict, detect_conflict_window

H_SEP = 9260.0      # 5 NM in metres
V_SEP = 305.0       # 1000 ft in metres
MAX_T = 600         # seconds of lookahead
DT = 1.0            # time step for the sweep-based methods (seconds)
N_PER_GROUP = 1000
SEED = 42
OUT_DIR = "results"


# ---------- scenario generation ----------

def random_aircraft(name, rng):
    x = rng.uniform(0, 200_000)
    y = rng.uniform(0, 200_000)
    z = rng.uniform(3000, 12000)
    speed = rng.uniform(120, 250)
    hdg = rng.uniform(0, 2 * math.pi)
    vx = speed * math.cos(hdg)
    vy = speed * math.sin(hdg)
    vz = rng.choice([-10, 0, 10])
    return Aircraft(name, x, y, z, vx, vy, vz)


def random_pair(rng):
    return random_aircraft("A", rng), random_aircraft("B", rng)


def converging_pair(rng):
    a = random_aircraft("A", rng)
    t0 = rng.uniform(60, 500)
    target = [a.pos[i] + a.vel[i] * t0 for i in range(3)]

    bpos = [
        a.pos[0] + rng.uniform(-50_000, 50_000),
        a.pos[1] + rng.uniform(-50_000, 50_000),
        a.pos[2] + rng.uniform(-1000, 1000),
    ]
    d = [target[i] - bpos[i] for i in range(3)]
    norm = math.sqrt(sum(c * c for c in d)) or 1.0
    speed = rng.uniform(120, 250)
    bvel = [c / norm * speed for c in d]
    return a, Aircraft("B", bpos[0], bpos[1], bpos[2], bvel[0], bvel[1], bvel[2])


# ---------- ground truth ----------

def ground_truth(a, b):
    """True if horizontal AND vertical separation are both below
    the thresholds at the same moment within MAX_T seconds."""
    t = 0.0
    while t <= MAX_T:
        pa = [a.pos[i] + a.vel[i] * t for i in range(3)]
        pb = [b.pos[i] + b.vel[i] * t for i in range(3)]
        horiz = math.hypot(pa[0] - pb[0], pa[1] - pb[1])
        vert = abs(pa[2] - pb[2])
        if horiz < H_SEP and vert < V_SEP:
            return True
        t += DT
    return False


# ---------- detectors under test ----------

DETECTORS = {
    "v1_closest_approach": lambda a, b: detect_conflict(
        a, b, lookahead_time=MAX_T),
    "v2_window_sweep": lambda a, b: detect_conflict_window(
        a, b, lookahead_time=MAX_T, dt=DT),
}


# ---------- evaluation ----------

def build_scenarios(n, seed):
    rng = random.Random(seed)
    scenarios = []
    for label, gen in [("random", random_pair), ("converging", converging_pair)]:
        for i in range(n):
            a, b = gen(rng)
            scenarios.append({
                "group": label,
                "scenario": f"{label}_{i:05d}",
                "a": a,
                "b": b,
                "truth": ground_truth(a, b),
            })
    return scenarios


def evaluate(det_name, det_fn, scenarios):
    rows, timings = [], []
    counts = {g: {"tp": 0, "fp": 0, "tn": 0, "fn": 0}
              for g in ("random", "converging", "ALL")}

    for s in scenarios:
        t0 = time.perf_counter()
        res = det_fn(s["a"], s["b"])
        timings.append(time.perf_counter() - t0)

        pred = bool(res["conflict"])
        truth = s["truth"]
        if pred and truth:
            key = "tp"
        elif pred and not truth:
            key = "fp"
        elif not pred and truth:
            key = "fn"
        else:
            key = "tn"

        counts[s["group"]][key] += 1
        counts["ALL"][key] += 1

        rows.append({
            "group": s["group"],
            "scenario": s["scenario"],
            "truth": int(truth),
            "predicted": int(pred),
            "t_closest": res.get("t_closest"),
            "min_horiz_m": res.get("min_horiz_dist"),
            "min_vert_m": res.get("min_vert_dist"),
        })

    return rows, counts, timings


def pct(num, den):
    return f"{100 * num / den:.2f}%" if den else "n/a"


def format_summary(det_name, counts, timings):
    lines = [f"=== {det_name} ==="]
    for g in ("random", "converging", "ALL"):
        c = counts[g]
        pos = c["tp"] + c["fn"]
        neg = c["fp"] + c["tn"]
        n = pos + neg
        lines.append(
            f"[{g}] n={n}  true conflicts={pos}  "
            f"TP={c['tp']} FP={c['fp']} TN={c['tn']} FN={c['fn']}\n"
            f"    detection rate={pct(c['tp'], pos)}  "
            f"false alarm rate={pct(c['fp'], neg)}"
        )
    avg_ms = 1000 * sum(timings) / len(timings)
    lines.append(
        f"    runtime: avg {avg_ms:.3f} ms/pair, "
        f"total {sum(timings):.3f} s"
    )
    return "\n".join(lines)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    scenarios = build_scenarios(N_PER_GROUP, SEED)

    all_summaries = []
    for det_name, det_fn in DETECTORS.items():
        rows, counts, timings = evaluate(det_name, det_fn, scenarios)

        csv_path = os.path.join(OUT_DIR, f"e1_scenarios_{det_name}.csv")
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)

        summary = format_summary(det_name, counts, timings)
        all_summaries.append(summary)

    final = "\n\n".join(all_summaries)
    with open(os.path.join(OUT_DIR, "e1_summary.txt"), "w") as f:
        f.write(final + "\n")
    print(final)


if __name__ == "__main__":
    main()