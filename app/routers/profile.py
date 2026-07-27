"""
Router del quiz de perfil vinícola / Wine taste profile quiz router.
"""

from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse

from app.data.user_profiles import USER_PROFILES
from app.services.recommender import get_user_profile, get_wines_by_cluster, get_wines_by_budget
from app.templates_config import templates

router = APIRouter()

_PRICE_MAX: dict[str, float | None] = {
    "menos_10": 10.0,
    "10_20":    20.0,
    "20_40":    40.0,
    "mas_40":   None,
}


@router.get("/perfil", response_class=HTMLResponse)
async def profile_page(request: Request):
    """Renders the 8-question wine personality quiz. / Muestra el quiz de 8 preguntas."""
    return templates.TemplateResponse(request, "profile.html", {
        "all_profiles": USER_PROFILES,
    })


@router.post("/perfil", response_class=HTMLResponse)
async def profile_result(
    request: Request,
    q1: str = Form("frutas_frescas"),
    q2: str = Form("ligero"),
    q3: str = Form("menos_10"),
    q4: str = Form("fines_semana"),
    q5: str = Form("variada"),
    q6: str = Form("pref_sin_pref"),
    q7: str = Form("car_joven"),
    q8: str = Form("criterio_precio"),
):
    """Assigns a wine personality profile and recommends wines from its cluster. / Asigna un perfil al usuario y recomienda vinos de ese cluster."""
    answers = [q1, q2, q3, q4, q5, q6, q7, q8]
    profile = get_user_profile(answers)
    max_price = _PRICE_MAX.get(q3)

    cluster_wines = get_wines_by_cluster(profile["cluster_id"], max_price=max_price)
    if len(cluster_wines) >= 4 or max_price is None:
        recommended = cluster_wines[:4]
    else:
        # Cluster too small for this budget → pad with top-rated wines from the full catalogue
        # El cluster tiene pocos vinos para este presupuesto → completar con los mejor valorados del catálogo
        seen = {w["id"] for w in cluster_wines}
        extras = get_wines_by_budget(max_price, exclude_ids=seen)
        recommended = (cluster_wines + extras)[:4]

    return templates.TemplateResponse(request, "profile.html", {
        "user_profile": profile,
        "recommended_wines": recommended,
        "all_profiles": USER_PROFILES,
    })
