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

Finalmente, entre los vinos que permanecen después de aplicar los filtros, selecciona el que tiene el `rating` más alto.

La ocasión no interviene directamente en la selección del vino, aunque se utiliza posteriormente para personalizar el texto de la recomendación.

Esta vía trabaja sobre el catálogo disponible y no comienza asignando al usuario un clúster.

### 2.2. Quiz de perfil

El quiz relaciona las respuestas del usuario con uno de los ocho perfiles de vino definidos por el equipo.

Cada respuesta otorga un voto a un perfil concreto. El perfil que recibe más votos determina el `cluster_id` asignado al usuario y la aplicación muestra vinos pertenecientes a ese clúster, teniendo también en cuenta el presupuesto indicado.

La asignación se realiza mediante reglas fijas creadas por el equipo, no mediante un modelo entrenado con datos de usuarios. Por tanto, el resultado depende directamente de cómo se hayan definido esas correspondencias y las reglas de desempate.

### 2.3. Recomendación conversacional

La aplicación también permite solicitar recomendaciones de forma conversacional, por ejemplo, indicando la comida, el presupuesto o algunas características deseadas.

Esta vía combina distintos criterios, como:

- Compatibilidad con el presupuesto.
- Tipo y crianza del vino.
- Maridaje.
- `rating`.
- Relación calidad-precio.

Si la primera recomendación no convence, el usuario puede pedir otra opción. En ese caso, la aplicación excluye los vinos mostrados anteriormente e intenta encontrar una alternativa perteneciente al mismo clúster. Si no existen candidatos compatibles suficientes, algunos criterios pueden relajarse.

### 2.4. Vinos similares y exploración de perfiles

La aplicación permite consultar vinos pertenecientes al mismo clúster que un vino de referencia y explorar los ocho perfiles creados mediante K-Means.

En este contexto, pertenecer al mismo clúster significa compartir características generales según las variables utilizadas durante el modelado. Sin embargo, la aplicación no calcula la distancia individual entre los vinos para ordenarlos por grado de similitud.

Por ello, estas opciones deben entenderse como vinos del mismo perfil general y no necesariamente como los vinos matemáticamente más cercanos entre sí.

### 2.5. Papel de PCA y K-Means

Antes de utilizarse en la aplicación, los vinos pasan por un proceso de preparación y escalado de sus variables.

PCA reduce la información a dos componentes principales, `PC1` y `PC2`, facilitando la representación visual de los vinos. K-Means utiliza las variables preparadas para agruparlos en ocho clústeres con características similares.

El equipo interpreta posteriormente esos grupos y les asigna nombres descriptivos para facilitar su comprensión. Estos nombres son una interpretación humana de las características predominantes en cada grupo y no categorías objetivas o universales.

Los resultados del modelado se incorporan al catálogo mediante columnas como `cluster_id`, `PC1` y `PC2`. La aplicación utiliza principalmente el `cluster_id` para explorar perfiles, ofrecer alternativas y buscar vinos pertenecientes al mismo grupo.

## 3. Sesgos y limitaciones del dataset

Las recomendaciones de InWine están condicionadas por los vinos incluidos en el dataset. Si determinados tipos, regiones, uvas o rangos de precio aparecen con mayor frecuencia, también tendrán más posibilidades de estar presentes en los clústeres y en los resultados de la aplicación.

Esto no significa que la aplicación favorezca esos vinos de manera intencionada, sino que trabaja con un catálogo que no representa de forma equilibrada toda la diversidad del mercado español.

### 3.1. Predominio de vinos tintos

Aproximadamente el 84 % de los vinos del dataset son tintos. Como consecuencia, los vinos blancos, rosados y espumosos tienen una representación mucho menor.

Este desequilibrio puede provocar que:

- Los clústeres estén definidos principalmente por las características de los vinos tintos.
- Existan menos alternativas disponibles para usuarios que prefieren otros tipos de vino.
- Al relajar algún filtro, sea más probable que aparezcan vinos tintos.
- Los resultados generales de la aplicación transmitan una imagen poco equilibrada de la oferta vinícola española.

La importancia histórica y comercial del vino tinto en España puede explicar parcialmente su presencia destacada. Sin embargo, los datos oficiales sobre superficie de cultivo y producción por color no muestran una diferencia suficiente para justificar por sí sola una proporción cercana al 84 %.

Por tanto, este desequilibrio debe considerarse una limitación de representatividad del dataset. También podría estar relacionado con la fuente original, la disponibilidad de reseñas o los criterios utilizados para recopilar y seleccionar los vinos.

### 3.2. Concentración en determinadas regiones

Regiones con una gran presencia comercial y un número elevado de reseñas, especialmente Rioja y Ribera del Duero, aparecen con mayor frecuencia en el dataset.

Esto puede hacer que:

- Tengan más presencia dentro de los clústeres.
- Dispongan de más candidatos cuando se aplican los filtros.
- Aparezcan con mayor frecuencia en las recomendaciones.
- Otras denominaciones de origen y regiones menos representadas tengan menos oportunidades de ser descubiertas.

No puede afirmarse que la aplicación recomiende sistemáticamente estas regiones sin analizar la frecuencia real de sus resultados. Sin embargo, su mayor presencia en el catálogo aumenta potencialmente sus posibilidades de selección.

### 3.3. Predominio de determinadas variedades de uva

La variedad Tempranillo tiene una presencia destacada en el dataset. Además, durante el preprocesamiento algunas variedades minoritarias o combinaciones de uvas se agrupan en categorías generales, como `Blend/Other`.

Esta simplificación facilita el tratamiento de los datos, pero también provoca una pérdida de información. Vinos elaborados con variedades diferentes pueden quedar representados bajo una misma categoría, aunque sus características reales no sean iguales.

Como consecuencia:

- Las variedades mayoritarias conservan una identidad más definida.
- Las variedades minoritarias pierden parte de su detalle.
- El modelo puede distinguir peor la diversidad existente dentro de `Blend/Other`.
- Las recomendaciones pueden favorecer indirectamente las categorías con más ejemplos y mejor diferenciadas.

### 3.4. Distribución del precio

El catálogo contiene vinos de distintos precios, pero su distribución no es uniforme. Los rangos con más ejemplos ofrecen más posibilidades de encontrar candidatos compatibles.

Además, el precio influye en varias partes de la aplicación:

- Como presupuesto máximo en el formulario.
- Como restricción en el quiz.
- Como criterio en la recomendación conversacional.
- En el cálculo de la relación calidad-precio.

Por ello, los vinos pertenecientes a rangos poco representados pueden aparecer con menor frecuencia. También debe tenerse en cuenta que el precio puede cambiar según la tienda, la añada, las promociones o el momento de la consulta, por lo que el valor incluido en el dataset no garantiza que el usuario encuentre actualmente el vino a ese precio.

### 3.5. Calidad y procedencia de las valoraciones

El `rating` tiene una influencia importante en la aplicación, especialmente en el recomendador mediante formulario, que selecciona el vino mejor valorado entre los candidatos disponibles.

Sin embargo, una valoración no constituye una medida completamente objetiva de calidad. Puede depender de:

- La cantidad y el perfil de las personas que valoraron el vino.
- La popularidad y visibilidad previa de la bodega.
- La plataforma o fuente de la que procede la puntuación.
- El número de reseñas disponibles.
- Los gustos de los usuarios o especialistas que realizaron las valoraciones.

Además, disponer de un `rating` elevado no significa necesariamente que el vino sea el más adecuado para las preferencias concretas de una persona.

Por tanto, el `rating` debe interpretarse como una señal adicional de calidad percibida, no como una medida universal ni neutral.

### 3.6. Cobertura limitada del mercado

El dataset no contiene todos los vinos disponibles en España ni se actualiza automáticamente con los cambios del mercado. Las recomendaciones solo pueden realizarse entre los vinos incluidos en el catálogo.

Esto implica que:

- Un vino adecuado para el usuario puede no aparecer porque no forma parte del dataset.
- La aplicación no garantiza la disponibilidad comercial de los vinos.
- Pueden quedar fuera bodegas pequeñas, vinos nuevos o productos con pocas reseñas.
- Los precios, añadas y otras características pueden quedar desactualizados.

Por ello, InWine recomienda la mejor opción encontrada dentro de su catálogo y según sus reglas, no necesariamente el mejor vino existente en todo el mercado.

## 4. Limitaciones del preprocesamiento de los datos

Antes de aplicar PCA y K-Means, los datos pasan por distintas transformaciones para convertir la información original en variables que puedan utilizarse durante el modelado.

Estas decisiones son necesarias para trabajar con el dataset, pero también simplifican la información y pueden influir en la forma en la que los vinos quedan representados y agrupados.

### 4.1. Agrupación de categorías minoritarias

Algunas variedades de uva con pocos ejemplos y determinadas combinaciones se agrupan dentro de categorías generales, como `Blend/Other`.

Esta decisión evita crear muchas categorías con muy pocos datos, pero hace que vinos diferentes compartan una misma representación. Como consecuencia, el modelo puede perder parte de la información que distingue a las variedades minoritarias.

La agrupación beneficia técnicamente a las categorías con más ejemplos, mientras que las menos frecuentes quedan representadas de una forma más general.

### 4.2. Codificación de variables categóricas

Variables como la región, la variedad de uva o la denominación de origen deben transformarse en valores numéricos antes de utilizarse en el modelado.

Esta codificación no reproduce completamente la complejidad cultural, geográfica y enológica de cada categoría. Dos regiones o variedades representadas mediante valores distintos no son necesariamente más o menos parecidas por la distancia entre esos números.

Por tanto, las variables codificadas son una representación técnica que permite entrenar el modelo, pero no deben interpretarse como una medición exacta de la relación real entre regiones, uvas o denominaciones.

### 4.3. Transformación del precio

El precio presenta una distribución desigual y puede contener algunos valores muy elevados. Para reducir la influencia de estos casos se aplica una transformación logarítmica mediante `log1p`.

Esta transformación permite que las diferencias entre los precios más altos no dominen el agrupamiento. Sin embargo, también modifica la distancia original entre los vinos: una diferencia de precio elevada queda comprimida después de la transformación.

Se trata de una decisión razonable para el modelado, pero debe tenerse en cuenta al interpretar los clústeres, ya que el modelo trabaja con el precio transformado y no directamente con su valor original en euros.

### 4.4. Escalado de las variables

Las variables utilizadas por el modelo tienen unidades y rangos diferentes. Por ejemplo, el precio, el `rating` y las variables sensoriales no se miden de la misma manera.

Para evitar que las variables con números más grandes tengan automáticamente más influencia, se utiliza `StandardScaler`. Este proceso centra y escala cada variable tomando como referencia la media y la desviación estándar del dataset.

El escalado mejora la comparabilidad entre variables, pero no garantiza que todas tengan la misma relevancia real para las preferencias de los usuarios. La importancia enológica o subjetiva de cada característica depende también de las variables seleccionadas y de la información disponible.

### 4.5. Creación de variables sensoriales a partir de descripciones

Las características sensoriales utilizadas por el proyecto se obtienen a partir de las descripciones textuales de los vinos mediante la búsqueda de palabras asociadas a perfiles como:

- Frutal.
- Floral.
- Especiado.
- Madera.
- Mineral.
- Dulce.

Este procedimiento permite convertir textos en variables utilizables por el modelo, pero presenta varias limitaciones:

- Depende del vocabulario incluido en los diccionarios.
- Puede no reconocer sinónimos o expresiones no previstas.
- Una palabra puede tener significados diferentes según el contexto.
- La ausencia de una palabra no demuestra que el vino carezca de esa característica.
- Las descripciones más extensas tienen más posibilidades de contener términos detectables.
- La calidad de la extracción depende de la calidad y el nivel de detalle de la descripción original.

Por tanto, estas variables representan la información que el sistema ha podido detectar en el texto, no una evaluación sensorial completa del vino.

### 4.6. Diferencia entre característica ausente e información desconocida

Cuando una característica sensorial no se encuentra en una descripción, puede representarse con un valor bajo o con cero. Sin embargo, este resultado puede significar dos cosas diferentes:

- Que el vino realmente no presenta esa característica.
- Que la descripción no la menciona o no contiene las palabras reconocidas por el sistema.

El modelo no siempre puede distinguir entre ambas situaciones. Esto puede hacer que vinos con descripciones incompletas parezcan sensorialmente similares, aunque en realidad no lo sean.

Esta limitación debe tenerse especialmente en cuenta al interpretar los clústeres y las recomendaciones basadas en perfiles de sabor.

### 4.7. Pérdida de registros durante la preparación

Durante la limpieza y preparación pueden descartarse registros incompletos, duplicados o vinos cuyo tipo no puede clasificarse correctamente.

Esta eliminación mejora la consistencia técnica del dataset, pero también reduce su cobertura. Si los registros descartados pertenecen con mayor frecuencia a determinadas regiones, variedades o tipos de vino, su eliminación podría aumentar la infrarrepresentación de esas categorías.

Por este motivo, es importante documentar cuántos registros se eliminan y por qué, y comprobar que el proceso no excluye de forma desproporcionada a un grupo concreto de vinos.

### 4.8. Reproducibilidad del proceso

El proyecto incorpora un flujo básico de MLOps para guardar y reutilizar los objetos empleados durante el preprocesamiento y el modelado, incluidos el escalado, K-Means y PCA.

Esto permite que los nuevos vinos reciban las mismas transformaciones y que las variables se utilicen en el mismo orden que durante el entrenamiento. También mejora la reproducibilidad, la trazabilidad y la coherencia técnica del sistema.

Sin embargo, este flujo no elimina automáticamente los sesgos del dataset ni corrige las limitaciones de las variables creadas. Si los datos originales están desequilibrados o una transformación pierde información, el pipeline reproducirá de forma consistente esas mismas decisiones.

## 5. Limitaciones de PCA y K-Means

PCA y K-Means permiten resumir la información del catálogo y organizar los vinos en perfiles generales. Estas técnicas son útiles para explorar el dataset y facilitar algunas funciones de la aplicación, pero sus resultados dependen de las variables seleccionadas y de las decisiones tomadas durante el modelado.

### 5.1. Reducción de información mediante PCA

PCA transforma las variables originales en nuevas componentes que concentran parte de la variabilidad presente en los datos.

En el proyecto se utilizan dos componentes, `PC1` y `PC2`, para representar visualmente los vinos. Esta reducción facilita la creación de gráficos y permite observar agrupaciones generales, pero dos componentes no conservan necesariamente toda la información del dataset.

Como consecuencia:

- Parte de la variabilidad original puede perderse.
- Dos vinos cercanos en el gráfico no tienen por qué ser idénticos en todas sus características.
- Algunas diferencias importantes para un usuario pueden quedar poco representadas.
- La interpretación de cada componente no siempre es directa, porque combina varias variables originales.

Por ello, el gráfico de PCA debe entenderse como una representación simplificada del catálogo y no como una descripción completa de cada vino.

### 5.2. Papel de PCA en el agrupamiento

PCA y K-Means cumplen funciones diferentes. PCA reduce dimensiones y facilita la visualización, mientras que K-Means es la técnica que asigna cada vino a un clúster.

La utilidad y las limitaciones de PCA dependen también de cómo se haya utilizado durante el entrenamiento final. Si K-Means se entrena con las variables preparadas originales, `PC1` y `PC2` sirven principalmente para visualizar los grupos. Si se entrena con las componentes principales, la pérdida de información producida por PCA también influye directamente en la formación de los clústeres.

Por este motivo, el pipeline debe conservar y documentar claramente qué variables recibe K-Means y en qué orden.

### 5.3. Elección del número de clústeres

El catálogo se ha dividido en ocho clústeres. Esta cantidad permite ofrecer perfiles variados y comprensibles dentro de la aplicación, pero no representa una división natural o universal de todos los vinos.

El número de clústeres depende de:

- Las métricas utilizadas durante la evaluación.
- La distribución de los datos.
- La utilidad práctica de los grupos para la aplicación.
- La interpretación realizada por el equipo.

Otra elección del número de clústeres podría producir agrupaciones diferentes. Por tanto, los ocho perfiles son una forma útil de organizar este catálogo, pero no deben presentarse como las únicas categorías posibles.

### 5.4. Diferencias de tamaño entre clústeres

Los clústeres no contienen necesariamente el mismo número de vinos. Algunos perfiles disponen de muchas más opciones que otros debido a la distribución original del dataset y a la forma en la que K-Means realiza el agrupamiento.

Esta diferencia puede provocar que:

- Algunos perfiles ofrezcan más variedad de precios, regiones y uvas.
- Los clústeres pequeños tengan menos alternativas compatibles con los filtros.
- Sea necesario recurrir antes a vinos de otros clústeres para completar resultados.
- Los usuarios asignados a perfiles grandes tengan más posibilidades de recibir recomendaciones variadas.

K-Means busca grupos internamente similares, pero no garantiza que tengan el mismo tamaño ni que ofrezcan las mismas oportunidades de recomendación.

### 5.5. Sensibilidad a las variables utilizadas

K-Means agrupa los vinos según las variables que recibe. Las características que no están presentes en el dataset no pueden influir en el resultado.

Además, aunque las variables estén escaladas, la selección de cuáles incluir determina el concepto de similitud utilizado por el modelo. Si se utilizan precio, `rating`, tipo de vino y características sensoriales, los clústeres reflejarán principalmente esas dimensiones.

Esto significa que dos vinos pueden pertenecer al mismo clúster según las variables disponibles y, aun así, diferenciarse en aspectos no incluidos, como:

- El método concreto de elaboración.
- La añada y su evolución.
- La disponibilidad comercial.
- Preferencias sensoriales más detalladas.
- La percepción subjetiva de cada persona.

La pertenencia a un mismo clúster representa una similitud aproximada dentro del modelo, no una equivalencia completa entre los vinos.

### 5.6. Sensibilidad de K-Means a la inicialización y a los datos

K-Means puede producir resultados diferentes según la inicialización de los centroides y los datos utilizados durante el entrenamiento.

El uso de una semilla fija permite reproducir el mismo resultado con el mismo dataset y la misma configuración. Sin embargo, si se incorporan vinos nuevos, cambian las variables o se modifica el preprocesamiento, los clústeres y sus centroides pueden variar.

El flujo de MLOps ayuda a conservar el modelo entrenado y evita recalcular los grupos de forma accidental en cada ejecución. Si en el futuro se vuelve a entrenar el modelo, será necesario comparar la nueva versión con la anterior y revisar si el significado de los clústeres ha cambiado.

### 5.7. Interpretación y nombres de los perfiles

Los nombres y descripciones de los ocho perfiles no son generados automáticamente por K-Means. El modelo únicamente crea agrupaciones numéricas; posteriormente, el equipo interpreta las características predominantes de cada clúster y les asigna nombres comprensibles.

Esta interpretación facilita el uso de la aplicación, pero introduce una valoración humana. Un nombre breve puede simplificar demasiado la diversidad interna del grupo o destacar unas características y dejar otras en segundo plano.

Por tanto:

- Los nombres deben presentarse como descripciones orientativas.
- No todos los vinos del clúster tienen que cumplir cada rasgo del perfil con la misma intensidad.
- Las descripciones deberían revisarse si cambia el modelo o el dataset.
- No deben interpretarse como categorías enológicas oficiales.

### 5.8. Similitud dentro de un mismo clúster

La aplicación utiliza el `cluster_id` para identificar vinos del mismo perfil. Sin embargo, pertenecer al mismo clúster no significa que todos sus integrantes sean igual de similares entre sí.

K-Means asigna cada vino al centroide más cercano, pero dentro de un mismo grupo puede haber vinos más próximos o más alejados entre sí. La función de vinos similares no calcula ni utiliza estas distancias para ordenar los resultados.

Por ello, es más preciso indicar que la aplicación muestra vinos pertenecientes al mismo clúster que afirmar que presenta los vinos matemáticamente más similares.

### 5.9. Ausencia de validación con preferencias reales de usuarios

Los clústeres se han creado a partir de las características de los vinos y no mediante datos históricos sobre los gustos o elecciones de los usuarios.

Por tanto, que dos vinos sean próximos según el modelo no garantiza que una persona que disfrute de uno vaya a preferir también el otro. Para comprobar la utilidad real de los perfiles sería necesario recopilar valoraciones voluntarias y analizar, respetando la privacidad, si las recomendaciones resultan relevantes para distintos tipos de usuarios.

Mientras no se realice esa validación, los perfiles deben considerarse una aproximación basada en las características disponibles del catálogo.

## 6. Sesgos y limitaciones de las vías de recomendación

InWine ofrece varias formas de obtener recomendaciones. Cada una emplea una lógica diferente, por lo que sus posibles sesgos y limitaciones deben analizarse por separado.

### 6.1. Recomendador mediante formulario

El formulario aplica diferentes filtros sobre el catálogo según las preferencias indicadas por el usuario. El presupuesto y el tipo de vino tienen una influencia directa, mientras que otros criterios, como la región, la variedad de uva o el perfil de sabor, se aplican de forma flexible.

Cuando uno de estos filtros flexibles no encuentra coincidencias, la aplicación mantiene los candidatos obtenidos en el paso anterior. Esta decisión evita que el sistema se quede sin resultados, pero también puede provocar que la recomendación final no cumpla todas las preferencias seleccionadas.

Por ejemplo, si no existen vinos compatibles con la región elegida, el sistema puede recomendar un vino de otra región sin que esta relajación resulte evidente para el usuario.

Una vez aplicados los filtros, la aplicación selecciona el vino con mayor `rating` entre los candidatos disponibles. Esto introduce varias limitaciones:

- El `rating` puede tener más peso que otras preferencias personales.
- Los vinos populares o con valoraciones elevadas parten con ventaja.
- El sistema no considera el número de valoraciones ni la incertidumbre asociada a la puntuación.
- Si se repite la misma consulta, normalmente se obtiene el mismo resultado.
- Los vinos con una puntuación algo menor tienen pocas oportunidades de ser mostrados, aunque también sean compatibles.

Además, la ocasión elegida no modifica directamente la selección del vino. Se utiliza para personalizar la explicación posterior, por lo que el texto puede transmitir una adaptación a la ocasión mayor que la que realmente ha intervenido en el cálculo.

### 6.2. Quiz de perfil

El quiz asigna al usuario uno de los ocho clústeres mediante reglas creadas por el equipo. Cada respuesta suma un voto a un perfil y el resultado final depende del perfil que acumula más votos.

Este sistema es comprensible y reproducible, pero no ha sido aprendido a partir de las preferencias reales de los usuarios. Las relaciones entre una respuesta y un clúster representan decisiones humanas sobre qué perfil se considera más apropiado.

Esto puede provocar que:

- Algunas respuestas simplifiquen demasiado los gustos personales.
- Personas con preferencias diferentes terminen en el mismo perfil.
- Una pequeña variación en una respuesta cambie el clúster asignado.
- Las reglas de desempate influyan en el resultado.
- Algunos perfiles reciban más votos potenciales que otros según el diseño de las preguntas.

Una vez asignado el clúster, la aplicación busca vinos que pertenezcan a él y que se encuentren dentro del presupuesto indicado. Sin embargo, si no hay cuatro vinos compatibles, completa las opciones con vinos de otros clústeres.

Esta estrategia garantiza que siempre aparezcan cuatro resultados, pero reduce la coherencia entre el perfil obtenido y las recomendaciones mostradas. Por tanto, no debe afirmarse que todos los vinos presentados por el quiz pertenecen necesariamente al clúster asignado.

También existe una diferencia de oportunidades entre perfiles: los clústeres grandes y con una mayor variedad de precios tienen más posibilidades de ofrecer cuatro vinos propios, mientras que los pequeños pueden necesitar recurrir con mayor frecuencia a otros grupos.

### 6.3. Recomendación conversacional

La recomendación conversacional interpreta la petición del usuario y combina criterios como el presupuesto, el tipo de vino, la crianza, el maridaje, el `rating` y la relación calidad-precio.

Esta vía permite consultas más flexibles, pero también presenta limitaciones:

- La petición del usuario puede ser ambigua o incompleta.
- Dos expresiones parecidas pueden interpretarse de manera diferente.
- El vocabulario reconocido por el sistema puede no cubrir todas las formas de describir un vino.
- Los criterios empleados no tienen necesariamente la misma importancia para todas las personas.
- El `rating` y la relación calidad-precio pueden favorecer a vinos bien puntuados o situados en determinados rangos de precio.

El chatbot aplica una puntuación que combina compatibilidad y calidad-precio. Este mecanismo no se utiliza necesariamente de la misma forma en el formulario ni en el quiz. Por ello, no debe describirse como un sistema general compartido por todas las recomendaciones de InWine.

Además, una buena relación entre `rating` y precio no significa que un vino sea objetivamente mejor. El resultado depende de la fiabilidad de la valoración, del precio almacenado y de la fórmula definida por el equipo.

### 6.4. Función de solicitar otra opción

Cuando el usuario pide otra alternativa, la aplicación excluye los vinos que ya se han mostrado. Esta medida mejora la diversidad y evita repetir continuamente la misma recomendación.

El sistema intenta mantener el mismo clúster para conservar el perfil general de la propuesta anterior. Sin embargo, esto solo es posible si siguen existiendo candidatos compatibles. Si no hay suficientes vinos disponibles, puede ser necesario relajar algunos criterios.

Por tanto, esta función constituye una mitigación parcial:

- Aumenta la variedad de vinos mostrados.
- Da mayor control al usuario.
- Reduce la repetición de las opciones mejor posicionadas.
- No garantiza que todas las alternativas cumplan exactamente los mismos criterios.
- No corrige el desequilibrio original del catálogo ni de los clústeres.

Sería conveniente que la aplicación informara al usuario cuando una nueva opción requiere relajar alguna preferencia.

### 6.5. Función de vinos similares

La función de vinos similares selecciona vinos que pertenecen al mismo clúster que el vino de referencia y excluye el propio vino consultado.

Esta aproximación permite descubrir productos del mismo perfil general, pero no calcula la distancia entre los vinos ni los ordena según su proximidad al vino original. Los resultados corresponden a los primeros candidatos compatibles encontrados en el catálogo.

Por tanto:

- Los vinos pertenecen al mismo clúster, pero no tienen que ser los más próximos entre sí.
- El orden del dataset puede influir en qué vinos aparecen.
- Las diferencias internas dentro del clúster no se tienen en cuenta.
- Los vinos situados cerca de los límites del grupo pueden tener características distintas.

La expresión más precisa es “vinos pertenecientes al mismo clúster” y no “los vinos más similares”.

### 6.6. Influencia del orden y de la disponibilidad de candidatos

En algunas funciones, cuando varios vinos cumplen las condiciones y no existe una ordenación adicional por distancia o diversidad, el orden en el que aparecen en el dataset puede influir en la selección.

Esto puede dar más visibilidad a determinados vinos sin que exista una razón relacionada con las preferencias del usuario. Además, los grupos con más candidatos tienen más posibilidades de ofrecer variedad que aquellos con pocos ejemplos.

Para reducir esta influencia podrían aplicarse, según la función:

- Una ordenación por compatibilidad claramente definida.
- Una selección aleatoria controlada entre candidatos equivalentes.
- Límites para evitar la repetición excesiva de regiones, bodegas o variedades.
- Criterios de diversidad dentro del conjunto de resultados.
- Una ordenación por distancia al centroide o al vino de referencia cuando se busque similitud.

### 6.7. Explicaciones de las recomendaciones

Las explicaciones ayudan al usuario a comprender la recomendación, pero deben corresponder exactamente con los criterios que realmente participaron en la selección.

Existe un riesgo de sobreexplicación cuando el texto menciona una preferencia, como la ocasión o el maridaje, aunque esta no haya influido directamente o haya sido relajada durante el filtrado.

Para mantener la transparencia, las explicaciones deberían diferenciar entre:

- Los criterios utilizados para seleccionar el vino.
- Las preferencias que se utilizaron únicamente para personalizar el texto.
- Los filtros que no pudieron cumplirse.
- Las reglas que se relajaron para encontrar una alternativa.

Una explicación comprensible no garantiza por sí sola que el proceso sea completamente explicable. Su contenido debe poder relacionarse con la lógica real ejecutada por la aplicación.

### 6.8. Evaluación limitada de los resultados generados

El proyecto incluye tests que comprueban el funcionamiento técnico de las recomendaciones en casos concretos. Sin embargo, todavía no se realiza un análisis global que mida qué vinos, tipos, regiones, variedades o clústeres aparecen con mayor frecuencia en el conjunto de resultados.

Esta evaluación permitiría detectar si determinados grupos reciben más visibilidad y comprobar la diversidad real de las recomendaciones.

## 7. Medidas de mitigación incorporadas

InWine incluye varias decisiones destinadas a mejorar la diversidad, la transparencia y la coherencia de sus recomendaciones. Estas medidas no eliminan completamente los sesgos y limitaciones detectados, pero ayudan a reducir algunos de sus efectos.

### 7.1. Posibilidad de solicitar otra recomendación

El usuario puede rechazar una propuesta y solicitar otra opción. La aplicación excluye los vinos mostrados anteriormente para evitar repeticiones y ampliar las alternativas disponibles.

Esta funcionalidad:

- Aumenta el control del usuario sobre la recomendación.
- Reduce la repetición de los vinos mejor posicionados.
- Permite descubrir opciones que inicialmente tenían una puntuación inferior.
- Introduce cierta diversidad dentro de los candidatos disponibles.

Sin embargo, su eficacia depende del número de vinos compatibles. Los clústeres o categorías con pocos ejemplos seguirán ofreciendo menos variedad.

### 7.2. Flexibilidad de algunos filtros

En el recomendador mediante formulario, algunos filtros se aplican de forma flexible para evitar que una combinación muy concreta de preferencias deje al usuario sin resultados.

Esta decisión mejora la utilidad de la aplicación, pero debe ir acompañada de transparencia. Cuando no sea posible respetar una preferencia, la aplicación debería indicarlo claramente y explicar qué criterio se ha relajado.

De este modo, el usuario puede decidir si la alternativa continúa siendo adecuada para sus necesidades.

### 7.3. Uso combinado de diferentes criterios

La aplicación no utiliza únicamente una característica para todas sus recomendaciones. Dependiendo de la vía elegida, puede tener en cuenta elementos como:

- Presupuesto.
- Tipo de vino.
- Región.
- Variedad de uva.
- Maridaje.
- Perfil sensorial.
- Crianza.
- `rating`.
- Relación calidad-precio.
- Pertenencia a un clúster.

Combinar distintos criterios reduce la dependencia de una única variable. No obstante, cada vía de recomendación utiliza estos elementos de manera diferente y algunos tienen más peso que otros.

### 7.4. Explicaciones para el usuario

InWine acompaña sus recomendaciones con textos que ayudan a comprender las características del vino y su posible adecuación a las preferencias indicadas.

Esta explicación mejora la accesibilidad del sistema, especialmente para personas que no tienen conocimientos especializados sobre vinos.

Para que esta medida sea realmente efectiva, el contenido debe reflejar la lógica aplicada por la aplicación. No debería afirmar que una preferencia determinó la selección cuando solo se utilizó para personalizar el mensaje o cuando tuvo que ser descartada.

### 7.5. Exploración de distintos perfiles

La posibilidad de consultar los ocho perfiles y descubrir vinos pertenecientes a cada uno permite al usuario explorar opciones diferentes a su recomendación inicial.

Esta funcionalidad reduce la idea de que existe una única elección correcta y presenta los clústeres como herramientas de descubrimiento, no como clasificaciones rígidas de los gustos personales.

### 7.6. Conservación del pipeline de modelado

El flujo de MLOps permite guardar y reutilizar los objetos utilizados durante el preprocesamiento y el modelado.

Esto ayuda a garantizar que:

- Las variables se procesen siempre de la misma manera.
- Se respete el mismo orden de las características.
- No se vuelva a entrenar el modelo accidentalmente en cada ejecución.
- Los resultados puedan reproducirse con la misma versión del dataset y del pipeline.
- Sea posible identificar qué versión del modelo se está utilizando.

Esta medida mejora la coherencia técnica y la trazabilidad, aunque no corrige por sí sola los desequilibrios presentes en los datos.

### 7.7. Uso de una semilla fija

El entrenamiento utiliza una semilla fija para controlar la aleatoriedad de K-Means. Esto permite obtener los mismos clústeres cuando se trabaja con los mismos datos, variables y parámetros.

La reproducibilidad facilita la revisión de los resultados y evita que los perfiles cambien sin una modificación consciente del proceso.

Sin embargo, una semilla fija no demuestra que la agrupación sea la única posible ni que sea la mejor para representar las preferencias reales de los usuarios.

### 7.8. Documentación de las limitaciones

La elaboración de este análisis constituye también una medida de mitigación. Documentar los posibles sesgos permite:

- Evitar afirmaciones exageradas sobre las capacidades del sistema.
- Informar al usuario sobre el alcance real de las recomendaciones.
- Identificar mejoras para futuras versiones.
- Facilitar la revisión del modelo y de las reglas utilizadas.
- Diferenciar entre resultados observados y riesgos potenciales.

La transparencia no elimina las limitaciones, pero permite utilizar la aplicación de una forma más responsable y comprender mejor sus resultados.

### 7.9. Supervisión y decisión final del usuario

InWine no toma decisiones obligatorias ni produce consecuencias de alto impacto. El usuario puede aceptar, rechazar o ignorar cualquier recomendación.

La decisión final sigue correspondiendo a la persona, que puede comparar varias opciones y tener en cuenta aspectos que la aplicación no conoce, como la disponibilidad real, sus experiencias anteriores o sus preferencias más específicas.

## 8. Propuestas de mejora

A partir de los sesgos y limitaciones identificados, se proponen distintas mejoras para aumentar la representatividad del catálogo, la calidad de las recomendaciones y la transparencia de InWine.

Estas medidas no forman parte necesariamente de la versión actual, sino que representan posibles líneas de trabajo para futuras versiones.

### 8.1. Ampliar y equilibrar el dataset

Una de las mejoras prioritarias sería incorporar más vinos de los grupos que actualmente tienen poca representación, especialmente:

- Vinos blancos.
- Vinos rosados.
- Vinos espumosos.
- Regiones y denominaciones de origen minoritarias.
- Variedades de uva menos frecuentes.
- Bodegas pequeñas o con menos presencia en plataformas de reseñas.
- Vinos pertenecientes a diferentes rangos de precio.

El objetivo no sería conseguir exactamente el mismo número de vinos en todas las categorías, ya que esto tampoco reflejaría necesariamente el mercado real, sino evitar que unos pocos grupos dominen excesivamente el catálogo.

También sería conveniente comparar la distribución del dataset con fuentes oficiales del sector vinícola para comprobar hasta qué punto representa la diversidad real de la oferta española.

### 8.2. Mejorar la información sobre las valoraciones

El `rating` sería más fiable si estuviera acompañado de información adicional, como:

- Número de valoraciones recibidas.
- Fuente de la puntuación.
- Fecha de actualización.
- Tipo de personas que realizaron la valoración, cuando esa información estuviera disponible.
- Diferenciación entre puntuaciones de usuarios y de especialistas.

De este modo, la aplicación podría evitar tratar de la misma manera un vino con una puntuación alta basada en pocas opiniones y otro con una valoración similar respaldada por muchas reseñas.

También podría utilizarse una puntuación ajustada que combine el `rating` con el número de valoraciones.

### 8.3. Actualizar precios y disponibilidad

Los precios deberían revisarse periódicamente o conectarse, cuando sea posible, con fuentes comerciales actualizadas.

La aplicación también podría indicar:

- La fecha de actualización del precio.
- Un intervalo orientativo en lugar de un precio exacto.
- Que el valor puede variar según la tienda y la añada.
- Si existe información reciente sobre su disponibilidad.

Esto reduciría el riesgo de recomendar vinos que ya no se encuentran en el mercado o cuyo precio actual supera el presupuesto del usuario.

### 8.4. Mejorar la extracción de características sensoriales

Las variables sensoriales podrían obtenerse mediante técnicas de procesamiento del lenguaje más avanzadas que la búsqueda directa de palabras.

Por ejemplo, se podrían incorporar:

- Diccionarios más completos con sinónimos y expresiones equivalentes.
- Lematización para reconocer distintas formas de una misma palabra.
- Detección del contexto en el que aparece cada término.
- Reconocimiento de negaciones.
- Modelos de lenguaje entrenados o adaptados al vocabulario enológico.
- Una revisión manual de una muestra de resultados para comprobar la calidad de la extracción.

También sería útil distinguir entre una característica realmente ausente y una característica desconocida porque la descripción no aporta información suficiente.

### 8.5. Revisar la agrupación de variedades minoritarias

La categoría `Blend/Other` podría dividirse en grupos más informativos cuando exista un número suficiente de registros.

Por ejemplo, podrían diferenciarse:

- Vinos elaborados con mezclas de variedades.
- Variedades autóctonas minoritarias.
- Variedades internacionales.
- Registros cuya variedad es realmente desconocida.

Esta separación permitiría conservar más información y evitaría representar de la misma manera vinos que presentan características distintas.

### 8.6. Evaluar periódicamente los clústeres

Los clústeres deberían revisarse cuando cambie el dataset, el preprocesamiento o el número de variables.

La evaluación podría incluir:

- Comparación de distintas cantidades de clústeres.
- Métricas como el coeficiente de silueta.
- Análisis del tamaño de cada grupo.
- Revisión de la estabilidad de los clústeres con distintas inicializaciones.
- Comprobación de la coherencia de los perfiles por parte de personas con conocimientos enológicos.
- Revisión de los nombres y descripciones asignados a cada perfil.

También sería importante comprobar si los ocho clústeres siguen siendo útiles para la aplicación después de incorporar nuevos vinos.

### 8.7. Mejorar la búsqueda de vinos similares

En lugar de seleccionar únicamente vinos que pertenezcan al mismo clúster, la aplicación podría calcular la distancia entre el vino de referencia y los demás vinos.

Esto permitiría ordenar los resultados según su proximidad real dentro del espacio utilizado por el modelo.

La búsqueda podría combinar:

- Distancia entre las variables escaladas.
- Pertenencia al mismo clúster.
- Compatibilidad con el presupuesto.
- Tipo de vino.
- Características sensoriales.
- Diversidad de regiones, bodegas o variedades.

De este modo, la expresión “vinos similares” tendría un respaldo matemático más preciso.

### 8.8. Aumentar la transparencia de los filtros

La aplicación debería informar claramente cuando no pueda cumplir alguna preferencia.

Por ejemplo, podría mostrar mensajes como:

- “No hemos encontrado opciones de la región seleccionada; te mostramos una alternativa de otra región”.
- “Para ofrecerte cuatro resultados hemos incluido vinos de otros perfiles”.
- “Esta recomendación respeta tu presupuesto y tipo de vino, pero no coincide con la variedad indicada”.

También sería útil diferenciar visualmente entre:

- Preferencias cumplidas.
- Preferencias aproximadas.
- Preferencias que tuvieron que relajarse.

Esto permitiría al usuario comprender mejor por qué ha recibido cada recomendación.

### 8.9. Revisar y validar las reglas del quiz

Las reglas que relacionan cada respuesta con un clúster deberían analizarse para comprobar que ningún perfil recibe una ventaja injustificada.

Para ello se podría:

- Contar cuántos votos potenciales puede recibir cada clúster.
- Probar todas las combinaciones posibles de respuestas.
- Revisar las reglas de desempate.
- Analizar con qué frecuencia se asigna cada perfil.
- Pedir a personas con conocimientos sobre vinos que revisen las asociaciones.
- Comparar el resultado del quiz con las preferencias expresadas posteriormente por los usuarios.

Esta validación permitiría detectar preguntas demasiado determinantes o perfiles que resulten muy difíciles de obtener.

### 8.10. Incorporar opiniones voluntarias de los usuarios

La aplicación podría permitir que los usuarios indicaran voluntariamente si una recomendación les ha resultado útil.

Por ejemplo, podrían valorar:

- Si les gustó el vino recomendado.
- Si la propuesta respetó sus preferencias.
- Si la explicación fue comprensible.
- Si encontraron el vino dentro de su presupuesto.
- Si desean recibir opciones diferentes en el futuro.

Esta información permitiría evaluar el sistema con experiencias reales y no únicamente con las características técnicas del dataset.

La recogida de datos debería ser voluntaria, limitada a la información necesaria y acompañada de una explicación clara sobre su uso.

### 8.11. Incorporar pruebas periódicas de sesgo

Como mejora futura, se podría crear un conjunto fijo de consultas para repetirlo cada vez que se actualicen los datos, el modelo o el sistema de recomendación.

Estas pruebas permitirían comparar versiones y detectar cambios importantes en la frecuencia con la que aparecen determinados tipos de vino, regiones, variedades, rangos de precio o clústeres. También ayudarían a identificar resultados excesivamente repetidos o perfiles con pocas alternativas.

Estas comprobaciones complementarían los tests técnicos actuales, ya que no evaluarían únicamente si la aplicación funciona correctamente, sino también la diversidad y el equilibrio de las recomendaciones que genera.

### 8.12. Prioridades de mejora

Tras revisar el estado actual del repositorio, se han identificado cuatro mejoras principales para futuras versiones.

1. **Avisar cuando no se pueda cumplir alguna preferencia.**  
   La aplicación debería indicar claramente cuándo ha tenido que flexibilizar o descartar algún criterio seleccionado por el usuario, como la región, la variedad de uva o el perfil de sabor.

2. **Ampliar la diversidad del catálogo.**  
   Se deberían incorporar más vinos blancos, rosados y espumosos, así como vinos de regiones, denominaciones de origen y variedades de uva que actualmente tienen poca representación.

3. **Mejorar la función de vinos similares.**  
   La aplicación debería calcular la distancia entre los vinos según sus características para mostrar los más próximos al vino de referencia. Actualmente, pertenecer al mismo clúster no garantiza que sean los vinos más similares.

4. **Añadir más información sobre las valoraciones.**  
   Además del `rating`, sería conveniente incluir el número de opiniones, su procedencia y la fecha de actualización. Esto permitiría valorar mejor la fiabilidad de cada puntuación.

Estas mejoras permitirían aumentar la diversidad, la transparencia y la calidad de las recomendaciones.

## 9. Conclusiones

El análisis realizado muestra que InWine ofrece diferentes formas de recomendar vinos y facilita que personas sin conocimientos especializados puedan explorar el catálogo según sus gustos, presupuesto u ocasión.

Sin embargo, la calidad y la variedad de las recomendaciones están condicionadas por los datos disponibles. El catálogo contiene una presencia mayoritaria de vinos tintos y algunas regiones, denominaciones de origen y variedades de uva tienen mucha más representación que otras. Por ello, determinados perfiles de vino cuentan con más posibilidades de aparecer en las recomendaciones.

También se han identificado limitaciones relacionadas con el origen y la actualización de los datos. El `rating` no incluye información suficiente sobre el número o la procedencia de las valoraciones, mientras que los precios y la disponibilidad pueden cambiar con el tiempo.

Las variables sensoriales proceden de las descripciones de los vinos y se han obtenido mediante reglas basadas en palabras clave. Esto permite convertir información textual en variables utilizables por el modelo, pero puede simplificar algunos matices o no reconocer características que no aparecen expresadas claramente.

PCA y K-Means permiten reducir la información y organizar los vinos en ocho perfiles. Estos grupos son útiles para explorar el catálogo, pero no representan categorías objetivas ni garantizan que todos los vinos de un mismo clúster sean igual de similares. Además, los nombres y las interpretaciones de los perfiles han sido definidos por el equipo a partir de las características predominantes de cada grupo.

Las tres vías de recomendación no utilizan exactamente la misma lógica. El formulario aplica filtros y prioriza el `rating`; el quiz asigna un perfil mediante reglas y votos; y la recomendación conversacional combina distintos criterios de compatibilidad y calidad-precio. Por tanto, sus resultados y limitaciones deben evaluarse por separado.

InWine incorpora algunas medidas que reducen parcialmente estos riesgos, como permitir solicitar otra opción, excluir vinos ya mostrados, conservar los objetos del pipeline y utilizar una semilla fija para que los resultados sean reproducibles. 

En conclusión, InWine debe entenderse como una herramienta de orientación y descubrimiento. Sus recomendaciones pueden ayudar al usuario a encontrar vinos compatibles con sus preferencias, pero no constituyen una valoración objetiva ni garantizan la elección perfecta. La decisión final corresponde siempre al usuario.

La ampliación del catálogo, la mejora de la información disponible, la validación del quiz y una mayor transparencia sobre los criterios que no se han podido cumplir permitirían desarrollar en el futuro un sistema más diverso, comprensible y fiable.