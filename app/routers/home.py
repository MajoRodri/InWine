"""
Home page router / Router de la página de inicio.
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.data import WINES, WINE_PROFILES
from app.templates_config import templates

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with hero, features and featured wines.
    Página de inicio con hero, features y vinos destacados."""
    total_regions = len(set(w["region"] for w in WINES))
    return templates.TemplateResponse(request, "index.html", {
        "featured_wines": sorted(WINES, key=lambda w: w.get("quality_price_ratio", 0), reverse=True)[:3],
        "total_wines": len(WINES),
        "total_clusters": len(WINE_PROFILES),
        "total_regions": total_regions,
    })
