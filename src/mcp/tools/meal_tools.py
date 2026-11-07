"""Tools MCP: registro de comidas y resumen diario."""

from typing import Optional


def register_meal(
    item_name: str,
    quantity: float,
    unit: str,
    item_type: Optional[str] = None,
    date: Optional[str] = None,
) -> dict:
    """Registrar una ingesta. Si no existe el item, se crea como provisional.

    Args:
        item_name: Nombre del ingrediente o receta.
        quantity: Cantidad consumida.
        unit: 'gr' | 'ml' | 'u'.
        item_type: 'ingredient' | 'recipe'. Si None, se busca en ambos.
        date: Fecha ISO. Default: hoy.

    Returns:
        dict con status, entry_id, macros, price, day_summary.
    """
    ...


def get_day_summary(date: Optional[str] = None) -> dict:
    """Resumen del día: macros consumidos vs objetivo + gasto.

    Args:
        date: Fecha ISO. Default: hoy.

    Returns:
        dict con consumed, goal, remaining, spend, meals.
    """
    ...