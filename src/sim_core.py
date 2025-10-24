import simpy
import random
import math
import statistics
from typing import Dict, Any


class QueueAreaTracker:
    def __init__(self):
        self.area_q = 0.0
        self.last_t = 0.0

    def update(self, env_now: float, current_q_len: int):
        dt = env_now - self.last_t
        if dt > 0:
            self.area_q += current_q_len * dt
            self.last_t = env_now

    def average(self, horizon_min: float) -> float:
        if horizon_min <= 0:
            return 0.0
        return self.area_q / horizon_min


class UtilizationTracker:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.last_t = 0.0
        self.busy_servers = 0
        self.busy_area = 0.0

    def _accumulate(self, now: float):
        dt = now - self.last_t
        if dt > 0:
            self.busy_area += self.busy_servers * dt
            self.last_t = now

    def start_service(self, now: float):
        self._accumulate(now)
        self.busy_servers = min(self.capacity, self.busy_servers + 1)

    def end_service(self, now: float):
        self._accumulate(now)
        self.busy_servers = max(0, self.busy_servers - 1)

    def finalize(self, now: float):
        self._accumulate(now)

    def utilization(self, horizon_min: float) -> float:
        if horizon_min <= 0 or self.capacity <= 0:
            return 0.0
        return self.busy_area / (self.capacity * horizon_min)


class BankTellerSim:
    def __init__(self, cfg: Dict[str, Any]):
        self.lam_per_hr = float(cfg["arrival_rate_per_hour"])
        self.mu_per_hr  = float(cfg["service_rate_per_hour"])
        self.c          = int(cfg["tellers"])
        self.hours      = float(cfg["hours"])
        self.seed       = int(cfg.get("seed", 123))
        self.snapshot_dt = float(cfg.get("snapshot_minutes", 1.0))
        self.piecewise  = cfg.get("piecewise_arrival_per_hour", None)

        random.seed(self.seed)

        self.env = simpy.Environment()
        self.resource = simpy.Resource(self.env, capacity=self.c)
        self.qtracker = QueueAreaTracker()
        self.utracker = UtilizationTracker(capacity=self.c)

        self.waits = []
        self.services = []
        self.totals = []
        self.arrivals = 0
        self.completions = 0

        if self.piecewise:
            self.piecewise = sorted(self.piecewise, key=lambda s: s["start_min"])

    def _current_lambda_per_min(self, tmin: float) -> float:
        if not self.piecewise:
            return self.lam_per_hr / 60.0
        r = self.lam_per_hr
        for seg in self.piecewise:
            if tmin >= float(seg["start_min"]):
                r = float(seg["rate_per_hour"])
            else:
                break
        return r / 60.0

    def _draw_interarrival(self, tmin: float) -> float:
        lam_per_min = self._current_lambda_per_min(tmin)
        if lam_per_min <= 0:
            return math.inf
        return random.expovariate(lam_per_min)

    def customer(self, name: str):
        arrival = self.env.now
        self.arrivals += 1
        self.qtracker.update(self.env.now, len(self.resource.queue))

        with self.resource.request() as req:
            yield req
            self.qtracker.update(self.env.now, len(self.resource.queue))
            wait = self.env.now - arrival
            self.waits.append(wait)

            self.utracker.start_service(self.env.now)
            service = random.expovariate(self.mu_per_hr / 60.0)
            self.services.append(service)
            yield self.env.timeout(service)
            self.utracker.end_service(self.env.now)

            self.qtracker.update(self.env.now, len(self.resource.queue))
            depart = self.env.now
            self.totals.append(depart - arrival)
            self.completions += 1

    def arrival_process(self, horizon_min: float):
        i = 0
        while self.env.now < horizon_min:
            iat = self._draw_interarrival(self.env.now)
            if math.isinf(iat):
                break
            yield self.env.timeout(iat)
            i += 1
            self.env.process(self.customer(f"C{i}"))

    def run(self):
        horizon_min = self.hours * 60.0
        self.env.process(self.arrival_process(horizon_min))
        self.env.run(until=horizon_min)
        self.utracker.finalize(self.env.now)
        self.qtracker.update(self.env.now, len(self.resource.queue))

        avg_wait = statistics.mean(self.waits) if self.waits else 0.0
        avg_service = statistics.mean(self.services) if self.services else 0.0
        avg_total = statistics.mean(self.totals) if self.totals else 0.0
        p95_wait = None
        if len(self.waits) >= 20:
            p95_wait = statistics.quantiles(self.waits, n=20)[18]

        summary = {
            "avg_wait_min": avg_wait,
            "p95_wait_min": p95_wait,
            "avg_service_min": avg_service,
            "avg_total_min": avg_total,
            "avg_queue_len": self.qtracker.average(horizon_min),
            "utilization_pct": self.utracker.utilization(horizon_min) * 100.0,
            "arrivals": self.arrivals,
            "completions": self.completions,
            "throughput_per_hour": (self.completions / self.hours) if self.hours > 0 else 0.0
        }
        raw = {
            "waits": self.waits,
            "services": self.services,
            "totals": self.totals
        }
        return summary, raw
