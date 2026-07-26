"""
Router de maridaje por comida / Food pairing router.
"""

from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Optional

from app.data.food_options import FOOD_OPTIONS
from app.services.pairing_service import get_food_pairings, get_food_pairings_split
from app.services.recommender import get_wine_recommendation, get_wine_recommendation_chat
from app.templates_config import templates

router = APIRouter()


@router.get("/comida", response_class=HTMLResponse)
async def food_page(request: Request, food: Optional[str] = None):
    """Food selection page and pairing display. / Selección de plato y visualización de maridajes."""
    pairings = get_food_pairings(food) if food else []
    selected = next((f for f in FOOD_OPTIONS if f["key"] == food), None)

    return templates.TemplateResponse(request, "food.html", {
        "food_options": FOOD_OPTIONS,
        "selected_food": selected,
        "pairings": pairings,
    })


@router.post("/comida", response_class=HTMLResponse)
async def food_result(request: Request, food: str = Form(...)):
    """Receives food selection via POST and shows pairings. / Recibe la selección de plato vía POST y muestra maridajes."""
    pairings = get_food_pairings(food)
    selected = next((f for f in FOOD_OPTIONS if f["key"] == food), None)

    return templates.TemplateResponse(request, "food.html", {
        "food_options": FOOD_OPTIONS,
        "selected_food": selected,
        "pairings": pairings,
    })


@router.get("/api/pairing")
async def food_api(food: str):
    """Returns food pairings as JSON for the chatbot. / Devuelve maridajes en JSON para el chatbot."""
    selected = next((f for f in FOOD_OPTIONS if f["key"] == food), None)
    if not selected:
        return JSONResponse({"error": "not found"}, status_code=404)

    split = get_food_pairings_split(food)

    def wine_summary(w: dict) -> dict:
        return {
            "id": w["id"],
            "wine_name": w["wine_name"],
            "winery": w["winery"],
            "vine_type": w["vine_type"],
            "region": w["region"],
            "rating": w["rating"],
            "price_euros": w["price_euros"],
        }

    return {
        "food": {
            "key": selected["key"],
            "name": selected["name"],
            "description": selected["description"],
        },
        "top_pairings": [wine_summary(w) for w in split["top"]],
        "value_pairings": [wine_summary(w) for w in split["value"]],
    }


@router.get("/api/recommend-chat")
async def recommend_chat_api(
    food: str,
    wine_type: str = "Sin preferencia",
    ageing: str = "Indiferente",
    budget: int = 30,
    exclude_ids: str = "",
    reference_id: int = 0,
):
    """Chatbot recommendation using real dataset: type, ageing and budget. / Recomendación usando datos reales: tipo, crianza y presupuesto del dataset."""
    parsed_ids = [int(x) for x in exclude_ids.split(",") if x.strip().isdigit()]
    rec = get_wine_recommendation_chat(
        food=food,
        budget=budget,
        wine_type=wine_type,
        ageing=ageing,
        exclude_ids=parsed_ids or None,
        reference_id=reference_id or None,
    )
    if not rec:
        return {"recommendation": None}
    return {
        "recommendation": {
            "id": rec["id"],
            "wine_name": rec["wine_name"],
            "winery": rec["winery"],
            "vine_type": rec["vine_type"],
            "region": rec["region"],
            "grape_variety": rec.get("grape_variety", ""),
            "wine_ageing": rec.get("wine_ageing", ""),
            "rating": rec["rating"],
            "price_euros": rec["price_euros"],
            "explanation": rec["explanation"],
        }
    }
