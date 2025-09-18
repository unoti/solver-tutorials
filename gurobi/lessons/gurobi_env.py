import os
import json
import gurobipy as gp

def get_gurobi_env():
    """Gets the default Gurobi environment. Integrates licenses as needed."""
    # For now we're going to use the default PIP license which is limited
    # to 2000 variables and 100 constraints.
    env = gp.Env()
    return env
