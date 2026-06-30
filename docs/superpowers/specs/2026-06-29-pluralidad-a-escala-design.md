# Diseño · El cierre "a escala": llevar el modelo del singular a la pluralidad

**Fecha:** 2026-06-29
**Ámbito:** libro WQuestions, edición HTML canónica (`libro/manuscrito2/`)
**Estado:** aprobado por el autor — pendiente de plan de ejecución

## Problema

El modelo se explica casi siempre en **singular**: un paciente, una venta, un
taxista, un préstamo, una ley. En datos reales, el valor dramático está en la
**pluralidad**: reportes, consolidados, listados y agregaciones sobre muchas
entidades ("todos los pacientes diagnosticados con X", "total de créditos por
estado", "ranking de productos del mes"). Modelar bien un caso individual parece
trivial; el verdadero dilema aparece al consolidar a miles.

Diagnóstico (verificado capítulo a capítulo):

- **La capacidad ya existe pero está localizada.** El cap. 08 enseña la vista
  pivote / agregación a fondo; el cap. 16 (spa) usa `suma()`/`count()` de verdad;
  el anexo de código (cap. 32) documenta `count`/`suma`/`promedio`.
- **El encuadre narrativo es casi todo singular.** La teoría (caps. 02–15) y
  sobre todo los dominios industriales (clínica, banco, ERP, universidad,
  municipalidad, minera) modelan *un* caso y nunca dan el salto a "todos los X
  con condición Y". De ahí la sensación de "datos sueltos".

No es un problema de capacidad del modelo, sino de **mostrar el pago**: que el
lector vea que modelar bien el caso singular es justo lo que hace triviales los
reportes sobre miles.

## El dispositivo: el cierre "a escala"

Un **cierre narrativo integrado en la prosa** (no una caja, no un recuadro) que
aparece tras el caso singular central de un capítulo. Toma *ese mismo* caso y lo
abre a la pluralidad, dejando claro que el modelo ya responde el reporte sin
estructura nueva.

**Forma:**

- 2–5 frases, voz del libro, registro medio (el ya calibrado).
- Donde el capítulo usa código, remata con **una** consulta concreta
  (`count`/`suma`/patrón), no más.
- **Sin** encabezado fijo repetido (nada de "A escala:" en cada capítulo: ese
  sonsonete es justo lo que hay que evitar). La transición es prosa, variando la
  entrada de un capítulo a otro.

Ejemplo de tono (clínica):

> Pero lo dramático no es la consulta de Vega. Es que ese mismo grafo, sin una
> tabla más, sabe responder cuántos pacientes ingresaron con dengue en junio, o
> qué diagnóstico encabezó el trimestre. Modelar bien el caso de uno es, sin
> querer, haber modelado el de todos.

**Regla anti-redundancia (clave):** cada cierre ataca la pluralidad desde un
**ángulo distinto**; no repite "el mismo grafo responde por muchos". Catálogo de
ángulos a repartir sin repetir:

- cohorte por categoría
- suma / promedio
- recorrer un cable sobre todos los sujetos
- columna consultable (apilar tripletas)
- todas las situaciones de un tipo
- agrupar por causa (causa raíz)
- consolidar una identidad entre sistemas
- agrupar por signatura de verbo
- reporte en el idioma del usuario
- ranking
- serie temporal de una cohorte
- privacidad de agregados

## Restricciones editoriales

- Editar **solo la HTML canónica** (`libro/manuscrito2/`); el markdown
  (`libro/manuscrito/`) queda fuera (está desfasado).
- Registro **medio**; glosar jerga sin quitarla.
- **Raya (—)** solo para ritmo/énfasis; preferir paréntesis / dos puntos según
  función.
- **No auto-proclamar** virtudes ("esto es elegante / honesto"): mostrar, no
  declarar.
- Tuteo neutro (no voseo argentino).
- No tocar la capacidad del modelo (ya existe); esto es encuadre narrativo.

## Mapa por capítulo

Tres niveles de tratamiento:

- **Núcleo:** cierre completo, prosa + una consulta concreta.
- **Ligero:** 1–2 frases, sin código.
- **Ajuste:** el capítulo ya cubre pluralidad; solo coser la idea recurrente.
- **Omitir:** añadirlo sería forzado o redundante.

| Cap | Ángulo de pluralidad (distinto en cada uno) | Nivel |
|----|----|----|
| 00 introducción | Sembrar: no un paciente, la sala entera | Ligero |
| 02 cuatro pilares | Las 4 preguntas rebanan muchas situaciones a la vez | Ligero |
| 03 clase (K) | Cohorte por plantilla: "todas las unidades del modelo X" | Núcleo |
| 04 cuánto (N) | Suma / promedio nativos: "total facturado", "descuento medio" | Núcleo |
| 05 predicados (M) | Recorrer un cable sobre todos los sujetos | Ligero |
| 07 hecho atómico | Apilar tripletas = columna consultable (semilla del reporte) | Núcleo |
| 08 espacio multidim. | Ya lo tiene (pivote). Coser la idea recurrente y nombrarlo como "hogar" del reporte | Ajuste |
| 09 situaciones | Todas las situaciones de un tipo: "todas las consultas de junio" | Núcleo |
| 10 por qué | Agrupar por causa: "fallas causadas por X" (causa raíz) | Núcleo |
| 11 identidad | Consolidar a una persona entre sistemas → vista única | Ligero |
| 13 verbo | Agrupar por signatura: todo lo que activa el mismo verbo | Ligero |
| 14 lexicon | Reportes en el idioma del usuario (no en etiquetas canónicas) | Ligero |
| 16 spa | Ya usa suma/count. Reforzar el encuadre, sin recargar | Ajuste |
| 17 taxi | Operación de flota: viajes por zona/hora, ranking de choferes | Núcleo |
| 18 clínica | Cohorte epidemiológica: "todos los pacientes con dengue", ocupación | Núcleo |
| 19 banco | Cartera: "créditos por estado", mora agregada, reporte regulatorio | Núcleo |
| 20 ERP | Consolidado que cruza módulos: ventas por línea, inventario por almacén | Núcleo |
| 21 universidad | Estadística académica: alumnos por carrera, tasa de aprobación | Núcleo |
| 22 municipalidad | El cap. 8 ya pivota trámites → otro ángulo: tiempo medio de resolución por tipo (SLA) | Núcleo |
| 23 minera | Confiabilidad: fallas por equipo, disponibilidad, punchlists abiertas | Núcleo |
| 24 yaku | Consolidados reales del negocio (ventas por servicio) | Núcleo |
| 25 cuatro dominios | Ranking por dominio: goleadores, contratos por estado | Ligero |
| 29 seguridad | Privacidad de agregados (reportar sobre muchos sin exponer a uno) | Ligero |
| 31 conclusión | Eco temático de cierre: modelar a uno fue modelar a todos | Ligero |

**Omitir** (añadirlo sería forzado o redundante): 01 torre de Babel, 06 raíces,
12 puentes, 15 bajo presión, 26 LLMs, 27 aplicaciones, 28 prueba reflexiva, 30
qué falta.

(Decisión abierta menor: en el cap. 26 podría caber un guiño Ligero — el LLM
redacta la consulta de reporte desde lenguaje natural. Por ahora se omite salvo
indicación contraria.)

## Coherencia entre capítulos (anti-redundancia operativa)

- Antes de redactar cada cierre, revisar los ángulos ya usados en capítulos
  previos y elegir uno no repetido del catálogo.
- Variar la frase de entrada (no empezar dos cierres igual).
- Los niveles **Ligero** no llevan código; reservar las consultas para los
  **Núcleo**, y aun ahí una sola.
- Donde el capítulo ya hace agregación (08, 16), no duplicar: conectar con la
  idea recurrente.

## Fuera de alcance

- Regenerar el PDF (`WQuestions.pdf` vía `generar_pdf.py`/`convertir.sh`): paso
  aparte y posterior, solo si el autor lo pide.
- El markdown desfasado (`libro/manuscrito/`).
- Cambios en el prototipo o en las APIs (la capacidad ya existe).

## Verificación

- Tras editar, revisión visual de un par de capítulos representativos en el
  navegador (uno de teoría, uno de dominio).
- Repaso de redundancia leyendo los cierres en secuencia.

## Criterio de éxito

Un lector que recorra el libro ya no percibe "datos sueltos": en cada punto donde
importa, ve que el caso singular era la puerta a reportes y consolidados sobre
muchos, sin estructura nueva — y cada vez por una razón distinta.
