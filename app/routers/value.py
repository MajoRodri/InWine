"""
Router de mejor calidad-precio / Best value wines router.
"""

from typing import List
from urllib.parse import urlencode

from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse

from app.services.pairing_service import get_best_value_wines, get_value_filter_options
from app.templates_config import templates

router = APIRouter()

PER_PAGE = 50


@router.get("/valor", response_class=HTMLResponse)
async def value_page(
    request: Request,
    max_price: int = 50,
    min_rating: float = 4.2,
    wine_types: List[str] = Query(default=[]),
    regions: List[str] = Query(default=[]),
    grape_varieties: List[str] = Query(default=[]),
    sort_by: str = "ratio",
    page: int = 1,
):
    all_wines = get_best_value_wines(max_price, min_rating, wine_types, regions, grape_varieties, sort_by)
    total = len(all_wines)
    total_pages = max(1, (total + PER_PAGE - 1) // PER_PAGE)
    page = max(1, min(page, total_pages))
    start = (page - 1) * PER_PAGE
    wines = all_wines[start : start + PER_PAGE]

    # Active filters query string (without page) for pagination links
    # Query string con filtros activos (sin page) para construir links de paginación
    filter_pairs = [("max_price", max_price), ("min_rating", min_rating), ("sort_by", sort_by)]
    filter_pairs += [("wine_types", wt) for wt in wine_types]
    filter_pairs += [("regions", r) for r in regions]
    filter_pairs += [("grape_varieties", g) for g in grape_varieties]
    filter_qs = urlencode(filter_pairs)

    filter_options = get_value_filter_options()
    return templates.TemplateResponse(request, "value.html", {
        "wines": wines,
        "total": total,
        "page": page,
        "total_pages": total_pages,
        "per_page": PER_PAGE,
        "filter_qs": filter_qs,
        "max_price": max_price,
        "min_rating": min_rating,
        "sel_wine_types": wine_types,
        "sel_regions": regions,
        "sel_grape_varieties": grape_varieties,
        "sort_by": sort_by,
        **filter_options,
    })
