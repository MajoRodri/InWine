"""
Router de ficha completa de vino / Wine detail page router.
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.data import WINE_PROFILES
from app.services.recommender import get_wine_by_id, get_similar_wines
from app.templates_config import templates

router = APIRouter()


def _build_explanation(wine: dict, cluster: dict) -> str:
    cluster_name = cluster.get("name", "")
    vine = wine["vine_type"].lower()
    region = wine["region"]
    grape = wine["grape_variety"]
    rating = wine["rating"]
    price = wine["price_euros"]
    ageing = wine.get("wine_ageing", "Joven")

    grape_desc = (
        "un ensamblaje único de variedades"
        if any(kw in grape for kw in ("Blend", "Other", "/"))
        else f"la varietal {grape}"
    )

    if ageing in ("Joven", "", None):
        ageing_phrase = "toda la frescura y vitalidad de un vino joven sin crianza"
    elif ageing == "Crianza":
        ageing_phrase = "toda la complejidad y elegancia de su crianza en barrica"
    elif ageing == "Reserva":
        ageing_phrase = "toda la profundidad y matices de su larga crianza en barrica"
    elif ageing == "Gran Reserva":
        ageing_phrase = "toda la riqueza y evolución de su extensa crianza en barrica"
    else:
        ageing_phrase = f"toda la personalidad de un vino {ageing.lower()}"

    if rating >= 4.5:
        rating_adj = "excepcional"
    elif rating >= 4.2:
        rating_adj = "sobresaliente"
    else:
        rating_adj = "notable"

    luxury_phrase = " Una elección de coleccionista." if wine.get("luxury_category") else ""

    return (
        f"Seleccionado bajo la categoría «{cluster_name}», "
        f"este {vine} de {region} es una auténtica joya por descubrir. "
        f"Elaborado a partir de {grape_desc}, ofrece "
        f"{ageing_phrase}, "
        f"respaldado por una {rating_adj} valoración de {rating}/5. "
        f"Una propuesta de calidad excepcional por {price:.0f} €.{luxury_phrase}"
    )


def _build_explanation_en(wine: dict, cluster: dict) -> str:
    cluster_name = cluster.get("name", "")
    vine = wine["vine_type"].lower()
    region = wine["region"]
    grape = wine["grape_variety"]
    rating = wine["rating"]
    price = wine["price_euros"]
    ageing = wine.get("wine_ageing", "Joven")

    grape_desc = (
        "a unique blend of grape varieties"
        if any(kw in grape for kw in ("Blend", "Other", "/"))
        else f"the {grape} varietal"
    )

    if ageing in ("Joven", "", None):
        ageing_phrase = "all the freshness and vitality of a young, unoaked wine"
    elif ageing == "Crianza":
        ageing_phrase = "all the complexity and elegance of its time in oak barrels"
    elif ageing == "Reserva":
        ageing_phrase = "all the depth and nuance of its extended barrel ageing"
    elif ageing == "Gran Reserva":
        ageing_phrase = "all the richness and evolution of its lengthy barrel ageing"
    else:
        ageing_phrase = f"all the character of a {ageing.lower()} wine"

    if rating >= 4.5:
        rating_adj = "exceptional"
    elif rating >= 4.2:
        rating_adj = "outstanding"
    else:
        rating_adj = "notable"

    luxury_phrase = " A collector's choice." if wine.get("luxury_category") else ""

    return (
        f"Selected under the «{cluster_name}» category, "
        f"this {vine} from {region} is a true hidden gem. "
        f"Made from {grape_desc}, it delivers "
        f"{ageing_phrase}, "
        f"backed by an {rating_adj} rating of {rating}/5. "
        f"Exceptional quality at {price:.0f} €.{luxury_phrase}"
    )


@router.get("/vino/{wine_id}", response_class=HTMLResponse)
async def wine_detail(request: Request, wine_id: int):
    """Full wine detail page: info, sensory profile and similar wines. / Ficha completa del vino: info, perfil sensorial y vinos similares."""
    wine = get_wine_by_id(wine_id)

    if not wine:
        return RedirectResponse(url="/")

    cluster = next((p for p in WINE_PROFILES if p["id"] == wine["cluster_id"]), None)
    similar = get_similar_wines(wine_id, n=3)
    explanation    = _build_explanation(wine, cluster)    if cluster else None
    explanation_en = _build_explanation_en(wine, cluster) if cluster else None

    return templates.TemplateResponse(request, "wine_detail.html", {
        "wine": wine,
        "cluster": cluster,
        "similar_wines": similar,
        "explanation":    explanation,
        "explanation_en": explanation_en,
    })
