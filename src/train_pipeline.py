"""
train_pipeline.py
=================
Entrena StandardScaler, K-Means y PCA y guarda todos los objetos en
models/inwine_pipeline.joblib para poder aplicarlos a vinos nuevos sin reentrenar.

Uso / Usage:
    python -m src.train_pipeline
"""

# sys permite modificar la lista de rutas donde Python busca módulos
# sys allows modifying the list of paths where Python looks for modules
import sys
from pathlib import Path  # Para trabajar con rutas de archivo de forma segura / For safe file path handling

import joblib              # Guarda y carga objetos Python en disco (más eficiente que pickle) / Saves and loads Python objects to disk
import pandas as pd        # Manejo de tablas de datos / Data table handling
from sklearn.cluster import KMeans        # Algoritmo de clustering K-Means
from sklearn.decomposition import PCA     # Algoritmo de reducción de dimensionalidad

# Ruta raíz del proyecto (sube un nivel desde src/) / Project root path (one level up from src/)
ROOT = Path(__file__).resolve().parents[1]

# Añade la carpeta preprocessing/ al path para poder importar preprocessing.py y mappings.py
# Adds the preprocessing/ folder to the path so we can import preprocessing.py and mappings.py
sys.path.insert(0, str(ROOT / "preprocessing"))

# Importa la función de preprocesamiento que ya existe en preprocessing/preprocessing.py
# Imports the preprocessing function that already exists in preprocessing/preprocessing.py
from preprocessing import preprocess  # noqa: E402

# Usa wines_SPA_enriched_FINAL.csv si existe (tiene flavor_descriptor del scraper).
# Si no existe, cae al CSV de limpieza básica (sin flavors).
# Uses wines_SPA_enriched_FINAL.csv if it exists (has flavor_descriptor from scraper).
# Falls back to the basic clean CSV (no flavors) if it doesn't exist.
_ENRICHED_FINAL = ROOT / "data" / "processed" / "wines_SPA_enriched_FINAL.csv"
_CLEAN = ROOT / "data" / "processed" / "wines_SPA_clean.csv"
DATA_PATH = _ENRICHED_FINAL if _ENRICHED_FINAL.exists() else _CLEAN

# Ruta donde se guardará el artefacto con todos los objetos entrenados
# Path where the artifact with all trained objects will be saved
MODEL_PATH = ROOT / "models" / "inwine_pipeline.joblib"

# Número de clusters — debe coincidir con los perfiles definidos en app/data/clusters.py
# Number of clusters — must match the profiles defined in app/data/clusters.py
K = 8

# Semilla aleatoria para reproducibilidad: con el mismo valor siempre da el mismo resultado
# Random seed for reproducibility: the same value always produces the same result
RANDOM_STATE = 42


def train(data_path: Path = DATA_PATH, model_path: Path = MODEL_PATH) -> dict:
    """
    Ejecuta el pipeline completo de entrenamiento y guarda el artefacto.
    Devuelve el diccionario de artefactos guardado.

    Runs the full training pipeline and saves the artifact.
    Returns the saved artifacts dictionary.
    """

    # Carga el CSV de vinos limpios como DataFrame / Load the clean wines CSV as a DataFrame
    df_raw = pd.read_csv(data_path)
    print(f"Dataset cargado: {df_raw.shape}")

    # Llama al preprocesamiento existente: transforma, escala y codifica las columnas
    # Calls the existing preprocessing: transforms, scales and encodes the columns
    # Devuelve / Returns:
    #   df       → DataFrame con las columnas escaladas listas para el modelo
    #   scaler   → StandardScaler ya entrenado (sabe la media y desviación de cada columna)
    #   encodings → diccionarios con los valores medios por región y por uva (Target Encoding)
    df, scaler, encodings = preprocess(df_raw)
    print(f"Preprocesamiento completado: {df.shape}")

    # Selecciona solo las columnas que terminan en "_scaled" (las que usa el modelo)
    # Selects only columns ending in "_scaled" (the ones the model uses)
    feature_columns = [c for c in df.columns if c.endswith("_scaled")]

    # Convierte el DataFrame a una matriz numpy (array de números) que sklearn entiende
    # Converts the DataFrame to a numpy matrix (number array) that sklearn understands
    X = df[feature_columns].values
    print(f"Features para clustering/PCA: {len(feature_columns)} columnas")

    # Crea el modelo K-Means con 8 clusters, semilla fija y 10 inicializaciones distintas
    # n_init=10 prueba 10 puntos de partida aleatorios y se queda con el mejor resultado
    # Creates K-Means with 8 clusters, fixed seed and 10 different initializations
    # n_init=10 tries 10 random starting points and keeps the best result
    kmeans = KMeans(n_clusters=K, random_state=RANDOM_STATE, n_init=10)

    # Entrena el modelo: calcula los 8 centroides sobre los datos
    # Trains the model: calculates the 8 centroids on the data
    kmeans.fit(X)

    # Cuenta cuántos vinos hay en cada cluster para mostrar la distribución
    # Counts how many wines are in each cluster to show the distribution
    cluster_counts = dict(
        sorted(pd.Series(kmeans.labels_).value_counts().to_dict().items())
    )
    print(f"K-Means entrenado (K={K}). Distribución: {cluster_counts}")

    # Crea el modelo PCA con 2 componentes (PC1 y PC2 para visualización en 2D)
    # Creates the PCA model with 2 components (PC1 and PC2 for 2D visualization)
    pca = PCA(n_components=2, random_state=RANDOM_STATE)

    # Entrena PCA: calcula las direcciones de máxima varianza en los datos
    # Trains PCA: calculates the directions of maximum variance in the data
    pca.fit(X)

    # Calcula qué porcentaje de información conserva cada componente
    # Calculates what percentage of information each component preserves
    pc1_var = pca.explained_variance_ratio_[0] * 100
    pc2_var = pca.explained_variance_ratio_[1] * 100
    print(f"PCA entrenado — PC1: {pc1_var:.1f}%, PC2: {pc2_var:.1f}% de varianza explicada")

    # Crea la carpeta models/ si no existe (exist_ok=True evita error si ya existe)
    # Creates the models/ folder if it doesn't exist (exist_ok=True avoids error if it already exists)
    model_path.parent.mkdir(exist_ok=True)

    # Agrupa todos los objetos entrenados en un diccionario (la "caja")
    # Groups all trained objects in a dictionary (the "box")
    artifacts = {
        "scaler": scaler,              # StandardScaler entrenado / Trained StandardScaler
        "target_encodings": encodings, # Medias de precio y rating por región y uva / Price and rating means by region and grape
        "kmeans": kmeans,              # Modelo K-Means entrenado con sus 8 centroides / Trained K-Means model with its 8 centroids
        "pca": pca,                    # Modelo PCA entrenado / Trained PCA model
        "feature_columns": feature_columns,  # Lista con los nombres de columnas en el orden exacto del entrenamiento
                                             # List with column names in the exact order used during training
        "k": K,                        # Número de clusters (guardado como referencia) / Number of clusters (saved as reference)
    }

    # Serializa el diccionario y lo guarda en disco como archivo .joblib
    # Serializes the dictionary and saves it to disk as a .joblib file
    joblib.dump(artifacts, model_path)
    print(f"Artefacto guardado en: {model_path}")

    # Devuelve el diccionario para poder usarlo directamente sin releer el disco
    # Returns the dictionary so it can be used directly without re-reading from disk
    return artifacts


# Solo ejecuta train() si este archivo se llama directamente (no si se importa)
# Only runs train() if this file is called directly (not if it's imported)
if __name__ == "__main__":
    train()
