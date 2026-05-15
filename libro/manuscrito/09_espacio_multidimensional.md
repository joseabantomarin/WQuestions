# Capítulo 9 — El espacio multidimensional

## Una hoja de cálculo imposiblemente grande

Imagina una hoja de cálculo con ocho columnas. Las columnas se llaman **Q, O, L, T, N, P, M, K**. Cada fila es un hecho del mundo: la celda en cada columna dice qué valor del eje correspondiente está involucrado en ese hecho. En la mayoría de las filas, varias columnas están vacías — un hecho típico solo involucra dos o tres ejes, no los ocho. Pero todas las columnas existen, y todas las filas tienen, en teoría, una posición posible en cada una.

Esa hoja de cálculo es **el espacio multidimensional de WQuestions**. Tiene 8 ejes (las columnas), y los hechos del mundo son puntos en ese espacio (las filas). Algunos puntos están densamente poblados — hechos que involucran muchos roles —, otros son rarísimos. Pero todos viven en la misma geometría.

Este capítulo se ocupa de esa geometría. No es una metáfora decorativa: es una herramienta de razonamiento que permite ver el modelo desde un punto de vista que cambia cómo se piensan las consultas, las relaciones entre dominios y la integración con sistemas de inteligencia artificial. Veámosla con detalle.

## La metáfora formal

Sea **V = Q ∪ O ∪ L ∪ T ∪ N ∪ K** el universo de individuos del modelo, y sea **L_P** y **L_M** los conjuntos de etiquetas de propiedad y de relación. Llamamos **espacio WQuestions** al producto cartesiano (parcial) sobre los ocho ejes:

```
E_W = Q × O × L × T × N × P × M × K
```

Un punto en este espacio es una tupla con, idealmente, un valor en cada eje. Pero la mayoría de los hechos del mundo no necesitan los ocho ejes — un hecho como *"Messi marcó un gol"* solo involucra Q (Messi), O (el gol) y, posiblemente, M (la relación `agente`). Los demás ejes quedan **sin asignar**.

Por eso es más útil pensar en el espacio como una **estructura parcial**: cada hecho ocupa solo las dimensiones que necesita. La afirmación del modelo no es que todo hecho viva en el centro de un cubo de ocho dimensiones; es que cualquier hecho que tenga lugar en el mundo puede **ubicarse** en ese cubo, dejando las dimensiones irrelevantes sin tocar.

Esa "ubicación parcial" se vuelve concreta cuando los hechos se acumulan: el grafo entero de hechos forma una nube de puntos densamente conectados por sus dimensiones compartidas. Si dos hechos comparten el mismo valor de O — porque ambos hablan del mismo gol —, están conectados por esa dimensión. Si tres hechos comparten valor de T — porque ocurrieron el mismo día —, también. La estructura de conexiones es lo que da forma al espacio.

## Tres diferencias con un espacio matemático clásico

El espacio WQuestions no es un espacio ℝⁿ clásico, ni un cubo OLAP de inteligencia de negocios, ni un espacio vectorial de embeddings. Comparte con todos ellos la idea de "varias dimensiones que coordenan información", pero se diferencia en tres puntos cruciales.

**Diferencia 1: el espacio es parcial.** En un ℝⁿ clásico, todo punto tiene un valor en cada dimensión. En WQuestions, un hecho típico tiene valor en dos o tres ejes; los demás quedan vacíos. La consulta *"todos los goles"* no exige que cada gol tenga un valor de N o de L; simplemente no se piden.

Esto tiene consecuencias prácticas. El sistema no necesita inventar valores nulos o "desconocidos" para llenar dimensiones que no aplican. Si una receta no tiene `dificultad` declarada, no hay un "punto cero" en esa dimensión: simplemente no hay hecho en esa coordenada. La diferencia entre "valor desconocido" y "valor inaplicable" se vuelve operativa en lugar de filosófica.

**Diferencia 2: el espacio es multi-valuado en ciertas dimensiones.** En ℝⁿ, cada punto tiene exactamente un valor por dimensión. En WQuestions, las dimensiones que corresponden a relaciones (M) admiten múltiples valores para el mismo sujeto. Un partido tiene dos equipos como `partes`; una llamada a un LLM tiene varias herramientas como `herramienta_invocada`; una receta tiene muchos `ingrediente`.

Esta multivalualidad es lo que llamamos "no funcional" en el capítulo 6. Geométricamente significa que un punto de la nube puede tener **varias coordenadas en el mismo eje**, lo cual rompe la analogía con espacios cartesianos puros pero es exactamente lo que hace falta para describir el mundo.

**Diferencia 3: cada eje es de un tipo distinto.** Las dimensiones de ℝⁿ son intercambiables — todas son números reales. Las dimensiones de WQuestions no: una contiene agentes (Q), otra fechas (T), otra magnitudes (N), otra conceptos abstractos (K). No es legal sumar un valor de Q con uno de T. El espacio es **tipado**, lo cual lo hace más restrictivo pero también más informativo: cada coordenada lleva implícita la naturaleza de lo que representa.

## La hoja de cálculo dispersa

La forma más concreta de visualizar el espacio es como una **hoja de cálculo dispersa**: ocho columnas (los ejes), miles o millones de filas (los hechos), y la mayoría de las celdas vacías.

Cuatro hechos en formato tabular, mezclando dominios:

| Hecho | Q | O | L | T | N | P/M | K |
|---|---|---|---|---|---|---|---|
| Receta cocinada | juan | preparacion_017 | cocina_casa | 2026-05-14T20:00 | — | cocinero | risotto |
| Gol marcado | messi | gol_001 | estadio_lima | 2026-10-14T20:23 | 87 | agente | gol_jugada_abierta |
| Llamada API | — | llamada_042 | — | 2026-05-14T10:32 | 4500 | tokens_entrada | llamada_modelo_lenguaje |
| Decreto firmado | ministro_017 | decreto_007 | sede_gobierno | 2026-05-14 | 50_000_000 | firmante | decreto_ejecutivo |

Las cuatro filas viven en el mismo espacio. La columna L está vacía en una fila (la llamada API es virtual, no tiene lugar físico claro). La columna Q está vacía en otra (la llamada API no tiene un agente humano explícito; o más bien, ese rol se modela aparte). Pero la **estructura es uniforme**: cualquier consumidor — humano o LLM — puede leer la tabla y entender qué dice cada fila sin saber de qué dominio viene.

![Cuatro hechos de cuatro dominios distintos viven en la misma estructura tabular. Las celdas vacías son la norma: el espacio es parcial por diseño.](../diagrams/png/15_hoja_dispersa.png)

Esa uniformidad es lo que permite que las consultas crucen dominios sin esfuerzo. Una consulta como *"todos los eventos del 14 de mayo de 2026"* simplemente filtra la columna T y devuelve las cuatro filas. Sin importar que tres sean de dominios distintos. Sin necesidad de un mapeo ad-hoc entre tablas heterogéneas.

## Consultas como restricciones geométricas

Si los hechos son puntos en un espacio, las consultas son **subconjuntos** de ese espacio definidos por restricciones sobre las coordenadas. La formulación general:

```
consulta = { hecho ∈ E_W : hecho.eje_i = valor_i,  para cada eje fijado }
```

Tres tipos de consulta canónicos:

**1. Punto fijo en un eje, libre en otros.** *"Todos los hechos donde Messi es protagonista."* Se fija Q = messi (en la posición de sujeto o de objeto, según el rol). Los demás ejes quedan libres.

**2. Intervalo en un eje numérico o temporal.** *"Todos los hechos entre el 1 de mayo y el 31 de mayo."* Se restringe T a un intervalo. Los demás ejes quedan libres.

**3. Conjunción de restricciones en múltiples ejes.** *"Todos los goles de Messi en partidos de Argentina en 2026."* Se restringen Q (messi como agente), K (instancia_de = gol), y T (2026). El espacio resultante es la intersección de las tres restricciones.

Geométricamente esto es **slicing**: cada restricción "corta" el espacio en un sub-espacio de menor dimensión, y la consulta es la intersección de los cortes. La misma operación, en cualquier dominio. Que es exactamente la promesa del modelo: una sola sintaxis de consulta para todos los hechos del mundo.

## Comparación con tres espacios multidimensionales conocidos

Para entender bien qué es WQuestions, conviene contrastarlo con tres espacios multidimensionales que el lector probablemente conoce.

**Cubos OLAP de inteligencia de negocios.** Un cubo OLAP tiene dimensiones (tiempo, geografía, producto, cliente) y métricas (ventas, costos, márgenes) que se agregan por las dimensiones. Estructura familiar: las filas viven en celdas indexadas por la combinación de dimensiones. Diferencia con WQuestions: el cubo OLAP es **homogéneo por dominio** — un cubo de ventas, un cubo de logística, un cubo de RRHH —, mientras que WQuestions es **un único cubo para todos los dominios**, con dimensiones (ejes) abstractas en lugar de específicas. Es como pasar de muchos cubos pequeños a un cubo universal donde los dominios son distinciones secundarias.

**Espacios conceptuales de Gärdenfors [13].** Gärdenfors propuso que los conceptos viven en espacios geométricos donde las dimensiones son cualidades continuas (matiz, saturación y luminosidad para el espacio de colores; pitch, timbre, intensidad para el espacio musical). Los conceptos son **regiones convexas** en ese espacio. WQuestions hereda la metáfora de las dimensiones como ejes, pero las trata como **discretas y simbólicas** en lugar de continuas y geométricas. Los conceptos no son regiones; son individuos (en K) con sus propias propiedades. Y el espacio no es para conceptos; es para **hechos** que involucran conceptos. Las dos teorías se complementan en lugar de competir: Gärdenfors describe cómo se aprenden y se categorizan los conceptos; WQuestions describe cómo se organizan los hechos que los usan.

**Espacios vectoriales de embeddings.** Cuando un modelo de lenguaje "entiende" una palabra, la representa internamente como un vector denso de cientos o miles de dimensiones. Esos vectores viven en un espacio donde la distancia coseno entre dos puntos mide similitud semántica: *"rey"* está cerca de *"reina"*, lejos de *"banana"*. La similitud con WQuestions termina en que ambos son multidimensionales y simbólicos. La diferencia es de naturaleza: el espacio de embeddings es **opaco** (no sabemos qué significa cada dimensión, solo emerge del entrenamiento), mientras que el espacio WQuestions es **transparente** (cada eje tiene un significado predefinido). Un LLM puede usar los dos al mismo tiempo: razona internamente en el espacio de embeddings, pero almacena y consulta el conocimiento estructurado en el espacio WQuestions. **Los dos no se reemplazan, se complementan**, y es esa complementariedad la que hace prometedora la combinación de LLMs con grafos de conocimiento estructurados.

![Cuatro espacios multidimensionales comparados. Cubos OLAP, espacios conceptuales y embeddings comparten con WQuestions la idea de varias dimensiones, pero difieren en granularidad, transparencia y propósito.](../diagrams/png/16_comparacion_espacios.png)

## Una propiedad cualitativa: la densidad emergente

Hay una propiedad del espacio que no es matemática pero sí cualitativa, y vale la pena nombrarla. A medida que un sistema acumula hechos, ciertas **regiones del espacio se vuelven densas** — muchos hechos comparten valores en ciertos ejes — y otras quedan vacías. La densidad emergente refleja la estructura real del mundo modelado.

Un sistema de gestión hospitalaria desarrolla densidad en las regiones donde aparecen pacientes (Q), consultas (O), fechas (T) y diagnósticos (K). Un sistema de inteligencia artificial conversacional desarrolla densidad en las regiones donde aparecen llamadas (O), modelos (K), tokens (N), latencias (N) y herramientas (O). Cada dominio "ocupa" una zona del espacio sin desplazar a los demás.

Esta propiedad es la que hace posible la **federación entre dominios**: cuando el sistema hospitalario y el sistema de IA conversacional comparten un mismo espacio, una zona puede empezar a llenarse — por ejemplo, "llamadas a un asistente médico para sugerir diagnósticos" — sin que ninguno de los dos sistemas haya tenido que rediseñar su estructura. La nueva intersección es un punto en el mismo espacio donde ya viven los hechos anteriores.

La densidad emergente es también lo que permite **explicar** un sistema sin documentación: si una zona del espacio está densamente poblada, sabes qué le importa al sistema; si está vacía, sabes qué no. Es una forma de observabilidad arquitectónica.

## Lo que el espacio NO es

Es útil ser explícito sobre tres cosas que el espacio WQuestions **no** es, para evitar confusiones:

1. **No es una métrica.** No hay "distancia" intrínseca entre dos hechos. Que dos hechos compartan valor en un eje los conecta, pero no establece una magnitud de cercanía. Para análisis de similitud cuantitativa hay que recurrir a otros formalismos (Gärdenfors, embeddings) y proyectar.

2. **No es un esquema de almacenamiento.** El espacio es una abstracción de razonamiento. Físicamente, los hechos pueden almacenarse como filas en SQL, documentos en JSON, tripletas en RDF, aristas en un grafo, o lo que prefiera el ingeniero. La metáfora del espacio no obliga a una implementación particular.

3. **No es un universo cerrado.** Decir que un dominio "vive en el espacio" no significa que el dominio esté completo o que no haya más por modelar. Significa que **todo lo que se modele del dominio aterriza en alguna región del espacio**. Lo no modelado simplemente está fuera del subconjunto de hechos cargados, no del espacio en sí.

## El espacio y los agentes de IA

Una observación final que une la metáfora del capítulo con la temática del libro.

Cuando un agente de inteligencia artificial — un LLM con function calling, por ejemplo — opera sobre un grafo de hechos en WQuestions, lo hace navegando este espacio. Una herramienta como `agregar_hecho` deposita un punto nuevo en el espacio; `consultar` recorta una región; `inferir` agrega puntos derivados de los existentes. La operación del agente es, literalmente, una serie de movimientos en una geometría compartida.

Y esa geometría es la misma que el agente ya conoce de su entrenamiento: el lenguaje natural distribuye sus oraciones en las mismas ocho dimensiones (quién, qué, dónde, cuándo, cuánto, cuál, cómo, qué tipo). El agente no aprende un espacio nuevo cuando interactúa con WQuestions; **encuentra explícita la estructura que su entrenamiento ya tenía implícita**.

Es la misma intuición que el capítulo 4 cerró con la anécdota del coche y el autolavado: cuando el espacio está estructurado, el agente no puede perder un pilar de vista. El espacio multidimensional es la formalización de ese andamio cognitivo.

## Lo que viene

Hasta aquí hemos visto la pieza mínima (el hecho atómico) y el espacio donde se ubica (el espacio multidimensional). En el próximo capítulo nos detenemos en una clase especial de individuos del espacio: las **situaciones reificadas**. Son los puntos articuladores del grafo — donde muchos hechos convergen porque hablan de lo mismo —, y donde el modelo gana su capacidad de hablar de eventos complejos, contextos, validez temporal y propósito.

El capítulo 10 se ocupa de eso.
