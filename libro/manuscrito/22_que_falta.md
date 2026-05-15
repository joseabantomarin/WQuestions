# Capítulo 22 — Qué falta: validación, tooling, comunidad

## El contrato del cierre

Hasta acá el libro acumuló unas veinte horas de propuesta. Tres partes conceptuales — las preguntas como invariantes, los ocho ejes, el modelo en operación — más una parte sobre lenguaje, otra sobre práctica, y una sexta que abre el panorama futuro con los LLMs. El prototipo en Python valida cada afirmación con tests pasando. Los diagramas ilustran lo que el texto explica. Los ocho dominios modelados confirman que el catálogo se sostiene en territorios disímiles.

Este último capítulo cambia de registro deliberadamente. No es una recapitulación; no es una mirada al horizonte. Es un **mapa de implementación**: lo que falta para que WQuestions deje de ser una propuesta y se vuelva una pieza de infraestructura adoptable. Está pensado para quien lea el libro y quiera empujar el proyecto adelante — sea como contribuyente al núcleo, como adoptante temprano en su organización, o simplemente como observador que necesita medir el camino que queda.

Lo organizo en seis frentes, cada uno con tres cosas: **qué falta**, **qué tan urgente es**, **qué requiere para resolverlo**. Cierro con la pieza que importa más de todas — y la que el autor no controla solo.

![Los seis frentes que separan al prototipo de la infraestructura industrial: motor de inferencia, bitemporalidad completa, persistencia, tooling, lexicon poblado, comunidad. Cada uno con su prioridad y dependencias.](../diagrams/png/39_roadmap_pendientes.png)

## Frente 1 — El motor de inferencia

Apareció seis veces a lo largo del libro: el evaluador externo que recorre el grafo y dispara reglas. La regla *"siete sesiones → una gratis"* del sauna. La verificación *"prescripción versus contraindicación"* de la clínica. El cálculo del marcador del partido. La aplicación de la cláusula de rescisión del contrato. Todas comparten la misma forma estructural: una condición declarativa sobre hechos del grafo, un consecuente que se efectúa cuando la condición se cumple.

**Qué falta**: una capa de evaluación de reglas que opere sobre WQuestions. Hay al menos cuatro tecnologías candidatas, cada una con su fortaleza:

- **SHACL** ([Shapes Constraint Language](https://www.w3.org/TR/shacl/), W3C 2017) — diseñado para validar grafos RDF. Bueno para chequear consistencia ("ningún paciente puede tener dos diagnósticos contradictorios vigentes"). Limitado para razonamiento positivo.
- **Datalog** — lenguaje lógico deductivo. Excelente para razonamiento composicional ("si X causa Y, e Y causa Z, entonces X causa Z transitivamente"). Bibliotecas como Soufflé tienen rendimiento industrial.
- **Código de aplicación** — funciones Python/Rust/Go que reciben el grafo y producen el efecto. Lo más flexible, lo menos auditable.
- **LLM con function calling** — usar al propio LLM como evaluador para reglas borrosas o ambiguas. Útil para reglas pragmáticas; no apto para reglas de cumplimiento estricto.

**Urgencia**: alta. Sin evaluador, WQuestions almacena reglas pero no las ejecuta. Para una mayoría de aplicaciones útiles, esto es un bloqueador.

**Qué requiere**: una **API de motor de inferencia** que el universo exponga (`u.evaluate(rule_id)`, `u.evaluate_all()`, con resultados que sean nuevamente hechos atómicos firmados por el evaluador). El primer paso es elegir un motor referencia — SHACL para validación, Datalog para inferencia — e integrarlo. Trabajo estimado: tres a seis meses para un primer release usable.

## Frente 2 — Bitemporalidad completa

Hoy el modelo soporta **valid time**: cada hecho lleva su rango `[valid_from, valid_to)`. Una consulta `at=T` recupera lo cierto del mundo en ese momento. Lo que **falta** es **transaction time**: cuándo el sistema afirmó ese hecho.

La diferencia importa cuando alguien pregunta no *"¿qué era cierto?"* sino *"¿qué sabíamos?"*. Si en mayo de 2024 registramos que el plan mensual de un cliente venció el 31 de marzo, pero el cliente apareció en abril a reclamar y mostró que renovó, retrocedemos el plan. La pregunta del auditor *"¿qué estaba en el sistema entre el 1 de abril y la fecha de la corrección?"* solo se responde si el sistema preservó esa versión transitoria.

**Qué falta**: en cada hecho, agregar `tx_inicio` y `tx_fin` (transaction interval) además del valid interval. Las consultas se vuelven *as-of dual*: `query(at_valid=T1, at_tx=T2)`. Snodgrass [17] formalizó esto en los noventa; las bases bitemporales modernas (Datomic, XTDB) lo implementan en producción.

**Urgencia**: alta para dominios regulados (finanzas, salud, derecho); baja para el resto. Cuando un dominio lo necesita, no es opcional.

**Qué requiere**: una refactorización compatible del módulo `fact.py` para llevar dos intervalos en vez de uno. La estructura ya tiene un `tx_time` único; solo hay que enriquecerlo. Trabajo estimado: un mes para implementación, más tests sobre dominio regulado real.

## Frente 3 — Persistencia industrial

El prototipo vive en memoria. Útil para validación arquitectónica; impráctico para sistemas reales. **Qué falta**: backends de persistencia con perfiles distintos:

- **SQLite** — para sistemas chicos y monousuario. Esquema simple: una tabla `individuals` con `(id, axis, payload_json)`, una tabla `facts` con `(subject_id, role, value_id, valid_from, valid_to, tx_start, tx_end)`. Implementación trivial sobre el universo actual.
- **Postgres + JSONB** — para sistemas multi-usuario medianos. Aprovecha índices GIN sobre payload, FTS sobre etiquetas, partitioning por tx_time para auditoría.
- **Kùzu o Neo4j** — para sistemas que privilegian consultas de grafo (rutas, caminos transitivos). Modelo más natural pero curva de adopción mayor.
- **RDF/SPARQL** (Apache Jena, GraphDB) — para sistemas que quieran interoperar con la web semántica existente. Mapeo trivial: cada hecho es una tripleta RDF; D9 se mapea con grafos nombrados.

**Urgencia**: alta para cualquier adoptante. Sin persistencia, no hay sistema.

**Qué requiere**: una **interfaz `Storage`** abstracta y al menos dos implementaciones (SQLite + Postgres). El módulo `universe.py` actual se refactoriza para delegar lectura/escritura. Trabajo estimado: dos a tres meses para los dos backends primarios.

## Frente 4 — Tooling

Una propuesta como WQuestions vive o muere por su tooling. Los conceptos pueden ser elegantes; si la fricción operativa es alta, nadie adopta. **Qué falta** se enumera por prioridad:

**4.1 — Lexicon ingestor.** Hoy las entradas del lexicon se escriben a mano. Hace falta una herramienta que ingiera entradas desde FrameNet [14], VerbNet [15], PropBank — recursos masivos ya construidos — y produzca entradas válidas del lexicon WQuestions. Esto da un piso de cobertura de miles de verbos sin trabajo manual.

**4.2 — Parser de lenguaje natural a hechos.** Hoy el parsing se hace vía LLM con function calling. Hace falta también un parser **local y determinístico** para textos donde la latencia del LLM importa (sistemas de tiempo real) o donde la privacidad lo exige (datos médicos). Combinar análisis sintáctico con el lexicon es trabajo concreto, no investigación abierta.

**4.3 — IDE / inspector.** Un visor interactivo del grafo: explorar individuos, ver sus hechos, ver vecinos, consultar con patrones, ver la cadena `causado_por`/`justificado_por` de cualquier nodo. Útil para modeladores, depuradores, auditores. Una primera versión web ligera es viable en semanas, no en meses.

**4.4 — Validador de migración.** Cuando un sistema legacy quiere migrar a WQuestions, hay que validar que el dialecto de dominio mapea correctamente al canónico. Una herramienta de validación detecta cuellos: roles sin signatura, ejes ambiguos, vigencias inconsistentes.

**4.5 — Generador de servidor MCP.** Dado un lexicon, generar automáticamente el servidor MCP correspondiente. Esto convierte cada dominio en un asistente conversacional sin escribir glue code. Trabajo de pocas semanas; impacto desproporcionado en adopción.

**Urgencia**: media en agregado, alta en el caso del **lexicon ingestor** (4.1) y el **generador MCP** (4.5), porque son los que más reducen el costo de probar la propuesta.

## Frente 5 — Lexicon poblado en varios idiomas

El catálogo D7 del libro tiene 38 roles canónicos. El lexicon del prototipo registra unos diez verbos. Para un sistema productivo, el lexicon de un solo idioma necesita del orden de **dos a cinco mil entradas** — los verbos frecuentes del español, sus formas nominales, las locuciones idiomáticas.

**Qué falta**: trabajo lingüístico paciente. Por dominio o por familia semántica (transferencia, comunicación, movimiento, percepción, estados, etc.), poblar el lexicon. FrameNet español, el spanish corpus de Universal Dependencies, AnCora son fuentes legítimas para mecanizar parcialmente este trabajo.

Para internacionalización: cada idioma necesita su propio lexicon. El **catálogo D7 es idiomáticamente neutral** (los nombres internos como `agente`, `paciente`, `tema` son etiquetas inglesas pero podrían ser griegas o números). Lo que cambia entre idiomas es la **capa de aliases** y los **patrones de polisemia** específicos.

**Urgencia**: la cobertura del lexicon **es** la usabilidad. Sin verbos suficientes, el modelo se siente incompleto. Esfuerzo sostenido, no proyecto puntual.

**Qué requiere**: equipo lingüístico-computacional. Idealmente colaboración con universidades que ya hacen recursos léxicos. Modelo de gobernanza para aceptar contribuciones de terceros.

## Frente 6 — Comunidad y gobernanza

Acá entramos en la pieza que el autor no controla. WQuestions, para volverse útil más allá de un libro, necesita **comunidad**: gente modelando dominios, contribuyendo lexicon, reportando fricciones, escribiendo herramientas, adoptándolo en proyectos.

**Qué falta**:

- **Repositorio canónico** abierto, con licencia permisiva. Una primera versión vive en GitHub mientras leés esto.
- **Proceso de contribución**: cómo proponer nuevas entradas al catálogo D7, nuevos dominios al lexicon, parches al motor. Necesita criterios escritos.
- **Foro o canal de discusión**: para resolver fricciones que surjan al modelar dominios nuevos. Cada conversación cualifica el catálogo.
- **Estandarización gradual**: una vez que varios proyectos adopten el modelo, vale la pena llevar partes del catálogo (los roles más universales) a un proceso de estandarización formal — IETF, W3C, ISO. Esto da estabilidad legal para uso empresarial.
- **Dialectos de dominio** mantenidos por comunidades sectoriales: clínico, financiero, legal, manufactura. Cada uno con su propia gobernanza dentro de la espina común.

**Urgencia**: el reloj corre. Si la comunidad no se forma en el momento en que los LLMs con MCP se popularizan, alguna otra propuesta menos cuidadosa ocupará el espacio. La ventana es de dos a cinco años.

**Qué requiere**: lo mismo que cualquier proyecto open source serio: un autor (o equipo fundador) dispuesto a moderar, criticar contribuciones, mantener la coherencia, decir que no cuando hace falta. Buena documentación. Casos de uso ejemplares. Adoptantes tempranos visibles.

![La pila completa: persistencia (Postgres / Kùzu) abajo, encima el núcleo WQuestions con sus 8 ejes, encima el evaluador de reglas y el lexicon, encima el LLM via MCP, encima la aplicación que el usuario final ve. Cada capa puede evolucionar independientemente.](../diagrams/png/40_pila_completa.png)

## Las fricciones documentadas que siguen sin parche

Además de los seis frentes mayores, hay un puñado de fricciones que el prototipo expuso y que viven todavía en `dominios.md` esperando trabajo. Las enumero en limpio para que queden listadas en un solo lugar:

| # | Fricción | Origen | Patch propuesto | Urgencia |
| --- | --- | --- | --- | --- |
| 1 | `paciente: O → Q` demasiado estrecho | química | Relajar a `O → V` | Media |
| 2 | `partes: O → Q` demasiado estrecho | fútbol | Relajar a `O → V` | Baja |
| 3 | `tema: O → O` rechaza K (obra, medicamento) | música, clínica | Considerar `tema_categorico: O → K` | Media |
| 4 | Patrones temporales finos (cada_mañana, recurrentes) | clínica | Reificar como O con estructura | Baja |
| 5 | Tiempo musical (compás, pulso) | música | Reificación de compases | Muy baja |
| 6 | Reglas de derivación versionadas | contrato | Frente 1 (motor) + D9 sobre reglas | Alta |

Ninguna bloquea el funcionamiento del modelo; varias quedan resueltas mediante roles de dominio bajo la política liberal. Pero forman la **lista de mejoras concretas al catálogo** que se acumula a medida que el modelo se prueba en territorios nuevos.

## El libro como semilla

Cerremos con la idea menos técnica del capítulo. Un libro no es una propuesta terminada — es **una invitación a que alguien la termine**. Las arquitecturas duraderas — Unix, TCP/IP, HTTP, SQL, Linux, RDF — empezaron como artículos, manifiestos, RFCs, libros: textos que articulaban una idea con suficiente claridad para que otros pudieran apropiársela y empujarla adelante.

WQuestions, en su forma actual, es un texto y un prototipo. El catálogo D7 está bien diseñado pero incompleto; el lexicon está bosquejado; las herramientas son embriónicas; la comunidad es nula. Lo que cualquier lector tiene en la mano al cerrar este libro no es un producto sino una **base operable**: suficiente para entender la propuesta, ejecutarla, criticarla, extenderla. Si la propuesta tiene valor, otros la perfeccionarán.

La conclusión que sigue — el último capítulo del libro — no es una recapitulación de lo dicho. Es un **regreso circular** al problema con el que abrimos: el médico que no podía leer la historia del paciente porque cada hospital usaba un schema distinto. La pregunta es si la respuesta que el libro propone — las preguntas mismas como base universal — aguanta el peso que prometió aguantar. Y, más honestamente: si vale la pena el esfuerzo de construirla.
