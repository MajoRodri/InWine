"""
Router de búsqueda / Search router.
"""

from typing import Optional

from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse

from app.data.loader import WINES
from app.services.search_service import search_wines
from app.templates_config import templates

router = APIRouter()

_WINES_BY_RATING = sorted(WINES, key=lambda w: w["rating"], reverse=True)


@router.get("/buscar", response_class=HTMLResponse)
async def search_page(request: Request, q: Optional[str] = Query(default=None, max_length=100)):
    """Wine search by name, winery or region. / Búsqueda de vinos por nombre, bodega o región."""
    results = search_wines(q) if q else []
    return templates.TemplateResponse(request, "search.html", {
        "query": q or "",
        "results": results,
        "result_count": len(results),
    })


@router.get("/api/sugerencias")
async def suggestions(q: str = Query(default="", max_length=100)):
    """Returns autocomplete suggestions as the user types. / Devuelve sugerencias de autocompletado mientras el usuario escribe."""
    q_lower = q.strip().lower()
    if len(q_lower) < 2:
        return JSONResponse([])

    names, wineries, regions = [], [], []
    seen_names, seen_wineries, seen_regions = set(), set(), set()

    for wine in _WINES_BY_RATING:
        wn, wr, rg = wine["wine_name"], wine["winery"], wine["region"]

        if len(names) < 5 and q_lower in wn.lower() and wn not in seen_names:
            seen_names.add(wn)
            names.append({"label": wn, "sublabel": wr, "type": "vino", "id": wine["id"]})

        if len(wineries) < 2 and q_lower in wr.lower() and wr not in seen_wineries:
            seen_wineries.add(wr)
            wineries.append({"label": wr, "type": "bodega"})

        if len(regions) < 2 and q_lower in rg.lower() and rg not in seen_regions:
            seen_regions.add(rg)
            regions.append({"label": rg, "type": "región"})

        if len(names) >= 5 and len(wineries) >= 2 and len(regions) >= 2:
            break

    return JSONResponse(names + wineries + regions)
