"""
Reproduction test for SCRUM-6.

Intentionally ephemeral — kept as regression guard after the fix.
"""

import pytest
from src.calculator import calculate_order_total


class TestReproSCRUM6:
    """Directly reproduces the bug described in SCRUM-6 (SyntaxError in calculator.py)."""

    def test_calculate_order_total_returns_dict(self):
        """
        As reported: importing calculate_order_total raises SyntaxError because
        the dict literal in the return statement was never closed.
        Expected: calculate_order_total(10.0, 2, 1.0) == {"subtotal": 20.0, "shipping": 0.0, "total": 20.0}.
        Got: SyntaxError — '{' was never closed at line 48 of src/calculator.py.
        """
        result = calculate_order_total(10.0, 2, 1.0)
        assert result == {"subtotal": 20.0, "shipping": 0.0, "total": 20.0}

    def test_calculate_order_total_with_shipping(self):
        """
        As reported: module cannot be imported at all due to SyntaxError.
        Expected: calculate_order_total(5.0, 3, 10.0) == {"subtotal": 15.0, "shipping": 5.0, "total": 20.0}.
        Got: SyntaxError — module fails to load.
        """
        result = calculate_order_total(5.0, 3, 10.0)
        assert result == {"subtotal": 15.0, "shipping": 5.0, "total": 20.0}
