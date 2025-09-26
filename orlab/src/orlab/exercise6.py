from typing import Optional, List, Tuple

import pandas as pd
from ortools.linear_solver import pywraplp


def tank_solve(tanks_df: pd.DataFrame, demands: List[int]) -> Tuple[bool, pd.DataFrame | None]:
    model = pywraplp.Solver.CreateSolver('SCIP')
    all_tanks = tanks_df.index
    all_demands = range(len(demands)) # Sequence numbers for demands.
    # Do we need to use ints? Would it be ok if with used floats?
    tank_remaining = list((tanks_df.max_level - tanks_df.current_level).astype(int))

    # Decision variables
    x_vars = {} # key: (tank, demand). True if we are serving this demand in this tank.
    for tank in all_tanks:
        for demand in all_demands:
            x_vars[tank, demand] = model.BoolVar(f'tank_{tank}_demand_{demand}')

    # Follower decision variables:
    # stranded_vars[tank] set to the remaining capacity for a tank if we used it.
    stranded_vars = {}
    for tank in all_tanks:
        stranded_vars[tank] = model.IntVar(0, tank_remaining[tank], f'stranded_{tank}')

    # Constraint: Each demand must be placed exactly once.
    for demand in all_demands:
        model.Add(sum(x_vars[tank, demand] for tank in all_tanks) == 1)

    # Constraint: tanks cannot exceed capacity
    for tank in all_tanks:
        capacity_added = sum([x_vars[tank, demand] * demands[demand]
                          for demand in all_demands])
        final_remaining = tank_remaining[tank] - capacity_added
        model.Add(final_remaining >= 0)

        # Tank is used if any demand is placed there
        tank_is_used = sum(x_vars[tank, demand] for demand in all_demands)

        # stranded_vars[tank] is final remaining if a demand is placed there, otherwise it is zero.
        # stranded_vars[tank] = final_remaining * tank_is_used
        big_M = tank_remaining[tank]
        model.Add(stranded_vars[tank] <= final_remaining)
        model.Add(stranded_vars[tank] <= big_M * tank_is_used)
        model.Add(stranded_vars[tank] >= final_remaining - big_M * (1 - tank_is_used))
    
    # Objective: minimize stranded capacity: unused capacity when we touch a tank.
    total_stranded = sum(stranded_vars[tank] for tank in all_tanks)
    # We penalize using tanks because we want to pack demands into as few tanks as we can.
    tank_usage_penalty = sum(1000 * sum(x_vars[tank, demand] for demand in all_demands) for tank in all_tanks)
    model.Minimize(total_stranded + tank_usage_penalty)

    # Solve
    status = model.Solve()

    # Interpret results
    ok = status == pywraplp.Solver.OPTIMAL
    if not ok:
        return ok, None
    
    df = tanks_df.copy()

    all_tank_demands = []
    all_tank_stranded = []
    for tank in all_tanks:
        tank_demands = []
        for demand in range(len(demands)):
            placed = x_vars[tank, demand].solution_value()
            if placed > 0:
                tank_demands.append(demands[demand])
        all_tank_demands.append(tank_demands)
        all_tank_stranded.append(stranded_vars[tank].solution_value())
        print(f'tank {tank} placed {tank_demands} stranded_vars[tank]={stranded_vars[tank].solution_value()}')
    df['demands'] = all_tank_demands
    df['placed'] = df['demands'].apply(sum)
    df['new_level'] = df.current_level + df.placed
    df['stranded_var'] = all_tank_stranded
    df['stranded'] = df.apply(lambda row: row.max_level - row.new_level if row.placed > 0 else 0, axis=1)
    return ok, df