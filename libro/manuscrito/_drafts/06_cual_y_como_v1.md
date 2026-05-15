# Capítulo 6 — Cuál y cómo: propiedades y relaciones (D3)

## Una pregunta que parece tonta

Cuando uno está empezando a modelar un dominio, llega un momento en que se enfrenta a una decisión que se siente trivial y resulta ser decisiva. Mira un dato — la edad de un paciente, el color de un auto, el autor de una canción — y se pregunta: *¿esto es una propiedad o una relación?*

La pregunta se siente tonta porque ambas palabras parecen significar cosas distintas con claridad. Una **propiedad** es algo que un objeto *tiene* (la edad, el color, el peso). Una **relación** es algo que conecta dos objetos (el autor de la canción, el médico tratante, el padre de). La intuición es: propiedades son atributos atómicos; relaciones son vínculos entre cosas.

Pero apenas se hace el ejercicio con más casos, la frontera empieza a borrarse.

- "El paciente tiene 42 años" — *propiedad* (edad: 42).
- "El paciente nació en 1984" — esto se siente como *propiedad* (fecha_nacimiento: 1984-...), pero también es una *relación* del paciente con un año.
- "El paciente vive en Buenos Aires" — *relación* (vive_en: buenos_aires), o *propiedad* (ciudad: "Buenos Aires").
- "El modelo GPT-X tiene 175B parámetros" — *propiedad* (parametros: 175e9), o *relación* del modelo con un número.
- "El modelo GPT-X fue entrenado con tal corpus" — *relación* claramente.

Si miras las dos columnas con cuidado, ves que la diferencia entre "propiedad" y "relación" no es una diferencia objetiva en el mundo. Es una diferencia en la **forma de hablar**. En castellano (y en casi todos los idiomas) decimos "tiene edad 42" y "vive en Buenos Aires" con construcciones gramaticales distintas; eso nos hace pensar que son dos clases de hechos. Pero matemáticamente — al nivel de qué información hay que almacenar — los dos hechos tienen exactamente la misma estructura: un sujeto, una predicación, un valor.

Esa observación, sostenida con disciplina, es la **decisión de diseño D3** de WQuestions: **propiedades y relaciones se unifican matemáticamente**. No son dos cosas: son dos nombres para la misma cosa.

Este capítulo explica esa unificación, qué se gana con ella, y por qué — pese a la unificación — el modelo sigue manteniendo dos ejes distintos, **P** y **M**, para los dos tipos de etiquetas. La explicación cabe en una oración: la diferencia entre P y M no es ontológica, es de **cardinalidad**.

## La estructura común: signatura

Volvamos al hecho más básico del modelo. Un hecho es una tripleta:

```
(sujeto, predicado, objeto)
```

Pongamos casos:

```
(paciente_042, edad,             42)              ∈ ?
(paciente_042, fecha_nacimiento, 1984-03-17)      ∈ ?
(paciente_042, vive_en,          buenos_aires)    ∈ ?
(modelo_gpt_x, parametros,       175_000_000_000) ∈ ?
(modelo_gpt_x, entrenado_con,    corpus_c4)       ∈ ?
```

¿En qué se diferencian estos cinco hechos estructuralmente? El sujeto siempre es un individuo de algún eje (Q u O en estos ejemplos). El objeto cae en algún eje también: el 42 en N, la fecha en T, *buenos_aires* en L, *175.000.000.000* en N, *corpus_c4* en O. El predicado — ese nombre que está en el medio — es una **etiqueta** que dice qué tipo de relación une al sujeto con el objeto.

Cada etiqueta tiene una **signatura**: dice de qué eje viene su sujeto y a qué eje va su objeto. En notación de funciones:

```
edad             : Q → N
fecha_nacimiento : Q → T
vive_en          : Q → L
parametros       : O → N      (un modelo es un objeto reificado en O)
entrenado_con    : O → O
```

La signatura es lo que el modelo conoce de antemano sobre cada etiqueta. Es lo que le permite validar que un hecho está bien formado: si alguien intenta escribir `(paciente_042, edad, buenos_aires)`, el sistema dice no — la signatura de `edad` es `Q → N`, y `buenos_aires` está en L, no en N.

Hasta acá nada nuevo: cualquier base de datos tipada hace esto. Lo interesante viene ahora.

## La distinción real: funcional o no

Mira las cinco signaturas de arriba. Cuatro de ellas son **funciones**: para un sujeto dado, la etiqueta determina un único objeto. Un paciente tiene una sola edad, una sola fecha de nacimiento, vive en una sola ciudad principal, un modelo tiene un único conteo de parámetros. La quinta — `entrenado_con` — **no** es función: un modelo puede haber sido entrenado con varios corpus distintos. Para el mismo sujeto, hay potencialmente múltiples objetos.

Esta es la única diferencia matemática real. Las etiquetas funcionales son **propiedades**; las no-funcionales son **relaciones**. Pero la diferencia no es entre dos tipos distintos de hecho: es entre dos tipos distintos de etiqueta, dentro de la misma estructura.

En el modelo, eso se traduce a dos ejes con la misma forma pero con cardinalidades distintas:

- **P** (de *Proprietas*): aloja las etiquetas funcionales. Cada hecho con etiqueta de P es único por sujeto: solo hay un `edad(paciente_042)`.
- **M** (de *Modus*): aloja las etiquetas no funcionales. Cada hecho con etiqueta de M puede repetirse: `entrenado_con(modelo_gpt_x, corpus_c4)` y `entrenado_con(modelo_gpt_x, corpus_books3)` coexisten sin conflicto.

P y M son ejes distintos por una sola razón: el motor de consulta y la lógica de actualización tratan diferente a una propiedad y a una relación. Una propiedad nueva *reemplaza* a la anterior (un paciente que cumple años pasa de tener edad 42 a tener edad 43; no se acumulan). Una relación nueva *se agrega* (un modelo entrenado con un corpus adicional simplemente añade el hecho a los que ya había).

Esa es toda la distinción. No hay nada más profundo. Y en muchos casos límite, el modelador tiene **libertad de elección**: edad puede modelarse como `Q → N` en P (un número que reemplaza al anterior cada cumpleaños), o como una relación reificada `Q → O` en M donde cada situación de "tener edad N" tiene su rango de validez vía D9. Las dos formas son legítimas. La elección depende del uso: si el sistema solo necesita la edad actual, P es más simple; si necesita historial de edades reportadas en distintos momentos, conviene la versión reificada.

## Qué se gana con la unificación

Que P y M sean matemáticamente la misma cosa — etiquetas predicativas con signatura — paga al menos cuatro veces.

**Un solo motor de consulta.** El sistema no tiene "consultas de propiedad" y "consultas de relación" como dos lenguajes distintos. Tiene una sola operación: dado un sujeto, dado un predicado, devolver objetos. Si el predicado es funcional, devuelve a lo sumo uno. Si no, devuelve los que haya. La consulta SQL tradicional, con sus *SELECT campos* (propiedades) y sus *JOIN tablas* (relaciones), se reemplaza por una sola forma uniforme.

**Un solo formato JSON.** Cuando un agente de IA pide los datos de un sujeto vía function calling, el sistema devuelve siempre la misma estructura: una lista de pares `predicado: objeto(s)`. No hay que enseñarle al agente que "edad" se accede de un modo y "entrenado_con" de otro. Es el tipo de uniformidad que hace barata la integración con LLMs.

**Un solo lugar para extender.** Agregar una etiqueta nueva al modelo no requiere decidir si va a ser "campo de tabla" o "tabla puente". Se declara su signatura y su cardinalidad en el catálogo de predicados, y el motor sabe qué hacer.

**Una sola conversación con el lenguaje natural.** En el capítulo de lexicon veremos que cada verbo del idioma se mapea a un conjunto de roles, y cada rol se traduce a una etiqueta de P o de M sin que el usuario tenga que distinguirlas. *"María vendió un libro a Juan por treinta dólares"* produce hechos sobre cinco roles: agente, tema, beneficiario, monto, moneda — y al modelo le da igual si tres de esos viven en P y dos en M, porque el formato es uniforme.

## La unificación cruzada con la realidad: tres casos

Tomemos tres dominios de la batería de pruebas del libro y veamos cómo se distribuyen las etiquetas entre P y M.

### Una receta de cocina

```
P (funcionales):
  tiempo_preparacion : O → N    (15 minutos)
  tiempo_coccion     : O → N    (45 minutos)
  porciones          : O → N    (4)
  dificultad         : O → K    (intermedia)

M (no funcionales):
  ingrediente        : O → O    (varios ingredientes por receta)
  paso               : O → O    (varios pasos)
  utensilio          : O → K    (varios utensilios)
  inspirada_en       : O → O    (puede haber varias recetas fuente)
```

La intuición se valida: lo que el sentido común llamaría "atributos de la receta" cae en P; lo que llamaría "componentes" o "vínculos" cae en M.

### Una llamada a un modelo de lenguaje

```
P:
  tokens_entrada     : O → N    (4500)
  tokens_salida      : O → N    (1200)
  latencia_ms        : O → N    (2300)
  costo_usd          : O → N    (0.018)
  modelo_usado       : O → K    (gpt-x-2026-05)
  temperatura        : O → N    (0.7)

M:
  herramienta_invocada : O → O  (varias function calls por llamada)
  fuente_documento     : O → O  (varios docs en RAG)
  parte_de             : O → O  (la llamada es parte de una sesión, que es parte de un proyecto)
```

Otra vez, lo que es atributo único de la llamada cae en P (tokens, latencia, modelo); lo que tiene cardinalidad arbitraria cae en M (herramientas invocadas, documentos fuente, jerarquía de pertenencia).

### Un partido de fútbol

```
P:
  resultado_final    : O → K    (victoria_local, victoria_visitante, empate)
  duracion_minutos   : O → N    (95)
  asistencia         : O → N    (52.000)
  arbitro_principal  : O → Q    (juan_perez)

M:
  partes             : O → V    (los dos equipos; cardinalidad fija pero múltiple)
  gol                : O → O    (varios goles por partido)
  tarjeta_amarilla   : O → O    (varias tarjetas)
  jugador_alineacion : O → Q    (22 jugadores)
```

La distinción no es siempre intuitiva: `partes` (los dos equipos) podría sentirse como propiedad porque siempre son dos, pero es no-funcional (hay dos objetos para el mismo sujeto), así que vive en M. La cardinalidad fija no la convierte en funcional.

## Una sutileza importante: el subobjeto

Hay una distinción más fina, escondida en los casos anteriores, que conviene nombrar. Cuando una etiqueta de M apunta a algo *cuya existencia es accesoria al sujeto* — un gol existe porque hay un partido, un paso existe porque hay una receta —, lo natural es que ese objeto sea una **situación reificada** (en O) que vive *dentro* del sujeto en lugar de ser un individuo independiente. El gol no es un objeto del mundo que el partido recoja; es un objeto que el partido **crea**.

Esto se modela vía la relación canónica `parte_de`:

```
(gol_001,  agente,  messi)          ∈ M(O, Q)
(gol_001,  minuto,  87)             ∈ P(O, N)
(gol_001,  parte_de, partido_arg_per) ∈ M(O, O)
```

El gol es un individuo de O — tiene UUID propio, propiedades propias, puede ser referido — pero su existencia es **contingente** al partido. Si el partido se cancela, el gol no tiene sentido.

La distinción entre "objetos del mundo" y "subobjetos contingentes" no es un eje nuevo del modelo, pero es una convención de modelado importante. La usaremos cuando lleguemos a las situaciones (capítulo 10).

## Un argumento adicional: el LLM lo encuentra natural

Hay un argumento práctico, no solo teórico, para mantener P y M unificados en su estructura. Los modelos de lenguaje grandes, entrenados sobre texto humano, no distinguen "propiedades" de "relaciones" de manera operativa. Lo que un LLM produce, cuando se le pide describir un hecho, es siempre una construcción `sujeto-predicado-objeto` (o `sujeto-predicado-objeto-modificadores`). Si el modelo subyacente al sistema espera dos tipos distintos de hechos — "los que son propiedades" y "los que son relaciones" —, el LLM tiene que aprender la distinción específica del sistema. Si el modelo acepta hechos uniformes y deja que la cardinalidad emerja del catálogo de etiquetas, el LLM no tiene que aprender nada nuevo.

En la práctica, esto se ve en function calling. Una herramienta `agregar_hecho(sujeto, predicado, objeto)` cubre tanto edad como autoría. Dos herramientas separadas `set_propiedad` y `add_relacion` son redundantes y obligan al modelo a clasificar antes de actuar. La unificación reduce el espacio de error.

## Resumen de D3

Antes de pasar al siguiente eje, vale la pena dejar la decisión D3 explícita:

> **D3 — Propiedades (P) y relaciones (M) se unifican matemáticamente como etiquetas predicativas con signatura. La diferencia entre ellas es de cardinalidad — funcional vs. no funcional — y se preserva como dos ejes distintos solo por la lógica de actualización: las propiedades reemplazan, las relaciones acumulan.**

Las consecuencias operativas:

1. Todo hecho tiene la forma `(sujeto, predicado, objeto)`, sea propiedad o relación.
2. Cada etiqueta tiene una signatura tipada que el sistema valida.
3. El motor de consulta es uno solo. El formato JSON de salida es uno solo. Las herramientas para LLMs son una sola.
4. Cuando hay duda sobre si algo es propiedad o relación, la pregunta correcta es: *¿hay un solo valor para este sujeto, o puede haber varios?* La respuesta decide el eje.
5. El subcaso especial del *subobjeto contingente* (un gol como parte de un partido) se modela como individuo de O con relación `parte_de`, no como nuevo tipo de hecho.

## Lo que viene

Con P y M cubiertos, quedan dos ejes por presentar: **K** (clase) y **el tratamiento del "por qué"**, que como vimos en la introducción no es eje sino familia canónica de relaciones en M.

El próximo capítulo se ocupa de K — el eje más sutil del modelo y, paradójicamente, el que más trabajo hace en sistemas reales. Es donde viven los tipos, las categorías, los conceptos abstractos. Es donde QUDT pone sus unidades, donde Schema.org pone sus *types*, donde una ontología de dominio cuelga su vocabulario. Es, en cierto sentido, el lugar donde WQuestions abraza a las ontologías existentes en lugar de competir con ellas.

Veremos cómo.
