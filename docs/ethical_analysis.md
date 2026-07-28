# Análisis de sesgos y limitaciones de InWine

## 1. Objetivo y alcance del análisis

Este documento analiza los posibles sesgos y limitaciones de InWine, una aplicación de recomendación de vinos que utiliza las preferencias del usuario, reglas definidas por el equipo y técnicas de machine learning para ofrecer recomendaciones personalizadas.

El objetivo no es afirmar que la aplicación produce resultados injustos, sino identificar qué aspectos podrían influir en sus recomendaciones y qué precauciones deben tenerse al interpretar los resultados.

El análisis tiene en cuenta:

- La composición y representatividad del dataset.
- Las decisiones tomadas durante el preprocesamiento de los datos.
- El uso de PCA y K-Means para crear perfiles de vinos.
- Las reglas utilizadas para relacionar las preferencias del usuario con esos perfiles.
- Los filtros y criterios empleados para seleccionar vinos concretos.
- La transparencia de las explicaciones mostradas al usuario.
- La privacidad y el tratamiento de los datos personales.
- Las medidas incorporadas para reducir algunos de los riesgos detectados.

InWine es una herramienta orientativa y no un sistema de decisión de alto impacto. Sus recomendaciones ayudan al usuario a descubrir vinos que podrían encajar con sus gustos, pero no garantizan que el resultado sea siempre la mejor opción para cada persona.

Los resultados dependen de los vinos incluidos en el catálogo, de la calidad de los datos disponibles y de las reglas definidas durante el desarrollo. Por tanto, las recomendaciones deben interpretarse como sugerencias y no como valoraciones objetivas o universales sobre la calidad de un vino.

## 2. Funcionamiento general de InWine

InWine combina información del catálogo, reglas definidas por el equipo y técnicas de machine learning. No existe un único método de recomendación: la aplicación ofrece distintas vías para descubrir vinos y cada una utiliza criterios diferentes.

### 2.1. Recomendador mediante formulario

El usuario puede indicar preferencias como:

- Presupuesto máximo.
- Tipo de vino.
- Región.
- Variedad de uva.
- Maridaje.
- Perfil de sabor.
- Ocasión.

La aplicación filtra el catálogo utilizando estas respuestas. Algunas preferencias, como la región, la uva o el sabor, se aplican de forma flexible: si no existen vinos que cumplan una de ellas, el sistema conserva los candidatos anteriores para evitar devolver una recomendación vacía.

Finalmente, los candidatos se ordenan según su `rating`. La aplicación toma como máximo los cinco vinos mejor valorados y selecciona aleatoriamente uno de ellos. Este procedimiento introduce cierta variedad y evita mostrar siempre el mismo vino, aunque sigue ofreciendo mayor visibilidad a los candidatos con las valoraciones más altas.

La ocasión no interviene directamente en la selección del vino, aunque se utiliza posteriormente para personalizar el texto de la recomendación.

Esta vía trabaja directamente sobre el catálogo disponible y no comienza asignando al usuario un clúster.

### 2.2. Recomendación mediante quiz

Esta vía realiza varias preguntas sobre las preferencias del usuario y utiliza sus respuestas para asignarle uno de los ocho perfiles de vino definidos a partir de los clústeres.

Cada respuesta suma votos a uno o varios perfiles. La respuesta relacionada con el tipo de vino tiene un peso triple, por lo que influye más que el resto en la elección del perfil. Si se produce un empate, se aplican las reglas de desempate establecidas en la aplicación.

Una vez seleccionado el perfil, la aplicación busca los vinos pertenecientes al clúster correspondiente y los puntúa teniendo en cuenta:

- La coincidencia con el tipo de vino indicado.
- La coincidencia con la crianza elegida.
- El `rating`.
- La cercanía del precio al presupuesto del usuario.

Finalmente, selecciona aleatoriamente un vino entre los candidatos mejor puntuados. Esto aporta variedad y evita que una misma combinación de respuestas muestre siempre exactamente el mismo resultado.

Esta recomendación depende tanto de la interpretación realizada por el equipo al definir los ocho perfiles como de los pesos y reglas utilizados en el quiz. Por ello, el perfil asignado representa una aproximación a las preferencias del usuario y no una clasificación objetiva o definitiva de sus gustos.

### 2.3. Recomendación conversacional

Esta vía solicita al usuario información sobre el plato que va a acompañar, su presupuesto, el tipo de vino que prefiere y la crianza deseada.

A partir de estas respuestas, la aplicación filtra y puntúa los vinos disponibles teniendo en cuenta:

- La compatibilidad del vino con el plato seleccionado.
- La coincidencia con el tipo de vino indicado.
- La coincidencia con la crianza elegida.
- El ajuste al presupuesto.
- El `rating`.
- La relación entre la valoración y el precio.

Los candidatos se ordenan según la puntuación obtenida y la aplicación selecciona aleatoriamente uno de los cinco vinos mejor posicionados. Esto introduce variedad en los resultados, aunque los vinos con mejor puntuación tienen más posibilidades de aparecer.

Cuando no existen vinos que cumplan todos los criterios, la aplicación puede flexibilizar algunas preferencias para poder ofrecer una recomendación. Por ello, el resultado no siempre satisface exactamente todas las condiciones introducidas por el usuario.

Esta vía depende de las reglas y ponderaciones definidas por el equipo para combinar los distintos criterios. Por tanto, la puntuación expresa la compatibilidad estimada por el sistema y no garantiza que el vino recomendado sea objetivamente la mejor opción para el usuario.

### 2.4. Recomendación de vinos similares

Esta función parte de un vino concreto y busca alternativas dentro de su mismo clúster. De esta forma, se limita inicialmente la búsqueda a vinos que comparten un perfil general según el modelo de clustering.

Después, los candidatos se puntúan teniendo en cuenta distintos criterios:

- La coincidencia de la variedad de uva.
- La coincidencia del tipo de vino.
- La coincidencia de la crianza.
- La pertenencia a la misma región.
- La cercanía entre los precios.

Finalmente, los vinos se ordenan según la puntuación obtenida y se introduce cierta aleatoriedad entre los candidatos mejor posicionados para ofrecer resultados variados.

Aunque este método utiliza más características que la pertenencia al clúster, no calcula la distancia matemática exacta entre los vinos utilizando todas las variables del modelo. Por ello, los resultados deben entenderse como alternativas con características compatibles, pero no necesariamente como los vinos más cercanos o parecidos desde el punto de vista estadístico.

Además, la similitud depende de los criterios y pesos definidos por el equipo. Algunas características pueden tener más influencia que otras y determinados vinos pueden recibir mayor visibilidad por estar mejor representados en el catálogo.

### 2.5. Uso de PCA y clustering

Antes de agrupar los vinos, el pipeline aplica PCA sobre las 18 variables escaladas y genera dos componentes principales, `PC1` y `PC2`. Estas componentes resumen parte de la información del conjunto de variables y permiten representar visualmente la distribución de los vinos en dos dimensiones.

En conjunto, `PC1` y `PC2` conservan el 48,83 % de la varianza de los datos. Por tanto, esta representación resulta útil para explorar y visualizar los grupos, pero deja fuera el 51,17 % restante de la información. Dos vinos que aparecen próximos en el gráfico no tienen por qué ser idénticos ni compartir todas sus características.

El modelo K-Means agrupa los vinos en ocho clústeres utilizando las 18 variables escaladas originales. Posteriormente, el equipo interpreta las características predominantes de cada grupo y les asigna nombres descriptivos para convertirlos en perfiles comprensibles dentro de la aplicación.

Estos nombres no son categorías oficiales ni objetivas del mundo del vino, sino interpretaciones realizadas por el equipo a partir de los valores medios de cada clúster. Además, el número asignado a cada clúster funciona únicamente como un identificador y no indica calidad, orden o superioridad.

Aunque el pipeline genera `PC1` y `PC2`, estas componentes no se guardan como columnas en el catálogo utilizado por la aplicación. El catálogo conserva el `cluster_id`, que permite relacionar cada vino con el perfil correspondiente.

## 3. Sesgos y limitaciones del dataset

Las recomendaciones de InWine están condicionadas por la composición del dataset. Los tipos de vino, regiones, variedades de uva y rangos de precio con mayor presencia disponen de más candidatos y, por tanto, pueden tener más posibilidades de aparecer en los clústeres y en las recomendaciones.

Esto no significa que la aplicación favorezca intencionadamente determinados vinos, sino que trabaja con un catálogo que no representa de forma equilibrada toda la diversidad del mercado español.

### 3.1. Predominio de vinos tintos

Aproximadamente el 84 % de los vinos del dataset son tintos. Los vinos blancos, rosados, espumosos y generosos tienen una representación considerablemente menor.

Este desequilibrio puede provocar que:

- Los clústeres estén condicionados principalmente por las características de los vinos tintos.
- Existan menos alternativas para los usuarios que prefieren otros tipos de vino.
- Algunas combinaciones de preferencias produzcan pocos resultados.
- Cuando se flexibilicen ciertos criterios, los vinos tintos tengan más posibilidades de aparecer.
- La aplicación muestre una visión poco equilibrada de la diversidad del vino español.

Esta distribución puede estar relacionada con la composición de la fuente original, la disponibilidad de información y reseñas o los criterios empleados para recopilar los vinos. Por tanto, debe entenderse como una limitación de representatividad del catálogo.

### 3.2. Concentración en determinadas regiones y denominaciones de origen

El dataset no representa de manera equilibrada todas las regiones y denominaciones de origen españolas. Algunas zonas cuentan con un número elevado de vinos, mientras que otras aparecen de forma minoritaria o no están representadas.

Este desequilibrio puede provocar que:

- Las regiones con más registros tengan una mayor presencia en los clústeres y en las recomendaciones.
- Los usuarios reciban menos alternativas procedentes de zonas con poca representación.
- Algunas regiones se asocien con mayor facilidad a determinados perfiles de vino.
- La aplicación transmita una visión incompleta de la diversidad geográfica del vino español.

Además, la ausencia o escasa presencia de una región no implica que sus vinos sean menos relevantes o de menor calidad. Únicamente indica que el catálogo utilizado contiene menos información sobre ellos.

Por tanto, las recomendaciones reflejan la distribución geográfica del dataset y no deben interpretarse como una clasificación de la importancia, calidad o variedad de las distintas regiones y denominaciones de origen.

### 3.3. Representación desigual de las variedades de uva

Las variedades de uva tampoco están representadas de manera equilibrada. Algunas aparecen en numerosos vinos, mientras que otras cuentan con pocos registros o no están presentes en el dataset.

Esta distribución puede provocar que:

- Las variedades mayoritarias tengan más influencia en la formación de los clústeres.
- Los vinos elaborados con variedades menos representadas tengan menos posibilidades de aparecer en las recomendaciones.
- Algunas preferencias del usuario dispongan de pocas alternativas.
- La aplicación refleje principalmente las características de las uvas más frecuentes en el catálogo.

Además, la variedad de uva se transforma mediante Target Encoding utilizando el precio medio asociado a cada categoría. Por tanto, su representación numérica no expresa directamente una característica sensorial de la uva, sino su relación con los precios disponibles en el dataset.

Esto puede hacer que dos variedades con precios medios similares reciban valores parecidos, aunque tengan características sensoriales diferentes. También puede reforzar diferencias económicas ya existentes en los datos.

La ausencia o menor presencia de una variedad no implica que sea menos importante, adecuada o valiosa. Únicamente refleja las limitaciones del catálogo utilizado..

### 3.4. Precios y disponibilidad

Los precios proceden del dataset original utilizado para construir el catálogo. Sin embargo, no se dispone de la fecha exacta en la que se recogió el precio de cada vino ni de información sobre su actualización posterior.

Por este motivo, los importes deben considerarse orientativos. El precio real puede variar según el establecimiento, la añada, el formato de la botella, las promociones o el momento de la consulta. Además, un vino incluido en el catálogo puede no encontrarse actualmente disponible.

Esta limitación influye especialmente en las funciones que utilizan el presupuesto y la relación calidad-precio, ya que sus cálculos se realizan con los precios almacenados en el dataset. Si estos están desactualizados, un vino podría clasificarse como ajustado al presupuesto o con buena relación calidad-precio sin que esto coincida con la situación actual del mercado.

Por tanto, la aplicación no debe presentar los precios como actuales ni garantizar la disponibilidad de los productos. Sería recomendable indicar al usuario que compruebe ambos datos en el establecimiento antes de realizar la compra.

### 3.5. Limitaciones de las valoraciones

El `rating` influye en varias funciones de la aplicación. Se utiliza para ordenar o puntuar candidatos y, por tanto, los vinos con valoraciones más altas pueden tener más posibilidades de aparecer en las recomendaciones.

Sin embargo, el dataset no proporciona suficiente información para interpretar completamente estas puntuaciones. No se conoce con precisión:

- El número de valoraciones utilizado para calcular cada puntuación.
- La fecha en la que se realizaron las valoraciones.
- El perfil o procedencia de las personas que valoraron los vinos.
- Si todos los vinos fueron evaluados siguiendo los mismos criterios.
- Si las puntuaciones se han actualizado posteriormente.

Por ello, dos vinos con un `rating` similar pueden no disponer de la misma cantidad ni calidad de información. Una puntuación alta basada en pocas opiniones no tiene necesariamente la misma solidez que otra obtenida a partir de muchas valoraciones.

Además, las valoraciones reflejan preferencias subjetivas y pueden estar condicionadas por la popularidad, el precio, la disponibilidad o la mayor visibilidad de determinadas bodegas, regiones y variedades.

Por tanto, el `rating` debe entenderse como una señal orientativa y no como una medida objetiva o definitiva de la calidad del vino. La aplicación debería combinarlo con el resto de las preferencias del usuario y evitar presentar el vino mejor valorado como necesariamente el mejor para todas las personas.

### 3.6. Cobertura limitada del mercado

El dataset no contiene todos los vinos disponibles en España ni se actualiza automáticamente cuando aparecen nuevos productos o cambia la oferta comercial. Por tanto, InWine únicamente puede recomendar vinos incluidos en su catálogo.

Esto implica que:

- Un vino adecuado para el usuario puede no aparecer porque no forma parte del dataset.
- Pueden estar menos representadas las bodegas pequeñas, los vinos nuevos o los productos con pocas reseñas.
- La aplicación no garantiza que los vinos continúen disponibles en el mercado.
- Algunas añadas, precios y características pueden haber cambiado desde la recopilación de los datos.

Por ello, InWine recomienda opciones compatibles dentro del catálogo disponible y según las reglas definidas por el equipo. No puede garantizar que el resultado sea el mejor vino existente en todo el mercado español.

### 3.7. Vinos repetidos y distintas añadas

El catálogo puede contener registros con el mismo nombre comercial o pertenecientes a una misma bodega. En algunos casos pueden corresponder a distintas añadas, variedades, formatos o versiones del producto, por lo que no deben considerarse automáticamente duplicados.

Sin embargo, cuando varios registros son muy similares, una misma marca, bodega o familia de vinos puede adquirir mayor presencia dentro del dataset. Esto puede provocar que:

- Tenga más influencia en la formación de los clústeres.
- Aparezca con mayor frecuencia entre los candidatos recomendados.
- Se reduzca la diversidad percibida por el usuario.
- Algunas recomendaciones parezcan repetidas, aunque correspondan a registros diferentes.

Además, las distintas añadas de un mismo vino pueden presentar diferencias de precio, valoración o características. Por ello, no sería adecuado eliminarlas únicamente porque compartan nombre.

Para detectar duplicados reales sería necesario comparar conjuntamente varios campos, como el nombre, la bodega, la añada, la región, la variedad, el tipo y el precio. La coincidencia en un solo campo no es suficiente para concluir que dos registros representan exactamente el mismo producto.

Por tanto, la posible repetición de vinos debe considerarse una limitación relacionada con la diversidad y la representación del catálogo, pero su revisión requiere distinguir cuidadosamente entre duplicados reales y versiones legítimamente diferentes.

## 4. Sesgos y limitaciones del preprocesamiento

Las transformaciones aplicadas durante el preprocesamiento permiten convertir los datos originales en variables que puedan utilizar PCA y K-Means. Sin embargo, estas decisiones también simplifican la información y pueden influir en la formación de los clústeres y en las recomendaciones posteriores.

### 4.1. Agrupación de categorías minoritarias

Durante el preprocesamiento, algunas categorías con pocos registros se agrupan bajo una categoría común, como `Otros`. Esta decisión evita generar numerosas variables con muy pocos ejemplos y facilita el entrenamiento del modelo.

Sin embargo, esta agrupación puede provocar una pérdida de información. Regiones, variedades de uva, tipos de vino u otras categorías poco frecuentes pueden quedar representadas mediante el mismo valor, aunque tengan características muy diferentes.

Como consecuencia:

- Se reduce la capacidad del modelo para distinguir algunas categorías minoritarias.
- Vinos con características diferentes pueden recibir una representación similar.
- Las particularidades de regiones o variedades poco frecuentes pueden tener menos influencia en la formación de los clústeres.
- Las categorías mayoritarias conservan una representación más específica y pueden tener mayor peso en el modelo.

La categoría `Otros` no debe interpretarse como un grupo homogéneo ni como una indicación de menor calidad. Únicamente reúne categorías con poca representación para facilitar el procesamiento de los datos.

Por tanto, esta transformación mejora la estabilidad técnica del modelo, pero puede reducir la visibilidad y los matices de los vinos menos representados.

### 4.2. Target Encoding de la región y la variedad de uva

Las variables categóricas `region` y `grape_variety` se transforman mediante Target Encoding utilizando el precio medio de los vinos de cada categoría. Para reducir valores extremos y evitar depender únicamente de categorías con pocos registros, se aplica un suavizado con respecto al precio medio global del dataset.

Esta transformación permite representar cada región y variedad de uva mediante un único valor numérico, evitando generar una gran cantidad de columnas. Sin embargo, ese valor no describe directamente sus características geográficas, sensoriales o enológicas, sino su relación con el precio dentro del dataset.

Como consecuencia:

- Dos regiones o variedades con precios medios similares pueden recibir valores parecidos, aunque sus vinos tengan características muy diferentes.
- Las categorías asociadas a vinos más caros pueden adquirir una posición diferente en el modelo por motivos económicos y no necesariamente sensoriales.
- Los precios desactualizados o poco representativos pueden influir también en la codificación.
- Las categorías con pocos registros dependen en mayor medida del suavizado aplicado.
- Las diferencias económicas existentes en el dataset pueden trasladarse a la formación de los clústeres.

Este procedimiento no utiliza la variable que la aplicación intenta predecir, ya que InWine es un sistema de clustering no supervisado. En este caso, el precio se emplea como referencia para codificar estas variables antes de aplicar K-Means.

Por tanto, los valores obtenidos no deben interpretarse como una medida de la calidad, importancia o similitud real de una región o variedad. Son únicamente una representación numérica diseñada para que estas categorías puedan incorporarse al modelo.

### 4.3. Transformación del precio

El precio presenta una distribución desigual: la mayoría de los vinos se concentra en determinados rangos, mientras que existen algunos importes considerablemente más elevados.

Para reducir la influencia de estos valores altos durante el modelado, se aplica la transformación logarítmica `log1p`. Esta transformación comprime las diferencias entre los precios, especialmente en la parte más elevada de la distribución, y evita que unos pocos vinos caros condicionen excesivamente la formación de los clústeres.

Sin embargo, también modifica las distancias originales entre los precios. Por ejemplo, una diferencia de 50 euros no conserva el mismo peso después de la transformación que en los valores originales.

Como consecuencia:

- El modelo no trabaja directamente con el precio expresado en euros.
- Las diferencias entre los vinos más caros quedan reducidas.
- El precio continúa influyendo en los clústeres, pero de una forma transformada.
- La interpretación económica de la distancia entre dos vinos resulta menos directa.

Esta transformación resulta útil para evitar que los precios extremos dominen el agrupamiento, pero debe tenerse en cuenta al interpretar los perfiles obtenidos. El precio original se mantiene en el catálogo para mostrarlo al usuario y aplicar criterios como el presupuesto.

### 4.4. Escalado de las variables

Las 18 variables utilizadas durante el modelado presentan escalas y unidades diferentes. Algunas son variables binarias, otras proceden de codificaciones categóricas y otras representan valores como el `rating` o el precio transformado.

Antes de aplicar PCA y K-Means, estas variables se estandarizan mediante `StandardScaler`. Este proceso transforma cada variable tomando como referencia su media y su desviación estándar, evitando que aquellas con valores numéricos más elevados dominen automáticamente el cálculo de las distancias.

Sin embargo, el escalado no determina qué características son realmente más importantes para los gustos de los usuarios. Después de estandarizarlas, todas las variables pueden influir en el modelo, aunque su relevancia sensorial o enológica no sea equivalente.

Además:

- Una variable incluida en el modelo puede influir aunque tenga poca importancia para determinados usuarios.
- Las variables relacionadas entre sí pueden aportar información parcialmente repetida.
- Los valores extremos pueden afectar a la media y a la desviación estándar utilizadas para escalar.
- Si cambia la distribución de los nuevos datos, el escalado aprendido con el dataset original puede representar peor esos vinos.

Por tanto, el escalado mejora la comparabilidad técnica entre las variables, pero no garantiza que su influencia coincida exactamente con la importancia que cada persona concede a las distintas características de un vino.

### 4.5. Extracción de características sensoriales

Las variables sensoriales, como las notas frutales, florales, especiadas, de madera o minerales, no proceden de mediciones físicas ni de catas realizadas específicamente para este proyecto. Se obtienen automáticamente a partir de las descripciones de los vinos mediante la búsqueda de palabras clave asociadas a cada categoría.

Este método permite transformar textos no estructurados en variables numéricas que pueden incorporarse al modelo. Sin embargo, simplifica la riqueza y los matices del lenguaje utilizado para describir un vino.

Como consecuencia:

- Una característica puede no detectarse si se expresa con una palabra o sinónimo que no está incluido en el diccionario.
- Una palabra puede aparecer en la descripción sin representar realmente una característica predominante del vino.
- El método puede tener dificultades para interpretar negaciones, comparaciones, ambigüedades o expresiones figuradas.
- Las descripciones más largas o detalladas pueden generar más coincidencias que las breves.
- Los vinos sin descripción, o con una descripción poco completa, disponen de menos información sensorial.
- Las categorías definidas por el equipo condicionan qué características puede reconocer el sistema.

Además, las descripciones originales pueden reflejar la opinión subjetiva de críticos, bodegas o vendedores. Por tanto, las variables extraídas no representan una medición objetiva del sabor, sino una aproximación basada en el texto disponible y en las reglas definidas para interpretarlo.

Estas variables resultan útiles para identificar patrones generales, pero no garantizan que todos los usuarios perciban en el vino los mismos aromas, sabores o sensaciones.

### 4.6. Diferencia entre característica ausente e información desconocida

Cuando el sistema no detecta una característica sensorial en la descripción de un vino, la variable correspondiente recibe un valor de cero. Sin embargo, este valor puede representar situaciones diferentes:

- La característica realmente no está presente en el vino.
- La característica está presente, pero no se menciona en la descripción.
- Se expresa mediante una palabra que no está incluida en el diccionario.
- La descripción es demasiado breve o incompleta para detectarla.

El modelo trata todos estos casos del mismo modo, porque no dispone de un valor específico que permita distinguir entre ausencia real e información desconocida.

Como consecuencia, los vinos con descripciones poco detalladas pueden parecer sensorialmente más neutros o similares entre sí. Esto puede afectar tanto a la formación de los clústeres como a las recomendaciones que utilizan el perfil de sabor.

Por tanto, un valor de cero en estas variables debe interpretarse como “característica no detectada en el texto” y no necesariamente como “característica ausente en el vino”.

### 4.7. Eliminación de registros duplicados

El dataset original utilizado por InWine contenía 7.500 filas. Durante la exploración inicial se comprobó que 5.452 de ellas, el 72,7 %, eran copias exactas de otros registros.

Estos duplicados coincidían en todas las columnas originales, incluyendo la bodega, el nombre del vino, la añada, el `rating`, el número de valoraciones, la región, el precio y el tipo. Por ejemplo, el vino `Contino - Reserva - 2016` aparecía repetido 220 veces con exactamente los mismos valores.

Por este motivo, la deduplicación se realizó antes del resto de las transformaciones. Tras eliminar las copias exactas, el dataset pasó de 7.500 a 2.048 vinos únicos.

Este paso era necesario porque, si se hubieran mantenido los duplicados:

- Algunos vinos habrían tenido mucha más influencia que otros en los cálculos y en la formación de los clústeres.
- Las bodegas, regiones, tipos de vino y variedades asociadas a esos registros habrían quedado sobrerrepresentadas.
- Los porcentajes, medias y demás estadísticas del análisis no habrían reflejado correctamente la composición del catálogo.
- La aplicación podría haber mostrado repetidamente el mismo producto en sus recomendaciones.
- El proceso de enriquecimiento de datos habría podido repetirse innecesariamente sobre un mismo vino.

Posteriormente se eliminaron las columnas `num_reviews`, `country`, `body` y `acidity`, porque no formaban parte de las variables utilizadas por el modelo. Al retirar estas columnas, algunos registros que antes presentaban alguna diferencia pasaron a ser idénticos dentro del catálogo final. Por ello, se realizó una segunda deduplicación, en la que se eliminaron otros 24 registros.

Finalmente, el dataset limpio quedó formado por 2.024 registros sin duplicados.

En este caso, la importante reducción del número de filas no significa que se eliminara una proporción equivalente de vinos diferentes. La mayor parte de los registros retirados eran copias exactas que ya estaban representadas en el dataset. La deduplicación permitió evitar que esas repeticiones alteraran el análisis, el clustering y las recomendaciones de InWine.

### 4.8. Reproducibilidad del pipeline y MLOps

InWine incorpora un pipeline reutilizable para aplicar a vinos nuevos las mismas transformaciones y modelos utilizados durante el entrenamiento.

El proceso parte de dos archivos generados previamente por los notebooks:

- `data/processed/wines_SPA_model_ready.csv`, que contiene los vinos preprocesados y las 18 variables escaladas utilizadas por K-Means y PCA.
- `preprocessing/preprocessing_objects.pkl`, generado por `03_preprocessing.ipynb`, que contiene el `StandardScaler`, los mapas de precios por región y variedad de uva y la lista ordenada de variables del modelo.

El script `src/train_pipeline.py` carga estos archivos y entrena:

- Un modelo K-Means con ocho clústeres, `random_state=42` y `n_init=10`.
- Un modelo PCA con dos componentes principales.

A continuación, guarda en `models/inwine_pipeline.joblib` un diccionario con estos ocho elementos:

- `scaler`: el `StandardScaler` entrenado en el notebook.
- `region_price_map`: el mapa utilizado para codificar las regiones.
- `grape_price_map`: el mapa utilizado para codificar las variedades de uva.
- `model_features`: las variables originales y su orden.
- `kmeans`: el modelo K-Means entrenado.
- `pca`: el modelo PCA entrenado.
- `feature_columns`: las 18 columnas escaladas y su orden.
- `k`: el número de clústeres, fijado en ocho.

El script `src/predict_pipeline.py` carga este artefacto para procesar vinos nuevos. Aplica la transformación logarítmica del precio, la extracción de las cinco familias sensoriales, la transformación de la temperatura de servicio, la codificación de región, uva y tipo de vino y el escalado de las variables.

Después utiliza:

- `scaler.transform()` para escalar el vino con los parámetros aprendidos durante el entrenamiento.
- `kmeans.predict()` para asignarle uno de los ocho `cluster_id`.
- `pca.transform()` para calcular sus coordenadas `PC1` y `PC2`.

Durante este proceso no se vuelve a ejecutar `fit()`. Por tanto, añadir un vino no modifica la media ni la desviación estándar del escalador, los centroides de K-Means ni las componentes aprendidas por PCA.

La aplicación web tampoco ejecuta el modelo cada vez que un usuario solicita una recomendación. El nuevo vino se procesa previamente y su `cluster_id` se incorpora al archivo `data/processed/wines_SPA_enriched.csv`. La aplicación carga este catálogo y utiliza el clúster ya asignado.

La reproducibilidad del clustering se refuerza mediante `random_state=42`. Sin embargo, el artefacto `inwine_pipeline.joblib` no guarda actualmente metadatos como la fecha de entrenamiento, la versión del dataset, el commit de Git utilizado, las versiones exactas de las dependencias o métricas de seguimiento. Además, `requirements.txt` establece versiones mínimas mediante `>=`, pero no fija versiones exactas.

Por tanto, el repositorio permite reutilizar el mismo pipeline sin reentrenar al incorporar cada vino, pero todavía no dispone de un sistema completo de versionado y trazabilidad de los experimentos y artefactos.

## 5. Limitaciones de PCA y K-Means

InWine utiliza PCA y K-Means con objetivos diferentes. Ambos modelos se entrenan en `src/train_pipeline.py` utilizando las mismas 18 variables escaladas de `data/processed/wines_SPA_model_ready.csv`.

PCA crea una representación bidimensional de los vinos, mientras que K-Means realiza la agrupación en ocho clústeres. Por tanto, las limitaciones de PCA afectan principalmente a la visualización y no a la asignación del `cluster_id`.

### 5.1. Reducción de información mediante PCA

El pipeline de InWine entrena `PCA(n_components=2)` sobre las 18 variables escaladas y obtiene dos componentes principales: `PC1` y `PC2`.

Estas dos componentes conservan conjuntamente el 48,83 % de la varianza del dataset. Esto significa que la representación bidimensional utilizada en los gráficos resume aproximadamente la mitad de la variabilidad contenida en las 18 variables, mientras que el 51,17 % restante no aparece representado en ese plano.

Por este motivo:

- La posición de un vino en el gráfico depende de una combinación de las 18 variables originales.
- Dos vinos próximos en el plano formado por `PC1` y `PC2` pueden presentar diferencias en información que no ha quedado reflejada en esas dos componentes.
- Dos vinos visualmente alejados no tienen por qué ser completamente incompatibles.
- El gráfico permite observar patrones generales, pero no representa todas las características de cada vino.
- `PC1` y `PC2` no deben interpretarse como puntuaciones de calidad ni como características concretas del vino.

En InWine, K-Means no se entrena utilizando únicamente `PC1` y `PC2`. El modelo se ajusta directamente sobre las 18 variables escaladas originales. Por tanto, la pérdida de información de esta reducción a dos dimensiones afecta a la representación visual, pero no determina la formación de los ocho clústeres.

Además, aunque el pipeline puede calcular las coordenadas `PC1` y `PC2` de un vino mediante `pca.transform()`, la aplicación utiliza principalmente su `cluster_id` para mostrar perfiles y generar alternativas.

### 5.2. Papel de PCA en el agrupamiento

En InWine, PCA y K-Means se entrenan sobre las mismas 18 variables escaladas, pero funcionan de manera independiente.

En `src/train_pipeline.py`, K-Means recibe directamente la matriz formada por esas 18 variables:

- No utiliza `PC1` y `PC2` para crear los clústeres.
- No utiliza las coordenadas generadas por PCA para calcular los centroides.
- La varianza conservada por PCA no interviene en la asignación del `cluster_id`.
- Modificar el número de componentes de PCA no cambiaría los clústeres mientras K-Means continúe entrenándose con las 18 variables escaladas.

El modelo PCA se utiliza para reducir las 18 variables a dos dimensiones y facilitar la representación gráfica de los vinos y los clústeres. K-Means, en cambio, utiliza toda la información incluida en las variables escaladas para distribuir los 2.024 vinos entre ocho grupos.

Por tanto, el gráfico formado por `PC1` y `PC2` es una proyección de los clústeres ya calculados en un espacio de 18 dimensiones. Como las dos componentes conservan el 48,83 % de la varianza, el gráfico no puede mostrar completamente las distancias que K-Means tuvo en cuenta.

Esto explica que en la representación bidimensional:

- Algunos vinos pertenecientes al mismo clúster puedan aparecer separados.
- Puntos de clústeres diferentes puedan verse próximos o parcialmente superpuestos.
- Los ocho grupos no tengan que aparecer como zonas completamente separadas.
- La forma observada en el gráfico no coincida exactamente con la distribución utilizada por K-Means.

Esta superposición visual no significa necesariamente que K-Means haya asignado incorrectamente los vinos. Indica que parte de la información utilizada para agruparlos se encuentra en dimensiones que no aparecen en el plano formado por `PC1` y `PC2`.

En la aplicación, las coordenadas de PCA no se utilizan para recomendar directamente un vino. La información operativa es el `cluster_id` asignado por K-Means, mientras que `PC1` y `PC2` se conservan como apoyo para analizar y visualizar la distribución del catálogo.

### 5.3. Selección de ocho clústeres

En `notebooks/04_clustering.ipynb`, InWine prueba configuraciones de K-Means desde `k=2` hasta `k=10`. Todos los modelos se entrenan con las 18 variables escaladas, utilizando `random_state=42` y `n_init=10`.

Para comparar las configuraciones se calculan dos métricas:

- La inercia, que mide la compactación interna de los clústeres.
- El Silhouette Score, que valora conjuntamente la cohesión de cada clúster y su separación respecto a los demás.

Los resultados obtenidos fueron:

| Número de clústeres | Inercia | Silhouette Score |
|---:|---:|---:|
| 2 | 19.581,16 | 0,4872 |
| 3 | 16.698,51 | 0,2239 |
| 4 | 14.236,37 | 0,2419 |
| 5 | 12.009,17 | 0,2690 |
| 6 | 10.602,50 | 0,2745 |
| 7 | 9.106,71 | 0,3442 |
| 8 | 6.946,11 | 0,3697 |
| 9 | 6.304,85 | 0,3670 |
| 10 | 5.840,58 | 0,3575 |

El valor más alto de Silhouette Score corresponde a `k=2`, con `0,4872`. Sin embargo, esta opción únicamente dividiría los 2.024 vinos en dos grupos muy amplios y no permitiría construir una segmentación suficientemente detallada para las recomendaciones de InWine.

Entre las alternativas con más grupos, `k=8` obtiene el mejor Silhouette Score, con `0,3697`. A partir de ese punto, aumentar el número de clústeres no mejora el resultado:

- Con `k=9`, el Silhouette Score baja a `0,3670`.
- Con `k=10`, desciende nuevamente hasta `0,3575`.
- La reducción de la inercia también se hace mucho menor después de `k=8`.

Por este motivo se seleccionó `k=8`: representa un equilibrio entre la separación estadística de los grupos y la necesidad de obtener perfiles comerciales diferenciados.

Los ocho clústeres obtenidos se caracterizaron posteriormente según el tipo de vino, el precio, el `rating`, la crianza y las regiones dominantes. A partir de sus características reales se asignaron manualmente los siguientes nombres:

1. Iconos de Guarda.
2. Blancos Selectos.
3. Tintos Jóvenes de Autor.
4. Vinos Singulares.
5. Generosos y Jerez.
6. Espumosos Premium.
7. Tintos Crianza Clásicos.
8. Tintos Jóvenes Premium.

Por tanto, `k=8` no se eligió porque fuera el valor con el Silhouette Score más alto de toda la prueba. Se eligió porque ofrecía el mejor resultado entre las configuraciones que permitían disponer de una segmentación más detallada y útil para el funcionamiento de InWine.

La elección también se validó repitiendo K-Means con las semillas `0`, `1`, `42`, `123` y `2024`. Las diez comparaciones entre sus resultados obtuvieron un Adjusted Rand Index de `1,0`, lo que indica que los 2.024 vinos recibieron agrupaciones equivalentes en las cinco ejecuciones.

### 5.4. Diferencias de tamaño entre clústeres

Los ocho clústeres creados por K-Means no contienen el mismo número de vinos. En `app/data/clusters.py` se registra la siguiente distribución:

| `cluster_id` | Perfil | Número de vinos | Porcentaje del catálogo |
|---:|---|---:|---:|
| 0 | Iconos de Guarda | 315 | 15,56 % |
| 1 | Blancos Selectos | 137 | 6,77 % |
| 2 | Tintos Jóvenes de Autor | 288 | 14,23 % |
| 3 | Vinos Singulares | 65 | 3,21 % |
| 4 | Generosos y Jerez | 90 | 4,45 % |
| 5 | Espumosos Premium | 38 | 1,88 % |
| 6 | Tintos Crianza Clásicos | 333 | 16,45 % |
| 7 | Tintos Jóvenes Premium | 758 | 37,45 % |

El perfil más numeroso es `Tintos Jóvenes Premium`, con 758 vinos, mientras que `Espumosos Premium` contiene únicamente 38. Por tanto, el clúster más grande tiene casi veinte veces más registros que el más pequeño.

Esta diferencia está relacionada con la composición del catálogo. Los clústeres 0, 2, 6 y 7 están dominados por vinos tintos y reúnen conjuntamente 1.694 de los 2.024 vinos, es decir, el 83,70 % del dataset. En cambio, los perfiles correspondientes a blancos, generosos y espumosos disponen de muchos menos registros.

Esta distribución influye directamente en las opciones disponibles en la aplicación:

- `Tintos Jóvenes Premium` ofrece un conjunto mucho mayor de vinos entre los que aplicar restricciones de precio u otros criterios.
- `Espumosos Premium`, `Vinos Singulares` y `Generosos y Jerez` disponen de menos alternativas.
- Al excluir recomendaciones ya mostradas, los clústeres pequeños pueden agotar antes sus candidatos compatibles.
- En el quiz, un usuario asignado a un clúster pequeño tiene menos posibilidades de encontrar cuatro vinos de su perfil que además cumplan su presupuesto.
- Cuando no existen suficientes candidatos del clúster asignado, la aplicación completa los resultados con vinos pertenecientes a otros clústeres.

K-Means no incorpora ninguna condición para equilibrar el número de vinos de los grupos. Su objetivo es asignar cada registro al centroide más cercano según las 18 variables escaladas. Por ello, esta diferencia de tamaño no constituye un error de ejecución, pero sí afecta a la variedad de recomendaciones que puede ofrecer cada perfil.

En InWine, los ocho perfiles no tienen la misma cobertura dentro del catálogo: los usuarios asociados a perfiles dominados por vinos tintos disponen de muchas más alternativas que quienes obtienen perfiles minoritarios, especialmente `Espumosos Premium`.

### 5.5. Influencia de las variables utilizadas

K-Means crea los ocho clústeres de InWine utilizando las 18 variables escaladas de `data/processed/wines_SPA_model_ready.csv`.

Estas variables incluyen información sobre:

- La valoración del vino.
- El precio y su relación con la calidad.
- La crianza.
- La región y la variedad de uva.
- La temperatura de servicio.
- Las cinco familias sensoriales.
- El tipo de vino.

Antes de entrenar K-Means, todas las variables se estandarizan mediante `StandardScaler`. De esta forma, las diferencias entre sus escalas originales no provocan que una variable domine el cálculo de las distancias únicamente por contener valores numéricos más elevados.

La selección realizada permite que los clústeres reflejen diferentes dimensiones del catálogo. Por ejemplo:

- Las columnas correspondientes al tipo de vino permiten diferenciar perfiles como `Blancos Selectos`, `Generosos y Jerez` y `Espumosos Premium`.
- Las variables relacionadas con el precio contribuyen a distinguir perfiles con niveles económicos diferentes.
- Las familias sensoriales incorporan información sobre los sabores y aromas identificados en la descripción de cada vino.
- La crianza, la región y la uva ayudan a diferenciar vinos que pueden compartir tipo o precio, pero presentan otras características distintas.

En el modelo, la información económica aparece representada mediante `price_log`, `luxury_category`, `quality_price_ratio`, `region_encoded` y `grape_variety_encoded`. Estas variables no contienen exactamente la misma información, ya que representan respectivamente el precio transformado, la categoría económica, la relación entre puntuación y precio y los precios medios asociados a cada región y variedad.

Sin embargo, su presencia conjunta hace que el componente económico tenga una influencia relevante en la segmentación. Esto se observa en las diferencias de precio entre perfiles como `Iconos de Guarda`, con un precio medio de 540,92 euros, y `Vinos Singulares`, con 33,53 euros.

Esta configuración es coherente con el objetivo de InWine, ya que el precio es una característica importante para diferenciar y recomendar productos. No obstante, los clústeres obtenidos representan necesariamente la selección concreta de variables utilizada por el equipo.

El repositorio no incluye actualmente una comparación del clustering eliminando diferentes grupos de variables. Como mejora futura, podría estudiarse cómo cambia la segmentación al utilizar únicamente variables sensoriales, retirar algunas variables económicas o asignar más importancia a las preferencias relacionadas con el sabor. Esta comparación permitiría comprobar qué combinación genera los perfiles más útiles para las recomendaciones.

### 5.6. Tratamiento de los valores extremos

K-Means asigna los vinos de InWine al centroide más próximo utilizando las 18 variables escaladas. Por ello, los valores especialmente alejados de la distribución habitual pueden influir en las distancias utilizadas para crear los clústeres.

El precio es la variable que presenta las diferencias más amplias dentro del catálogo. Para reducir su efecto, el preprocesamiento no utiliza directamente `price_euros`, sino que crea:

`price_log = log1p(price_euros)`

La transformación logarítmica reduce la distancia numérica entre los vinos de precio habitual y los vinos de varios cientos de euros. Esto permite conservar la información económica sin que los importes más elevados tengan la misma influencia que tendrían utilizando el precio original.

Después, las 18 variables se estandarizan mediante `StandardScaler`. Este paso sitúa las variables en una escala comparable antes de entrenar K-Means y evita que una característica influya más solamente por utilizar unidades o rangos numéricos mayores.

Estas decisiones son adecuadas para el dataset de InWine y permiten que el precio forme parte de la segmentación de una manera más controlada. Aun así, algunos vinos presentan características muy diferentes de las del resto del catálogo y pueden quedar alejados de los centroides obtenidos.

Esta situación no impide el funcionamiento del modelo: K-Means siempre asigna cada vino al clúster cuyo centroide se encuentra más próximo. Por tanto, el `cluster_id` indica cuál es el perfil más cercano entre los ocho disponibles, pero no mide por sí mismo el grado de proximidad del vino a dicho perfil.

Como posible evolución del pipeline, podría calcularse la distancia de cada vino a su centroide. Esta información permitiría identificar productos especialmente atípicos y analizar individualmente si su asignación representa correctamente sus características.

En conclusión, InWine ya reduce el efecto de los precios extremos mediante `log1p` y aplica el mismo escalado a todas las variables. El control de la distancia a los centroides sería una mejora adicional para analizar casos poco habituales, no un requisito para el funcionamiento actual del clustering.

### 5.7. Interpretación y nombres de los perfiles

K-Means crea los ocho clústeres utilizando las características de los 2.024 vinos, pero no les asigna automáticamente un significado comercial ni un nombre.

Después de entrenar el modelo, el equipo analizó cada clúster mediante variables como:

- El tipo de vino predominante.
- El precio medio.
- El `rating`.
- La crianza.
- Las regiones y variedades de uva más frecuentes.
- Las familias sensoriales.

A partir de las características predominantes, los ocho grupos recibieron manualmente los siguientes nombres:

| `cluster_id` | Nombre del perfil |
|---:|---|
| 0 | Iconos de Guarda |
| 1 | Blancos Selectos |
| 2 | Tintos Jóvenes de Autor |
| 3 | Vinos Singulares |
| 4 | Generosos y Jerez |
| 5 | Espumosos Premium |
| 6 | Tintos Crianza Clásicos |
| 7 | Tintos Jóvenes Premium |

Estos nombres permiten presentar los resultados del modelo de una forma comprensible para los usuarios de la aplicación. En lugar de mostrar únicamente un número de clúster, InWine utiliza una denominación que resume las características principales del grupo.

Los nombres deben interpretarse como descripciones orientativas. Un clúster agrupa vinos próximos según las 18 variables utilizadas por K-Means, pero no todos sus integrantes presentan cada característica con la misma intensidad. Por ejemplo, pertenecer a `Iconos de Guarda` indica que el vino está incluido en el perfil identificado con ese nombre, pero no constituye por sí mismo una clasificación enológica oficial.

La interpretación humana es adecuada para trasladar el resultado matemático del modelo a la aplicación. Si en el futuro se modifica el dataset, el conjunto de variables o el número de clústeres, será necesario revisar las características de los nuevos grupos antes de mantener o modificar estos nombres.

### 5.8. Similitud dentro de un mismo clúster

K-Means asigna cada vino de InWine al clúster cuyo centroide se encuentra más próximo, teniendo en cuenta conjuntamente las 18 variables escaladas.

Por tanto, los vinos que pertenecen al mismo clúster comparten un perfil general, pero no tienen que ser idénticos en todas sus características. Dentro de un mismo grupo pueden existir diferencias de precio, `rating`, región, variedad de uva, crianza o perfil sensorial.

Esta diversidad es coherente con el objetivo de InWine. Los clústeres no representan categorías cerradas, sino conjuntos de vinos que presentan una combinación de características similar. Así, dos vinos pueden pertenecer al mismo perfil aunque uno destaque más por su precio y otro por su crianza o sus características sensoriales.

Además, el tamaño de los clústeres influye en su variedad interna. Por ejemplo, `Tintos Jóvenes Premium` contiene 758 vinos, por lo que reúne un catálogo más amplio y diverso que `Espumosos Premium`, formado por 38 vinos.

En la aplicación, el `cluster_id` se utiliza como punto de partida para identificar vinos pertenecientes al mismo perfil. Después se aplican otros criterios, como el presupuesto indicado por el usuario, para seleccionar las recomendaciones más adecuadas dentro de los candidatos disponibles.

Por tanto, compartir un clúster significa que dos vinos pertenecen al mismo perfil general según el modelo, no que sean equivalentes ni que tengan exactamente las mismas características. Esta variedad permite que InWine ofrezca distintas alternativas dentro de una recomendación coherente.

### 5.9. Validación con preferencias reales de usuarios

Los clústeres de InWine se han creado a partir de las características de los vinos, como el precio, el tipo, la crianza, la región, la uva y el perfil sensorial. No se han utilizado historiales de compras ni valoraciones personales para entrenar el modelo.

Esta decisión permite organizar el catálogo sin recopilar datos personales y resulta adecuada para una primera versión de la aplicación. Sin embargo, la similitud entre las características de dos vinos no garantiza que todos los usuarios perciban esa similitud de la misma manera o disfruten de ambos por igual.

Por ahora, la utilidad de los perfiles se ha evaluado mediante el análisis de sus características y su coherencia dentro de la aplicación. Como mejora futura, podrían incorporarse valoraciones voluntarias y anónimas para conocer si las recomendaciones se ajustan a los gustos de los usuarios.

Esta información permitiría comprobar la utilidad real de los perfiles y mejorar progresivamente las recomendaciones, siempre informando de forma clara sobre el uso de los datos recopilados.

## 6. Sesgos y limitaciones de las vías de recomendación

InWine permite obtener recomendaciones mediante distintas vías de interacción. Cada una utiliza información diferente: las respuestas del cuestionario, las características de un vino seleccionado o los filtros y preferencias indicados por el usuario.

Estas vías facilitan la búsqueda dentro de un catálogo amplio, pero sus resultados dependen tanto de la información proporcionada como de la disponibilidad de vinos compatibles. Por ello, las recomendaciones deben entenderse como propuestas personalizadas dentro del catálogo de InWine, no como una valoración definitiva sobre cuál es el mejor vino para cada persona.

### 6.1. Recomendador mediante formulario

El formulario filtra el catálogo según las preferencias indicadas por el usuario. El presupuesto y el tipo de vino actúan como criterios principales, mientras que otros elementos, como la región, la variedad de uva o el perfil sensorial, se aplican de forma flexible.

Esta flexibilidad evita que una combinación muy concreta deje al usuario sin ninguna recomendación. Cuando un filtro no encuentra coincidencias, la aplicación mantiene los candidatos obtenidos anteriormente y continúa la búsqueda con el resto de los criterios.

Una vez seleccionados los vinos compatibles, se priorizan los que tienen un `rating` más elevado. Esta decisión permite destacar opciones bien valoradas, aunque también hace que determinados vinos aparezcan con mayor frecuencia que otros con una puntuación algo inferior.

La ocasión seleccionada se utiliza principalmente para adaptar la explicación de la recomendación. Por ello, sería conveniente que la aplicación diferenciara claramente entre las preferencias que participaron directamente en la selección y las utilizadas para personalizar el mensaje.

En futuras versiones podría mostrarse un aviso cuando no haya sido posible respetar algún criterio. De esta forma, el usuario sabría qué preferencias se han cumplido y cuáles se han flexibilizado para poder ofrecerle una alternativa.

### 6.2. Quiz de perfil

El quiz asigna al usuario uno de los ocho perfiles de InWine mediante reglas definidas por el equipo. Cada respuesta aporta votos a determinados clústeres y el perfil con más votos se utiliza como resultado final.

Este sistema es comprensible, reproducible y permite relacionar las respuestas del usuario con los perfiles creados por K-Means. Sin embargo, las asociaciones entre las respuestas y los clústeres no han sido aprendidas a partir del comportamiento real de los usuarios, sino diseñadas a partir de la interpretación de los perfiles.

Una vez obtenido el resultado, la aplicación busca vinos pertenecientes al clúster asignado y compatibles con el presupuesto indicado. Si no existen cuatro candidatos adecuados, completa las opciones con vinos de otros clústeres.

Esta estrategia permite que el usuario reciba siempre varias recomendaciones, aunque los perfiles pequeños disponen de menos alternativas que los más numerosos. Por ello, no todos los vinos mostrados tienen que pertenecer necesariamente al clúster obtenido en el quiz.

Como mejora futura, podrían revisarse las reglas del cuestionario utilizando pruebas con usuarios reales. Esto permitiría comprobar si las personas se identifican con el perfil recibido y si las recomendaciones se ajustan a sus preferencias.

### 6.3. Recomendación conversacional

La recomendación conversacional permite expresar las preferencias de una forma más libre. El sistema interpreta la petición y combina criterios como el presupuesto, el tipo de vino, la crianza, el maridaje, el `rating` y la relación calidad-precio.

Esta vía ofrece una experiencia más flexible que un formulario cerrado, aunque su resultado depende de que la petición contenga información suficiente y pueda relacionarse con las variables disponibles en el catálogo.

El sistema utiliza una puntuación que combina la compatibilidad con las preferencias y la relación calidad-precio. Esta lógica es específica de la recomendación conversacional y no se utiliza necesariamente de la misma manera en el formulario o en el quiz.

La relación calidad-precio resulta útil para comparar distintas alternativas, pero debe entenderse como un criterio definido dentro de InWine. Depende del `rating`, del precio almacenado y de la fórmula utilizada, por lo que no representa una medida objetiva y universal de la calidad de un vino.

Cuando una petición sea ambigua o incluya características que no se encuentran en los datos, una posible mejora sería solicitar información adicional antes de generar la recomendación.

### 6.4. Solicitud de otra opción

El usuario puede pedir una alternativa cuando la primera propuesta no le convence. En ese caso, la aplicación excluye los vinos mostrados anteriormente para evitar repeticiones.

Esta funcionalidad:

- Aumenta el control del usuario.
- Favorece la variedad de las recomendaciones.
- Permite descubrir vinos que inicialmente no ocupaban la primera posición.
- Reduce la repetición continua de los productos mejor valorados.

La aplicación intenta conservar el perfil y los criterios de la recomendación anterior. No obstante, si quedan pocos candidatos compatibles, puede ser necesario flexibilizar alguna preferencia.

Esta función mejora la diversidad dentro de las opciones disponibles, aunque su alcance depende del número de vinos existentes en cada categoría o clúster.

### 6.5. Función de vinos similares

La función de vinos similares selecciona productos pertenecientes al mismo clúster que el vino de referencia y excluye el propio vino consultado.

Este sistema permite descubrir alternativas con un perfil general parecido. Sin embargo, actualmente los resultados no se ordenan calculando la distancia exacta entre el vino seleccionado y los demás vinos del grupo.

Por tanto, la expresión más precisa es que la aplicación muestra vinos pertenecientes al mismo perfil, no necesariamente los vinos matemáticamente más próximos.

Como evolución futura, podría calcularse la distancia entre los vinos utilizando sus variables escaladas. Esto permitiría ordenar las alternativas según su similitud y combinar esa distancia con otros criterios, como el presupuesto, el tipo de vino o la diversidad de regiones y bodegas.

### 6.6. Disponibilidad y variedad de candidatos

La cantidad de vinos disponibles influye en la variedad de recomendaciones que puede ofrecer cada función.

Los perfiles con más registros disponen de un conjunto mayor de candidatos entre los que aplicar filtros de precio, tipo o región. Los perfiles minoritarios pueden agotar antes sus alternativas y necesitar recurrir con mayor frecuencia a vinos pertenecientes a otros grupos.

Además, cuando varios vinos cumplen las mismas condiciones y no se aplica una ordenación adicional, su posición en el catálogo puede influir en cuáles aparecen primero.

Para aumentar la variedad podrían incorporarse criterios que eviten repetir en exceso las mismas bodegas, regiones o variedades, o realizar una selección controlada entre candidatos con un nivel de compatibilidad similar.

### 6.7. Explicaciones de las recomendaciones

InWine acompaña las recomendaciones con explicaciones para que el usuario comprenda las características del vino y su posible relación con las preferencias indicadas.

Esta funcionalidad mejora la accesibilidad de la aplicación, especialmente para personas que no tienen conocimientos especializados sobre vinos.

Para mantener la transparencia, la explicación debería reflejar los criterios que realmente participaron en la selección. También sería útil indicar cuándo una preferencia se utilizó únicamente para adaptar el mensaje o tuvo que flexibilizarse por falta de candidatos.

De esta manera, el usuario podría comprender no solo por qué se propone un vino, sino también qué condiciones se han cumplido completamente y cuáles solo de forma aproximada.

### 6.8. Evaluación de las recomendaciones

El análisis del dataset permite identificar posibles desequilibrios, pero no indica por sí solo con qué frecuencia aparece cada vino en el funcionamiento real de la aplicación.

Para evaluar el sistema de una forma más completa, podrían ejecutarse consultas controladas y medir:

- La frecuencia de recomendación de cada tipo de vino.
- La representación de regiones, denominaciones de origen y variedades de uva.
- La distribución de precios de los vinos mostrados.
- La frecuencia con la que el quiz necesita utilizar otros clústeres.
- El número de ocasiones en las que se flexibiliza algún filtro.
- La repetición de vinos, bodegas o perfiles.
- La diversidad de las alternativas ofrecidas.

Estas pruebas permitirían comprobar el comportamiento real de las tres vías y detectar posibles diferencias entre el catálogo disponible y las recomendaciones finalmente generadas.

## 7. Medidas incorporadas en InWine

InWine incluye distintas decisiones que favorecen la diversidad, la transparencia y la coherencia técnica de sus recomendaciones. Estas medidas no eliminan todas las limitaciones, pero contribuyen a reducir algunos de sus efectos.

### 7.1. Participación y control del usuario

El usuario puede comparar varias opciones, rechazar una propuesta y solicitar una alternativa. La aplicación excluye los vinos mostrados anteriormente para evitar repeticiones.

La recomendación no obliga a tomar ninguna decisión ni produce consecuencias de alto impacto. La elección final corresponde siempre a la persona, que puede valorar aspectos que la aplicación no conoce, como sus experiencias anteriores, la disponibilidad comercial o preferencias más concretas.

### 7.2. Flexibilidad de los filtros

Algunos filtros se aplican de forma flexible para evitar que una combinación muy específica deje al usuario sin resultados.

Esta decisión mejora la utilidad de la aplicación y permite ofrecer una alternativa incluso cuando el catálogo no contiene una coincidencia exacta. Para reforzar la transparencia, sería conveniente informar al usuario cuando se haya flexibilizado alguna preferencia.

### 7.3. Combinación de distintos criterios

Dependiendo de la vía seleccionada, InWine puede considerar elementos como:

- El presupuesto.
- El tipo de vino.
- La región.
- La variedad de uva.
- El maridaje.
- El perfil sensorial.
- La crianza.
- El `rating`.
- La relación calidad-precio.
- La pertenencia a un clúster.

La combinación de diferentes criterios evita que todas las recomendaciones dependan de una única característica. Cada vía los utiliza de una forma distinta para adaptarse al tipo de interacción elegido por el usuario.

### 7.4. Exploración de diferentes perfiles

La aplicación permite consultar los ocho perfiles y descubrir vinos incluidos en cada uno de ellos.

Esta funcionalidad presenta los clústeres como herramientas de exploración y permite conocer opciones diferentes a la recomendación inicial. Los perfiles ayudan a organizar el catálogo, pero no se presentan como clasificaciones rígidas ni como la única forma posible de describir los gustos de una persona.

### 7.5. Reproducibilidad del pipeline

InWine guarda en un único artefacto los principales objetos entrenados: `StandardScaler`, K-Means, PCA, las columnas utilizadas y los elementos necesarios para reproducir las transformaciones.

El script de predicción carga este artefacto y aplica a los vinos nuevos el mismo procesamiento utilizado durante el entrenamiento. Esto permite reutilizar el modelo sin volver a entrenarlo con cada predicción y evita diferencias accidentales en el orden o tratamiento de las variables.

Además, K-Means utiliza una semilla fija y se comprobó su estabilidad con distintas semillas. En las ejecuciones realizadas, las comparaciones obtuvieron un Adjusted Rand Index de `1,0`, lo que indica que las agrupaciones fueron equivalentes.

Estas decisiones proporcionan una base técnica reproducible y estable para la versión actual de la aplicación.

### 7.6. Documentación del funcionamiento y sus límites

La elaboración de este análisis permite diferenciar claramente entre:

- Los resultados observados en los datos.
- Las decisiones tomadas por el equipo.
- Las limitaciones de la versión actual.
- Las posibles mejoras para futuras versiones.

Documentar estos aspectos evita atribuir al sistema capacidades que no tiene y facilita que sus resultados se interpreten correctamente.

## 8. Propuestas de mejora

Las siguientes propuestas representan posibles líneas de evolución para futuras versiones de InWine. No son requisitos pendientes para que la aplicación actual funcione, sino oportunidades para ampliar su alcance y mejorar progresivamente las recomendaciones.

### 8.1. Ampliar la diversidad del catálogo

Una de las mejoras principales sería incorporar más vinos pertenecientes a los grupos menos representados, especialmente:

- Vinos blancos, rosados y espumosos.
- Regiones y denominaciones de origen minoritarias.
- Variedades de uva menos frecuentes.
- Bodegas pequeñas o con menor presencia en plataformas de reseñas.
- Vinos pertenecientes a diferentes rangos de precio.

El objetivo no tendría que ser igualar artificialmente todas las categorías, sino conseguir un catálogo suficientemente variado para ofrecer alternativas relevantes a distintos perfiles de usuario.

También podría compararse la distribución del dataset con fuentes oficiales del sector para conocer mejor su grado de representatividad.

### 8.2. Completar la información sobre las valoraciones

Además del `rating`, sería útil disponer de información como:

- El número de valoraciones recibidas.
- La fuente de la puntuación.
- La fecha de actualización.
- La diferenciación entre opiniones de usuarios y valoraciones de especialistas.

Estos datos permitirían interpretar mejor la fiabilidad de cada puntuación y evitarían tratar de la misma forma un `rating` basado en pocas opiniones y otro respaldado por un número elevado de reseñas.

También podría utilizarse una puntuación ajustada que combine la valoración media con el número de opiniones.

### 8.3. Actualizar precios y disponibilidad

Los precios pueden cambiar según la tienda, la añada o el momento de la consulta. Por ello, podrían revisarse periódicamente o conectarse en el futuro con fuentes comerciales actualizadas.

La aplicación también podría mostrar:

- La fecha de actualización del precio.
- Un intervalo aproximado en lugar de un importe exacto.
- Un aviso indicando que el valor puede variar.
- Información reciente sobre la disponibilidad del producto.

Esto ayudaría a mantener la utilidad del presupuesto como criterio de recomendación.

### 8.4. Mejorar las variables sensoriales

Las familias sensoriales actuales permiten transformar las descripciones de los vinos en variables numéricas mediante la identificación de términos asociados a distintos sabores y aromas.

En futuras versiones podría ampliarse este proceso mediante:

- Diccionarios más completos.
- Incorporación de sinónimos.
- Reconocimiento de distintas formas de una misma palabra.
- Interpretación del contexto y de las negaciones.
- Revisión manual de una muestra de resultados.
- Técnicas de procesamiento del lenguaje adaptadas al vocabulario enológico.

También podría diferenciarse entre una característica realmente ausente y una característica desconocida porque la descripción no aporta información suficiente.

### 8.5. Revisar las variedades agrupadas

La categoría `Blend/Other` reúne variedades minoritarias, mezclas y casos con poca representación.

Si el catálogo aumenta, podría dividirse en grupos más informativos, como:

- Mezclas de distintas variedades.
- Variedades autóctonas minoritarias.
- Variedades internacionales.
- Registros cuya variedad es desconocida.

Esto permitiría conservar más información sin crear categorías con un número demasiado reducido de ejemplos.

### 8.6. Evaluar periódicamente los clústeres

Los ocho clústeres deberían revisarse cuando cambie de forma importante el dataset, el preprocesamiento o las variables utilizadas.

La evaluación podría incluir:

- Comparación de diferentes números de clústeres.
- Coeficiente de silueta e inercia.
- Tamaño de los grupos.
- Estabilidad con distintas inicializaciones.
- Coherencia de los perfiles.
- Revisión de los nombres y descripciones asignados.
- Utilidad de los grupos dentro de la aplicación.

También podría probarse K-Means después de aplicar PCA con el número de componentes necesario para conservar entre el 80 % y el 90 % de la varianza. Los resultados podrían compararse con el enfoque actual, en el que K-Means utiliza directamente las 18 variables escaladas.

### 8.7. Mejorar la función de vinos similares

La aplicación podría calcular la distancia entre el vino de referencia y el resto de los vinos utilizando las variables escaladas.

De esta forma, las alternativas podrían ordenarse según su proximidad real y combinarse con otros criterios, como:

- Pertenencia al mismo clúster.
- Compatibilidad con el presupuesto.
- Tipo de vino.
- Características sensoriales.
- Diversidad de regiones, bodegas y variedades.

Esta mejora permitiría que la expresión “vinos similares” tuviera un significado matemático más preciso.

### 8.8. Aumentar la transparencia de los filtros

Cuando no sea posible cumplir alguna preferencia, la aplicación podría mostrar mensajes como:

- “No hemos encontrado vinos de la región seleccionada; te mostramos una alternativa de otra región”.
- “Para ofrecerte cuatro resultados hemos incluido vinos pertenecientes a otros perfiles”.
- “Esta recomendación respeta tu presupuesto y el tipo de vino, pero no coincide con la variedad indicada”.

También podrían diferenciarse visualmente las preferencias cumplidas, aproximadas y flexibilizadas.

### 8.9. Validar las reglas del quiz

Las reglas que relacionan las respuestas con los clústeres podrían revisarse para comprobar que los perfiles tienen oportunidades similares de ser seleccionados.

Para ello se podría:

- Contar los votos potenciales de cada clúster.
- Probar distintas combinaciones de respuestas.
- Revisar las reglas de desempate.
- Analizar la frecuencia con la que aparece cada perfil.
- Solicitar la revisión de personas con conocimientos enológicos.
- Comprobar si los usuarios se identifican con el resultado obtenido.

Esta evaluación permitiría ajustar las preguntas sin perder la sencillez actual del cuestionario.

### 8.10. Incorporar valoraciones voluntarias

La aplicación podría permitir que los usuarios indicaran voluntariamente:

- Si les gustó la recomendación.
- Si respetó sus preferencias.
- Si la explicación fue comprensible.
- Si encontraron el vino dentro de su presupuesto.
- Si desean recibir opciones diferentes.

Esta información permitiría evaluar la utilidad real de las recomendaciones y mejorar el sistema a partir de experiencias de uso.

La recogida debería limitarse a los datos necesarios, ser voluntaria e incluir una explicación clara de su finalidad.

### 8.11. Crear pruebas periódicas del sistema

Podría prepararse un conjunto estable de consultas para ejecutar después de cada actualización.

Estas pruebas permitirían comparar entre versiones:

- Los tipos de vino recomendados.
- La presencia de regiones y variedades.
- Los rangos de precio predominantes.
- La frecuencia con la que se flexibilizan filtros.
- El uso de otros clústeres en el quiz.
- La repetición de productos.
- La variedad de las alternativas.
- La correspondencia entre las explicaciones y los criterios aplicados.

Así sería posible detectar si un cambio mejora o reduce la diversidad y la coherencia de las recomendaciones.

### 8.12. Ampliar el seguimiento de las versiones

El proyecto ya permite conservar y reutilizar los objetos entrenados en un único artefacto. Como evolución del flujo de MLOps, podrían registrarse también:

- La versión del dataset.
- La fecha de entrenamiento.
- Las variables y su orden.
- Las transformaciones aplicadas.
- Los parámetros de PCA y K-Means.
- La semilla utilizada.
- Las métricas obtenidas.
- El tamaño y las características de cada clúster.
- Los cambios respecto a la versión anterior.
- El commit del repositorio asociado al entrenamiento.

Esta información facilitaría la comparación entre modelos y permitiría recuperar una versión anterior si una actualización produjera resultados menos adecuados.

### 8.13. Prioridades para futuras versiones

Entre todas las mejoras propuestas, se consideran prioritarias las siguientes:

1. Informar cuando no se pueda cumplir alguna preferencia.
2. Evaluar las recomendaciones generadas mediante consultas controladas.
3. Ampliar la diversidad del catálogo.
4. Ordenar los vinos similares mediante una medida de distancia.
5. Añadir información sobre la procedencia, cantidad y actualización de las valoraciones.

Estas acciones reforzarían especialmente la diversidad, la transparencia y la evaluación del sistema.

## 9. Conclusiones

InWine es una herramienta de orientación y descubrimiento que facilita la exploración de un catálogo de 2.024 vinos españoles. La aplicación permite buscar alternativas según diferentes preferencias y ofrece tres vías de recomendación adaptadas a distintas formas de interacción.

El proyecto combina el análisis de las características de los vinos con técnicas de aprendizaje no supervisado. K-Means organiza el catálogo en ocho perfiles utilizando las 18 variables escaladas, mientras que PCA permite representar esos datos en dos dimensiones para facilitar su análisis visual.

Las decisiones técnicas adoptadas son coherentes con el objetivo de esta primera versión. El precio se transforma mediante `log1p`, las variables se estandarizan, se comparan distintos valores de `k` y se comprueba la estabilidad del clustering con varias semillas. Además, el flujo de MLOps permite guardar y reutilizar los objetos entrenados sin volver a ejecutar manualmente todo el proceso.

Los ocho perfiles ayudan a presentar los clústeres de una forma comprensible, aunque sus nombres son interpretaciones creadas por el equipo y no categorías enológicas oficiales. Los vinos de un mismo grupo comparten un perfil general, pero pueden mantener diferencias de precio, región, crianza, variedad o características sensoriales.

La variedad de las recomendaciones depende en parte de la composición del catálogo, donde los vinos tintos tienen una presencia mayoritaria. Los perfiles más numerosos disponen de más candidatos, mientras que los grupos pequeños pueden ofrecer menos alternativas compatibles con todas las preferencias.

Las tres vías de recomendación utilizan lógicas diferentes. El formulario aplica filtros y prioriza el `rating`; el quiz asigna un perfil mediante reglas y votos; y la recomendación conversacional combina distintos criterios de compatibilidad y relación calidad-precio. Esta variedad permite adaptar la experiencia, aunque cada vía debe evaluarse según su propio funcionamiento.

InWine también incorpora medidas que favorecen un uso responsable: permite solicitar otras opciones, evita repetir vinos ya mostrados, combina distintos criterios, explica las recomendaciones y mantiene la decisión final en manos del usuario.

En conclusión, InWine cumple su objetivo como primera versión de un sumiller virtual orientado a ayudar al usuario a descubrir vinos compatibles con sus preferencias. Sus recomendaciones no pretenden sustituir el criterio personal ni proporcionar una elección perfecta, sino ofrecer un punto de partida comprensible dentro del catálogo disponible.

La ampliación del dataset, la validación de las recomendaciones con usuarios, la mejora de la función de vinos similares y una mayor transparencia cuando se flexibilicen los filtros permitirían seguir desarrollando en el futuro un sistema más diverso, preciso y útil.git sta