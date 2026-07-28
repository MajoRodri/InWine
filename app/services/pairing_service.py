"""
Pairing and value service / Servicio de maridaje y calidad-precio.
"""

from app.data.loader import WINES
from app.data.food_options import FOOD_OPTIONS


def get_food_pairings(food_key: str) -> list[dict]:
    """Return recommended wines for a food type.
    Devuelve vinos recomendados para un tipo de comida."""
    food = next((f for f in FOOD_OPTIONS if f["key"] == food_key), None)
    if not food:
        return []

    preferred_types = food["wine_types"]
    preferred_ageing = food["ageing"]

    # Two-tier matching: wines that match BOTH type and ageing come first,
    # then wines that match only type. This surfaces the best pairing first
    # while keeping the list broad enough to always show results.
    # Maridaje en dos niveles: primero los vinos que coinciden en tipo Y crianza,
    # luego los que solo coinciden en tipo, para asegurar siempre resultados.
    primary = [
        w for w in WINES
        if w["vine_type"] in preferred_types and w["wine_ageing"] in preferred_ageing
    ]
    secondary = [
        w for w in WINES
        if w["vine_type"] in preferred_types and w not in primary
    ]

    results = primary + secondary
    return sorted(results, key=lambda w: w["rating"], reverse=True)[:6]


def get_food_pairings_split(food_key: str) -> dict:
    """Return top 3 by rating and top 3 by quality-price ratio for a food.
    Devuelve top 3 por valoración y top 3 por ratio calidad-precio para un plato."""
    food = next((f for f in FOOD_OPTIONS if f["key"] == food_key), None)
    if not food:
        return {"top": [], "value": []}

    preferred_types = food["wine_types"]
    preferred_ageing = food["ageing"]

    primary = [
        w for w in WINES
        if w["vine_type"] in preferred_types and w["wine_ageing"] in preferred_ageing
    ]
    secondary = [
        w for w in WINES
        if w["vine_type"] in preferred_types and w not in primary
    ]
    all_candidates = primary + secondary

    top = sorted(all_candidates, key=lambda w: w["rating"], reverse=True)[:3]
    top_ids = {w["id"] for w in top}

    # Value picks exclude the top-rated three to avoid showing the same wines twice
    # Los de calidad-precio excluyen los tres mejor valorados para no repetir
    remaining = [w for w in all_candidates if w["id"] not in top_ids]
    value = sorted(remaining, key=lambda w: w.get("quality_price_ratio", 0), reverse=True)[:3]

    return {"top": top, "value": value}


def get_value_filter_options() -> dict:
    """Return unique filter values derived from the real dataset."""
    vine_types = sorted({w["vine_type"] for w in WINES if w["vine_type"] != "Desconocido"})
    regions = sorted({w["region"] for w in WINES})
    grapes = sorted({g.strip() for w in WINES for g in w["grape_variety"].split(" / ")})
    return {"vine_types": vine_types, "regions": regions, "grapes": grapes}


def get_best_value_wines(
    max_price: int = 50,
    min_rating: float = 4.2,
    wine_types: list[str] | None = None,
    regions: list[str] | None = None,
    grape_varieties: list[str] | None = None,
    sort_by: str = "ratio",
) -> list[dict]:
    """Return best quality-price wines applying all active filters."""
    filtered = [
        w for w in WINES
        if w["price_euros"] <= max_price
        and w["rating"] >= min_rating
        and (not wine_types or w["vine_type"] in wine_types)
        and (not regions or w["region"] in regions)
        and (not grape_varieties or any(gv in w["grape_variety"] for gv in grape_varieties))
    ]
    if sort_by == "price_asc":
        return sorted(filtered, key=lambda w: w["price_euros"])
    if sort_by == "price_desc":
        return sorted(filtered, key=lambda w: w["price_euros"], reverse=True)
    return sorted(filtered, key=lambda w: w["quality_price_ratio"], reverse=True)


