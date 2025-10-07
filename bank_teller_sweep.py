import simpy, random, numpy as np

# ----------------------------
# Helper functions
# ----------------------------
def customer(env, name, teller, service_rate, stats):
    arrival = env.now
    with teller.request() as req:
        yield req
        wait = env.now - arrival
        service = random.expovariate(service_rate)
        yield env.timeout(service)
        depart = env.now
        stats.append({
            "wait": wait,
            "service": service,
            "total": depart - arrival
        })

def run_simulation(arrival_rate, service_rate, tellers, hours, runs=5):
    results = []
    for _ in range(runs):
        env = simpy.Environment()
        teller = simpy.Resource(env, capacity=tellers)
        stats = []

        def arrival_process(env):
            while True:
                yield env.timeout(random.expovariate(arrival_rate))
                env.process(customer(env, f"C{len(stats)+1}", teller, service_rate, stats))

        env.process(arrival_process(env))
        env.run(until=hours)
        results.append(stats)
    return results

def summarize(results, tellers):
    waits = [s["wait"] for run in results for s in run]
    services = [s["service"] for run in results for s in run]
    totals = [s["total"] for run in results for s in run]
    customers = sum(len(run) for run in results)
    total_time = sum(sum(s["service"] for s in run) for run in results)
    utilization = (total_time / (3600 * len(results))) / tellers * 100  # %

    print(f"\nTellers = {tellers}")
    print(f"Avg wait time (min): {np.mean(waits):.2f}")
    print(f"Avg total time in system (min): {np.mean(totals):.2f}")
    print(f"Avg queue length (approx): {arrival_rate*np.mean(waits)/60:.2f}")
    print(f"Teller utilization: {utilization:.1f}%")
    print(f"Throughput (cust/hr): {customers/hours/len(results):.2f}")

# ----------------------------
# Main experiment
# ----------------------------
if __name__ == "__main__":
    random.seed(42)
    arrival_rate = 10 / 60     # 10 per hour → per minute
    service_rate = 12 / 60     # 12 per hour → per minute
    hours = 8 * 60             # 8-hour day (in minutes)
    runs = 5

    print("--- Bank Teller Simulation: Staffing Sweep ---")
    for tellers in [1, 2, 3, 4]:
        results = run_simulation(arrival_rate, service_rate, tellers, hours, runs)
        summarize(results, tellers)

    print("\n--- Validation: M/M/c Theoretical Comparison ---")
    def mmc_metrics(lam, mu, c):
        rho = lam / (c * mu)
        from math import factorial
        if rho >= 1: return None
        sum_terms = sum([(lam/mu)**n / factorial(n) for n in range(c)])
        p0 = 1 / (sum_terms + ((lam/mu)**c / (factorial(c) * (1 - rho))))
        lq = p0 * ((lam/mu)**c * rho) / (factorial(c) * (1 - rho)**2)
        wq = lq / lam * 60
        w = wq + (1/mu * 60)
        return rho*100, wq, w

    for c in [1,2,3,4]:
        rho, wq, w = mmc_metrics(10, 12, c)
        print(f"Tellers={c}: Util={rho:.1f}%  Wq={wq:.2f}min  W={w:.2f}min")
