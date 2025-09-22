"""
Employee Shift Scheduling Problem
A small call center needs to staff customer service 24/7.
They want to minimize total labor costs while ensuring adequate coverage.

1. Shift structure: [ ]

- [ ] Day shift (8am-4pm): Needs at least 12 employees, pays $20/hour
- [ ] Evening shift (4pm-12am): Needs at least 8 employees, pays $22/hour
- [ ] Night shift (12am-8am): Needs at least 4 employees, pays $25/hour

2. Employee constraints:

- [ ] Each employee works exactly one 8-hour shift per day
- [ ] You have 25 total employees available
- [ ] No employee can work more than 5 days per week
- [ ] At least 3 employees must be scheduled for each shift (safety requirement)

Business rules:

Day shift handles highest call volume (requires most staff)
Evening shift has moderate volume
Night shift has lowest volume but pays premium for inconvenience
- [ ] Weekend shifts (Saturday/Sunday) require 20% fewer staff minimum

Goal: Schedule employees to shifts for one week to minimize total payroll costs
while meeting all coverage requirements.

**This is a constraints we should do. Bonus item?**
- [ ] There must be at least 2 shifts off between each employee worked shift
    - This avoids situations where someone works until midnight friday and then
    - gets a shift at mightnight saturday or 8am saturday.
    - Other formulations of this constraint could work like need 3 days off if changing shifts
"""
from ortools.linear_solver import pywraplp


def main():
    print('Shift Scheduling Example')
    solver = pywraplp.Solver.CreateSolver('SCIP')

    # ids
    day_shift = 'day'
    eve_shift = 'eve'
    night_shift = 'ngt'
    all_shifts = [day_shift, eve_shift, night_shift]

    # Framing
    

if __name__ == '__main__':
    main()