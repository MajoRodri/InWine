"""
Wine recommendation service / Servicio de recomendación de vinos.
"""

from app.data.loader import WINES
from app.data import WINE_PROFILES
from app.data.food_options import FOOD_OPTIONS
from app.data.user_profiles import USER_PROFILES, USER_PROFILES_BY_ID

_VALID_WINE_TYPES = {"Tinto", "Blanco", "Rosado", "Espumoso", "Generoso", "Sin preferencia"}
_NO_PREF = "Sin preferencia"


def _clean(value: str | None) -> str:
    """Strip and normalise a string input. / Limpia y normaliza una entrada de texto."""
    return (value or "").strip()


def get_filter_options() -> dict:
    """Return unique regions and grape varieties for form dropdowns.
    Devuelve regiones y uvas únicas para los desplegables del formulario."""
    regions = sorted(set(w["region"] for w in WINES))
    grapes = sorted({
        g.strip()
        for w in WINES
        for g in w["grape_variety"].split(" / ")
    })
    return {"regions": regions, "grapes": grapes}


# Food → preferred wine types / Comida → tipos de vino preferidos
_FOOD_WINE_MAP = {
    "carne_roja": ["Tinto"],
    "pescado":    ["Blanco"],
    "marisco":    ["Blanco", "Espumoso"],
    "aves":       ["Blanco", "Tinto"],
    "pasta":      ["Tinto", "Rosado"],
    "quesos":     ["Tinto", "Blanco", "Generoso"],
    "postres":    ["Espumoso", "Generoso"],
    "aperitivo":  ["Espumoso", "Blanco", "Rosado", "Generoso"],
}

_FOOD_LABELS = {
    "carne_roja": "carnes rojas",
    "pescado":    "pescado",
    "marisco":    "marisco",
    "aves":       "aves",
    "pasta":      "pasta o arroz",
    "quesos":     "quesos",
    "postres":    "postres",
    "aperitivo":  "aperitivo",
}

_AGEING_LABELS = {
    "Crianza": "crianza en barrica",
    "Joven":   "estilo joven y fresco",
}

# Razones de maridaje por plato — tono humano y cálido
_FOOD_PAIRING_REASONS = {
    "carne_roja": (
        "Las carnes rojas piden un tinto con carácter: sus taninos se ablandan con las proteínas y la grasa de la carne, "
        "creando ese equilibrio que hace que cada bocado sea mejor que el anterior."
    ),
    "pescado": (
        "El pescado tiene una textura delicada que se realza con un blanco fresco — "
        "su acidez limpia el paladar entre bocado y bocado sin eclipsar el sabor del mar."
    ),
    "marisco": (
        "El marisco tiene ese punto yodado y salino que encaja de maravilla con la acidez mineral de un buen blanco. "
        "Uno realza al otro y el resultado es sencillamente delicioso."
    ),
    "aves": (
        "Las aves son versátiles: su carne suave admite tanto blancos con cuerpo como tintos de carácter ligero. "
        "Este en concreto da justo en el clavo para conseguir ese equilibrio perfecto."
    ),
    "pasta": (
        "La pasta y el arroz agradecen un vino con personalidad propia que acompañe sin eclipsar el plato — "
        "ni demasiado tímido ni demasiado contundente, simplemente el compañero ideal."
    ),
    "quesos": (
        "El queso es uno de los maridajes más gratificantes: la grasa y la sal contrastan con la estructura del vino "
        "y se potencian mutuamente. Juntos son más de lo que son por separado."
    ),
    "postres": (
        "Los postres piden un vino con personalidad dulce o efervescente que no compita con el plato sino que lo celebre. "
        "Es el broche de oro que merece cualquier buena comida."
    ),
    "aperitivo": (
        "Para el aperitivo lo ideal es algo festivo y ligero que abra el apetito sin cansar el paladar. "
        "Un vino que invite a la conversación y ponga el ambiente desde el primer sorbo."
    ),
}

_GRAPE_ES = {
    "Grenache":    "Garnacha",
    "Carinena":    "Cariñena",
    "Tempranillo": "Tempranillo",
    "Albarino":    "Albariño",
    "Monastrell":  "Monastrell",
    "Verdejo":     "Verdejo",
    "Viura":       "Viura",
    "Mencia":      "Mencía",
}

# Flavor preference → keyword in flavor_descriptor
# Preferencia de sabor → palabra clave en flavor_descriptor
_FLAVOR_MAP = {
    "Afrutado":  "fruta",
    "Seco":      "mineral",
    "Especiado": "especias",
    "Suave":     "floral",
    "Robusto":   "tabaco",
}


def get_wine_recommendation(
    food: str, budget: int, wine_type: str,
    region: str, grape_variety: str,
    occasion: str, flavor: str,
) -> dict | None:
    """Return the best wine matching the user's parameters.
    Devuelve el mejor vino según los parámetros del usuario."""
    food = _clean(food)
    wine_type = _clean(wine_type) or _NO_PREF
    region = _clean(region) or _NO_PREF
    grape_variety = _clean(grape_variety) or _NO_PREF
    occasion = _clean(occasion) or "Día a día"
    flavor = _clean(flavor) or _NO_PREF
    budget = max(1, int(budget))

    if wine_type not in _VALID_WINE_TYPES:
        wine_type = _NO_PREF

    # 1. Filtro DURO de presupuesto — primero, nunca se relaja
    in_budget = [w for w in WINES if w["price_euros"] <= budget]
    if not in_budget:
        return None
    candidates = in_budget

    # 2. Tipo de vino (duro cuando el usuario elige uno)
    if wine_type != _NO_PREF:
        candidates = [w for w in candidates if w["vine_type"] == wine_type]

    # 3. Región (blando — los desplegables vienen del dataset, rara vez vacío)
    if region != _NO_PREF:
        region_match = [w for w in candidates if w["region"] == region]
        if region_match:
            candidates = region_match

    # 4. Variedad de uva (blando — misma razón)
    if grape_variety != _NO_PREF:
        grape_match = [w for w in candidates if grape_variety in w["grape_variety"]]
        if grape_match:
            candidates = grape_match

    # 5. Maridaje por comida (blando — preferencia orientativa)
    preferred_types = _FOOD_WINE_MAP.get(food, [])
    if preferred_types and wine_type == _NO_PREF:
        food_match = [w for w in candidates if w["vine_type"] in preferred_types]
        if food_match:
            candidates = food_match

    # 6. Sabor (blando — preferencia orientativa)
    if flavor != _NO_PREF:
        keyword = _FLAVOR_MAP.get(flavor, "")
        if keyword:
            flavor_match = [
                w for w in candidates
                if keyword in (w.get("flavor_descriptor") or "")
            ]
            if flavor_match:
                candidates = flavor_match

    if not candidates:
        return None

    best = max(candidates, key=lambda w: w["rating"])

    food_label = _FOOD_LABELS.get(food, food)
    explanation = (
        f"He seleccionado {best['wine_name']} de {best['winery']} porque su perfil "
        f"de {best['vine_type'].lower()} de {best['region']} marida perfectamente con "
        f"{food_label}. Con {best['price_euros']:.0f}€ entra en tu presupuesto y su "
        f"valoración de {best['rating']}/5 lo convierte en una elección ideal para "
        f"{occasion.lower()}."
    )

    return {**best, "explanation": explanation}


def get_wine_recommendation_chat(
    food: str,
    budget: int,
    wine_type: str,
    ageing: str,
    exclude_ids: list[int] | None = None,
    reference_id: int | None = None,
) -> dict | None:
    """Chatbot recommendation using real dataset scoring.
    Usa datos reales del dataset para puntuar y recomendar."""
    food = _clean(food)
    wine_type = _clean(wine_type) or _NO_PREF
    ageing = _clean(ageing) or "Indiferente"
    budget = max(1, int(budget))

    # 1. Filtro DURO de presupuesto — siempre primero, nunca se relaja
    in_budget = [w for w in WINES if w["price_euros"] <= budget]
    if not in_budget:
        return None
    candidates = in_budget

    # 2. Filtro de tipo de vino (blando — si no hay resultado se queda con in_budget)
    if wine_type != _NO_PREF and wine_type in _VALID_WINE_TYPES:
        type_match = [w for w in candidates if w["vine_type"] == wine_type]
        if type_match:
            candidates = type_match
    else:
        # Sin preferencia → guiar por maridaje con la comida
        preferred = _FOOD_WINE_MAP.get(food, [])
        if preferred:
            food_match = [w for w in candidates if w["vine_type"] in preferred]
            if food_match:
                candidates = food_match

    # 3. Filtro de crianza (blando — si no hay resultado se queda con los anteriores)
    if ageing != "Indiferente":
        ageing_match = [w for w in candidates if w.get("wine_ageing") == ageing]
        if ageing_match:
            candidates = ageing_match

    if exclude_ids:
        candidates = [w for w in candidates if w["id"] not in exclude_ids]

    # Si hay vino de referencia, restringir al mismo cluster (estilo similar)
    if reference_id:
        ref = next((w for w in WINES if w["id"] == reference_id), None)
        if ref:
            same_cluster = [w for w in candidates if w["cluster_id"] == ref["cluster_id"]]
            if same_cluster:
                candidates = same_cluster

    if not candidates:
        return None

    # 4. Scoring multi-factor (todos los candidatos ya están dentro del presupuesto)
    preferred_types = _FOOD_WINE_MAP.get(food, [])

    def score(w: dict) -> float:
        s = 0.0
        # Valoración real
        s += (w["rating"] - 4.0) * 5.0
        # Ratio calidad-precio real
        if w.get("quality_price_ratio", 0) > 0.08:
            s += 1.0
        # Maridaje comida-tipo real
        if preferred_types and w["vine_type"] in preferred_types:
            s += 2.0
        return s

    best = max(candidates, key=score)

    # 5. Explicación con campos reales del dataset
    food_label = _FOOD_LABELS.get(food, food)
    vine = best["vine_type"].lower()
    region = best["region"]
    grape_raw = best.get("grape_variety", "")
    wine_ageing = best.get("wine_ageing", "")

    grape = _GRAPE_ES.get(grape_raw, grape_raw) if grape_raw not in ("Blend/Other", "") else ""
    grape_part = f", elaborado con uva <em>{grape}</em>," if grape else ""
    ageing_desc = _AGEING_LABELS.get(wine_ageing, "")
    ageing_part = f" Es un vino de {ageing_desc}," if ageing_desc else ""

    pairing_reason = _FOOD_PAIRING_REASONS.get(food, f"que marida a la perfección con {food_label}")

    explanation = (
        f"Mi elección es <strong>{best['wine_name']}</strong>, de la bodega {best['winery']} — "
        f"un {vine} de {region}{grape_part} con una valoración de {best['rating']:.1f} sobre 5, "
        f"que lo sitúa entre los mejores de su categoría.{ageing_part} "
        f"{pairing_reason} "
        f"Y a {best['price_euros']:.0f}€ es una opción que cumple de sobra con las expectativas."
    )

    return {**best, "explanation": explanation}


def get_wine_by_id(wine_id: int) -> dict | None:
    """Find a wine by its ID."""
    return next((w for w in WINES if w["id"] == wine_id), None)


def get_wines_by_cluster(cluster_id: int, max_price: float | None = None) -> list[dict]:
    """Return wines belonging to a cluster, optionally capped by budget."""
    wines = [w for w in WINES if w["cluster_id"] == cluster_id]
    if max_price is not None:
        wines = [w for w in wines if w["price_euros"] <= max_price]
        return sorted(wines, key=lambda w: w.get("rating", 0), reverse=True)
    return wines


def get_wines_by_budget(max_price: float, exclude_ids: set | None = None) -> list[dict]:
    """Return best-rated wines within budget, excluding given IDs."""
    wines = [w for w in WINES if w["price_euros"] <= max_price]
    if exclude_ids:
        wines = [w for w in wines if w["id"] not in exclude_ids]
    return sorted(wines, key=lambda w: w.get("rating", 0), reverse=True)


def get_similar_wines(wine_id: int, n: int = 3) -> list[dict]:
    """Return wines from the same cluster, excluding the current wine.
    Devuelve vinos del mismo cluster excluyendo el actual."""
    if not isinstance(wine_id, int) or wine_id < 1:
        return []
    wine = next((w for w in WINES if w["id"] == wine_id), None)
    if not wine:
        return []
    similar = [
        w for w in WINES
        if w["cluster_id"] == wine["cluster_id"] and w["id"] != wine_id
    ]
    return similar[:n]


def get_user_profile(answers: list[str]) -> dict:
    """Map quiz answers to a user wine personality profile via voting.
    Asigna un perfil vinícola del usuario basado en las respuestas del quiz.

    Profile reference / Referencia de perfiles:
      0 = El Coleccionista       — high-end, collector
      1 = El Amante del Blanco   — whites, fresh, seafood
      2 = El Explorador          — young reds, emerging regions
      3 = El Libre Pensador      — eclectic, affordable
      4 = El Sibarita            — fortified, jerez, gourmet
      5 = El Festivo             — sparkling, celebrations
      6 = El Clásico             — classic aged reds, Rioja/Ribera
      7 = El Cotidiano Premium   — everyday quality reds
    """
    answer_profile_map = {
        # Q1: flavors / sabores
        "frutas_frescas": 7,  "frutas_secas": 4,  "especias": 6,
        "hierbas": 1,          "maderas": 0,
        # Q2: body / cuerpo
        "ligero": 1,  "estructura": 6,  "cremoso": 5,  "burbujas": 5,
        # Q3: price / precio
        "menos_10": 3,  "10_20": 7,  "20_40": 2,  "mas_40": 0,
        # Q4: frecuencia
        "celebraciones": 5,  "fines_semana": 6,  "frecuente": 7,  "siempre": 6,
        # Q5: cuisine / cocina
        "mediterranea": 1,  "carnes": 6,  "mariscos": 5,  "variada": 7,
        # Q6: tipo de vino preferido
        "pref_tinto": 7,  "pref_blanco": 1,  "pref_espumoso": 5,
        "pref_generoso": 4,  "pref_sin_pref": 3,
        # Q7: carácter del vino
        "car_joven": 7,  "car_barrica": 6,  "car_reserva": 0,
        "car_espumoso": 5,  "car_indiferente": 3,
        # Q8: criterio de elección
        "criterio_tradicion": 6,  "criterio_sorpresa": 3,
        "criterio_precio": 7,     "criterio_exclusividad": 0,
    }

    votes: dict[int, int] = {}
    for ans in (answers or []):
        profile_id = answer_profile_map.get(_clean(ans), 7)
        votes[profile_id] = votes.get(profile_id, 0) + 1

    profile_id = max(votes, key=lambda k: votes[k]) if votes else 7
    return USER_PROFILES_BY_ID.get(profile_id, USER_PROFILES[0])
