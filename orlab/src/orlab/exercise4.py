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

    # Solve
    result_status = solver.Solve()

    # Show Results
    is_solved = result_status == pywraplp.Solver.OPTIMAL

    if not is_solved:
        print('Unable to find solution')
        exit(1)
    
    print('Solved! Solution:')
    print(f'Objective value: Cost={objective.Value()}')
    for day in all_days:
        print(day)
        for shift in all_shifts:
            working_emps = [emp for emp in all_emps
                            if sched_vars[day, shift, emp].solution_value()]
            workers_str = ', '.join(working_emps)
            print(f'  {shift}: ({len(working_emps)} reps) {workers_str}')

    # Objective value: Cost=3488.0
    # mon
    #   day: (12 reps) E1, E3, E13, E16, E18, E20, E21, E22, E23, E30, E31, E33
    #   eve: (8 reps) E14, E15, E19, E24, E25, E29, E32, E35
    #   ngt: (4 reps) E17, E27, E28, E34
    # tue
    #   day: (12 reps) E1, E2, E5, E6, E7, E8, E9, E10, E12, E13, E19, E23
    #   eve: (8 reps) E3, E15, E16, E20, E24, E25, E28, E29
    #   ngt: (4 reps) E21, E22, E26, E27
    # wed
    #   day: (12 reps) E11, E14, E16, E17, E18, E19, E21, E22, E23, E24, E25, E26
    #   eve: (8 reps) E2, E8, E9, E20, E31, E33, E34, E35
    #   ngt: (4 reps) E4, E12, E15, E27
    # thu
    #   day: (12 reps) E1, E2, E3, E8, E9, E11, E12, E14, E15, E21, E24, E32
    #   eve: (8 reps) E5, E6, E7, E10, E18, E19, E20, E22
    #   ngt: (4 reps) E4, E13, E17, E35
    # fri
    #   day: (12 reps) E1, E2, E3, E8, E9, E10, E11, E12, E14, E23, E26, E29
    #   eve: (8 reps) E4, E5, E6, E7, E13, E17, E27, E28
    #   ngt: (4 reps) E15, E16, E34, E35
    # sat
    #   day: (10 reps) E1, E3, E8, E9, E11, E12, E17, E28, E32, E34
    #   eve: (7 reps) E2, E4, E5, E6, E13, E18, E25
    #   ngt: (4 reps) E7, E10, E20, E26
    # sun
    #   day: (10 reps) E4, E5, E6, E11, E21, E22, E23, E26, E34, E35
    #   eve: (7 reps) E25, E28, E29, E30, E31, E32, E33
    #   ngt: (4 reps) E7, E10, E14, E18


if __name__ == '__main__':
    main()