

* [CP-SAT](https://developers.google.com/optimization/cp/cp_solver). Integers only. CP = Constraint Programming. 
    * [Nurse Scheduling](https://developers.google.com/optimization/scheduling/employee_scheduling)
        - includes example showing requested schedules. They treat those as optimization criteria
          where we try to meet as many requests as we can.
* [Primer on Integer Optimization: Mosek Modeling Cookbook](https://docs.mosek.com/modeling-cookbook/linear.html)


## Learnings
* Specifying variables as `IntVar` isn't enough. You must select the right solver:
    * GLOP will merrily give you floats for decision variables declared as IntVar.

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
