# Capítulo 14 — Cuando el lenguaje aprieta: nominalizaciones, modales e idiomas

## Tres oraciones que romperían un parser ingenuo

Tomemos tres oraciones, todas perfectamente naturales en español, que un sistema construido siguiendo solo el procedimiento del capítulo 12 procesaría mal:

> *La llegada tardía del avión causó la cancelación de la conexión.*
>
> *El cliente quería contratar el plan mensual pero no podía pagarlo todavía.*
>
> *La doctora le tomó el pelo al residente nuevo durante la guardia.*

Aplicado mecánicamente, el procedimiento del capítulo 12 buscaría verbos principales y los reificaría como situaciones. En la primera oración no hay verbo principal de acción — *causó* es el verbo gramatical, pero las dos cosas interesantes (la llegada, la cancelación) están escondidas como sustantivos. En la segunda, *quería* parece ser el verbo principal y *contratar* un infinitivo subordinado — pero el sistema acabaría creando una situación de "querer" que no existe en el mundo, distinta de la de "contratar" que sí está pasando. En la tercera, una traducción literal generaría una situación de "tomar" con tema "pelo", aplicada a un residente — ridícula. *Tomar el pelo* es una expresión idiomática que significa **bromear o engañar con buena intención**, y no tiene nada que ver con cabello ni con apropiación.

Estos tres casos — **nominalizaciones**, **modales** y **idiomas** — son los lugares donde el lenguaje natural ejerce más presión sobre cualquier modelo de representación semántica. Vale la pena verlos uno por uno, no para presumir de que el modelo los resuelve mágicamente, sino para mostrar exactamente con qué convenciones los absorbe y dónde quedan zonas grises.

## Nominalización: cuando el verbo se vuelve sustantivo

El español tiene una facilidad extraordinaria para convertir verbos en sustantivos: *llegar* → *la llegada*; *contratar* → *la contratación*; *vender* → *la venta*; *renunciar* → *la renuncia*; *consultar* → *la consulta*. Esta operación gramatical, llamada **nominalización**, no es decorativa. Cuando un hablante dice *"la llegada del avión"*, está hablando exactamente del mismo evento que cuando dice *"el avión llegó"*. La diferencia es solo sintáctica.

Para el modelo, esto significa una cosa importante: **una nominalización es una situación reificada bajo otro empaque gramatical**. La frase *"la llegada del avión"* no necesita un mecanismo nuevo: necesita ser reconocida por el lexicon como un disparador del mismo tipo de situación que el verbo *llegar*. La signatura es la misma, los roles son los mismos, lo único que cambia es qué constituyente de la oración lleva al verbo y cuál al sustantivo.

Tomemos la primera oración y desarmémosla:

> *La llegada tardía del avión causó la cancelación de la conexión.*

```
(llegada_017, instancia_de,    accion_llegar)
(llegada_017, agente,          avion_LP2226)
(llegada_017, estatus_factual, real)
(llegada_017, calificacion,    tardia)
(llegada_017, momento,         2026-05-15T11:47Z)

(cancelacion_004, instancia_de, accion_cancelar)
(cancelacion_004, tema,         conexion_lima_arica)
(cancelacion_004, estatus_factual, real)

(cancelacion_004, causado_por,  llegada_017)    ∈ M(O, O)
```

Una oración con dos sustantivos derivados produce dos situaciones reificadas conectadas por `causado_por` (la relación canónica del capítulo 11). El verbo *causar* de la oración superficial no se reifica como una tercera situación; se traduce a la relación misma, que es lo que el predicado verbal estaba pidiendo. El modelo termina con una representación que es estructuralmente idéntica a la que produciría una versión "verbal" equivalente: *"El avión llegó tarde, lo que canceló la conexión."*

![Una nominalización y su forma verbal equivalente producen exactamente la misma situación reificada en el modelo. El lexicon hace que ambos disparadores —el verbo "llegar" y el sustantivo "llegada"— activen la misma entrada.](../diagrams/png/25_nominalizacion.png)

La convención que esto requiere en el lexicon es explícita: cada entrada verbal debe **declarar también sus formas nominales aceptables**. Una entrada parcial de *llegar* en el lexicon, con esta convención, se ve así:

```yaml
verbo: llegar
  formas_nominales: ["llegada", "arribo"]
  tipo_situacion: accion_llegar
  obligatorios:   [agente]
  opcionales:     [destino, origen, momento, lugar_de, modo]
```

Cuando el parser encuentra *la llegada del avión*, busca por superficie nominal y encuentra la entrada de *llegar*. El rol que ocupaba el sujeto en la forma verbal (*el avión*) ahora aparece como complemento del nombre (*del avión*), pero el rol semántico — `agente` — es el mismo. El motor no necesita saber gramática; necesita un lexicon que mapee ambas formas.

La consecuencia práctica es agradable: el modelo se vuelve **invariante a la transformación nominalización-verbalización**, una propiedad valiosa cuando los textos reales mezclan ambas formas libremente. *"El paciente fue diagnosticado con hipertensión por la doctora Torres"* y *"El diagnóstico de hipertensión fue emitido por la doctora Torres"* y *"La doctora Torres diagnosticó al paciente con hipertensión"* producen exactamente los mismos hechos atómicos. La maquinaria captura el contenido, no la superficie.

## Modales: lo que se quiere, se debe o se puede

Los **verbos modales** — *querer*, *deber*, *poder*, *soler*, *parecer*, *tener que*, *haber de* — son una clase aparte. Sintácticamente parecen verbos principales que toman infinitivos como complemento. Semánticamente, son **modificadores** de la situación expresada por ese infinitivo. *Quiero viajar* no afirma que existan dos situaciones — una de "querer" y otra de "viajar" — sino una sola situación de viajar, marcada con un atributo que dice "está en estado volitivo del agente, no ocurrió todavía".

El modelo trata esto con una convención de un solo hecho: la **modalidad** como propiedad de la situación principal.

```
"El cliente quería contratar el plan mensual."

(contratar_017, instancia_de,    accion_contratar)
(contratar_017, agente,          cliente_003)
(contratar_017, tema,            plan_mensual_oasis)
(contratar_017, modalidad,       volitiva)        ∈ P(O, K)
(contratar_017, estatus_factual, intencionado)    ∈ P(O, K)
```

Una sola situación reificada: la del contratar. Dos hechos atómicos extras — `modalidad: volitiva` y `estatus_factual: intencionado` — que dicen "el cliente quiere esto, no lo hizo todavía". No hay una situación-de-querer aparte; no hay un verbo *querer* reificado. El querer es un modificador del contratar.

Las cuatro modalidades del español que el modelo reconoce explícitamente son:

- **Volitiva** — *querer*, *desear*, *planear*, *tener ganas de*. Lo expresado depende de un deseo o intención del agente.
- **Deóntica** — *deber*, *tener que*, *haber de*, *estar obligado a*. Lo expresado es una obligación normativa.
- **Alética** — *poder* (en sentido de capacidad). El agente es capaz de ejecutarlo, lo haga o no.
- **Epistémica** — *poder* (en sentido de probabilidad), *parecer*, *probablemente*. Lo expresado es una afirmación sobre la probabilidad o el conocimiento, no sobre el mundo.

Tomemos la segunda oración de la apertura entera y desarmémosla con esta convención:

> *El cliente quería contratar el plan mensual pero no podía pagarlo todavía.*

```
(contratar_017, instancia_de,    accion_contratar)
(contratar_017, agente,          cliente_003)
(contratar_017, tema,            plan_mensual_oasis)
(contratar_017, modalidad,       volitiva)
(contratar_017, estatus_factual, intencionado)

(pagar_017, instancia_de,    accion_pagar)
(pagar_017, agente,          cliente_003)
(pagar_017, tema,            plan_mensual_oasis)
(pagar_017, modalidad,       alética)
(pagar_017, polaridad,       negativa)            ∈ P(O, K)
(pagar_017, estatus_factual, no_realizable)
(pagar_017, momento,         hoy)
```

Dos situaciones, no cuatro. Ninguna situación de querer; ninguna situación de poder. El "querer" y el "no poder" son hechos sobre las situaciones-objeto. La conjunción adversativa *pero* se traduce como una relación canónica adicional entre ambas:

```
(pagar_017, contrasta_con, contratar_017)    ∈ M(O, O)
```

![Los modales no crean nuevas situaciones: decoran una situación existente con propiedades de modalidad. "Quiere viajar" y "viaja" describen la misma situación con distinto modo factual.](../diagrams/png/26_modales_decoradores.png)

La economía es importante. Si cada modal reificara una situación nueva, las oraciones modales triplicarían o cuadruplicarían los hechos en la base; los grafos se llenarían de nodos huecos. Tratar los modales como propiedades preserva el principio fundamental del modelo: **una situación del mundo, una situación en el grafo**. Las actitudes proposicionales del agente no son situaciones del mundo; son cualidades del registro.

Hay un caso límite que vale la pena mencionar. Cuando *querer* aparece como verbo pleno — *"Pedro quiere a María"* — significa **amar**, no es modal, y sí reifica una situación propia (`experiencia_amor`). El lexicon lo distingue por patrón sintáctico: *querer + infinitivo* es modal; *querer + a + persona* es la entrada de amar. La misma lógica de polisemia que vimos en el capítulo 13.

## Idiomas y colocaciones: las unidades léxicas no son palabras

El tercer caso es el más espinoso y el que más reveladoramente expone los límites de cualquier procedimiento mecánico. *Tomar el pelo* no significa nada parecido a la suma de *tomar* y *pelo*. *Echar de menos* no es echar nada ni medir. *Dar a luz* no es dar luminosidad. *Ponerse las pilas* no involucra baterías. *Hablar por los codos* no es hablar a través de las articulaciones. Estas combinaciones — llamadas **expresiones idiomáticas** o **colocaciones fijas** — son frecuentes en cualquier lengua natural y no admiten descomposición palabra por palabra.

La regla operativa del lexicon ya quedó establecida en el capítulo 13: **la unidad léxica no es necesariamente una palabra**. El lexicon mapea **patrones** — combinaciones específicas de verbo y complemento — a tipos de situación, no verbos sueltos. Las entradas idiomáticas se registran como cualquier otra entrada:

```yaml
tomar [el_pelo a Q]
  tipo_situacion: accion_bromear
  obligatorios:   [agente, paciente]
  opcionales:     [momento, lugar_de, sobre_que]
  ejemplo:        "la doctora le tomó el pelo al residente"
  notas:          colocación idiomática; no relacionado con cabello

echar [de_menos a Q]
  tipo_situacion: experiencia_extrañar
  obligatorios:   [experimentador, tema]
  opcionales:     [intensidad, desde]
  ejemplo:        "Juan echaba de menos a su perro"
  notas:          locución verbal; experimentador es el sujeto

dar [a_luz a Q]
  tipo_situacion: accion_parir
  obligatorios:   [agente, paciente]
  opcionales:     [momento, lugar_de, instrumento]
  ejemplo:        "dio a luz a una niña sana"
  notas:          eufemismo para parir
```

El parser intenta hacer *match* con los patrones más específicos primero. Para *"la doctora le tomó el pelo al residente"*, el patrón `tomar [el_pelo a Q]` coincide y se activa la entrada de bromear. Para *"el camarero tomó la orden"*, el patrón específico no aplica y el parser cae al *tomar* genérico (tomar = recibir/registrar).

Hasta acá, igual que la polisemia. Lo nuevo es la **escala**: el español tiene del orden de varios miles de colocaciones fijas y locuciones verbales. Inglés tiene más. Cualquier lengua los tiene. Construir un lexicon que cubra el grueso de las locuciones es trabajo de años de lingüistas y, hoy, un buen candidato para aprenderse parcialmente de modelos de lenguaje: los LLMs ya conocen las locuciones; el problema es codificarlas en un diccionario explícito que el motor pueda consultar.

Este capítulo no resuelve ese trabajo. Lo importante para el modelo es que la **arquitectura lo admite sin contorsiones**: el lexicon es extensible por diseño, y cada locución que se registra es una entrada como cualquier otra.

## Donde el modelo todavía sufre

Sería deshonesto cerrar la Parte IV pretendiendo que con nominalizaciones, modales e idiomas se cubren todos los casos difíciles del lenguaje natural. Hay zonas donde el modelo apenas alcanza y otras donde derechamente cruje. Las dejo enumeradas, sin remedio, porque la honestidad del libro depende de no esconderlas.

**Negación y alcance.** *"Juan no cree que María vino"* y *"Juan cree que María no vino"* son oraciones distintas — la negación tiene **alcance** diferente sobre lo embebido. El modelo distingue ambas (la primera niega la situación-de-creer, la segunda niega la situación-embebida-de-venir), pero la ambigüedad sintáctica del español puede hacer difícil el parsing automático.

**Cuantificación generalizada.** *"La mayoría de los pacientes mejora con el tratamiento"* introduce un cuantificador generalizado que no es un agente identificable. El modelo reifica esto como una afirmación sobre una clase (con propiedades de proporción y muestra), pero la formalización honesta requiere extensiones a la lógica de hechos atómicos que todavía están pendientes.

**Aspecto fino.** El español distingue *empezó a hablar*, *estaba hablando*, *terminó de hablar*, *seguía hablando*, *acababa de hablar*. Cada uno marca un momento distinto de un evento. El modelo cubre lo grueso (con `aspecto: perfectivo / imperfectivo / progresivo / completivo`) pero las distinciones finas requieren reificar el evento y sus subfases — trabajo viable pero pesado.

**Presuposiciones.** *"Juan dejó de fumar"* presupone que Juan fumaba antes; *"María se arrepiente de haber renunciado"* presupone que María renunció. El modelo registra los hechos afirmados, pero las presuposiciones — las cosas que la oración da por sentado sin afirmarlas — no se capturan automáticamente; quedan como trabajo del parser o del LLM que produce la representación.

**Discurso e implicaturas.** *"¿Puedes pasarme la sal?"* no es una pregunta sobre capacidad; es un pedido. La diferencia entre lo dicho y lo significado vive en la pragmática, y el modelo todavía no tiene un mecanismo claro para representarla salvo por convenciones específicas del dominio.

Estos casos no son tachas del modelo — son áreas activas de investigación lingüística después de décadas de trabajo. Lo que importa es que el modelo **no se rompe**: produce representaciones parciales útiles, y deja explícito qué no representa. El día que la representación sea mejor, los hechos extras simplemente se agregan al grafo; nada de lo ya almacenado se invalida.

## Cierre de Parte IV: lo estructurado al servicio de lo conversacional

Una reflexión que conviene dejar dicha al cerrar esta parte. Mientras este libro se escribe, los modelos de lenguaje contemporáneos manejan ventanas de contexto de un millón de tokens y la **ingeniería de prompts** se ha vuelto una disciplina por derecho propio. El instinto natural cuando hay tanto espacio disponible es escribir en lenguaje natural — descripciones largas, historias clínicas redactadas en prosa, contratos completos, registros operativos en bruto — y dejar que el modelo encuentre lo que necesita por sí solo.

Funciona. Pero gasta presupuesto de tokens en forma desmedida y arrastra la **ambigüedad** del lenguaje hasta el final del pipeline. Una historia clínica en prosa puede tomar dos mil tokens; los mismos hechos representados como un grafo de situaciones reificadas en formato WQuestions caben en seiscientos. Y, más importante, el grafo es **inequívoco**: no requiere que el modelo reinterprete, no introduce ambigüedades de coreferencia, no se confunde entre *él* y *el doctor*. El LLM puede dedicar sus capacidades a lo que hace mejor — razonar, conversar, decidir — en lugar de gastar su atención reconstruyendo estructura a partir de texto plano.

La relación entre WQuestions y los modelos de lenguaje, vista así, es **simbiótica**. El LLM aporta lo que el modelo no tiene: capacidad lingüística, manejo de implicaturas, intuición pragmática, generación fluida. WQuestions aporta lo que el LLM no tiene: persistencia inequívoca, consultabilidad estructural, auditoría, identidad estable de entidades, distinción explícita entre lo afirmado y lo modal. Cuando ambos trabajan juntos — el LLM como traductor en la entrada y la salida, el grafo como sustrato persistente — cada uno hace lo suyo y la conversación resultante es a la vez fluida y rigurosa.

Esa simbiosis es la base de los capítulos finales del libro. Pero antes — y aquí termina la teoría — viene la Parte V: ver cómo todo esto se aplica, sin atajos, a dominios concretos de extremo a extremo.
