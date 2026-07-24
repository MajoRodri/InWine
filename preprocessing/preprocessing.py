"""
preprocessing.py
================
Preprocesamiento final para el motor de recomendación de Sommelier IA.

Entrada:  wines_SPA_enriched_FINAL.csv (1918 filas, validado: 0 nulos,
          0 duplicados, 0 inconsistencias vine_type/grape_variety).
Salida:   DataFrame escalado y codificado, listo para vectorizar/entrenar.

"""
"""
Decisiones de preprocesamiento y codificación (justificadas post-EDA):
----------------------------------------------------------------------
- price_euros -> TRANSFORMACIÓN LOGARÍTMICA (price_log). Como se vio en el EDA, 
  el precio tiene una fuerte asimetría (cola larga a la derecha). Aplicar log1p() 
  comprime esta asimetría y evita que los vinos de lujo dominen y distorsionen 
  matemáticamente el cálculo de distancias en el recomendador.

- Prevención de Colinealidad -> Se descartan 'luxury_category' y 'price_euros' 
  crudo. Al mantener 'price_log' y 'quality_price_ratio', evitamos el triple-conteo 
  de la variable precio, lo que le daría un peso desproporcionado en el modelo.

- vine_type (5 categorías: Tinto, Blanco, Rosado, Espumoso, Generoso) ->
  ONE-HOT ENCODING. Cardinalidad baja y sin relación de orden entre
  categorías (un "Blanco" no es "más" ni "menos" que un "Tinto"). Aporta 
  interpretabilidad sin disparar la dimensionalidad (5 dummies).

- grape_variety (16 categorías) y region (69 categorías) -> TARGET ENCODING 
  (no One-Hot). Un One-Hot para estas variables sería muy disperso (especialmente 
  con el 20% de "Blend/Other" en uvas y regiones con 1-2 vinos) y añadiría ruido. 
  Se codifican por sus estadísticos agregados relevantes para el recomendador: 
  precio medio y rating medio (ej. region_mean_price, grape_variety_mean_rating),
  con SUAVIZADO (smoothing) hacia la media global para muestras pequeñas,
  evitando medias extremas poco fiables. Riesgo a vigilar: con datos nuevos 
  (una región o uva no vista en entrenamiento) se usa la media global como fallback.

- wine_ageing -> YA ESTÁ CODIFICADA. Es un flag binario (0=Joven,
  1=Crianza) desde el propio pipeline de limpieza; no necesita
  transformación adicional, se usa tal cual como feature numérica.

Variables numéricas escaladas con StandardScaler (media 0, desviación 1):
  price_log, rating, quality_price_ratio, year, wine_ageing, 
  region_mean_price, region_mean_rating, grape_variety_mean_price, 
  grape_variety_mean_rating, service_temp_midpoint y flavor_families (si aplica).
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from pathlib import Path
from mappings import map_flavors_to_families, map_temperature_to_semantic, FLAVOR_FAMILIES

# 1. Detectamos dónde está ubicado ESTE script (carpeta 'preprocessing')
BASE_DIR = Path(__file__).resolve().parent

# 2. Construimos las rutas absolutas subiendo un nivel (.parent) hacia 'data/processed'
# Esto funcionará sin importar desde qué carpeta de la terminal se ejecute el script.
INPUT_PATH = BASE_DIR.parent / "data" / "processed" / "wines_SPA_clean.csv"
OUTPUT_PATH = BASE_DIR.parent / "data" / "processed" / "wines_SPA_model_ready.csv"

TARGET_ENCODING_SMOOTHING = 10  # Suavizado estadístico

def validate_dataset(df: pd.DataFrame) -> None:
    """Validaciones de integridad basadas en las reglas de negocio."""
    # Permitimos nulos SOLO en 'flavor_descriptor' por si el scraper no se ejecutó
    nulos_no_flavor = df.drop(columns=['flavor_descriptor'], errors='ignore').isna().sum().sum()
    assert nulos_no_flavor == 0, "Hay nulos residuales en columnas core"
    assert df.duplicated().sum() == 0, "Hay filas duplicadas residuales"
    assert df["price_euros"].min() > 0, "Hay precios <= 0"
    assert df["rating"].between(1, 5).all(), "Hay ratings fuera de rango [1,5]"
    print("Validación OK: dataset listo para transformar.")

def target_encode_feature(df: pd.DataFrame, feature_name: str) -> tuple:
    """
    Target Encoding con suavizado para variables de alta cardinalidad (region, grape_variety).
    Evita la maldición de la dimensionalidad reemplazando el texto por el precio/rating medio.
    """
    global_mean_price = df["price_euros"].mean()
    global_mean_rating = df["rating"].mean()

    stats = df.groupby(feature_name).agg(
        n=("price_euros", "size"),
        mean_price=("price_euros", "mean"),
        mean_rating=("rating", "mean"),
    )
    
    k = TARGET_ENCODING_SMOOTHING
    stats[f"{feature_name}_mean_price"] = (stats["mean_price"] * stats["n"] + global_mean_price * k) / (stats["n"] + k)
    stats[f"{feature_name}_mean_rating"] = (stats["mean_rating"] * stats["n"] + global_mean_rating * k) / (stats["n"] + k)

    df = df.merge(stats[[f"{feature_name}_mean_price", f"{feature_name}_mean_rating"]], on=feature_name, how="left")
    
    # Fallback para datos nuevos en inferencia
    df[f"{feature_name}_mean_price"] = df[f"{feature_name}_mean_price"].fillna(global_mean_price)
    df[f"{feature_name}_mean_rating"] = df[f"{feature_name}_mean_rating"].fillna(global_mean_rating)
    
    dict_stats = {
        "global_mean_price": global_mean_price, 
        "global_mean_rating": global_mean_rating,
        f"{feature_name}_stats": stats[[f"{feature_name}_mean_price", f"{feature_name}_mean_rating"]].to_dict("index")
    }
    return df, dict_stats

def apply_flavor_mapping(df: pd.DataFrame) -> pd.DataFrame:
    """Convierte flavor_descriptor en 5 columnas numéricas. Resistente a ausencia de la columna."""
    # Control de fallos: Si los alumnos no hicieron el scraping, se ponen a 0
    if "flavor_descriptor" not in df.columns:
        print("⚠️ 'flavor_descriptor' no encontrado. Se llenarán las familias aromáticas con 0.")
        for fam in FLAVOR_FAMILIES:
            df[f"flavor_{fam}"] = 0
        return df

    family_counts = df["flavor_descriptor"].apply(map_flavors_to_families).apply(pd.Series)
    family_counts.columns = [f"flavor_{c}" for c in family_counts.columns]
    return pd.concat([df, family_counts], axis=1)

def apply_temperature_mapping(df: pd.DataFrame) -> pd.DataFrame:
    """Extrae punto medio numérico de la temperatura."""
    mapped = df["service_temperature"].apply(map_temperature_to_semantic)
    df["service_temp_label"] = mapped.apply(lambda t: t[0])
    df["service_temp_midpoint"] = mapped.apply(lambda t: t[1])
    # Llenamos nulos con la media por si hay desconocidos
    df["service_temp_midpoint"] = df["service_temp_midpoint"].fillna(df["service_temp_midpoint"].mean())
    return df

def preprocess(df: pd.DataFrame) -> tuple:
    """Pipeline completo corregido según hallazgos del EDA."""
    validate_dataset(df)
    df = df.copy()

    # 0. Transformación logarítmica del precio (CORRECCIÓN EDA: Mitigar asimetría extrema)
    df['price_log'] = np.log1p(df['price_euros'])

    # 1. Mapeos semánticos
    df = apply_flavor_mapping(df)
    df = apply_temperature_mapping(df)

    # 2. Target Encoding para regiones y uvas (CORRECCIÓN: Se añade uva por alta cardinalidad)
    df, region_encoding = target_encode_feature(df, "region")
    df, grape_encoding = target_encode_feature(df, "grape_variety")

    # 3. One-Hot Encoding de vine_type (baja cardinalidad)
    df = pd.get_dummies(df, columns=["vine_type"], prefix="vine_type", dtype=int)

    # 4. Escalado de variables numéricas continuas
    # CORRECCIÓN EDA: Se elimina 'luxury_category' y 'price_euros' crudo para evitar 
    # triple-conteo y multicolinealidad con 'quality_price_ratio' y 'price_log'.
    numeric_cols = [
        "price_log", "rating", "quality_price_ratio", "year", "wine_ageing",
        "region_mean_price", "region_mean_rating",
        "grape_variety_mean_price", "grape_variety_mean_rating", "service_temp_midpoint"
    ]
    
# Añadimos las variables de sabor a escalar si existen
    flavor_cols = [f"flavor_{fam}" for fam in FLAVOR_FAMILIES]
    numeric_cols.extend(flavor_cols)

    scaler = StandardScaler()
    scaled_feature_names = [f"{c}_scaled" for c in numeric_cols]
    df[scaled_feature_names] = scaler.fit_transform(df[numeric_cols])

    # --> NUEVO: Borramos las columnas redundantes del DataFrame final
    df = df.drop(columns=['price_euros', 'luxury_category'], errors='ignore')

    return df, scaler, {"region": region_encoding, "grape": grape_encoding}

if __name__ == "__main__":
    df_raw = pd.read_csv(INPUT_PATH)
    df_processed, scaler, encodings = preprocess(df_raw)

    df_processed.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

    print(f"\nForma final: {df_processed.shape}")
    print(f"Guardado en: {OUTPUT_PATH}")