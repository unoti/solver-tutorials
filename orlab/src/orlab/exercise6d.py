"""Iterative tank utilization solver that concentrates leftover capacity."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence, Tuple

import math
import sys

import pandas as pd
from ortools.linear_solver import pywraplp


@dataclass
class SolveDiagnostics:
    """Lightweight diagnostics emitted by the standalone runner."""

    ok: bool
    objective_value: float | None
    iterations: int


def _build_solver() -> pywraplp.Solver:
    solver = pywraplp.Solver.CreateSolver("SCIP")
    if solver is None:
        raise RuntimeError("Unable to create OR-Tools SCIP solver instance.")
    return solver


def _lexicographic_weights(spare_capacity: pd.Series) -> dict[int, float]:
    """Return weights that enforce a lexicographic objective.

    Tanks with tighter spare capacity receive exponentially larger weights so
    that reducing their stranded volume dominates any trade-off involving lower
    priority tanks.
    """

    priority_order = list(spare_capacity.sort_values(kind="mergesort").index)
    base = float(spare_capacity.sum()) + 1.0
    if base <= 0.0:
        raise ValueError("Spare capacity must yield a positive lexicographic base.")

    log_base = math.log(base)
    weights: dict[int, float] = {}
    max_exponent = len(priority_order) - 1
    margin = 1.0
    offset = max(
        0.0,
        max_exponent * log_base - math.log(sys.float_info.max) + margin,
    )

    log_min = math.log(sys.float_info.min)
    for rank, tank in enumerate(priority_order):
        exponent = len(priority_order) - 1 - rank
        log_weight = exponent * log_base - offset
        if log_weight <= log_min:
            weight = sys.float_info.min
        else:
            weight = math.exp(log_weight)
        weights[tank] = weight
    return weights


def tank_solve_d(
    tanks_df: pd.DataFrame,
    demands: Sequence[float],
    *,
    tank_usage_penalty: float = 1.0,
) -> Tuple[bool, pd.DataFrame | None]:
    """Assign demands so that stranded capacity is lexicographically minimal.

    Compared to :func:`tank_solve_c`, this variant keeps each tank's stranded
    capacity active in the objective, even when the solver would otherwise leave
    a tank untouched.  Doing so nudges the optimizer to pour volume into the
    tightest tanks first, concentrating the inevitable leftover volume into as
    few tanks as possible.
    """

    solver = _build_solver()

    demands = list(demands)
    if any(d < 0 for d in demands):
        raise ValueError("Demands must be non-negative volumes.")

    if not demands:
        df = tanks_df.copy()
        df["demands"] = [[] for _ in range(len(df))]
        df["placed"] = 0.0
        df["new_level"] = df["current_level"]
        df["stranded"] = (
            df["max_level"].astype(float) - df["current_level"].astype(float)
        )
        return True, df

    spare_capacity = (
        tanks_df["max_level"].astype(float) - tanks_df["current_level"].astype(float)
    )
    if (spare_capacity < 0).any():
        raise ValueError("Current level exceeds max level for at least one tank.")

    tank_indices = list(tanks_df.index)
    demand_indices = range(len(demands))

    assign = {
        (tank, demand): solver.BoolVar(f"assign_{tank}_{demand}")
        for tank in tank_indices
        for demand in demand_indices
    }
    use_tank = {tank: solver.BoolVar(f"use_{tank}") for tank in tank_indices}
    stranded = {
        tank: solver.NumVar(0.0, float(spare_capacity.loc[tank]), f"stranded_{tank}")
        for tank in tank_indices
    }

    # Every demand must be placed exactly once.
    for demand in demand_indices:
        solver.Add(
            sum(assign[tank, demand] for tank in tank_indices) == 1,
            name=f"assign_once_{demand}",
        )

    # Flow conservation and linking constraints per tank.
    capacity_added_expr: dict[int, pywraplp.LinearExpr] = {}
    for tank in tank_indices:
        capacity_added = solver.Sum(
            demands[demand] * assign[tank, demand] for demand in demand_indices
        )
        capacity_added_expr[tank] = capacity_added

        spare = float(spare_capacity.loc[tank])
        solver.Add(capacity_added <= spare, name=f"capacity_{tank}")

        # Activate ``use_tank`` whenever any demand touches the tank.
        for demand in demand_indices:
            solver.Add(use_tank[tank] >= assign[tank, demand], name=f"use_link_{tank}_{demand}")

        # Keep the stranded definition active even when ``use_tank`` is zero.
        solver.Add(stranded[tank] + capacity_added == spare, name=f"balance_{tank}")

    weights = _lexicographic_weights(spare_capacity)
    objective = solver.Sum(weights[tank] * stranded[tank] for tank in tank_indices)
    objective += tank_usage_penalty * solver.Sum(use_tank.values())
    solver.Minimize(objective)

    status = solver.Solve()
    ok = status == pywraplp.Solver.OPTIMAL
    if not ok:
        return False, None

    result = tanks_df.copy()
    placed_demands: list[list[float]] = []
    stranded_values = []
    placed_amounts = []

    for tank in tank_indices:
        allocations: list[float] = []
        for demand in demand_indices:
            if assign[tank, demand].solution_value() > 0.5:
                allocations.append(float(demands[demand]))
        placed_volume = sum(allocations)
        placed_demands.append(allocations)
        placed_amounts.append(placed_volume)
        stranded_values.append(stranded[tank].solution_value())

    result["demands"] = placed_demands
    result["placed"] = placed_amounts
    result["new_level"] = result["current_level"] + result["placed"]
    result["stranded"] = stranded_values

    return True, result


def run_iterative_scenarios(
    scenarios: Iterable[tuple[pd.DataFrame, Sequence[float]]],
    *,
    verbose: bool = True,
) -> SolveDiagnostics:
    """Execute a sequence of scenarios, printing each outcome.

    The helper exists purely for manual experimentation via ``python -m``.
    """

    objective_value: float | None = None
    ok = True
    for iteration, (tanks, demands) in enumerate(scenarios, start=1):
        success, placement = tank_solve_d(tanks, demands)
        if verbose:
            pd.set_option("display.max_columns", None)
            print(f"Scenario {iteration}")
            if success:
                print(placement)
            else:
                print("Solver failed to find an optimal solution")
        ok = ok and success
        if success:
            objective_value = placement.get("stranded", pd.Series(dtype=float)).sum()
    return SolveDiagnostics(ok=ok, objective_value=objective_value, iterations=iteration)


if __name__ == "__main__":
    base_case = pd.DataFrame(
        {
            "capacity": [100, 100, 100, 100],
            "max_level": [95, 95, 95, 95],
            "current_level": [20, 0, 80, 0],
        },
        index=["tank_0", "tank_1", "tank_2", "tank_3"],
    )

    diagnostic = run_iterative_scenarios(
        [
            (base_case, [56.0, 2.0, 18.0, 40.0]),
            (base_case, [56.0, 18.0, 2.0, 40.0]),
        ]
    )

    print("\nSummary:")
    print(diagnostic)
