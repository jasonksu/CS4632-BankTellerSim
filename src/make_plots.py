import json
import matplotlib.pyplot as plt
from pathlib import Path
import csv

def load_summary_json(exp_name):
    path = Path(f"results/summary/{exp_name}.json")
    if not path.exists():
        raise FileNotFoundError(f"No summary file found for {exp_name}")
    with path.open() as f:
        return json.load(f)

def plot_staffing_sweep(exp_names):
    tellers = []
    waits = []
    utils = []
    for exp in exp_names:
        data = load_summary_json(exp)
        tellers.append(data["parameters"]["tellers"])
        waits.append(data["avg_wait_min"])
        utils.append(data["utilization_pct"])

    plt.figure(figsize=(7, 5))
    plt.plot(tellers, waits, marker="o", label="Average Wait (min)")
    plt.plot(tellers, utils, marker="s", label="Teller Utilization (%)")
    plt.title("Bank Teller Simulation: Staffing Sweep")
    plt.xlabel("Number of Tellers")
    plt.ylabel("Performance Metric")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("results/summary/staffing_sweep.png", dpi=200)
    plt.show()

if __name__ == "__main__":
    # Example: assuming you’ll have results for 1–4 tellers
    exp_names = [f"baseline_c{i}" for i in range(1, 5)]
    plot_staffing_sweep(exp_names)
