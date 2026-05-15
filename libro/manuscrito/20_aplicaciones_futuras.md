# Capítulo 20 — Aplicaciones futuras: lo que se vuelve posible

## Tres escenas a tres años vista

Imaginemos tres escenas que hoy son técnicamente plausibles pero económicamente inviables, y que con WQuestions más LLMs en su lugar maduro se vuelven asequibles para organizaciones medianas:

**Escena uno — el dueño de la franquicia.** El Sauna Oasis se expandió: ahora tiene cuatro sedes en tres ciudades. El dueño, sin equipo de analytics, le pregunta por la mañana a su asistente:

> *— ¿Qué pasó esta semana?*
>
> — *Las ventas de la sede Centro bajaron 12% respecto a la semana pasada. La causa principal: una caída en el plan mensual el miércoles. Ese mismo día subieron las cancelaciones de sesiones — siete cancelaciones, seis por mismo motivo: ducha rota. Mantenimiento ya está pedido pero la orden lleva tres días sin atender. Sugiero priorizar.*

El asistente cruzó cinco fuentes — ventas, plan, sesiones, cancelaciones, órdenes de mantenimiento — siguiendo cadenas de `causado_por` y `motivado_por` por el grafo. Lo que para un equipo humano hubiera sido medio día de cruzar planillas, fue un minuto de conversación.

**Escena dos — la médica buscando patrones.** En un hospital con quinientos médicos y veinte años de historias clínicas estructuradas en WQuestions, una doctora le pregunta a su asistente:

> *— Muéstrame los pacientes con hipertensión grado 2 que iniciaron enalapril en los últimos seis meses y no lograron control después de tres meses.*

El sistema devuelve la lista. La doctora pide más:

> *— De esos, ¿cuántos tenían diabetes co-mórbida? ¿Y cuál fue el segundo medicamento que se les agregó?*

El sistema responde con una tabla cruzada y una visualización. Lo que antes era un proyecto de tesis — extracción manual de quinientas historias clínicas en prosa, codificación, análisis — es ahora una consulta de tres segundos. **Porque las historias estaban en el grafo desde el inicio.**

**Escena tres — el auditor retrospectivo.** Una empresa enfrenta una investigación regulatoria. El fiscal pregunta:

> *— ¿Qué sabía el directorio sobre la cláusula de garantía el 15 de noviembre de 2024?*

El sistema reconstruye el estado del grafo en esa fecha exacta — usando bitemporalidad completa: no solo qué era cierto, sino qué estaba afirmado en el sistema en ese momento. Devuelve los hechos accesibles, los actos formales registrados, las reglas vigentes. La pregunta *"¿qué sabía la organización cuándo?"* se vuelve consultiva, no testimonial.

Las tres escenas comparten una propiedad. **No se trata de innovaciones puntuales** — analítica conversacional, búsqueda semántica, auditoría temporal. Se trata de un mismo cambio arquitectónico que las hace posibles a las tres a la vez: el grafo persistente como sustrato, el LLM como interfaz, las relaciones canónicas como infraestructura de razonamiento. Lo que sigue son las cinco familias de aplicaciones que ese cambio abre.

![Cinco familias de aplicaciones que se vuelven viables cuando WQuestions vive bajo un LLM: búsqueda cross-dominio, auditoría retrospectiva, razonamiento composicional, multi-agente, explicabilidad. Todas radian del mismo núcleo: un grafo persistente con interface conversacional.](../diagrams/png/37_familias_aplicaciones.png)

## Familia 1 — Búsqueda cross-dominio sin schema matching

La búsqueda corporativa hoy vive en silos. Los datos de ventas están en SAP, los de RRHH en Workday, los de marketing en Salesforce, los financieros en SAP de nuevo pero un módulo distinto, los operativos en un sistema legacy. Cada sistema tiene su schema. Para responder *"¿cuál fue el costo total de adquisición de un cliente que terminó cancelando dentro de los primeros 90 días?"* hay que cruzar cuatro sistemas, lo que en la práctica significa un proyecto de integración con presupuesto propio.

WQuestions reemplaza ese cruce por un sustrato común. Las áreas siguen operando sus sistemas, pero los hechos relevantes — ventas, contactos, transacciones, churn — se publican al grafo central con su dialecto de dominio respectivo. La pregunta del CFO se vuelve una consulta sobre el grafo, ejecutada por el LLM. El **schema matching** — el cuello de botella histórico de la integración empresarial — desaparece, porque todos los dialectos ya están mapeados al catálogo canónico D7.

Esta no es una promesa nueva — Tim Berners-Lee la formuló en el artículo fundacional del Semantic Web [31] hace un cuarto de siglo. Lo que faltaba era un modelo lo suficientemente simple para que las áreas lo adoptaran y un traductor lo suficientemente fluido para no exigir vocabulario técnico al usuario final. Las ocho coordenadas-pregunta cumplen el primer requisito; los LLMs el segundo.

## Familia 2 — Auditoría retrospectiva con bitemporalidad

Esta es la familia que más beneficio inmediato traerá a sectores regulados — finanzas, salud, derecho — y la única donde D9 (vigencia temporal) no es solo conveniencia sino requisito legal. El principio es simple: **el sistema nunca olvida, y puede mostrar lo que sabía en cualquier momento del pasado**.

Una corte que pregunta *"¿qué políticas internas estaban vigentes el 30 de junio de 2023?"* recibe una respuesta exacta, no una reconstrucción aproximada. Un regulador financiero que pide *"¿cuál era el límite de exposición de este cliente cuando se firmó la operación?"* obtiene el valor histórico, no el actual. Un equipo médico que estudia un evento adverso reconstruye **qué se sabía del paciente al momento de prescribir** — y por ende, si la decisión fue defendible bajo el conocimiento disponible.

La diferencia con sistemas tradicionales no es la **capacidad** — Snodgrass [17] formalizó bitemporalidad SQL en los noventa, y bases como Datomic la implementan en producción. La diferencia es la **uniformidad**: en WQuestions, todo hecho lleva su vigencia, no solo los selectivamente marcados. La pregunta retrospectiva nunca se topa con *"este dato no se preservó"*, porque la inmutabilidad es la regla, no la excepción.

Sectores donde esto cambia el juego: cumplimiento normativo bancario, due diligence corporativa, ensayos clínicos longitudinales, registros catastrales, registros académicos, archivos periodísticos. En todos ellos, **lo que importa no es solo el estado actual sino la historia auditable**.

## Familia 3 — Razonamiento composicional sobre conocimiento

Esta es la familia más ambiciosa y la que más promete a largo plazo. La idea es que un LLM, con acceso al grafo, no solo recupera información sino que **razona** combinando piezas:

- *"¿Qué clientes muestran patrones de uso similares al de Mariana C., quien canceló el mes pasado, y todavía no han cancelado?"* — composición de patrones de comportamiento.
- *"Si reduzco el precio del plan mensual en 10%, ¿cuántos clientes con intención registrada de contratarlo se convertirían según el modelo de elasticidad?"* — simulación basada en hechos y reglas.
- *"Lista los pacientes cuyo medicamento actual entra en contraindicación con la nueva guía clínica de agosto de 2026."* — composición de reglas + estado + cronología.

Cada una de estas preguntas combina hechos, reglas, y razonamiento del LLM. WQuestions provee la materia prima inequívoca; el LLM compone. La frontera entre **base de conocimiento** y **razonador** se vuelve fluida — el LLM hace los saltos, el grafo le ofrece la huella firme donde apoyarlos.

El riesgo conocido es la **alucinación compositiva**: un LLM puede inventar conexiones plausibles que no están en el grafo. La mitigación viene de exigir trazabilidad — cada conclusión debe poder citar los hechos del grafo que la sostienen, con identificador y momento. Cuando una respuesta no se puede trazar, el sistema lo declara abiertamente en lugar de inventar.

## Familia 4 — Sistemas multi-agente con modelo del mundo compartido

Hasta hace poco "agente IA" significaba un solo LLM con herramientas. Para 2026 ya se ven sistemas donde **varios agentes especializados colaboran** — uno hace investigación, otro redacta, otro verifica, otro audita. El cuello de botella es que cada agente vive en su propio contexto y la coordinación entre ellos es frágil.

WQuestions ofrece a esos sistemas un **modelo del mundo compartido**: un grafo persistente que todos los agentes consultan y al que todos contribuyen. Las decisiones de uno son hechos consultables por los demás. La cadena de razonamiento de un agente — *"agente A diagnosticó X basado en hechos Y, justificado por regla Z"* — queda registrada con la misma estructura que cualquier otra situación. La coordinación se vuelve **observable** en lugar de implícita.

```
(diagnostico_001, agente, lim_clinico_v3)         ∈ M(O, Q)
(diagnostico_001, motivado_por, evidencia_023)
(opinion_legal_002, agente, lim_legal_v1)
(opinion_legal_002, motivado_por, diagnostico_001)  ← un agente cita a otro
```

Este patrón abre escenarios concretos: equipos de auditoría donde un agente sospecha, otro investiga, otro verifica; equipos médicos donde un agente sugiere diagnóstico, otro revisa contraindicaciones, otro registra; equipos legales donde un agente redacta, otro audita por riesgo, otro confronta con jurisprudencia. Todos sobre el **mismo** grafo, todos con la **misma** trazabilidad.

Acá D5 — la agencia contextual del capítulo 10 — paga el dividendo final: los LLMs entran al modelo como agentes Q de pleno derecho, tratados uniformemente con humanos. El sistema no necesita módulos especiales para "agentes IA"; el modelo ya los acepta porque siempre aceptó agentes no humanos.

## Familia 5 — Educación y explicabilidad

Una aplicación menos comercial pero quizás más significativa a largo plazo: WQuestions como **herramienta pedagógica**. Cuando se le explica a un estudiante un dominio complejo — anatomía, derecho constitucional, química orgánica — la dificultad típica es que el dominio se presenta como un texto lineal, mientras que su estructura real es un grafo.

Si el dominio está modelado en WQuestions, el estudiante puede **navegarlo**: partir de un concepto, ver sus instancias, ver sus relaciones causales y normativas, hacer consultas exploratorias. *"¿Qué situaciones dependen de la disponibilidad de ATP?"*, *"¿Qué causa qué en la cascada inflamatoria?"*, *"¿Qué cláusulas se justifican mutuamente en este sistema legal?"*. El grafo se vuelve un libro de texto **interactivo y consultable**, donde la estructura del conocimiento es explorable, no recitable.

La aplicación tiene un correlato indirecto en explicabilidad de la IA. Cuando un sistema basado en LLMs toma una decisión — denegar un crédito, sugerir un tratamiento, sancionar un contenido — la pregunta *"¿por qué?"* requiere una respuesta auditable. Si la decisión se construyó sobre un grafo con relaciones canónicas del "por qué", la cadena de explicación es **literalmente** un recorrido del grafo. No es post-hoc rationalization; es la reconstrucción del razonamiento real.

![Una consulta multi-fuente real: el periodista pregunta cómo afectó la reforma tributaria a las ventas. El LLM combina consultas sobre noticias políticas, indicadores macroeconómicos y ventas trimestrales — todos en el mismo grafo — y produce una respuesta narrativa con trazabilidad.](../diagrams/png/38_cross_domain.png)

## La constante: identidad estable a través del tiempo

Si tuviera que destilar las cinco familias en una sola observación, sería ésta. Lo que las hace posibles a todas es la misma propiedad: **el grafo preserva identidad estable de las entidades a través del tiempo**. María Gonzales es el mismo individuo en 2026 y en 2034; el Sauna Oasis es la misma persona jurídica antes y después de expandirse; la cláusula 14 del contrato es la misma cláusula con o sin enmiendas posteriores.

Esto suena trivial pero no lo es. En sistemas tradicionales, la identidad se reconstruye por *foreign keys* que apuntan a registros que pueden ser editados, borrados o renombrados. La identidad es **frágil**: una migración de schema, un cambio de criterio, una limpieza de datos, y la trazabilidad se rompe. WQuestions hace lo opuesto: cada individuo recibe un UUID inmutable, los hechos sobre él son acumulativos, los cambios son nuevos hechos con vigencia. La identidad se vuelve **infraestructura**, no convención.

Sobre esa base se construye todo lo demás: la auditoría retrospectiva, el razonamiento composicional, el multi-agente, la explicabilidad. Todos exigen poder decir *"este individuo, en este momento, era así"* y obtener una respuesta unívoca. La identidad estable es la propiedad que hace que decir *este* signifique siempre lo mismo.

## El sesgo de optimismo

Sería deshonesto cerrar este capítulo sin matizar. Los escenarios que describí son **plausibles**, no inevitables. Cada uno depende de que varias condiciones se cumplan a la vez:

- Que las organizaciones acepten exponer su información estructurada a un grafo común (ni siquiera tienen que hacerlo *público*, pero sí *consultable* dentro de su perímetro).
- Que los LLMs sigan mejorando en exactitud y en honestidad sobre lo que no saben.
- Que el costo de cómputo de un asistente conversacional con grafo persistente siga bajando.
- Que aparezcan **ingenieros de lexicon** — un rol nuevo, equivalente al del data engineer pero centrado en mapear vocabulario de dominio a roles canónicos.
- Que la regulación acompañe en lugar de bloquear, especialmente en sectores regulados (salud, finanzas, derecho).

Algunas de estas condiciones se están cumpliendo solas, otras requieren empuje activo. La especulación es honesta cuando reconoce la diferencia.

## Lo que falta: el puente al cap 21

Las aplicaciones de este capítulo asumen una versión madura del proyecto. La versión actual — la que el prototipo ejecuta — está incompleta. Falta persistencia industrial, motor de inferencia, bitemporalidad completa, lexicon poblado en varios idiomas, herramientas para que las organizaciones definan sus dialectos sin asistencia de un ingeniero.

El próximo capítulo — el último antes de la conclusión — enumera ese trabajo pendiente honestamente. No es un capítulo de promesas: es un **mapa de implementación**, dirigido a quien lea este libro y quiera contribuir o adoptar la propuesta como base de un proyecto propio. Las cinco familias de este capítulo viven en el futuro; el capítulo 21 vive en el presente operativo.
