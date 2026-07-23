<div align="center">
  <img src="app/static/img/items_flipped.png" width="160" align="left"/>
  <img src="app/static/img/items.png" width="160" align="right"/>
</div>
<div align="center">
  <img src="app/static/img/logosinfondo.png" alt="InWine logo" height="120" />
  <h1>𝓘𝓷𝓦𝓲𝓷𝓮</h1>
  <p><em>Descubre · Comprende · Disfruta</em></p>
</div>

<br/>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-6B1020?style=flat-square&logo=python&logoColor=F0E4CC"/>
  <img src="https://img.shields.io/badge/FastAPI-0.111-8B1A2E?style=flat-square&logo=fastapi&logoColor=F0E4CC"/>
  <img src="https://img.shields.io/badge/scikit--learn-1.4-9B7010?style=flat-square&logo=scikit-learn&logoColor=F0E4CC"/>
  <img src="https://img.shields.io/badge/estado-activo-C9882A?style=flat-square&logoColor=F0E4CC"/>
</p>

---

## ¿Qué es InWine?

**InWine** es un sommelier virtual para vinos españoles.

La mayoría de personas no sabe elegir vino — las etiquetas son confusas, las regiones desconocidas y el precio no siempre garantiza calidad. InWine analiza más de **1.900 vinos españoles** y, a partir de tus gustos, ocasión y presupuesto, te recomienda el vino perfecto. Sin que necesites saber nada de vinos.

---

## Pipeline

```
Scraping  ›  Limpieza  ›  EDA  ›  Preprocesamiento  ›  Clustering  ›  PCA  ›  App
```

<details>
<summary>&nbsp;▸ &nbsp;<strong>I &nbsp;·&nbsp; Scraping</strong> &nbsp;—&nbsp; <code>scrapper/</code></summary>
<br/>

Scraping de enriquecimiento con **Playwright** sobre [Vivinos](https://www.vivinos.com). El script cruzaba los vinos del dataset original con la página y completaba los campos que faltaban:

- Descriptores de sabor (`flavor_descriptor`)
- Tipo de vino (`vine_type` — Tinto, Blanco, Rosado, Espumoso, Generoso)
- Variedad de uva (`grape_variety`)

→ `data/processed/wines_SPA_enriched.csv` &nbsp;·&nbsp; 6.956 vinos

</details>

<details>
<summary>&nbsp;▸ &nbsp;<strong>II &nbsp;·&nbsp; Limpieza</strong> &nbsp;—&nbsp; <code>notebooks/01_cleaning.ipynb</code></summary>
<br/>

Preparación y validación del dataset enriquecido:

- **5.038 duplicados** detectados y eliminados
- Corrección y estandarización de `vine_type` y `grape_variety`
- Detección y codificación de `wine_ageing` (Joven / Crianza)
- Creación de la feature `quality_price_ratio`
- 0 nulos en el dataset resultante

→ `data/processed/wines_SPA_clean.csv` &nbsp;·&nbsp; 6.956 → **2.024 vinos únicos**

</details>

<details>
<summary>&nbsp;▸ &nbsp;<strong>III &nbsp;·&nbsp; EDA</strong> &nbsp;—&nbsp; <code>notebooks/02_eda.ipynb</code></summary>
<br/>

Exploración visual y estadística para entender el dataset y justificar las decisiones de modelado:

- Distribución de precios — fuerte asimetría → transformación logarítmica
- Distribución de ratings y relación calidad-precio
- Análisis por región, tipo de vino y uva
- Correlaciones y detección de outliers

<blockquote>
<details>
<summary><em>Hallazgos</em></summary>
<br/>

| Hallazgo | Implicación para el modelo |
| :--- | :--- |
| Precio muy asimétrico (skew 5.09, rango 4.99 € – 3.119 €) | Escalar en log antes de calcular distancias |
| Rating casi sin varianza (4.2 – 4.9, media 4.4) | No usarlo como señal fuerte de calidad |
| 76 regiones muy desiguales — Ribera del Duero y Rioja concentran el 50 % | Target Encoding en vez de One-Hot para `region` |
| Tempranillo domina el 55 % · `Blend/Other` representa el 20 % | Aceptado — no forzar uva donde no hay dominante clara |
| `quality_price_ratio` correlaciona fuerte con `price_euros` y `luxury_category` | Evitar las tres juntas en el motor de similitud — triple-conteo de precio |
| 931 vinos únicos con una media de 2.2 añadas cada uno | Split train/test agrupado por `(winery, wine_name)`, no fila a fila |
| 20.6 % de vinos con crianza — tienden a ser más caros pero con mucho solape | Usar como feature binaria, no como señal de calidad absoluta |
| 0 inconsistencias `vine_type` / `grape_variety` | Dataset consistente, listo para preprocesamiento |

</details>
</blockquote>

</details>

<details>
<summary>&nbsp;▸ &nbsp;<strong>IV &nbsp;·&nbsp; Preprocesamiento</strong> &nbsp;—&nbsp; <code>notebooks/03_preprocessing.ipynb</code></summary>
<br/>

Transformaciones justificadas por el EDA para preparar el dataset para los modelos:

| Variable | Transformación | Motivo |
| :--- | :--- | :--- |
| `price_euros` | Log — `price_log` | Asimetría extrema en precios |
| `vine_type` | One-Hot Encoding | 5 categorías sin orden entre ellas |
| `region` / `grape_variety` | Target Encoding + suavizado | Alta cardinalidad (69 y 16 categorías) |
| `wine_ageing` | Sin cambios | Ya es binaria desde limpieza |
| Numéricas | StandardScaler | Escala común para cálculo de distancias |

→ `data/processed/wines_SPA_model_ready.csv`

<blockquote>
<details>
<summary><em>Decisiones</em></summary>
<br/>

| Problema detectado | Corrección aplicada |
| :--- | :--- |
| `price_euros` sin transformación — su asimetría extrema (skew 5.09) destruye la matriz de distancias en el recomendador | `np.log1p()` antes de estandarizar → feature `price_log` |
| Triple-conteo de precio — `price_euros`, `luxury_category` y `quality_price_ratio` están altamente correlacionadas; meterlas juntas da peso desproporcionado al factor precio | Se descartan `price_euros` crudo y `luxury_category`; solo entran `price_log` y `quality_price_ratio` |
| `grape_variety` con 16 categorías y 20 % `Blend/Other` — One-Hot generaría columnas dispersas y ruidosas | Target Encoding con suavizado estadístico, igual que `region` |
| Si el pipeline se corre sin haber ejecutado el scraper, `flavor_descriptor` no existe y el código falla | Validación previa — si la columna no existe, las familias aromáticas se rellenan con ceros y el modelo continúa |

</details>
</blockquote>

</details>

<details>
<summary>&nbsp;▸ &nbsp;<strong>V &nbsp;·&nbsp; Clustering</strong> &nbsp;—&nbsp; <code>notebooks/04_clustering.ipynb</code></summary>
<br/>

Agrupación de vinos en perfiles con **k-means** sobre el espacio preprocesado. El objetivo es identificar grupos con características similares — precio, tipo, sabor, región — que sirvan de base al recomendador.

</details>

<details>
<summary>&nbsp;▸ &nbsp;<strong>VI &nbsp;·&nbsp; PCA</strong> &nbsp;—&nbsp; <code>notebooks/05_pca.ipynb</code></summary>
<br/>

Reducción de dimensionalidad con **PCA** para visualizar los clusters en 2D/3D y validar que los grupos tienen sentido enológico.

</details>

<details>
<summary>&nbsp;▸ &nbsp;<strong>VII &nbsp;·&nbsp; Aplicación Web</strong> &nbsp;—&nbsp; <code>app/</code></summary>
<br/>

Web app con **FastAPI + Jinja2**. Diseño luxury: fondo burdeos, tipografía serif, paleta dorada.

| Ruta | Descripción |
| :--- | :--- |
| `/` | Inicio |
| `/buscar` | Búsqueda libre de vinos |
| `/recomendar` | Recomendación personalizada |
| `/explorar` | Perfiles de usuario (clusters) |
| `/valor` | Ranking calidad-precio |
| `/comida` | Chatbot sommelier por plato |
| `/vino/{id}` | Ficha de vino |
| `/nosotros` | Equipo y metodología |

</details>

---

<details>
<summary>&nbsp;▸ &nbsp;<strong>Stack tecnológico</strong></summary>
<br/>

| Capa | Tecnología |
| :--- | :--- |
| Scraping | Python · Playwright |
| Análisis | Pandas · NumPy · Matplotlib · Seaborn |
| Modelado | scikit-learn — k-means · PCA · StandardScaler |
| Backend | FastAPI · Uvicorn |
| Frontend | Jinja2 · CSS · Vanilla JS |

</details>

<details>
<summary>&nbsp;▸ &nbsp;<strong>Estructura del proyecto</strong></summary>
<br/>

```
InWine/
├── app/                        # Aplicación web
│   ├── data/                   # Datos de muestra
│   ├── routers/                # Endpoints
│   ├── services/               # Recomendador y búsqueda
│   ├── static/                 # CSS, JS, imágenes
│   └── templates/              # HTML (Jinja2)
├── notebooks/
│   ├── 01_cleaning.ipynb
│   ├── 02_eda.ipynb
│   ├── 03_preprocessing.ipynb
│   ├── 04_clustering.ipynb
│   └── 05_pca.ipynb
├── preprocessing/
│   ├── preprocessing.py
│   └── mappings.py
├── scrapper/
│   └── scrapper_enriched.py
├── data/
│   ├── raw/
│   └── processed/
└── requirements.txt
```

</details>

<details>
<summary>&nbsp;▸ &nbsp;<strong>Cómo ejecutar</strong></summary>
<br/>

**Requisitos** — Python 3.11+ · pip

```bash
git clone https://github.com/MajoRodri/InWine.git
cd InWine
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux / Mac
pip install -r requirements.txt
```

**App web**
```bash
uvicorn app.main:app --reload
# http://localhost:8000
```

**Scraper**
```bash
playwright install chromium
python scrapper/scrapper_enriched.py
```

**Preprocesamiento**
```bash
cd preprocessing && python preprocessing.py
```

</details>

---

## Equipo

| Miembro | Rol | Contacto |
| :--- | :--- | :--- |
| **Mariajose Alvarez** | Scrum Master | [@MajoRodri](https://github.com/MajoRodri) |
| **María Roldán** | Product Owner | [@Mary1922](https://github.com/Mary1922) |
| **Adrianna Aránguez** | Developer | [@adrianaarang](https://github.com/adrianaarang) |
| **Gema Villanueva** | Developer | [@Gema-Villanueva](https://github.com/Gema-Villanueva) |

<br/>

<img src="app/static/img/tinto.png" width="100%" style="display:block;margin:0;padding:0;"/>
