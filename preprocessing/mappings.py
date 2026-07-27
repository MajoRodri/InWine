"""
mappings.py
===========
Diccionarios de mapeo semántico para Sommelier IA.

Contiene dos mapeos:
    1. FLAVOR_SEMANTIC_MAP: cada descriptor de sabor individual -> su categoría
         semántica (familia aromática). Permite pasar de 51 columnas dummy
         (una por descriptor) a solo 5 features agregadas por familia, mucho
         más manejable para el motor de similitud.
    2. SERVING_TEMP_SEMANTIC_MAP: cada rango de temperatura de servicio ->
         una etiqueta semántica ordinal + su punto medio numérico (para poder
         tratarla como variable numérica si el modelo lo necesita).

Basado en el vocabulario real presente en wines_SPA_enriched_FINAL.csv
(51 descriptores únicos tras fusionar sinónimos ES/EN) y en las 5 familias
usadas originalmente en FLAVOR_KEYWORDS del scraper.
"""

# ─────────────────────────────────────────────────────────────────────────────
# 1. FLAVOR_DESCRIPTOR -> FAMILIA AROMÁTICA
# ─────────────────────────────────────────────────────────────────────────────
FLAVOR_SEMANTIC_MAP: dict = {
        # Frutas rojas y negras
        "Cherry": "fruta_roja_negra", "Blackberry": "fruta_roja_negra", "Plum": "fruta_roja_negra",
        "Strawberry": "fruta_roja_negra", "Raspberry": "fruta_roja_negra", "Cassis": "fruta_roja_negra",
        "Blueberry": "fruta_roja_negra", "Fig": "fruta_roja_negra",

        # Frutas blancas y tropicales
        "Peach": "fruta_blanca_tropical", "Apricot": "fruta_blanca_tropical", "Citrus": "fruta_blanca_tropical",
        "Lemon": "fruta_blanca_tropical", "Orange": "fruta_blanca_tropical", "Apple": "fruta_blanca_tropical",
        "Pear": "fruta_blanca_tropical", "Melon": "fruta_blanca_tropical", "Tropical": "fruta_blanca_tropical",
        "Pineapple": "fruta_blanca_tropical", "Mango": "fruta_blanca_tropical",

        # Madera y especias
        "Oak": "madera_especias", "Vanilla": "madera_especias", "Cedar": "madera_especias",
        "Tobacco": "madera_especias", "Leather": "madera_especias", "Smoke": "madera_especias",
        "Toast": "madera_especias",

        # Confitería y tierra
        "Chocolate": "confiteria_tierra", "Coffee": "confiteria_tierra", "Caramel": "confiteria_tierra",
        "Licorice": "confiteria_tierra", "Anise": "confiteria_tierra", "Spice": "confiteria_tierra",
        "Pepper": "confiteria_tierra", "Clove": "confiteria_tierra", "Cinnamon": "confiteria_tierra",
        "Truffle": "confiteria_tierra", "Mushroom": "confiteria_tierra", "Earthy": "confiteria_tierra",

        # Florales y minerales
        "Herb": "floral_mineral", "Grass": "floral_mineral", "Floral": "floral_mineral",
        "Rose": "floral_mineral", "Violet": "floral_mineral", "Mineral": "floral_mineral",
        "Saline": "floral_mineral", "Slate": "floral_mineral", "Almond": "floral_mineral",
        "Hazelnut": "floral_mineral", "Honey": "floral_mineral", "Dried Fruit": "floral_mineral",
        "Raisin": "floral_mineral",
}

FLAVOR_FAMILIES: list = [
        "fruta_roja_negra", "fruta_blanca_tropical", "madera_especias",
        "confiteria_tierra", "floral_mineral",
]


def map_flavors_to_families(flavor_descriptor: str) -> dict:
        """Convierte un string 'Cherry, Oak, Vanilla' en un dict de conteos por familia,
        ej. {'fruta_roja_negra': 1, 'madera_especias': 2, ...}.
        Términos no reconocidos en FLAVOR_SEMANTIC_MAP se ignoran (no deberían
        aparecer si el dato viene de flavor_descriptor ya limpio)."""
        counts = {fam: 0 for fam in FLAVOR_FAMILIES}
        if not isinstance(flavor_descriptor, str):
                return counts
        for token in flavor_descriptor.split(","):
                family = FLAVOR_SEMANTIC_MAP.get(token.strip())
                if family:
                        counts[family] += 1
        return counts


# ─────────────────────────────────────────────────────────────────────────────
# 2. SERVING_TEMPERATURE -> CATEGORÍA SEMÁNTICA + PUNTO MEDIO NUMÉRICO
# ─────────────────────────────────────────────────────────────────────────────
SERVING_TEMP_SEMANTIC_MAP: dict = {
        "6-8°C":   {"label": "muy_frio",        "midpoint_celsius": 7.0},
        "8-10°C":  {"label": "frio",            "midpoint_celsius": 9.0},
        "10-12°C": {"label": "fresco",          "midpoint_celsius": 11.0},
        "10-14°C": {"label": "fresco",          "midpoint_celsius": 12.0},
        "12-14°C": {"label": "fresco_templado", "midpoint_celsius": 13.0},
        "16-18°C": {"label": "templado",        "midpoint_celsius": 17.0},
}


def map_temperature_to_semantic(service_temperature: str) -> tuple:
        """Devuelve (etiqueta_semantica, punto_medio_en_celsius) para un rango
        de temperatura de servicio. Si el rango no está en el mapa, devuelve
        ('desconocido', None)."""
        entry = SERVING_TEMP_SEMANTIC_MAP.get(service_temperature)
        if entry is None:
                return "desconocido", None
        return entry["label"], entry["midpoint_celsius"]
