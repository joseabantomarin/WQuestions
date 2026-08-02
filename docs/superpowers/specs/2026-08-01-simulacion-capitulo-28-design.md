# Capítulo 28 · El grafo como lienzo del futuro

Diseño validado · 2026-08-01

## Origen

Un texto suelto sobre «WQuestions como motor de simulación» que no estaba en el
libro. La revisión del manuscrito mostró que el tema sí aparece, pero reducido a
una viñeta dentro de la Familia 3 del capítulo 27 («Simulación sobre hechos y
reglas»). Este capítulo la promueve a capítulo propio y corrige dos afirmaciones
del texto original que el propio libro desmiente.

## Tesis

Un simulador necesita tres cosas: estado actual, regla de transformación y
estado proyectado. La tesis no es que WQuestions pueda alojar las tres, sino que
**no necesita nada nuevo para alojarlas**. Un hecho proyectado es un hecho
corriente cuya vigencia empieza en el futuro y que cuelga de un escenario. La
simulación no es un subsistema: es una lectura del mismo grafo.

La espina del capítulo la da el capítulo 23. Allí el auditor recorre
`causado_por` hacia atrás, del accidente de Quispe al desprendimiento y de este
al debilitamiento de la pared. El simulador recorre los mismos cables en la
dirección contraria: de una intervención propuesta a sus consecuencias
proyectadas. Mismo mecanismo, signo cambiado.

El corolario cierra el capítulo: la explicabilidad no se añade, se hereda. En un
simulador convencional el rastro de por qué el modelo llegó a un número se
pierde. Aquí el rastro *es* el dato, porque los cables de D7 quedaron escritos al
proyectar.

## Correcciones al texto original

| Pieza | Texto original | Capítulo | Motivo |
|---|---|---|---|
| Estado inicial | tripletas situadas | igual | correcto |
| Ramas paralelas | tiempo de transacción ($T_{assert}$) | **escenario reificado en O (D4)** | dos relojes no ramifican; un nodo sí |
| Avance del tiempo | bitemporalidad completa | **valid time (D6), `valid_from` futuro** | es lo único implementado hoy |
| Causalidad | D7 | igual | correcto |
| Agencia | D5 | igual | correcto |

La numeración `Dn` del texto original es correcta y se conserva: D5 agencia
contextual, D6 vigencia temporal, D7 los cuatro cables. Verificada contra
`libro/manuscrito2/anexo-reglas.html`.

El escenario como entidad da lo que el tiempo de transacción no daría nunca:
**N ramas simultáneas**, no dos. Y como es una entidad, admite lo que cualquier
entidad admite: agente, fecha, `justificado_por` la regla que lo generó.

## Validación ejecutada

Guion aislado sobre `prototipo/ejemplos/minera.py` (el capítulo 23 ejecutable),
en memoria, sin tocar el universo persistente `~/.wquestions/universe.jsonl`
(4.833 hechos reales del usuario). Resultados que el capítulo transcribe:

| Prueba | Resultado |
|---|---|
| Contaminación del presente | `camion_007` tenía 4 hechos vigentes hoy antes y después de simular |
| Hecho proyectado al consultar hoy | invisible; solo se ven los 5 estructurales sin fecha |
| El mismo hecho al 2026-07-15 | visible: `disponibilidad` 94,0 %, `monto` 41.200 t |
| Aislamiento entre ramas | cada escenario contiene exactamente sus dos miembros |
| Comparar escenarios | una consulta: 41.200 t (junio) contra 39.850 t (agosto) |
| Cadena causal | los mismos hechos, hacia atrás dan la cadena del accidente; hacia adelante, la simulación |
| Vocabulario | 13 roles: 9 canónicos del catálogo, 4 de dominio (`estado` ya se usa 18 veces en el cap. 23). Cero mecanismos nuevos |
| Hechos reales modificados | 0 — el almacén es append-only |

El guion queda como artefacto reproducible en `prototipo/ejemplos/simulacion.py`.

## Estructura

| Sección | Contenido |
|---|---|
| Apertura | El planificador ante la decisión: adelantar el mantenimiento del `camion_007` a junio o sostenerlo hasta agosto. Escena, no definición |
| Lo que ya sabes hacer | La cadena del cap. 23 girada 180°. Figura 28.1: las mismas flechas, la otra dirección |
| El escenario como entidad | D4 aplicada al escenario. Aislamiento estructural, no temporal |
| Proyectar es fechar hacia adelante | D6 con `valid_from` futuro; `ask(at=...)` sirve igual para el pasado y para el futuro |
| La regla como hecho | La lógica vive en el grafo, fechada y consultable. Enlaza con el Frente 1 del cap. 31 |
| Agentes simulados | D5: el camión es objeto cuando lo reparan y agente cuando produce |
| Escenario contra escenario | Comparar dos ramas es una consulta, no una función. Figura 28.2 |
| Por qué el resultado se explica solo | El corolario: la trazabilidad se hereda |
| Los límites | Seco, sin confesionario |

## Límites que el capítulo declara

Como hoja de ruta, no como confesión:

- **Falta el tiempo de transacción** (Frente 2, cap. 31). Consecuencia concreta:
  puedes preguntar qué proyectaste, no cuándo lo proyectaste, salvo que lo
  escribas como hecho del escenario.
- **El grafo no calcula.** No hay motor de inferencia (Frente 1). El grafo
  sostiene estado, reglas y resultado; quien multiplica es el llamador o el
  modelo de lenguaje. La explicabilidad no depende de eso.
- **Nada valida el escenario.** Mundo abierto: un escenario absurdo se guarda
  igual de bien que uno sensato.

## Cambios estructurales

1. Nuevo `28-simulacion.html`, Parte VI, entre el 27 y la prueba reflexiva.
2. Renumeración 28→29 … 34→35: renombrar archivo y actualizar en cada uno
   `<title>`, `og:title`, `og:url`, `twitter:title`, `--cap`, `num-cap` y la
   navegación previo/siguiente.
3. Siete stubs de redirección en las rutas viejas (`meta refresh` + `canonical`),
   para no romper las URLs públicas ya compartidas.
4. `indice.html`, `index.html`, `referencias.html`.
5. Las ~18 menciones «capítulo NN» en prosa. Las densas: `33-anexo-prototipo`
   (cinco veces al 30), `24-yaku` (tres).
6. La viñeta de simulación en la Familia 3 del cap. 27 se acorta y remite al 28.
7. Tabla §5 de `GUIA-DE-ESTILO.md` (interna, quedaría desfasada).
8. Nuevo `prototipo/ejemplos/simulacion.py`: el guion de validación, limpio y
   con sus aserciones, para que el capítulo sea reproducible como lo son los
   demás capítulos de dominio.

## Desajuste resuelto

El `b04` del libro contra el `b03` del prototipo resultó ser la punta de una
deriva mayor: la reescritura HTML del capítulo 23 creó un escenario nuevo
(turno de noche, otro banco, otras magnitudes) y el prototipo se quedó con el de
la edición Markdown. Siete contradicciones en total:

| Concepto | Libro (canónico) | Prototipo (antes) |
|---|---|---|
| Turno | `turno_noche_2026_05_19`, 18:00→06:00 | `turno_dia_2026_05_19`, 06:00→18:00 |
| Accidente | 23:40 | 11:40 |
| Banco, frente, debilitamiento | `b04` | `b03` |
| Desprendimiento | `evento_desprendimiento_07` | `..._001` |
| Producción | 2.480 t @ 8,6 g/t | 2.400 t @ 8,2 g/t |
| Oro fino | 685,8 oz | 632,7 oz |
| Arsénico medido | 0,34 mg/L | 0,32 mg/L |

Manda el libro: el turno de noche no es un desliz sino una decisión narrativa que
sostiene el capítulo entero («mientras todos duermen, el camión registra horas de
motor en un turno desierto»). El prototipo se alineó, y sus 18 validaciones y los
32 tests siguen pasando. La extracción se movió de 09:15 a 21:15 para caer dentro
del turno nuevo; el libro no la fecha, así que no había restricción.

Única decisión de criterio: la norma ambiental pasó de `ds_004_2017_minam` a
`eca_agua_cat3`, que es lo que el libro cita. Se pierde la referencia al decreto
peruano real; el organismo regulador (`oefa_peru`) sigue en el modelo.

## Canon a respetar

- Español neutro, tuteo (`puedes`, `quieres`). Prohibido el voseo.
- Apertura con escena concreta; densidad técnica creciente.
- Identificadores canónicos del cap. 23: `camion_007`, `tajo_norte`,
  `nivel_4250`, `supervisor_mamani`, `operador_quispe`, `planta_procesamiento`,
  `produccion_oro`, `orden_trabajo_88`.
- Ninguna caja `caja--decision` con una `Dn` que este capítulo no defina: el 28
  solo referencia D4, D5, D6 y D7. Se usan `caja--idea` / `caja--practica`.
- La raya (—) solo para ritmo o énfasis; paréntesis para lo secundario, dos
  puntos para introducir.
