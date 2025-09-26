"""Lexicographic variant of the tank utilization solver."""

from __future__ import annotations

from typing import Sequence, Tuple

import pandas as pd
from ortools.linear_solver import pywraplp


def tank_solve_c(
    tanks_df: pd.DataFrame,
    demands: Sequence[float],
    *,
    tank_usage_penalty: float = 1.0,
) -> Tuple[bool, pd.DataFrame | None]:
    """Assign demands to tanks while minimizing stranded capacity lexicographically.

    Args:
        tanks_df: DataFrame indexed by tank identifier with at least the columns
            ``current_level`` and ``max_level``.  The index is preserved in the
            output so callers can identify the placement for each tank.
        demands: Non-negative demand volumes that must each be assigned to a
            single tank.
        tank_usage_penalty: Small positive weight that discourages touching
            additional tanks.  The default ``1.0`` is tiny compared to the
            stranded capacity units, but helps the solver break ties when
            multiple lexicographically equivalent solutions exist.

    Returns:
        Tuple ``(ok, result_df)``.  ``ok`` is ``True`` if an optimal solution is
        found.  ``result_df`` is ``None`` when the model is infeasible.
    """

    solver = pywraplp.Solver.CreateSolver("SCIP")
    if solver is None:
        raise RuntimeError("Unable to create OR-Tools SCIP solver instance.")

    demands = list(demands)
    if not demands:
        # Nothing to place; the original dataframe is already optimal.
        df = tanks_df.copy()
        df["demands"] = [[] for _ in range(len(df))]
        df["placed"] = 0.0
        df["new_level"] = df["current_level"]
        df["stranded"] = 0.0
        return True, df

    spare_capacity = (
        tanks_df["max_level"].astype(float) - tanks_df["current_level"].astype(float)
    )
    if (spare_capacity < 0).any():
        raise ValueError("Current level exceeds max level for at least one tank.")

    tank_indices = list(tanks_df.index)
    demand_indices = range(len(demands))

    # Decision variables
    assign = {}
    for t in tank_indices:
        for d in demand_indices:
            assign[t, d] = solver.BoolVar(f"assign_{t}_{d}")

    use_tank = {t: solver.BoolVar(f"use_{t}") for t in tank_indices}

    stranded = {
        t: solver.NumVar(0.0, float(spare_capacity.loc[t]), f"stranded_{t}")
        for t in tank_indices
    }

    # Each demand is assigned exactly once.
    for d in demand_indices:
        solver.Add(
            sum(assign[t, d] for t in tank_indices) == 1,
            name=f"assign_once_{d}",
        )

    # Capacity and linking constraints per tank.
    for t in tank_indices:
        capacity_added = solver.Sum(demands[d] * assign[t, d] for d in demand_indices)
        spare = float(spare_capacity.loc[t])

        solver.Add(capacity_added <= spare, name=f"capacity_{t}")

        # Activate use_tank whenever any demand is placed into tank t.
        for d in demand_indices:
            solver.Add(use_tank[t] >= assign[t, d], name=f"use_link_{t}_{d}")

        big_m = spare
        solver.Add(stranded[t] <= spare - capacity_added + big_m * (1 - use_tank[t]))
        solver.Add(stranded[t] >= spare - capacity_added - big_m * (1 - use_tank[t]))
        solver.Add(stranded[t] <= big_m * use_tank[t])

    # Build lexicographic weights using a deterministic priority order.  We sort
    # tanks by their *initial* spare capacity, so tighter tanks are optimized
    # first.  This keeps the objective linear while nudging the solver to fill
    # small holes before opening roomier ones.
    priority_order = list(
        spare_capacity.sort_values(kind="mergesort").index  # stable for ties
    )

    base = float(spare_capacity.sum()) + 1.0
    weights: dict[int, float] = {}
    for rank, t in enumerate(priority_order):
        exponent = len(priority_order) - 1 - rank
        weights[t] = base**exponent

    objective = solver.Sum(weights[t] * stranded[t] for t in tank_indices)
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

    for t in tank_indices:
        allocations: list[float] = []
        for d in demand_indices:
            if assign[t, d].solution_value() > 0.5:
                allocations.append(float(demands[d]))
        placed_volume = sum(allocations)
        placed_demands.append(allocations)
        placed_amounts.append(placed_volume)
        stranded_values.append(stranded[t].solution_value())

    result["demands"] = placed_demands
    result["placed"] = placed_amounts
    result["new_level"] = result["current_level"] + result["placed"]
    result["stranded"] = stranded_values

    return True, result
