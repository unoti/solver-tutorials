from typing import List
import pandas as pd
from ortools.linear_solver import pywraplp


def tank_solve(tanks_df: pd.DataFrame, demands: List[int]) -> pd.DataFrame:
    model = pywraplp.Solver.CreateSolver('SCIP')
    all_tanks = tanks_df.index
    all_demands = range(len(demands)) # Sequence numbers for demands.
    tank_remaining = tanks_df.max_level - tanks_df.current_level
    tank_max_levels = tanks_df.max_level

    # Decision variables
    x_vars = {} # key: (tank, demand). True if we are serving this demand in this tank.
    for tank in all_tanks:
        for demand in all_demands:
            x_vars[tank, demand] = model.BoolVar(f'tank_{tank}_demand_{demand}')

    # Follower decision variables:
    # used_vars[tank] true if we put something into a given tank.
    # stranded_vars[tank] set to the remaining capacity for a tank if we used it.
    used_vars = {}
    stranded_vars = {}
    for tank in all_tanks:
        used_vars[tank] = model.BoolVar(f'tank_used_{tank}')
        # Link used_vars to be true if anything is placed in a tank.
        # used_vars is the logical OR of all the demands in the tank.
        # In linear programming, we do 2 things for that:
        #     used_vars[tank] >= x_vars[tank, demand]: set it if a demand goes in a tank.
        #     used_vars[tank] <= sum of all tank demands: to keep it zero when possible.
        demands_in_tank = [x_vars[tank, demand] for demand in all_demands]
        for demand in all_demands:
            model.Add(used_vars[tank] >= x_vars[tank, demand])
        model.Add(used_vars[tank] <= sum(demands_in_tank))

        stranded_vars[tank] = model.NumVar()
    

    # Constraint: Each demand must be placed exactly once.
    for demand in all_demands:
        model.Add(sum(x_vars[tank, demand] for tank in all_tanks) == 1)

    # Constraint: tanks cannot exceed capacity
    stranded_capacity = 0
    for tank in all_tanks:
        capacity_added = sum([x_vars[tank, demand] * demands[demand]
                          for demand in all_demands])
        final_remaining = tank_remaining[tank] - capacity_added
        model.Add(final_remaining >= 0)

        stranded_capacity += used_vars[tank] * final_remaining
    
    # Objective: minimize stranded capacity: unused capacity when we touch a tank.
    objective = model.Objective()
    for tank in all_tanks:
        ...
    model.Minimize(stranded_capacity)
    status = model.Solve()