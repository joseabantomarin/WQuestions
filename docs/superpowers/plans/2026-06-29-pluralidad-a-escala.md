# El cierre "a escala" — Plan de implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Añadir, capítulo a capítulo del libro, un cierre narrativo que lleva el caso singular a la pluralidad (reportes, consolidados, agregaciones), para que el modelo no se lea como "datos sueltos".

**Architecture:** Trabajo editorial sobre la HTML canónica (`libro/manuscrito2/`). Cada capítulo del mapa recibe un párrafo de cierre integrado en la prosa (nivel Núcleo, Ligero o Ajuste). No hay código de aplicación ni tests automatizados: la verificación es lectura del párrafo, chequeo de las restricciones editoriales y control de redundancia entre capítulos. Un commit por capítulo.

**Tech Stack:** HTML estático + CSS del libro (`assets/estilo.css`). Sin build obligatorio (el PDF se regenera aparte y fuera de alcance).

## Global Constraints

Cada tarea hereda estas reglas (verbatim del spec):

- Editar **solo** `libro/manuscrito2/` (HTML canónica). No tocar `libro/manuscrito/` (markdown desfasado).
- Registro **medio**: más llano pero con voz; glosar jerga sin quitarla.
- **Raya (—)** solo para ritmo/énfasis; paréntesis = secundario, dos puntos = introduce idea.
- **No auto-proclamar** virtudes ("elegante", "honesto", "potente"): mostrar, no declarar.
- Tuteo neutro (no voseo argentino: "puedes", no "podés").
- El cierre es **prosa integrada**, no una caja/recuadro. Sin encabezado fijo repetido ("A escala:").
- 2–5 frases. En nivel **Núcleo**, rematar con **una** consulta concreta (`count`/`suma`/patrón) y nada más. En **Ligero**, sin código.
- **Anti-redundancia:** cada capítulo usa un ángulo distinto del catálogo; variar la frase de entrada; nunca repetir "el mismo grafo responde por muchos".
- Insertar el cierre dentro de `<div class="contenido">`, tras el caso/sección central del capítulo (antes del cierre conceptual del capítulo si lo hay), como uno o más `<p>`. La consulta, si la hay, en el bloque de código del libro (`<div class="bloque-codigo">…<pre><code data-lang="python">`), imitando los que ya usa ese capítulo.

**API real del libro (verificada contra `prototipo/wq/query.py` y cap. 32) — usar EXACTAMENTE este idioma en los snippets:**

- `count(u, Pattern(...), *, at=None)` → entero (sujetos que satisfacen el patrón).
- `suma(u, "campo", Pattern(...))` y `promedio(u, "campo", Pattern(...))` → el campo numérico va **posicional, como string** (mismo molde que `count`, cambia qué devuelven). Ej. real del cap. 16: `suma(u, "monto", Pattern(fixed={"acreedor": fisco, "estatus_factual": u.ind("por_remitir")}, type_constraint=u.ind("impuesto_consumo_18")))`.
- `query(u, Pattern(fixed={}, ask={}, type_constraint=None), *, at=None)` → lista de bindings.
- En `Pattern`: roles en **crudo** (`"acreedor"`, `"estado"`), no `"rol:..."`. Valores y tipos con `u.ind("...")`. El tipo de situación va en `type_constraint=u.ind("...")`, no como `fixed["rol:tipo"]`.
- **No existe GROUP BY ni agrupación en una sola llamada.** Un reporte "por categoría/estado/zona" se representa como (a) **un corte concreto** —un `count`/`suma` sobre un patrón fijo a un valor— y la prosa describe el reporte completo; o (b) una **tabla** estilo Fig. 8.5 (cada celda es un conteo de un cruce). Nunca inventar `ask={...}` para significar "agrupar por".
- `at=` recibe un `datetime` (`datetime(2026,6,30,tzinfo=timezone.utc)`), no un string. En estos snippets ilustrativos, **omitir `at=`** salvo que la temporalidad sea el punto.

**Catálogo de ángulos (repartir sin repetir):** cohorte por categoría · suma/promedio · recorrer un cable sobre todos · columna consultable (apilar tripletas) · todas las situaciones de un tipo · agrupar por causa · consolidar identidad entre sistemas · agrupar por signatura de verbo · reporte en idioma del usuario · ranking · serie temporal de cohorte · privacidad de agregados.

**Procedimiento estándar de cada tarea (sustituye al ciclo TDD):**
1. Leer el capítulo completo; localizar el caso/sección central y el punto natural de inserción (fin de la sección de modelado).
2. Anotar los nombres reales de los ejemplos del capítulo (personas, entidades, IDs) para que el cierre use ESOS nombres.
3. Insertar el cierre (texto borrador de la tarea, ajustado a los nombres reales).
4. Verificar contra las Global Constraints + que el ángulo no se repite con capítulos ya hechos.
5. Commit.

---

## Tranche 1 · Núcleo y Ajuste de la Parte V (dominios)

Empezamos por donde el pago es más obvio. Tras esta tanda, releer los cierres en secuencia para confirmar que los ángulos no se solapan.

### Task 1: Cap. 17 · Taxi — operación de flota

**Files:**
- Modify: `libro/manuscrito2/17-taxi.html` (dentro de `<div class="contenido">`, tras la sección del viaje individual)

**Ángulo:** operación de flota / ranking (viajes por zona y hora; ranking de choferes). Distinto de todos los demás.

- [ ] **Step 1: Leer el capítulo y ubicar el cierre del caso del viaje individual**

Run: `grep -n 'count\|nav-cap\|<h2' libro/manuscrito2/17-taxi.html`
Localizar el último `<h2>` de modelado y el `</div>` que cierra `contenido`.

- [ ] **Step 2: Insertar el cierre "a escala"**

Texto borrador (ajustar nombres al viaje real del capítulo):

```html
<p>Hasta aquí seguimos un viaje: una solicitud, una asignación, un cobro. Pero quien
  opera la flota no vive en un viaje, vive en diez mil. Y la pregunta que paga el sueldo
  no es «¿dónde está este taxi?», sino «¿qué zona se queda sin autos a las siete de la
  tarde?» o «¿quién rechaza más carreras de las que acepta?». Esas no son consultas
  nuevas: son las mismas situaciones de viaje, agrupadas por zona, por hora, por chofer.</p>
```

Y, si el capítulo ya usa bloques de código, una sola consulta:

```html
<div class="bloque-codigo">
  <div class="barra"><span class="lenguaje">python</span><button class="copiar">⧉ copiar</button></div>
  <pre><code data-lang="python"># Viajes hacia una zona en la franja de la tarde — un corte; el tablero cruza todas las zonas
count(u, Pattern(fixed={"zona_destino": u.ind("zona_sur")},
                 type_constraint=u.ind("viaje")))</code></pre>
</div>
```

- [ ] **Step 3: Verificar restricciones + ángulo único**

Releer: 2–5 frases de prosa, una sola consulta, sin caja, sin auto-elogio, raya justificada, tuteo neutro. Ángulo "flota/ranking" no usado aún.

- [ ] **Step 4: Commit**

```bash
git add libro/manuscrito2/17-taxi.html
git commit -m "docs(libro): cap.17 cierre a escala — operación de flota"
```

### Task 2: Cap. 18 · Clínica — cohorte epidemiológica

**Files:**
- Modify: `libro/manuscrito2/18-clinica.html` (el caso central es el paciente **Vega**, cardiología; ver línea ~59)

**Ángulo:** cohorte epidemiológica (todos los pacientes con un diagnóstico; ocupación). Distinto de "flota".

- [ ] **Step 1: Leer y ubicar el fin del modelado de la consulta de Vega**

Run: `grep -n '<h2\|Vega\|nav-cap' libro/manuscrito2/18-clinica.html`

- [ ] **Step 2: Insertar el cierre**

Borrador:

```html
<p>Modelamos la consulta de Vega: un diagnóstico, una prescripción, un control futuro.
  Pero lo que mantiene despierto a un director médico no es Vega. Es cuántos pacientes
  ingresaron con dengue en junio, qué diagnóstico encabezó el trimestre, cuántas camas
  sigue ocupando hoy la cardiología. Ninguna de esas preguntas pide una tabla nueva: el
  diagnóstico de Vega es una situación más, y contar situaciones de un tipo es contar a
  todos los Vega a la vez.</p>
```

Consulta (una sola):

```html
<div class="bloque-codigo">
  <div class="barra"><span class="lenguaje">python</span><button class="copiar">⧉ copiar</button></div>
  <pre><code data-lang="python"># Cohorte: pacientes con diagnóstico de dengue
count(u, Pattern(fixed={"condicion": u.ind("dengue")},
                 type_constraint=u.ind("diagnostico")))</code></pre>
</div>
```

- [ ] **Step 3: Verificar restricciones + ángulo único** (cohorte epidemiológica, no usado).

- [ ] **Step 4: Commit**

```bash
git add libro/manuscrito2/18-clinica.html
git commit -m "docs(libro): cap.18 cierre a escala — cohorte epidemiológica"
```

### Task 3: Cap. 19 · Banco — cartera y reporte regulatorio

**Files:**
- Modify: `libro/manuscrito2/19-banco.html` (casos: transferencia Mariana→Bruno; préstamo de Mariana)

**Ángulo:** cartera / consolidado regulatorio (créditos por estado, mora agregada). Distinto de cohorte.

- [ ] **Step 1: Leer y ubicar el fin del modelado del préstamo/transferencia**

Run: `grep -n '<h2\|Mariana\|préstamo\|nav-cap' libro/manuscrito2/19-banco.html`

- [ ] **Step 2: Insertar el cierre**

Borrador:

```html
<p>Una transferencia de Mariana a Bruno, un préstamo, un fraude: casos que se entienden
  de a uno. El regulador, en cambio, nunca pregunta por Mariana. Pregunta por la cartera
  entera: cuánto saldo vivo hay por estado de mora, qué porcentaje de los créditos lleva
  más de noventa días vencido, cómo evolucionó ese número mes a mes. Cada préstamo ya
  guarda su estado y sus fechas de vigencia; el reporte regulatorio es agrupar esos
  estados y sumar saldos sobre toda la cartera.</p>
```

Consulta (una sola, usando suma/agrupación por estado):

```html
<div class="bloque-codigo">
  <div class="barra"><span class="lenguaje">python</span><button class="copiar">⧉ copiar</button></div>
  <pre><code data-lang="python"># Saldo vivo de los créditos con mora > 90 días — un corte de la cartera
suma(u, "saldo", Pattern(fixed={"estado_mora": u.ind("vencido_90")},
                         type_constraint=u.ind("credito")))</code></pre>
</div>
```

- [ ] **Step 3: Verificar restricciones + ángulo único** (cartera/regulatorio).

- [ ] **Step 4: Commit**

```bash
git add libro/manuscrito2/19-banco.html
git commit -m "docs(libro): cap.19 cierre a escala — cartera y reporte regulatorio"
```

### Task 4: Cap. 20 · ERP — consolidado que cruza módulos

**Files:**
- Modify: `libro/manuscrito2/20-erp.html` (caso: una venta que cruza inventario/contabilidad/compras)

**Ángulo:** consolidado cruzando módulos (ventas por línea, inventario por almacén). Distinto de cartera.

- [ ] **Step 1: Leer y ubicar el fin del modelado de la venta multi-módulo**

Run: `grep -n '<h2\|nav-cap' libro/manuscrito2/20-erp.html`

- [ ] **Step 2: Insertar el cierre**

Borrador:

```html
<p>Seguimos una venta que tocó inventario, contabilidad y compras. La gerencia no mira
  una venta: mira el cierre de mes. Ventas por línea de producto, margen por sucursal,
  existencias por almacén, cuentas por pagar que vencen la semana próxima. Lo notable es
  que ninguno de esos reportes vive en un módulo: son cortes distintos del mismo grafo de
  situaciones, agrupados por la dimensión que cada gerente necesita.</p>
```

Consulta (una sola):

```html
<div class="bloque-codigo">
  <div class="barra"><span class="lenguaje">python</span><button class="copiar">⧉ copiar</button></div>
  <pre><code data-lang="python"># Ventas de una línea de producto — un corte; el cierre de mes recorre todas
suma(u, "total", Pattern(fixed={"linea_producto": u.ind("calzado")},
                         type_constraint=u.ind("venta")))</code></pre>
</div>
```

- [ ] **Step 3: Verificar restricciones + ángulo único** (consolidado cross-módulo).

- [ ] **Step 4: Commit**

```bash
git add libro/manuscrito2/20-erp.html
git commit -m "docs(libro): cap.20 cierre a escala — consolidado entre módulos"
```

### Task 5: Cap. 21 · Universidad — estadística académica

**Files:**
- Modify: `libro/manuscrito2/21-universidad.html` (caso: prerrequisitos como grafo, plan de estudios)

**Ángulo:** estadística académica (alumnos por carrera, tasa de aprobación). Distinto de consolidado financiero.

- [ ] **Step 1: Leer y ubicar el fin del modelado del plan/prerrequisitos**

Run: `grep -n '<h2\|nav-cap' libro/manuscrito2/21-universidad.html`

- [ ] **Step 2: Insertar el cierre**

Borrador:

```html
<p>Modelar el plan de estudios de un alumno y sus prerrequisitos es resolver un caso.
  El rectorado vive en el agregado: cuántos estudiantes hay por carrera, qué materia
  tiene la tasa de reprobación más alta, cuántos egresan a tiempo. La inscripción de cada
  alumno ya es una situación con su carrera y su periodo; la estadística del semestre es
  agruparlas y contarlas.</p>
```

Consulta (una sola):

```html
<div class="bloque-codigo">
  <div class="barra"><span class="lenguaje">python</span><button class="copiar">⧉ copiar</button></div>
  <pre><code data-lang="python"># Estudiantes activos de una carrera — un corte; el tablero recorre todas
count(u, Pattern(fixed={"carrera": u.ind("ingenieria"), "estado": u.ind("activa")},
                 type_constraint=u.ind("matricula")))</code></pre>
</div>
```

- [ ] **Step 3: Verificar restricciones + ángulo único** (estadística académica).

- [ ] **Step 4: Commit**

```bash
git add libro/manuscrito2/21-universidad.html
git commit -m "docs(libro): cap.21 cierre a escala — estadística académica"
```

### Task 6: Cap. 22 · Municipalidad — tiempo de resolución (SLA)

**Files:**
- Modify: `libro/manuscrito2/22-municipalidad.html` (trámites, expedientes)

**Ángulo:** serie temporal / SLA (tiempo medio de resolución por tipo de trámite). **No** usar "trámites por zona/tipo": el cap. 8 ya pivota eso. Distinto de los anteriores.

- [ ] **Step 1: Leer y ubicar el fin del modelado del expediente/trámite**

Run: `grep -n '<h2\|nav-cap' libro/manuscrito2/22-municipalidad.html`

- [ ] **Step 2: Insertar el cierre**

Borrador:

```html
<p>Seguimos un trámite de punta a punta. Al alcalde, sin embargo, no le preguntan por un
  expediente: le preguntan por la demora. Cuántos días, en promedio, tarda una licencia de
  funcionamiento; qué oficina es el cuello de botella; si el «una sola vez» de verdad
  recortó los tiempos este año. Cada trámite registró sus fechas de inicio y de cierre;
  el indicador de gestión es promediar esa diferencia, trámite por trámite, agrupando por
  tipo.</p>
```

Consulta (una sola, promedio sobre la duración):

```html
<div class="bloque-codigo">
  <div class="barra"><span class="lenguaje">python</span><button class="copiar">⧉ copiar</button></div>
  <pre><code data-lang="python"># Días promedio de resolución de un tipo de trámite — el SLA se calcula por tipo
promedio(u, "dias_resolucion", Pattern(fixed={"estado": u.ind("cerrado")},
                                       type_constraint=u.ind("tramite_licencia_funcionamiento")))</code></pre>
</div>
```

- [ ] **Step 3: Verificar restricciones + ángulo único** (SLA temporal; confirmar que NO repite el pivote del cap. 8).

- [ ] **Step 4: Commit**

```bash
git add libro/manuscrito2/22-municipalidad.html
git commit -m "docs(libro): cap.22 cierre a escala — tiempos de resolución (SLA)"
```

### Task 7: Cap. 23 · Minera — confiabilidad de activos

**Files:**
- Modify: `libro/manuscrito2/23-minera.html` (cadenas causales, sensores, mantenimiento, punchlists)

**Ángulo:** confiabilidad (fallas por equipo, disponibilidad, punchlists abiertas por sistema). Distinto de SLA.

- [ ] **Step 1: Leer y ubicar el fin del modelado de la cadena causal/mantenimiento**

Run: `grep -n '<h2\|nav-cap\|causado_por' libro/manuscrito2/23-minera.html`

- [ ] **Step 2: Insertar el cierre**

Borrador:

```html
<p>Reconstruimos una cadena causal: un sensor, una falla, una parada. Mantenimiento no
  planifica sobre una falla, planifica sobre el historial: qué equipo acumula más horas
  fuera de servicio, cuántas órdenes siguen abiertas por sistema, qué causa raíz se repite
  trimestre a trimestre. Cada falla quedó registrada con su equipo y su causa; el reporte
  de confiabilidad es contar esas fallas agrupadas por equipo.</p>
```

Consulta (una sola):

```html
<div class="bloque-codigo">
  <div class="barra"><span class="lenguaje">python</span><button class="copiar">⧉ copiar</button></div>
  <pre><code data-lang="python"># Fallas registradas en un equipo — un corte; el plan recorre todos los equipos
count(u, Pattern(fixed={"equipo": u.ind("chancadora_01")},
                 type_constraint=u.ind("falla")))</code></pre>
</div>
```

- [ ] **Step 3: Verificar restricciones + ángulo único** (confiabilidad de activos).

- [ ] **Step 4: Commit**

```bash
git add libro/manuscrito2/23-minera.html
git commit -m "docs(libro): cap.23 cierre a escala — confiabilidad de activos"
```

### Task 8: Cap. 24 · Yaku — consolidados reales del negocio

**Files:**
- Modify: `libro/manuscrito2/24-yaku.html` (sistema real: sauna/hostal/gimnasio/cafetín)

**Ángulo:** consolidados de negocio multi-servicio (ventas por servicio; comparar líneas). Distinto de confiabilidad.

- [ ] **Step 1: Leer y ubicar el fin del relato de migración**

Run: `grep -n '<h2\|nav-cap\|sauna\|hostal' libro/manuscrito2/24-yaku.html`

- [ ] **Step 2: Insertar el cierre**

Borrador (usar los servicios reales que mencione el capítulo):

```html
<p>Migrar yaku al modelo de preguntas no fue el objetivo final: fue la condición para
  poder preguntar. Y lo que el dueño quiere preguntar no es por una venta del sauna, sino
  por el negocio entero: cuánto factura cada servicio —sauna, hostal, gimnasio, cafetín—,
  cuál crece y cuál se estanca, qué día de la semana rinde más. Antes esas respuestas
  vivían repartidas en tablas que no se hablaban; ahora son un mismo grafo de ventas
  agrupado por servicio.</p>
```

Consulta (una sola):

```html
<div class="bloque-codigo">
  <div class="barra"><span class="lenguaje">python</span><button class="copiar">⧉ copiar</button></div>
  <pre><code data-lang="python"># Facturación de un servicio — un corte; el consolidado compara los cuatro
suma(u, "total", Pattern(fixed={"servicio": u.ind("sauna")},
                         type_constraint=u.ind("venta")))</code></pre>
</div>
```

- [ ] **Step 3: Verificar restricciones + ángulo único** (consolidado multi-servicio).

- [ ] **Step 4: Commit**

```bash
git add libro/manuscrito2/24-yaku.html
git commit -m "docs(libro): cap.24 cierre a escala — consolidados del negocio real"
```

### Task 9: Cap. 16 · Spa — Ajuste (ya agrega; coser la idea)

**Files:**
- Modify: `libro/manuscrito2/16-spa.html` (ya usa `suma()`/`count()` para impuestos del mes, líneas ~520–700)

**Ángulo:** no añadir agregación nueva; nombrar explícitamente que ese `suma()` de impuestos es el primer ejemplo de un patrón recurrente en el libro (el cierre "a escala"). Una o dos frases.

- [ ] **Step 1: Leer el bloque de suma de impuestos existente**

Run: `grep -n 'suma\|count\|impuesto\|<h2' libro/manuscrito2/16-spa.html`

- [ ] **Step 2: Insertar una frase puente (sin código nuevo) junto al `suma()` existente**

Borrador:

```html
<p>Conviene detenerse aquí, porque esta suma es la primera aparición de algo que volverá
  en cada dominio que sigue. No preguntamos por una venta: preguntamos por todas las del
  mes a la vez. Modelar bien la venta de una camiseta fue, sin proponérnoslo, dejar listo
  el reporte de impuestos de todo el negocio.</p>
```

- [ ] **Step 3: Verificar** que no se duplica código y que la frase enlaza con el patrón. Ángulo: meta-conexión (no consume un ángulo del catálogo).

- [ ] **Step 4: Commit**

```bash
git add libro/manuscrito2/16-spa.html
git commit -m "docs(libro): cap.16 conecta la suma de impuestos con el patrón a escala"
```

### Task 10: Cap. 25 · Cuatro dominios — ranking por dominio (Ligero)

**Files:**
- Modify: `libro/manuscrito2/25-cuatro-dominios.html` (música, química, fútbol, contratos)

**Ángulo:** ranking (goleadores; contratos por estado). Nivel Ligero: 1–2 frases, sin código.

- [ ] **Step 1: Leer y ubicar el cierre del capítulo**

Run: `grep -n '<h2\|nav-cap\|gol\|contrato' libro/manuscrito2/25-cuatro-dominios.html`

- [ ] **Step 2: Insertar el cierre (sin código)**

Borrador:

```html
<p>Y como cada gol, cada compuesto y cada cláusula son situaciones del mismo tipo, la
  pregunta interesante deja de ser «¿quién marcó este gol?» para volverse «¿quién encabeza
  la tabla de goleadores?» o «¿cuántos contratos siguen sin firmar?». El ranking no es una
  función aparte: es ordenar lo que ya contamos.</p>
```

- [ ] **Step 3: Verificar** (Ligero, sin código; ángulo ranking, distinto del de taxi que era flota).

- [ ] **Step 4: Commit**

```bash
git add libro/manuscrito2/25-cuatro-dominios.html
git commit -m "docs(libro): cap.25 cierre a escala — ranking por dominio"
```

- [ ] **Step 5 (fin de tranche): releer los 10 cierres en secuencia**

Run: `for f in 16-spa 17-taxi 18-clinica 19-banco 20-erp 21-universidad 22-municipalidad 23-minera 24-yaku 25-cuatro-dominios; do echo "== $f =="; done`
Leer cada inserción y confirmar: ningún ángulo repetido, ninguna frase de entrada repetida.

---

## Tranche 2 · Núcleo y Ajuste de teoría

### Task 11: Cap. 03 · Clase (K) — cohorte por plantilla

**Files:**
- Modify: `libro/manuscrito2/03-clase.html`

**Ángulo:** cohorte por categoría/plantilla (todas las instancias de un modelo). Distinto de los de Parte V.

- [ ] **Step 1: Leer y ubicar el fin de la sección plantilla/instancia**

Run: `grep -n '<h2\|nav-cap\|plantilla\|instancia' libro/manuscrito2/03-clase.html`

- [ ] **Step 2: Insertar el cierre**

Borrador:

```html
<p>Que la plantilla viva separada de sus instancias no es solo orden conceptual: es lo que
  hace barata una pregunta que en otros modelos es cara. Si «camiseta modelo 17» es una
  categoría en K, entonces «todas las unidades de ese modelo» ya está dicho —son las
  instancias que cuelgan de esa plantilla—. Preguntar por una unidad o por las diez mil
  cuesta lo mismo.</p>
```

Consulta (una sola):

```html
<div class="bloque-codigo">
  <div class="barra"><span class="lenguaje">python</span><button class="copiar">⧉ copiar</button></div>
  <pre><code data-lang="python"># Cuántas unidades instancian la misma plantilla de K
count(u, Pattern(type_constraint=u.ind("camiseta_modelo_17")))</code></pre>
</div>
```

- [ ] **Step 3: Verificar** (ángulo cohorte-por-plantilla).

- [ ] **Step 4: Commit**

```bash
git add libro/manuscrito2/03-clase.html
git commit -m "docs(libro): cap.03 cierre a escala — cohorte por plantilla"
```

### Task 12: Cap. 04 · Cuánto (N) — suma y promedio nativos

**Files:**
- Modify: `libro/manuscrito2/04-cuanto.html`

**Ángulo:** suma/promedio como operación nativa del eje N. Distinto de cohorte.

- [ ] **Step 1: Leer y ubicar el fin de la sección de magnitudes**

Run: `grep -n '<h2\|nav-cap\|descuento\|impuesto' libro/manuscrito2/04-cuanto.html`

- [ ] **Step 2: Insertar el cierre**

Borrador:

```html
<p>Una magnitud aislada —49.90 dólares, 18% de impuesto— dice poco. El eje cuantitativo
  cobra sentido cuando se acumula: el total facturado del día, el descuento promedio de la
  campaña, el ticket medio por cliente. Como cada importe es un valor tipado sobre una
  situación, sumarlos o promediarlos sobre miles de situaciones es la operación más natural
  del eje, no un añadido.</p>
```

Consulta (una sola):

```html
<div class="bloque-codigo">
  <div class="barra"><span class="lenguaje">python</span><button class="copiar">⧉ copiar</button></div>
  <pre><code data-lang="python"># Total facturado — suma sobre todas las ventas
suma(u, "total", Pattern(type_constraint=u.ind("venta")))</code></pre>
</div>
```

- [ ] **Step 3: Verificar** (ángulo suma/promedio).

- [ ] **Step 4: Commit**

```bash
git add libro/manuscrito2/04-cuanto.html
git commit -m "docs(libro): cap.04 cierre a escala — suma y promedio nativos"
```

### Task 13: Cap. 07 · Hecho atómico — la columna consultable

**Files:**
- Modify: `libro/manuscrito2/07-hecho-atomico.html`

**Ángulo:** apilar tripletas sobre el mismo cable = una columna consultable (la semilla del reporte). Distinto de suma.

- [ ] **Step 1: Leer y ubicar el fin de la explicación de la tripleta**

Run: `grep -n '<h2\|nav-cap\|tripleta' libro/manuscrito2/07-hecho-atomico.html`

- [ ] **Step 2: Insertar el cierre**

Borrador:

```html
<p>Hay un efecto secundario en apilar tripletas que conviene ver desde ya. Cuando mil
  sujetos distintos comparten el mismo cable —digamos <code>diagnostico</code>—, ese cable
  deja de ser un dato suelto y se vuelve, de hecho, una columna que se puede recorrer
  entera. Cada hecho atómico que escribes sobre un sujeto es, a la vez, una fila en el
  reporte de todos los sujetos que comparten ese cable. Lo que parece guardar un dato
  individual está construyendo, sin avisar, la base de la consulta colectiva.</p>
```

(Nivel Núcleo, pero aquí la consulta sería prematura —las APIs llegan después—. Permitido cerrar sin código si el capítulo aún no introdujo `query`; el ángulo se sostiene en prosa.)

- [ ] **Step 3: Verificar** (ángulo columna-consultable; sin código si las APIs no aparecen aún).

- [ ] **Step 4: Commit**

```bash
git add libro/manuscrito2/07-hecho-atomico.html
git commit -m "docs(libro): cap.07 cierre a escala — la columna consultable"
```

### Task 14: Cap. 09 · Situaciones — todas las situaciones de un tipo

**Files:**
- Modify: `libro/manuscrito2/09-situaciones.html`

**Ángulo:** contar todas las situaciones reificadas de un tipo. Distinto de columna.

- [ ] **Step 1: Leer y ubicar el fin de la sección de reificación**

Run: `grep -n '<h2\|nav-cap\|reific' libro/manuscrito2/09-situaciones.html`

- [ ] **Step 2: Insertar el cierre**

Borrador:

```html
<p>Reificar una situación tiene un dividendo que se cobra más tarde. En el momento parece
  que solo le damos identidad a un evento —esta venta, esta consulta— para colgarle
  atributos. Pero al hacerlo creamos, sin querer, un conjunto: «todas las ventas», «todas
  las consultas de junio». Una situación con identidad es una situación que se puede contar
  junto a sus pares.</p>
```

Consulta (una sola):

```html
<div class="bloque-codigo">
  <div class="barra"><span class="lenguaje">python</span><button class="copiar">⧉ copiar</button></div>
  <pre><code data-lang="python"># Cuántas consultas se reificaron — un tipo de situación, contado entero
count(u, Pattern(type_constraint=u.ind("consulta")))</code></pre>
</div>
```

- [ ] **Step 3: Verificar** (ángulo todas-las-situaciones-de-un-tipo).

- [ ] **Step 4: Commit**

```bash
git add libro/manuscrito2/09-situaciones.html
git commit -m "docs(libro): cap.09 cierre a escala — todas las situaciones de un tipo"
```

### Task 15: Cap. 10 · Por qué — agrupar por causa (causa raíz)

**Files:**
- Modify: `libro/manuscrito2/10-por-que.html`

**Ángulo:** agrupar por causa (análisis de causa raíz). Distinto de los anteriores.

- [ ] **Step 1: Leer y ubicar el fin de la sección de los cuatro cables**

Run: `grep -n '<h2\|nav-cap\|causado_por\|motivado_por' libro/manuscrito2/10-por-que.html`

- [ ] **Step 2: Insertar el cierre**

Borrador:

```html
<p>Separar el porqué en cuatro cables paga su precio cuando dejas de mirar un caso y
  miras el patrón. Si cada parada de planta cuelga de un <code>causado_por</code>, entonces
  «¿qué causa repite más?» es agrupar las situaciones por el otro extremo de ese cable. El
  análisis de causa raíz —que en otros sistemas es un proyecto— aquí es contar, agrupando
  por causa.</p>
```

Consulta (una sola):

```html
<div class="bloque-codigo">
  <div class="barra"><span class="lenguaje">python</span><button class="copiar">⧉ copiar</button></div>
  <pre><code data-lang="python"># Paradas atribuidas a una causa concreta — la causa raíz se compara entre causas
count(u, Pattern(fixed={"causado_por": u.ind("falla_electrica")},
                 type_constraint=u.ind("parada")))</code></pre>
</div>
```

- [ ] **Step 3: Verificar** (ángulo agrupar-por-causa).

- [ ] **Step 4: Commit**

```bash
git add libro/manuscrito2/10-por-que.html
git commit -m "docs(libro): cap.10 cierre a escala — agrupar por causa"
```

### Task 16: Cap. 08 · Espacio multidimensional — Ajuste (ya pivota; nombrar el patrón)

**Files:**
- Modify: `libro/manuscrito2/08-espacio-multidimensional.html` (vista pivote/conteos, líneas ~405–547)

**Ángulo:** no añadir agregación nueva; nombrar este capítulo como el "hogar" del mecanismo de reporte al que el resto del libro remite. Una o dos frases junto a la pivote.

- [ ] **Step 1: Leer la sección de la vista pivote**

Run: `grep -n 'pivote\|GROUP BY\|conteo\|<h2' libro/manuscrito2/08-espacio-multidimensional.html`

- [ ] **Step 2: Insertar una frase puente junto a la pivote (sin código nuevo)**

Borrador:

```html
<p>Vale la pena nombrar lo que acaba de pasar, porque reaparecerá en cada dominio del
  libro. Pivotar es tomar muchas situaciones y agruparlas por dos coordenadas a la vez.
  Cada vez que más adelante un hospital pregunte por sus diagnósticos o un banco por su
  cartera, estará haciendo esto mismo: el caso individual era la entrada; el reporte sobre
  muchos es la salida natural del espacio.</p>
```

- [ ] **Step 3: Verificar** (Ajuste; no duplica la pivote; enlaza hacia adelante).

- [ ] **Step 4: Commit**

```bash
git add libro/manuscrito2/08-espacio-multidimensional.html
git commit -m "docs(libro): cap.08 nombra la pivote como el patrón de reporte recurrente"
```

- [ ] **Step 5 (fin de tranche): releer los cierres de teoría en secuencia** y confirmar ángulos no repetidos contra la Tranche 1.

---

## Tranche 3 · Ligeros (1–2 frases, sin código)

Una tarea por capítulo. En todos: insertar 1–2 frases en el punto natural, verificar restricciones y ángulo único, commit. Mensaje de commit: `docs(libro): cap.NN cierre a escala — <ángulo>`.

### Task 17: Cap. 00 · Introducción — sembrar (la sala, no el paciente)

**Files:** Modify `libro/manuscrito2/00-introduccion.html`

- [ ] **Step 1:** Localizar el cierre de la escena de urgencias. Run: `grep -n '<h2\|nav-cap' libro/manuscrito2/00-introduccion.html`
- [ ] **Step 2:** Insertar:

```html
<p>Y conviene decirlo desde el principio: lo que está en juego no es ordenar los datos de
  un paciente, sino poder preguntar por la sala entera sin rearmar nada. Esa diferencia
  —de uno a todos— es la que recorre el libro.</p>
```
- [ ] **Step 3:** Verificar (Ligero, ángulo "sembrar de uno a todos").
- [ ] **Step 4:** Commit `docs(libro): cap.00 siembra el salto de uno a todos`.

### Task 18: Cap. 02 · Cuatro pilares — rebanar muchas situaciones

**Files:** Modify `libro/manuscrito2/02-cuatro-pilares.html`

- [ ] **Step 1:** Localizar el cierre de la presentación de Q/O/L/T. Run: `grep -n '<h2\|nav-cap' libro/manuscrito2/02-cuatro-pilares.html`
- [ ] **Step 2:** Insertar:

```html
<p>Cada pregunta es, además, un eje por el que cortar el conjunto. Fijar el «cuándo» y
  dejar libre el «quién» ya es pedir «todos los que actuaron ese día». Las cuatro preguntas
  no describen una situación: rebanan miles a la vez.</p>
```
- [ ] **Step 3:** Verificar (ángulo "ejes como cortes", distinto).
- [ ] **Step 4:** Commit `docs(libro): cap.02 cierre a escala — los ejes rebanan el conjunto`.

### Task 19: Cap. 05 · Predicados (M) — recorrer un cable sobre todos

**Files:** Modify `libro/manuscrito2/05-predicados.html`

- [ ] **Step 1:** Localizar el fin de la sección de cardinalidad. Run: `grep -n '<h2\|nav-cap\|cardinalidad' libro/manuscrito2/05-predicados.html`
- [ ] **Step 2:** Insertar:

```html
<p>Un cable conecta dos cosas, sí; pero el mismo cable, repetido sobre miles de sujetos, es
  una relación recorrible de punta a punta. «¿Quién trabaja para esta empresa?» no se
  responde mirando a una persona: se responde recorriendo el cable <code>empleador</code>
  hacia atrás desde todos los que lo tienen.</p>
```
- [ ] **Step 3:** Verificar (ángulo "recorrer un cable sobre todos").
- [ ] **Step 4:** Commit `docs(libro): cap.05 cierre a escala — recorrer un cable sobre todos`.

### Task 20: Cap. 11 · Identidad — consolidar una identidad entre sistemas

**Files:** Modify `libro/manuscrito2/11-identidad.html`

- [ ] **Step 1:** Localizar el fin de la sección de reconciliación. Run: `grep -n '<h2\|nav-cap\|reconcil' libro/manuscrito2/11-identidad.html`
- [ ] **Step 2:** Insertar:

```html
<p>Resolver que el Juan de la tienda y el de la clínica son el mismo no sirve solo para
  ese Juan. Hecho a escala, es lo que permite el padrón único: cruzar los registros de
  todos los Juanes repartidos entre sistemas y contarlos una sola vez, sin duplicados.</p>
```
- [ ] **Step 3:** Verificar (ángulo "consolidar identidad entre sistemas").
- [ ] **Step 4:** Commit `docs(libro): cap.11 cierre a escala — padrón único entre sistemas`.

### Task 21: Cap. 13 · Verbo — agrupar por signatura

**Files:** Modify `libro/manuscrito2/13-verbo.html`

- [ ] **Step 1:** Localizar el fin de la sección de signatura. Run: `grep -n '<h2\|nav-cap\|signatura' libro/manuscrito2/13-verbo.html`
- [ ] **Step 2:** Insertar:

```html
<p>Si cada verbo activa un tipo de situación con sus roles, entonces el verbo es también la
  llave de un agregado: «todas las situaciones que activó <em>vender</em>» es,
  literalmente, todas las ventas. Elegir bien el verbo no solo escribe el hecho; define de
  antemano el conjunto sobre el que algún día se reportará.</p>
```
- [ ] **Step 3:** Verificar (ángulo "agrupar por signatura de verbo").
- [ ] **Step 4:** Commit `docs(libro): cap.13 cierre a escala — agrupar por signatura`.

### Task 22: Cap. 14 · Lexicon — reporte en el idioma del usuario

**Files:** Modify `libro/manuscrito2/14-lexicon.html`

- [ ] **Step 1:** Localizar el fin de la sección del traductor. Run: `grep -n '<h2\|nav-cap' libro/manuscrito2/14-lexicon.html`
- [ ] **Step 2:** Insertar:

```html
<p>El lexicon no traduce solo al escribir: también al preguntar. El gerente pide «el total
  por vendedor» en sus palabras, y el diccionario lo resuelve contra el catálogo sin que él
  vea jamás una etiqueta canónica. El reporte sobre miles de registros se pide en el idioma
  del negocio, no en el del modelo.</p>
```
- [ ] **Step 3:** Verificar (ángulo "reporte en idioma del usuario").
- [ ] **Step 4:** Commit `docs(libro): cap.14 cierre a escala — reportes en el idioma del usuario`.

### Task 23: Cap. 29 · Seguridad — privacidad de agregados

**Files:** Modify `libro/manuscrito2/29-seguridad.html`

- [ ] **Step 1:** Localizar un punto sobre acceso/consulta. Run: `grep -n '<h2\|nav-cap\|acceso\|privacidad' libro/manuscrito2/29-seguridad.html`
- [ ] **Step 2:** Insertar:

```html
<p>La pluralidad tiene su propio filo en seguridad. A veces queremos el agregado —cuántos
  pacientes con cierta condición— sin permitir llegar a ninguno en particular. Que el
  reporte sume sobre muchos no debe ser una puerta trasera para reidentificar a uno: el
  control de acceso tiene que distinguir entre contar y ver.</p>
```
- [ ] **Step 3:** Verificar (ángulo "privacidad de agregados").
- [ ] **Step 4:** Commit `docs(libro): cap.29 cierre a escala — privacidad de agregados`.

### Task 24: Cap. 31 · Conclusión — eco temático

**Files:** Modify `libro/manuscrito2/31-conclusion.html`

- [ ] **Step 1:** Localizar el cierre del capítulo (antes del `nav-cap`). Run: `grep -n '<h2\|nav-cap' libro/manuscrito2/31-conclusion.html`
- [ ] **Step 2:** Insertar (eco, sin reintroducir mecanismo):

```html
<p>Quizá esa sea la promesa más discreta del modelo. Cada vez que alguien se sentó a
  describir bien un caso —una venta, una consulta, una falla— estaba, sin saberlo, dejando
  listo el reporte de todos. Modelar a uno con cuidado terminó siendo la forma de poder
  preguntar por todos.</p>
```
- [ ] **Step 3:** Verificar (eco temático; no repite mecanismo ni código).
- [ ] **Step 4:** Commit `docs(libro): cap.31 eco de cierre — de uno a todos`.

- [ ] **Step 5 (fin de tranche): releer los 8 Ligeros** y confirmar que ninguno repite frase de entrada ni ángulo de las tranches anteriores.

---

## Tranche 4 · Verificación final

### Task 25: Revisión visual y de redundancia global

**Files:** ninguno (solo lectura)

- [ ] **Step 1:** Abrir en el navegador dos capítulos representativos (uno de teoría, p. ej. `09-situaciones.html`; uno de dominio, p. ej. `19-banco.html`) y confirmar que el cierre se ve integrado, sin caja, con el código bien formateado.

Run: `open libro/manuscrito2/09-situaciones.html libro/manuscrito2/19-banco.html`

- [ ] **Step 2:** Leer en secuencia todas las frases de entrada de los cierres y verificar variedad (ninguna arranca igual). Confirmar el reparto de ángulos del catálogo: ningún ángulo en dos capítulos.

- [ ] **Step 3:** Confirmar contra el spec que los 8 capítulos "Omitir" siguen sin cierre (01, 06, 12, 15, 26, 27, 28, 30).

Run: `for f in 01-torre-de-babel 06-raices 12-puentes 15-bajo-presion 26-llms 27-aplicaciones 28-prueba-reflexiva 30-que-falta; do echo "== $f =="; grep -c 'a escala\|sin una tabla\|de uno a todos' libro/manuscrito2/$f.html; done`
Expected: 0 en todos (o coincidencias preexistentes no relacionadas, a revisar).

- [ ] **Step 4:** Resumen al autor de capítulos tocados y propuesta de merge / PR (vía finishing-a-development-branch). El PDF se regenera por separado solo si el autor lo pide.

---

## Self-review (hecho)

- **Cobertura del spec:** las 23 entradas del mapa (Núcleo/Ligero/Ajuste) tienen tarea (Tasks 1–24). Los 8 "Omitir" se verifican en Task 25/Step 3. ✓
- **Sin placeholders:** cada tarea trae el borrador real del párrafo a insertar. Los nombres de roles/ejemplos (`rol:tipo`, IDs) son tentativos y se ajustan al leer cada capítulo (Step 1 de cada tarea lo exige); esto es intencional, no un placeholder. ✓
- **Consistencia:** API verificada contra `prototipo/wq/query.py` y el uso real del cap. 16. Firmas: `count(u, Pattern(...))`, `suma(u, "campo", Pattern(...))`, `promedio(u, "campo", Pattern(...))`, `query(u, Pattern(fixed, ask, type_constraint))`. **No hay GROUP BY**: los snippets son cortes concretos (un valor fijo + `type_constraint`), no agrupaciones; la prosa describe el reporte completo. Roles en crudo + `u.ind(...)`. Todos los snippets del plan ya siguen este idioma. ✓
- **Anti-redundancia:** cada tarea declara su ángulo; los Steps de fin de tranche releen en secuencia. ✓
