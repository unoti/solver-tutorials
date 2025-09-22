

* [CP-SAT](https://developers.google.com/optimization/cp/cp_solver). Integers only. CP = Constraint Programming. 
    * [Nurse Scheduling](https://developers.google.com/optimization/scheduling/employee_scheduling)
        - includes example showing requested schedules. They treat those as optimization criteria
          where we try to meet as many requests as we can.
* [Primer on Integer Optimization: Mosek Modeling Cookbook](https://docs.mosek.com/modeling-cookbook/linear.html)


## Learnings
* Specifying variables as `IntVar` isn't enough. You must select the right solver:
    * GLOP will merrily give you floats for decision variables declared as IntVar.

## Things to like about OR-Tools
I like the way they use coefficients works out nicer in the code.
OR-Tools inherently recognizes that our things will be decision variables multipled
by values, and that many of these terms will be added.

With Gurobi, I feel like I'm contorting to try to fit my objectives and constraints
into `gp.quicksum` blocks with nested generators all in one big multiline generator.
But with OR-Tools, I like the "air and space" that it gives me to express those
concepts more naturally with multiple lines. This is because OR-Tools acknowledges
that I'm going to be setting multipliers against decision variables, and adding the terms.

Compare these pieces of code which express the same thing:

**Gurobi:**
```py
    model.setObjective(gp.quicksum(shipments[(w,s)] * cost[(w,s)]
                                    for w in warehouses for s in stores)
                       , GRB.MINIMIZE)
```

**OR-Tools:**
```py
    # Objective function (minimize cost)
    objective = solver.Objective()
    for w in all_warehouses:
        for s in all_stores:
            objective.SetCoefficient(ship_vars[w, s], shipment_costs[w, s])
    objective.SetMinimization()
```

## Ideas
Make a tutorial that shows how to blend AI agents with solver.
We're scheduling for a restaurant.
You can talk to the agent and tell it what's up.
And it gives you options.

For example:
* Jenny works days, but is willing to work nights if you really need it.
* Bob has a vacation and can't work during certain dates.
And so on, and it gives you options, and says we can meet everybody's
preferences if you're willing to pay this much overtime, but here's
another schedule that doesn't meet everybody's *preferences* but
pays more overtime.

Then you can iteratively work the schedule.
