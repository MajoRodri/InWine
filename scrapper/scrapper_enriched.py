"""
Sommelier IA — Pipeline de enriquecimiento de datos / Data Enrichment Pipeline
Dataset: Spanish Wine Quality (Kaggle, 7 500 filas / rows)

Etapas / Stages:
  1. Scraping de notas de cata reales desde Vivino con Playwright.
     Real tasting notes scraped from Vivino via Playwright.
     Vinos no encontrados son eliminados / Wines not found are dropped.
  2. Limpieza y transformación del dataset / Dataset cleaning & transformation.
  3. Feature engineering de negocio / Business feature engineering.

Esquema final (13 columnas / columns):
  winery, wine_name, year, rating, region, price_euros,
  vine_type, grape_variety, wine_ageing, service_temperature,
  flavor_descriptor, quality_price_ratio, luxury_category
"""

import time
import random
import logging
import warnings
from pathlib import Path
from urllib.parse import quote

import numpy as np
import pandas as pd
from playwright.sync_api import sync_playwright, Page

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────────────────────────
# LOGGING
# ─────────────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("sommelier_ia")


# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTES / CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────

CURRENT_YEAR: int = 2026

# Fuente de notas de cata / Source of tasting notes
VIVINO_SEARCH_URL: str = "https://www.vivino.com/search/wines?q={query}"

# Tiempos de espera (ms) — Vivino es una SPA React / Timeouts (ms) — Vivino is a React SPA
PLAYWRIGHT_NAV_TIMEOUT: int = 30_000  # 30 s por navegación / per navigation
PLAYWRIGHT_RENDER_WAIT: int = 5_000   # 5 s para que React hidrate el DOM / for React hydration

# Recursos bloqueados para acelerar la carga / Blocked resources to speed up loading
# Se mantiene stylesheet porque Vivino lo necesita para renderizar / Stylesheet kept: Vivino needs it
BLOCKED_RESOURCE_TYPES: list = ["image", "media", "font"]

# Descriptores de sabor en EN + ES para matchear notas de cata de Vivino
# Flavor descriptors in EN + ES to match Vivino tasting notes
FLAVOR_KEYWORDS: list = [
    # Frutas rojas y negras / Red & dark fruits
    "cherry", "blackberry", "plum", "strawberry", "raspberry", "cassis",
    "blueberry", "fig", "cereza", "mora", "ciruela", "fresa", "frambuesa",
    # Frutas blancas y tropicales / White & tropical fruits
    "peach", "apricot", "citrus", "lemon", "orange", "apple", "pear",
    "melon", "tropical", "pineapple", "mango", "melocoton", "albaricoque",
    "manzana", "pera",
    # Madera y especias / Wood & spices
    "oak", "vanilla", "cedar", "tobacco", "leather", "smoke", "toast",
    "roble", "vainilla", "tabaco", "cuero", "humo", "tostado",
    # Confitería y tierra / Confectionery & earthy
    "chocolate", "coffee", "caramel", "licorice", "anise", "spice",
    "pepper", "clove", "cinnamon", "truffle", "mushroom", "earthy",
    "chocolate", "cafe", "caramelo", "regaliz", "especias", "pimienta",
    "trufa", "tierra",
    # Florales y minerales / Floral & mineral
    "herb", "grass", "floral", "rose", "violet", "mineral", "saline",
    "slate", "almond", "hazelnut", "honey", "dried fruit", "raisin",
    "hierba", "floral", "violeta", "mineral", "pizarra", "almendra",
    "avellana", "miel", "frutos secos",
]

# Crianza en barrica → wine_ageing = 1 / Barrel-aged wines → wine_ageing = 1
AGEING_POSITIVE_KEYWORDS: list = [
    "crianza", "reserva", "gran reserva", "roble", "barrica",
    "aged", "oak aged", "barrel", "madera",
]

# Vino joven → wine_ageing = 0 / Young wine → wine_ageing = 0
AGEING_NEGATIVE_KEYWORDS: list = [
    "joven", "cosechero", "nuevo", "young", "sin crianza",
]

# Temperatura de servicio por tipo / Serving temperature by wine type
SERVING_TEMPERATURE: dict = {
    "Tinto":       "16-18°C",
    "Blanco":      "8-10°C",
    "Rosado":      "10-12°C",
    "Espumoso":    "6-8°C",
    "Generoso":    "12-14°C",
    "Desconocido": "10-14°C",
}

# Palabras clave para clasificar el tipo de vino desde `type`
# Keywords to classify wine type from the `type` column
# Orden de prioridad / Priority order: Generoso > Espumoso > Rosado > Blanco > Tinto
WINE_TYPE_KEYWORDS: dict = {
    "Generoso": [
        "sherry", "pedro ximenez", "moscatel", "muscat", "muscatel",
        "amontillado", "oloroso", "manzanilla", "palo cortado", "cream",
        "dulce", "sweet",
    ],
    "Espumoso": ["sparkling", "cava", "espumoso", "frizzante"],
    "Rosado":   ["rose", "rosado", "rosé"],
    "Blanco": [
        "white", "blanco", "albarino", "verdejo", "chardonnay",
        "sauvignon blanc", "viura", "godello", "treixadura", "palomino",
        "ribeiro", "rias baixas",
    ],
    "Tinto": ["red", "tinto", "rouge"],
}

# Variedades de más a menos específicas para evitar falsos positivos
# Varieties ordered most-to-least specific to avoid false positives
GRAPE_VARIETIES: list = [
    "Cabernet Sauvignon", "Sauvignon Blanc", "Pedro Ximenez",
    "Tempranillo", "Monastrell", "Grenache", "Albarino", "Verdejo",
    "Chardonnay", "Mencia", "Garnacha", "Syrah", "Muscatel", "Muscat",
    "Godello", "Treixadura", "Palomino", "Bobal", "Viura", "Macabeo",
    "Xarel-lo", "Parellada",
]

# Esquema de columnas del dataset final / Final dataset column schema
FINAL_COLUMNS: list = [
    "winery", "wine_name", "year", "rating", "region", "price_euros",
    "vine_type", "grape_variety", "wine_ageing", "service_temperature",
    "flavor_descriptor", "quality_price_ratio", "luxury_category",
]


# ─────────────────────────────────────────────────────────────────────────────
# MÓDULO 1 — SCRAPING CON PLAYWRIGHT / MODULE 1 — PLAYWRIGHT SCRAPING
# ─────────────────────────────────────────────────────────────────────────────

def scrape_wine_flavors(page: Page, winery: str, wine_name: str) -> list:
    """Busca el vino en Vivino y devuelve sus descriptores de sabor.
    Searches Vivino for the wine and returns its flavor descriptors."""
    found = _navigate_to_vivino_wine(page, winery, wine_name)
    if not found:
        return []
    return _extract_flavors_from_page(page)


def _navigate_to_vivino_wine(page: Page, winery: str, wine_name: str) -> bool:
    """Navega a la ficha del vino en Vivino. Devuelve True si tiene éxito.
    Navigates to the wine detail page on Vivino. Returns True on success."""
    search_query = quote(f"{winery} {wine_name}")
    search_url = VIVINO_SEARCH_URL.format(query=search_query)

    try:
        # networkidle asegura que React terminó todas sus peticiones XHR
        # networkidle ensures React finished all XHR requests
        page.goto(search_url, wait_until="networkidle", timeout=PLAYWRIGHT_NAV_TIMEOUT)
        page.wait_for_timeout(PLAYWRIGHT_RENDER_WAIT)

        # Scroll mínimo para activar lazy-loading / Minimal scroll to trigger lazy-loading
        page.evaluate("window.scrollTo(0, 300)")
        page.wait_for_timeout(1000)

        # Selector robusto: patrón /w/ identifica fichas de vino en Vivino
        # Robust selector: /w/ pattern identifies wine detail pages on Vivino
        wine_link = page.query_selector("a[href*='/w/']")
        if wine_link is None:
            return False

        href = wine_link.get_attribute("href") or ""
        if not href:
            return False

        # Construir URL absoluta / Build absolute URL
        wine_url = href if href.startswith("http") else f"https://www.vivino.com{href}"
        page.goto(wine_url, wait_until="networkidle", timeout=PLAYWRIGHT_NAV_TIMEOUT)
        page.wait_for_timeout(PLAYWRIGHT_RENDER_WAIT)
        return True

    except Exception as exc:
        logger.warning("Error navegando Vivino para '%s - %s': %s", winery, wine_name, exc)
        return False


def _extract_flavors_from_page(page: Page) -> list:
    """Extrae descriptores de sabor del DOM renderizado de Vivino.
    Extracts flavor descriptors from Vivino's rendered DOM."""
    try:
        # Texto completo post-JS (React ya ejecutó su renderizado)
        # Full post-JS text (React has already rendered)
        page_text = page.inner_text("body").lower()
    except Exception:
        return []

    matched = [kw.title() for kw in FLAVOR_KEYWORDS if kw in page_text]
    return list(dict.fromkeys(matched))  # Deduplicar manteniendo orden / Deduplicate keeping order


# ─────────────────────────────────────────────────────────────────────────────
# MÓDULO 2 — LIMPIEZA Y TRANSFORMACIÓN / MODULE 2 — CLEANING & TRANSFORMATION
# ─────────────────────────────────────────────────────────────────────────────

def clean_and_transform_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Limpia y transforma el dataset bruto al esquema objetivo.
    Cleans and transforms the raw dataset to the target schema."""
    logger.info("Starting dataset cleaning and transformation...")
    df = df.copy()

    # Renombrar al esquema objetivo / Rename to target schema
    df = df.rename(columns={"wine": "wine_name", "price": "price_euros"})

    # Eliminar columnas irrelevantes / Drop irrelevant columns
    df = df.drop(columns=["num_reviews", "country", "body", "acidity"], errors="ignore")

    df = _split_vine_type_and_grape(df)
    df = _derive_wine_ageing(df)
    df = _process_year_column(df)

    logger.info("Cleaning complete. Shape: %s", df.shape)
    return df


def _split_vine_type_and_grape(df: pd.DataFrame) -> pd.DataFrame:
    """Separa `type` (mezcla de color, región y variedad) en vine_type y grape_variety.
    Splits the mixed `type` column into vine_type and grape_variety."""
    df["vine_type"] = df["type"].fillna("").apply(_extract_vine_type)
    df["grape_variety"] = df["type"].fillna("").apply(_extract_grape_variety)
    df = df.drop(columns=["type"], errors="ignore")  # Ya no es necesaria / No longer needed

    logger.info("vine_type distribution:\n%s", df["vine_type"].value_counts().to_string())
    return df


def _extract_vine_type(type_str: str) -> str:
    """Infiere el tipo de vino en español desde la columna `type`.
    Infers the Spanish wine type from the raw `type` column."""
    normalized = type_str.lower().strip()

    # Evaluar por prioridad para evitar solapamientos / Evaluate in priority order to avoid overlaps
    for category in ["Generoso", "Espumoso", "Rosado", "Blanco", "Tinto"]:
        if any(kw in normalized for kw in WINE_TYPE_KEYWORDS[category]):
            return category

    return "Desconocido"


def _extract_grape_variety(type_str: str) -> str:
    """Detecta variedades de uva en `type`. Soporta blends separados con ' / '.
    Detects grape varieties from `type`. Supports blends joined with ' / '."""
    normalized = type_str.lower().strip()
    found = [grape for grape in GRAPE_VARIETIES if grape.lower() in normalized]
    return " / ".join(found) if found else "Blend/Other"


def _derive_wine_ageing(df: pd.DataFrame) -> pd.DataFrame:
    """Crea `wine_ageing` (0/1) basándose en palabras clave del nombre del vino.
    Creates `wine_ageing` (0/1) based on wine name keywords."""
    def _is_aged(wine_name: str) -> int:
        text = wine_name.lower()
        if any(neg in text for neg in AGEING_NEGATIVE_KEYWORDS):
            return 0  # Explícitamente joven / Explicitly young
        if any(pos in text for pos in AGEING_POSITIVE_KEYWORDS):
            return 1  # Crianza en barrica confirmada / Barrel ageing confirmed
        return 0      # Sin información → asume joven / No info → assume young

    df["wine_ageing"] = df["wine_name"].fillna("").apply(_is_aged)
    logger.info("wine_ageing (0=Joven, 1=Crianza):\n%s", df["wine_ageing"].value_counts().to_string())
    return df


def _process_year_column(df: pd.DataFrame) -> pd.DataFrame:
    """Limpia `year`: convierte N.V. a NaN, imputa con mediana y castea a int.
    Cleans `year`: converts N.V. to NaN, imputes with median, casts to int."""
    df["year"] = df["year"].replace("N.V.", np.nan)  # Non-Vintage → NaN
    df["year"] = pd.to_numeric(df["year"], errors="coerce")

    year_median = df["year"].median()
    missing = int(df["year"].isna().sum())
    df["year"] = df["year"].fillna(year_median).astype(int)

    logger.info("year: %d NaN imputed with median = %d.", missing, int(year_median))
    return df


# ─────────────────────────────────────────────────────────────────────────────
# MÓDULO 3 — FEATURES DE NEGOCIO / MODULE 3 — BUSINESS FEATURES
# ─────────────────────────────────────────────────────────────────────────────

def engineer_business_features(df: pd.DataFrame) -> pd.DataFrame:
    """Crea las 3 features de negocio: temperatura, ratio calidad-precio y categoría de lujo.
    Creates the 3 business features: temperature, quality-price ratio, and luxury category."""
    logger.info("Engineering business features...")

    # Temperatura recomendada según tipo / Recommended temperature by vine type
    df["service_temperature"] = df["vine_type"].map(SERVING_TEMPERATURE).fillna("10-14°C")

    # Relación calidad-precio: rating / precio / Quality-price ratio: rating / price
    df["quality_price_ratio"] = (df["rating"] / df["price_euros"]).round(3)

    # Lujo: >50€ = premium / Luxury: >50€ = premium
    df["luxury_category"] = (df["price_euros"] > 50).astype(int)

    logger.info("luxury_category (0=Standard, 1=Premium):\n%s", df["luxury_category"].value_counts().to_string())
    return df


# ─────────────────────────────────────────────────────────────────────────────
# MÓDULO 4 — ENRIQUECIMIENTO Y FILTRADO / MODULE 4 — ENRICHMENT & FILTERING
# ─────────────────────────────────────────────────────────────────────────────

def enrich_and_filter_dataset(
    df: pd.DataFrame,
    request_delay: float = 2.5,
    limit: int = None,
) -> pd.DataFrame:
    """Raspa Vivino por cada (winery, wine_name) único. Elimina los no encontrados.
    Scrapes Vivino for each unique (winery, wine_name). Drops wines not found."""
    logger.info("Starting Playwright enrichment via Vivino...")

    # Pares únicos para no raspar el mismo vino dos veces / Unique pairs to avoid duplicate scraping
    unique_wines = df[["winery", "wine_name"]].drop_duplicates().reset_index(drop=True)

    if limit is not None:
        unique_wines = unique_wines.head(limit)
        logger.info("Limit applied: scraping %d unique wines.", len(unique_wines))

    total = len(unique_wines)
    logger.info("%d unique (winery, wine) pairs to process.", total)

    # Caché en memoria: clave → descriptores o None / In-memory cache: key → descriptors or None
    flavor_cache: dict = {}
    found_count = 0

    with sync_playwright() as playwright:
        # Flags anti-detección para parecer un navegador real / Anti-detection flags to mimic real browser
        browser = playwright.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-extensions",
            ],
        )
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            locale="es-ES",
            viewport={"width": 1920, "height": 1080},
            java_script_enabled=True,
        )
        page = context.new_page()

        # Bloquear recursos pesados para acelerar la carga / Block heavy resources to speed up loading
        def _block_heavy_resources(route, request):
            if request.resource_type in BLOCKED_RESOURCE_TYPES:
                route.abort()
            else:
                route.continue_()

        page.route("**/*", _block_heavy_resources)

        for idx, row in unique_wines.iterrows():
            key = (row["winery"], row["wine_name"])
            flavors = scrape_wine_flavors(page, row["winery"], row["wine_name"])

            if flavors:
                flavor_cache[key] = ", ".join(flavors)
                found_count += 1
                logger.info("[%d/%d] FOUND   | %s - %s | %s", idx + 1, total, row["winery"], row["wine_name"], flavor_cache[key][:65])
            else:
                flavor_cache[key] = None  # None → será eliminado del dataset / will be dropped
                logger.info("[%d/%d] DROPPED | %s - %s | not found on Vivino", idx + 1, total, row["winery"], row["wine_name"])

            # Delay aleatorio de cortesía / Randomized politeness delay
            time.sleep(max(0.5, request_delay + random.uniform(-0.5, 0.5)))

        browser.close()

    # Mapear descriptores de vuelta al DataFrame completo / Map descriptors back to full DataFrame
    df = df.copy()
    df["flavor_descriptor"] = df.apply(lambda r: flavor_cache.get((r["winery"], r["wine_name"])), axis=1)

    # Eliminar filas sin datos reales de Vivino / Drop rows without real Vivino data
    initial_rows = len(df)
    df = df[df["flavor_descriptor"].notna()].reset_index(drop=True)

    logger.info("Result: %d/%d wines found | %d rows kept | %d rows dropped", found_count, total, len(df), initial_rows - len(df))
    return df


# ─────────────────────────────────────────────────────────────────────────────
# SELECCIÓN DE COLUMNAS FINALES / FINAL COLUMN SELECTION
# ─────────────────────────────────────────────────────────────────────────────

def select_final_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Selecciona y reordena columnas al esquema objetivo de 13 variables.
    Selects and reorders columns to the 13-variable target schema."""
    available = [c for c in FINAL_COLUMNS if c in df.columns]
    missing = [c for c in FINAL_COLUMNS if c not in df.columns]

    if missing:
        logger.warning("Expected columns not found: %s", missing)

    return df[available]


# ─────────────────────────────────────────────────────────────────────────────
# PIPELINE PRINCIPAL / MAIN PIPELINE RUNNER
# ─────────────────────────────────────────────────────────────────────────────

def run_pipeline(
    input_path: str,
    output_path: str,
    scrape_limit: int = None,
    request_delay: float = 2.5,
) -> pd.DataFrame:
    """Ejecuta el pipeline completo de extremo a extremo.
    Executes the complete end-to-end pipeline."""
    logger.info("=" * 60)
    logger.info("SOMMELIER IA - PIPELINE START")
    logger.info("=" * 60)

    # Etapa 1: Carga / Stage 1: Load
    logger.info("Loading: %s", input_path)
    df = pd.read_csv(input_path)
    logger.info("Raw shape: %s | Columns: %s", df.shape, df.columns.tolist())

    # Etapa 2: Limpieza / Stage 2: Clean
    df = clean_and_transform_dataset(df)

    # Etapa 3: Features de negocio / Stage 3: Business features
    df = engineer_business_features(df)

    # Etapa 4: Scraping + filtrado / Stage 4: Scraping + filtering
    df = enrich_and_filter_dataset(df, request_delay=request_delay, limit=scrape_limit)

    # Etapa 5: Guardar resultado / Stage 5: Save output
    df = select_final_columns(df)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, encoding="utf-8-sig")

    logger.info("Saved: %s | Final shape: %s", output_path, df.shape)
    logger.info("=" * 60)
    logger.info("PIPELINE COMPLETE")
    logger.info("=" * 60)

    return df


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    RAW_DATA_PATH = "data/raw/dataset/wines_SPA.csv"
    OUTPUT_PATH   = "data/processed/wines_SPA_enriched.csv"

    # scrape_limit=None procesa los ~931 vinos únicos / processes all ~931 unique wines
    enriched_df = run_pipeline(
        input_path=RAW_DATA_PATH,
        output_path=OUTPUT_PATH,
        scrape_limit=None,
        request_delay=2.5,
    )

    print("\n" + "=" * 60)
    print("SOMMELIER IA - DATASET SUMMARY")
    print("=" * 60)
    print(f"Final shape    : {enriched_df.shape}")
    print(f"Final columns  : {enriched_df.columns.tolist()}")
    print(f"\nData types:\n{enriched_df.dtypes.to_string()}")
    print(f"\nSample (5 rows):")
    print(enriched_df.head(5).to_string(index=False))
    print("=" * 60)
