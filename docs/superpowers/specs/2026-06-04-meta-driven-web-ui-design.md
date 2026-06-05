# Diseño — Capa de UI web sobre el menú meta-driven (WQuestions)

- **Fecha:** 2026-06-04
- **Estado:** aprobado (diseño), pendiente plan de implementación
- **Ubicación del código:** `prototipo/meta/` (motor) + `prototipo/meta/web/` (capa web)
- **Spec base:** `docs/superpowers/specs/2026-06-04-meta-driven-menu-design.md`

## 1. Propósito

Añadir una **capa de presentación visible** sobre el menú meta-driven existente: una
UI web (HTML/JS) donde el usuario navega el menú con clics, ve los textos de las
acciones, y —como gancho que refuerza la tesis— ve en vivo las **tripletas WQuestions**
que respaldan lo que está en pantalla. El motor Python sigue siendo la autoridad
(lee SQLite, valida signaturas, despacha por tipo-K); el HTML/JS es un cliente delgado.

## 2. Decisiones tomadas

| # | Decisión | Justificación |
|---|---|---|
| Medio | **UI web (HTML/JS)** | Elección del usuario; lo más "visible" para mostrar/capturar (libro). |
| Conexión | **Servidor Python local + API JSON; motor autoritativo** | Un solo evaluador (el del libro) reusado server-side; el JS es piel delgada. Cuando las acciones tengan efectos reales, solo cambia el motor. |
| Alcance v1 | **Navegación visible + panel inspector de tripletas** | Consumir el menú (no editar). El inspector hace visible que la UI sale de datos. |
| Refactor | **Extraer un motor headless `MenuSession`** del loop de `runtime` | La web maneja la interacción evento-por-evento; la lógica de navegación debe vivir una sola vez y servir a CLI y web. |
| Stack | **`http.server` + HTML/JS sin frameworks** | Cero dependencias nuevas (stdlib); Chrome ya disponible para render/captura. |
| Salir (web) | Efecto `salir` → overlay "Sesión finalizada" + botón **Reiniciar** | Cerrar la pestaña desde JS no es confiable. |

## 3. Arquitectura

Refactor chico: el corazón pasa de "loop que imprime" a un **motor headless por pasos**
con dos pieles delgadas.

1. **`MenuSession` (motor headless, `engine.py`)** — tiene el `universe` + el `stack`
   de navegación; expone una API por pasos; los handlers **devuelven un efecto** (no
   imprimen) y mutan el stack. Toda la lógica de navegación vive aquí, una sola vez.
2. **Driver CLI (`runtime.run`, refactorizado)** — crea una `MenuSession`, en el loop
   pinta con `estado()`, lee, llama `seleccionar()` y traduce el efecto a `print`.
   Mantiene la firma actual → los 10 tests existentes siguen verdes.
3. **Driver web (`web/server.py`)** — `http.server`; llama la misma API de `MenuSession`
   y serializa a JSON; sirve los estáticos.
4. **Frontend (`web/static/`)** — `index.html` + `app.js` + `style.css`: dos paneles
   (menú navegable + inspector de tripletas) y un área de salida para los textos.

```
prototipo/meta/
  engine.py          ← NUEVO: MenuSession (headless), lógica extraída de runtime
  runtime.py         ← driver CLI sobre MenuSession (python -m meta sin cambios)
  web/
    __init__.py
    server.py        ← NUEVO: http.server (API JSON + estáticos)
    __main__.py      ← NUEVO: python -m meta.web (arranca el servidor)
    static/
      index.html
      app.js
      style.css
  catalogo_app.py, storage.py, seed.py, __main__.py   (sin cambios funcionales)
  tests/test_meta.py (extendido), tests/test_web.py (NUEVO)
```

## 4. Motor `MenuSession` (`engine.py`)

```python
class MenuSession:
    def __init__(self, universe, menu_inicial="menu_principal"): ...
    def estado(self) -> dict
    def seleccionar(self, indice: int) -> dict
    def tripletas_visibles(self) -> list
```

- `estado()` → `{menu_id, titulo, es_submenu, terminada, opciones:[{indice,id,label}]}`
  (opciones ordenadas por el rol `orden`).
- `seleccionar(n)` → `{efecto, estado}`; avanza un paso y devuelve el estado nuevo.
- `tripletas_visibles()` → lista de `{sujeto, rol, valor, sujeto_label, valor_label}`:
  todos los hechos donde el menú actual, sus opciones o sus acciones son sujeto.

**Efectos** (los handlers devuelven uno y mutan el stack):

| verbo-K | efecto | mutación |
|---|---|---|
| `mostrar_texto` | `{tipo:"texto", contenido:"…"}` | — |
| `abrir_submenu` | `{tipo:"navegado"}` | `stack.append(destino)` |
| `volver` | `{tipo:"navegado"}` | `stack.pop()` (si `len(stack)>1`) |
| `salir` | `{tipo:"salir"}` | `terminada = True` |
| índice fuera de rango | `{tipo:"invalido"}` | — |
| opción sin `tiene_accion` | `{tipo:"sin_accion"}` | — |
| verbo sin handler | `{tipo:"desconocido"}` | — |

Los helpers de consulta (`_valores`, `_uno`, `_opciones`) viven en `engine.py`;
`runtime.py` los reexporta si algún test existente los referencia (preservar verde).

## 5. API HTTP (`web/server.py`)

Single-user local. El servidor mantiene **una `MenuSession` viva** (universo cargado de
`menu.db` al arrancar) y delega todo en ella.

| método | ruta | acción |
|---|---|---|
| `GET` | `/` | sirve `index.html` |
| `GET` | `/static/app.js`, `/static/style.css` | estáticos |
| `GET` | `/api/estado` | `{estado, tripletas}` |
| `POST` | `/api/seleccionar` body `{indice:n}` | `{efecto, estado, tripletas}` |
| `POST` | `/api/reiniciar` | nueva sesión → `{estado, tripletas}` |

- Solo escucha en `127.0.0.1`. Sin auth (demo local).
- Carga el universo **una vez al arrancar**, vía un helper compartido
  `abrir_universo(db_path) -> (conn, universe)` que vive en **`seed.py`** (abrir db →
  seed si vacío → load; reusa `storage` + `build_catalog`, sin ciclos de import).
  Lo usan `__main__.py` (CLI) y `web/server.py`.
- Respuestas JSON con `Content-Type: application/json`; estáticos con su mimetype.
- Errores: body malformado o `indice` no entero → HTTP 400 con `{error:"…"}`.

**Lanzar:** `PYTHONPATH=prototipo python3 -m meta.web` → `ThreadingHTTPServer` en
`http://127.0.0.1:8000`, imprime la URL e intenta `webbrowser.open` (envuelto en try).

## 6. UI (`web/static/`)

Layout en dos columnas:

```
┌─ WQuestions · menú meta-driven ───────────────────────────────┐
├───────────────────────────────┬──────────────────────────────┤
│  «título del menú»  (‹migas›)  │  Tripletas detrás (inspector) │
│   [ opción 1 ]                 │  sujeto                       │
│   [ opción 2 ]                 │    rol → valor                │
│   …                            │  …                            │
│  ┌ salida ───────────────────┐ │                              │
│  │ «texto de mostrar_texto»  │ │                              │
│  └───────────────────────────┘ │                              │
└───────────────────────────────┴──────────────────────────────┘
```

**`app.js` (delgado):**
- Al cargar: `GET /api/estado` → `render(estado)` + `renderInspector(tripletas)`.
- Click en opción → `POST /api/seleccionar {indice}` → según `efecto`:
  - `texto` → muestra `contenido` en el panel **salida**.
  - `navegado` → re-pinta menú + inspector; migas reflejan la profundidad (`es_submenu`).
  - `salir` → overlay "Sesión finalizada" + botón **Reiniciar** → `POST /api/reiniciar`.
  - `invalido` / `sin_accion` / `desconocido` → aviso discreto (defensivo).
- Sin frameworks; `fetch` + DOM API.

**`style.css`:** grid de 2 columnas, botones tipo tarjeta, inspector en fuente
monoespaciada (que "se vean los datos"), estética limpia y presentable para capturas.

**`index.html`:** esqueleto con contenedores `#menu`, `#salida`, `#inspector`, el overlay
de fin de sesión, `<link>` al css y `<script>` al js.

## 7. Testing

1. **`MenuSession` (unit, `tests/test_meta.py`)** — `estado()` con el menú esperado;
   `seleccionar()` por cada efecto (texto, navegado al abrir submenú, navegado al volver
   con pop, salir deja `terminada`, índice fuera de rango → invalido, opción sin acción →
   sin_accion); `tripletas_visibles()` incluye hechos del menú + opciones + acciones.
2. **Preservación** — los 10 tests existentes siguen verdes tras el refactor.
3. **API (integración, `tests/test_web.py`)** — servidor en puerto efímero (`port 0`,
   hilo); con `urllib`: `GET /api/estado` (forma esperada), `POST /api/seleccionar
   {indice:2}` navega al submenú, `POST /api/reiniciar` vuelve al principal.
4. **Smoke visual (verificación, no unittest)** — arrancar el servidor y usar Chrome
   headless `--screenshot` sobre `/` para confirmar render del menú + dejar una captura.

Corren con `PYTHONPATH=prototipo python3 -m unittest meta.tests.test_meta meta.tests.test_web`.

## 8. Fuera de alcance (YAGNI por ahora)

- Edición/CRUD del menú desde la UI (escribir tripletas) — iteración futura.
- Multi-usuario / múltiples sesiones concurrentes (es single-user local; una sola sesión).
- Recarga en caliente de `menu.db` (cambios en datos → reiniciar el servidor).
- Autenticación, HTTPS, despliegue remoto.
- Tests unitarios del JS (se cubre el contrato vía tests de la API + smoke con Chrome).
- Resaltar en el inspector qué tripleta corresponde a cada elemento (nice-to-have).
