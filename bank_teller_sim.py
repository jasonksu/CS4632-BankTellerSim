# bank_teller_sim.py
"""
Bank Teller Simulation using SimPy
----------------------------------
This program simulates how customers are served at a bank with a few tellers.
Customers arrive randomly, wait in a single line, and get served by the first available teller.
The program tracks the average wait time, teller utilization, and other stats.

Time is measured in minutes.

Example:
    python bank_teller_sim.py --lam 10 --mu 12 --tellers 2 --hours 8 --runs 10
"""

import simpy
import random
import statistics
import argparse

# ------------------------------------------------------
# Helper function for exponential times (arrivals & service)
# ------------------------------------------------------
def expovariate_from_rate_per_hour(rate_per_hour):
    """Return an exponential random value in minutes based on a rate per hour."""
    if rate_per_hour <= 0:
        raise ValueError("Rate must be positive.")
    rate_per_minute = rate_per_hour / 60.0
    return random.expovariate(rate_per_minute)

# ------------------------------------------------------
# Data collector for recording simulation results
# ------------------------------------------------------
class Stats:
    def __init__(self):
        self.wait_times = []        # how long each customer waits
        self.service_times = []     # how long service takes
        self.system_times = []      # total time in system (wait + service)
        self.area_q = 0.0           # used to calculate average queue length
        self.last_time = 0.0
        self.teller_busy_time = 0.0 # total time tellers are busy
        self.total_teller_time = 0.0

    def update_queue_area(self, env, q_length):
        """Update area under the queue length curve."""
        dt = env.now - self.last_time
        self.area_q += q_length * dt
        self.last_time = env.now

# ------------------------------------------------------
# Teller resource with utilization tracking
# ------------------------------------------------------
class TellerPool:
    def __init__(self, env, num_tellers, stats):
        self.env = env
        self.resource = simpy.Resource(env, capacity=num_tellers)
        self.stats = stats
        self.num_tellers = num_tellers
        self._busy = 0
        self._last_change = env.now
        self._monitor = env.process(self._track_utilization())

    def request(self):
        return self.resource.request()

    def release(self, req):
        return self.resource.release(req)

    def _track_utilization(self):
        """Keeps track of how many tellers are busy over time."""
        while True:
            current_busy = len(self.resource.users)
            if current_busy != self._busy:
                dt = self.env.now - self._last_change
                self.stats.teller_busy_time += self._busy * dt
                self._busy = current_busy
                self._last_change = self.env.now
            yield self.env.timeout(0.1)  # small delay for updates

# ------------------------------------------------------
# Customer process
# ------------------------------------------------------
def customer(env, name, tellers, stats, mu_per_hour):
    arrival_time = env.now
    stats.update_queue_area(env, len(tellers.resource.queue))

    # Wait for teller
    with tellers.request() as req:
        yield req
        start_service = env.now
        wait = start_service - arrival_time
        stats.wait_times.append(wait)

        # Service time
        service_time = expovariate_from_rate_per_hour(mu_per_hour)
        stats.service_times.append(service_time)
        yield env.timeout(service_time)

        finish_time = env.now
        stats.system_times.append(finish_time - arrival_time)
        stats.update_queue_area(env, len(tellers.resource.queue))

# ------------------------------------------------------
# Customer arrival generator
# ------------------------------------------------------
def arrival_process(env, tellers, stats, lam_per_hour, mu_per_hour, sim_minutes):
    i = 0
    while env.now < sim_minutes:
        interarrival = expovariate_from_rate_per_hour(lam_per_hour)
        yield env.timeout(interarrival)
        i += 1
        env.process(customer(env, f"Customer_{i}", tellers, stats, mu_per_hour))

# ------------------------------------------------------
# Run one replication
# ------------------------------------------------------
def run_replication(lam_per_hour=10, mu_per_hour=12, tellers=2, hours=8, seed=None):
    if seed is not None:
        random.seed(seed)
    env = simpy.Environment()
    stats = Stats()
    teller_pool = TellerPool(env, tellers, stats)
    sim_minutes = hours * 60

    env.process(arrival_process(env, teller_pool, stats, lam_per_hour, mu_per_hour, sim_minutes))
    env.run(until=sim_minutes)

    # Final utilization update
    dt = env.now - teller_pool._last_change
    stats.teller_busy_time += teller_pool._busy * dt
    stats.total_teller_time = tellers * sim_minutes

    # Calculate metrics
    avg_wait = statistics.mean(stats.wait_times) if stats.wait_times else 0
    avg_service = statistics.mean(stats.service_times) if stats.service_times else 0
    avg_system = statistics.mean(stats.system_times) if stats.system_times else 0
    avg_q_len = stats.area_q / sim_minutes if sim_minutes > 0 else 0
    utilization = stats.teller_busy_time / stats.total_teller_time if stats.total_teller_time > 0 else 0
    throughput = (len(stats.system_times) / sim_minutes) * 60 if sim_minutes > 0 else 0

    p95_wait = None
    if len(stats.wait_times) >= 20:
        p95_wait = statistics.quantiles(stats.wait_times, n=20)[18]

    return {
        "avg_wait_min": avg_wait,
        "p95_wait_min": p95_wait,
        "avg_service_min": avg_service,
        "avg_system_min": avg_system,
        "avg_queue_len": avg_q_len,
        "utilization": utilization,
        "throughput_per_hour": throughput,
        "customers_completed": len(stats.system_times),
        "hours": hours,
        "lam": lam_per_hour,
        "mu": mu_per_hour,
        "tellers": tellers,
    }

# ------------------------------------------------------
# Run multiple replications
# ------------------------------------------------------
def run_experiment(lam_per_hour=10, mu_per_hour=12, tellers=2, hours=8, runs=10, seed=123):
    results = []
    for r in range(runs):
        res = run_replication(lam_per_hour, mu_per_hour, tellers, hours, seed + r)
        results.append(res)

    def avg(key):
        vals = [r[key] for r in results if r[key] is not None]
        return statistics.mean(vals) if vals else 0

    summary = {
        "avg_wait_min": avg("avg_wait_min"),
        "p95_wait_min": avg("p95_wait_min"),
        "avg_service_min": avg("avg_service_min"),
        "avg_system_min": avg("avg_system_min"),
        "avg_queue_len": avg("avg_queue_len"),
        "utilization": avg("utilization"),
        "throughput_per_hour": avg("throughput_per_hour"),
        "runs": runs,
    }

    return summary

# ------------------------------------------------------
# Main function for CLI
# ------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Bank Teller Simulation")
    parser.add_argument("--lam", type=float, default=10, help="Customer arrival rate (per hour)")
    parser.add_argument("--mu", type=float, default=12, help="Service rate (per hour per teller)")
    parser.add_argument("--tellers", type=int, default=2, help="Number of tellers")
    parser.add_argument("--hours", type=float, default=8, help="Simulation duration (hours)")
    parser.add_argument("--runs", type=int, default=10, help="Number of replications")
    parser.add_argument("--seed", type=int, default=123, help="Random seed")
    args = parser.parse_args()

    summary = run_experiment(args.lam, args.mu, args.tellers, args.hours, args.runs, args.seed)

    print("\n--- Bank Teller Simulation Results ---")
    print(f"λ = {args.lam}/hr, μ = {args.mu}/hr, tellers = {args.tellers}, runs = {args.runs}")
    print(f"Avg wait time (min): {summary['avg_wait_min']:.2f}")
    if summary['p95_wait_min']:
        print(f"95th percentile wait: {summary['p95_wait_min']:.2f}")
    print(f"Avg service time (min): {summary['avg_service_min']:.2f}")
    print(f"Avg total time in system (min): {summary['avg_system_min']:.2f}")
    print(f"Avg queue length: {summary['avg_queue_len']:.2f}")
    print(f"Teller utilization: {summary['utilization']*100:.1f}%")
    print(f"Throughput (customers/hour): {summary['throughput_per_hour']:.2f}")
    print("--------------------------------------\n")

if __name__ == "__main__":
    main()
