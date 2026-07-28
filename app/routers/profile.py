"""
Router del quiz de perfil vinícola / Wine taste profile quiz router.
"""

from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse

from app.data.user_profiles import USER_PROFILES
from app.services.recommender import get_user_profile, get_profile_wines
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
    q6: str = Form("pref_tinto"),
    q7: str = Form("car_joven"),
    q8: str = Form("criterio_precio"),
):
    """Assigns a wine personality profile and recommends wines from its cluster. / Asigna un perfil al usuario y recomienda vinos de ese cluster."""
    answers = [q1, q2, q3, q4, q5, q6, q7, q8]
    profile = get_user_profile(answers)
    max_price = _PRICE_MAX.get(q3)

    recommended = get_profile_wines(
        profile["cluster_id"],
        max_price=max_price,
        vine_type_pref=q6,
        ageing_pref=q7,
        n=4,
    )

    return templates.TemplateResponse(request, "profile.html", {
        "user_profile": profile,
        "recommended_wines": recommended,
        "all_profiles": USER_PROFILES,
    })
