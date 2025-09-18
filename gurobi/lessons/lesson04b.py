"""
This is another version that introduces addVars() instead of addVar().

1. Shift structure [1.0]
- [ ] Day shift (8am-4pm): Needs at least 12 employees, pays $20/hour
- [ ] Evening shift (4pm-12am): Needs at least 8 employees, pays $22/hour
- [ ] Night shift (12am-8am): Needs at least 4 employees, pays $25/hour

2. Employee constraints:

- [2.1] Each employee works exactly one 8-hour shift per day
- [x] You have 35 total employees available
- [2.2] No employee can work more than 5 days per week
- [/] At least 3 employees must be scheduled for each shift (safety requirement)
    - This will happen naturally unless we change some other data
"""
from dataclasses import dataclass
import math
from typing import List

import gurobipy as gp
from gurobipy import GRB
from gurobi_env import get_gurobi_env

@dataclass
class Shift:
    name: str
    worker_count: int
    pay_per_hour: float

all_shifts = [
    Shift(name="day", worker_count=12, pay_per_hour=20),
    Shift(name="eve", worker_count=8,  pay_per_hour=22),
    Shift(name="ngt", worker_count=4,  pay_per_hour=25),
]
#shifts = {s.name: s for s in all_shifts}

days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
staff_levels = [1, 1, 1, 1, 1, 0.8, 0.8] # 20% less staff on weekends

#def selected_employees(x, emps: List[str], day: str, shift: Shift) -> List[str]:
#    ...

def main():
    env = get_gurobi_env()
    model = gp.Model("call_center2", env=env)

    # Framing.
    employee_count = 35
    emps = [f'E{i+1}' for i in range(employee_count)]
    hours_per_shift = 8
    emp_shifts_per_week = 5

    # Decision variables.
    # `x` is a checkmark for a (day, shift, emp) tuple.
    shift_names = [s.name for s in all_shifts]
    x = model.addVars(days, shift_names, emps, vtype=GRB.BINARY)

    # Objective.
    # Minimize payroll cost.
    model.setObjective(gp.quicksum(
        x[d, s.name, e] * hours_per_shift * s.pay_per_hour
        for d in days
        for s in all_shifts
        for e in emps
        ), GRB.MINIMIZE)

    # Constraints.
    # [1.0] Shift minimum workers.
    for day, staff_level in zip(days, staff_levels):
        for shift in all_shifts:
            worker_min = math.ceil(shift.worker_count * staff_level)
            model.addConstr(
                gp.quicksum(x[day, shift.name, emp] for emp in emps)
                >= worker_min,
                f'staff_level_{day}_{shift.name}'
            )

    # [2.1] per employee: max one shift per day.
    for day in days:
        for emp in emps:
            model.addConstr(
                gp.quicksum(x[day, s, emp] for s in shift_names)
                <= 1,
                f'shifts_{day}_{emp}'
            )

    # [2.2] per employee: Max 5 shifts per week
    for emp in emps:
        model.addConstr(
            gp.quicksum(x[d, s, emp]
                        for d in days
                        for s in shift_names)
            <= emp_shifts_per_week,
            f'shifts_{emp}'
        )

    # Solve
    print("Optimizing...")
    model.optimize()

    if model.status == GRB.OPTIMAL:
        print("✅ Optimal solution found!")
        print(f"📊 Objective value (Minimize Payroll): ${model.objVal:.2f}")

        for day in days:
            print(f'{day}:')
            for shift in all_shifts:
                # The `.x` on this is to get the value of the decision var, the "checkmark"
                selected_emps = [e for e in emps if x[day, shift.name, e].x]
                emp_ids_str = ', '.join(selected_emps)
                print(f'  {shift.name}: {emp_ids_str}')

    else:
        print("❌ No optimal solution found.")
        print(f"Status: {model.status}")

if __name__ == "__main__":
    main()