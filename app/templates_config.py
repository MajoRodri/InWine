"""
Instancia compartida de Jinja2Templates / Shared Jinja2Templates instance.

Usa ruta absoluta para evitar problemas con el directorio de trabajo.
Uses absolute path to avoid working-directory issues.

NOTA: El caché LRU de Jinja2 3.1.x no es compatible con Python 3.14
(TypeError al usar dict como clave de tuple). Se deshabilita hasta que
Jinja2 publique un fix oficial.
NOTE: Jinja2 3.1.x LRU cache is incompatible with Python 3.14
(TypeError when using dict as tuple key). Disabled until Jinja2 ships a fix.
"""

import os
from fastapi.templating import Jinja2Templates

# Ruta absoluta al directorio de templates / Absolute path to templates dir
_BASE   = os.path.dirname(os.path.abspath(__file__))          # .../app
_TMPL   = os.path.join(_BASE, "templates")

templates = Jinja2Templates(directory=_TMPL)

# Deshabilitar LRU cache — bug en Jinja2 3.1.x con Python 3.14
# Disable LRU cache — Jinja2 3.1.x bug with Python 3.14
templates.env.cache = None  # type: ignore[assignment]
