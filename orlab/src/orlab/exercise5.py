"""
Multi-Product Manufacturing with Setup Costs
A specialty electronics manufacturer produces 4 different circuit board types on
3 production lines over a 5-day planning horizon.
They want to minimize total costs (production + setup) and maximize profit.

Production lines:

Line A: High precision, $50/hour, 40 hours available per day
Line B: Standard quality, $35/hour, 48 hours available per day
Line C: High volume, $25/hour, 60 hours available per day

Products & requirements:

Premium boards: 2 hours/unit, $200 profit each, can only use Line A
Standard boards: 1.5 hours/unit, $120 profit each, can use Line A or B
Basic boards: 1 hour/unit, $80 profit each, can use any line
Prototype boards: 4 hours/unit, $500 profit each, can only use Line A

Setup costs (one-time if you produce that product on that line):

Premium on Line A: $2,000 setup
Standard on Line A: $1,500 setup, on Line B: $1,000 setup
Basic on any line: $500 setup
Prototype on Line A: $3,000 setup

Customer demands (minimum quantities needed by end of week):

Premium: 50 units
Standard: 80 units
Basic: 200 units
Prototype: 15 units

Business rule: Once you start production of a product on a line,
you must produce at least 10 units (to justify the setup cost).


Clarification about production line capacity:
Line A capacity: 40 hours/day x 5 days = 200 hours per week
Premium board production: 200 hours ÷ 2 hours/unit = 100 Premium boards max per week
    from Line A.
You can think of the 40 hours per day as something like 5 machines x 8 hour shift = 40 hours.

The hourly costs are how much it costs to produce items on this line.
So if we make 30 items on a line, we multiply the line's hourly cost by
the number of hours used to make the items we made, and that is the production cost.


Goal: Maximize profit (revenue - production costs - setup costs) while meeting all demands.

- [x] production lines
- [x] demand constraint
- [x] objective function
- [x] line compatibility with products
- [x] production time constraint
- [.] setup costs
- [ ] On a line + product: Must produce at least 10 units if you make any
"""
from ortools.linear_solver import pywraplp


def main():
    print('Production Planning Example')
    solver = pywraplp.Solver.CreateSolver('SCIP')

    # Framing
    p_premium = 'premium'
    p_standard = 'standard'
    p_basic = 'basic'
    p_prototype = 'prototype'
    all_parts = [p_premium, p_standard, p_basic, p_prototype]
    part_times_per_unit = [2, 1.5, 1, 4]
    part_profit_per_unit = [200, 120, 80, 500]
    part_demands = [50, 80, 200, 15]

    all_lines = ['a', 'b', 'c']
    line_cost_per_hour = [50, 35, 25]
    line_hours_per_day = [40, 48, 60] # Represents capacity, like 5 machines * 8 hr = 40 hr
    line_min_qty = 10 # If a line makes a product, it must make at least this qty.
    part_line_compatibility = set([
        (p_premium, 'a'),
        (p_standard, 'a'),
        (p_standard, 'b'),
        (p_basic, 'a'),
        (p_basic, 'b'),
        (p_basic, 'c'),
        (p_prototype, 'a'),
    ])

    setup_costs = {
        (p_premium, 'a'): 2000,
        (p_standard, 'a'): 1500,
        (p_standard, 'b'): 1000,
        (p_basic, 'a'): 500,
        (p_basic, 'b'): 500,
        (p_basic, 'c'): 500,
        (p_prototype, 'a'): 3000,
    }

    # A "slot" is a an item that a line makes. We will have many of these per line.
    fastest_capacity = max(line_hours_per_day)
    fastest_item = min(part_times_per_unit)
    schedule_days = 5
    max_slots = schedule_days * fastest_capacity // fastest_item # 300
    all_slots = list(range(max_slots))

    def is_compatible(part: str, line: str) -> bool:
        return (part, line) in part_line_compatibility

    # Decision variables
    x_vars = {} # Key: tuple(slot, line, part), true if we're making that item in this slot.
    for slot in all_slots:
        for line in all_lines:
            for part in all_parts:
                if not is_compatible(part, line):
                    continue
                x_vars[slot, line, part] = solver.BoolVar(f'make_{slot}_{line}_{part}')

    # Shadow decision variables: Setup Costs
    # These are bool variables indicating if a given line is used to make a product.
    # We will make constraints below to force these to be checked.
    # See orlab\docs\05-exercise5.ipynb "Modelling One-Time Setup Costs"
    pay_setup = {} # Key tuple(line, part), true if using this line for this product.
    for line in all_lines:
        for part in all_parts:
            if not is_compatible(part, line):
                continue
            pay_setup[part, line] = solver.BoolVar(f'setup_{part}_{line}')

    # Constraints
    infinity = solver.infinity()
    # Constraint: A line can only make one kind of thing at a time.
    for line in all_lines:
        for slot in all_slots:
            constraint = solver.Constraint(0, 1, f'single_{line}_{slot}')
            for part in all_parts:
                if not is_compatible(part, line):
                    continue
                constraint.SetCoefficient(x_vars[slot, line, part], 1)

    # Constraint: Demand must be met.
    for part, demand_qty in zip(all_parts, part_demands):
        constraint = solver.Constraint(demand_qty, infinity, f'demand_{part}')
        for slot in all_slots:
            for line in all_lines:
                if not is_compatible(part, line):
                    continue
                constraint.SetCoefficient(x_vars[slot, line, part], 1)

    # Constraint: line capacity
    for line, hrs_per_day in zip(all_lines, line_hours_per_day):
        capacity_hrs = schedule_days * hrs_per_day
        # production_hours <= capacity_hrs
        constraint = solver.Constraint(-infinity, capacity_hrs, f'capacity_{line}')
        for slot in all_slots:
            for part, build_hours in zip(all_parts, part_times_per_unit):
                if not is_compatible(part, line):
                    continue
                constraint.SetCoefficient(x_vars[slot, line, part], build_hours)

    # Constraint: Setup Costs decision var must be set if making an item on a line.
    # See orlab\docs\05-exercise5.ipynb "The setup cost constraint expression"
    for line in all_lines:
        for part in all_parts:
            if not is_compatible(part, line):
                continue
            for slot in all_slots:
                # make[slot, line, item] <= pay_setup[line, item].
                # This transforms to:
                # make[slot, line, item] - pay_setup[line, item] <= 0.
                constraint = solver.Constraint(-infinity, 0, f'setup_{line}_{part}_{slot}')
                constraint.SetCoefficient(x_vars[slot, line, part], 1)
                constraint.SetCoefficient(pay_setup[part, line], -1)

    # Objective: maximize profit
    objective = solver.Objective()
    for slot in all_slots:
        for line in all_lines:
            for part, part_profit in zip(all_parts, part_profit_per_unit):
                if not is_compatible(part, line):
                    continue
                objective.SetCoefficient(x_vars[slot, line, part], part_profit)
    for part in all_parts:
        for line in all_lines:
            if not is_compatible(part, line):
                continue
            objective.SetCoefficient(pay_setup[part, line], -setup_costs[part, line])

    # Solve
    result_status = solver.Solve()

    # Show Results
    is_solved = result_status == pywraplp.Solver.OPTIMAL

    if not is_solved:
        print('Unable to find solution')
        exit(1)

    print('Solved! Solution:')
    print(f'Objective value: Profit={objective.Value()}')

    print('Production Plan')
    for line in all_lines:
        qty_by_item = {}
        for part in all_parts:
            if not is_compatible(part, line):
                continue
            for slot in all_slots:
                if not x_vars[slot, line, part].solution_value():
                    continue
                qty = qty_by_item.get(part, 0)
                qty += 1
                qty_by_item[part] = qty
        setup_cost_items = [part for part in all_parts if is_compatible(part, line) and pay_setup[part, line].solution_value()]
        setup_cost_str = ', '.join(setup_cost_items)
        print(f'Line {line}: {qty_by_item}. Setup: {setup_cost_str}')

    # - [ ] Why are we seeing, and paying, setup costs for line A? something is wrong...
    # Solved! Solution:
    # Objective value: Profit=34100.0
    # Production Plan
    # Line a: {'premium': 50, 'basic': 40, 'prototype': 15}. Setup: premium, standard, basic, prototype
    # Line b: {'standard': 80, 'basic': 51}. Setup: standard, basic
    # Line c: {'basic': 109}. Setup: basic

if __name__ == '__main__':
    main()