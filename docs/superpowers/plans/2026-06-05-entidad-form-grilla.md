# Pantallas de entidad (form + grilla) meta-driven — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Sobre el menú meta-driven, agregar pantallas de entidad genéricas (form de edición + grilla) cuyo esquema y registros viven en datos, con entidades compartidas en un grafo único y escritura persistente.

**Architecture:** Se ajusta `wq` (`instancia_de` V→K, alineando con el libro) para clasificar entidades de cualquier eje. El motor suma 3 primitivas genéricas (`abrir_formulario`, `abrir_grilla`, `guardar`) que leen el esquema/registros del grafo; el servidor suma 2 endpoints (uno escribe y persiste a `wq.db`); el frontend abre una ventana modal con form o grilla. Todo el esquema (`venta` + campos) y los registros son datos en el seed.

**Tech Stack:** Python 3.9 stdlib (`http.server`, `sqlite3`, `unittest`), librería local `wq`, HTML/CSS/JS vanilla. Chrome headless para smoke. NO hay pytest: `unittest`.

**Spec:** `docs/superpowers/specs/2026-06-05-entidad-form-grilla-design.md`

**Entorno:** comandos desde la raíz `/Users/joseabanto/WQuestions` con `PYTHONPATH=prototipo`. Rama `main`.

---

## File Structure

| Archivo | Cambio |
|---|---|
| `prototipo/wq/axes.py` | MOD: añadir `Axis.V` (comodín de signatura). |
| `prototipo/wq/catalog.py` | MOD: `validate` trata `V` como comodín; `instancia_de` → `V→K`. |
| `prototipo/tests/test_wq.py` | MOD: tests de `instancia_de` V→K. |
| `libro/manuscrito/29_anexo_prototipo.md` | MOD: sync del catálogo (`instancia_de: V→K`) y `axes.py`. |
| `prototipo/meta/catalogo_app.py` | MOD: 5 roles estructurales del app. |
| `prototipo/meta/seed.py` | MOD: rama Ventas + tipo `venta` + esquema + entidades + registros; `abrir_universo` usa `wq.db`. |
| `prototipo/meta/__main__.py` | MOD: `DB_PATH` → `wq.db`. |
| `prototipo/meta/engine.py` | MOD: lectores + `guardar` + handlers `abrir_formulario`/`abrir_grilla` + `efecto_formulario`/`efecto_grilla` + título en `seleccionar`. |
| `prototipo/meta/web/server.py` | MOD: endpoints `/api/abrir_formulario`, `/api/guardar`; guarda `db_path`. |
| `prototipo/meta/web/__main__.py` | MOD: `DB_PATH` → `wq.db`. |
| `prototipo/meta/web/static/{index.html,app.js,style.css}` | MOD: ventana modal + form + grilla. |
| `prototipo/meta/tests/test_meta.py` | MOD: `TestEntidad`. |
| `prototipo/meta/tests/test_web.py` | MOD: tests de guardar/abrir_formulario. |
| `.gitignore` | MOD: `menu.db` → `wq.db`. |

---

## Task 1: Ajuste `wq` — `Axis.V` + `instancia_de` V→K

**Files:** Modify `prototipo/wq/axes.py`, `prototipo/wq/catalog.py`, `prototipo/tests/test_wq.py`

- [ ] **Step 1: Tests que fallan**

Añadir a `prototipo/tests/test_wq.py`, dentro de `class TestSignatures` (que ya tiene `setUp` con `self.u`, `self.sit`∈O, `self.persona`∈Q, `self.lugar`∈L, `self.cat_k`∈K):
```python
    def test_instancia_de_acepta_sujeto_de_cualquier_eje_de_valor(self):
        # V→K: un sujeto en Q es válido (antes el dominio era O)
        f = self.u.assert_fact(self.persona, "instancia_de", self.cat_k)
        self.assertEqual(f.role, "instancia_de")

    def test_instancia_de_sigue_exigiendo_valor_K(self):
        with self.assertRaises(SignatureError):
            self.u.assert_fact(self.persona, "instancia_de", self.lugar)
```

- [ ] **Step 2: Correr y ver que el primero falla**

Run: `PYTHONPATH=prototipo python3 -m unittest prototipo.tests.test_wq 2>/dev/null || PYTHONPATH=prototipo python3 -m unittest discover -s prototipo/tests -k instancia_de -v`
Expected: `test_instancia_de_acepta_sujeto_de_cualquier_eje_de_valor` FALLA con `SignatureError` (dominio O); el otro pasa.

- [ ] **Step 3: Añadir `Axis.V`**

En `prototipo/wq/axes.py`, dentro de `class Axis(Enum)`, añadir (después de `M`):
```python
    V = "V"  # comodín de signatura: "cualquier eje de valor" (no es lugar de individuos)
```
`VALUE_AXES` y `is_value_axis` NO cambian (V no es eje de valor → los individuos siguen sin poder vivir en V).

- [ ] **Step 4: `validate` trata V como comodín + `instancia_de` V→K**

En `prototipo/wq/catalog.py`, en `Catalog.validate`, reemplazar las dos comprobaciones:
```python
        if subject.axis != sig.domain:
            raise SignatureError(
                f"Sujeto en eje incorrecto para '{role}': se esperaba "
                f"{sig.domain.value}, recibido {subject.axis.value} "
                f"(sujeto={subject})"
            )
        if value.axis != sig.range:
            raise SignatureError(
                f"Valor en eje incorrecto para '{role}': se esperaba "
                f"{sig.range.value}, recibido {value.axis.value} "
                f"(valor={value})"
            )
```
por (añadiendo el comodín `Axis.V`):
```python
        if sig.domain != Axis.V and subject.axis != sig.domain:
            raise SignatureError(
                f"Sujeto en eje incorrecto para '{role}': se esperaba "
                f"{sig.domain.value}, recibido {subject.axis.value} "
                f"(sujeto={subject})"
            )
        if sig.range != Axis.V and value.axis != sig.range:
            raise SignatureError(
                f"Valor en eje incorrecto para '{role}': se esperaba "
                f"{sig.range.value}, recibido {value.axis.value} "
                f"(valor={value})"
            )
```
Y cambiar la signatura canónica de `instancia_de` (en `_load_canonical`):
```python
            RoleSignature("instancia_de", Axis.O, Axis.K, False,
                          "sujeto pertenece a la categoría"),
```
por:
```python
            RoleSignature("instancia_de", Axis.V, Axis.K, False,
                          "sujeto (cualquier eje de valor) pertenece a la categoría"),
```

- [ ] **Step 5: Correr toda la suite `wq`**

Run: `PYTHONPATH=prototipo python3 -m unittest discover -s prototipo/tests -v`
Expected: OK — 23 tests (21 previos + 2 nuevos). El cambio solo afloja el dominio; nada se rompe.

- [ ] **Step 6: Commit**

```bash
git add prototipo/wq/axes.py prototipo/wq/catalog.py prototipo/tests/test_wq.py
git commit -m "feat(wq): instancia_de pasa a V→K (Axis.V comodín), alinea con el libro Cap 4

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 2: Renombrar `menu.db` → `wq.db` (grafo único)

**Files:** Modify `prototipo/meta/__main__.py`, `prototipo/meta/web/__main__.py`, `.gitignore`; delete `prototipo/meta/menu.db`

- [ ] **Step 1: Cambiar las rutas y el .gitignore**

En `prototipo/meta/__main__.py`, la línea:
```python
DB_PATH = os.path.join(os.path.dirname(__file__), "menu.db")
```
por:
```python
DB_PATH = os.path.join(os.path.dirname(__file__), "wq.db")
```
En `prototipo/meta/web/__main__.py`, la línea:
```python
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "menu.db")
```
por:
```python
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "wq.db")
```
En `.gitignore`, cambiar `prototipo/meta/menu.db` por `prototipo/meta/wq.db`.

- [ ] **Step 2: Borrar el menu.db viejo (datos efímeros)**

Run: `rm -f prototipo/meta/menu.db`

- [ ] **Step 3: Smoke CLI (se re-siembra wq.db)**

Run: `printf '1\n3\n' | PYTHONPATH=prototipo python3 -m meta`
Expected: muestra el menú, el texto de bienvenida y sale; se crea `prototipo/meta/wq.db`. Verifica que NO se creó `menu.db`.

- [ ] **Step 4: Commit**

```bash
git add prototipo/meta/__main__.py prototipo/meta/web/__main__.py .gitignore
git commit -m "refactor(meta): renombrar el store a wq.db (un solo grafo)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 3: Roles estructurales del app

**Files:** Modify `prototipo/meta/catalogo_app.py`, `prototipo/meta/tests/test_meta.py`

- [ ] **Step 1: Test que falla**

Añadir a `prototipo/meta/tests/test_meta.py` (en `class TestCatalogo`, junto a los asserts existentes — o como método nuevo):
```python
    def test_roles_de_entidad_registrados(self):
        cat = build_catalog()
        self.assertEqual(cat.get("tiene_campo").domain, Axis.K)
        self.assertEqual(cat.get("tiene_campo").range, Axis.O)
        self.assertFalse(cat.get("tiene_campo").functional)
        self.assertEqual(cat.get("sobre_tipo").range, Axis.K)
        self.assertEqual(cat.get("tipo_dato").range, Axis.K)
        self.assertEqual(cat.get("rol").range, Axis.K)
        self.assertEqual(cat.get("referencia_a").range, Axis.K)
```

- [ ] **Step 2: Correr y ver que falla**

Run: `PYTHONPATH=prototipo python3 -m unittest meta.tests.test_meta.TestCatalogo.test_roles_de_entidad_registrados -v`
Expected: FAIL (`cat.get("tiene_campo")` es None → AttributeError).

- [ ] **Step 3: Registrar los roles**

En `prototipo/meta/catalogo_app.py`, dentro de `build_catalog`, añadir a la lista `roles`:
```python
        RoleSignature("sobre_tipo", Axis.O, Axis.K, True,
                      "acción → tipo de entidad sobre el que opera"),
        RoleSignature("tiene_campo", Axis.K, Axis.O, False,
                      "tipo de entidad → campo (descriptor)"),
        RoleSignature("tipo_dato", Axis.O, Axis.K, True,
                      "campo → tipo de dato (texto/numero/fecha/referencia)"),
        RoleSignature("rol", Axis.O, Axis.K, True,
                      "campo → rol; el id de ese K es el predicado en los registros"),
        RoleSignature("referencia_a", Axis.O, Axis.K, True,
                      "campo referencia → tipo de entidad apuntado"),
```

- [ ] **Step 4: Correr y ver que pasa**

Run: `PYTHONPATH=prototipo python3 -m unittest meta.tests.test_meta.TestCatalogo -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add prototipo/meta/catalogo_app.py prototipo/meta/tests/test_meta.py
git commit -m "feat(meta): roles estructurales de entidad (sobre_tipo, tiene_campo, tipo_dato, rol, referencia_a)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 4: Seed — rama Ventas + tipo `venta` + esquema + entidades + registros

**Files:** Modify `prototipo/meta/seed.py`, `prototipo/meta/tests/test_meta.py`

- [ ] **Step 1: Test que falla**

Añadir a `prototipo/meta/tests/test_meta.py`:
```python
class TestSeedVentas(unittest.TestCase):
    def setUp(self):
        self.u = seed.build_universe()

    def test_menu_principal_incluye_ventas(self):
        opts = [f.value.label for f in self.u.facts_about(self.u.ind("menu_principal"))
                if f.role == "tiene_opcion"]
        self.assertIn("Ventas", opts)

    def test_esquema_venta_cuatro_campos(self):
        campos = [f.value for f in self.u.facts_about(self.u.ind("venta"))
                  if f.role == "tiene_campo"]
        roles = set()
        for c in campos:
            rol = [f.value for f in self.u.facts_about(c) if f.role == "rol"][0]
            roles.add(rol.id)
        self.assertEqual(roles, {"fecha", "cliente", "producto", "monto"})

    def test_cliente_es_agente_Q_clasificado(self):
        ana = self.u.ind("ana")
        self.assertEqual(ana.axis, Axis.Q)
        tipos = [f.value.id for f in self.u.facts_about(ana) if f.role == "instancia_de"]
        self.assertIn("cliente", tipos)

    def test_hay_registros_de_ejemplo(self):
        ventas = [f.subject for f in self.u.facts_with_value(self.u.ind("venta"))
                  if f.role == "instancia_de"]
        self.assertGreaterEqual(len(ventas), 2)
```

- [ ] **Step 2: Correr y ver que falla**

Run: `PYTHONPATH=prototipo python3 -m unittest meta.tests.test_meta.TestSeedVentas -v`
Expected: FAIL (`self.u.ind("venta")` lanza KeyError — aún no existe).

- [ ] **Step 3: Ampliar `seed.build_universe`**

En `prototipo/meta/seed.py`: añadir `time_point` al import de `wq`:
```python
from wq import Universe, Individual, Axis, time_point
```
(si ya importa de wq, agrega `time_point` a esa línea).

Dentro de `build_universe`, **antes de `return u`**, y reusando los helpers `_k/_o/_n` y los individuos ya creados (`t_menu`, `t_opcion`, `m_main`, `v_volver`, `v_sub`):
```python
    # --- Rama Ventas (permanente) ---
    v_form = _k("abrir_formulario"); v_grilla = _k("abrir_grilla")

    # tipo de entidad + meta-tipo de campo + tipos de dato (K)
    venta = _k("venta", "Venta"); campo = _k("campo")
    t_texto = _k("texto"); t_numero = _k("numero"); t_fecha = _k("fecha")
    t_ref = _k("referencia")
    k_cliente = _k("cliente"); k_producto = _k("producto")  # tipos de entidad

    # esquema de venta: 4 campos (descriptores O)
    def _campo(cid, etiqueta, tipo_k, orden, rol_k, ref_k=None):
        c = _o(cid, etiqueta)
        u.assert_fact(c, "instancia_de", campo)
        u.assert_fact(venta, "tiene_campo", c)
        u.assert_fact(c, "tipo_dato", tipo_k)
        u.assert_fact(c, "orden", _n(orden))
        u.assert_fact(c, "rol", rol_k)
        if ref_k is not None:
            u.assert_fact(c, "referencia_a", ref_k)
        return c
    _campo("campo_fecha",    "Fecha",    t_fecha,  1, t_fecha)
    _campo("campo_cliente",  "Cliente",  t_ref,    2, k_cliente, k_cliente)
    _campo("campo_producto", "Producto", t_ref,    3, k_producto, k_producto)
    _campo("campo_monto",    "Monto",    t_numero, 4, _k("monto"))

    # entidades compartidas: clientes en Q, productos en O (instancia_de via V→K)
    ana = Individual(id="ana", axis=Axis.Q, label="Ana")
    beto = Individual(id="beto", axis=Axis.Q, label="Beto")
    laptop = _o("laptop", "Laptop"); mouse = _o("mouse", "Mouse")
    for ent, tipo in [(ana, k_cliente), (beto, k_cliente),
                      (laptop, k_producto), (mouse, k_producto)]:
        u.assert_fact(ent, "instancia_de", tipo)

    # registros de ejemplo
    def _venta(vid, fecha_iso, cli, prod, monto):
        r = _o(vid, vid)
        u.assert_fact(r, "instancia_de", venta)
        u.assert_fact(r, "fecha", time_point(fecha_iso))
        u.assert_fact(r, "cliente", cli)
        u.assert_fact(r, "producto", prod)
        u.assert_fact(r, "monto", _n(monto))
    _venta("venta_001", "2026-06-01", ana, laptop, 120)
    _venta("venta_002", "2026-06-02", beto, mouse, 25)

    # opción "Ventas" en el menú principal + submenú
    m_ventas = _o("menu_ventas", "Ventas")
    opt_ventas = _o("opt_ventas", "Ventas"); acc_abrir_ventas = _o("acc_abrir_ventas")
    u.assert_fact(opt_ventas, "instancia_de", t_opcion)
    u.assert_fact(m_main, "tiene_opcion", opt_ventas)
    u.assert_fact(opt_ventas, "orden", _n(2.5))   # entre Configuración(2) y Salir(3)
    u.assert_fact(opt_ventas, "tiene_accion", acc_abrir_ventas)
    u.assert_fact(acc_abrir_ventas, "instancia_de", v_sub)
    u.assert_fact(acc_abrir_ventas, "submenu_destino", m_ventas)
    u.assert_fact(m_ventas, "instancia_de", t_menu)

    opt_reg = _o("opt_registro", "Registro"); acc_reg = _o("acc_registro")
    opt_con = _o("opt_consulta", "Consulta"); acc_con = _o("acc_consulta")
    opt_volv = _o("opt_volver_ventas", "Volver"); acc_volv = _o("acc_volver_ventas")
    for o in (opt_reg, opt_con, opt_volv):
        u.assert_fact(o, "instancia_de", t_opcion)
    for o, n in ((opt_reg, 1), (opt_con, 2), (opt_volv, 3)):
        u.assert_fact(m_ventas, "tiene_opcion", o)
        u.assert_fact(o, "orden", _n(n))
    u.assert_fact(opt_reg, "tiene_accion", acc_reg)
    u.assert_fact(acc_reg, "instancia_de", v_form)
    u.assert_fact(acc_reg, "sobre_tipo", venta)
    u.assert_fact(opt_con, "tiene_accion", acc_con)
    u.assert_fact(acc_con, "instancia_de", v_grilla)
    u.assert_fact(acc_con, "sobre_tipo", venta)
    u.assert_fact(opt_volv, "tiene_accion", acc_volv)
    u.assert_fact(acc_volv, "instancia_de", v_volver)
```
(Ventas queda en `orden 2.5`, entre Configuración y Salir; no hace falta tocar el orden de las opciones existentes.)

- [ ] **Step 4: Correr y ver que pasa**

Run: `PYTHONPATH=prototipo python3 -m unittest meta.tests.test_meta.TestSeedVentas -v`
Expected: PASS (4 tests). (Si `cliente`/`producto` no validaran, es por el ajuste Task 1 — `instancia_de` V→K; confirma que Task 1 está hecha.)

- [ ] **Step 5: Commit**

```bash
git add prototipo/meta/seed.py prototipo/meta/tests/test_meta.py
git commit -m "feat(meta): seed con Ventas + tipo venta (esquema y registros como datos, entidades compartidas)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 5: Motor — lectores, `guardar`, handlers form/grilla

**Files:** Modify `prototipo/meta/engine.py`, `prototipo/meta/runtime.py` (reexport), `prototipo/meta/tests/test_meta.py`

- [ ] **Step 1: Tests que fallan**

Añadir a `prototipo/meta/tests/test_meta.py`:
```python
from meta import engine as _engine


class TestEntidad(unittest.TestCase):
    def setUp(self):
        self.u = seed.build_universe()

    def test_campos_ordenados(self):
        campos = _engine._campos(self.u, self.u.ind("venta"))
        self.assertEqual([c["rol"] for c in campos],
                         ["fecha", "cliente", "producto", "monto"])
        self.assertEqual(campos[1]["tipo"], "referencia")
        self.assertEqual(campos[1]["referencia_a"], "cliente")

    def test_opciones_ref_lista_clientes(self):
        ops = _engine._opciones_ref(self.u, "cliente")
        self.assertEqual({o["id"] for o in ops}, {"ana", "beto"})

    def test_efecto_grilla_tiene_filas_legibles(self):
        ef = _engine.efecto_grilla(self.u, self.u.ind("venta"), "Consulta")
        self.assertEqual(ef["tipo"], "grilla")
        self.assertEqual({c["rol"] for c in ef["columnas"]},
                         {"fecha", "cliente", "producto", "monto"})
        fila = next(f for f in ef["filas"] if f["id"] == "venta_001")
        self.assertEqual(fila["valores"]["cliente"], "Ana")
        self.assertEqual(fila["valores"]["producto"], "Laptop")

    def test_guardar_crea_y_comparte_referencia(self):
        rid = _engine.guardar(self.u, "venta",
                              {"fecha": "2026-06-03", "cliente": "ana",
                               "producto": "mouse", "monto": "300"})
        # el cliente referenciado es el MISMO individuo ana (compartido)
        cli = [f.value for f in self.u.facts_about(self.u.ind(rid))
               if f.role == "cliente"][-1]
        self.assertEqual(cli.id, "ana")
        self.assertEqual(cli.axis, Axis.Q)

    def test_guardar_actualiza_ultimo_gana(self):
        _engine.guardar(self.u, "venta", {"monto": "999"}, registro_id="venta_001")
        ef = _engine.efecto_grilla(self.u, self.u.ind("venta"), "Consulta")
        fila = next(f for f in ef["filas"] if f["id"] == "venta_001")
        self.assertEqual(fila["valores"]["monto"], "999")

    def test_efecto_formulario_precargado(self):
        ef = _engine.efecto_formulario(self.u, self.u.ind("venta"), "Editar",
                                       registro_id="venta_001")
        self.assertEqual(ef["valores"]["cliente"], "ana")   # id para el select
        self.assertEqual(ef["valores"]["monto"], 120)
        campo_cli = next(c for c in ef["campos"] if c["rol"] == "cliente")
        self.assertIn({"id": "ana", "label": "Ana"}, campo_cli["opciones"])
```

- [ ] **Step 2: Correr y ver que falla**

Run: `PYTHONPATH=prototipo python3 -m unittest meta.tests.test_meta.TestEntidad -v`
Expected: FAIL (`_engine._campos` no existe).

- [ ] **Step 3: Añadir lectores, `guardar`, efectos y handlers en `engine.py`**

En `prototipo/meta/engine.py`, añadir el import al tope:
```python
from wq import Individual, Axis, mint_id, time_point
```
Añadir estos lectores/funciones (después de `_opciones`):
```python
def _ultimo(u, subj, rol):
    vals = [f.value for f in u.facts_about(subj) if f.role == rol]
    return vals[-1] if vals else None


def _campos(u, tipo):
    campos = sorted(_valores(u, tipo, "tiene_campo"), key=lambda c: _orden(u, c))
    out = []
    for c in campos:
        td = _uno(u, c, "tipo_dato")
        rol = _uno(u, c, "rol")
        ref = _uno(u, c, "referencia_a")
        out.append({
            "campo": c.id,
            "rol": rol.id if rol is not None else c.id,
            "etiqueta": c.label,
            "tipo": td.id if td is not None else "texto",
            "orden": _orden(u, c),
            "referencia_a": ref.id if ref is not None else None,
        })
    return out


def _instancias(u, tipo):
    return [f.subject for f in u.facts_with_value(tipo) if f.role == "instancia_de"]


def _opciones_ref(u, tipo_id):
    return [{"id": o.id, "label": o.label} for o in _instancias(u, u.ind(tipo_id))]


def _valor_display(u, reg, rol):
    v = _ultimo(u, reg, rol)
    return v.label if v is not None else ""


def _valor_raw(u, reg, campo):
    v = _ultimo(u, reg, campo["rol"])
    if v is None:
        return ""
    if campo["tipo"] == "referencia":
        return v.id
    if campo["tipo"] == "numero":
        return (v.payload or {}).get("value", v.label)
    return v.label  # fecha (iso) / texto


def efecto_formulario(u, tipo, titulo, registro_id=None):
    campos = _campos(u, tipo)
    for c in campos:
        if c["tipo"] == "referencia" and c["referencia_a"]:
            c["opciones"] = _opciones_ref(u, c["referencia_a"])
    valores = {}
    if registro_id:
        reg = u.ind(registro_id)
        for c in campos:
            valores[c["rol"]] = _valor_raw(u, reg, c)
    return {"tipo": "formulario", "titulo": titulo, "entidad": tipo.id,
            "campos": campos, "registro_id": registro_id, "valores": valores}


def efecto_grilla(u, tipo, titulo):
    campos = _campos(u, tipo)
    columnas = [{"rol": c["rol"], "etiqueta": c["etiqueta"]} for c in campos]
    filas = []
    for reg in _instancias(u, tipo):
        valores = {c["rol"]: _valor_display(u, reg, c["rol"]) for c in campos}
        filas.append({"id": reg.id, "valores": valores})
    return {"tipo": "grilla", "titulo": titulo, "entidad": tipo.id,
            "columnas": columnas, "filas": filas}


def guardar(u, tipo_id, valores, registro_id=None):
    tipo = u.ind(tipo_id)
    campos = _campos(u, tipo)
    if registro_id:
        reg = u.ind(registro_id)
    else:
        reg = Individual(id=mint_id(tipo_id), axis=Axis.O, label=f"{tipo_id} nuevo")
        u.assert_fact(reg, "instancia_de", tipo)
    for c in campos:
        raw = valores.get(c["rol"])
        if raw is None or raw == "":
            continue
        if c["tipo"] == "referencia":
            valor = u.ind(raw)                       # individuo existente (compartido)
        elif c["tipo"] == "numero":
            valor = Individual(id=mint_id("n"), axis=Axis.N, label=str(raw),
                               payload={"value": float(raw)})
        elif c["tipo"] == "fecha":
            valor = time_point(str(raw))
        else:
            valor = Individual(id=mint_id("k"), axis=Axis.K, label=str(raw))
        u.assert_fact(reg, c["rol"], valor)
    return reg.id


def _h_abrir_formulario(sess, accion):
    tipo = _uno(sess.u, accion, "sobre_tipo")
    return efecto_formulario(sess.u, tipo, None)


def _h_abrir_grilla(sess, accion):
    tipo = _uno(sess.u, accion, "sobre_tipo")
    return efecto_grilla(sess.u, tipo, None)
```
Registrar los handlers en `_DISPATCH`:
```python
_DISPATCH = {
    "mostrar_texto": _h_mostrar_texto,
    "abrir_submenu": _h_abrir_submenu,
    "volver": _h_volver,
    "salir": _h_salir,
    "abrir_formulario": _h_abrir_formulario,
    "abrir_grilla": _h_abrir_grilla,
}
```
Y en `MenuSession.seleccionar`, donde hoy hace `efecto = handler(self, accion)` y devuelve, poner el título de la opción en los efectos de ventana:
```python
        efecto = handler(self, accion)
        if efecto.get("tipo") in ("formulario", "grilla"):
            efecto["titulo"] = opcion.label
        return {"efecto": efecto, "estado": self.estado()}
```
(Reemplaza la línea `efecto = handler(self, accion)` + el `return` por este bloque; `opcion` ya está en scope en `seleccionar`.)

En `prototipo/meta/runtime.py`, añadir los nuevos nombres a la reexportación (la línea `from .engine import ...`), agregando `guardar, efecto_formulario, efecto_grilla` para que estén disponibles si algún consumidor los usa vía runtime (no rompe nada):
```python
from .engine import (MenuSession, _valores, _uno, _orden, _opciones,  # noqa: F401
                     guardar, efecto_formulario, efecto_grilla)
```

- [ ] **Step 4: Correr `TestEntidad` y TODA la suite meta**

Run: `PYTHONPATH=prototipo python3 -m unittest meta.tests.test_meta -v`
Expected: PASS — todos (los previos + `TestSeedVentas` + `TestEntidad`). Los efectos `formulario`/`grilla` que devuelve el handler llevan `titulo=None`; lo llena `seleccionar`.

- [ ] **Step 5: Commit**

```bash
git add prototipo/meta/engine.py prototipo/meta/runtime.py prototipo/meta/tests/test_meta.py
git commit -m "feat(meta): primitivas abrir_formulario/abrir_grilla + guardar (genéricas, leen esquema del grafo)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 6: API — `/api/abrir_formulario` y `/api/guardar` (escribe + persiste)

**Files:** Modify `prototipo/meta/web/server.py`, `prototipo/meta/tests/test_web.py`

- [ ] **Step 1: Tests que fallan**

Añadir a `prototipo/meta/tests/test_web.py` (en `class TestWebAPI`, antes de `if __name__`):
```python
    def test_guardar_crea_y_persiste(self):
        import sqlite3
        d = self._post("/api/guardar", {"entidad": "venta",
                                        "valores": {"fecha": "2026-06-09", "cliente": "ana",
                                                    "producto": "mouse", "monto": "77"}})
        self.assertTrue(d["ok"])
        rid = d["registro_id"]
        # persistido en la db del server
        conn = sqlite3.connect(self.db)
        n = conn.execute("SELECT COUNT(*) FROM hechos WHERE sujeto=? AND rol='monto'",
                         (rid,)).fetchone()[0]
        conn.close()
        self.assertGreaterEqual(n, 1)

    def test_abrir_formulario_precargado(self):
        d = self._post("/api/abrir_formulario", {"entidad": "venta",
                                                 "registro_id": "venta_001"})
        ef = d["efecto"]
        self.assertEqual(ef["tipo"], "formulario")
        self.assertEqual(ef["valores"]["cliente"], "ana")

    def test_guardar_body_malformado_400(self):
        req = urllib.request.Request(self._url("/api/guardar"), data=b"{}",
                                     headers={"Content-Type": "application/json"},
                                     method="POST")
        with self.assertRaises(urllib.error.HTTPError) as cm:
            urllib.request.urlopen(req)
        self.assertEqual(cm.exception.code, 400)
```

- [ ] **Step 2: Correr y ver que falla**

Run: `PYTHONPATH=prototipo python3 -m unittest meta.tests.test_web.TestWebAPI.test_abrir_formulario_precargado -v`
Expected: FAIL (HTTP 404 — endpoint no existe).

- [ ] **Step 3: Añadir endpoints + persistencia en `server.py`**

En `prototipo/meta/web/server.py`, añadir al tope: `import sqlite3` y `from .. import storage`. En `crear_servidor`, guardar el `db_path` en `estado`:
```python
def crear_servidor(db_path, host="127.0.0.1", port=8000):
    conn, u = abrir_universo(db_path)
    conn.close()
    estado = {"universe": u, "sesion": MenuSession(u), "db_path": db_path}
    httpd = HTTPServer((host, port), crear_handler(estado))
    return httpd, estado
```
En `do_POST`, añadir las dos ramas (dentro del `if/elif` existente, antes del `else: send_error(404)`):
```python
            elif self.path == "/api/abrir_formulario":
                try:
                    datos = json.loads(raw or b"{}")
                    entidad = datos["entidad"]
                    registro_id = datos.get("registro_id")
                except (KeyError, ValueError, TypeError, json.JSONDecodeError):
                    self._enviar_json({"error": "datos inválidos"}, 400)
                    return
                from ..engine import efecto_formulario
                u = estado["universe"]
                tipo = u.ind(entidad)
                ef = efecto_formulario(u, tipo, "Editar " + (tipo.label or entidad),
                                       registro_id)
                self._enviar_json({"efecto": ef})
            elif self.path == "/api/guardar":
                try:
                    datos = json.loads(raw or b"{}")
                    entidad = datos["entidad"]
                    valores = datos["valores"]
                except (KeyError, ValueError, TypeError, json.JSONDecodeError):
                    self._enviar_json({"error": "datos inválidos"}, 400)
                    return
                from ..engine import guardar
                u = estado["universe"]
                rid = guardar(u, entidad, valores, datos.get("registro_id"))
                conn = sqlite3.connect(estado["db_path"])
                storage.save(u, conn)
                conn.close()
                self._enviar_json({"ok": True, "registro_id": rid})
```

- [ ] **Step 4: Correr la suite web**

Run: `PYTHONPATH=prototipo python3 -m unittest meta.tests.test_web -v`
Expected: PASS — los previos + los 3 nuevos.

- [ ] **Step 5: Commit**

```bash
git add prototipo/meta/web/server.py prototipo/meta/tests/test_web.py
git commit -m "feat(meta-web): endpoints abrir_formulario y guardar (escribe + persiste a wq.db)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 7: Frontend — ventana modal con form y grilla

**Files:** Modify `prototipo/meta/web/static/index.html`, `app.js`, `style.css`

- [ ] **Step 1: `index.html` — añadir la ventana modal**

En `prototipo/meta/web/static/index.html`, antes de `<script src="/static/app.js">`, añadir:
```html
  <div id="ventana" class="oculto">
    <div class="ventana-card">
      <div class="ventana-titulo"></div>
      <div class="ventana-cuerpo"></div>
      <div class="ventana-pie"></div>
    </div>
  </div>
```

- [ ] **Step 2: `app.js` — manejar efectos formulario/grilla + ventana**

En `prototipo/meta/web/static/app.js`, en `onSeleccion`, añadir las ramas (dentro del bloque de tipos de efecto):
```javascript
  } else if (ef.tipo === "formulario") {
    abrirVentanaForm(ef); aplicar(data);
  } else if (ef.tipo === "grilla") {
    abrirVentanaGrilla(ef); aplicar(data);
```
Y añadir al final del archivo (antes de `cargar()`):
```javascript
function cerrarVentana() { $("#ventana").classList.add("oculto"); }

function abrirVentanaForm(ef) {
  $(".ventana-titulo").textContent = ef.titulo || "Registro";
  const cuerpo = $(".ventana-cuerpo");
  cuerpo.innerHTML = "";
  for (const c of ef.campos) {
    const fila = document.createElement("div");
    fila.className = "campo";
    const lab = document.createElement("label");
    lab.textContent = c.etiqueta;
    let input;
    if (c.tipo === "referencia") {
      input = document.createElement("select");
      for (const o of (c.opciones || [])) {
        const opt = document.createElement("option");
        opt.value = o.id;
        opt.textContent = o.label;
        if (String(ef.valores[c.rol]) === String(o.id)) opt.selected = true;
        input.appendChild(opt);
      }
    } else {
      input = document.createElement("input");
      input.type = c.tipo === "numero" ? "number" : c.tipo === "fecha" ? "date" : "text";
      if (ef.valores[c.rol] != null) input.value = ef.valores[c.rol];
    }
    input.dataset.rol = c.rol;
    fila.appendChild(lab);
    fila.appendChild(input);
    cuerpo.appendChild(fila);
  }
  const pie = $(".ventana-pie");
  pie.innerHTML = "";
  const bGuardar = document.createElement("button");
  bGuardar.textContent = "Guardar";
  bGuardar.onclick = async () => {
    const valores = {};
    cuerpo.querySelectorAll("[data-rol]").forEach(el => { valores[el.dataset.rol] = el.value; });
    try {
      await fetch("/api/guardar", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ entidad: ef.entidad, valores, registro_id: ef.registro_id }),
      });
      cerrarVentana();
      mostrarSalida("Guardado.");
    } catch (e) { mostrarError(); }
  };
  const bCerrar = document.createElement("button");
  bCerrar.textContent = "Cerrar";
  bCerrar.className = "secundario";
  bCerrar.onclick = cerrarVentana;
  pie.appendChild(bGuardar);
  pie.appendChild(bCerrar);
  $("#ventana").classList.remove("oculto");
}

function abrirVentanaGrilla(ef) {
  $(".ventana-titulo").textContent = ef.titulo || "Consulta";
  const cuerpo = $(".ventana-cuerpo");
  cuerpo.innerHTML = "";
  const tabla = document.createElement("table");
  tabla.className = "grilla";
  const cab = document.createElement("tr");
  for (const col of ef.columnas) {
    const th = document.createElement("th");
    th.textContent = col.etiqueta;
    cab.appendChild(th);
  }
  tabla.appendChild(cab);
  for (const f of ef.filas) {
    const tr = document.createElement("tr");
    tr.className = "fila-click";
    for (const col of ef.columnas) {
      const td = document.createElement("td");
      td.textContent = f.valores[col.rol] || "";
      tr.appendChild(td);
    }
    tr.onclick = async () => {
      try {
        const r = await fetch("/api/abrir_formulario", {
          method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ entidad: ef.entidad, registro_id: f.id }),
        });
        const d = await r.json();
        abrirVentanaForm(d.efecto);
      } catch (e) { mostrarError(); }
    };
    tabla.appendChild(tr);
  }
  cuerpo.appendChild(tabla);
  const pie = $(".ventana-pie");
  pie.innerHTML = "";
  const bCerrar = document.createElement("button");
  bCerrar.textContent = "Cerrar";
  bCerrar.className = "secundario";
  bCerrar.onclick = cerrarVentana;
  pie.appendChild(bCerrar);
  $("#ventana").classList.remove("oculto");
}
```
Verifica que existan helpers `mostrarSalida` y `mostrarError`. Si en el `app.js` actual el texto se muestra con código inline (no funciones), añade arriba estos helpers y úsalos:
```javascript
function mostrarSalida(t) { const s = $("#salida"); s.textContent = t; s.classList.remove("oculto"); }
function mostrarError() { mostrarSalida("Error de comunicación con el servidor."); }
```
(Si ya hay equivalentes, reúsalos y no dupliques.)

- [ ] **Step 3: `style.css` — estilos de la ventana (con el fix de especificidad)**

En `prototipo/meta/web/static/style.css`, añadir al final:
```css
#ventana { position:fixed; inset:0; background:rgba(15,23,42,.55); display:flex; align-items:center; justify-content:center; }
#ventana.oculto { display:none; }
.ventana-card { background:#fff; border-radius:12px; padding:22px 26px; min-width:380px; max-width:90vw; max-height:85vh; overflow:auto; }
.ventana-titulo { font-size:17px; font-weight:700; color:var(--azul); margin-bottom:14px; }
.campo { display:flex; flex-direction:column; margin:10px 0; }
.campo label { font-size:12px; color:var(--gris); margin-bottom:4px; }
.campo input, .campo select { padding:8px 10px; border:1px solid #cbd5e1; border-radius:6px; font-size:14px; }
.ventana-pie { margin-top:18px; display:flex; gap:10px; justify-content:flex-end; }
.ventana-pie button { padding:9px 18px; font-size:14px; background:var(--azul2); color:#fff; border:none; border-radius:8px; cursor:pointer; }
.ventana-pie button.secundario { background:#e5e7eb; color:#374151; }
table.grilla { border-collapse:collapse; width:100%; }
table.grilla th, table.grilla td { border:1px solid #e5e7eb; padding:7px 12px; text-align:left; font-size:13px; }
table.grilla th { background:#f1f5f9; }
tr.fila-click { cursor:pointer; }
tr.fila-click:hover td { background:#eff6ff; }
```

- [ ] **Step 4: Smoke visual (grilla y form)**

Run (arranca server con wq.db ya sembrado de la Task 4/2; reinícialo limpio):
```bash
rm -f prototipo/meta/wq.db
PYTHONPATH=prototipo python3 -c "
import os
from meta.web.server import crear_servidor
httpd,_ = crear_servidor(os.path.join('prototipo','meta','wq.db'),'127.0.0.1',8000)
httpd.serve_forever()
" > /tmp/w.log 2>&1 &
SRV=$!; sleep 2
# navegar la sesión a la grilla de Ventas → Consulta antes de capturar
curl -s -X POST -H "Content-Type: application/json" -d '{"indice":3}' http://127.0.0.1:8000/api/seleccionar >/dev/null   # Ventas
curl -s -X POST -H "Content-Type: application/json" -d '{"indice":2}' http://127.0.0.1:8000/api/seleccionar >/dev/null   # Consulta
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu --hide-scrollbars --virtual-time-budget=4000 --window-size=1200,860 --screenshot=/tmp/ventas_grilla.png http://127.0.0.1:8000/ 2>/dev/null
kill $SRV 2>/dev/null
ls -l /tmp/ventas_grilla.png
```
Expected: `/tmp/ventas_grilla.png` > 0 bytes; la imagen muestra la ventana "Consulta" con la grilla (columnas Fecha/Cliente/Producto/Monto, filas Ana/Beto). (La sesión queda navegada a la grilla, así que la página la abre directo.)

- [ ] **Step 5: Commit**

```bash
git add prototipo/meta/web/static/
git commit -m "feat(meta-web): ventana modal con form (selects de referencia) y grilla (click→editar)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 8: Sync del anexo del libro (`instancia_de` V→K)

**Files:** Modify `libro/manuscrito/29_anexo_prototipo.md`

- [ ] **Step 1: Actualizar el listado de `axes.py` y la signatura de `instancia_de`**

En `libro/manuscrito/29_anexo_prototipo.md`:
- En el bloque de `axes.py` (§A1), añadir la línea del enum `Axis`:
  ```python
      M = "M"  # cómo / predicados (modus)
  ```
  → añadir debajo:
  ```python
      V = "V"  # comodín de signatura: cualquier eje de valor
  ```
- En el listado del catálogo (§ donde aparece `RoleSignature("instancia_de", Axis.O, Axis.K, ...)`), cambiar `Axis.O` por `Axis.V` y el texto a "sujeto (cualquier eje de valor) pertenece a la categoría", para reflejar el código.

(Buscar con: `grep -n "instancia_de" libro/manuscrito/29_anexo_prototipo.md`.)

- [ ] **Step 2: Verificar coherencia**

Run: `grep -n "instancia_de\|V =" libro/manuscrito/29_anexo_prototipo.md | head`
Expected: el anexo muestra `Axis.V` en `instancia_de` y la línea `V = "V"` en el enum.

- [ ] **Step 3: Commit**

```bash
git add libro/manuscrito/29_anexo_prototipo.md
git commit -m "docs(libro): sync del anexo — instancia_de V→K y Axis.V

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Verificación final

- [ ] **Suites completas**

Run: `PYTHONPATH=prototipo python3 -m unittest discover -s prototipo/tests -q && PYTHONPATH=prototipo python3 -m unittest meta.tests.test_meta meta.tests.test_web -q`
Expected: ambos OK. `wq`: 23. `meta`: los previos + `TestSeedVentas` (4) + `TestEntidad` (6); `web`: los previos + 3.

- [ ] **Flujo end-to-end por API (crear → aparece en la grilla, persiste)**

Run:
```bash
rm -f prototipo/meta/wq.db
PYTHONPATH=prototipo python3 -c "
import os
from meta.web.server import crear_servidor
httpd,_ = crear_servidor(os.path.join('prototipo','meta','wq.db'),'127.0.0.1',8000)
httpd.serve_forever()" > /tmp/w.log 2>&1 &
SRV=$!; sleep 2
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"entidad":"venta","valores":{"fecha":"2026-06-10","cliente":"beto","producto":"laptop","monto":"450"}}' \
  http://127.0.0.1:8000/api/guardar
echo
# la grilla ahora debe tener 3 filas
curl -s -X POST -H "Content-Type: application/json" -d '{"indice":3}' http://127.0.0.1:8000/api/seleccionar >/dev/null
curl -s -X POST -H "Content-Type: application/json" -d '{"indice":2}' http://127.0.0.1:8000/api/seleccionar | python3 -c "import sys,json; print('filas:', len(json.load(sys.stdin)['efecto']['filas']))"
kill $SRV 2>/dev/null
```
Expected: `{"ok": true, "registro_id": "..."}`; `filas: 3`. (Y `wq.db` quedó con la venta nueva → persistió.)
