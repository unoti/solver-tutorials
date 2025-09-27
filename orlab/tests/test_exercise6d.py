"""Tests for the iterative tank utilization solver."""

from __future__ import annotations

import math
import sys

import pytest

pd = pytest.importorskip("pandas")

from orlab.exercise6d import _lexicographic_weights


def test_lexicographic_weights_remain_finite_and_ordered():
    """Weights stay finite for large tank counts and preserve ordering."""

    num_tanks = 95
    base_spare = 28_000.0
    spare_capacity = pd.Series(
        [base_spare + ((i % 11) - 5) * 0.125 for i in range(num_tanks)],
        index=[f"tank_{i}" for i in range(num_tanks)],
    ).sample(frac=1.0, random_state=42)

    weights = _lexicographic_weights(spare_capacity)
    assert len(weights) == num_tanks

    assert all(math.isfinite(value) for value in weights.values())
    assert all(value >= sys.float_info.min for value in weights.values())

    priority_order = list(spare_capacity.sort_values(kind="mergesort").index)
    ordered_weights = [weights[tank] for tank in priority_order]

    for earlier, later in zip(ordered_weights, ordered_weights[1:]):
        assert earlier > later

    cumulative_tail = 0.0
    for weight in reversed(ordered_weights):
        assert weight > cumulative_tail
        cumulative_tail += weight
