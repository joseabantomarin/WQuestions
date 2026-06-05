# Maestros (persona/producto) + Compras — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Agregar entidades maestras `persona` (Q) y `producto` (registrable) y una transacción `compra` que espeja a `venta`, todo sobre el mismo grafo, con dos generalizaciones chicas del motor para que sea casi solo datos.

**Architecture:** El motor gana dos lecturas de datos en `guardar` (`eje_instancia` → eje del individuo nuevo; `campo_etiqueta` → label visible). El resto es seed: tipos, esquemas, entidades compartidas y ramas de menú. La UI y la API no cambian (ya son genéricas).

**Tech Stack:** Python 3.9 stdlib, librería `wq`, `unittest` (NO pytest), `PYTHONPATH=prototipo`. Chrome headless para smoke. Rama `main`.

**Spec:** `docs/superpowers/specs/2026-06-05-maestros-compras-design.md`

**Entorno:** comandos desde `/Users/joseabanto/WQuestions` con `PYTHONPATH=prototipo`.

---

## File Structure

| Archivo | Cambio |
|---|---|
| `prototipo/meta/catalogo_app.py` | MOD: roles `eje_instancia` (K→K), `campo_etiqueta` (K→O). |
| `prototipo/meta/engine.py` | MOD: `guardar` lee `eje_instancia` y `campo_etiqueta` al crear. |
| `prototipo/meta/seed.py` | MOD: tipos persona/producto/compra + esquemas + entidades + menús; migra venta.cliente→persona. |
| `prototipo/meta/tests/test_meta.py` | MOD: tests nuevos + ajustar 2 tests por la migración. |

UI (`web/static/*`) y API (`web/server.py`) **no se tocan**.

---

## Task 1: Roles de catálogo `eje_instancia` y `campo_etiqueta`

**Files:** Modify `prototipo/meta/catalogo_app.py`, `prototipo/meta/tests/test_meta.py`

- [ ] **Step 1: Test que falla**

Añadir a `prototipo/meta/tests/test_meta.py` en `class TestCatalogo`:
```python
    def test_roles_de_maestros_registrados(self):
        cat = build_catalog()
        self.assertEqual(cat.get("eje_instancia").domain, Axis.K)
        self.assertEqual(cat.get("eje_instancia").range, Axis.K)
        self.assertEqual(cat.get("campo_etiqueta").domain, Axis.K)
        self.assertEqual(cat.get("campo_etiqueta").range, Axis.O)
```

- [ ] **Step 2: Correr y ver que falla**

Run: `PYTHONPATH=prototipo python3 -m unittest meta.tests.test_meta.TestCatalogo.test_roles_de_maestros_registrados -v`
Expected: FAIL (`cat.get("eje_instancia")` es None → AttributeError).

- [ ] **Step 3: Registrar los roles**

En `prototipo/meta/catalogo_app.py`, dentro de `build_catalog`, añadir a la lista de roles:
```python
        RoleSignature("eje_instancia", Axis.K, Axis.K, True,
                      "tipo de entidad → eje (K cuyo label es la letra: Q/O/...) de sus instancias"),
        RoleSignature("campo_etiqueta", Axis.K, Axis.O, True,
                      "tipo de entidad → campo cuyo valor es la etiqueta visible del individuo"),
```

- [ ] **Step 4: Correr y ver que pasa**

Run: `PYTHONPATH=prototipo python3 -m unittest meta.tests.test_meta.TestCatalogo -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add prototipo/meta/catalogo_app.py prototipo/meta/tests/test_meta.py
git commit -m "feat(meta): roles eje_instancia y campo_etiqueta

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 2: `guardar` lee `eje_instancia` y `campo_etiqueta`

**Files:** Modify `prototipo/meta/engine.py`, `prototipo/meta/tests/test_meta.py`

- [ ] **Step 1: Test que falla (universo mínimo, independiente del seed)**

Añadir a `prototipo/meta/tests/test_meta.py`:
```python
class TestGuardarGeneralizado(unittest.TestCase):
    def _mini(self):
        from wq import Universe, Individual, Axis
        from meta.catalogo_app import build_catalog
        u = Universe(catalog=build_catalog())

        def K(i, l=None):
            ind = Individual(id=i, axis=Axis.K, label=l or i); u.add_individual(ind); return ind

        def O(i, l=None):
            ind = Individual(id=i, axis=Axis.O, label=l or i); u.add_individual(ind); return ind

        def N(v):
            ind = Individual(id=f"n_{v}", axis=Axis.N, label=str(v), payload={"value": v}); u.add_individual(ind); return ind

        persona = K("persona", "Persona"); campo = K("campo"); texto = K("texto"); eje_q = K("eje_q", "Q")
        cn = O("campo_persona_nombre", "Nombre")
        u.assert_fact(cn, "instancia_de", campo)
        u.assert_fact(persona, "tiene_campo", cn)
        u.assert_fact(cn, "tipo_dato", texto)
        u.assert_fact(cn, "orden", N(1))
        u.assert_fact(cn, "rol", K("nombre"))
        u.assert_fact(persona, "eje_instancia", eje_q)
        u.assert_fact(persona, "campo_etiqueta", cn)
        return u

    def test_guardar_usa_eje_instancia_y_campo_etiqueta(self):
        u = self._mini()
        rid = _engine.guardar(u, "persona", {"nombre": "Ana"})
        reg = u.ind(rid)
        self.assertEqual(reg.axis, Axis.Q)      # eje_instancia → Q
        self.assertEqual(reg.label, "Ana")      # campo_etiqueta → "Ana"

    def test_guardar_default_axis_O_sin_eje_instancia(self):
        u = self._mini()
        # un tipo sin eje_instancia ni campo_etiqueta → O y label genérico
        from wq import Individual, Axis
        cosa = Individual(id="cosa", axis=Axis.K, label="Cosa"); u.add_individual(cosa)
        rid = _engine.guardar(u, "cosa", {})
        self.assertEqual(u.ind(rid).axis, Axis.O)
```
(`_engine` ya se importa en `test_meta.py` de la iteración previa: `from meta import engine as _engine`. Si no estuviera, añádelo arriba.)

- [ ] **Step 2: Correr y ver que falla**

Run: `PYTHONPATH=prototipo python3 -m unittest meta.tests.test_meta.TestGuardarGeneralizado -v`
Expected: FAIL — `test_guardar_usa_eje_instancia_y_campo_etiqueta` falla (hoy `guardar` crea en O con label genérico).

- [ ] **Step 3: Generalizar `guardar`**

En `prototipo/meta/engine.py`, en la función `guardar`, reemplazar el bloque `else:` que crea el individuo nuevo:
```python
    else:
        reg = Individual(id=mint_id(tipo_id), axis=Axis.O, label=f"{tipo_id} nuevo")
        u.assert_fact(reg, "instancia_de", tipo)
```
por:
```python
    else:
        ax = _uno(u, tipo, "eje_instancia")
        axis = Axis(ax.label) if ax is not None else Axis.O
        etq = _uno(u, tipo, "campo_etiqueta")
        label = f"{tipo_id} nuevo"
        if etq is not None:
            rol_etq_ind = _uno(u, etq, "rol")
            rol_etq = rol_etq_ind.id if rol_etq_ind is not None else etq.id
            label = str(valores.get(rol_etq, label))
        reg = Individual(id=mint_id(tipo_id), axis=axis, label=label)
        u.assert_fact(reg, "instancia_de", tipo)
```

- [ ] **Step 4: Correr y ver que pasa**

Run: `PYTHONPATH=prototipo python3 -m unittest meta.tests.test_meta.TestGuardarGeneralizado -v`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
git add prototipo/meta/engine.py prototipo/meta/tests/test_meta.py
git commit -m "feat(meta): guardar lee eje_instancia (eje del individuo) y campo_etiqueta (label)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 3: Seed — persona, producto registrable, compra + menús (migra venta.cliente→persona)

**Files:** Modify `prototipo/meta/seed.py`, `prototipo/meta/tests/test_meta.py`

- [ ] **Step 1: Reemplazar el bloque de entidades/menú del seed**

En `prototipo/meta/seed.py`, dentro de `build_universe`, localiza el bloque que la iteración anterior añadió para Ventas — arranca en el comentario `# --- Rama Ventas (permanente) ---` (donde se crean `v_form`, el tipo `venta`, su esquema, las entidades ana/beto/laptop/mouse, los registros y la rama de menú Ventas) y termina **justo antes de `return u`**. Reemplaza ese bloque COMPLETO por el siguiente (reusa `_k`, `_o`, `_n`, `m_main`, `t_menu`, `t_opcion`, `v_volver`, `v_sub`, `Individual`, `Axis`, `time_point` ya presentes en el archivo):

```python
    # --- Verbos de pantalla + tipos de dato + meta-tipo campo + ejes ---
    v_form = _k("abrir_formulario"); v_grilla = _k("abrir_grilla")
    campo = _k("campo")
    t_texto = _k("texto"); t_numero = _k("numero"); t_fecha = _k("fecha"); t_ref = _k("referencia")
    eje_q = _k("eje_q", "Q"); eje_o = _k("eje_o", "O")

    def _campo(tipo, cid, etiqueta, tipo_k, orden, rol_k, ref_k=None):
        c = _o(cid, etiqueta)
        u.assert_fact(c, "instancia_de", campo)
        u.assert_fact(tipo, "tiene_campo", c)
        u.assert_fact(c, "tipo_dato", tipo_k)
        u.assert_fact(c, "orden", _n(orden))
        u.assert_fact(c, "rol", rol_k)
        if ref_k is not None:
            u.assert_fact(c, "referencia_a", ref_k)
        return c

    # --- Tipos de entidad ---
    persona = _k("persona", "Persona"); producto = _k("producto", "Producto")
    venta = _k("venta", "Venta"); compra = _k("compra", "Compra")
    u.assert_fact(persona, "eje_instancia", eje_q)
    u.assert_fact(producto, "eje_instancia", eje_o)
    # venta/compra sin eje_instancia → default O en guardar

    # esquemas (campos como datos)
    cp_nombre = _campo(persona, "campo_persona_nombre", "Nombre", t_texto, 1, _k("nombre"))
    u.assert_fact(persona, "campo_etiqueta", cp_nombre)

    cpr_nombre = _campo(producto, "campo_producto_nombre", "Nombre", t_texto, 1, _k("nombre_producto"))
    _campo(producto, "campo_producto_precio", "Precio", t_numero, 2, _k("precio"))
    u.assert_fact(producto, "campo_etiqueta", cpr_nombre)

    _campo(venta, "campo_venta_fecha", "Fecha", t_fecha, 1, t_fecha)
    _campo(venta, "campo_venta_cliente", "Cliente", t_ref, 2, _k("cliente"), persona)
    _campo(venta, "campo_venta_producto", "Producto", t_ref, 3, producto, producto)
    _campo(venta, "campo_venta_monto", "Monto", t_numero, 4, _k("monto"))

    _campo(compra, "campo_compra_fecha", "Fecha", t_fecha, 1, t_fecha)
    _campo(compra, "campo_compra_proveedor", "Proveedor", t_ref, 2, _k("proveedor"), persona)
    _campo(compra, "campo_compra_producto", "Producto", t_ref, 3, producto, producto)
    _campo(compra, "campo_compra_monto", "Monto", t_numero, 4, _k("monto"))

    # --- Entidades maestras compartidas ---
    ana = Individual(id="ana", axis=Axis.Q, label="Ana")
    beto = Individual(id="beto", axis=Axis.Q, label="Beto")
    laptop = _o("laptop", "Laptop"); mouse = _o("mouse", "Mouse")
    for p, nom in [(ana, "Ana"), (beto, "Beto")]:
        u.assert_fact(p, "instancia_de", persona)
        u.assert_fact(p, "nombre", _k(nom))
    for pr, nom, pre in [(laptop, "Laptop", 1200), (mouse, "Mouse", 25)]:
        u.assert_fact(pr, "instancia_de", producto)
        u.assert_fact(pr, "nombre_producto", _k(nom))
        u.assert_fact(pr, "precio", _n(pre))

    # --- Registros de ejemplo ---
    def _registro(tipo, rid, **rol_valor):
        r = _o(rid, rid)
        u.assert_fact(r, "instancia_de", tipo)
        for rol, val in rol_valor.items():
            u.assert_fact(r, rol, val)
        return r
    _registro(venta, "venta_001", fecha=time_point("2026-06-01"), cliente=ana, producto=laptop, monto=_n(120))
    _registro(venta, "venta_002", fecha=time_point("2026-06-02"), cliente=beto, producto=mouse, monto=_n(25))
    _registro(compra, "compra_001", fecha=time_point("2026-05-20"), proveedor=ana, producto=laptop, monto=_n(900))

    # --- Menús: Ventas, Compras, Maestros(Personas/Productos) ---
    def _submenu(mid, label, orden_en_padre, padre):
        m = _o(mid, label)
        u.assert_fact(m, "instancia_de", t_menu)
        opt = _o(f"opt_{mid}", label); acc = _o(f"acc_open_{mid}")
        u.assert_fact(opt, "instancia_de", t_opcion)
        u.assert_fact(padre, "tiene_opcion", opt)
        u.assert_fact(opt, "orden", _n(orden_en_padre))
        u.assert_fact(opt, "tiene_accion", acc)
        u.assert_fact(acc, "instancia_de", v_sub)
        u.assert_fact(acc, "submenu_destino", m)
        return m

    def _opcion(menu, oid, label, orden, verbo, **extra):
        opt = _o(oid, label); acc = _o(f"acc_{oid}")
        u.assert_fact(opt, "instancia_de", t_opcion)
        u.assert_fact(menu, "tiene_opcion", opt)
        u.assert_fact(opt, "orden", _n(orden))
        u.assert_fact(opt, "tiene_accion", acc)
        u.assert_fact(acc, "instancia_de", verbo)
        for rol, val in extra.items():
            u.assert_fact(acc, rol, val)
        return opt

    def _pantallas(menu_padre, mid, label, orden_padre, tipo):
        m = _submenu(mid, label, orden_padre, menu_padre)
        _opcion(m, f"opt_{mid}_reg", "Registro", 1, v_form, sobre_tipo=tipo)
        _opcion(m, f"opt_{mid}_con", "Consulta", 2, v_grilla, sobre_tipo=tipo)
        _opcion(m, f"opt_{mid}_vol", "Volver", 3, v_volver)
        return m

    _pantallas(m_main, "menu_ventas", "Ventas", 2.5, venta)
    _pantallas(m_main, "menu_compras", "Compras", 2.6, compra)
    m_maestros = _submenu("menu_maestros", "Maestros", 2.7, m_main)
    _pantallas(m_maestros, "menu_personas", "Personas", 1, persona)
    _pantallas(m_maestros, "menu_productos", "Productos", 2, producto)
    _opcion(m_maestros, "opt_maestros_vol", "Volver", 3, v_volver)
```
**Nota:** si el seed previo creaba el verbo `abrir_submenu`/`v_sub` o el menú base con nombres distintos a `m_main`/`t_menu`/`t_opcion`/`v_volver`/`v_sub`, usa los reales del archivo. NO redefinas el menú base (Bienvenida/Configuración/Salir): este bloque solo agrega ramas a `m_main`.

- [ ] **Step 2: Ajustar los 2 tests previos afectados por la migración**

En `prototipo/meta/tests/test_meta.py`, en `class TestEntidad`:
- En `test_campos_ordenados`, cambiar la aserción del campo cliente:
  ```python
        self.assertEqual(campos[1]["referencia_a"], "cliente")
  ```
  por:
  ```python
        self.assertEqual(campos[1]["referencia_a"], "persona")
  ```
- Renombrar/reescribir `test_opciones_ref_lista_clientes`:
  ```python
    def test_opciones_ref_lista_personas(self):
        ops = _engine._opciones_ref(self.u, "persona")
        self.assertEqual({o["id"] for o in ops}, {"ana", "beto"})
  ```

- [ ] **Step 3: Tests nuevos de maestros + compras**

Añadir a `prototipo/meta/tests/test_meta.py`:
```python
class TestMaestrosCompras(unittest.TestCase):
    def setUp(self):
        self.u = seed.build_universe()

    def test_persona_es_Q_clasificada_con_nombre(self):
        ana = self.u.ind("ana")
        self.assertEqual(ana.axis, Axis.Q)
        tipos = [f.value.id for f in self.u.facts_about(ana) if f.role == "instancia_de"]
        self.assertIn("persona", tipos)

    def test_eje_instancia_persona_es_Q(self):
        ax = _engine._uno(self.u, self.u.ind("persona"), "eje_instancia")
        self.assertEqual(ax.label, "Q")

    def test_guardar_persona_crea_en_Q_con_label(self):
        rid = _engine.guardar(self.u, "persona", {"nombre": "Caro"})
        reg = self.u.ind(rid)
        self.assertEqual(reg.axis, Axis.Q)
        self.assertEqual(reg.label, "Caro")

    def test_guardar_producto_con_precio(self):
        rid = _engine.guardar(self.u, "producto",
                              {"nombre_producto": "Teclado", "precio": "50"})
        reg = self.u.ind(rid)
        self.assertEqual(reg.axis, Axis.O)
        self.assertEqual(reg.label, "Teclado")
        precio = [f.value for f in self.u.facts_about(reg) if f.role == "precio"][-1]
        self.assertEqual(precio.axis, Axis.N)

    def test_compra_referencia_persona_y_producto(self):
        campos = _engine._campos(self.u, self.u.ind("compra"))
        prov = next(c for c in campos if c["rol"] == "proveedor")
        self.assertEqual(prov["referencia_a"], "persona")

    def test_persona_compartida_cliente_y_proveedor(self):
        # ana es proveedor en compra_001 (seed) y la usamos como cliente en una venta
        vid = _engine.guardar(self.u, "venta",
                              {"fecha": "2026-06-05", "cliente": "ana",
                               "producto": "laptop", "monto": "300"})
        cli = [f.value for f in self.u.facts_about(self.u.ind(vid)) if f.role == "cliente"][-1]
        prov = [f.value for f in self.u.facts_about(self.u.ind("compra_001")) if f.role == "proveedor"][-1]
        self.assertEqual(cli.id, prov.id)   # mismo individuo persona

    def test_menu_principal_incluye_compras_y_maestros(self):
        opts = [f.value.label for f in self.u.facts_about(self.u.ind("menu_principal"))
                if f.role == "tiene_opcion"]
        self.assertIn("Compras", opts)
        self.assertIn("Maestros", opts)

    def test_maestros_tiene_personas_y_productos(self):
        opts = [f.value.label for f in self.u.facts_about(self.u.ind("menu_maestros"))
                if f.role == "tiene_opcion"]
        self.assertIn("Personas", opts)
        self.assertIn("Productos", opts)
```

- [ ] **Step 4: Correr toda la suite meta**

Run: `PYTHONPATH=prototipo python3 -m unittest meta.tests.test_meta -v`
Expected: PASS — previos (con los 2 ajustes) + `TestMaestrosCompras` (8) + `TestGuardarGeneralizado` (2).

- [ ] **Step 5: Commit**

```bash
git add prototipo/meta/seed.py prototipo/meta/tests/test_meta.py
git commit -m "feat(meta): seed con persona/producto/compra + menús Compras y Maestros (venta.cliente→persona)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Verificación final

- [ ] **Suites completas**

Run: `PYTHONPATH=prototipo python3 -m unittest discover -s prototipo/tests -q && PYTHONPATH=prototipo python3 -m unittest meta.tests.test_meta meta.tests.test_web -q`
Expected: ambos OK (wq sin cambios = 23; meta crece con los tests nuevos; web sin cambios).

- [ ] **End-to-end por API (registrar persona, registrar producto, crear compra que los referencia)**

```bash
rm -f prototipo/meta/wq.db
PYTHONPATH=prototipo python3 -c "
import os
from meta.web.server import crear_servidor
httpd,_ = crear_servidor(os.path.join('prototipo','meta','wq.db'),'127.0.0.1',8000)
httpd.serve_forever()" > /tmp/w.log 2>&1 &
SRV=$!; sleep 2
echo "alta persona:"; curl -s -X POST -H "Content-Type: application/json" -d '{"entidad":"persona","valores":{"nombre":"Caro"}}' http://127.0.0.1:8000/api/guardar
echo; echo "alta producto:"; curl -s -X POST -H "Content-Type: application/json" -d '{"entidad":"producto","valores":{"nombre_producto":"Teclado","precio":"50"}}' http://127.0.0.1:8000/api/guardar
echo; echo "personas disponibles (form de compra):"; curl -s -X POST -H "Content-Type: application/json" -d '{"entidad":"compra","registro_id":null}' http://127.0.0.1:8000/api/abrir_formulario | python3 -c "import sys,json;ef=json.load(sys.stdin)['efecto'];prov=next(c for c in ef['campos'] if c['rol']=='proveedor');print('  opciones proveedor:',[o['label'] for o in prov['opciones']])"
kill $SRV 2>/dev/null
```
Expected: dos `{"ok": true, ...}`; las opciones de proveedor incluyen `Ana`, `Beto` y `Caro` (la persona recién creada **aparece compartida** en el form de compra).

- [ ] **Smoke visual**

```bash
PYTHONPATH=prototipo python3 -c "
import os
from meta.web.server import crear_servidor
httpd,_ = crear_servidor(os.path.join('prototipo','meta','wq.db'),'127.0.0.1',8000)
httpd.serve_forever()" > /tmp/w.log 2>&1 &
SRV=$!; sleep 2
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu --hide-scrollbars --virtual-time-budget=4000 --window-size=1200,860 --screenshot=/tmp/maestros.png http://127.0.0.1:8000/ 2>/dev/null
kill $SRV 2>/dev/null
ls -l /tmp/maestros.png
```
Expected: `/tmp/maestros.png` > 0 bytes (muestra el menú principal con Ventas/Compras/Maestros). Las pantallas modales solo se ven al hacer click (Chrome headless no clickea); la verificación funcional real es el end-to-end por API de arriba.
