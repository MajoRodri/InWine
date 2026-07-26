"""
Router de recomendación / Recommendation router.
"""

from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse

from app.services.recommender import get_wine_recommendation, get_filter_options
from app.templates_config import templates

router = APIRouter()


@router.get("/recomendar", response_class=HTMLResponse)
async def recommend_form(request: Request):
    """Muestra el formulario de 7 pasos / Shows the 7-step form."""
    return templates.TemplateResponse(request, "recommend.html", {
        "filter_opts": get_filter_options(),
    })


@router.post("/recomendar", response_class=HTMLResponse)
async def recommend_result(
    request: Request,
    food: str = Form(...),
    budget: int = Form(30),
    wine_type: str = Form("Sin preferencia"),
    region: str = Form("Sin preferencia"),
    grape_variety: str = Form("Sin preferencia"),
    occasion: str = Form("Día a día"),
    flavor: str = Form("Sin preferencia"),
):
    """Procesa el formulario y devuelve la recomendación."""
    recommendation = get_wine_recommendation(
        food, budget, wine_type, region, grape_variety, occasion, flavor
    )
    return templates.TemplateResponse(request, "recommend.html", {
        "recommendation": recommendation,
        "filter_opts": get_filter_options(),
        "form_data": {
            "food": food, "budget": budget, "wine_type": wine_type,
            "region": region, "grape_variety": grape_variety,
            "occasion": occasion, "flavor": flavor,
        },
    })
