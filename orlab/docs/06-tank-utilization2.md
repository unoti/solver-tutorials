# Tank Utilization – Strategy Notes

## Problem interpretation
We have a fixed set of storage tanks.  Each tank `i` is characterized by a current fill level `current_level_i` and a maximum level `max_level_i`.  A series of demands arrives sequentially.  For every demand `d` we must choose a single tank that will receive the entire amount `d`.  The sum of the existing contents and all assigned demands may never exceed a tank’s maximum level.  Once we decide to place at least one demand into a tank we become exposed to “stranded capacity” — the free space that remains in that tank after all known demands are assigned.  The goal is to choose the tank for each demand so that the total stranded capacity across all used tanks is minimized.

This is fundamentally a combinatorial allocation problem.  It resembles a bin-packing problem with the twist that the cost of using a tank is proportional to the unused space that remains in it after the known assignments.  That objective pushes us to pack the selected tanks as tightly as possible and to avoid touching unnecessary tanks.

## Modeling strategy
My approach is to pose the problem as a mixed-integer linear program (MILP):

* Binary decision variables `x[i, d]` indicate whether demand `d` is assigned to tank `i`.
* For every demand we require `sum_i x[i, d] = 1` so that each demand is assigned to exactly one tank.
* The volume added to a tank equals `sum_d demand[d] * x[i, d]`.  This value must not exceed the spare capacity `max_level_i - current_level_i`.
* To capture stranded capacity we introduce a continuous non-negative variable `s[i]` representing the unused space in tank `i` provided that the tank is used.  We relate `s[i]` to the decision variables with linear inequalities so that `s[i]` equals the remaining free space when the tank is used and becomes `0` when it is untouched.
* The objective is to minimize `sum_i s[i]`.  This directly penalizes unused space only in the tanks we touched.  Optionally we can add a tiny penalty on the number of tanks that receive at least one demand to break ties in favor of packing.

This formulation closely mirrors the narrative description in the original document and gives a transparent, explainable optimization model.

## Implementation notes
The solver implementation in `exercise6b.py` performs the following steps:

1. Accepts the tank data as a `pandas.DataFrame` with columns `current_level` and `max_level` plus a sequence of demand quantities.
2. Builds the MILP using OR-Tools’ SCIP backend and the variables/constraints described above.
3. Solves the model and translates the assignment into a tidy `DataFrame` that lists, for each tank, the demands placed there, the total volume placed, the resulting fill level, and the stranded capacity implied by the model.
4. Returns a tuple `(ok, result_df)` where `ok` is `True` when an optimal solution is found.  If the instance is infeasible the function returns `(False, None)`.

The model is small and purely linear, so SCIP solves it quickly even with dozens of tanks and demands.  Should we need to scale further, the same structure is compatible with commercial solvers via OR-Tools without changing the formulation.
