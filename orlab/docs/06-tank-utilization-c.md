# Tank Utilization – Lexicographic Packing Strategy

## Motivation

The formulation from `exercise6b.py` minimizes the *aggregate* stranded
capacity across all touched tanks.  Once the solver decides which tanks must be
used, that sum becomes fixed—the spare capacity of those tanks minus the total
demand we assigned to them.  Different placements that leave the same total
unused space (e.g., swapping two demands between the same pair of tanks) are
therefore perfectly tied in the objective, so SCIP can legitimately return any
of them.  Some of those tied placements leave a single tank “half full” while
others pack one tank tight and keep the other nearly empty.  We prefer the
latter because concentrating the leftover space improves future flexibility.

## Lexicographic objective

We can express the “pack one tank before opening the next” preference without
leaving the MILP world by turning that tie into a lexicographic objective:

1. Choose a deterministic priority order for the tanks.  The implementation
   sorts tanks by their initial spare capacity (stable for ties) so that tighter
   tanks receive priority and get packed first.
2. Pre-compute a strictly decreasing sequence of weights `w_t` so that each
   weight dominates the total possible contribution of all lower-priority
   tanks.  A robust recipe is:

   ```python
   base = spare_capacity.sum() + 1
   weights[t_rank] = base ** (n_tanks - 1 - rank)
   ```

   Because each stranded variable is bounded above by its spare capacity, the
   weighted sum effectively minimizes the stranded volume tank-by-tank.
3. Keep the original binary assignment variables, capacity constraints, and
   linking constraints.  The objective becomes

   ```
   minimize  sum_t w_t * stranded_t + penalty * sum_t use_t
   ```

   All coefficients are constants, so the model remains linear and compatible
   with SCIP.

This trick makes the solver first minimize the leftover space in the highest
priority tank.  Among those optima it minimizes the stranded capacity in the
next tank, and so on.  In the motivating example the solver now prefers to pack
the first tank with the larger demand (leaving it nearly full) before touching
the second tank.

## Implementation highlights

`exercise6c.py` follows the same data pipeline as `exercise6b.py`:

* The function `tank_solve_c` accepts a dataframe with tank states and a list of
  demand volumes, builds the MILP, and returns the resulting allocation as a new
  dataframe.
* All feasibility constraints are unchanged.  The only difference is the new
  weighted objective based on the spare-capacity priority order.
* The small `tank_usage_penalty` term is kept to discourage opening extra tanks
  when multiple assignments share the same lexicographic pattern.

The approach keeps the model small, transparent, and linear while producing the
desired “fill one tank first” behavior.
