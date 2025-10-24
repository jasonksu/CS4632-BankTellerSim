import json
import csv
import time
from pathlib import Path
import statistics
from sim_core import BankTellerSim


def ensure_dirs():
    Path("results/runs").mkdir(parents=True, exist_ok=True)
    Path("results/summary").mkdir(parents=True, exist_ok=True)


def run_one(cfg: dict):
    sim = BankTellerSim(cfg)
    summary, _ = sim.run()
    # flatten parameters we care about into the row
    row = {
        "avg_wait_min": round(summary["avg_wait_min"], 4),
        "p95_wait_min": round(summary["p95_wait_min"], 4) if summary["p95_wait_min"] is not None else "",
        "avg_service_min": round(summary["avg_service_min"], 4),
        "avg_total_min": round(summary["avg_total_min"], 4),
        "avg_queue_len": round(summary["avg_queue_len"], 4),
        "utilization_pct": round(summary["utilization_pct"], 2),
        "throughput_per_hour": round(summary["throughput_per_hour"], 4),
        "arrivals": summary["arrivals"],
        "completions": summary["completions"],
        "tellers": cfg["tellers"],
        "lam_per_hr": cfg["arrival_rate_per_hour"],
        "mu_per_hr": cfg["service_rate_per_hour"],
        "hours": cfg["hours"],
        "seed": cfg.get("seed", "")
    }
    return row


def aggregate(rows: list) -> dict:
    def collect(key):
        vals = [r[key] for r in rows if r[key] != ""]
        return vals

    def mean_or_zero(vals):
        return statistics.mean(vals) if vals else 0.0

    agg = {
        "replications": len(rows),
        "avg_wait_min": mean_or_zero(collect("avg_wait_min")),
        "p95_wait_min": statistics.quantiles(collect("avg_wait_min"), n=20)[18] if len(rows) >= 20 else "",
        "avg_service_min": mean_or_zero(collect("avg_service_min")),
        "avg_total_min": mean_or_zero(collect("avg_total_min")),
        "avg_queue_len": mean_or_zero(collect("avg_queue_len")),
        "utilization_pct": mean_or_zero(collect("utilization_pct")),
        "throughput_per_hour": mean_or_zero(collect("throughput_per_hour")),
    }
    return agg


def save_outputs(experiment_name: str, rows: list, cfg: dict, wall_clock_s: float):
    # per-replication CSV
    run_dir = Path(f"results/runs/{experiment_name}")
    run_dir.mkdir(parents=True, exist_ok=True)
    runs_csv = run_dir / "runs.csv"
    if rows:
        with runs_csv.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

    # summary CSV + JSON
    summary = aggregate(rows)
    summary["parameters"] = cfg
    summary["wall_clock_seconds"] = round(wall_clock_s, 3)

    summary_dir = Path("results/summary")
    sum_csv_path = summary_dir / f"{experiment_name}.csv"
    with sum_csv_path.open("w", newline="") as f:
        w = csv.writer(f)
        for k, v in summary.items():
            if k == "parameters":
                continue
            w.writerow([k, v])

    sum_json_path = summary_dir / f"{experiment_name}.json"
    with sum_json_path.open("w") as f:
        json.dump(summary, f, indent=2)

    return runs_csv, sum_csv_path, sum_json_path


def main(config_path: str):
    ensure_dirs()
    cfg = json.loads(Path(config_path).read_text())
    name = cfg["experiment_name"]
    reps = int(cfg.get("replications", 5))
    seed_base = int(cfg.get("seed_base", 1000))

    print(f"Experiment: {name}  |  replications: {reps}")
    rows = []
    t0 = time.time()
    for r in range(reps):
        cfg["seed"] = seed_base + r
        row = run_one(cfg)
        row["rep"] = r + 1
        rows.append(row)
        print(f"  finished rep {r+1}/{reps}  avg_wait={row['avg_wait_min']} min  util={row['utilization_pct']}%")
    elapsed = time.time() - t0

    runs_csv, sum_csv, sum_json = save_outputs(name, rows, cfg, elapsed)

    print("\n--- Summary ---")
    print(f"Saved per-rep CSV:   {runs_csv}")
    print(f"Saved summary CSV:   {sum_csv}")
    print(f"Saved summary JSON:  {sum_json}")
    print(f"Wall clock seconds:  {round(elapsed, 3)}")


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--config", required=True, help="Path to a JSON config file")
    args = p.parse_args()
    main(args.config)
