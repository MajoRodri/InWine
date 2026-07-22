import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ==============================================================================
# 1. CARGA DE DATOS Y VALIDACIÓN
# ==============================================================================

# TODO: Aquí irá la ruta al archivo que generará tu compañera
ruta_archivo = 'wines_SPA_clean.csv' 

print("--- Cargando dataset ---")
try:
    df = pd.read_csv(ruta_archivo)
    print("Dataset cargado correctamente. Filas y columnas:", df.shape)
except FileNotFoundError:
    print(f"Esperando a que el archivo {ruta_archivo} esté disponible en el repositorio.")
    # Creamos un DataFrame vacío temporal para que el código no rompa al probarlo hoy
    df = pd.DataFrame(columns=['price', 'rating', 'region', 'vine_type', 'wine_ageing'])

# Validación 1: Nulos residuales
print("\n--- Validación de Nulos ---")
# Debería dar 0 en todas las columnas si la limpieza previa es correcta
print(df.isnull().sum())

# Validación 2: Tipos de datos
print("\n--- Tipos de Datos ---")
print(df.dtypes)

# ==============================================================================
# 2. ANÁLISIS EXPLORATORIO DE DATOS (EDA)
# ==============================================================================

# Si el DataFrame no está vacío, generamos los gráficos
if not df.empty:
    sns.set_theme(style="whitegrid")
    
    # Configuramos el lienzo con la estructura de 5 gráficos: 2 arriba y 3 abajo
    fig = plt.figure(figsize=(18, 10))
    fig.suptitle('EDA Completo del Dataset de Vinos', fontsize=16, fontweight='bold')

    # Fila superior: 2 gráficos (centrados usando un grid de 6 columnas)
    ax1 = plt.subplot2grid((2, 6), (0, 1), colspan=2) # Arriba izquierda
    ax2 = plt.subplot2grid((2, 6), (0, 3), colspan=2) # Arriba derecha

    # Fila inferior: 3 gráficos
    ax3 = plt.subplot2grid((2, 6), (1, 0), colspan=2) # Abajo izquierda
    ax4 = plt.subplot2grid((2, 6), (1, 2), colspan=2) # Abajo centro
    ax5 = plt.subplot2grid((2, 6), (1, 4), colspan=2) # Abajo derecha

    # --- Gráfico 1 (Arriba Izq): Distribución de Precios ---
    # TODO: Ajustar el nombre de la columna si tu compañera la llama distinto ('precio', 'price')
    sns.histplot(df['price'], bins=30, kde=True, ax=ax1, color='purple')
    ax1.set_title('Distribución de Precio')

    # --- Gráfico 2 (Arriba Der): Distribución de Rating ---
    sns.histplot(df['rating'], bins=20, kde=True, ax=ax2, color='gold')
    ax2.set_title('Distribución de Rating')

    # --- Gráfico 3 (Abajo Izq): Región ---
    # Al ser categórica, un countplot es ideal. Limitamos al top 10 para que se lea bien.
    top_regions = df['region'].value_counts().nlargest(10).index
    sns.countplot(data=df[df['region'].isin(top_regions)], y='region', ax=ax3, order=top_regions, palette='viridis')
    ax3.set_title('Top 10 Regiones')

    # --- Gráfico 4 (Abajo Centro): Tipo de Uva ---
    top_vines = df['vine_type'].value_counts().nlargest(10).index
    sns.countplot(data=df[df['vine_type'].isin(top_vines)], y='vine_type', ax=ax4, order=top_vines, palette='magma')
    ax4.set_title('Top 10 Tipos de Uva')

    # --- Gráfico 5 (Abajo Der): Crianza (Gráfico Lineal) ---
    # Para mantener una representación visual puramente lineal en esta posición,
    # agrupamos los conteos y los trazamos como una línea continua ordenando por la edad de la crianza.
    ageing_counts = df['wine_ageing'].value_counts().sort_index()
    sns.lineplot(x=ageing_counts.index, y=ageing_counts.values, ax=ax5, marker='o', color='teal', linewidth=2)
    ax5.set_title('Distribución de Crianza (Evolución Lineal)')
    ax5.tick_params(axis='x', rotation=45)

    plt.tight_layout()
    plt.show()