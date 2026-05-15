# Capítulo 8 — El hecho atómico

## La unidad mínima

En los capítulos anteriores estuvimos presentando los ejes uno por uno, como si fueran piezas separadas de un rompecabezas. Es hora de mostrar la pieza que hace que el rompecabezas tenga sentido. Esa pieza no es ninguno de los ejes; es **lo que se construye con ellos**.

Se llama **hecho atómico** y su forma es desarmadora de tan simple:

```
hecho = (sujeto, predicado, objeto)
```

Tres campos. El sujeto y el objeto son individuos de algún eje. El predicado es una etiqueta que vive en P (si es propiedad) o en M (si es relación). Eso es todo. **Todo lo que el modelo sabe del mundo se compone, hecho a hecho, con esta forma.**

La afirmación se siente exagerada al principio. ¿Todo? ¿Las recetas, los goles, las canciones, los decretos, las llamadas a un LLM, las historias clínicas, los partidos de fútbol? Sí, todo. Y este capítulo se ocupa de demostrarlo: muestra por qué el hecho atómico basta, qué se gana al insistir en esa atomicidad, cómo se compone para describir cosas complejas, y por qué la forma resulta ser exactamente la que un LLM produce naturalmente cuando se le pide describir algo.

## La forma

Un hecho atómico es una tripleta. Cuatro ejemplos para empezar, uno por cada dominio que venimos siguiendo:

```
(receta_risotto,    tiempo_coccion,    45)              ∈ P(O, N)
(gol_001,           agente,            messi)           ∈ M(O, Q)
(cancion_yesterday, compositor,        mccartney)       ∈ P(O, Q)
(decreto_017,       fecha_publicacion, 2026-05-14)      ∈ P(O, T)
(llamada_api_042,   tokens_entrada,    4500)            ∈ P(O, N)
```

Cinco hechos atómicos. Cinco dominios. Cinco predicados distintos. Pero **la misma forma**. Ese es el primer mensaje del capítulo: la uniformidad no es decorativa, es la propiedad estructural más importante del modelo.

![Cinco hechos atómicos en cinco dominios distintos: misma forma sujeto-predicado-objeto, distintos tipos de individuos en cada eje. Las flechas azules son predicados de P (funcionales); las ámbar son de M (no funcionales).](../diagrams/png/13_hecho_atomico.png)

Veamos por qué.

## Tres exigencias que el hecho atómico cumple

Para que la unidad mínima funcione como base de una arquitectura universal, tiene que satisfacer tres exigencias acumulativas:

**Exigencia 1: tipada.** Cada hecho lleva implícita una signatura. El predicado `tiempo_coccion` *sabe* que su sujeto debe vivir en O y su objeto en N. Si alguien intenta `(receta_risotto, tiempo_coccion, "rojo")`, el sistema lo rechaza: "rojo" está en K, no en N. La signatura convierte una tripleta opaca en un hecho validable.

**Exigencia 2: independiente.** Cada hecho atómico se sostiene por sí solo. No hace falta consultar otros hechos para entenderlo. `(gol_001, agente, messi)` significa lo mismo se acompañe o no de `(gol_001, minuto, 87)`. Esta independencia permite que los hechos vivan distribuidos en cualquier almacén — JSON files, base relacional, triple store, grafo de propiedades — sin perder semántica.

**Exigencia 3: componible.** Aunque cada hecho sea independiente, los hechos *se combinan* sobre sujetos compartidos para describir cosas complejas. La receta no se "describe" en un solo hecho; se describe con varios hechos que comparten `receta_risotto` como sujeto:

```
(receta_risotto, instancia_de,      receta)              ∈ M(O, K)
(receta_risotto, tiempo_coccion,    45)                  ∈ P(O, N)
(receta_risotto, unidad_tiempo,     minuto)              ∈ P(O, K)
(receta_risotto, porciones,         4)                   ∈ P(O, N)
(receta_risotto, ingrediente,       arroz_arborio)       ∈ M(O, K)
(receta_risotto, ingrediente,       caldo_vegetal)       ∈ M(O, K)
(receta_risotto, ingrediente,       azafran)             ∈ M(O, K)
(receta_risotto, dificultad,        intermedia)          ∈ P(O, K)
```

Ocho hechos atómicos describen la receta. Cada uno se entiende por separado. Juntos, dibujan el objeto completo.

La operación inversa también vale: si la receta se vuelve "más detallada" — alguien quiere agregar las cantidades exactas de cada ingrediente —, **no hace falta cambiar la estructura del modelo**. Se agregan más hechos atómicos. Por ejemplo, reificando cada ingrediente como una situación con cantidad y unidad:

```
(uso_arroz_001,  parte_de,    receta_risotto)            ∈ M(O, O)
(uso_arroz_001,  ingrediente, arroz_arborio)             ∈ M(O, K)
(uso_arroz_001,  cantidad,    320)                       ∈ P(O, N)
(uso_arroz_001,  unidad,      gramo)                     ∈ P(O, K)
```

La estructura no cambia. Solo crecen los hechos. Esta es una propiedad enorme: **el modelo escala por acumulación de tripletas, no por refactor de esquema**.

## El grafo de hechos

Cuando los hechos atómicos se acumulan, se forma un grafo. Cada individuo de V es un nodo; cada hecho es una arista etiquetada que lo conecta con otro individuo. Una base de conocimiento WQuestions es, literalmente, **un conjunto finito de hechos atómicos** — ni más ni menos.

Esto importa porque significa que el "estado del mundo según el sistema" se reduce a contar y proyectar tripletas. No hay archivos, índices secundarios, vistas materializadas, schemas escondidos. Solo tripletas. Si alguien necesita responder *"¿quién compuso Yesterday?"*, lo único que necesita es buscar tripletas con sujeto `cancion_yesterday` y predicado `compositor`. Si necesita *"¿qué compositores escribieron canciones después de 1960?"*, busca tripletas con predicado `año_composicion`, filtra las que tengan objeto > 1960, sigue al sujeto-canción, busca su `compositor`. Cada paso es una consulta sobre tripletas. Nada más.

## Reificación: cuando una tripleta no alcanza

Hay un caso donde una sola tripleta parece insuficiente: cuando lo que se quiere decir tiene **más de dos participantes** o **propiedades propias del enlace**.

> *"Messi le pasó el balón a Di María en el minuto 87 con un toque de pierna izquierda."*

Esa oración tiene cinco roles: agente (Messi), beneficiario (Di María), objeto (balón), tiempo (minuto 87), instrumento (pierna izquierda). Una tripleta `(messi, pasar_a, di_maria)` retiene dos, pierde tres. ¿Cómo se modela el conjunto?

La respuesta es **reificación**: subir el evento al estatus de individuo en O, darle un identificador propio, y conectar a sus participantes con tripletas separadas.

```
(pase_001, instancia_de,  accion_pasar)                  ∈ M(O, K)
(pase_001, agente,        messi)                         ∈ M(O, Q)
(pase_001, beneficiario,  di_maria)                      ∈ M(O, Q)
(pase_001, objeto_pase,   balon_partido_001)             ∈ M(O, O)
(pase_001, minuto,        87)                            ∈ P(O, N)
(pase_001, instrumento,   pierna_izquierda)              ∈ P(O, K)
```

Lo que era una oración compleja se descompone en seis hechos atómicos. Cada uno individualmente verificable, cada uno consultable, cada uno componible con el resto.

![El pase de Messi reificado como individuo en O y sus seis participantes conectados por roles canónicos: agente, beneficiario, objeto, instrumento, minuto, momento. La estructura n-aria se preserva sin abandonar la forma de tripleta.](../diagrams/png/14_evento_reificado.png)

Esta es la propiedad que conecta WQuestions con la semántica neo-davidsoniana [12]: los eventos son individuos de primera clase, no relaciones puras. Davidson lo formuló filosóficamente en 1967; el modelo lo absorbe como mecánica operativa estándar.

La regla práctica, que ya vimos en los capítulos previos pero conviene repetir aquí: **se reifica solo cuando hace falta**. Si la relación tiene exactamente dos participantes y ninguna propiedad propia, una tripleta plana basta. Si tiene más participantes o si va a recibir propiedades propias (tiempo, lugar, modo), se reifica.

## Tipos de hecho según los ejes de sus extremos

El modelo no produce hechos en abstracto; los produce con tipos. La signatura del predicado dice qué ejes pueden ocupar el sujeto y el objeto. Veamos las combinaciones más frecuentes con ejemplos:

```
Q → Q     (messi, hermano_de, matias)
Q → O     (juan, paciente_en, consulta_017)
Q → L     (maria, vive_en, ciudad_marina)
Q → T     (paciente_042, fecha_nacimiento, 1984-03-17)
Q → N     (juan, edad, 42)
Q → K     (maria, profesion, medica)

O → Q     (gol_001, agente, messi)
O → O     (gol_001, parte_de, partido_arg_per)
O → L     (consulta_017, lugar, consultorio_05)
O → T     (decreto_017, fecha_publicacion, 2026-05-14)
O → N     (llamada_api_042, latencia_ms, 2300)
O → K     (cancion_yesterday, genero, pop_rock)

K → K     (transformer, subtipo_de, modelo_de_lenguaje)
K → K     (casado, opuesto_de, soltero)
```

La lista no es exhaustiva. Hay combinaciones con L, T, N como sujetos (raras pero posibles). Lo importante es que **cualquier hecho del mundo que pueda enunciarse en lenguaje natural se traduce a una o varias tripletas tipadas** sobre este zoológico de combinaciones. Es la operacionalización del programa.

## Por qué el LLM produce hechos atómicos naturalmente

Hay una observación curiosa que vale la pena hacer explícita. Cuando se le pide a un modelo de lenguaje que describa un evento, el modelo produce *casi siempre*, sin que se lo pidamos, una estructura de tripletas. Pídele a GPT, Claude o Llama: *"describe quién hizo qué en esta noticia"* y la respuesta tipo es:

```
- El ministro firmó el decreto.
- El decreto entra en vigor en 30 días.
- El decreto asigna 50 millones de dólares.
- La medida afecta a tres ministerios.
```

Cuatro líneas, cuatro hechos. Cada línea con su sujeto, su predicado, su objeto. El LLM no aprendió esto porque alguien le enseñó WQuestions: lo aprendió porque **así habla el lenguaje natural cuando describe hechos**. Las oraciones simples del lenguaje (sujeto + verbo + complemento) son exactamente la forma de un hecho atómico tipado.

Esto tiene una consecuencia práctica fuerte. Si los hechos del mundo se almacenan como tripletas con signaturas, y si los LLMs producen tripletas con signaturas implícitas cuando hablan, **la interfaz entre lenguaje natural y la base es trivial**. No hay parser sofisticado; no hay capa de NLP profunda; hay un mapeo casi directo entre lo que el LLM dice y lo que el modelo guarda.

Esa trivialidad es lo que hace posible el escenario que el libro persigue: un agente de inteligencia artificial que conversa, lee y escribe sobre cualquier dominio sin que cada dominio le exija aprender un esquema nuevo. Function calling termina pareciéndose más a *"agregar este hecho atómico al grafo"* que a *"llamar a la API específica con sus 17 parámetros y validaciones particulares"*.

## Consultar es invertir el hecho

Si los hechos del mundo se almacenan como tripletas, las consultas son **tripletas con huecos**. La forma básica:

```
consulta = (sujeto, predicado, objeto)   donde alguno de los tres es ?
```

Tres patrones canónicos:

```
(messi, ?,           ?)        →  todo lo que sabemos de Messi
(?,     compositor,  mccartney) →  qué cosas tienen a McCartney como compositor
(?,     agente,      messi)     →  todas las situaciones donde Messi actuó
```

Los huecos pueden ser múltiples y pueden tener restricciones de tipo:

```
(?O,    agente,      messi)     →  solo cosas en O con Messi como agente
(?Q,    pais,        argentina) →  personas argentinas
```

Una consulta más rica se compone como **conjunción de tripletas-con-huecos**:

```
(?gol,  agente,      messi)
(?gol,  parte_de,    ?partido)
(?partido, fecha,    [2026-01-01, 2026-12-31])
→ todos los goles de Messi en partidos de 2026
```

Tres tripletas con huecos coordinados (`?gol` aparece en dos; `?partido` aparece en dos). La consulta se resuelve buscando asignaciones de los huecos que hagan que las tres tripletas existan en el grafo.

Es decir: **consultar es buscar el patrón en el grafo de hechos**. La misma operación, en cualquier dominio, en cualquier escala. Que es exactamente lo que la "torre de Babel" del capítulo 1 no permitía.

## El hecho atómico y los cuatro dominios

Cerremos el capítulo viendo el hecho atómico aplicado a los cuatro dominios que vinimos siguiendo, más el caso de IA.

**Receta:** ya lo hicimos arriba. Ocho hechos describen la receta a alto nivel; reificación de cada ingrediente agrega detalle.

**Gol de fútbol:**

```
(gol_001, instancia_de,  gol_jugada_abierta)
(gol_001, agente,        messi)
(gol_001, asistente,     di_maria)
(gol_001, parte_de,      partido_arg_per_2026)
(gol_001, minuto,        87)
(gol_001, pierna,        zurda)
```

Seis hechos. El gol está descripto con suficiente detalle para estadísticas tácticas, sin reducirlo a una fila de planilla.

**Canción:**

```
(cancion_yesterday, compositor,    mccartney)
(cancion_yesterday, año_creacion,  1965)
(cancion_yesterday, album,         help)
(cancion_yesterday, tonalidad,     fa_mayor)
(cancion_yesterday, duracion_seg,  125)
```

Una composición en cinco hechos. Bastan para que un sistema de recomendación cruce: "todas las canciones compuestas por McCartney antes de 1970 en tonalidad mayor".

**Noticia política (un decreto):**

```
(decreto_017, instancia_de,    decreto_ejecutivo)
(decreto_017, firmante,        ministro_017)
(decreto_017, fecha_firma,     2026-05-14)
(decreto_017, entra_en_vigor,  2026-06-13)
(decreto_017, presupuesto,     50_000_000)
(decreto_017, moneda,          dolar)
(decreto_017, afecta_a,        ministerio_salud)
(decreto_017, afecta_a,        ministerio_educacion)
(decreto_017, afecta_a,        ministerio_trabajo)
```

Una decisión política, nueve hechos. La consulta "¿qué decretos firmó el ministro 017 en 2026?" cruza dos tripletas.

**Llamada a un LLM:**

```
(llamada_042, instancia_de,    llamada_modelo_lenguaje)
(llamada_042, modelo,          gpt_x_2026_05)
(llamada_042, agente_usuario,  juan)
(llamada_042, tokens_entrada,  4500)
(llamada_042, tokens_salida,   1200)
(llamada_042, latencia_ms,     2300)
(llamada_042, costo_usd,       0.018)
(llamada_042, temperatura,     0.7)
(llamada_042, herramienta_usada, busqueda_web)
(llamada_042, herramienta_usada, lectura_archivo)
```

Diez hechos describen la llamada con todo lo que un sistema de observabilidad necesita: a quién atendió, qué modelo, cuánto tomó, cuánto costó, qué herramientas se usaron. Cada uno consultable; ninguno acoplado a un schema particular del proveedor.

## Resumen del capítulo

El hecho atómico es la unidad mínima del modelo. Tiene una forma fija — *(sujeto, predicado, objeto)* — con signatura tipada de predicado. Acumulando hechos se describe cualquier cosa: cosas simples con pocos, cosas complejas con muchos, eventos n-arios mediante reificación. Una base de conocimiento es un conjunto de hechos; una consulta es una tripleta con huecos.

La forma coincide con la forma natural en que el lenguaje humano describe hechos, que es por lo cual los modelos de lenguaje producen estructuras compatibles sin esfuerzo. Y esa coincidencia es el punto: el modelo no impone una estructura ajena al lenguaje, sino que **explicita la que el lenguaje ya tiene**.

## Lo que viene

Hasta aquí el modelo se ha presentado como una arquitectura de hechos discretos. El próximo capítulo da un giro de perspectiva: muestra que los hechos atómicos, vistos en conjunto, forman un **espacio multidimensional** — y que ese espacio tiene propiedades geométricas que permiten pensar las consultas como restricciones sobre coordenadas.

No es solo una metáfora. Es una herramienta de razonamiento que ayuda a entender por qué el modelo es uniforme, por qué es eficiente, y por qué el mismo lenguaje de consulta sirve para cualquier dominio. Lo veremos en el capítulo 9.
