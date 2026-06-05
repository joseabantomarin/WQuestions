# Meta-driven Menu (WQuestions) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Construir un menú CLI meta-driven cuya estructura y comportamiento se describen como hechos WQuestions en SQLite e interpretados por un evaluador genérico.

**Architecture:** Tres capas — datos (SQLite) → almacén (`storage`, serializa/carga un `Universe` de `wq`) → evaluador (`runtime`, despacha por el tipo-K de cada acción). Reusa la librería `prototipo/wq/` (modelo de 7 ejes). Vive en `prototipo/meta/` y corre con `PYTHONPATH=prototipo`.

**Tech Stack:** Python 3.9, `sqlite3` (stdlib), `unittest` (stdlib), la librería local `wq` (en `prototipo/wq/`). No hay pytest en el entorno: los tests son `unittest`.

**Spec:** `docs/superpowers/specs/2026-06-04-meta-driven-menu-design.md`

**Nota de naming:** el rol del spec llamado `destino` se implementa como **`submenu_destino`** (O→O) para no chocar con el rol canónico `destino` de `wq` (que es O→L). El spec ya está actualizado.

---

## File Structure

| Archivo | Responsabilidad |
|---|---|
| `prototipo/meta/__init__.py` | Marca el paquete `meta`. |
| `prototipo/meta/tests/__init__.py` | Marca el paquete de tests. |
| `prototipo/meta/catalogo_app.py` | Construye un `Catalog` de `wq` con los 5 roles del app. |
| `prototipo/meta/storage.py` | Esquema SQLite + `init_db` / `save` / `load`. |
| `prototipo/meta/seed.py` | `build_universe()` (el menú como hechos) + `seed(conn)`. |
| `prototipo/meta/runtime.py` | Evaluador: helpers de consulta + `DISPATCH` + `run()`. |
| `prototipo/meta/__main__.py` | Entry point `python -m meta`. |
| `prototipo/meta/tests/test_meta.py` | Los 4 tests del spec. |
| `prototipo/wq/__init__.py` | (cleanup) docstring "8 ejes" → "7 ejes". |

Todos los comandos se corren **desde la raíz del repo** con el prefijo `PYTHONPATH=prototipo`.

---

## Task 0: Scaffold del paquete `meta`

**Files:**
- Create: `prototipo/meta/__init__.py`
- Create: `prototipo/meta/tests/__init__.py`

- [ ] **Step 1: Crear los `__init__.py` vacíos**

`prototipo/meta/__init__.py`:
```python
"""Sistema meta-driven sobre WQuestions: un menú CLI definido como hechos."""
```

`prototipo/meta/tests/__init__.py`:
```python
```

- [ ] **Step 2: Verificar que el paquete importa**

Run: `PYTHONPATH=prototipo python3 -c "import meta, meta.tests; print('ok')"`
Expected: imprime `ok` sin error.

- [ ] **Step 3: Commit**

```bash
git add prototipo/meta/__init__.py prototipo/meta/tests/__init__.py
git commit -m "feat(meta): scaffold del paquete meta"
```

---

## Task 1: `catalogo_app.py` — roles del app

**Files:**
- Create: `prototipo/meta/catalogo_app.py`
- Test: `prototipo/meta/tests/test_meta.py`

- [ ] **Step 1: Escribir el test que falla**

Crear `prototipo/meta/tests/test_meta.py` con:
```python
import sqlite3
import unittest

from wq import Individual, Axis, SignatureError
from meta.catalogo_app import build_catalog


class TestCatalogo(unittest.TestCase):
    def test_roles_del_app_registrados(self):
        cat = build_catalog()
        sig = cat.get("tiene_opcion")
        self.assertIsNotNone(sig)
        self.assertEqual(sig.domain, Axis.O)
        self.assertEqual(sig.range, Axis.O)
        self.assertFalse(sig.functional)  # múltiple

        orden = cat.get("orden")
        self.assertEqual(orden.range, Axis.N)
        self.assertTrue(orden.functional)

        # submenu_destino existe y es O->O (no choca con el canónico 'destino' O->L)
        self.assertEqual(cat.get("submenu_destino").range, Axis.O)
        self.assertEqual(cat.get("contenido").range, Axis.K)
        # el canónico 'destino' sigue intacto
        self.assertEqual(cat.get("destino").range, Axis.L)
```

- [ ] **Step 2: Correr el test y verificar que falla**

Run: `PYTHONPATH=prototipo python3 -m unittest meta.tests.test_meta.TestCatalogo -v`
Expected: FAIL con `ModuleNotFoundError: No module named 'meta.catalogo_app'`.

- [ ] **Step 3: Implementar `catalogo_app.py`**

`prototipo/meta/catalogo_app.py`:
```python
"""Catálogo del app meta-driven: los roles propios sobre el catálogo canónico de wq.

Parte del `Catalog` de wq (que ya trae `instancia_de`, etc.) y añade los 5 roles
que el menú necesita. `submenu_destino` se llama así (no `destino`) para no chocar
con el rol canónico `destino` (O→L).
"""
from wq import Catalog, RoleSignature, Axis


def build_catalog() -> Catalog:
    cat = Catalog()
    roles = [
        RoleSignature("tiene_opcion", Axis.O, Axis.O, False, "menú → opción"),
        RoleSignature("orden", Axis.O, Axis.N, True, "opción → posición"),
        RoleSignature("tiene_accion", Axis.O, Axis.O, True, "opción → acción"),
        RoleSignature("submenu_destino", Axis.O, Axis.O, True,
                      "acción abrir_submenu → menú destino"),
        RoleSignature("contenido", Axis.O, Axis.K, True,
                      "acción mostrar_texto → texto (individuo K)"),
    ]
    for sig in roles:
        cat.register(sig)
    return cat
```

- [ ] **Step 4: Correr el test y verificar que pasa**

Run: `PYTHONPATH=prototipo python3 -m unittest meta.tests.test_meta.TestCatalogo -v`
Expected: PASS (1 test).

- [ ] **Step 5: Commit**

```bash
git add prototipo/meta/catalogo_app.py prototipo/meta/tests/test_meta.py
git commit -m "feat(meta): catálogo con los 5 roles del app meta-driven"
```

---

## Task 2: `storage.py` — persistencia SQLite

**Files:**
- Create: `prototipo/meta/storage.py`
- Modify: `prototipo/meta/tests/test_meta.py`

- [ ] **Step 1: Añadir el test que falla**

Añadir a `prototipo/meta/tests/test_meta.py` (después de la clase anterior):
```python
from meta import storage


class TestStorage(unittest.TestCase):
    def _universo_minimo(self):
        from wq import Universe
        cat = build_catalog()
        u = Universe(catalog=cat)
        m = Individual(id="m1", axis=Axis.O, label="Menú")
        o = Individual(id="o1", axis=Axis.O, label="Opción 1")
        u.assert_fact(m, "tiene_opcion", o)
        return u

    def test_storage_roundtrip(self):
        u = self._universo_minimo()
        conn = sqlite3.connect(":memory:")
        storage.save(u, conn)
        u2 = storage.load(conn, build_catalog())
        self.assertEqual(len(u2.individuals), len(u.individuals))
        self.assertEqual(len(u2.facts), len(u.facts))
        valores = [f.value.id for f in u2.facts_about(u2.ind("m1"))
                   if f.role == "tiene_opcion"]
        self.assertEqual(valores, ["o1"])
        self.assertEqual(u2.ind("o1").label, "Opción 1")
```

- [ ] **Step 2: Correr el test y verificar que falla**

Run: `PYTHONPATH=prototipo python3 -m unittest meta.tests.test_meta.TestStorage -v`
Expected: FAIL con `ModuleNotFoundError: No module named 'meta.storage'`.

- [ ] **Step 3: Implementar `storage.py`**

`prototipo/meta/storage.py`:
```python
"""Persistencia SQLite de un Universe de wq (almacén; carga-en-memoria).

Dos tablas que espejan el modelo: `individuos` y `hechos`. El runtime solo usa
`load()`; promover a SQLite-consultado-directo después = reemplazar `load()`.
"""
import json
import sqlite3

from wq import Universe, Individual, Axis

_SCHEMA = """
CREATE TABLE IF NOT EXISTS individuos(
    id TEXT PRIMARY KEY,
    eje TEXT NOT NULL,
    label TEXT,
    payload TEXT
);
CREATE TABLE IF NOT EXISTS hechos(
    rowid INTEGER PRIMARY KEY AUTOINCREMENT,
    sujeto TEXT NOT NULL,
    rol TEXT NOT NULL,
    valor TEXT NOT NULL,
    valid_from TEXT,
    valid_to TEXT,
    tx_time TEXT
);
CREATE INDEX IF NOT EXISTS ix_hechos_sujeto ON hechos(sujeto);
CREATE INDEX IF NOT EXISTS ix_hechos_rol ON hechos(rol);
"""


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(_SCHEMA)
    conn.commit()


def save(universe: Universe, conn: sqlite3.Connection) -> None:
    init_db(conn)
    conn.execute("DELETE FROM hechos")
    conn.execute("DELETE FROM individuos")
    for ind in universe.individuals.values():
        conn.execute(
            "INSERT INTO individuos(id, eje, label, payload) VALUES (?, ?, ?, ?)",
            (ind.id, ind.axis.value, ind.label,
             json.dumps(ind.payload) if ind.payload is not None else None),
        )
    for f in universe.facts:
        conn.execute(
            "INSERT INTO hechos(sujeto, rol, valor, valid_from, valid_to, tx_time) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (f.subject.id, f.role, f.value.id,
             f.valid_from.isoformat() if f.valid_from else None,
             f.valid_to.isoformat() if f.valid_to else None,
             f.tx_time.isoformat() if f.tx_time else None),
        )
    conn.commit()


def load(conn: sqlite3.Connection, catalog) -> Universe:
    init_db(conn)
    u = Universe(catalog=catalog)
    inds = {}
    for id_, eje, label, payload in conn.execute(
            "SELECT id, eje, label, payload FROM individuos"):
        ind = Individual(
            id=id_, axis=Axis(eje), label=label,
            payload=json.loads(payload) if payload is not None else None,
        )
        inds[id_] = ind
        u.add_individual(ind)
    for sujeto, rol, valor in conn.execute(
            "SELECT sujeto, rol, valor FROM hechos ORDER BY rowid"):
        u.assert_fact(inds[sujeto], rol, inds[valor])
    return u
```

- [ ] **Step 4: Correr el test y verificar que pasa**

Run: `PYTHONPATH=prototipo python3 -m unittest meta.tests.test_meta.TestStorage -v`
Expected: PASS (1 test).

- [ ] **Step 5: Commit**

```bash
git add prototipo/meta/storage.py prototipo/meta/tests/test_meta.py
git commit -m "feat(meta): persistencia SQLite (save/load del Universe)"
```

---

## Task 3: `seed.py` — el menú como hechos

**Files:**
- Create: `prototipo/meta/seed.py`
- Modify: `prototipo/meta/tests/test_meta.py`

- [ ] **Step 1: Añadir el test que falla**

Añadir a `prototipo/meta/tests/test_meta.py`:
```python
from meta import seed


def _valores(u, subj_id, rol):
    s = u.ind(subj_id)
    return [f.value for f in u.facts_about(s) if f.role == rol]


def _uno(u, subj_id, rol):
    vs = _valores(u, subj_id, rol)
    return vs[0] if vs else None


def _orden(u, opt):
    n = _uno(u, opt.id, "orden")
    return n.payload["value"] if n and n.payload else 0


class TestSeed(unittest.TestCase):
    def setUp(self):
        self.u = seed.build_universe()

    def test_menu_principal_tres_opciones_ordenadas(self):
        opts = sorted(_valores(self.u, "menu_principal", "tiene_opcion"),
                      key=lambda o: _orden(self.u, o))
        self.assertEqual([o.id for o in opts],
                         ["opt_bienvenida", "opt_config", "opt_salir"])

    def test_config_abre_submenu(self):
        acc = _uno(self.u, "opt_config", "tiene_accion")
        verbo = _uno(self.u, acc.id, "instancia_de")
        self.assertEqual(verbo.id, "abrir_submenu")
        destino = _uno(self.u, acc.id, "submenu_destino")
        self.assertEqual(destino.id, "menu_config")

    def test_submenu_config_dos_opciones(self):
        opts = sorted(_valores(self.u, "menu_config", "tiene_opcion"),
                      key=lambda o: _orden(self.u, o))
        self.assertEqual([o.id for o in opts], ["opt_idioma", "opt_volver"])

    def test_bienvenida_tiene_texto(self):
        acc = _uno(self.u, "opt_bienvenida", "tiene_accion")
        txt = _uno(self.u, acc.id, "contenido")
        self.assertEqual(txt.axis, Axis.K)
        self.assertIn("Bienvenido", txt.label)
```

- [ ] **Step 2: Correr y verificar que falla**

Run: `PYTHONPATH=prototipo python3 -m unittest meta.tests.test_meta.TestSeed -v`
Expected: FAIL con `ModuleNotFoundError: No module named 'meta.seed'`.

- [ ] **Step 3: Implementar `seed.py`**

`prototipo/meta/seed.py`:
```python
"""Construye el menú meta-driven como hechos WQuestions y los persiste a SQLite."""
from wq import Universe, Individual, Axis

from .catalogo_app import build_catalog
from . import storage


def _k(id_, label=None):
    return Individual(id=id_, axis=Axis.K, label=label or id_)


def _o(id_, label=None):
    return Individual(id=id_, axis=Axis.O, label=label or id_)


def _n(value):
    return Individual(id=f"n_{value}", axis=Axis.N, label=str(value),
                      payload={"value": value})


def build_universe() -> Universe:
    u = Universe(catalog=build_catalog())

    # Tipos (K)
    t_menu, t_opcion = _k("menu"), _k("opcion")
    # Verbos-primitiva (K)
    v_texto = _k("mostrar_texto")
    v_sub = _k("abrir_submenu")
    v_volver = _k("volver")
    v_salir = _k("salir")
    # Textos (K) — el texto vive en el label
    txt_bien = _k("txt_bienvenida",
                  "¡Bienvenido a la demo meta-driven de WQuestions!")
    txt_idioma = _k("txt_idioma", "Idioma actual: español (es).")
    # Menús (O)
    m_main = _o("menu_principal", "Menú principal")
    m_cfg = _o("menu_config", "Configuración")
    # Opciones (O)
    opt_bien = _o("opt_bienvenida", "Bienvenida")
    opt_cfg = _o("opt_config", "Configuración")
    opt_salir = _o("opt_salir", "Salir")
    opt_idioma = _o("opt_idioma", "Idioma")
    opt_volver = _o("opt_volver", "Volver")
    # Acciones (O)
    acc_bien = _o("acc_bienvenida")
    acc_abrir = _o("acc_abrir_config")
    acc_salir = _o("acc_salir")
    acc_idioma = _o("acc_idioma")
    acc_volver = _o("acc_volver")

    def inst(o, k):
        u.assert_fact(o, "instancia_de", k)

    inst(m_main, t_menu)
    inst(m_cfg, t_menu)
    for o in (opt_bien, opt_cfg, opt_salir, opt_idioma, opt_volver):
        inst(o, t_opcion)
    inst(acc_bien, v_texto)
    inst(acc_abrir, v_sub)
    inst(acc_salir, v_salir)
    inst(acc_idioma, v_texto)
    inst(acc_volver, v_volver)

    # Menú principal y submenú: opciones + orden
    for opt, orden in [(opt_bien, 1), (opt_cfg, 2), (opt_salir, 3)]:
        u.assert_fact(m_main, "tiene_opcion", opt)
        u.assert_fact(opt, "orden", _n(orden))
    for opt, orden in [(opt_idioma, 1), (opt_volver, 2)]:
        u.assert_fact(m_cfg, "tiene_opcion", opt)
        u.assert_fact(opt, "orden", _n(orden))

    # Opción → acción
    for opt, acc in [(opt_bien, acc_bien), (opt_cfg, acc_abrir),
                     (opt_salir, acc_salir), (opt_idioma, acc_idioma),
                     (opt_volver, acc_volver)]:
        u.assert_fact(opt, "tiene_accion", acc)

    # Parámetros de las acciones
    u.assert_fact(acc_bien, "contenido", txt_bien)
    u.assert_fact(acc_idioma, "contenido", txt_idioma)
    u.assert_fact(acc_abrir, "submenu_destino", m_cfg)

    return u


def seed(conn) -> None:
    """Construye el universo del menú y lo persiste en `conn`."""
    storage.save(build_universe(), conn)
```

- [ ] **Step 4: Correr y verificar que pasa**

Run: `PYTHONPATH=prototipo python3 -m unittest meta.tests.test_meta.TestSeed -v`
Expected: PASS (4 tests).

- [ ] **Step 5: Commit**

```bash
git add prototipo/meta/seed.py prototipo/meta/tests/test_meta.py
git commit -m "feat(meta): seed del menú como hechos WQuestions"
```

---

## Task 4: `runtime.py` — el evaluador

**Files:**
- Create: `prototipo/meta/runtime.py`
- Modify: `prototipo/meta/tests/test_meta.py`

- [ ] **Step 1: Añadir los tests que fallan**

Añadir a `prototipo/meta/tests/test_meta.py`:
```python
from meta import runtime


class TestSignatura(unittest.TestCase):
    def test_signatura_protege(self):
        u = seed.build_universe()
        k = Individual(id="x_k", axis=Axis.K, label="x")
        menu = u.ind("menu_principal")
        # tiene_opcion espera valor en O; un K debe ser rechazado
        with self.assertRaises(SignatureError):
            u.assert_fact(menu, "tiene_opcion", k)


class TestNavegacion(unittest.TestCase):
    def test_navegacion_completa(self):
        u = seed.build_universe()
        entradas = iter(["1", "2", "2", "3"])  # Bienvenida, Configuración, Volver, Salir
        salida = []
        runtime.run(
            u,
            leer=lambda *_: next(entradas),
            escribir=lambda s: salida.append(str(s)),
        )
        texto = "\n".join(salida)
        self.assertIn("Bienvenido", texto)       # opción 1 mostró el texto
        self.assertIn("Menú principal", texto)    # se mostró el menú principal
        self.assertIn("Idioma", texto)            # el submenú mostró sus opciones

    def test_entrada_invalida_no_rompe(self):
        u = seed.build_universe()
        entradas = iter(["9", "x", "3"])  # fuera de rango, no-número, luego Salir
        salida = []
        runtime.run(
            u,
            leer=lambda *_: next(entradas),
            escribir=lambda s: salida.append(str(s)),
        )
        self.assertIn("inválida", "\n".join(salida).lower())


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Correr y verificar que falla**

Run: `PYTHONPATH=prototipo python3 -m unittest meta.tests.test_meta.TestNavegacion -v`
Expected: FAIL con `ModuleNotFoundError: No module named 'meta.runtime'`.

- [ ] **Step 3: Implementar `runtime.py`**

`prototipo/meta/runtime.py`:
```python
"""Evaluador genérico del menú meta-driven.

No conoce ninguna opción por nombre: lee el menú actual desde el grafo, lo muestra,
y despacha cada acción según su tipo-K (`instancia_de`). Agregar una primitiva nueva
= un individuo K + una entrada en DISPATCH.
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


# --- handlers: (u, accion, stack, escribir) -> bool "seguir corriendo" -------

def _h_mostrar_texto(u, accion, stack, escribir):
    txt = _uno(u, accion, "contenido")
    escribir(txt.label if txt is not None else "")
    return True


def _h_abrir_submenu(u, accion, stack, escribir):
    destino = _uno(u, accion, "submenu_destino")
    if destino is not None:
        stack.append(destino)
    return True


def _h_volver(u, accion, stack, escribir):
    if len(stack) > 1:
        stack.pop()
    return True


def _h_salir(u, accion, stack, escribir):
    return False


DISPATCH = {
    "mostrar_texto": _h_mostrar_texto,
    "abrir_submenu": _h_abrir_submenu,
    "volver": _h_volver,
    "salir": _h_salir,
}


def run(u, leer=input, escribir=print, menu_inicial="menu_principal"):
    """Corre el menú. `leer`/`escribir` son inyectables para testear sin teclado."""
    stack = [u.ind(menu_inicial)]
    seguir = True
    while seguir:
        menu = stack[-1]
        opciones = _opciones(u, menu)
        escribir(f"\n== {menu.label} ==")
        for i, opt in enumerate(opciones, 1):
            escribir(f"  {i}. {opt.label}")

        entrada = str(leer("> ")).strip()
        if not entrada.isdigit() or not (1 <= int(entrada) <= len(opciones)):
            escribir("Opción inválida.")
            continue

        opcion = opciones[int(entrada) - 1]
        accion = _uno(u, opcion, "tiene_accion")
        verbo = _uno(u, accion, "instancia_de")
        handler = DISPATCH.get(verbo.id) if verbo is not None else None
        if handler is None:
            escribir(f"(sin handler para '{verbo.id if verbo else '?'}')")
            continue
        seguir = handler(u, accion, stack, escribir)
```

- [ ] **Step 4: Correr y verificar que pasa**

Run: `PYTHONPATH=prototipo python3 -m unittest meta.tests.test_meta.TestSignatura meta.tests.test_meta.TestNavegacion -v`
Expected: PASS (3 tests).

- [ ] **Step 5: Correr TODA la suite del paquete meta**

Run: `PYTHONPATH=prototipo python3 -m unittest meta.tests.test_meta -v`
Expected: PASS — 9 tests (1 catálogo + 1 storage + 4 seed + 1 signatura + 2 navegación) sin errores.

- [ ] **Step 6: Commit**

```bash
git add prototipo/meta/runtime.py prototipo/meta/tests/test_meta.py
git commit -m "feat(meta): evaluador genérico (dispatch por tipo-K) + tests de navegación"
```

---

## Task 5: `__main__.py` — entry point

**Files:**
- Create: `prototipo/meta/__main__.py`

- [ ] **Step 1: Implementar `__main__.py`**

`prototipo/meta/__main__.py`:
```python
"""Entry point: `PYTHONPATH=prototipo python3 -m meta`.

Abre (o crea) la BD SQLite del menú; si está vacía, la siembra; carga el universo
y corre el evaluador.
"""
import os
import sqlite3

from .catalogo_app import build_catalog
from . import storage, seed, runtime

DB_PATH = os.path.join(os.path.dirname(__file__), "menu.db")


def main():
    conn = sqlite3.connect(DB_PATH)
    storage.init_db(conn)
    vacio = conn.execute("SELECT COUNT(*) FROM hechos").fetchone()[0] == 0
    if vacio:
        seed.seed(conn)
    u = storage.load(conn, build_catalog())
    try:
        runtime.run(u)
    except (EOFError, KeyboardInterrupt):
        print("\nHasta luego.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Smoke test manual (navegación scripteada por stdin)**

Run:
```bash
printf '1\n2\n2\n3\n' | PYTHONPATH=prototipo python3 -m meta
```
Expected: imprime el "Menú principal" con sus 3 opciones, muestra el texto de bienvenida tras `1`, entra a "Configuración" tras `2`, vuelve tras `2`, y termina tras `3`. Debe quedar creado el archivo `prototipo/meta/menu.db`.

- [ ] **Step 3: Verificar que el menú vive en SQLite**

Run:
```bash
sqlite3 prototipo/meta/menu.db "SELECT sujeto,rol,valor FROM hechos WHERE rol='tiene_opcion';"
```
Expected: filas `menu_principal|tiene_opcion|opt_bienvenida` (y las demás opciones). Confirma que la estructura está en la BD, no en el código.

- [ ] **Step 4: Ignorar la BD generada en git**

Añadir a `.gitignore` (al final):
```
# BD generada por el demo meta-driven
prototipo/meta/menu.db
```

- [ ] **Step 5: Commit**

```bash
git add prototipo/meta/__main__.py .gitignore
git commit -m "feat(meta): entry point python -m meta (seed + load + run)"
```

---

## Task 6: Cleanup — docstring de `wq/__init__.py`

**Files:**
- Modify: `prototipo/wq/__init__.py:4`

- [ ] **Step 1: Corregir "8 ejes" → "7 ejes"**

En `prototipo/wq/__init__.py`, en el docstring, cambiar la línea:
```python
- 8 ejes (Q, O, L, T, N, K, P, M)
```
por:
```python
- 7 ejes (Q, O, L, T, N, K, M)
```

- [ ] **Step 2: Verificar que la librería sigue importando y los tests del prototipo pasan**

Run: `PYTHONPATH=prototipo python3 -m unittest discover -s prototipo/tests -q`
Expected: `OK` (21 tests).

- [ ] **Step 3: Commit**

```bash
git add prototipo/wq/__init__.py
git commit -m "docs(wq): corregir docstring a 7 ejes (residuo del colapso de P)"
```

---

## Verificación final

- [ ] **Suite completa del paquete meta**

Run: `PYTHONPATH=prototipo python3 -m unittest meta.tests.test_meta -v`
Expected: PASS, 9 tests.

- [ ] **Demo corre end-to-end**

Run: `printf '1\n2\n1\n2\n3\n' | PYTHONPATH=prototipo python3 -m meta`
Expected: navega principal → bienvenida → configuración → idioma (muestra el texto de idioma) → volver → salir, sin errores.
