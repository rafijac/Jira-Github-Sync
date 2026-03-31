"""
Reproduction test for SCRUM-5.

Acts as a permanent regression guard once the fix is applied.
"""

from src.calculator import calculate_shipping_cost, calculate_order_total


class TestReproSCRUM5:
    """Directly reproduces the bug described in SCRUM-5."""

    def test_just_over_20kg(self):
        """
        As reported: weight=21.0 → expected $15.00 (heavy tier), got $5.00 (standard tier).
        The elif weight_kg >= 5 branch catches all weights >= 5, including > 20,
        so the heavy tier is dead code and never evaluated.
        """
        assert calculate_shipping_cost(21.0) == 15.00

    def test_very_heavy_package(self):
        """
        As reported: weight=25.0 → expected $15.00 (heavy tier), got $5.00 (standard tier).
        """
        assert calculate_shipping_cost(25.0) == 15.00

    def test_heavy_order_total(self):
        """
        As reported: order with weight=25.0 → expected shipping=$15.00, total=$35.00,
        got shipping=$5.00, total=$25.00.
        """
        result = calculate_order_total(unit_price=5.0, quantity=4, weight_kg=25.0)
        assert result["shipping"] == 15.00
        assert result["total"] == 35.00
