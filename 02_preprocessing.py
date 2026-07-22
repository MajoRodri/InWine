import pandas as pd
from sklearn.preprocessing import StandardScaler, TargetEncoder, OneHotEncoder
import pickle # Para guardar los diccionarios y codificadores

# ==============================================================================
# 1. CARGA DE DATOS
# ==============================================================================
# TODO: Cambiar ruta cuando el archivo esté listo
ruta_archivo = 'wines_SPA_clean.csv' 

try:
    df = pd.read_csv(ruta_archivo)
except FileNotFoundError:
    print("Archivo no encontrado. Usa este script cuando wines_SPA_clean.csv esté listo.")
    exit()

# Hacemos una copia para no modificar el original de golpe
df_procesado = df.copy()

# ==============================================================================
# 2. CREACIÓN DE DICCIONARIOS DE MAPEO (Categorías Semánticas)
# ==============================================================================

# TODO: Rellenar estos diccionarios con las categorías reales cuando explores los datos.
# Ejemplo: si 'serving_temperature' dice '10-12 grados', lo pasamos a un valor numérico o clase.
dict_serving_temp = {
    'frio': 0,
    'ambiente': 1,
    # Añadir las correspondencias reales aquí...
}

dict_flavor = {
    'afrutado': 1,
    'amaderado': 2,
    # Añadir las correspondencias reales aquí...
}

# Aplicamos el mapeo (si las columnas existen en el dataset final)
if 'serving_temperature' in df_procesado.columns:
    df_procesado['serving_temperature_mapped'] = df_procesado['serving_temperature'].map(dict_serving_temp)

if 'flavor_descriptor' in df_procesado.columns:
    df_procesado['flavor_mapped'] = df_procesado['flavor_descriptor'].map(dict_flavor)

# ==============================================================================
# 3. ESCALADO DE VARIABLES NUMÉRICAS (StandardScaler)
# ==============================================================================
# El modelo necesita que métricas como precio y rating estén en la misma escala
# para que los precios altos no 'aplasten' la importancia de los ratings pequeños.

columnas_numericas = ['price', 'rating'] # TODO: Añadir si hay más
scaler = StandardScaler()

# Ajustamos y transformamos los datos
df_procesado[columnas_numericas] = scaler.fit_transform(df_procesado[columnas_numericas])

# ==============================================================================
# 4. CODIFICACIÓN DE CATEGÓRICAS (One-Hot vs Target Encoding)
# ==============================================================================
"""
JUSTIFICACIÓN DE LA ESTRATEGIA (Para comentar en la presentación del proyecto):
1. One-Hot Encoding: Lo usaremos para 'wine_ageing' porque previsiblemente tiene 
   pocas categorías (baja cardinalidad: Joven, Crianza, Reserva, Gran Reserva). 
   Crear 4 columnas nuevas no satura el modelo.
   
2. Target Encoding: Lo usaremos para 'region' y 'vine_type'. En España hay docenas 
   de regiones y cientos de tipos de uva (alta cardinalidad). Si usamos One-Hot, 
   crearíamos cientos de columnas de ceros y unos, provocando "la maldición de la 
   dimensionalidad". Target Encoding las reemplaza por el valor promedio de la 
   variable objetivo (ej. el rating o el precio medio de esa uva/región), manteniendo 
   la tabla compacta.
"""

# --- A) One-Hot Encoding para Baja Cardinalidad ---
col_onehot = ['wine_ageing']
ohe = OneHotEncoder(sparse_output=False, drop='first') # drop='first' evita colinealidad
ohe_results = ohe.fit_transform(df_procesado[col_onehot])

# Convertimos a DataFrame para unirlo al original
df_ohe = pd.DataFrame(ohe_results, columns=ohe.get_feature_names_out(col_onehot))
df_procesado = pd.concat([df_procesado.reset_index(drop=True), df_ohe], axis=1)
df_procesado = df_procesado.drop(columns=col_onehot)

# --- B) Target Encoding para Alta Cardinalidad ---
cols_target = ['region', 'vine_type']
target_col = 'price' # TODO: Definir si vuestra variable a predecir es el precio o el rating

target_encoder = TargetEncoder()
# Importante: El Target Encoder necesita conocer la variable objetivo para calcular la media
df_procesado[cols_target] = target_encoder.fit_transform(df_procesado[cols_target], df_procesado[target_col])

# ==============================================================================
# 5. OUTPUT ENTREGABLE
# ==============================================================================

# Guardamos el DataFrame final listo para Machine Learning
ruta_output = 'wines_SPA_preprocessed.csv'
df_procesado.to_csv(ruta_output, index=False)
print(f"Procesamiento terminado. DataFrame guardado en: {ruta_output}")

# Opcional pero muy buena práctica: guardar los encoders y diccionarios como archivos .pkl 
# para que el equipo que haga el modelo pueda desescalar o codificar nuevos datos en el futuro.
with open('preprocessing_objects.pkl', 'wb') as f:
    pickle.dump({
        'scaler': scaler,
        'ohe': ohe,
        'target_encoder': target_encoder,
        'dict_serving_temp': dict_serving_temp,
        'dict_flavor': dict_flavor
    }, f)
print("Objetos de preprocesamiento (escaladores y diccionarios) guardados en 'preprocessing_objects.pkl'")