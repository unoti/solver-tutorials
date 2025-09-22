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
from ortools.linear_solver import pywraplp


def main():
    print('Production Planning Example')
    solver = pywraplp.Solver.CreateSolver('SCIP')

    # IDs
    # Items
    chair = 'chair'
    table = 'table'
    
    # Resources
    wood = 'wood'
    labor = 'labor'

    # Framing
    resource_types = [wood, labor]
    supply_by_type = {wood: 100, labor: 80}

    all_items = [chair, table]
    item_requirements = {
        (chair, wood): 2,
        (chair, labor): 3,
        (table, wood): 5,
        (table, labor): 2,
    }
    profit_by_item = {chair: 40, table: 60}

    # Decision variables
    produce_vars = {} # key: item id. value: variable for how many to produce.
    infinity = solver.infinity()
    for item in all_items:
        produce_vars[item] = solver.IntVar(0, infinity, f'produce_{item}')

    # Constraints
    # Resources Used - materials and labor
    for resource in resource_types:
        constraint = solver.Constraint(0, supply_by_type[resource], f'supply_{resource}')
        for item in all_items:
            constraint.SetCoefficient(produce_vars[item], item_requirements[item, resource])

    # Objective
    objective = solver.Objective()
    for item in all_items:
        objective.SetCoefficient(produce_vars[item], profit_by_item[item])
    objective.SetMaximization()

    # Solve
    result_status = solver.Solve()

    # Show Results
    is_solved = result_status == pywraplp.Solver.OPTIMAL

    if not is_solved:
        print('Unable to find solution')
        exit(1)
    
    print('Solved! Solution:')
    print(f'Objective value: Profit={objective.Value()}')
    for item in all_items:
        qty = int(produce_vars[item].solution_value())
        used = [f'{qty * item_requirements[item, resource]} {resource}'
            for resource in resource_types]
        used_str = ', '.join(used)
        print(f'{item}: qty {qty}. {used_str}')
    # Objective value: Profit=1460.0
    # chair: qty 17. 34 wood, 51 labor
    # table: qty 13. 65 wood, 26 labor


if __name__ == '__main__':
    main()