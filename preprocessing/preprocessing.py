"""
preprocessing.py
================
Preprocesamiento final para el motor de recomendación de Sommelier IA.

Entrada:  wines_SPA_enriched_FINAL.csv (1918 filas, validado: 0 nulos,
          0 duplicados, 0 inconsistencias vine_type/grape_variety).
Salida:   DataFrame escalado y codificado, listo para vectorizar/entrenar.

Decisiones de codificación (justificadas):
-------------------------------------------
- vine_type (5 categorías: Tinto, Blanco, Rosado, Espumoso, Generoso) ->
  ONE-HOT ENCODING. Cardinalidad baja y sin relación de orden entre
  categorías (un "Blanco" no es "más" ni "menos" que un "Tinto"), así que
  Target Encoding aportaría poco y One-Hot es interpretable y barato en
  columnas (5 dummies).

- wine_ageing -> YA ESTÁ CODIFICADA. Es un flag binario (0=Joven,
  1=Crianza) desde el propio pipeline de limpieza; no necesita
  transformación adicional, se usa tal cual como feature numérica binaria.

- region (69 categorías, muy desigual: desde 507 vinos en Ribera del Duero
  hasta regiones con 1-2 vinos) -> TARGET ENCODING (no One-Hot). Un
  One-Hot de 69 columnas sería muy disperso (la mayoría 0) y añadiría
  dimensionalidad sin aportar señal para las regiones con pocos vinos.
  Como este no es un problema supervisado clásico (no hay una sola
  variable objetivo a predecir), se codifica la región por sus
  estadísticos agregados relevantes para el recomendador: precio medio y
  rating medio de esa región (region_mean_price, region_mean_rating),
  con SUAVIZADO (smoothing) hacia la media global para regiones con pocos
  vinos, evitando que una región de 1-2 vinos tenga una media extrema y
  poco fiable. Riesgo a vigilar: con datos nuevos (una región no vista en
  entrenamiento) hay que usar la media global como fallback, ya
  implementado abajo.

Variables numéricas escaladas con StandardScaler (media 0, desviación 1):
  price_euros, rating, quality_price_ratio, year, region_mean_price,
  region_mean_rating.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

from mappings import map_flavors_to_families, map_temperature_to_semantic, FLAVOR_FAMILIES


INPUT_PATH = "wines_SPA_enriched_FINAL.csv"
OUTPUT_PATH = "wines_SPA_model_ready.csv"

TARGET_ENCODING_SMOOTHING = 10  # nº de vinos "virtuales" que se asume tiene la media global


def validate_dataset(df: pd.DataFrame) -> None:
    """Repite las validaciones de limpieza; lanza AssertionError si algo falla."""
    assert df.isna().sum().sum() == 0, "Hay nulos residuales"
    assert df.duplicated().sum() == 0, "Hay filas duplicadas residuales"
    assert df["price_euros"].min() > 0, "Hay precios <= 0"
    assert df["rating"].between(1, 5).all(), "Hay ratings fuera de rango [1,5]"
    red = {"Tempranillo","Monastrell","Grenache","Grenache / Carinena","Mencia","Bobal","Syrah","Cabernet Sauvignon"}
    white = {"Albarino","Verdejo","Chardonnay","Godello","Treixadura","Palomino","Viura","Macabeo","Xarel-lo","Parellada","Sauvignon Blanc"}
    inconsist = df[((df["vine_type"] == "Blanco") & (df["grape_variety"].isin(red))) |
                   ((df["vine_type"] == "Tinto") & (df["grape_variety"].isin(white)))]
    assert len(inconsist) == 0, f"vine_type/grape_variety inconsistentes en {len(inconsist)} filas"
    print("Validación OK: sin nulos, sin duplicados, sin inconsistencias.")


def target_encode_region(df: pd.DataFrame) -> pd.DataFrame:
    """Target Encoding con suavizado para `region` sobre price_euros y rating.
    Guarda las medias por región en un dict para poder aplicarlas a datos
    nuevos (fallback a la media global si la región no se vio antes)."""
    global_mean_price = df["price_euros"].mean()
    global_mean_rating = df["rating"].mean()

    stats = df.groupby("region").agg(
        n=("price_euros", "size"),
        mean_price=("price_euros", "mean"),
        mean_rating=("rating", "mean"),
    )
    # Suavizado: cuantos menos vinos tenga la región, más se acerca a la media global
    k = TARGET_ENCODING_SMOOTHING
    stats["region_mean_price"] = (stats["mean_price"] * stats["n"] + global_mean_price * k) / (stats["n"] + k)
    stats["region_mean_rating"] = (stats["mean_rating"] * stats["n"] + global_mean_rating * k) / (stats["n"] + k)

    df = df.merge(stats[["region_mean_price", "region_mean_rating"]], on="region", how="left")
    # Fallback por si apareciera una región nueva en datos futuros
    df["region_mean_price"] = df["region_mean_price"].fillna(global_mean_price)
    df["region_mean_rating"] = df["region_mean_rating"].fillna(global_mean_rating)
    return df, {"global_mean_price": global_mean_price, "global_mean_rating": global_mean_rating,
                "region_stats": stats[["region_mean_price", "region_mean_rating"]].to_dict("index")}


def apply_flavor_mapping(df: pd.DataFrame) -> pd.DataFrame:
    """Convierte flavor_descriptor (texto libre) en 5 columnas numéricas,
    una por familia aromática (conteo de descriptores de esa familia)."""
    family_counts = df["flavor_descriptor"].apply(map_flavors_to_families).apply(pd.Series)
    family_counts.columns = [f"flavor_{c}" for c in family_counts.columns]
    return pd.concat([df, family_counts], axis=1)


def apply_temperature_mapping(df: pd.DataFrame) -> pd.DataFrame:
    """Convierte service_temperature en una etiqueta semántica + su punto medio numérico."""
    mapped = df["service_temperature"].apply(map_temperature_to_semantic)
    df["service_temp_label"] = mapped.apply(lambda t: t[0])
    df["service_temp_midpoint"] = mapped.apply(lambda t: t[1])
    return df


def preprocess(df: pd.DataFrame) -> tuple:
    """Pipeline completo de preprocesamiento. Devuelve (df_procesado, scaler, region_encoding_dict)."""
    validate_dataset(df)
    df = df.copy()

    # 1. Mapeos semánticos
    df = apply_flavor_mapping(df)
    df = apply_temperature_mapping(df)

    # 2. Target Encoding de region (con suavizado)
    df, region_encoding = target_encode_region(df)

    # 3. One-Hot Encoding de vine_type
    df = pd.get_dummies(df, columns=["vine_type"], prefix="vine_type", dtype=int)

    # 4. Escalado de variables numéricas continuas
    numeric_cols = [
        "price_euros", "rating", "quality_price_ratio", "year",
        "region_mean_price", "region_mean_rating",
    ]
    scaler = StandardScaler()
    df[[f"{c}_scaled" for c in numeric_cols]] = scaler.fit_transform(df[numeric_cols])

    return df, scaler, region_encoding


if __name__ == "__main__":
    df_raw = pd.read_csv(INPUT_PATH)
    df_processed, scaler, region_encoding = preprocess(df_raw)

    df_processed.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

    print(f"\nForma final: {df_processed.shape}")
    print(f"Columnas: {df_processed.columns.tolist()}")
    print(f"\nGuardado en: {OUTPUT_PATH}")
