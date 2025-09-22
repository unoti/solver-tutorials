"""
Employee Shift Scheduling Problem
A small call center needs to staff customer service 24/7.
They want to minimize total labor costs while ensuring adequate coverage.

1. Shift structure: [1.0]

- [ ] Day shift (8am-4pm): Needs at least 12 employees, pays $20/hour
- [ ] Evening shift (4pm-12am): Needs at least 8 employees, pays $22/hour
- [ ] Night shift (12am-8am): Needs at least 4 employees, pays $25/hour

2. Employee constraints:

- [2.1] Each employee works exactly one 8-hour shift per day
- [x] You have 35 total employees available
- [2.2] No employee can work more than 5 days per week
- [2.3] At least 3 employees must be scheduled for each shift (safety requirement)

Business rules:

Day shift handles highest call volume (requires most staff)
Evening shift has moderate volume
Night shift has lowest volume but pays premium for inconvenience
- [x] Weekend shifts (Saturday/Sunday) require 20% fewer staff minimum

Goal: Schedule employees to shifts for one week to minimize total payroll costs
while meeting all coverage requirements.

**This is a constraints we should do. Bonus item?**
- [ ] There must be at least 2 shifts off between each employee worked shift
    - This avoids situations where someone works until midnight friday and then
    - gets a shift at mightnight saturday or 8am saturday.
    - Other formulations of this constraint could work like need 3 days off if changing shifts

Technical notes:
x = solver.BoolVar('my_var_name') # Creates a 0 or 1 decision variable in OR Tools.
https://developers.google.com/optimization/scheduling/employee_scheduling

"""
import math
from ortools.linear_solver import pywraplp


def main():
    print('Shift Scheduling Example')
    solver = pywraplp.Solver.CreateSolver('SCIP')

    # Framing
    day_shift = 'day'
    eve_shift = 'eve'
    night_shift = 'ngt'
    all_shifts = [day_shift, eve_shift, night_shift]
    base_shift_coverage = [12, 8, 4]
    shift_minimum = 3
    shift_pay = [20, 22, 25]
    all_days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
    day_coverage_factors = [1, 1, 1, 1, 1, 0.8, 0.8]
    
    coverage_per_shift = {} # Key: (day, shift)
    for day, day_coverage in zip(all_days, day_coverage_factors):
        for shift, base_coverage in zip(all_shifts, base_shift_coverage):
            coverage_per_shift[day, shift] = math.ceil(base_coverage * day_coverage)

    emp_count = 35
    all_emps = [f'E{emp+1}' for emp in range(emp_count)]
    max_emp_shifts = 5 # An employee can work no more than 5 shifts per week

    # Decision variables
    sched_vars = {} # Keyed by tuple(day, shift, emp)
    for day in all_days:
        for shift in all_shifts:
            for emp in all_emps:
                sched_vars[day, shift, emp] = solver.BoolVar(f'sched_{day}_{shift}_{emp}')

    # Constraints
    infinity = solver.infinity()
    # [1.0] Each shift must have adequate coverage
    for day in all_days:
        for shift in all_shifts:
            required_coverage = coverage_per_shift[day, shift]
            constraint = solver.Constraint(required_coverage, infinity, f'coverage_{day}_{shift}')
            for emp in all_emps:
                constraint.SetCoefficient(sched_vars[day, shift, emp], 1)

    # [2.1] each employee works no more than 1 shift per day
    for day in all_days:
        for emp in all_emps:
            constraint = solver.Constraint(0, 1, f'emp_shifts_{emp}')
            for shift in all_shifts:
                constraint.SetCoefficient(sched_vars[day, shift, emp], 1)
    
    # [2.2] An employee can work a limited number of shifts per week
    for emp in all_emps:
        constraint = solver.Constraint(0, max_emp_shifts, f'emp_week_{emp}')
        for day in all_days:
            for shift in all_shifts:
                constraint.SetCoefficient(sched_vars[day, shift, emp], 1)


    # [2.3] Each shift must have minimum workers for safety reasons
    for day in all_days:
        for shift in all_shifts:
            constraint = solver.Constraint(shift_minimum, infinity, f'shift_minimum_{day}_{shift}')
            for emp in all_emps:
                constraint.SetCoefficient(sched_vars[day, shift, emp], 1)


    # Objective: Minimize cost
    objective = solver.Objective()
    for day in all_days:
        for shift, pay in zip(all_shifts, shift_pay):
            for emp in all_emps:
                objective.SetCoefficient(sched_vars[day, shift, emp], pay)
    objective.SetMinimization()


if __name__ == '__main__':
    main()