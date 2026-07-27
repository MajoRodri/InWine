"""
InWine — Sommelier IA
Punto de entrada de la aplicación FastAPI / FastAPI application entry point.

Ejecutar localmente / Run locally:
    uvicorn app.main:app --reload

Despliegue en Railway / Railway deployment:
    Configured via railway.toml — PORT is set automatically by the platform.
"""

import os
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routers import home, recommend, search, explore, profile, food, value, wine, about

# ── Crear la aplicación / Create the app ──────────────────────────────────────

app = FastAPI(
    title="InWine — Sommelier IA",
    description="Tu sumiller virtual de vinos españoles",
    version="0.1.0",
)

# ── Archivos estáticos (CSS, JS, imágenes) / Static files ─────────────────────

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# ── Registrar routers / Register routers ──────────────────────────────────────

app.include_router(home.router)
app.include_router(recommend.router)
app.include_router(search.router)
app.include_router(explore.router)
app.include_router(profile.router)
app.include_router(food.router)
app.include_router(value.router)
app.include_router(wine.router)
app.include_router(about.router)

# ── Punto de entrada directo / Direct entry point ─────────────────────────────
# Railway sets $PORT automatically; locally defaults to 8000.
# Railway asigna $PORT automáticamente; localmente usa 8000 por defecto.

if __name__ == "__main__":
    try:
        port = int(os.getenv("PORT", "8000"))
    except ValueError:
        port = 8000
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
