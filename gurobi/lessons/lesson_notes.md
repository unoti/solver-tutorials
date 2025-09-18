# Lesson Notes

## Pitch

A workshop where we teach the essence of Gurobi as I've learned it so far. I show you what I've learned, what surprised me, how to think like a Gurobi OR scientist (a baby one), and by the end of this workshop you will have solved a handful of optimization problems.
 
Fun fact: a lot of leetcode problems that are "hard" to solve are actually super easy to solve with Gurobi

# Less obvious things

* It's easy to miss a constraint or detail.
    * Solution can still look real good with a missed detail;
        you may not realize you missed it.
    * Make a checklist and be methodical.
* When you add a decision variable it gives you a reference to use for
    constraints and objectives

* Structure is always:
    * Framing
    * Decision variables
    * Objective
    * Constraints
    * Solve
    * Interpret output

* Decision variable types
    * `GRB.CONTINUOUS` Float values
    * `GRB.INTEGER` Integers, by default constrainted to be >= 0
    * `GRB.BINARY` Can only be 0 or 1

* A key challenge is keeping your data structures straight, layering the complexity

## Example problems
Quite a few example problems here showing that [leetcode problems are often constraint problems](https://buttondown.com/hillelwayne/archive/many-hard-leetcode-problems-are-easy-constraint/)

Given a list of stock prices through the day, find maximum profit you can get by buying one stock and selling one stock later.

array[int] of int: prices = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5, 8];
var int: buy;
var int: sell;
var int: profit = prices[sell] - prices[buy];

constraint sell > buy;
constraint profit > 0;
solve maximize profit;


## Future topics
* Hierarchical solving
    * Converting an objective function into a constraint, and re-solving with a new objective
        - e.g., find the lowest cost option with a lead time of no more than X
    * Showing the top 3 solutions
        - add a constraint that says "and you can't do it this way" and re-solve

---

## Big M Technique
You cannot put decision variables on both sides of an inequality in linear programming. But there's a standard technique for this exact situation.

The "Big M" Method:
For "if setup = 1, then production ≥ 10":

How it works:
When setup = 0 (not producing):

production >= 10 * 0 → production >= 0 ✓
production <= 10000 * 0 → production <= 0 → forces production = 0 ✓
When setup = 1 (producing):

production >= 10 * 1 → production >= 10 ✓ (minimum batch size)
production <= 10000 * 1 → production <= 10000 ✓ (doesn't restrict)



---

## AddVars plural

```py
    days = ['mon', 'tue']
    shifts = ['day', 'eve']
    emps = ['1', '2']

    # Imagine looping over all the combinations of this
    # and putting the variables into a single dictionary
    # where each item is keyed by a tuple:
    x = {}
    for e in emps:
        for d in days:
            for s in shifts:
                x[(e, d, s)] = model.addVar(vtype=GRB.BINARY)
                # Shortcut: things with commas automatically make tuples:
                x[e, d, s] = model.addVar(vtype=GRB.BINARY)

    x = model.addVars(emps, days, shifts, vtype=GRB.BINARY)
    # This is a decision variable for employee 2 working the tue eve shift:
    #x['tue', 'eve', '2']

    print(f'type of x is {type(x)}')
    # type of x is <class 'gurobipy._core.tupledict'>

    print(f'x is:')
    print(x)
    # {('1', 'mon', 'day'): <gurobi.Var *Awaiting Model Update*>,
    #  ('1', 'mon', 'eve'): <gurobi.Var *Awaiting Model Update*>, ...
    print(f'x keys: {x.keys()}')
    # x keys: dict_keys([
    # ('1', 'mon', 'day'), ('1', 'mon', 'eve'), ('1', 'tue', 'day'),
    # ('1', 'tue', 'eve'), ('2', 'mon', 'day'), ('2', 'mon', 'eve'),
    # ('2', 'tue', 'day'), ('2', 'tue', 'eve')])
```