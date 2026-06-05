# Capa UI web sobre el menú meta-driven — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Añadir una UI web (HTML/JS) que navega visiblemente el menú meta-driven y muestra en vivo las tripletas WQuestions detrás de la pantalla, con el motor Python autoritativo detrás de una API JSON.

**Architecture:** Se extrae un motor headless `MenuSession` (lógica de navegación, una sola vez) del loop de `runtime`. Dos pieles delgadas lo usan: el driver CLI (`runtime.run`, refactorizado, sin romper tests) y un servidor `http.server` que expone una API JSON y sirve el frontend HTML/JS. El JS solo hace `fetch` → pinta → clic.

**Tech Stack:** Python 3.9 stdlib (`http.server`, `json`, `sqlite3`, `unittest`), la librería local `wq` (`prototipo/wq/`), HTML/CSS/JS vanilla (sin frameworks). Google Chrome (ya instalado) para el smoke visual. NO hay pytest: los tests son `unittest`.

**Spec:** `docs/superpowers/specs/2026-06-04-meta-driven-web-ui-design.md`

**Entorno:** todos los comandos desde la raíz `/Users/joseabanto/WQuestions` con prefijo `PYTHONPATH=prototipo`. Se trabaja en `main`.

---

## File Structure

| Archivo | Responsabilidad |
|---|---|
| `prototipo/meta/engine.py` | NUEVO. `MenuSession` (motor headless) + helpers de consulta. |
| `prototipo/meta/runtime.py` | MODIFICAR. Driver CLI fino sobre `MenuSession` (preserva `run()`). |
| `prototipo/meta/seed.py` | MODIFICAR. Añade `abrir_universo(db_path)`. |
| `prototipo/meta/__main__.py` | MODIFICAR. Usa `abrir_universo`. |
| `prototipo/meta/web/__init__.py` | NUEVO. Marca el paquete. |
| `prototipo/meta/web/server.py` | NUEVO. `http.server`: API JSON + estáticos. |
| `prototipo/meta/web/__main__.py` | NUEVO. `python -m meta.web` arranca el servidor. |
| `prototipo/meta/web/static/index.html` | NUEVO. Esqueleto de la UI. |
| `prototipo/meta/web/static/app.js` | NUEVO. Cliente delgado (fetch + render). |
| `prototipo/meta/web/static/style.css` | NUEVO. Estilos. |
| `prototipo/meta/tests/test_meta.py` | MODIFICAR. Añade `TestMenuSession`, `TestAbrirUniverso`. |
| `prototipo/meta/tests/test_web.py` | NUEVO. Tests de integración de la API. |

---

## Task 1: Motor `MenuSession` (`engine.py`) + refactor del driver CLI

**Files:**
- Create: `prototipo/meta/engine.py`
- Modify: `prototipo/meta/runtime.py`
- Modify: `prototipo/meta/tests/test_meta.py`

- [ ] **Step 1: Escribir los tests del motor (fallan)**

Añadir a `prototipo/meta/tests/test_meta.py`, antes de `if __name__ == "__main__":`. (Si `seed` no está importado al tope, ya lo está por tareas previas; usa `seed.build_universe()`.)
```python
from meta.engine import MenuSession


class TestMenuSession(unittest.TestCase):
    def setUp(self):
        self.u = seed.build_universe()

    def test_estado_menu_principal(self):
        e = MenuSession(self.u).estado()
        self.assertEqual(e["titulo"], "Menú principal")
        self.assertFalse(e["es_submenu"])
        self.assertEqual([o["label"] for o in e["opciones"]],
                         ["Bienvenida", "Configuración", "Salir"])

    def test_seleccionar_texto(self):
        r = MenuSession(self.u).seleccionar(1)
        self.assertEqual(r["efecto"]["tipo"], "texto")
        self.assertIn("Bienvenido", r["efecto"]["contenido"])

    def test_seleccionar_abre_y_vuelve(self):
        s = MenuSession(self.u)
        r = s.seleccionar(2)  # Configuración
        self.assertEqual(r["efecto"]["tipo"], "navegado")
        self.assertTrue(r["estado"]["es_submenu"])
        self.assertEqual(r["estado"]["titulo"], "Configuración")
        r2 = s.seleccionar(2)  # Volver
        self.assertEqual(r2["efecto"]["tipo"], "navegado")
        self.assertFalse(r2["estado"]["es_submenu"])

    def test_seleccionar_salir(self):
        r = MenuSession(self.u).seleccionar(3)
        self.assertEqual(r["efecto"]["tipo"], "salir")
        self.assertTrue(r["estado"]["terminada"])

    def test_indice_invalido(self):
        self.assertEqual(MenuSession(self.u).seleccionar(99)["efecto"]["tipo"], "invalido")

    def test_tripletas_visibles_incluye_opciones(self):
        trips = MenuSession(self.u).tripletas_visibles()
        pares = {(t["sujeto"], t["rol"], t["valor"]) for t in trips}
        self.assertIn(("menu_principal", "tiene_opcion", "opt_bienvenida"), pares)
        self.assertIn(("opt_bienvenida", "orden", "n_1"), pares)
```

- [ ] **Step 2: Correr y verificar que fallan**

Run: `PYTHONPATH=prototipo python3 -m unittest meta.tests.test_meta.TestMenuSession -v`
Expected: FAIL con `ModuleNotFoundError: No module named 'meta.engine'`.

- [ ] **Step 3: Crear `engine.py`**

`prototipo/meta/engine.py`:
```python
"""Motor headless del menú meta-driven: MenuSession.

Toda la lógica de navegación vive aquí, una sola vez. Los handlers devuelven un
efecto (no imprimen) y mutan el stack. CLI y web son pieles delgadas sobre este motor.
"""


def _valores(u, subj, rol):
    return [f.value for f in u.facts_about(subj) if f.role == rol]


def _uno(u, subj, rol):
    vs = _valores(u, subj, rol)
    return vs[0] if vs else None


def _orden(u, opt):
    n = _uno(u, opt, "orden")
    return n.payload["value"] if n is not None and n.payload else 0


def _opciones(u, menu):
    return sorted(_valores(u, menu, "tiene_opcion"), key=lambda o: _orden(u, o))


def _h_mostrar_texto(sess, accion):
    txt = _uno(sess.u, accion, "contenido")
    return {"tipo": "texto", "contenido": txt.label if txt is not None else ""}


def _h_abrir_submenu(sess, accion):
    destino = _uno(sess.u, accion, "submenu_destino")
    if destino is not None:
        sess.stack.append(destino)
    return {"tipo": "navegado"}


def _h_volver(sess, accion):
    if len(sess.stack) > 1:
        sess.stack.pop()
    return {"tipo": "navegado"}


def _h_salir(sess, accion):
    sess.terminada = True
    return {"tipo": "salir"}


_DISPATCH = {
    "mostrar_texto": _h_mostrar_texto,
    "abrir_submenu": _h_abrir_submenu,
    "volver": _h_volver,
    "salir": _h_salir,
}


class MenuSession:
    """Una sesión de navegación: el universo + un stack de menús."""

    def __init__(self, universe, menu_inicial="menu_principal"):
        self.u = universe
        self.stack = [universe.ind(menu_inicial)]
        self.terminada = False

    def estado(self):
        menu = self.stack[-1]
        opciones = _opciones(self.u, menu)
        return {
            "menu_id": menu.id,
            "titulo": menu.label,
            "es_submenu": len(self.stack) > 1,
            "terminada": self.terminada,
            "opciones": [{"indice": i, "id": o.id, "label": o.label}
                         for i, o in enumerate(opciones, 1)],
        }

    def seleccionar(self, indice):
        if self.terminada:
            return {"efecto": {"tipo": "terminada"}, "estado": self.estado()}
        opciones = _opciones(self.u, self.stack[-1])
        if not isinstance(indice, int) or not (1 <= indice <= len(opciones)):
            return {"efecto": {"tipo": "invalido"}, "estado": self.estado()}
        opcion = opciones[indice - 1]
        accion = _uno(self.u, opcion, "tiene_accion")
        if accion is None:
            return {"efecto": {"tipo": "sin_accion"}, "estado": self.estado()}
        verbo = _uno(self.u, accion, "instancia_de")
        handler = _DISPATCH.get(verbo.id) if verbo is not None else None
        if handler is None:
            return {"efecto": {"tipo": "desconocido"}, "estado": self.estado()}
        efecto = handler(self, accion)
        return {"efecto": efecto, "estado": self.estado()}

    def tripletas_visibles(self):
        menu = self.stack[-1]
        nodos = [menu]
        for o in _opciones(self.u, menu):
            nodos.append(o)
            acc = _uno(self.u, o, "tiene_accion")
            if acc is not None:
                nodos.append(acc)
        vistos = set()
        out = []
        for n in nodos:
            if n.id in vistos:
                continue
            vistos.add(n.id)
            for f in self.u.facts_about(n):
                out.append({
                    "sujeto": f.subject.id, "rol": f.role, "valor": f.value.id,
                    "sujeto_label": f.subject.label, "valor_label": f.value.label,
                })
        return out
```

- [ ] **Step 4: Refactorizar `runtime.py` como driver fino**

Reemplazar TODO el contenido de `prototipo/meta/runtime.py` por:
```python
"""Driver CLI sobre el motor headless `MenuSession`.

Mantiene la firma `run(u, leer, escribir, menu_inicial)` para no romper los tests
existentes. La lógica de navegación vive en engine.MenuSession; aquí solo se traduce
el motor a print/input. Reexporta los helpers por compatibilidad.
"""
from .engine import MenuSession, _valores, _uno, _orden, _opciones  # noqa: F401 (reexport)


def run(u, leer=input, escribir=print, menu_inicial="menu_principal"):
    """Corre el menú en la terminal. `leer`/`escribir` son inyectables para tests."""
    sess = MenuSession(u, menu_inicial)
    while not sess.terminada:
        e = sess.estado()
        escribir(f"\n== {e['titulo']} ==")
        for o in e["opciones"]:
            escribir(f"  {o['indice']}. {o['label']}")
        entrada = str(leer("> ")).strip()
        if not entrada.isdigit():
            escribir("Opción inválida.")
            continue
        ef = sess.seleccionar(int(entrada))["efecto"]
        tipo = ef["tipo"]
        if tipo == "texto":
            escribir(ef["contenido"])
        elif tipo == "invalido":
            escribir("Opción inválida.")
        elif tipo == "sin_accion":
            escribir("(opción sin acción)")
        elif tipo == "desconocido":
            escribir("(sin handler para esa acción)")
        # navegado / salir: nada que imprimir
```

- [ ] **Step 5: Correr los tests del motor y TODA la suite de meta**

Run: `PYTHONPATH=prototipo python3 -m unittest meta.tests.test_meta -v`
Expected: PASS — 16 tests (los 10 previos + 6 de `TestMenuSession`). Los tests de navegación CLI (`TestNavegacion`, `TestOpcionSinAccion`) siguen verdes porque el comportamiento observable de `run()` no cambió.

- [ ] **Step 6: Commit**

```bash
git add prototipo/meta/engine.py prototipo/meta/runtime.py prototipo/meta/tests/test_meta.py
git commit -m "refactor(meta): extraer motor headless MenuSession; runtime queda como driver CLI

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 2: `seed.abrir_universo` + refactor de `__main__.py`

**Files:**
- Modify: `prototipo/meta/seed.py`
- Modify: `prototipo/meta/__main__.py`
- Modify: `prototipo/meta/tests/test_meta.py`

- [ ] **Step 1: Escribir el test que falla**

Añadir a `prototipo/meta/tests/test_meta.py` (antes de `if __name__ == "__main__":`):
```python
class TestAbrirUniverso(unittest.TestCase):
    def test_siembra_y_carga(self):
        import tempfile, os
        db = os.path.join(tempfile.mkdtemp(), "menu.db")
        conn, u = seed.abrir_universo(db)
        try:
            self.assertEqual(u.ind("menu_principal").label, "Menú principal")
        finally:
            conn.close()
```

- [ ] **Step 2: Correr y verificar que falla**

Run: `PYTHONPATH=prototipo python3 -m unittest meta.tests.test_meta.TestAbrirUniverso -v`
Expected: FAIL con `AttributeError: module 'meta.seed' has no attribute 'abrir_universo'`.

- [ ] **Step 3: Añadir `abrir_universo` a `seed.py`**

En `prototipo/meta/seed.py`, añadir `import sqlite3` al tope (junto a los otros imports) y al final del archivo:
```python
def abrir_universo(db_path):
    """Abre la BD SQLite; si está vacía la siembra; devuelve (conn, universe)."""
    conn = sqlite3.connect(db_path)
    storage.init_db(conn)
    vacio = conn.execute("SELECT COUNT(*) FROM hechos").fetchone()[0] == 0
    if vacio:
        seed(conn)
    u = storage.load(conn, build_catalog())
    return conn, u
```

- [ ] **Step 4: Refactorizar `__main__.py` para usarlo**

Reemplazar TODO el contenido de `prototipo/meta/__main__.py` por:
```python
"""Entry point: `PYTHONPATH=prototipo python3 -m meta` — corre el menú en la terminal."""
import os

from . import seed, runtime

DB_PATH = os.path.join(os.path.dirname(__file__), "menu.db")


def main():
    conn, u = seed.abrir_universo(DB_PATH)
    try:
        runtime.run(u)
    except (EOFError, KeyboardInterrupt):
        print("\nHasta luego.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Correr el test y un smoke de la CLI**

Run: `PYTHONPATH=prototipo python3 -m unittest meta.tests.test_meta.TestAbrirUniverso -v`
Expected: PASS.

Run: `printf '1\n3\n' | PYTHONPATH=prototipo python3 -m meta`
Expected: muestra el menú, el texto de bienvenida tras `1`, y sale tras `3`, sin errores.

- [ ] **Step 6: Commit**

```bash
git add prototipo/meta/seed.py prototipo/meta/__main__.py prototipo/meta/tests/test_meta.py
git commit -m "feat(meta): helper abrir_universo (abrir+seed+load) reusable por CLI y web

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 3: Paquete `web` — servidor y API JSON

**Files:**
- Create: `prototipo/meta/web/__init__.py`
- Create: `prototipo/meta/web/server.py`
- Create: `prototipo/meta/web/__main__.py`
- Create: `prototipo/meta/tests/test_web.py`

- [ ] **Step 1: Escribir los tests de la API (fallan)**

Crear `prototipo/meta/tests/test_web.py`:
```python
import json
import os
import tempfile
import threading
import unittest
import urllib.request

from meta.web.server import crear_servidor


class TestWebAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = os.path.join(tempfile.mkdtemp(), "menu.db")
        cls.httpd, cls.estado = crear_servidor(cls.db, "127.0.0.1", 0)
        cls.port = cls.httpd.server_address[1]
        cls.hilo = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.hilo.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()

    def _url(self, ruta):
        return f"http://127.0.0.1:{self.port}{ruta}"

    def _get(self, ruta):
        with urllib.request.urlopen(self._url(ruta)) as r:
            return json.loads(r.read())

    def _post(self, ruta, obj=None):
        data = json.dumps(obj).encode() if obj is not None else b""
        req = urllib.request.Request(self._url(ruta), data=data,
                                     headers={"Content-Type": "application/json"},
                                     method="POST")
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())

    def setUp(self):
        self._post("/api/reiniciar")  # estado limpio por test

    def test_estado_inicial(self):
        d = self._get("/api/estado")
        self.assertEqual(d["estado"]["titulo"], "Menú principal")
        self.assertEqual(len(d["estado"]["opciones"]), 3)
        self.assertTrue(any(t["rol"] == "tiene_opcion" for t in d["tripletas"]))

    def test_seleccionar_navega_submenu(self):
        d = self._post("/api/seleccionar", {"indice": 2})
        self.assertEqual(d["efecto"]["tipo"], "navegado")
        self.assertEqual(d["estado"]["titulo"], "Configuración")

    def test_reiniciar_vuelve_al_principal(self):
        self._post("/api/seleccionar", {"indice": 2})
        d = self._post("/api/reiniciar")
        self.assertEqual(d["estado"]["titulo"], "Menú principal")
        self.assertFalse(d["estado"]["es_submenu"])


if __name__ == "__main__":
    unittest.main()
```
(El test que sirve el HTML se añade en la Task 4, cuando ya existe `index.html`, para que cada commit quede verde.)

- [ ] **Step 2: Correr y verificar que fallan**

Run: `PYTHONPATH=prototipo python3 -m unittest meta.tests.test_web -v`
Expected: FAIL con `ModuleNotFoundError: No module named 'meta.web'`.

- [ ] **Step 3: Crear el paquete `web`**

`prototipo/meta/web/__init__.py`:
```python
"""Capa de UI web sobre el menú meta-driven."""
```

`prototipo/meta/web/server.py`:
```python
"""Servidor HTTP del menú meta-driven: API JSON + estáticos. Single-user, localhost."""
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from ..engine import MenuSession
from ..seed import abrir_universo

_STATIC = os.path.abspath(os.path.join(os.path.dirname(__file__), "static"))
_MIME = {
    ".html": "text/html; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
}


def crear_handler(estado):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):  # silencia el log por request
            pass

        def _enviar_json(self, obj, code=200):
            body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _payload(self):
            s = estado["sesion"]
            return {"estado": s.estado(), "tripletas": s.tripletas_visibles()}

        def _enviar_estatico(self, nombre):
            ruta = os.path.abspath(os.path.join(_STATIC, nombre))
            if not ruta.startswith(_STATIC) or not os.path.isfile(ruta):
                self.send_error(404)
                return
            with open(ruta, "rb") as f:
                body = f.read()
            ext = os.path.splitext(ruta)[1]
            self.send_response(200)
            self.send_header("Content-Type", _MIME.get(ext, "application/octet-stream"))
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if self.path in ("/", "/index.html"):
                self._enviar_estatico("index.html")
            elif self.path.startswith("/static/"):
                self._enviar_estatico(self.path[len("/static/"):])
            elif self.path == "/api/estado":
                self._enviar_json(self._payload())
            else:
                self.send_error(404)

        def do_POST(self):
            length = int(self.headers.get("Content-Length", 0) or 0)
            raw = self.rfile.read(length) if length else b""
            if self.path == "/api/seleccionar":
                try:
                    indice = int(json.loads(raw or b"{}")["indice"])
                except (KeyError, ValueError, TypeError, json.JSONDecodeError):
                    self._enviar_json({"error": "indice inválido"}, 400)
                    return
                efecto = estado["sesion"].seleccionar(indice)["efecto"]
                payload = self._payload()
                payload["efecto"] = efecto
                self._enviar_json(payload)
            elif self.path == "/api/reiniciar":
                estado["sesion"] = MenuSession(estado["universe"])
                self._enviar_json(self._payload())
            else:
                self.send_error(404)

    return Handler


def crear_servidor(db_path, host="127.0.0.1", port=8000):
    """Carga el universo (siembra si hace falta) y devuelve (httpd, estado)."""
    conn, u = abrir_universo(db_path)
    conn.close()  # el universo ya está en memoria
    estado = {"universe": u, "sesion": MenuSession(u)}
    httpd = ThreadingHTTPServer((host, port), crear_handler(estado))
    return httpd, estado
```

`prototipo/meta/web/__main__.py`:
```python
"""python -m meta.web → arranca el servidor del menú meta-driven."""
import os
import webbrowser

from .server import crear_servidor

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "menu.db")
HOST, PORT = "127.0.0.1", 8000


def main():
    httpd, _ = crear_servidor(DB_PATH, HOST, PORT)
    url = f"http://{HOST}:{PORT}/"
    print(f"Menú meta-driven en {url}  (Ctrl-C para detener)")
    try:
        webbrowser.open(url)
    except Exception:
        pass
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Correr los tests de la API**

Run: `PYTHONPATH=prototipo python3 -m unittest meta.tests.test_web -v`
Expected: PASS — 3 tests (`test_estado_inicial`, `test_seleccionar_navega_submenu`, `test_reiniciar_vuelve_al_principal`). No dependen de archivos estáticos.

- [ ] **Step 5: Commit**

```bash
git add prototipo/meta/web/__init__.py prototipo/meta/web/server.py prototipo/meta/web/__main__.py prototipo/meta/tests/test_web.py
git commit -m "feat(meta): servidor http.server con API JSON sobre MenuSession

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 4: Frontend (`web/static/`) + smoke visual

**Files:**
- Create: `prototipo/meta/web/static/index.html`
- Create: `prototipo/meta/web/static/style.css`
- Create: `prototipo/meta/web/static/app.js`

- [ ] **Step 1: Crear `index.html`**

`prototipo/meta/web/static/index.html`:
```html
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>WQuestions · menú meta-driven</title>
  <link rel="stylesheet" href="/static/style.css">
</head>
<body>
  <header><h1>WQuestions · menú meta-driven</h1></header>
  <main>
    <section id="panel-menu">
      <div id="migas"></div>
      <h2 id="titulo"></h2>
      <div id="opciones"></div>
      <div id="salida" class="oculto"></div>
    </section>
    <aside id="panel-inspector">
      <h2>Tripletas detrás (lo que ves = datos)</h2>
      <div id="inspector"></div>
    </aside>
  </main>
  <div id="overlay" class="oculto">
    <div class="overlay-card">
      <p>Sesión finalizada.</p>
      <button id="btn-reiniciar">Reiniciar</button>
    </div>
  </div>
  <script src="/static/app.js"></script>
</body>
</html>
```

- [ ] **Step 2: Crear `style.css`**

`prototipo/meta/web/static/style.css`:
```css
:root { --azul:#1e3a8a; --azul2:#1d4ed8; --gris:#6b7280; --fondo:#f8fafc; }
* { box-sizing: border-box; }
body { margin:0; font-family: system-ui, -apple-system, sans-serif; color:#1f2937; background:var(--fondo); }
header { background:var(--azul); color:#fff; padding:14px 22px; }
header h1 { margin:0; font-size:18px; font-weight:600; }
main { display:grid; grid-template-columns:1fr 1fr; gap:18px; padding:22px; max-width:1100px; margin:0 auto; }
#panel-menu, #panel-inspector { background:#fff; border:1px solid #e5e7eb; border-radius:10px; padding:18px; }
#migas { color:var(--gris); font-size:12px; min-height:16px; }
#titulo { margin:4px 0 16px; color:var(--azul); }
.opcion { display:block; width:100%; text-align:left; margin:8px 0; padding:12px 16px;
          font-size:15px; background:#eef2ff; color:var(--azul2); border:1px solid #c7d2fe;
          border-radius:8px; cursor:pointer; }
.opcion:hover { background:#e0e7ff; }
#salida { margin-top:16px; padding:14px 16px; background:#ecfdf5; border:1px solid #a7f3d0;
          border-radius:8px; color:#065f46; }
.oculto { display:none; }
#panel-inspector h2 { margin:0 0 12px; font-size:14px; color:var(--gris); font-weight:600; }
#inspector { font-family:"SF Mono", Menlo, Consolas, monospace; font-size:12px; line-height:1.5; }
.trip-sujeto { font-weight:700; color:var(--azul); margin-top:10px; }
.trip-row { color:#374151; padding-left:14px; }
#overlay { position:fixed; inset:0; background:rgba(15,23,42,.55); display:flex; align-items:center; justify-content:center; }
.overlay-card { background:#fff; padding:28px 34px; border-radius:12px; text-align:center; }
.overlay-card button { margin-top:12px; padding:10px 20px; font-size:15px; background:var(--azul2);
                       color:#fff; border:none; border-radius:8px; cursor:pointer; }
```

- [ ] **Step 3: Crear `app.js`**

`prototipo/meta/web/static/app.js`:
```javascript
const $ = (sel) => document.querySelector(sel);

async function getEstado() {
  const r = await fetch("/api/estado");
  return r.json();
}
async function seleccionar(indice) {
  const r = await fetch("/api/seleccionar", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ indice }),
  });
  return r.json();
}
async function reiniciar() {
  const r = await fetch("/api/reiniciar", { method: "POST" });
  return r.json();
}

function renderMenu(estado) {
  $("#titulo").textContent = estado.titulo;
  $("#migas").textContent = estado.es_submenu ? "‹ submenú" : "";
  const cont = $("#opciones");
  cont.innerHTML = "";
  for (const opt of estado.opciones) {
    const b = document.createElement("button");
    b.className = "opcion";
    b.textContent = opt.label;
    b.onclick = () => onSeleccion(opt.indice);
    cont.appendChild(b);
  }
}

function renderInspector(tripletas) {
  const cont = $("#inspector");
  cont.innerHTML = "";
  let sujetoActual = null;
  for (const t of tripletas) {
    if (t.sujeto !== sujetoActual) {
      sujetoActual = t.sujeto;
      const h = document.createElement("div");
      h.className = "trip-sujeto";
      h.textContent = t.sujeto_label || t.sujeto;
      cont.appendChild(h);
    }
    const row = document.createElement("div");
    row.className = "trip-row";
    row.textContent = `${t.rol} → ${t.valor_label || t.valor}`;
    cont.appendChild(row);
  }
}

function aplicar(data) {
  renderMenu(data.estado);
  renderInspector(data.tripletas);
}

async function onSeleccion(indice) {
  const data = await seleccionar(indice);
  const ef = data.efecto || {};
  if (ef.tipo === "texto") {
    const s = $("#salida");
    s.textContent = ef.contenido;
    s.classList.remove("oculto");
    aplicar(data);
  } else if (ef.tipo === "navegado") {
    $("#salida").classList.add("oculto");
    aplicar(data);
  } else if (ef.tipo === "salir") {
    $("#overlay").classList.remove("oculto");
  } else {
    aplicar(data);
  }
}

$("#btn-reiniciar").onclick = async () => {
  const data = await reiniciar();
  $("#overlay").classList.add("oculto");
  $("#salida").classList.add("oculto");
  aplicar(data);
};

(async () => aplicar(await getEstado()))();
```

- [ ] **Step 4: Añadir el test que sirve el HTML y correr la suite web**

Ahora que existe `index.html`, añadir este método a la clase `TestWebAPI` en
`prototipo/meta/tests/test_web.py` (antes de `if __name__ == "__main__":`):
```python
    def test_index_html_se_sirve(self):
        with urllib.request.urlopen(self._url("/")) as r:
            self.assertEqual(r.status, 200)
            self.assertIn(b"meta-driven", r.read())
```
Run: `PYTHONPATH=prototipo python3 -m unittest meta.tests.test_web -v`
Expected: PASS — 4 tests (los 3 de la API + `test_index_html_se_sirve`).

- [ ] **Step 5: Smoke visual con Chrome headless (verificación + captura)**

Arrancar el servidor en background, renderizar con Chrome, capturar, apagar:
```bash
PYTHONPATH=prototipo python3 -m meta.web > /tmp/meta_web.log 2>&1 &
SRV=$!
sleep 2
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless=new --disable-gpu --virtual-time-budget=4000 \
  --window-size=1200,800 --screenshot=/tmp/menu_web.png \
  http://127.0.0.1:8000/
kill $SRV
ls -l /tmp/menu_web.png
```
Expected: se crea `/tmp/menu_web.png` (>0 bytes). Abrir/inspeccionar la imagen debe mostrar el menú principal a la izquierda (Bienvenida / Configuración / … / Salir como botones) y el inspector de tripletas a la derecha.

- [ ] **Step 6: Commit**

```bash
git add prototipo/meta/web/static/ prototipo/meta/tests/test_web.py
git commit -m "feat(meta): frontend HTML/JS del menú con inspector de tripletas

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Verificación final

- [ ] **Suite completa (meta + web)**

Run: `PYTHONPATH=prototipo python3 -m unittest meta.tests.test_meta meta.tests.test_web -v`
Expected: PASS — 21 tests (17 en test_meta: 10 previos + 6 MenuSession + 1 AbrirUniverso; 4 en test_web).

- [ ] **Sin regresiones en el prototipo `wq`**

Run: `PYTHONPATH=prototipo python3 -m unittest discover -s prototipo/tests -q`
Expected: OK (21 tests).

- [ ] **CLI sigue funcionando**

Run: `printf '1\n2\n2\n3\n' | PYTHONPATH=prototipo python3 -m meta`
Expected: navega principal → bienvenida → configuración → volver → salir, sin errores.

- [ ] **Web arranca y responde**

Run:
```bash
PYTHONPATH=prototipo python3 -m meta.web > /tmp/meta_web.log 2>&1 &
SRV=$!; sleep 2
curl -s http://127.0.0.1:8000/api/estado | head -c 200
kill $SRV
```
Expected: imprime un JSON con `"titulo": "Menú principal"` y la lista de opciones.
