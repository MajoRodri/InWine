"""
Wine search service / Servicio de búsqueda de vinos.
"""

from app.data.loader import WINES


def search_wines(query: str) -> list[dict]:
    """Case-insensitive substring search across name, winery, region and grape.
    Búsqueda de subcadena insensible a mayúsculas en nombre, bodega, región y uva."""
    q = query.strip().lower()
    if not q:
        return []

    results = []
    for wine in WINES:
        searchable = " ".join([
            wine["wine_name"],
            wine["winery"],
            wine["region"],
            wine["grape_variety"],
            wine["vine_type"],
        ]).lower()
        if q in searchable:
            results.append(wine)

    return sorted(results, key=lambda w: w["rating"], reverse=True)
