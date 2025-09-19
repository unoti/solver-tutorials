"""
Problem: A bakery wants to maximize profit from making cookies and cakes.
- Each cookie gives $3 profit and takes 1 hour to make
- Each cake gives $5 profit and takes 2 hours to make  
- The bakery has 8 hours available per day
- They can make at most 5 cookies per day (due to oven space)

Question: How many cookies and cakes should they make to maximize profit?

Mathematical formulation:
- Decision variables: x = cookies, y = cakes
- Objective: Maximize 3x + 5y (profit)
- Constraints: 
  * 1x + 2y ≤ 8 (time constraint)
  * x ≤ 5 (cookie limit)
  * x ≥ 0, y ≥ 0 (non-negativity)
  """

from ortools.linear_solver import pywraplp

def main():
    print('Bakery Example')

    # Note that even though we're using IntVar below, we can't use GLOP
    # because GLOP doesn't respect integer constraints, and we'd get 1.5 cakes in the solution.
    # We need to use SCIP or CBC.
    #solver = pywraplp.Solver.CreateSolver('GLOP')
    solver = pywraplp.Solver.CreateSolver('SCIP')

    # Framing
    max_cookies = 5 # Can only make 5 cookies per day due to oven space
    hr_per_cookie = 1 # Cookies take 1 hour to make
    hr_per_cake = 2
    hr_per_day = 8
    profit_per_cookie = 3
    profit_per_cake = 5

    # Decision Variables
    infinity = solver.infinity()
    # Note that if you use `NumVar` you will get a solution for 1.5 cakes.
    # We need `IntVar` here.
    #cookies_var = solver.NumVar(0, max_cookies, 'cookies')
    #cakes_var = solver.NumVar(0, infinity, 'cakes')
    cookies_var = solver.IntVar(0, max_cookies, 'cookies')
    cakes_var = solver.IntVar(0, infinity, 'cakes')

    # Constraints
    time_constraint = solver.Constraint(0, hr_per_day, 'ctime') # Time 0 to hr_per_day
    time_constraint.SetCoefficient(cookies_var, hr_per_cookie) # Adds: 1 * cookies_var
    time_constraint.SetCoefficient(cakes_var, hr_per_cake) # Adds: 2 * cakes_var

    # Objective Function
    objective = solver.Objective()
    objective.SetCoefficient(cookies_var, profit_per_cookie) # Adds 3 * cookies_var
    objective.SetCoefficient(cakes_var, profit_per_cake) # Adds 5 * cakes_var
    objective.SetMaximization()

    # Solve
    result_status = solver.Solve()

    # Show Results
    is_solved = result_status == pywraplp.Solver.OPTIMAL

    if not is_solved:
        print('Unable to find solution')
        exit(1)
    
    print('Solved! Solution:')
    print(f'Objective value: {objective.Value()}')
    print(f'cookies={cookies_var.solution_value()} cakes={cakes_var.solution_value()}')
    # Solved! Solution:
    # Objective value: 22.0
    # cookies=4.0 cakes=2.0

if __name__ == '__main__':
    main()