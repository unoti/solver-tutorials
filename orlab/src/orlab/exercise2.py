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
from ortools.linear_solver import pywraplp


def main():
    print('Delivery Example')
    solver = pywraplp.Solver.CreateSolver('SCIP')

    # IDs
    warehouse_a = 0
    warehouse_b = 1
    store_1 = 0
    store_2 = 1
    store_3 = 2
    all_stores = range(3)
    all_warehouses = range(2)

    # Framing
    warehouse_supply = {warehouse_a: 100, warehouse_b: 150}
    store_demand = {store_1: 80, store_2: 70, store_3: 90}
    # Shipment costs keyed by tuple(warehouse, store)
    shipment_costs = {
        (warehouse_a, store_1): 2,
        (warehouse_a, store_2): 3,
        (warehouse_a, store_3): 4,
        (warehouse_b, store_1): 5,
        (warehouse_b, store_2): 1,
        (warehouse_b, store_3): 2,
    }

    # Decision variables
    ship_vars = {} # tuple(warehouse, store) = qty to ship
    for w in all_warehouses:
        supply = warehouse_supply[w]
        for s in all_stores:
            store_demand = store_demand[s]
            max_ship = min(supply, store_demand)
            ship_vars[(w, s)] = solver.IntVar(0, max_ship, f'ship_w{w}_s{s}')

    # Constraints
    # Every store must receive its total demand.
    for s in all_stores:
        demand = store_demand[s]
        constraint = solver.Constraint(demand, demand, f'store_{s}_demand')
        for w in all_warehouses:
            constraint.SetCoefficient(ship_vars[w,s], 1)