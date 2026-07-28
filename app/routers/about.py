"""
About page router / Router de la página 'Nosotros'.
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from app.templates_config import templates

router = APIRouter()


@router.get("/nosotros", response_class=HTMLResponse)
async def about(request: Request):
    """About page: team and methodology. / Página del equipo y metodología."""
    return templates.TemplateResponse(request, "about.html", {})
