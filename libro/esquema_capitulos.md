# Esquema detallado de capítulos

Cada capítulo se describe con: **tesis del capítulo**, **3-5 puntos clave**, **cómo abre**, **cómo cierra**, y **material fuente** del proyecto.

---

## PARTE I — POR QUÉ LAS PREGUNTAS

### Capítulo 1 — El problema: la torre de Babel de las ontologías

**Tesis**: cada dominio inventa su propio vocabulario para describir el mundo, y eso impide que la información dialogue.

Puntos clave:
- Cuatro modelos del mismo hecho (venta, viaje, consulta médica) en cuatro sistemas distintos. Mismo evento, cuatro nomenclaturas incompatibles.
- El costo de la heterogeneidad: integradores, ETLs, errores, retrabajos. Anécdotas industriales (Biolink, Mars Climate Orbiter, Healthcare interoperability).
- Por qué los intentos previos fallaron: ontologías de dominio capturan profundidad pero pierden ancho; OpenIE captura ancho pero pierde estructura.
- La pregunta del libro: ¿hay una raíz común a todas las descripciones del mundo?

Abre con: anécdota concreta (un médico que no puede ver la historia clínica de un paciente porque cada hospital usa un esquema distinto).
Cierra con: la promesa del libro de proponer una respuesta operativa.

Fuente: contexto general + `related/yang-hu-5w1h.md` (motivación) + `related/universal-schema-biolink.md`.

### Capítulo 2 — Aristóteles, el periodismo y la cognición: las preguntas como invariantes

**Tesis**: las mismas preguntas que organizan una nota periodística son las que organizan la cognición humana — y aparecen una y otra vez en la historia.

Puntos clave:
- Aristóteles: las "circunstancias" del acto moral (quién, qué, cómo, dónde, cuándo, por qué, para qué).
- 5W1H en periodismo (siglo XX): Hermes inspirado en Cicerón.
- Las preguntas-W en lingüística indoeuropea: cómo todos los idiomas conservaron la misma familia.
- Cognición infantil: el orden en que aparecen las preguntas en niños (qué → quién → dónde → cuándo → por qué → cómo).
- Hipótesis: las preguntas son invariantes cognitivos, no convenciones culturales.

Abre con: el ejercicio de un curso de periodismo de 1917 anotando los 5W1H.
Cierra con: si las preguntas son invariantes, deberían ser una buena base para arquitectura universal.

Fuente: `related/yang-hu-5w1h.md`, Wikipedia sobre Five Ws, lectura adicional sobre semántica indoeuropea.

### Capítulo 3 — Lo que ya intentamos: 5W1H, RDF, ontologías de dominio

**Tesis**: hay tres tradiciones que se aproximaron al problema; ninguna lo cerró. Vale la pena entender por qué.

Puntos clave:
- 5W1H como metodología (Yang & Hu, Mahmood): excelente como guía heurística pero no como arquitectura de datos.
- RDF y el Semantic Web: poderoso pero abierto a tal punto que no resuelve la diversidad de vocabularios.
- Ontologías de dominio (CIDOC CRM, Biolink, Schema.org): profundas dentro de su dominio pero requieren puentes ad-hoc.
- Lo que falta: un esquema universal **fijo, explícito, y simple** que sirva de canónico común.

Abre con: la tabla de la sección "Otros precedentes" del `WQuestions.md`.
Cierra con: la propuesta del libro encajando entre esos tres.

Fuente: `related/yang-hu-5w1h.md`, `related/cidoc-crm.md`, `related/rdf-and-reification.md`, `related/universal-schema-biolink.md`.

---

## PARTE II — LAS OCHO COORDENADAS

### Capítulo 4 — Quién, qué, dónde, cuándo: los cuatro pilares

**Tesis**: cuatro preguntas son universales en cualquier descripción del mundo. Comencemos por ahí.

Puntos clave:
- **Q (quién)**: agentes capaces de acción. Por qué la agencia es contextual (D5).
- **O (qué)**: objetos, cosas, eventos, situaciones. El qué que se vuelve evento.
- **L (dónde)**: ubicaciones. La distinción ubicación-organización.
- **T (cuándo)**: momentos. Pluralidad de tiempos (reloj, narrativo, musical).
- Por qué estos cuatro no bastan, anticipando los otros cuatro.

Abre con: la oración "Juan le dio un libro a María ayer en su casa".
Cierra con: la pregunta "¿y cuánto cuesta el libro?" — adelantando N.

Fuente: secciones 1 y 2 (D1–D5) de `WQuestions.md`.

### Capítulo 5 — Clase: el zócalo categórico (K)

**Tesis**: además de los individuos concretos hay categorías. K es el segundo zócalo del modelo, presentado temprano porque casi todo lo que sigue lo necesita.

Puntos clave:
- Los cuatro pilares alojan instancias; faltan las categorías.
- Cuatro familias en K: tipos, unidades, estados enumerativos, nomenclaturas.
- Tres razones para que K sea eje propio: estructura interna, autoridad externa (URIs), consultas habituales.
- `instancia_de` y `subtipo_de` como relaciones canónicas; cierre transitivo.
- K como zócalo para ontologías existentes (Schema.org, QUDT, SNOMED, CIDOC CRM, Biolink).
- D4: K son conceptos atemporales; O son entidades creadas/situadas.

Abre con: lo que los cuatro pilares dejan sin decir — Marta y su sobrino son ambos *personas*, pero los pilares no nos dejan decir esto explícitamente.
Cierra con: anuncio de N — los números necesitan unidades, y las unidades viven en K.

Fuente: secciones 1 y 2 (D4) de `WQuestions.md`, `related/cidoc-crm.md`.

### Capítulo 6 — Cuánto: el eje cuantitativo y sus trampas

**Tesis**: los números aparecen transversalmente y tienen sus propias peculiaridades — unidades, conversiones, incertidumbre.

Puntos clave:
- N como eje de valor (no de entidad).
- Magnitudes vs cardinalidad.
- El problema de las unidades. Mars Climate Orbiter + confusión de tokens en producción.
- QUDT como vocabulario canónico (anclado en K, ya presentado en cap 5).
- Unidades emergentes de IA: token, parámetros, perplexity, costo por millón de tokens.
- Cuándo reificar una medición.
- Incertidumbre como rango o distribución reificada.

Abre con: dos historias paralelas de confusión de unidades.
Cierra con: anuncio de P y M — los conectores que faltan.

Fuente: `WQuestions.md` (convención de mediciones), `related/qudt-measurements.md`.

### Capítulo 7 — Cuál y cómo: los predicados (P y M)

**Tesis**: con el universo de valores completo (Q, O, L, T, N, K) falta lo que los conecta: los predicados. P y M son ejes estructuralmente idénticos que se distinguen solo por cardinalidad.

Puntos clave:
- El universo está completo pero las cosas siguen sueltas; faltan los enlaces.
- Forma común: signatura tipada `predicado : eje_sujeto → eje_objeto`.
- La distinción real entre P y M es de cardinalidad (funcional vs no funcional).
- D3: unificación algebraica con preservación de dos ejes por lógica de actualización.
- Cuatro consecuencias prácticas (motor de consulta único, JSON único, extensibilidad, LLM-friendly).
- Tres dominios cruzados (receta, llamada a LLM, partido de fútbol).
- Subobjeto contingente: `parte_de` como puente a las situaciones reificadas.

Abre con: la pregunta que parece tonta — ¿esto es propiedad o relación?
Cierra con: el inventario de los ocho ejes completo; puente a la Parte III.

Fuente: secciones 1 y 2 (D3) de `WQuestions.md`, `related/neo-davidsonian.md`.

---

## PARTE III — CÓMO FUNCIONAN JUNTAS

### Capítulo 8 — El hecho atómico: la unidad mínima

**Tesis**: la información se descompone en triples tipo (sujeto, etiqueta, valor). Una situación es un manojo de triples que comparten sujeto.

Puntos clave:
- Hecho atómico como tupla.
- Situación como reificación.
- Composición: una situación dentro de otra.
- Comparación con RDF, neo-davidsoniano, infones de Barwise-Perry.

Abre con: descomponer un párrafo periodístico en sus hechos atómicos.
Cierra con: la situación como punto en el espacio multidimensional.

Fuente: secciones 3 y 4 de `WQuestions.md`, `related/barwise-perry-situations.md`, `related/neo-davidsonian.md`.

### Capítulo 9 — El espacio multidimensional

**Tesis**: las coordenadas no son metáfora — son geometría real, con propiedades formales (parcial, multi-valuada, tipada).

Puntos clave:
- Cada situación es un punto multidimensional.
- Las dimensiones son los roles, no los ejes.
- Diferencias con ℝⁿ clásico, tablas relacionales, OLAP cubes.
- Las consultas como restricciones geométricas (hiperplanos, proyecciones).

Abre con: el diagrama del espacio dispersa.
Cierra con: lo que se gana operativamente al pensar geométricamente.

Fuente: sección 3 de `WQuestions.md`, `related/gardenfors-conceptual-spaces.md`.

### Capítulo 10 — Situaciones, contextos y agencia

**Tesis**: el mundo no son hechos sueltos — son escenas reificadas con participantes en roles. La agencia es contextual.

Puntos clave:
- D2: contexto = situación en O.
- D5: agencia contextual — un robot puede ser agente en una situación específica.
- Composición de situaciones: parte_de y precede.
- La convención de hechos inmutables (cambios = nuevas situaciones).

Abre con: la diferencia entre "Juan corre" y "el correr de Juan ayer en el parque".
Cierra con: por qué reificar siempre vence a propiedades flotantes.

Fuente: D2, D5, convenciones, `related/cidoc-crm.md`.

### Capítulo 11 — El "por qué" no es una pregunta más

**Tesis**: las cuatro "por qué" (causa, motivo, finalidad, justificación) son relaciones, no un eje. Tratarlas así da más expresividad, no menos.

Puntos clave:
- D6 y sus cuatro relaciones canónicas.
- Por qué un eje "por qué" no funcionaría (heterogeneidad de valores).
- Cadenas explicativas y razonamiento.
- Modelado de reglas declarativas (la convención).

Abre con: cuatro preguntas "por qué" con respuestas distintas semánticamente.
Cierra con: las reglas reificadas como puente al motor de inferencia futuro.

Fuente: D6, convención de reglas, ejemplos de taxi y contrato.

---

## PARTE IV — DEL LENGUAJE A LOS HECHOS

### Capítulo 12 — Por qué el verbo es el corazón de la oración

**Tesis**: cada verbo es una firma de función que activa un tipo de situación con sus roles. Es la conexión natural entre lengua y datos.

Puntos clave:
- Análisis neo-davidsoniano: el evento como argumento.
- Sujeto + verbo + predicado → situación con roles.
- Mapeo casi mecánico al modelo WQuestions.
- Las preguntas-WH como proyecciones.

Abre con: descomposición paso a paso de "Juan le dio un libro a María ayer".
Cierra con: el verbo como contrato de tipos.

Fuente: sección 9 de `WQuestions.md`, `related/neo-davidsonian.md`, `related/framenet-verbnet.md`.

### Capítulo 13 — Diccionarios léxicos como compiladores

**Tesis**: una vez aceptado que el verbo gobierna, necesitamos un diccionario que mapee verbos a tipos. Ese diccionario es el lexicon.

Puntos clave:
- El lexicon como artefacto central.
- D8: el catálogo canónico es invisible; el lexicon es la interfaz.
- Aliases por rol y por dominio.
- FrameNet, VerbNet, PropBank como precedentes industriales.
- Conexión con function calling de LLMs.

Abre con: el problema de la polisemia ("dar la mano" ≠ "dar un regalo").
Cierra con: por qué el lexicon es lo que más impacta usabilidad.

Fuente: D8, `lexicon.md`, `related/framenet-verbnet.md`, `related/llm-function-calling.md`.

### Capítulo 14 — Cuando el modelo se rompe: nominalización, modales, idiomas

**Tesis**: hay tres casos lingüísticos que estresan cualquier modelo. WQuestions los absorbe con convenciones específicas.

Puntos clave:
- Nominalización: "la llegada del avión" — situación reificada como nominal.
- Modales: querer, deber, poder — modificadores, no situaciones independientes.
- Idiomas y colocaciones: el lexicon como unidad léxica, no verbo.

Abre con: tres frases que romperían un parser ingenuo.
Cierra con: el límite real del modelo está en otra parte — en las reglas.

Fuente: ejemplos de la batería de oraciones (sección 9), discusión de polisemia.

---

## PARTE V — EN LA PRÁCTICA

### Capítulo 15 — Modelando un sistema de ventas

**Tesis**: un dominio comercial minorista modelado en WQuestions, con autoridad tributaria, comprobantes, impuesto al consumo, multi-divisa.

Caso completo: aeropuerto + sistema de ventas. Cómo se ve un sistema real.

Fuente: secciones 6 y 7 de `WQuestions.md`.

### Capítulo 16 — Modelando un servicio on-demand

**Tesis**: el app de taxi como ejemplo de dominio con agentes múltiples (humano, app, vehículo) y situaciones encadenadas.

Caso completo: app de taxi con D6 y D7.

Fuente: sección 8 de `WQuestions.md`.

### Capítulo 17 — Modelando un dominio nuevo: historia clínica

**Tesis**: el modelo aguanta dominios nuevos con poca fricción. Mostremos el proceso.

Caso completo: consulta médica con diagnóstico, prescripción, control futuro. La metodología de elicitación.

Fuente: prueba de Nivel 1 de historia clínica.

### Capítulo 18 — El dominio más exigente: un banco

**Tesis**: el dominio bancario es donde casi todas las decisiones de diseño previas pasan de ser elegantes a ser exigencias regulatorias.

Cuatro casos: transferencia con cinco agentes y dos asientos contables; ciclo de vida de un préstamo con D9 (vigente → mora → reestructurado); investigación de fraude que reconstruye el pasado; producto bancario como oferta reificada. Muestra que el modelo absorbe la complejidad industrial y evidencia que las pendientes operativas del cap 22 (persistencia industrial, motor de inferencia, bitemporalidad completa) son requisitos, no nicho.

Fuente: prototipo `ejemplos/banco.py` con 11 validaciones pasadas.

### Capítulo 19 — Cuando el modelo se prueba: música, química, fútbol, contratos

**Tesis**: el verdadero test de un modelo universal es someterlo a dominios cualitativamente distintos.

Cuatro dominios estresantes:
- Música: recursión, sin agentes humanos, K denso.
- Química: D5 al extremo, plantilla + instancia.
- Fútbol: concurrencia, estado derivado.
- Contratos: normativo intensivo, validez temporal.

Cierre: qué emergió de cada uno; cómo el modelo se refinó.

Fuente: pruebas de Nivel 1 (composición musical, química, fútbol, contrato).

---

## PARTE VI — IMPLICACIONES Y FUTURO

### Capítulo 20 — WQuestions y los modelos de lenguaje

**Tesis**: el momento de WQuestions es 2026 — la era de function calling, agentes y MCP — porque resuelve el problema central de cómo conectar lenguaje natural con conocimiento estructurado.

Puntos clave:
- Function calling como capa 4 de D8.
- El lexicon como function schema universal.
- Cómo exponer WQuestions vía MCP.
- Casos de uso: asistentes empresariales, investigación, ingesta automática.

Abre con: una conversación entre usuario y agente LLM, mostrando el pipeline interno.
Cierra con: WQuestions como infraestructura para IA conversacional.

Fuente: `related/llm-function-calling.md`.

### Capítulo 21 — Aplicaciones futuras

**Tesis**: si la arquitectura funciona, ¿qué se vuelve posible que antes no?

Puntos clave:
- Búsqueda cross-dominio sin schema-matching.
- Auditoría legal automatizada vía bitemporalidad.
- Razonamiento composicional sobre conocimiento.
- Sistemas multi-agente que comparten un modelo del mundo.
- Educación: explicar dominios complejos desde sus coordenadas.

Abre con: tres escenarios futuristas plausibles a 3-5 años.
Cierra con: el mapa de lo que falta implementar.

### Capítulo 22 — Qué falta: validación, tooling, comunidad

**Tesis**: la propuesta está completa conceptualmente; falta hacerla real.

Puntos clave:
- Motor de inferencia (Datalog, SHACL, custom).
- Bitemporalidad completa (valid + transaction time).
- Tooling: lexicon ingestor, parser, IDE.
- Comunidad: gobernanza, contribuciones, dialectos de dominio.
- Libro como semilla, no como punto final.

Fuente: decisiones pendientes y pisos siguientes.

### Conclusión — Por qué importan las preguntas

**Tesis** (resumen final): las preguntas son anteriores a cualquier ontología; son cómo el lenguaje humano organiza la realidad; son la base natural para que la IA hable nuestro idioma sin perder rigor.

Vuelta circular al capítulo 1: el médico que ahora sí puede ver la historia del paciente, porque ambos hospitales hablan en preguntas.

---

## Anexos planeados

- **Glosario** — todos los conceptos técnicos.
- **Catálogo D7 completo** — versión de referencia rápida.
- **Lexicon ejemplar** — los ~50 verbos del lexicon actual.
- **Comparación con precedentes** — tabla maestra de las 12 fichas en `related/`.
- **Decisiones de diseño** — D1–D9 con justificación.
- **Bibliografía**.

## Notas de redacción

- Cada capítulo abre con una historia o anécdota; nunca con definición seca.
- Las cajas de código se introducen progresivamente; en capítulos 1-3 son raras.
- Los gráficos ASCII del proyecto se incluyen para texto plano; pueden redibujarse para edición.
- Cuando se mencione un precedente, citar con número de página de la edición original cuando sea posible.
- Tono: serio pero accesible, con humor ocasional cuando el ejemplo lo permite.
