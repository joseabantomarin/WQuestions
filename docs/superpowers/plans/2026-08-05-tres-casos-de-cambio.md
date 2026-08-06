# Los tres casos de cambio — Plan de implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Añadir al manuscrito la distinción entre los tres motivos por los que un identificador deja de ser el que vale (el mundo cambió · lo anotamos mal · son la misma cosa), como sección nueva en el capítulo 11 y como eco atribuido a su propia presión en el capítulo 29.

**Architecture:** Dos inserciones de HTML en archivos existentes de `libro/manuscrito2/`, más la regeneración de los dos PDF versionados. No hay código: el entregable es prosa marcada con los componentes del canon. Este plan contiene el texto final; la ejecución es insertar, verificar y commitear.

**Tech Stack:** HTML estático + `assets/estilo.css` (componentes `rejilla-3`/`tarjeta`, `caja--alerta`, `cita-destacada`, `nota-margen`) · Python 3 + Chrome headless para `libro/generar_pdf_html.py`.

## Global Constraints

Del spec [`2026-08-05-tres-casos-de-cambio-design.md`](../specs/2026-08-05-tres-casos-de-cambio-design.md) y de `libro/manuscrito2/GUIA-DE-ESTILO.md`:

- **Tuteo neutro** (`tú tienes`, `puedes`, `quieres`). Prohibido el voseo argentino.
- **Ninguna `Dn` nueva.** D6 (vigencia) se **referencia**, nunca se enuncia: se define en el capítulo 9. No abrir ninguna `caja--decision` en este trabajo.
- **Identificadores canónicos del repertorio**, exactos: `persona_maria_g`, `cliente_1042`, `paciente_maria_g`, `contribuyente_77_3389`. María Gonzales, mujer de 42 años.
- **Sin nombres de API** en el capítulo 11: nada de `valid_from`, `valid_to`, `correct(...)`, `at=`, `history=`, `identidades`, `fixed=`. El capítulo es conceptual y hoy no menciona ninguna interfaz.
- **Ejemplos solo de María.** Nada de precios, ventas ni camisetas: son de otros capítulos.
- **Tono:** no auto-declarar honestidad (mostrar el hallazgo, no anunciarlo como acto de transparencia). Registro medio: llano pero con voz. La raya (—) solo para ritmo o énfasis; paréntesis para lo secundario, dos puntos para introducir.
- **No tocar** `indice.html`, `index.html`, `mcp-server/` ni los tests. El índice lateral lo construye `assets/interacciones.js` por scrollspy.

---

## File Structure

| Archivo | Responsabilidad en este trabajo |
|---|---|
| `libro/manuscrito2/11-identidad.html` | Núcleo conceptual: la sección nueva con los tres casos, la rejilla y la caja de alerta. Se inserta entre dos secciones existentes. |
| `libro/manuscrito2/29-prueba-reflexiva.html` | Eco: sección corta que atribuye el hallazgo a la segunda presión y lo empareja con la corrección de `instancia_de`. |
| `libro/manuscrito2/WQuestions.pdf` · `WQuestions-resumen.pdf` | Artefactos versionados; se regeneran de una sola corrida al final. |

---

## Task 1: Sección nueva en el capítulo 11

**Files:**
- Modify: `libro/manuscrito2/11-identidad.html` — insertar entre la línea 366 (cierre `</aside>` de la nota "Dirección del cable") y la 368 (`<h2>No es una decisión numerada…`)

**Interfaces:**
- Consumes: el reparto ya establecido en el capítulo (identidad canónica `persona_maria_g` con tres alias colgando por `mismo_que`) y la tesis del papelito, que aparece como `cita-destacada` al final del archivo.
- Produces: el `<h2>` "Tres cosas que le pasan a un identificador", al que remitirá la Tarea 2 desde el capítulo 29 con `<a href="11-identidad.html">`.

- [ ] **Step 1: Confirmar el punto de inserción**

Run: `sed -n '360,372p' libro/manuscrito2/11-identidad.html`

Esperado: ver el `<aside class="nota-margen">` de "Dirección del cable" cerrando en la 366, una línea en blanco en la 367, y `<h2>No es una decisión numerada: es una convención de fondo</h2>` en la 368. Si los números no coinciden (el archivo cambió), localizar los mismos dos anclajes por texto y usar esos.

- [ ] **Step 2: Insertar la sección**

Insertar este bloque completo en la línea 367, entre el `</aside>` y el `<h2>` siguiente:

```html
        <h2>Tres cosas que le pasan a un identificador</h2>

        <p>Con el patrón sobre la mesa, la reacción natural es preguntarse por qué tanto rodeo. Si
          <code>cliente_1042</code>, <code>paciente_maria_g</code> y
          <code>contribuyente_77_3389</code> son la misma señora, ¿por qué no corregir los tres a
          <code>persona_maria_g</code> y terminar el asunto? Porque corregir es una de tres
          operaciones distintas, y aquí es la equivocada. Conviene separarlas, porque desde fuera se
          parecen mucho y el sistema no va a avisarte.</p>

        <p><strong>María se mudó.</strong> Su dirección era la avenida Grau 220 y ahora es el jirón
          Camaná 415. Nada estuvo mal anotado: lo que cambió fue el mundo. El valor viejo fue verdad
          durante un tiempo y hay que poder seguir consultándolo, porque el envío que llegó a Grau el
          año pasado llegó a la dirección correcta. Esto es la vigencia: el hecho lleva su rango de
          inicio y fin, y preguntar por una fecha devuelve lo que valía en esa fecha.</p>

        <aside class="nota-margen">
          <span class="etq">Referencia</span>
          La vigencia (reificar con rango de inicio y fin las propiedades que cambian) es la decisión
          <span class="codigo-d" style="font-family:var(--mono);font-weight:700;background:var(--eje-o);color:#fff;border-radius:4px;padding:.05rem .4rem;font-size:.8rem">D6</span>,
          enunciada en el <a href="09-situaciones.html">capítulo&nbsp;9</a>. Aquí solo la contrastamos
          con sus dos vecinas.
        </aside>

        <p><strong>A María le tecleamos mal el apellido.</strong> En la ficha de la clínica figura
          «Gonzalez» y siempre fue «Gonzales». Aquí no cambió nada afuera: cambió lo que nosotros
          habíamos escrito. El valor viejo no fue verdad en ningún momento, ni un solo minuto, y por
          eso no debe seguir respondiendo consultas. Esto es una corrección, y su diferencia con el
          caso anterior no es de grado sino de naturaleza. Una vigencia certifica que algo fue cierto
          durante un periodo; aplicarla a un tecleo deja escrito en el grafo que María se apellidó
          «Gonzalez» entre marzo y julio, una afirmación falsa que nadie hizo nunca.</p>

        <p><strong><code>contribuyente_77_3389</code> resulta ser María.</strong> Este es el caso del
          capítulo. No hay nada que corregir, porque nada está mal: la municipalidad la registró bajo
          ese identificador y bajo ese identificador ocurrieron sus arbitrios. Tampoco cambió el
          mundo. Lo único que pasó es que ahora sabemos algo que antes no sabíamos, que ese papelito
          y los otros dos llevan a la misma persona. Y eso se escribe con <code>mismo_que</code>, sin
          tocar ninguno de los hechos que ya estaban.</p>

        <div class="rejilla-3 revelar">
          <div class="tarjeta">
            <h4>El mundo cambió</h4>
            <p style="margin:0 0 .5rem;font-size:.93rem"><em>María se mudó de Grau a Camaná.</em></p>
            <p style="margin:0;font-size:.93rem"><strong>¿El valor viejo fue verdad?</strong> Sí,
              hasta la fecha del cambio.<br>
              <strong>¿Qué se escribe?</strong> El hecho con su vigencia.<br>
              <strong>¿Y si preguntas luego por el valor viejo?</strong> Lo encuentras, fechado.</p>
          </div>
          <div class="tarjeta">
            <h4>Lo anotamos mal</h4>
            <p style="margin:0 0 .5rem;font-size:.93rem"><em>Escribimos «Gonzalez» por
              «Gonzales».</em></p>
            <p style="margin:0;font-size:.93rem"><strong>¿El valor viejo fue verdad?</strong> No, en
              ningún momento.<br>
              <strong>¿Qué se escribe?</strong> Una corrección.<br>
              <strong>¿Y si preguntas luego por el valor viejo?</strong> Ya no responde, pero queda
              el rastro de que se corrigió.</p>
          </div>
          <div class="tarjeta">
            <h4>Son la misma cosa</h4>
            <p style="margin:0 0 .5rem;font-size:.93rem"><em><code>contribuyente_77_3389</code> es
              María.</em></p>
            <p style="margin:0;font-size:.93rem"><strong>¿El valor viejo fue verdad?</strong> Los dos
              lo son.<br>
              <strong>¿Qué se escribe?</strong> Una tripleta <code>mismo_que</code>.<br>
              <strong>¿Y si preguntas luego por el valor viejo?</strong> Lo encuentras por
              cualquiera de los dos, y suman juntos.</p>
          </div>
        </div>

        <p>Vistos así, los tres casos no se distinguen por lo que ocurrió afuera. Se distinguen por
          <strong>sobre qué se está afirmando algo</strong>. La vigencia afirma sobre el mundo: esto
          fue así y luego dejó de serlo. La corrección afirma sobre la anotación: lo que escribimos no
          correspondía. <code>mismo_que</code> afirma sobre el referente: estos dos papelitos llevan
          al mismo sitio. Tres objetos distintos (el mundo, el registro y la cosa designada) que este
          capítulo ya había separado cuando distinguió el papelito de lo que encuentras al mirar.</p>

        <div class="caja caja--alerta revelar">
          <p class="caja-tit">El error que no se anuncia</p>
          <p style="margin:0 0 .6rem">Elegir mal entre las tres no rompe nada. El grafo acepta las
            tres operaciones sin protestar, porque las tres son tripletas bien formadas: lo que las
            distingue no está en los datos, está en la intención de quien anota. El almacén no puede
            saberlo.</p>
          <p style="margin:0">Corregir lo que era una identidad compartida borra una verdad. Los
            arbitrios ocurrieron bajo <code>contribuyente_77_3389</code>, y si ese identificador
            desaparece, la pregunta hecha con el rótulo que la municipalidad usó de verdad deja de
            encontrarlos: una suma que debía juntar tres sistemas junta dos. Corregir lo que era un
            cambio del mundo borra el pasado y deja sin explicación todo lo que se decidió con el
            valor viejo. Y fechar un tecleo asciende un error a hecho histórico. Ninguno de los tres
            fallos levanta una excepción; los tres devuelven un número.</p>
        </div>

        <p>Nada de esto añade maquinaria. La vigencia venía del capítulo&nbsp;9, corregir es asentar
          un hecho nuevo y <code>mismo_que</code> es el cable que llevamos toda la sección tendiendo.
          Lo que hay que añadir no es un mecanismo sino una decisión, y hay que tomarla antes de
          escribir: cuál de las tres cosas ha pasado.</p>
```

- [ ] **Step 3: Verificar que el HTML sigue balanceado**

Run:
```bash
python3 - <<'PY'
from html.parser import HTMLParser
import sys
VOID = {'br','img','hr','meta','link','input','source','col','area','base','embed','param','track','wbr'}
class P(HTMLParser):
    def __init__(self): super().__init__(); self.stack=[]; self.bad=[]
    def handle_starttag(self,t,a):
        if t not in VOID: self.stack.append((t,self.getpos()))
    def handle_endtag(self,t):
        if not self.stack or self.stack[-1][0]!=t:
            self.bad.append((t,self.getpos(),self.stack[-1] if self.stack else None))
        else: self.stack.pop()
p=P(); p.feed(open('libro/manuscrito2/11-identidad.html',encoding='utf-8').read())
print("desbalanceados:",p.bad)
print("sin cerrar:",[s[0] for s in p.stack])
sys.exit(1 if (p.bad or p.stack) else 0)
PY
```

Esperado: `desbalanceados: []` · `sin cerrar: []` y código de salida 0.

- [ ] **Step 4: Verificar las restricciones globales sobre lo insertado**

Run:
```bash
grep -nE 'podés|tenés|querés|valid_from|valid_to|history=|identidades\(|fixed=|caja--decision' libro/manuscrito2/11-identidad.html
```

Esperado: **sin salida** (código 1). Cualquier coincidencia es una violación de las restricciones globales y hay que corregirla antes de commitear.

- [ ] **Step 5: Verificar que la sección aparece y que los enlaces resuelven**

Run:
```bash
grep -c 'Tres cosas que le pasan a un identificador' libro/manuscrito2/11-identidad.html
grep -o 'href="09-situaciones.html"' libro/manuscrito2/11-identidad.html | head -1
ls libro/manuscrito2/09-situaciones.html
```

Esperado: `1` · el `href` encontrado · el archivo existe.

- [ ] **Step 6: Commit**

```bash
git add libro/manuscrito2/11-identidad.html
git commit -m "$(cat <<'EOF'
feat(libro): el cap 11 distingue los tres casos de cambio

El capítulo explicaba mismo_que en aislamiento, nunca frente a los otros
dos motivos por los que un identificador deja de valer. El lector podía
terminarlo entero y seguir eligiendo la operación equivocada, porque
nunca se le enseñó que hay una elección que hacer.

La sección nueva los contrasta sobre María: se mudó (el mundo cambió),
le tecleamos mal el apellido (lo anotamos mal), contribuyente_77_3389
resulta ser ella (son la misma cosa). El filo es que no se distinguen
por lo ocurrido afuera sino por sobre qué se afirma: el mundo, la
anotación o el referente.

Con eso, el consejo de "no renumeres los ids" del final del capítulo
deja de ser una recomendación suelta y pasa a leerse como corolario.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 2: Eco en el capítulo 29

**Files:**
- Modify: `libro/manuscrito2/29-prueba-reflexiva.html` — insertar entre la línea 479 (cierre `</div>` de la `caja--alerta` "La frontera que no cerramos") y la 481 (`<h2>Honradez intelectual</h2>`)

**Interfaces:**
- Consumes: el `<h2>` creado en la Tarea 1, al que enlaza con `<a href="11-identidad.html">`.
- Produces: nada que otras tareas usen.

- [ ] **Step 1: Confirmar el punto de inserción**

Run: `sed -n '472,483p' libro/manuscrito2/29-prueba-reflexiva.html`

Esperado: la `caja--alerta` con `<p class="caja-tit">La frontera que no cerramos</p>` cerrando en la 479, línea en blanco en la 480, y `<h2>Honradez intelectual</h2>` en la 481. **No tocar** el `<h2>Las fricciones nuevas: dos cerradas, una abierta</h2>` de la línea 408 ni su conteo.

- [ ] **Step 2: Insertar la sección**

Insertar este bloque completo en la línea 480, entre el `</div>` y el `<h2>Honradez intelectual</h2>`:

```html
        <h2>La interfaz, por detrás de su propia teoría</h2>

        <p>El experimento reflexivo no fue la última presión. Vino después otra, de otra clase: en vez
          de describirse a sí mismo, el modelo tuvo que dejarse operar. Un modelo de lenguaje, hablando
          con el grafo a través de su interfaz, cargó y consultó los datos de un sistema real en
          producción, el mismo <a href="24-yaku.html">yaku del capítulo&nbsp;24</a>, sin un humano en
          medio que tradujera sus intenciones.</p>

        <p>La frontera apareció temprano. Un cliente estaba registrado dos veces, bajo dos
          identificadores distintos, y había que dejar constancia de que era uno solo. La interfaz
          ofrecía dos puertas: corregir un dato mal anotado, o fechar un dato que había cambiado.
          Ninguna servía, porque no había error ni cambio, sino dos nombres para una misma cosa.
          Obligado a elegir entre las dos que existían, el modelo eligió corregir. Nada falló. La
          consulta siguiente devolvió una cifra menor que la real, con la misma cara de confianza que
          si hubiera sido correcta.</p>

        <p>Vale la pena ver en qué se parece y en qué no a la corrección de <code>instancia_de</code>.
          Allí el prototipo estaba detrás de su propia teoría: el libro ya clasificaba sujetos de
          cualquier eje y el código no lo permitía. Aquí la teoría estaba completa desde mucho antes.
          <code>mismo_que</code> lleva escrito desde el <a href="11-identidad.html">capítulo&nbsp;11</a>,
          con sus tres vías de resolución y su precedente en <code>owl:sameAs</code>. Lo que estaba
          detrás era la interfaz, que sabía nombrar dos de los tres casos y callaba el tercero. Un
          modelo no puede elegir una opción que su interfaz no sabe decir.</p>

        <p>La distinción entre los tres casos (el mundo cambió, lo anotamos mal, son la misma cosa)
          vive ahora en el <a href="11-identidad.html">capítulo&nbsp;11</a>, que es su sitio. Lo que
          esta segunda presión aporta es la medida de lo que cuesta dejarla implícita.</p>

        <p class="cita-destacada revelar">Una interfaz que ofrece dos puertas donde el mundo tiene
          tres no produce un error: produce una respuesta.<cite>Sobre la segunda presión</cite></p>
```

- [ ] **Step 3: Verificar que el HTML sigue balanceado**

Run: el mismo script de la Tarea 1, Step 3, cambiando el archivo:

```bash
python3 - <<'PY'
from html.parser import HTMLParser
import sys
VOID = {'br','img','hr','meta','link','input','source','col','area','base','embed','param','track','wbr'}
class P(HTMLParser):
    def __init__(self): super().__init__(); self.stack=[]; self.bad=[]
    def handle_starttag(self,t,a):
        if t not in VOID: self.stack.append((t,self.getpos()))
    def handle_endtag(self,t):
        if not self.stack or self.stack[-1][0]!=t:
            self.bad.append((t,self.getpos(),self.stack[-1] if self.stack else None))
        else: self.stack.pop()
p=P(); p.feed(open('libro/manuscrito2/29-prueba-reflexiva.html',encoding='utf-8').read())
print("desbalanceados:",p.bad)
print("sin cerrar:",[s[0] for s in p.stack])
sys.exit(1 if (p.bad or p.stack) else 0)
PY
```

Esperado: `desbalanceados: []` · `sin cerrar: []` y código de salida 0.

- [ ] **Step 4: Verificar que el conteo de fricciones quedó intacto y los enlaces resuelven**

Run:
```bash
grep -c 'dos cerradas, una abierta' libro/manuscrito2/29-prueba-reflexiva.html
grep -c 'La interfaz, por detrás de su propia teoría' libro/manuscrito2/29-prueba-reflexiva.html
grep -oE 'href="(11-identidad|24-yaku).html"' libro/manuscrito2/29-prueba-reflexiva.html | sort -u
grep -nE 'podés|tenés|querés' libro/manuscrito2/29-prueba-reflexiva.html
```

Esperado: `1` (el encabezado original sigue diciendo "dos cerradas") · `1` (la sección nueva existe) · los dos `href` listados · sin salida del último grep.

- [ ] **Step 5: Commit**

```bash
git add libro/manuscrito2/29-prueba-reflexiva.html
git commit -m "$(cat <<'EOF'
feat(libro): el cap 29 registra la segunda presión sobre el modelo

Una sección aparte, no un cuarto ítem de "dos cerradas, una abierta":
esas tres salieron del prototipo reflexivo y esta salió de otra cosa,
un LLM operando el grafo por su interfaz sobre los datos de yaku.
Mezclarlas habría falseado la procedencia y, como testigo
independiente, prueba más separada que dentro.

El paralelo con instancia_de es el pago: allí el prototipo estaba
detrás de su propia teoría; aquí la teoría estaba completa desde el
capítulo 11 y quien estaba detrás era la interfaz, que sabía nombrar
dos de los tres casos y callaba el tercero.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: Repaso de tono y regeneración de los PDF

**Files:**
- Read: `libro/manuscrito2/11-identidad.html`, `libro/manuscrito2/29-prueba-reflexiva.html`
- Modify (generados): `libro/manuscrito2/WQuestions.pdf`, `libro/manuscrito2/WQuestions-resumen.pdf`

**Interfaces:**
- Consumes: las dos secciones de las Tareas 1 y 2, ya commiteadas.
- Produces: nada.

- [ ] **Step 1: Repaso de las rayas**

Run:
```bash
grep -n '—' libro/manuscrito2/11-identidad.html libro/manuscrito2/29-prueba-reflexiva.html
```

Revisar cada coincidencia **de las secciones nuevas** (las preexistentes no se tocan) y clasificarla por función: si introduce una idea, cambiar a dos puntos; si es material secundario, cambiar a paréntesis; dejar la raya solo donde marca ritmo o énfasis. El texto de este plan ya viene revisado, así que lo esperable es que las secciones nuevas no aporten ninguna raya; si aparece una, es que se coló en la inserción.

- [ ] **Step 2: Repaso de tono**

Releer las dos secciones nuevas buscando frases que **anuncien** honestidad en vez de mostrar el hallazgo ("hay que reconocer que", "seamos honestos", "conviene admitir"). No debería haber ninguna. Si aparece, reescribir la frase para que el hecho hable solo.

- [ ] **Step 3: Regenerar los dos PDF**

Run: `python3 libro/generar_pdf_html.py`

Esperado: termina sin error y reescribe `libro/manuscrito2/WQuestions.pdf` y `libro/manuscrito2/WQuestions-resumen.pdf`. Requiere Chrome headless disponible. **Si el generador falla por falta de Chrome o de la portada, no lo fuerces:** detente, reporta el error exacto y deja los PDF sin tocar. Las dos tareas anteriores ya están commiteadas y el HTML es la fuente canónica.

- [ ] **Step 4: Verificar que las secciones nuevas entraron al PDF**

Run:
```bash
git status --short libro/manuscrito2/*.pdf
python3 -c "
import subprocess
out = subprocess.run(['git','diff','--stat','--','libro/manuscrito2/WQuestions.pdf'],capture_output=True,text=True).stdout
print(out or 'sin cambios en el PDF')
"
```

Esperado: los dos PDF aparecen modificados. Si aparecen sin cambios, la corrida no tomó el HTML nuevo y hay que investigar antes de commitear.

- [ ] **Step 5: Commit**

```bash
git add libro/manuscrito2/WQuestions.pdf libro/manuscrito2/WQuestions-resumen.pdf
git commit -m "$(cat <<'EOF'
chore(libro): regenera los PDF con las dos secciones nuevas

Las dos ediciones salen de la misma corrida para que no se
desincronicen.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Self-review de este plan

**Cobertura del spec.** Cambio 1 (cap 11: apertura, tres casos sobre María, `rejilla-3`, giro conceptual, `caja--alerta`, enganche a D6 y cierre hacia "No es una decisión numerada") → Tarea 1. Cambio 2 (cap 29: sección aparte tras "Las fricciones nuevas", con el paralelo de `instancia_de` y la remisión al cap 11) → Tarea 2. Verificación (HTML balanceado, generador de PDF, repaso de tono y de rayas) → Steps 3-5 de las Tareas 1 y 2, más la Tarea 3.

**Placeholders.** Ninguno: el texto final de las dos secciones va literal en los Steps 2 de las Tareas 1 y 2.

**Consistencia.** Los identificadores (`persona_maria_g`, `cliente_1042`, `paciente_maria_g`, `contribuyente_77_3389`) coinciden entre el texto insertado, el capítulo existente y el repertorio de la guía. Los títulos de sección usados en los enlaces y en los `grep` de verificación coinciden carácter a carácter con los insertados.

**Riesgo conocido.** Los números de línea son del estado en `ad90102`. Cada tarea empieza confirmándolos y da el anclaje por texto como alternativa.
