"""
Pytest suite for src/calculator.py — calculate_shipping_cost.

Two tests below are EXPECTED TO FAIL on the unpatched codebase because the
heavy-shipping tier (> 20 kg → $15.00) is unreachable dead code.

  XFAIL markers are intentionally NOT used: the failures must be visible in CI
  so the automation loop knows exactly what to fix.
"""

import pytest

from src.calculator import calculate_shipping_cost, calculate_order_total


# ---------------------------------------------------------------------------
# calculate_shipping_cost — happy-path / boundary tests
# ---------------------------------------------------------------------------

class TestFreeShipping:
    def test_zero_weight(self):
        assert calculate_shipping_cost(0.0) == 0.00

    def test_well_under_threshold(self):
        assert calculate_shipping_cost(2.5) == 0.00

    def test_just_below_threshold(self):
        assert calculate_shipping_cost(4.99) == 0.00


class TestStandardShipping:
    def test_exactly_5kg(self):
        assert calculate_shipping_cost(5.0) == 5.00

    def test_midrange(self):
        assert calculate_shipping_cost(12.0) == 5.00

    def test_exactly_20kg(self):
        """20 kg sits on the boundary — should still be standard rate."""
        assert calculate_shipping_cost(20.0) == 5.00


class TestHeavyShipping:
    """
    These two tests expose JIRA-101.

    On the unpatched code both fail with:
        AssertionError: assert 5.0 == 15.0
    because weight_kg >= 5 absorbs all weights, making weight_kg > 20 dead code.
    """

    def test_just_over_20kg(self):
        """21 kg should cost $15.00 — FAILS on buggy code (returns $5.00)."""
        assert calculate_shipping_cost(20.1) == 15.00  # FAILS

    def test_very_heavy_package(self):
        """50 kg should cost $15.00 — FAILS on buggy code (returns $5.00)."""
        assert calculate_shipping_cost(50.0) == 15.00  # FAILS


# ---------------------------------------------------------------------------
# calculate_shipping_cost — edge / error tests
# ---------------------------------------------------------------------------

class TestShippingEdgeCases:
    def test_negative_weight_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            calculate_shipping_cost(-1.0)

    def test_float_precision_boundary(self):
        """5.000001 kg rounds into the standard tier, not free."""
        assert calculate_shipping_cost(5.000001) == 5.00


# ---------------------------------------------------------------------------
# calculate_order_total — integration smoke tests
# ---------------------------------------------------------------------------

class TestOrderTotal:
    def test_light_order_no_shipping(self):
        result = calculate_order_total(unit_price=10.0, quantity=3, weight_kg=1.0)
        assert result["subtotal"] == 30.00
        assert result["shipping"] == 0.00
        assert result["total"] == 30.00

    def test_standard_shipping_order(self):
        result = calculate_order_total(unit_price=20.0, quantity=2, weight_kg=8.0)
        assert result["subtotal"] == 40.00
        assert result["shipping"] == 5.00
        assert result["total"] == 45.00

    def test_heavy_shipping_order(self):
        """
        Depends on calculate_shipping_cost(25.0) returning 15.00.
        Also FAILS on buggy code because shipping returns 5.00 instead of 15.00.
        """
        result = calculate_order_total(unit_price=5.0, quantity=4, weight_kg=25.0)
        assert result["subtotal"] == 20.00
        assert result["shipping"] == 15.00   # FAILS on buggy code
        assert result["total"] == 35.00      # FAILS on buggy code
