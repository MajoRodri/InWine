"""
predict_pipeline.py
===================
Aplica el pipeline guardado a vinos nuevos: asigna cluster_id, PC1 y PC2.
No re-entrena ningún objeto (usa .transform() y .predict(), nunca .fit()).

Uso / Usage:
    python -m src.predict_pipeline --input data/new_wines.csv [--output resultado.csv]
    python -m src.predict_pipeline --input data/new_wines.csv --append
"""

# argparse permite leer argumentos desde la línea de comandos (--input, --output, etc.)
# argparse allows reading arguments from the command line (--input, --output, etc.)
import argparse
import sys
from pathlib import Path

import joblib        # Para cargar el artefacto guardado en disco / To load the artifact saved on disk
import numpy as np   # Para operaciones matemáticas (log, arrays) / For mathematical operations (log, arrays)
import pandas as pd  # Para manejar tablas de datos / For handling data tables

# Ruta raíz del proyecto (sube un nivel desde src/) / Project root path (one level up from src/)
ROOT = Path(__file__).resolve().parents[1]

# Añade preprocessing/ al path para poder importar mappings.py
# Adds preprocessing/ to the path so we can import mappings.py
sys.path.insert(0, str(ROOT / "preprocessing"))

# Importa las funciones de mapeo que ya existen en preprocessing/mappings.py
# Imports the mapping functions that already exist in preprocessing/mappings.py
# FLAVOR_FAMILIES     → lista de las 5 familias aromáticas / list of the 5 flavor families
# map_flavors_to_families → convierte descriptores de sabor en conteos por familia / converts flavor descriptors into counts per family
# map_temperature_to_semantic → convierte rango de temperatura en punto medio numérico / converts temperature range into numeric midpoint
from mappings import FLAVOR_FAMILIES, map_flavors_to_families, map_temperature_to_semantic  # noqa: E402

# Ruta por defecto al artefacto entrenado / Default path to the trained artifact
DEFAULT_MODEL_PATH = ROOT / "models" / "inwine_pipeline.joblib"

# Ruta al CSV que usa la app en producción / Path to the CSV that the app uses in production
ENRICHED_CSV = ROOT / "data" / "processed" / "wines_SPA_enriched.csv"

# Lista exacta de columnas que loader.py espera encontrar en el CSV del catálogo
# Exact list of columns that loader.py expects to find in the catalog CSV
_CATALOG_COLS = [
    "winery", "wine_name", "year", "rating", "region", "price_euros",
    "vine_type", "grape_variety", "wine_ageing", "service_temperature",
    "quality_price_ratio", "luxury_category", "cluster_id",
]


def _apply_flavor_mapping(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convierte flavor_descriptor en 5 columnas numéricas de familias aromáticas.
    Si la columna no existe, rellena con 0 (el scraper no se ejecutó).

    Converts flavor_descriptor into 5 numeric aroma family columns.
    If the column doesn't exist, fills with 0 (the scraper wasn't run).
    """
    # Si el vino no tiene descriptores de sabor, crea columnas vacías con 0
    # If the wine has no flavor descriptors, creates empty columns with 0
    if "flavor_descriptor" not in df.columns:
        for fam in FLAVOR_FAMILIES:
            df[f"flavor_{fam}"] = 0  # Columna flavor_XXX a 0 para cada familia / flavor_XXX column to 0 for each family
        return df

    # Aplica el mapeo: "Cherry, Oak" → {"fruta_roja_negra": 1, "madera_especias": 1, ...}
    # Applies the mapping: "Cherry, Oak" → {"fruta_roja_negra": 1, "madera_especias": 1, ...}
    family_counts = (
        df["flavor_descriptor"]
        .apply(map_flavors_to_families)  # Convierte cada string en un diccionario de conteos / Converts each string into a counts dictionary
        .apply(pd.Series)                # Expande el diccionario en columnas separadas / Expands the dictionary into separate columns
    )

    # Renombra las columnas añadiendo el prefijo "flavor_"
    # Renames the columns adding the "flavor_" prefix
    family_counts.columns = [f"flavor_{c}" for c in family_counts.columns]

    # Une las nuevas columnas al DataFrame original y devuelve el resultado
    # Joins the new columns to the original DataFrame and returns the result
    # reset_index(drop=True) evita errores de índice al concatenar / avoids index errors when concatenating
    return pd.concat(
        [df.reset_index(drop=True), family_counts.reset_index(drop=True)], axis=1
    )


def _apply_temperature_mapping(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convierte el rango de temperatura de servicio ("16-18°C") en su punto medio numérico (17.0).
    Converts the service temperature range ("16-18°C") into its numeric midpoint (17.0).
    """
    # Aplica el mapeo a cada fila: "16-18°C" → ("templado", 17.0)
    # Applies the mapping to each row: "16-18°C" → ("templado", 17.0)
    mapped = df["service_temperature"].apply(map_temperature_to_semantic)

    # Extrae solo el punto medio numérico (el segundo elemento de la tupla)
    # Extracts only the numeric midpoint (the second element of the tuple)
    df["service_temp_midpoint"] = mapped.apply(lambda t: t[1])

    # Si algún valor es desconocido (None), usa la media del resto como fallback
    # If any value is unknown (None), uses the average of the rest as a fallback
    df["service_temp_midpoint"] = df["service_temp_midpoint"].fillna(
        df["service_temp_midpoint"].mean()
    )
    return df


def _apply_target_encodings(df: pd.DataFrame, encodings: dict) -> pd.DataFrame:
    """
    Sustituye región y variedad de uva por sus estadísticos medios guardados durante el entrenamiento.
    Si la región o uva es desconocida, usa la media global como fallback.

    Replaces region and grape variety with their mean statistics saved during training.
    If the region or grape is unknown, uses the global mean as fallback.
    """
    # Extrae el diccionario de encodings de región del artefacto
    # Extracts the region encodings dictionary from the artifact
    region_enc = encodings["region"]
    region_stats = region_enc["region_stats"]       # Tabla con estadísticos por región / Table with stats per region
    global_price_r = region_enc["global_mean_price"] # Precio medio global (fallback) / Global mean price (fallback)
    global_rating_r = region_enc["global_mean_rating"] # Rating medio global (fallback) / Global mean rating (fallback)

    # Para cada vino, busca el precio medio de su región en la tabla guardada
    # Si la región no existe, usa la media global
    # For each wine, looks up the mean price of its region in the saved table
    # If the region doesn't exist, uses the global mean
    df["region_mean_price"] = df["region"].map(
        lambda r: region_stats.get(r, {}).get("region_mean_price", global_price_r)
    )

    # Mismo proceso para el rating medio de la región
    # Same process for the mean rating of the region
    df["region_mean_rating"] = df["region"].map(
        lambda r: region_stats.get(r, {}).get("region_mean_rating", global_rating_r)
    )

    # Repite el proceso para la variedad de uva
    # Repeats the process for the grape variety
    grape_enc = encodings["grape"]
    grape_stats = grape_enc["grape_variety_stats"]
    global_price_g = grape_enc["global_mean_price"]
    global_rating_g = grape_enc["global_mean_rating"]

    df["grape_variety_mean_price"] = df["grape_variety"].map(
        lambda g: grape_stats.get(g, {}).get("grape_variety_mean_price", global_price_g)
    )
    df["grape_variety_mean_rating"] = df["grape_variety"].map(
        lambda g: grape_stats.get(g, {}).get("grape_variety_mean_rating", global_rating_g)
    )

    return df


def predict_from_artifacts(df_new: pd.DataFrame, artifacts: dict) -> pd.DataFrame:
    """
    Aplica el pipeline guardado a un DataFrame de vinos nuevos.
    Acepta el dict de artefactos directamente (útil para tests y para add_wine.py).
    Devuelve el mismo DataFrame con cluster_id, PC1 y PC2 añadidos.

    Applies the saved pipeline to a DataFrame of new wines.
    Accepts the artifacts dict directly (useful for tests and add_wine.py).
    Returns the same DataFrame with cluster_id, PC1 and PC2 added.
    """
    # Extrae cada objeto del artefacto por su clave / Extracts each object from the artifact by its key
    scaler = artifacts["scaler"]                    # StandardScaler ya entrenado / Already trained StandardScaler
    encodings = artifacts["target_encodings"]       # Diccionarios de Target Encoding / Target Encoding dictionaries
    kmeans = artifacts["kmeans"]                    # Modelo K-Means ya entrenado / Already trained K-Means model
    pca = artifacts["pca"]                          # Modelo PCA ya entrenado / Already trained PCA model
    feature_columns = artifacts["feature_columns"]  # Nombres de columnas en el orden exacto del entrenamiento
                                                    # Column names in the exact order used during training

    # Trabaja sobre una copia para no modificar el DataFrame original
    # Works on a copy to avoid modifying the original DataFrame
    df = df_new.copy()

    # PASO 1 / STEP 1:
    # Transformación logarítmica del precio: reduce el efecto de precios extremos
    # Log transformation of price: reduces the effect of extreme prices
    # log1p(x) = log(x + 1), funciona también si precio = 0
    df["price_log"] = np.log1p(df["price_euros"])

    # PASO 2 / STEP 2:
    # Convierte descriptores de sabor en 5 variables numéricas (familias aromáticas)
    # Converts flavor descriptors into 5 numeric variables (aroma families)
    df = _apply_flavor_mapping(df)

    # PASO 3 / STEP 3:
    # Convierte el rango de temperatura en un número (su punto medio)
    # Converts the temperature range into a number (its midpoint)
    df = _apply_temperature_mapping(df)

    # PASO 4 / STEP 4:
    # Sustituye región y uva por sus estadísticos guardados (sin re-entrenar)
    # Replaces region and grape with their saved statistics (without retraining)
    df = _apply_target_encodings(df, encodings)

    # PASO 5 / STEP 5:
    # Recupera los nombres de columnas sin escalar a partir de los nombres escalados
    # e.g. "price_log_scaled" → "price_log"
    # Recovers the unscaled column names from the scaled column names
    unscaled_cols = [col[: -len("_scaled")] for col in feature_columns]

    # PASO 6 / STEP 6:
    # Escala los datos usando el scaler ya entrenado
    # CRÍTICO: .transform() aplica la fórmula aprendida, .fit() la re-aprendería desde cero
    # Scales the data using the already trained scaler
    # CRITICAL: .transform() applies the learned formula, .fit() would re-learn it from scratch
    X = scaler.transform(df[unscaled_cols])

    # PASO 7 / STEP 7:
    # KMeans.predict() asigna cada vino al cluster más cercano sin mover los centroides
    # KMeans.predict() assigns each wine to the nearest cluster without moving the centroids
    df["cluster_id"] = kmeans.predict(X)

    # PCA.transform() proyecta los datos en 2D usando los ejes aprendidos
    # PCA.transform() projects the data into 2D using the learned axes
    pca_coords = pca.transform(X)
    df["PC1"] = pca_coords[:, 0]  # Primera componente principal / First principal component
    df["PC2"] = pca_coords[:, 1]  # Segunda componente principal / Second principal component

    return df


def predict(df_new: pd.DataFrame, model_path: Path = DEFAULT_MODEL_PATH) -> pd.DataFrame:
    """
    Versión pública: carga el artefacto desde disco y aplica el pipeline.
    Public version: loads the artifact from disk and applies the pipeline.
    """
    # Lee el archivo .joblib y reconstruye el diccionario de objetos en memoria
    # Reads the .joblib file and reconstructs the objects dictionary in memory
    artifacts = joblib.load(model_path)
    return predict_from_artifacts(df_new, artifacts)


def append_to_catalog(df_result: pd.DataFrame, csv_path: Path = ENRICHED_CSV) -> int:
    """
    Añade los vinos procesados al catálogo CSV que usa la app.
    Solo escribe las columnas que loader.py espera; descarta el resto (PC1, price_log, etc.).
    Devuelve el número de filas añadidas.

    Adds the processed wines to the catalog CSV that the app uses.
    Only writes the columns that loader.py expects; discards the rest (PC1, price_log, etc.).
    Returns the number of rows added.
    """
    # Filtra solo las columnas que el loader necesita (descarta columnas internas del pipeline)
    # Filters only the columns that the loader needs (discards internal pipeline columns)
    cols = [c for c in _CATALOG_COLS if c in df_result.columns]
    df_to_append = df_result[cols]

    # Si el CSV no existe todavía, escribe también la cabecera (nombres de columnas)
    # If the CSV doesn't exist yet, also writes the header (column names)
    write_header = not csv_path.exists()

    # mode="a" significa "append": añade al final sin borrar lo que ya hay
    # mode="a" means "append": adds to the end without deleting what's already there
    df_to_append.to_csv(
        csv_path,
        mode="a",          # Añadir al final / Append to end
        index=False,       # No escribir el índice numérico de pandas / Don't write the pandas numeric index
        header=write_header,  # Solo escribe cabecera si el archivo es nuevo / Only write header if file is new
        encoding="utf-8-sig",  # UTF-8 con BOM, compatible con Excel / UTF-8 with BOM, Excel compatible
    )
    n = len(df_to_append)
    print(f"{n} vino(s) añadido(s) a {csv_path}")
    print("Reinicia la app para que cargue el catálogo actualizado.")
    return n


def main() -> None:
    """
    Punto de entrada cuando se ejecuta desde la línea de comandos.
    Entry point when run from the command line.
    """
    # Configura los argumentos que acepta el script por línea de comandos
    # Configures the arguments the script accepts from the command line
    parser = argparse.ArgumentParser(
        description="Asigna cluster_id, PC1 y PC2 a vinos nuevos usando el pipeline guardado."
    )
    parser.add_argument("--input", required=True, help="CSV con los vinos nuevos")  # Obligatorio / Required
    parser.add_argument("--output", default=None, help="Ruta de salida (opcional)")
    parser.add_argument(
        "--append",
        action="store_true",  # Si está presente es True, si no está es False / If present it's True, if absent it's False
        help="Añade los vinos procesados al catálogo de la app (wines_SPA_enriched.csv)",
    )
    parser.add_argument(
        "--model",
        default=str(DEFAULT_MODEL_PATH),
        help="Ruta al artefacto .joblib",
    )

    # Lee los argumentos que el usuario pasó al ejecutar el script
    # Reads the arguments the user passed when running the script
    args = parser.parse_args()

    # Carga el CSV de vinos nuevos / Loads the new wines CSV
    df_new = pd.read_csv(args.input)
    print(f"Vinos nuevos cargados: {df_new.shape}")

    # Aplica el pipeline completo / Applies the full pipeline
    df_out = predict(df_new, Path(args.model))

    # Decide qué hacer con el resultado según los flags pasados
    # Decides what to do with the result based on the passed flags
    if args.append:
        # Añade al catálogo de la app / Adds to the app's catalog
        append_to_catalog(df_out)
    elif args.output:
        # Guarda en un archivo nuevo / Saves to a new file
        df_out.to_csv(args.output, index=False, encoding="utf-8-sig")
        print(f"Resultado guardado en: {args.output}")
    else:
        # Sin flags: imprime por pantalla un resumen / No flags: prints a summary to screen
        cols = ["wine_name", "cluster_id", "PC1", "PC2"]
        cols = [c for c in cols if c in df_out.columns]
        print(df_out[cols].to_string(index=False))


# Solo ejecuta main() si este archivo se llama directamente
# Only runs main() if this file is called directly
if __name__ == "__main__":
    main()
