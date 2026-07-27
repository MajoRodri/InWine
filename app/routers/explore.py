"""
Router de exploración de perfiles / Wine profile exploration router.
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from typing import Optional

from app.data import WINE_PROFILES
from app.services.recommender import get_wines_by_cluster
from app.templates_config import templates

router = APIRouter()


@router.get("/explorar", response_class=HTMLResponse)
async def explore_page(request: Request, cluster: Optional[int] = None):
    """Shows wine cluster profiles. If ?cluster=N is provided, displays wines for that profile.
    Muestra los perfiles (clusters) de vinos. Si se pasa ?cluster=N, muestra los vinos de ese perfil."""
    selected = next((p for p in WINE_PROFILES if p["id"] == cluster), None)
    cluster_wines = get_wines_by_cluster(cluster) if cluster is not None else []

    top_wines = {
        p["id"]: sorted(get_wines_by_cluster(p["id"]), key=lambda w: w["rating"], reverse=True)[:3]
        for p in WINE_PROFILES
    }

    return templates.TemplateResponse(request, "explore.html", {
        "profiles": WINE_PROFILES,
        "selected_profile": selected,
        "cluster_wines": cluster_wines,
        "top_wines": top_wines,
    })
