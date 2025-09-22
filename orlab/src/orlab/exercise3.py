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
    requirement_types = [wood, labor]
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
    for resource in requirement_types:
        constraint = solver.Constraint(0, supply_by_type[resource], f'supply_{resource}')
        for item in all_items:
            constraint.SetCoefficient(produce_vars[item], item_requirements[item, resource])

    # Objective

    # Solve

    # Show Results


if __name__ == '__main__':
    main()