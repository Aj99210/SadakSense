"""SadakPlan: choose repairs under a budget with an exact solver (OR-Tools)."""
from dataclasses import dataclass

TREATMENTS = {"patch": (1.0, 0.45), "drainage": (1.6, 0.55), "resurface": (4.0, 0.95)}  # (cost x, risk removed share)


@dataclass
class Candidate:
    segment_id: int
    length_km: float
    risk: float
    structural: bool


def build_options(c: Candidate, base_cost_per_km: float = 4.0e5):
    opts = []
    for name, (cm, share) in TREATMENTS.items():
        if name == "patch" and c.structural:
            continue        # patching structural damage is not durable
        opts.append((name, cm * base_cost_per_km * c.length_km, c.risk * share))
    return opts


def solve(cands, budget: float, max_roads: int = 32):
    from ortools.linear_solver import pywraplp
    s = pywraplp.Solver.CreateSolver("SCIP")
    meta = []
    for c in cands:
        for name, cost, removed in build_options(c):
            meta.append((c.segment_id, name, cost, removed, s.BoolVar(f"x_{c.segment_id}_{name}")))
    for sid in {m[0] for m in meta}:                       # at most one treatment per road
        s.Add(sum(v for (i, _, _, _, v) in meta if i == sid) <= 1)
    s.Add(sum(cost * v for (_, _, cost, _, v) in meta) <= budget)
    s.Add(sum(v for (*_, v) in meta) <= max_roads)
    s.Maximize(sum(r * v for (_, _, _, r, v) in meta))
    s.Solve()
    return [(i, n, cost, r) for (i, n, cost, r, v) in meta if v.solution_value() > 0.5]
