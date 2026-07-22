"""
data_enrichment_and_pipeline.py
================================
Sommelier IA — Data Enrichment & Feature Engineering Pipeline
Spanish Wine Quality Dataset (Kaggle, 7,500 rows)

Pipeline stages:
    1. Playwright / Vivino scraping of real tasting notes.
       Wines NOT found on Vivino are DROPPED from the dataset.
    2. Dataset cleaning, variable splitting and renaming.
    3. Business feature engineering.

Final output schema (13 columns):
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
# CONSTANTS & BUSINESS CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

CURRENT_YEAR: int = 2026

# URL de búsqueda de Vivino — fuente de notas de cata reales
VIVINO_SEARCH_URL: str = "https://www.vivino.com/search/wines?q={query}"

# Tiempos de espera para el navegador (ms)
# Vivino es una SPA React que necesita networkidle + tiempo extra para hidratar el DOM
PLAYWRIGHT_NAV_TIMEOUT: int = 30_000  # 30 s máximo por navegación
PLAYWRIGHT_RENDER_WAIT: int = 5_000   # 5 s tras networkidle para que React hidrate los links

# Tipos de recursos bloqueados para acelerar la carga — stylesheet se mantiene
# porque Vivino lo necesita para renderizar correctamente los componentes React
BLOCKED_RESOURCE_TYPES: list = ["image", "media", "font"]

# Léxico de descriptores aromáticos/sabores reconocibles en notas de cata
# Incluye términos en inglés (Vivino global) y español (Vivino es-ES)
FLAVOR_KEYWORDS: list = [
    # Frutas rojas y negras
    "cherry", "blackberry", "plum", "strawberry", "raspberry", "cassis",
    "blueberry", "fig", "cereza", "mora", "ciruela", "fresa", "frambuesa",
    # Frutas blancas y tropicales
    "peach", "apricot", "citrus", "lemon", "orange", "apple", "pear",
    "melon", "tropical", "pineapple", "mango", "melocoton", "albaricoque",
    "manzana", "pera",
    # Notas de madera y especias
    "oak", "vanilla", "cedar", "tobacco", "leather", "smoke", "toast",
    "roble", "vainilla", "tabaco", "cuero", "humo", "tostado",
    # Notas de confitería y tierra
    "chocolate", "coffee", "caramel", "licorice", "anise", "spice",
    "pepper", "clove", "cinnamon", "truffle", "mushroom", "earthy",
    "chocolate", "cafe", "caramelo", "regaliz", "especias", "pimienta",
    "trufa", "tierra",
    # Notas florales y minerales
    "herb", "grass", "floral", "rose", "violet", "mineral", "saline",
    "slate", "almond", "hazelnut", "honey", "dried fruit", "raisin",
    "hierba", "floral", "violeta", "mineral", "pizarra", "almendra",
    "avellana", "miel", "frutos secos",
]

# Palabras clave que indican crianza en barrica → wine_ageing = 1
AGEING_POSITIVE_KEYWORDS: list = [
    "crianza", "reserva", "gran reserva", "roble", "barrica",
    "aged", "oak aged", "barrel", "madera",
]

# Palabras clave que indican vino joven sin crianza → wine_ageing = 0
AGEING_NEGATIVE_KEYWORDS: list = [
    "joven", "cosechero", "nuevo", "young", "sin crianza",
]

# Temperatura de servicio recomendada por tipo de vino (sumillería española)
SERVING_TEMPERATURE: dict = {
    "Tinto":       "16-18°C",
    "Blanco":      "8-10°C",
    "Rosado":      "10-12°C",
    "Espumoso":    "6-8°C",
    "Generoso":    "12-14°C",
    "Desconocido": "10-14°C",
}

# Palabras clave para inferir el tipo de vino desde la columna `type`
# Evaluados en orden de prioridad para evitar ambigüedades
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

# Variedades de uva detectables en la columna `type`
# Ordenadas de más a menos específicas para evitar falsos positivos en el matching
GRAPE_VARIETIES: list = [
    "Cabernet Sauvignon", "Sauvignon Blanc", "Pedro Ximenez",
    "Tempranillo", "Monastrell", "Grenache", "Albarino", "Verdejo",
    "Chardonnay", "Mencia", "Garnacha", "Syrah", "Muscatel", "Muscat",
    "Godello", "Treixadura", "Palomino", "Bobal", "Viura", "Macabeo",
    "Xarel-lo", "Parellada",
]

# Columnas del dataset final de Sommelier IA — esquema de variables objetivo
FINAL_COLUMNS: list = [
    "winery",
    "wine_name",
    "year",
    "rating",
    "region",
    "price_euros",
    "vine_type",
    "grape_variety",
    "wine_ageing",
    "service_temperature",
    "flavor_descriptor",
    "quality_price_ratio",
    "luxury_category",
]


# ─────────────────────────────────────────────────────────────────────────────
# MODULE 1 — PLAYWRIGHT SCRAPING (VIVINO)
# ─────────────────────────────────────────────────────────────────────────────

def scrape_wine_flavors(page: Page, winery: str, wine_name: str) -> list:
    """
    Search Vivino for a wine using a Playwright browser page and extract
    real flavor / aroma descriptors from the rendered wine detail page.

    Parameters
    ----------
    page : playwright.sync_api.Page
        Active Playwright browser page reused across all wines for efficiency.
    winery : str
        Name of the winery / producer.
    wine_name : str
        Name of the wine.

    Returns
    -------
    list of str
        Flavor descriptors found on Vivino, or empty list if wine not found.
    """
    # Navegar al resultado de búsqueda en Vivino y acceder a la ficha del vino
    found = _navigate_to_vivino_wine(page, winery, wine_name)
    if not found:
        return []

    # Extraer descriptores de sabor del DOM ya renderizado por React
    return _extract_flavors_from_page(page)


def _navigate_to_vivino_wine(page: Page, winery: str, wine_name: str) -> bool:
    """
    Search Vivino and navigate to the first wine result's detail page.

    Parameters
    ----------
    page : Page
        Playwright page.
    winery : str
        Producer name.
    wine_name : str
        Wine name.

    Returns
    -------
    bool
        True if a wine detail page was successfully reached, False otherwise.
    """
    search_query = quote(f"{winery} {wine_name}")
    search_url = VIVINO_SEARCH_URL.format(query=search_query)

    try:
        # networkidle garantiza que todas las peticiones XHR de React han terminado
        page.goto(search_url, wait_until="networkidle", timeout=PLAYWRIGHT_NAV_TIMEOUT)
        page.wait_for_timeout(PLAYWRIGHT_RENDER_WAIT)

        # Scroll mínimo para activar el lazy-loading de los resultados de Vivino
        page.evaluate("window.scrollTo(0, 300)")
        page.wait_for_timeout(1000)

        # Vivino usa el patrón /es/wine-slug/w/wine-id para las fichas de vino
        # Este selector es robusto y no depende de clases CSS hasheadas de React
        wine_link = page.query_selector("a[href*='/w/']")

        if wine_link is None:
            return False

        href = wine_link.get_attribute("href") or ""
        if not href:
            return False

        # Construir URL absoluta y navegar a la ficha del vino
        wine_url = href if href.startswith("http") else f"https://www.vivino.com{href}"
        page.goto(wine_url, wait_until="networkidle", timeout=PLAYWRIGHT_NAV_TIMEOUT)
        page.wait_for_timeout(PLAYWRIGHT_RENDER_WAIT)
        return True

    except Exception as exc:
        logger.warning("Error navegando Vivino para '%s - %s': %s", winery, wine_name, exc)
        return False


def _extract_flavors_from_page(page: Page) -> list:
    """
    Extract flavor keywords from the currently rendered Vivino wine page.

    Reads the full post-JavaScript text from the DOM and matches it against
    FLAVOR_KEYWORDS (English + Spanish terms).

    Parameters
    ----------
    page : Page
        Playwright page pointing to a Vivino wine detail URL.

    Returns
    -------
    list of str
        Deduplicated flavor descriptors in Title Case, or empty list on error.
    """
    try:
        # Leer el texto completo renderizado del DOM (React ya ejecutó su JS)
        page_text = page.inner_text("body").lower()
    except Exception:
        return []

    # Filtrar solo las palabras clave que aparecen en el texto de la página
    matched = [kw.title() for kw in FLAVOR_KEYWORDS if kw in page_text]

    # Eliminar duplicados manteniendo el orden de aparición
    return list(dict.fromkeys(matched))


# ─────────────────────────────────────────────────────────────────────────────
# MODULE 2 — CLEANING & TRANSFORMATION
# ─────────────────────────────────────────────────────────────────────────────

def clean_and_transform_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply all cleaning and transformation steps to the raw wine DataFrame.

    Transformations:
        1. Rename columns to the target schema (wine→wine_name, price→price_euros).
        2. Drop columns not in the final schema (num_reviews, country, body, acidity).
        3. Split `type` into `vine_type` (Spanish) and `grape_variety` (multi-value).
        4. Derive `wine_ageing` (0/1) from wine name keywords.
        5. Clean `year` and cast to int (no decimals).

    Parameters
    ----------
    df : pd.DataFrame
        Raw Spanish Wine Quality dataset (wines_SPA.csv).

    Returns
    -------
    pd.DataFrame
        Cleaned dataset aligned to the target schema.
    """
    logger.info("Starting dataset cleaning and transformation...")
    df = df.copy()

    # Renombrar al esquema de variables objetivo
    df = df.rename(columns={"wine": "wine_name", "price": "price_euros"})

    # Eliminar variables que no aportan al modelo
    df = df.drop(columns=["num_reviews", "country", "body", "acidity"], errors="ignore")

    # División de la columna original `type` en dos variables limpias
    df = _split_vine_type_and_grape(df)

    # Derivar si el vino tiene crianza en barrica a partir del nombre
    df = _derive_wine_ageing(df)

    # Limpiar la añada y convertirla a entero sin decimales
    df = _process_year_column(df)

    logger.info("Cleaning complete. Shape: %s", df.shape)
    return df


def _split_vine_type_and_grape(df: pd.DataFrame) -> pd.DataFrame:
    """
    Derive `vine_type` and `grape_variety` from the mixed raw `type` column.

    The original `type` column mixes color, region and grape variety
    (e.g., 'Rioja Red', 'Tempranillo', 'Pedro Ximenez'). This function
    separates those concepts. `type` is dropped after the split.

    Parameters
    ----------
    df : pd.DataFrame
        Dataset with a mixed `type` column.

    Returns
    -------
    pd.DataFrame
        Dataset with `vine_type` and `grape_variety` added; `type` dropped.
    """
    df["vine_type"] = df["type"].fillna("").apply(_extract_vine_type)
    df["grape_variety"] = df["type"].fillna("").apply(_extract_grape_variety)

    # La columna `type` original queda obsoleta tras la división
    df = df.drop(columns=["type"], errors="ignore")

    logger.info("vine_type distribution:\n%s", df["vine_type"].value_counts().to_string())
    return df


def _extract_vine_type(type_str: str) -> str:
    """
    Infer the vine type category from a raw `type` string.

    Returns values in Spanish to match the target schema:
    Tinto, Blanco, Rosado, Espumoso, Generoso, Desconocido.
    Evaluation priority: Generoso > Espumoso > Rosado > Blanco > Tinto.

    Parameters
    ----------
    type_str : str
        Raw value from the `type` column (e.g. 'Rioja Red', 'Albarino').

    Returns
    -------
    str
        Spanish vine type category.
    """
    normalized = type_str.lower().strip()

    # Evaluar en orden de prioridad para evitar solapamientos entre categorías
    for category in ["Generoso", "Espumoso", "Rosado", "Blanco", "Tinto"]:
        if any(kw in normalized for kw in WINE_TYPE_KEYWORDS[category]):
            return category

    return "Desconocido"


def _extract_grape_variety(type_str: str) -> str:
    """
    Identify grape variety / varieties in a raw `type` string.

    Supports multi-varietal blends by joining found varieties with ' / '.
    Returns 'Blend/Other' when no known variety is detected.

    Parameters
    ----------
    type_str : str
        Raw value from the `type` column.

    Returns
    -------
    str
        Grape variety or varieties (e.g., 'Tempranillo', 'Garnacha / Tempranillo'),
        or 'Blend/Other'.
    """
    normalized = type_str.lower().strip()

    # Recopilar todas las variedades detectadas para soporte multivarietal
    found = [grape for grape in GRAPE_VARIETIES if grape.lower() in normalized]

    if not found:
        return "Blend/Other"

    # Separador "/" para que el campo soporte múltiples variedades en un texto
    return " / ".join(found)


def _derive_wine_ageing(df: pd.DataFrame) -> pd.DataFrame:
    """
    Derive `wine_ageing` binary flag (0/1) from wine name keywords.

    A wine is considered aged (1) if its name contains terms associated
    with barrel ageing (Crianza, Reserva, Gran Reserva, Roble, Barrica).
    Defaults to 0 (young wine) when no keyword is found.

    Parameters
    ----------
    df : pd.DataFrame
        Dataset with `wine_name` column.

    Returns
    -------
    pd.DataFrame
        Dataset with new `wine_ageing` column (int 0/1).
    """
    def _is_aged(wine_name: str) -> int:
        text = wine_name.lower()

        # Si contiene indicadores de vino joven, definitivamente no tiene crianza
        if any(neg in text for neg in AGEING_NEGATIVE_KEYWORDS):
            return 0

        # Indicadores de crianza en barrica → sí tiene envejecimiento
        if any(pos in text for pos in AGEING_POSITIVE_KEYWORDS):
            return 1

        # Por defecto se asume vino joven (sin datos de crianza en el nombre)
        return 0

    df["wine_ageing"] = df["wine_name"].fillna("").apply(_is_aged)

    logger.info(
        "wine_ageing (0=Joven, 1=Crianza):\n%s",
        df["wine_ageing"].value_counts().to_string(),
    )
    return df


def _process_year_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the `year` column and cast to integer (no decimals).

    Operations:
        - Replace 'N.V.' (Non-Vintage) with NaN.
        - Coerce remaining values to numeric (malformed entries → NaN).
        - Impute NaN with median (robust to extreme vintage outliers).
        - Cast to int so the final column has no decimal point.

    Parameters
    ----------
    df : pd.DataFrame
        Dataset with a mixed-type `year` column.

    Returns
    -------
    pd.DataFrame
        Dataset with `year` as a clean integer column.
    """
    # "N.V." (Non-Vintage) es una etiqueta de texto que se convierte a NaN
    df["year"] = df["year"].replace("N.V.", np.nan)
    df["year"] = pd.to_numeric(df["year"], errors="coerce")

    year_median = df["year"].median()
    missing = int(df["year"].isna().sum())
    df["year"] = df["year"].fillna(year_median).astype(int)

    logger.info("year: %d NaN imputed with median = %d.", missing, int(year_median))
    return df


# ─────────────────────────────────────────────────────────────────────────────
# MODULE 3 — BUSINESS FEATURE ENGINEERING
# ─────────────────────────────────────────────────────────────────────────────

def engineer_business_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create the three derived business features of the Sommelier IA schema.

    Features:
        - service_temperature : recommended serving range string by vine_type.
        - quality_price_ratio : rating / price_euros rounded to 3 decimal places.
        - luxury_category     : binary 1 if price_euros > 50, else 0.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned dataset with `vine_type`, `rating`, and `price_euros` columns.

    Returns
    -------
    pd.DataFrame
        Dataset with three new feature columns appended.
    """
    logger.info("Engineering business features...")

    # Temperatura de servicio según tipo de vino — dato de valor para la app
    df["service_temperature"] = df["vine_type"].map(SERVING_TEMPERATURE).fillna("10-14°C")

    # Ratio calidad-precio: a mayor valor, mejor relación calidad por euro invertido
    df["quality_price_ratio"] = (df["rating"] / df["price_euros"]).round(3)

    # Segmento de lujo: el umbral de 50€ separa el mercado premium del masivo
    df["luxury_category"] = (df["price_euros"] > 50).astype(int)

    logger.info(
        "luxury_category (0=Standard, 1=Premium):\n%s",
        df["luxury_category"].value_counts().to_string(),
    )
    return df


# ─────────────────────────────────────────────────────────────────────────────
# MODULE 4 — PLAYWRIGHT ENRICHMENT + FILTERING
# ─────────────────────────────────────────────────────────────────────────────

def enrich_and_filter_dataset(
    df: pd.DataFrame,
    request_delay: float = 2.5,
    limit: int = None,
) -> pd.DataFrame:
    """
    Scrape Vivino for each unique (winery, wine_name) pair using Playwright.

    Wines for which Vivino returns no flavor data are DROPPED entirely.
    Only rows with real, scraped tasting notes are kept in the dataset.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned and feature-engineered dataset.
    request_delay : float
        Base seconds between wine searches (randomised ±0.5 s for politeness).
    limit : int, optional
        Cap on unique wines to scrape. None = scrape all (slow for 7,500 rows).
        Use a small number (e.g. 10) for pipeline testing.

    Returns
    -------
    pd.DataFrame
        Filtered dataset with `flavor_descriptor` column. Wines not found on
        Vivino are excluded.
    """
    logger.info("Starting Playwright enrichment via Vivino...")

    # Tabla de pares únicos para no raspar el mismo vino varias veces
    unique_wines = (
        df[["winery", "wine_name"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )

    if limit is not None:
        unique_wines = unique_wines.head(limit)
        logger.info("Limit applied: scraping %d unique wines.", len(unique_wines))

    total = len(unique_wines)
    logger.info("%d unique (winery, wine) pairs to process.", total)

    # Caché en memoria: (winery, wine_name) → flavor string o None
    flavor_cache: dict = {}
    found_count = 0

    with sync_playwright() as playwright:
        # Lanzar Chromium con flags anti-detección para parecer un navegador real
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

        # Bloquear recursos pesados innecesarios para acelerar la carga de páginas
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
                logger.info(
                    "[%d/%d] FOUND   | %s - %s | %s",
                    idx + 1, total,
                    row["winery"], row["wine_name"],
                    flavor_cache[key][:65],
                )
            else:
                # None marca este vino para ser eliminado del dataset final
                flavor_cache[key] = None
                logger.info(
                    "[%d/%d] DROPPED | %s - %s | not found on Vivino",
                    idx + 1, total,
                    row["winery"], row["wine_name"],
                )

            # Delay de cortesía entre peticiones para no sobrecargar Vivino
            time.sleep(max(0.5, request_delay + random.uniform(-0.5, 0.5)))

        browser.close()

    # Mapear los descriptores del caché de vuelta a todas las filas del DataFrame
    df = df.copy()
    df["flavor_descriptor"] = df.apply(
        lambda r: flavor_cache.get((r["winery"], r["wine_name"])), axis=1
    )

    # Eliminar filas cuyo vino no fue encontrado en Vivino — solo datos reales
    initial_rows = len(df)
    df = df[df["flavor_descriptor"].notna()].reset_index(drop=True)
    dropped_rows = initial_rows - len(df)

    logger.info(
        "Result: %d/%d wines found | %d rows kept | %d rows dropped",
        found_count, total, len(df), dropped_rows,
    )
    return df


# ─────────────────────────────────────────────────────────────────────────────
# FINAL COLUMN SELECTION
# ─────────────────────────────────────────────────────────────────────────────

def select_final_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Select and reorder columns to match the Sommelier IA target schema.

    Drops all intermediate columns not defined in FINAL_COLUMNS.

    Parameters
    ----------
    df : pd.DataFrame
        Fully processed dataset.

    Returns
    -------
    pd.DataFrame
        Dataset with exactly the FINAL_COLUMNS in canonical order.
    """
    available = [c for c in FINAL_COLUMNS if c in df.columns]
    missing = [c for c in FINAL_COLUMNS if c not in df.columns]

    if missing:
        logger.warning("Expected columns not found: %s", missing)

    return df[available]


# ─────────────────────────────────────────────────────────────────────────────
# PIPELINE RUNNER
# ─────────────────────────────────────────────────────────────────────────────

def run_pipeline(
    input_path: str,
    output_path: str,
    scrape_limit: int = None,
    request_delay: float = 2.5,
) -> pd.DataFrame:
    """
    Execute the complete Sommelier IA pipeline end to end.

    Stages:
        1. Load raw CSV.
        2. Clean and transform variables to match the target schema.
        3. Engineer business features.
        4. Scrape Vivino with Playwright; drop wines not found.
        5. Select the 13 final columns and save to disk.

    Parameters
    ----------
    input_path : str
        Path to the raw wines_SPA.csv file.
    output_path : str
        Destination path for the enriched output CSV.
    scrape_limit : int, optional
        Max unique (winery, wine) pairs to scrape. None = scrape all.
        Use a small number for development/testing.
    request_delay : float
        Base delay in seconds between Vivino requests.

    Returns
    -------
    pd.DataFrame
        Final enriched, filtered, 13-column dataset.
    """
    logger.info("=" * 60)
    logger.info("SOMMELIER IA - PIPELINE START")
    logger.info("=" * 60)

    # Etapa 1: Carga del dataset bruto
    logger.info("Loading: %s", input_path)
    df = pd.read_csv(input_path)
    logger.info("Raw shape: %s | Columns: %s", df.shape, df.columns.tolist())

    # Etapa 2: Limpieza y transformación de variables
    df = clean_and_transform_dataset(df)

    # Etapa 3: Feature engineering de negocio
    df = engineer_business_features(df)

    # Etapa 4: Scraping real con Playwright + filtrado de vinos no encontrados
    df = enrich_and_filter_dataset(df, request_delay=request_delay, limit=scrape_limit)

    # Etapa 5: Selección de columnas finales y persistencia en disco
    df = select_final_columns(df)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, encoding="utf-8-sig")

    logger.info("Saved: %s | Final shape: %s", output_path, df.shape)
    logger.info("Final columns: %s", df.columns.tolist())
    logger.info("=" * 60)
    logger.info("PIPELINE COMPLETE")
    logger.info("=" * 60)

    return df


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT — TEST RUN
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    RAW_DATA_PATH = "data/raw/dataset/wines_SPA.csv"
    OUTPUT_PATH   = "data/processed/wines_SPA_enriched.csv"

    # scrape_limit=None procesa los 931 vinos unicos del dataset completo
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
