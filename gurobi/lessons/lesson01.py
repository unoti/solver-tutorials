"""
Lesson 01: Your First Gurobi Linear Programming Example
======================================================

This is a super simple example to introduce you to Gurobi basics.

Problem: A bakery wants to maximize profit from making cookies and cakes.
- Each cookie gives $3 profit and takes 1 hour to make
- Each cake gives $5 profit and takes 2 hours to make  
- The bakery has 8 hours available per day
- They can make at most 5 cookies per day (due to oven space)

Question: How many cookies and cakes should they make to maximize profit?

Mathematical formulation:
- Decision variables: x = cookies, y = cakes
- Objective: Maximize 3x + 5y (profit)
- Constraints: 
  * 1x + 2y ≤ 8 (time constraint)
  * x ≤ 5 (cookie limit)
  * x ≥ 0, y ≥ 0 (non-negativity)
"""

import gurobipy as gp
from gurobipy import GRB
from gurobi_env import get_gurobi_env

def main():
    print("🍪 Welcome to your first Gurobi example! 🍰")
    print("Solving the bakery optimization problem...\n")
    
    try:
        # Step 1: Create a new Gurobi environment using ISV license
        env = get_gurobi_env()
        model = gp.Model("bakery", env=env)

        # Step 2: Create decision variables
        x = model.addVar(vtype=GRB.CONTINUOUS, name="cookies")
        y = model.addVar(vtype=GRB.CONTINUOUS, name="cakes")

        # Step 3: Set the objective function (maximize profit)
        model.setObjective(3 * x + 5 * y, GRB.MAXIMIZE)

        # Step 4: Add constraints
        model.addConstr(1 * x + 2 * y <= 8, "time_limit")
        model.addConstr(x <= 5, "cookie_limit")
        model.addConstr(x >= 0, "cookies_non_negative")
        model.addConstr(y >= 0, "cakes_non_negative")

        # Step 5: Solve the model
        print("Optimizing...")
        model.optimize()

        # Step 6: Check if we found an optimal solution
        if model.status == GRB.OPTIMAL:
            print("✅ Optimal solution found!")
            print(f"📊 Objective value (maximum profit): ${model.objVal:.2f}")
            print(f"🍪 Cookies to make: {x.x:.2f}")
            print(f"🍰 Cakes to make: {y.x:.2f}")

            total_time = 1 * x.x + 2 * y.x
            print(f"⏰ Total time used: {total_time:.2f} hours (out of 8 available)")
        else:
            print("❌ No optimal solution found.")
            print(f"Status: {model.status}")
    except gp.GurobiError as e:
        print(f"❌ Gurobi Error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()