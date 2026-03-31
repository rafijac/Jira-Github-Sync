"""
Order shipping cost calculator.

Shipping tiers (by package weight):
  - Under 5 kg  : Free  ($0.00)
  - 5 – 20 kg   : Standard ($5.00)
  - Over 20 kg  : Heavy   ($15.00)
"""


def calculate_shipping_cost(weight_kg: float) -> float:
    """Return the shipping cost in USD for a package of the given weight (kg).

    Args:
        weight_kg: Package weight in kilograms. Must be >= 0.

    Returns:
        Shipping cost as a float.

    Raises:
        ValueError: If weight_kg is negative.
    """
    if weight_kg < 0:
        raise ValueError(f"Weight must be non-negative, got {weight_kg}")

    if weight_kg < 5:
        return 0.00
    elif weight_kg <= 20:
        return 5.00
    else:
        return 15.00


def calculate_order_total(unit_price: float, quantity: int, weight_kg: float) -> dict:
    """Calculate the full order breakdown including subtotal, shipping, and total.

    Args:
        unit_price: Price per unit in USD.
        quantity:   Number of units ordered.
        weight_kg:  Total shipment weight in kg.

    Returns:
        A dict with keys: subtotal, shipping, total.
    """
    subtotal = unit_price * quantity
    shipping = calculate_shipping_cost(weight_kg)
    total = subtotal + shipping
    return {"subtotal": subtotal, "shipping": shipping, "total": total
