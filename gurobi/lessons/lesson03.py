"""
Production Planning Problem
A furniture company makes chairs and tables using two resources: wood and labor.

Resource availability:

Wood: 100 board-feet available per week
Labor: 80 hours available per week
Resource requirements per unit:

Each chair needs: 2 board-feet of wood, 3 hours of labor
Each table needs: 5 board-feet of wood, 2 hours of labor
Profit per unit:

Each chair sells for $40 profit
Each table sells for $60 profit
Goal: Determine how many chairs and tables to produce to maximize weekly profit.
"""
import gurobipy as gp
from gurobipy import GRB
from gurobi_env import get_gurobi_env


def main():
    env = get_gurobi_env()
    model = gp.Model("furniture_production", env=env)

    # Framing
    profit_chair = 40
    profit_table = 60
    wood_chair = 2
    wood_table = 5
    labor_chair = 3
    labor_table = 2
    wood_supply = 100
    labor_supply = 80

    # Decision variables.
    chairs = model.addVar(name="chairs", vtype=GRB.INTEGER)
    tables = model.addVar(name="tables", vtype=GRB.INTEGER)

    # Objective: Maximize profit
    model.setObjective(chairs * profit_chair + tables * profit_table, GRB.MAXIMIZE)

    # Constraints
    model.addConstr(chairs * wood_chair + tables * wood_table <= wood_supply, "wood_constraint")
    model.addConstr(chairs * labor_chair + tables * labor_table <= labor_supply, "labor_constraint")

    # Solve
    print("Optimizing...")
    model.optimize()

    if model.status == GRB.OPTIMAL:
        print("✅ Optimal solution found!")
        print(f"📊 Objective value (maximum profit): ${model.objVal:.2f}")

        print(f"Produce {chairs.x:.0f} chairs")
        print(f"Produce {tables.x:.0f} tables")
    else:
        print("❌ No optimal solution found.")
        print(f"Status: {model.status}")

if __name__ == "__main__":
    main()