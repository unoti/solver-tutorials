# Tank Utilization – Variant D

Variant **6d** keeps the original MILP structure but tightens the objective so
that leftover capacity is concentrated into as few tanks as possible.  The key
observations are:

1. Under the 6b/6c formulations, the stranded-capacity variable is relaxed to
   zero whenever a tank is not used.  That allows the solver to leave partially
   filled tanks untouched without any penalty.
2. If we force the stranded definition to stay active regardless of usage,
   then the lexicographic weights truly prioritize packing the tightest tanks
   first.  The trade-off remains linear because the coefficients are
   pre-computed constants.

## Model changes

* **Active stranded balance** – Replace the big-M linkage with the exact
  balance constraint `stranded_t + placed_t = spare_t`.  Even unused tanks now
  contribute their initial spare capacity to the objective, so the solver
  prefers to drain the tightest spare volume before opening a new tank.
* **Lexicographic weights** – Retain the deterministic exponential weights from
  variant C.  With the balance constraint in place the weighted objective
  effectively maximizes the high-priority fill volume while leaving the MILP
  linear.
* **Manual harness** – Add a small `__main__` driver that lets us iterate on
  different demand orders directly from the command line.  This makes it easy
  to inspect how the solver rearranges placements to keep the last few tanks as
  empty as possible.

## Usage

```bash
python -m orlab.exercise6d
```

The standalone execution runs the scenario from the feedback discussion twice
with the two different orders of the 2 and 18 unit demands.  In both cases the
solver pushes volume into the partially filled tank before touching the empty
ones, yielding a much tighter packing than the previous variant.
