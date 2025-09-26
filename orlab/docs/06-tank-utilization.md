
# Problem 6: Tank Utilization
We have several liquid tanks, and each tank has a maximum capacity.
Each of the tanks has an amount of starting liquid in it at the start.
We would like the tanks to be as close their maximum capacity as we can.
We have a list of demands of liquid quanity.
For each demand we must choose exactly one of the tanks to add some liquid to,
and all of the newly added liquid must go into exactly one of the tanks.

What we're actually trying to do here is make choices to protect ourselves from
the uncertainty of the future demand that will come after the demand we know about.
So the combination of all the choices we make must minimize the total of the
"stranded capacity."  We're definiting stranded capacity of a single tank
as the capacity remaining in that tank after all placements have been made.

We only count the capacity as stranded if we placed something in the tank.

If we were to have perfect knowledge of our future demand then this becomes a simple exercise of placing
all that.  But the reality is that we won't have perfect knowledge of the future demand.
We have rough ideas and guesses about it, based on what we know about the past and what we know about 
the future, but we don't have perfect knowledge of future demand.  So we need to make choices in a way
that we're in the best position we can be for satisfying the future demand.

Trying to full up all the holes in the tanks seems like the best strategy.
