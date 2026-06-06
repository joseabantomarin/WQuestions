# Situaciones encontradas implementando el menú meta-driven + su capa web

- **Fecha:** 2026-06-05
- **Alcance:** las dos sub-iteraciones de esta sesión — (1) el motor del menú meta-driven (`prototipo/meta/`) y (2) la capa de UI web (`prototipo/meta/web/`).
- **Por qué este doc:** registrar las fricciones, decisiones y bugs reales del trabajo. Varias son material para el libro (especialmente las de modelado y la de "render ≠ review").

---

## 1. Decisiones de modelado (propias de WQuestions)

### 1.1 ¿Dónde vive el texto libre? — no hay "eje string"
El modelo de 7 ejes (Q, O, L, T, N, K, M) no tiene un eje para cadenas de texto
arbitrarias. El contenido de "Bienvenida" (`"¡Bienvenido a la demo…!"`) es texto libre.
**Decisión:** reificar el texto como un **individuo K** (`txt_bienvenida`, con el texto en
su `label`) referenciado por el rol `contenido` (O→K). Así todo sigue siendo hechos
tipados, y mañana ese `txt_*` puede tener traducciones/versiones.
*Alternativa descartada:* meter el texto en el `payload` de la acción (menos hechos,
pero el texto deja de ser individuo de primera clase).

> **Para el libro:** ejemplifica una fricción honesta del modelo — el texto libre no es
> un eje, se reifica. Encaja en la discusión de K (Cap 4) o en los pendientes (Cap 26).

### 1.2 El comportamiento como datos (Opción C) — fiel a la teoría, no por comodidad
Al diseñar "qué hace cada opción" surgieron tres caminos: (A) la acción como *string
opaco* mapeado a una función Python; (B) toda la lógica de ejecución como datos; (C) un
catálogo acotado de **verbos-primitiva tipados (K)** interpretados por un **evaluador
genérico**. Se eligió **C porque es lo que el modelo prescribe**, no por pragmatismo:
- En WQuestions una acción es un **verbo (K)** que se **reifica** en una situación (O) con
  **roles tipados** (su signatura). Por eso A sub-modela (acción = string ciego, el
  anti-patrón del 5W1H plano del Cap 2) y B sobre-modela (mete el motor de ejecución en
  los datos, cuando el libro **separa** el grafo del evaluador — Cap 6 D2, Cap 26).
- El runtime es el "evaluador externo" que el Cap 26 lista como la pieza pendiente; aquí
  apareció de forma natural como un `DISPATCH` por tipo-K.

> **Para el libro:** este es un caso de uso *reflexivo* — la propia app se modela con
> WQuestions. Refuerza la tesis de "agregar comportamiento = agregar datos".

### 1.3 Colisión de nombre de rol: `destino` ya era canónico
El diseño usaba un rol `destino` (O→O) para "a qué submenú abre". Pero el catálogo
canónico de `wq` ya define `destino` como **O→L** ("lugar de destino"), y
`Catalog.register` **lanza error ante una signatura distinta para el mismo nombre**.
**Detectado al escribir el plan** (no en runtime). Renombrado a **`submenu_destino`**.

> **Lección:** un catálogo cerrado y validado *te protege* — el choque salta temprano,
> no en producción. Es exactamente la ventaja que el libro vende del catálogo D8.

---

## 2. Arquitectura / refactor

### 2.1 Extraer un motor headless (`MenuSession`) del loop
El `runtime` original **era dueño del loop**: leía input, despachaba e imprimía, todo
junto. Una UI web necesita manejar la interacción **evento por evento**, no en un bucle
bloqueante. Hubo que **separar el motor de la presentación**:
- `MenuSession` (headless) tiene el universo + el `stack` y expone `estado()` /
  `seleccionar()` / `tripletas_visibles()`.
- Los handlers pasaron de **imprimir** a **devolver un efecto** (`{tipo:"texto"...}`); la
  CLI y la web son "pieles" delgadas que traducen el efecto a print o a JSON.
Restricción cumplida: preservar la firma `runtime.run(...)` para no romper los 10 tests
existentes (mismo comportamiento observable).

> **Lección general:** mezclar "lógica de dominio" con "IO/presentación" se paga al
> agregar una segunda interfaz. Separarlas de entrada lo habría evitado.

---

## 3. Bugs encontrados (y *cómo* se encontraron)

### 3.1 CRÍTICO (motor): crash si una opción no tiene acción
`runtime.py`/`engine.py`: si una opción carecía del rol `tiene_accion`, `accion` quedaba
`None` y la línea siguiente hacía `_uno(u, None, "instancia_de")` → `facts_about(None)` →
`None.id` → **`AttributeError`**. El evaluador se anuncia como *genérico* sobre datos del
grafo (potencialmente editables), así que debe tolerar datos malformados.
**Encontrado en:** la revisión de **calidad de código** (subagente). **Fix:** una guarda
`if accion is None: ... ; continue` + un test TDD que construye esa opción degenerada.

### 3.2 VISUAL: el overlay "Sesión finalizada" siempre visible — y *quién no lo vio*
Bug de **especificidad CSS**: `#overlay { display:flex }` (selector ID, especificidad
100) le ganaba a `.oculto { display:none }` (clase, especificidad 10). Resultado: aunque
el `<div>` tenía `class="oculto"`, el overlay aparecía **al cargar la página**, tapando el
menú. **Fix:** `#overlay.oculto { display:none }` (ID+clase, especificidad 110).

Lo instructivo es **cómo se encontró**: ni la **revisión de cumplimiento del spec** ni la
**revisión de calidad de código** lo detectaron — *porque ninguna renderiza la página*. Lo
atrapó el **smoke visual con Chrome headless** (la captura). 

> **Lección (la más importante de este work):** *code review ≠ verificación visual.* Para
> UI, una captura/render headless encuentra clases enteras de bugs (layout, CSS,
> especificidad, z-index) que la lectura de código no ve. El paso de screenshot no es un
> lujo: es la única red que cubre lo visual.

---

## 4. Endurecimiento salido de la revisión de calidad (nits, todos baratos)

- **`ThreadingHTTPServer` → `HTTPServer`.** Con sesión mutable compartida había una *race
  condition teórica* entre requests concurrentes. Pasar a un solo hilo la elimina **gratis**
  (no hay IO lento que justifique hilos en un demo single-user).
- **Guarda de path-traversal con separador.** `ruta.startswith(_STATIC)` admitía un hermano
  con prefijo (`/static_secreto`); endurecida a `_STATIC + os.sep`. *Detalle:* `urllib`
  **normaliza `../` del lado cliente**, así que el test de traversal `/static/../server.py`
  llega como `/server.py` y cae en 404 igual — lo que importa es que **no** sirva el código.
- **`fetch` sin `try/catch`.** Si el servidor cae, quedaba una promesa rechazada silenciosa.
  Añadido manejo que muestra un aviso en el panel de salida.

---

## 5. Persistencia y datos

### 5.1 Asimetría save/load de columnas temporales
`storage.save()` escribe `valid_from`/`valid_to`/`tx_time`, pero `storage.load()` las
ignora y reconstruye los hechos con `assert_fact` (que regenera `tx_time`). Para el menú
(hechos atemporales) es inerte, pero el esquema guarda columnas que nunca relee.
Documentado con un comentario; restaurar bitemporalidad queda para una versión futura.

### 5.2 El menú **es** datos — y eso sorprendió en los outputs
`menu.db` **persiste entre corridas**. La opción "Acerca de" que insertamos en una demo
anterior (solo con tripletas) **seguía ahí** en una verificación posterior, mostrando 4
opciones donde el seed pone 3. El implementador lo reportó como "desviación".
**No era un bug:** es exactamente la tesis funcionando — *agregar una opción = insertar
hechos, sin tocar código, y persiste*. Para las capturas reseteamos `menu.db` (se
re-siembra limpio).

> **Para el libro:** prueba viva de "la estructura vive en la BD, no en el código".

---

## 6. Entorno / herramientas

- **No hay `pytest`** en el entorno: todos los tests son `unittest` (stdlib) y se corren
  con `PYTHONPATH=prototipo python3 -m unittest ...`.
- **No hay motor de PDF** (ni pandoc, ni LaTeX, ni Homebrew; `weasyprint` instalado pero
  roto por libs nativas). La salida visual (PDF del libro y verificación de la web) se
  resolvió con **Google Chrome headless** (`--print-to-pdf`, `--screenshot`). Chrome
  resultó ser **la herramienta clave** para todo lo visual sin display interactivo.
- **El servidor es local** (`127.0.0.1`): no se puede teclear "en vivo" desde aquí, así que
  toda la verificación interactiva fue por inputs guionados (CLI) y por capturas (web).

---

## 7. Proceso (subagent-driven development)

- **Tareas acopladas vs. un subagente por tarea.** El plan tenía tareas que compartían
  archivos (`test_meta.py`, `test_web.py`) y dependían en orden. El propio árbol de
  decisión de la skill dice que las tareas *fuertemente acopladas* no encajan en
  "un subagente por tarea". Se resolvió con **un implementador** para todo el plan + las
  dos revisiones (spec → calidad) al final.
- **`SendMessage` no disponible** en este toolset: no se pudo *continuar* el mismo
  subagente para los fixes; se despacharon **subagentes frescos** con instrucciones
  precisas (funciona igual para fixes chicos y bien especificados).
- **El self-review del plan atrapó un commit en rojo:** la Task 3 iba a commitear un test
  (`test_index_html_se_sirve`) que fallaba porque el HTML se creaba en la Task 4. Se movió
  el test a la Task 4 para que **cada commit quede verde**.
- **Las dos capas de revisión son complementarias, no redundantes.** La de spec confirmó
  "construiste lo pedido, ni más ni menos"; la de calidad atrapó el crash crítico; y la
  **verificación visual** (fuera de ambas revisiones) atrapó el bug de CSS. Cada red cubre
  algo distinto.

---

## Resumen de bugs reales (cuántos y de qué tipo)

| # | Severidad | Dónde | Lo encontró |
|---|---|---|---|
| Crash si opción sin `tiene_accion` | Crítico | motor | revisión de calidad |
| Overlay siempre visible (especificidad CSS) | Visual/funcional | front | **smoke con Chrome** |
| Race teórica (ThreadingHTTPServer) | Menor | servidor | revisión de calidad |
| Guarda de traversal sin separador | Menor (hardening) | servidor | revisión de calidad |
| `fetch` sin manejo de error | Menor | front | revisión de calidad |
| Colisión de rol `destino` | — (evitado) | catálogo | self-review del plan |

Ningún bug llegó a `main` sin test que lo fije (los críticos/visuales tienen test o
verificación de captura asociada).
