"""
Problem:
Delivery company has 2 warehouses and needs to supply 3 stores.
Minimize transportation costs.

* Warehouse A has 100 units available
* Warehouse B has 150 units available
* Store 1 needs 80 units
* Store 2 needs 70 units
* Store 3 needs 90 units.

Transportation costs per unit:
* From warehouse A, $2 to store 1, $3 to store 2, $4 to store 3
* From warehouse B, $5 to store 1, $1 to store 2, $2 to store 3

Determine how many units to ship from each warehouse to each store to minimize total cost
while meeting all demands.
"""
import gurobipy as gp
from gurobipy import GRB
from gurobi_env import get_gurobi_env

def main():
    env = get_gurobi_env()
    model = gp.Model("supply_chain", env=env)

    # Create decision variables.
    # We have 6 decision variables for the combinations of 2 warehouses and 3 stores.
    # I realize there's an array-type approach I could use.
    # But for now, I'm going to use 6 individual variables.
    w1_s1 = model.addVar(vtype=GRB.INTEGER, name="w1_s1")
    w1_s2 = model.addVar(vtype=GRB.INTEGER, name="w1_s2")
    w1_s3 = model.addVar(vtype=GRB.INTEGER, name="w1_s3")
    w2_s1 = model.addVar(vtype=GRB.INTEGER, name="w2_s1")
    w2_s2 = model.addVar(vtype=GRB.INTEGER, name="w2_s2")
    w2_s3 = model.addVar(vtype=GRB.INTEGER, name="w2_s3")

    # Set the objective function (minimize cost)
    model.setObjective(w1_s1 * 2 + w1_s2 * 3 + w1_s3 * 4 + \
                       w2_s1 * 5 + w2_s2 * 1 + w2_s3 * 2 \
                       , GRB.MINIMIZE)

    # Set constraints.
    model.addConstr(w1_s1 + w2_s1 == 80, "store1_demand")
    model.addConstr(w1_s2 + w2_s2 == 70, "store2_demand")
    model.addConstr(w1_s3 + w2_s3 == 90, "store3_demand")
    model.addConstr(w1_s1 + w1_s2 + w1_s3 <= 100, "warehouse1_supply")
    model.addConstr(w2_s1 + w2_s2 + w2_s3 <= 150, "warehouse2_supply")

    # Solve
    print("Optimizing...")
    model.optimize()

    if model.status == GRB.OPTIMAL:
        print("✅ Optimal solution found!")
        print(f"📊 Objective value (minimum cost): ${model.objVal:.2f}")
        print(f"🚚 Ship {w1_s1.x:.2f} units from Warehouse 1 to Store 1")
        print(f"🚚 Ship {w1_s2.x:.2f} units from Warehouse 1 to Store 2")
        print(f"🚚 Ship {w1_s3.x:.2f} units from Warehouse 1 to Store 3")
        print(f"🚚 Ship {w2_s1.x:.2f} units from Warehouse 2 to Store 1")
        print(f"🚚 Ship {w2_s2.x:.2f} units from Warehouse 2 to Store 2")
        print(f"🚚 Ship {w2_s3.x:.2f} units from Warehouse 2 to Store 3")
    else:
        print("❌ No optimal solution found.")
        print(f"Status: {model.status}")

if __name__ == "__main__":
    main()