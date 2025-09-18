"""
Employee Shift Scheduling Problem
A small call center needs to staff customer service 24/7.
They want to minimize total labor costs while ensuring adequate coverage.

1. Shift structure: [1.0]

- [x] Day shift (8am-4pm): Needs at least 12 employees, pays $20/hour
- [x] Evening shift (4pm-12am): Needs at least 8 employees, pays $22/hour
- [x] Night shift (12am-8am): Needs at least 4 employees, pays $25/hour

2. Employee constraints:

- [2.1] Each employee works exactly one 8-hour shift per day
- [x] You have 25 total employees available
- [2.2] No employee can work more than 5 days per week
- [/] At least 3 employees must be scheduled for each shift (safety requirement)
    - This will happen naturally unless we change some other data
**This is a constraints we should do. Bonus item?**
- [ ] There must be at least 2 shifts off between each employee worked shift
    - This avoids situations where someone works until midnight friday and then
    - gets a shift at mightnight saturday or 8am saturday.
    - Other formulations of this constraint could work like need 3 days off if changing shifts

Business rules:

Day shift handles highest call volume (requires most staff)
Evening shift has moderate volume
Night shift has lowest volume but pays premium for inconvenience
- [ ] Weekend shifts (Saturday/Sunday) require 20% fewer staff minimum

Goal: Schedule employees to shifts for one week to minimize total payroll costs
while meeting all coverage requirements.
"""
from dataclasses import dataclass
from typing import Iterable, List

import gurobipy as gp
from gurobipy import GRB
from gurobi_env import get_gurobi_env
import math


@dataclass
class Shift:
    name: str
    worker_count: int
    worker_pay: float


@dataclass
class Day:
    name: str
    staff_level: float # 1=normal load, 0.8 = 20% lighter


@dataclass
class ShiftScheduleItem:
    """Think of this like a checkmark that says if an employee is working a shift on a day"""
    emp_id: str
    day: Day
    shift: Shift
    var: any    # Gurobi decision variable, true if this employee working this shift

def get_schedule_items(schedule: List[ShiftScheduleItem], day: Day, shift: Shift) -> Iterable[ShiftScheduleItem]:
    """Gets the ScheduleItems for a given day and shift."""
    for item in schedule:
        if item.day != day:
            continue
        if item.shift != shift:
            continue
        yield item

def get_staff_level(shift: Shift, day: Day) -> int:
    """Gets the number of employees needed for a given day and shift."""
    return math.ceil(shift.worker_count * day.staff_level)

def get_selected_schedule(schedule: List[ShiftScheduleItem], day: Day, shift: Shift) -> Iterable[ShiftScheduleItem]:
    """Gets the final schedule selected for a day and shift."""
    for item in get_schedule_items(schedule, day, shift):
        if not item.var.x:
            continue
        yield item

def get_items_for_emp_day(schedule: List[ShiftScheduleItem], emp_id: str, day: Day) -> Iterable[ShiftScheduleItem]:
    """Get schedule items for a given employee and day."""
    for item in schedule:
        if item.emp_id != emp_id or item.day != day:
            continue
        yield item

def get_vars_for_emp_week(schedule: List[ShiftScheduleItem], emp_id: str):
    for item in schedule:
        if item.emp_id != emp_id:
            continue
        yield item.var

def main():
    env = get_gurobi_env()
    model = gp.Model("call_center", env=env)

    # Framing
    employee_count = 33 # s/b 25. But I found it's infeasable with that workforce. Need >= 33
    employee_ids = [f'E{i+1}' for i in range(employee_count)]
    shifts_per_week = 5
    hours_per_shift = 8

    shifts = [
        Shift(name="day", worker_count=12, worker_pay=20),
        Shift(name="eve", worker_count=8,  worker_pay=22),
        Shift(name="ngt", worker_count=4,  worker_pay=25),
    ]

    day_names = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
    staff_levels = [1, 1, 1, 1, 1, 0.8, 0.8] # 20% less staff on weekends
    days = [Day(name=name, staff_level=level) for name, level in zip(day_names, staff_levels)]

    # Decision Variables
    schedule: List[ShiftScheduleItem] = []
    for day in days:
        for shift in shifts:
            for emp_id in employee_ids:
                s = ShiftScheduleItem(emp_id, day, shift, None)
                var_name = f'{emp_id}_{day.name}_{shift.name}'
                s.var = model.addVar(name=var_name, vtype=GRB.BINARY)
                schedule.append(s)

    # Objective
    model.setObjective(gp.quicksum(
        s.var * s.shift.worker_pay * hours_per_shift for s in schedule
        ), GRB.MINIMIZE)

    # Constraints
    # [1] Shift minimum workers
    for day in days:
        for shift in shifts:
            model.addConstr(gp.quicksum(
                item.var for item in get_schedule_items(schedule, day, shift)
                ) >= get_staff_level(shift, day), f'staff_level_{day.name}_{shift.name}')

    # [2.1] Per employee: at most one shift per day
    for day in days:
        for emp in employee_ids:
            model.addConstr(gp.quicksum(
                s.var for s in get_items_for_emp_day(schedule, emp, day)
                ) <= 1, f'single_shift_{day.name}_{emp}')

    # [2.2] Per employee: max 5 shifts per week
    for emp in employee_ids:
        # Notice get_vars_for_emp_week returns `item.var`
        # so I can immediately put it into quicksum without the generator, unlike the above items.
        # I could make a function get_vars() that I could use to wrap get_items_for_emp_day()
        # but that would make the code a bit harder to follow.
        # Or I could make them all return vars...
        model.addConstr(gp.quicksum(get_vars_for_emp_week(schedule, emp)) <= shifts_per_week, f'shifts_{emp}')

    # Solve
    print("Optimizing...")
    model.optimize()

    if model.status == GRB.OPTIMAL:
        print("✅ Optimal solution found!")
        print(f"📊 Objective value (Minimize Payroll): ${model.objVal:.2f}")

        for day in days:
            print(f'{day.name}:')
            for shift in shifts:
                emp_ids = [item.emp_id for item in get_selected_schedule(schedule, day, shift)]
                emp_ids_str = ', '.join(emp_ids)
                print(f'  {shift.name}: {emp_ids_str}')

    else:
        print("❌ No optimal solution found.")
        print(f"Status: {model.status}")

if __name__ == "__main__":
    main()


# See how repetitive our helper functions are?
# Notice how we keep re-traversing and re-filtering the same list?
# Let's see how professionals solve this...