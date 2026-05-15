# Capítulo 11 — El "por qué" no es una pregunta más

## Cuatro preguntas que parecen una

Tomemos cuatro preguntas que en español comienzan con las mismas dos palabras:

- *¿Por qué se cayó el vaso?* — Porque alguien lo empujó.
- *¿Por qué Marta vendió la casa?* — Porque quería mudarse a otra ciudad.
- *¿Por qué el cirujano abrió esta vía?* — Para acceder al pulmón izquierdo.
- *¿Por qué el contrato se rescindió?* — Porque la cláusula 14 lo prevé en caso de impago.

Las cuatro respuestas comienzan con un "porque" o un "para" — pero las cuatro están explicando cosas radicalmente distintas. La primera describe una **causa física**: un empujón transfiere momento, el vaso cae, la gravedad termina el trabajo. La segunda describe un **motivo psicológico**: un deseo, una intención de Marta. La tercera describe una **finalidad**: el cirujano apunta a un estado futuro al que su acción está dirigida. La cuarta describe una **justificación normativa**: la rescisión está autorizada por una regla previa.

Si miramos solo el "porque" superficial, las cuatro son intercambiables. Si miramos qué tipo de cosa está respondiendo, son cuatro respuestas a cuatro preguntas distintas. Y esto tiene una consecuencia inmediata para el diseño del modelo: si quisiéramos un eje "por qué", **¿qué valores iría a contener?**

## Por qué no hay un eje "por qué"

Recordemos cómo se ven los demás ejes. Q contiene agentes — individuos capaces de acción intencional. T contiene momentos — puntos o rangos en alguna escala temporal. K contiene categorías — conceptos atemporales con su jerarquía. Cada eje es homogéneo: todo lo que vive en él comparte una naturaleza ontológica común.

Para que existiera un eje "por qué", su contenido debería ser igualmente homogéneo. Pero no lo es: la respuesta a *"¿por qué se cayó el vaso?"* es **una situación previa** (el empujón ∈ O); la respuesta a *"¿por qué vendió la casa?"* es **una motivación** (un deseo, que también podría reificarse en O, pero con una semántica completamente distinta); la respuesta a *"¿por qué abrió esa vía?"* es **un estado futuro** (un objeto en O todavía no realizado); la respuesta a *"¿por qué el contrato se rescindió?"* es **una regla** (otro tipo de objeto en O, este normativo).

Forzar todo eso en un único eje sería meter en la misma bolsa cuatro cosas que el lenguaje natural distingue por buenas razones. La consulta *"¿qué causó X?"* es distinta de *"¿cuál es el propósito de X?"*; pedirle a un sistema que las trate igual condena al usuario a desambiguar a mano.

Aquí entra la **decisión de diseño 6 (D6)**: el modelo *no* tiene un eje "por qué". En su lugar, ofrece **cuatro relaciones canónicas**, cada una con su semántica explícita, viviendo todas como predicados ordinarios en M(O, O) — porque sus argumentos son siempre situaciones.

```
causado_por      : O → O     (causalidad mecánica/física)
motivado_por     : O → O     (intención de un agente)
con_finalidad    : O → O     (propósito; objeto situado en el futuro)
justificado_por  : O → O     (autoridad normativa o regla)
```

Cuatro relaciones, no un eje. Cuatro preguntas, no una sola. El "por qué" del lenguaje natural se desambigua antes de entrar al modelo, no después.

![Las cuatro relaciones canónicas del "por qué": cada una conecta una situación con otra de naturaleza distinta — causa previa, intención del agente, estado futuro buscado, regla que la autoriza.](../diagrams/png/19_cuatro_por_que.png)

## Las cuatro relaciones, una por una

### `causado_por` — la causa eficiente

`causado_por` describe la conexión mecánica entre dos eventos: el primero produce el segundo, sin que medie deseo, intención o regla. Es el "porque" del mundo físico, del dominó que cae, de la presión que rompe un dique.

```
(caida_vaso_001, causado_por, empujon_001)        ∈ M(O, O)
(incendio_edif_017, causado_por, cortocircuito_001)
(infeccion_001, causado_por, bacteria_001)
```

La relación es asimétrica y, en general, transitiva: si A causa B y B causa C, entonces A causa C — aunque la cadena se va volviendo más débil cuanto más larga. Es la relación que la física, la medicina diagnóstica y la ingeniería forense rastrean.

Una propiedad importante: `causado_por` no necesita agentes. Un terremoto causa un derrumbe sin que nadie quiera nada. El modelo lo refleja: ninguna de las situaciones involucradas necesita tener agente.

### `motivado_por` — el motivo intencional

`motivado_por` describe la conexión entre una acción y el estado mental (deseo, creencia, miedo) del agente que la ejecuta. Es la explicación que damos cuando la pregunta no es *"¿qué hizo que ocurriera X?"* sino *"¿qué llevó al agente a hacer X?"*.

```
(venta_casa_002, motivado_por, deseo_mudarse_marta)    ∈ M(O, O)
(renuncia_001,   motivado_por, conflicto_con_jefe_017)
(consulta_medica_046, motivado_por, dolor_persistente_001)
```

La diferencia con `causado_por` es semántica y no siempre obvia, pero clave. *"El incendio causó el derrumbe"* es distinto de *"el incendio motivó la evacuación"*. El derrumbe no es algo que el edificio *quisiera* hacer; la evacuación sí — alguien la decidió, en respuesta al incendio. Los motivos viven en mentes; las causas no.

En la práctica, el motivo suele ser otra situación reificada: un deseo, una creencia, una percepción. Cuando el modelo necesita registrar *por qué un agente hizo algo*, esa razón se reifica como cualquier otra situación, con su sujeto (el agente que tenía el motivo), su contenido y su momento. Y se conecta a la acción por `motivado_por`.

### `con_finalidad` — el propósito teleológico

`con_finalidad` es la relación más rara de todas, porque su objeto no es algo que ya ocurrió, sino **algo que se busca que ocurra**. Es la teleología explícita: la acción está orientada hacia un estado futuro, todavía no realizado.

```
(incision_001, con_finalidad, acceso_pulmon_izquierdo_001)   ∈ M(O, O)
(rebajar_precio_001, con_finalidad, aumento_ventas_q3_2026)
(reunion_004, con_finalidad, decision_inversion_001)
```

¿Cómo modelamos un estado futuro? Como una situación reificada con su `estatus_factual : K` apuntando a un valor del catálogo K que indica modalidad — `previsto`, `intencionado`, `pendiente`, `hipotetico`. El estado futuro **vive en O** porque es objeto del cual hablamos; pero está marcado como no realizado.

Esta es la razón por la que el modelo no tiene tres "tiempos verbales" como eje propio: el pasado, el presente y el futuro de una situación se distinguen por su `estatus_factual`, no por una dimensión temporal nueva. La situación con finalidad existe en O ahora; lo que apunta al futuro es su modalidad.

### `justificado_por` — la autoridad normativa

`justificado_por` aparece cada vez que una acción no se explica por causa, motivo o finalidad, sino por **una regla previa que la autoriza o exige**. Es el "por qué" del derecho, los procedimientos, los protocolos clínicos, las cláusulas contractuales.

```
(rescision_contrato_017, justificado_por, clausula_14_contrato_017)   ∈ M(O, O)
(despacho_radioactivo_001, justificado_por, protocolo_iaea_2022)
(rechazo_devolucion_001, justificado_por, politica_30_dias_tienda)
```

La situación justificadora no es una causa física ni una intención: es una **norma**, expresada como una situación que vive en O y que tiene su propia forma. Por lo general, una norma reificada incluye `condicion`, `consecuencia`, `vigencia_desde`, `emisor`, `prioridad` — más sobre esto en la siguiente sección.

`justificado_por` es la relación que hace auditable cualquier sistema regulado: explica no qué pasó, sino bajo qué autoridad. En dominios como el clínico, el financiero o el legal, esta relación suele ser **obligatoria** para que una acción se considere válida.

## Las cuatro pueden coexistir

Una misma situación puede tener varias de estas relaciones simultáneamente, y cada una explica un aspecto distinto. Una cirugía concreta puede:

```
(cirugia_023, causado_por,      tumor_001)                    ← qué la hizo necesaria
(cirugia_023, motivado_por,     pedido_paciente_001)          ← por qué el agente la decidió
(cirugia_023, con_finalidad,    extirpacion_tumor_001)        ← qué busca lograr
(cirugia_023, justificado_por,  protocolo_oncologico_2025)    ← bajo qué autoridad procede
```

Cuatro hechos atómicos, cuatro respuestas distintas a la misma pregunta superficial. Esto es lo que pierde un modelo que unifica todos los "por qué" en un solo campo: la riqueza explicativa se aplana.

## Cadenas explicativas

Las relaciones del "por qué" rara vez aparecen aisladas. Encadenadas, producen lo que llamamos una **cadena explicativa**: una secuencia de situaciones conectadas por relaciones causales, motivacionales, teleológicas o normativas, que reconstruye cómo se llegó a un hecho.

Tomemos un caso de noticia política: el ministro renuncia. ¿Por qué? Porque enfrenta una investigación. ¿Por qué hay una investigación? Porque un periodista publicó una nota. ¿Por qué publicó esa nota? Porque recibió una filtración. ¿Por qué recibió la filtración? Porque un funcionario disconforme decidió contactarlo.

```
(renuncia_ministro_001,     motivado_por, investigacion_001)
(investigacion_001,         causado_por,   publicacion_nota_001)
(publicacion_nota_001,      causado_por,   filtracion_001)
(filtracion_001,            motivado_por,  disconformidad_funcionario_001)
```

La cadena no es una metáfora — es un grafo recorrible. Una consulta del tipo *"¿qué eventos contribuyeron, directa o indirectamente, a la renuncia del ministro?"* es simplemente un recorrido transitivo sobre las relaciones de la familia "por qué" partiendo del nodo `renuncia_ministro_001`. El motor no necesita saber nada del dominio: solo seguir las aristas.

![Una cadena explicativa: cómo cuatro relaciones canónicas del "por qué", encadenadas, reconstruyen una historia entera desde un evento final hasta sus orígenes lejanos.](../diagrams/png/20_cadena_explicativa.png)

Y como las relaciones llevan su semántica explícita, la cadena no es ciega: distingue entre causalidad física, motivación humana, propósito y autoridad. Una consulta puede pedir *"solo causas físicas"* o *"solo motivaciones"* o *"toda la cadena, pero etiquetada por tipo"*. Esta es la ventaja concreta de no haber unificado los cuatro "por qué" en un campo único.

## Reglas declarativas: la convención

Hay un caso especial que merece atención: cuando la justificación de una acción es una regla. ¿Cómo se modela una regla en sí misma?

El modelo trata las reglas como **situaciones reificadas de un tipo particular** — tipo `regla` o `norma`. Una regla tiene una forma canónica: un antecedente (la condición), un consecuente (la acción autorizada o exigida), un alcance (a qué situaciones aplica), una vigencia (desde cuándo y hasta cuándo es válida) y un emisor (quién la promulgó).

```
(regla_devolucion_001) ∈ O
  instancia_de    : regla
  emisor          : tienda_central
  vigencia_desde  : 2025-01-01
  vigencia_hasta  : null
  condicion       : situacion_compra con dias_desde_compra ≤ 30 y producto_no_perecedero = true
  consecuente     : devolucion_autorizada
  prioridad       : 1
```

Una vez reificada, la regla es un objeto del modelo: puede citarse, puede modificarse (con D9 — vigencia temporal — para conservar el historial), puede entrar en conflicto con otra regla y resolverse por prioridad. Cuando una situación cae bajo su alcance, la conexión es directa:

```
(devolucion_solicitada_017, justificado_por, regla_devolucion_001)
```

Esto importa por dos razones prácticas. La primera: el sistema queda **auditable** sin trabajo adicional. La pregunta *"¿por qué se permitió esta devolución?"* se responde recorriendo `justificado_por` hasta llegar a una regla, y esa regla incluye su versión vigente al momento de la decisión. La segunda: el modelo se vuelve **extensible normativamente** sin tocar el código. Una regla nueva se agrega como cualquier otra situación reificada; no hace falta migrar esquema.

Conviene aclarar el alcance: esta convención permite **registrar** reglas con suficiente estructura para que sean consultables, pero **no convierte al modelo en un motor de inferencia**. Para que una regla *dispare* — es decir, para que el sistema deduzca automáticamente *"este caso cumple la condición, por lo tanto aplico el consecuente"* — hace falta un componente adicional: un evaluador. Ese evaluador puede ser SHACL para validación, Datalog para razonamiento, una regla custom en código aplicación, o un LLM consultando la regla como contexto. WQuestions provee el **soporte declarativo**; el razonamiento sobre él se construye encima.

## Lo que se gana

Repasemos lo que la familia de relaciones del "por qué" aporta al modelo, comparado con dos alternativas peores.

Una alternativa sería un único campo `razon` o `motivo` colgado de cada situación, conteniendo texto libre. Esto es lo que muchos sistemas hacen, y es lo que produce los infames campos *"observaciones"* o *"justificación"* que terminan siendo cementerios de información no consultable. Sin estructura explícita, ningún motor puede recorrer cadenas, distinguir tipos de explicación o auditar decisiones.

Otra alternativa sería un único predicado `por_que`, sin discriminar tipos. Esto mejora respecto al texto libre porque ya es estructura, pero pierde la distinción semántica entre causa, motivo, finalidad y justificación — distinción que el lenguaje natural mantiene porque le sirve. El usuario que consulta tiene que adivinar a cuál se refería cada hecho, y los reportes mezclan razones físicas con motivos psicológicos como si fueran lo mismo.

La familia de cuatro relaciones canónicas captura lo que el lenguaje ya hacía: distingue explícitamente los cuatro tipos de explicación, los expresa como hechos atómicos sobre el universo O × O, y los integra a la misma maquinaria de consulta que el resto del modelo. Sin esfuerzo extra, el grafo deja de ser una colección de hechos y se convierte en una **explicación recorrible**.

## Cierre de la Parte III

Con esto cerramos la Parte III. Empezamos con el hecho atómico como unidad mínima (capítulo 8); le dimos geometría con el espacio multidimensional (capítulo 9); le dimos puntos articuladores con las situaciones reificadas (capítulo 10); y ahora le dimos conectores explicativos con las cuatro relaciones del "por qué".

Lo que tenemos es un modelo donde el universo entero se describe con tripletas sobre ocho ejes, los puntos de articulación son situaciones, y la estructura explicativa emerge de un puñado de relaciones canónicas. Toda la maquinaria conceptual está lista.

Falta lo que hace que esta maquinaria sea **utilizable** desde el lenguaje humano — porque al final del día nadie va a escribir tripletas a mano. La Parte IV se ocupa de eso: cómo el verbo de una oración determina la signatura de la situación que describe, cómo un diccionario de verbos (el *lexicon*) hace de compilador entre el lenguaje natural y el modelo, y qué hacer cuando el lenguaje se pone difícil — nominalizaciones, modales, idiomas.
