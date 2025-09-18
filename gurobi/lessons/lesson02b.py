"""
Problem:
Delivery company has 2 warehouses and needs to supply 3 stores.
Minimize transportation gosts.

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

    # Problem framing
    warehouses = ['w1', 'w2']
    supply = {'w1': 100, 'w2': 150}
    cost = {('w1', 's1'): 2, ('w1', 's2'): 3, ('w1', 's3'): 4,
            ('w2', 's1'): 5, ('w2', 's2'): 1, ('w2', 's3'): 2}

    stores = ['s1', 's2', 's3']
    demand = {'s1': 80, 's2': 70, 's3': 90}

    # Create decision variables.
    # We have 6 decision variables for the combinations of 2 warehouses and 3 stores.
    shipments = {}
    for w in warehouses:
        for s in stores:
            shipments[(w, s)] = model.addVar(name=f"{w}_{s}", vtype=GRB.INTEGER)

    # Set the objective function (minimize cost)
    model.setObjective(gp.quicksum(shipments[(w,s)] * cost[(w,s)]
                                    for w in warehouses for s in stores)
                       , GRB.MINIMIZE)

    # Set constraints.
    # Demand constraints
    for store in stores:
        model.addConstr(
            gp.quicksum(shipments[w, store] for w in warehouses) == demand[store], f"{store}_demand")

    # Supply constraints
    for warehouse in warehouses:
        model.addConstr(
            gp.quicksum(shipments[warehouse, s] for s in stores) <= supply[warehouse], f"{warehouse}_supply"
        )

    # Solve
    print("Optimizing...")
    model.optimize()

    if model.status == GRB.OPTIMAL:
        print("✅ Optimal solution found!")
        print(f"📊 Objective value (minimum cost): ${model.objVal:.2f}")
        for w in warehouses:
            for s in stores:
                qty = shipments[(w, s)].x
                if qty > 0:
                    print(f"Ship {qty:.0f} units from {w} to {s}")
    else:
        print("❌ No optimal solution found.")
        print(f"Status: {model.status}")

if __name__ == "__main__":
    main()