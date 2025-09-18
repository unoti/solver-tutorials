"""
Multi-Product Manufacturing with Setup Costs
A specialty electronics manufacturer produces 4 different circuit board types on
3 production lines over a 5-day planning horizon. They want to minimize total costs (production + setup).

Production lines:

Line A: High precision, $50/hour, 40 hours available per day
Line B: Standard quality, $35/hour, 48 hours available per day
Line C: High volume, $25/hour, 60 hours available per day

Products & requirements:

Premium boards: 2 hours/unit, $200 profit each, can only use Line A
Standard boards: 1.5 hours/unit, $120 profit each, can use Line A or B
Basic boards: 1 hour/unit, $80 profit each, can use any line
Prototype boards: 4 hours/unit, $500 profit each, can only use Line A

Setup costs (one-time if you produce that product on that line):

Premium on Line A: $2,000 setup
Standard on Line A: $1,500 setup, on Line B: $1,000 setup
Basic on any line: $500 setup
Prototype on Line A: $3,000 setup

Customer demands (minimum quantities needed by end of week):

Premium: 50 units
Standard: 80 units
Basic: 200 units
Prototype: 15 units

Business rule: Once you start production of a product on a line, you must produce at least 10 units (to justify the setup cost).

Goal: Maximize profit (revenue - production costs - setup costs) while meeting all demands.
"""