# El catálogo como dato — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Derivar la firma (signatura) de cada campo del esquema desde sus propios datos y registrarla en el catálogo, de modo que los campos dinámicos se validen como los roles canónicos; y surfacing limpio (400) de las violaciones.

**Architecture:** Un post-pass `registrar_firmas_de_esquema(u)` recorre los `campo` del grafo, deriva `(dominio, rango)` de `eje_instancia`/`tipo_dato`/`referencia_a`, y registra cada rol nuevo en el catálogo (omite los ya canónicos). Se llama al finalizar el universo. Los endpoints de escritura mapean las excepciones de dominio a 400.

**Tech Stack:** Python 3.9 stdlib, librería `wq`, `unittest` (NO pytest), `PYTHONPATH=prototipo`. Rama `main`.

**Spec:** `docs/superpowers/specs/2026-06-05-catalogo-como-dato-design.md`

**Entorno:** comandos desde `/Users/joseabanto/WQuestions` con `PYTHONPATH=prototipo`.

---

## File Structure

| Archivo | Cambio |
|---|---|
| `prototipo/meta/catalogo_app.py` | MOD: función `registrar_firmas_de_esquema(u)`. |
| `prototipo/meta/seed.py` | MOD: llamarla al final de `build_universe` y tras la carga en `abrir_universo`. |
| `prototipo/meta/web/server.py` | MOD: endpoints `/api/guardar` y `/api/abrir_formulario` → 400 ante SignatureError/ValueError/KeyError. |
| `prototipo/meta/tests/test_meta.py` | MOD: tests de derivación de firmas. |
| `prototipo/meta/tests/test_web.py` | MOD: tests de surfacing 400. |

---

## Task 1: Derivar y registrar las firmas del esquema

**Files:** Modify `prototipo/meta/catalogo_app.py`, `prototipo/meta/seed.py`, `prototipo/meta/tests/test_meta.py`

- [ ] **Step 1: Tests que fallan**

Añadir a `prototipo/meta/tests/test_meta.py`:
```python
class TestCatalogoComoDato(unittest.TestCase):
    def setUp(self):
        self.u = seed.build_universe()
        self.cat = self.u.catalog

    def test_firmas_de_campos_nuevos_registradas(self):
        self.assertEqual((self.cat.get("precio").domain, self.cat.get("precio").range),
                         (Axis.O, Axis.N))
        self.assertEqual((self.cat.get("fecha").domain, self.cat.get("fecha").range),
                         (Axis.O, Axis.T))
        self.assertEqual((self.cat.get("nombre_producto").domain, self.cat.get("nombre_producto").range),
                         (Axis.O, Axis.K))

    def test_referencia_deriva_rango_del_eje_apuntado(self):
        # proveedor → persona (Q); producto-como-rol → producto (O)
        self.assertEqual(self.cat.get("proveedor").range, Axis.Q)
        self.assertEqual(self.cat.get("producto").range, Axis.O)

    def test_no_sobrescribe_roles_canonicos(self):
        # cliente y monto siguen siendo los canónicos (O→Q, O→N)
        self.assertEqual(self.cat.get("cliente").range, Axis.Q)
        self.assertEqual(self.cat.get("monto").range, Axis.N)

    def test_universo_minimo_sin_campo_no_rompe(self):
        from wq import Universe
        from meta.catalogo_app import build_catalog, registrar_firmas_de_esquema
        u = Universe(catalog=build_catalog())
        registrar_firmas_de_esquema(u)  # no debe lanzar

    def test_campo_agregado_en_vivo_se_tipa(self):
        from wq import Individual, Axis as A
        from meta.catalogo_app import registrar_firmas_de_esquema
        u = self.u
        c = Individual(id="campo_x_doc", axis=A.O, label="Doc"); u.add_individual(c)
        rol = Individual(id="doc_rol", axis=A.K, label="doc_rol"); u.add_individual(rol)
        u.assert_fact(c, "instancia_de", u.ind("campo"))
        u.assert_fact(u.ind("venta"), "tiene_campo", c)
        u.assert_fact(c, "tipo_dato", u.ind("texto"))
        u.assert_fact(c, "rol", rol)
        registrar_firmas_de_esquema(u)
        self.assertEqual((u.catalog.get("doc_rol").domain, u.catalog.get("doc_rol").range),
                         (A.O, A.K))
```

- [ ] **Step 2: Correr y ver que fallan**

Run: `PYTHONPATH=prototipo python3 -m unittest meta.tests.test_meta.TestCatalogoComoDato -v`
Expected: FAIL (`registrar_firmas_de_esquema` no existe / `cat.get("precio")` es None).

- [ ] **Step 3: Implementar `registrar_firmas_de_esquema`**

En `prototipo/meta/catalogo_app.py` (ya importa `Axis` y `RoleSignature`), añadir al final del archivo:
```python
def registrar_firmas_de_esquema(u):
    """Deriva y registra en el catálogo la firma de cada campo del esquema.

    dominio = eje_instancia del tipo dueño (default O); rango = de tipo_dato
    (texto→K, numero→N, fecha→T, referencia→eje del referencia_a). Solo registra
    roles que no estén ya en el catálogo (se confía en el núcleo canónico).
    """
    try:
        campo_meta = u.ind("campo")
    except Exception:
        return

    def _uno(subj, rol):
        for f in u.facts_about(subj):
            if f.role == rol:
                return f.value
        return None

    rango_por_tipo = {"texto": Axis.K, "numero": Axis.N, "fecha": Axis.T}
    cat = u.catalog
    campos = [f.subject for f in u.facts_with_value(campo_meta) if f.role == "instancia_de"]
    for c in campos:
        rol = _uno(c, "rol")
        rol_id = rol.id if rol is not None else c.id
        if cat.get(rol_id) is not None:
            continue  # ya tipado (canónico o ya derivado) — se confía en el núcleo
        duenos = [f.subject for f in u.facts_with_value(c) if f.role == "tiene_campo"]
        dom = Axis.O
        if duenos:
            ax = _uno(duenos[0], "eje_instancia")
            if ax is not None:
                dom = Axis(ax.label)
        td = _uno(c, "tipo_dato")
        td_id = td.id if td is not None else "texto"
        if td_id == "referencia":
            ref = _uno(c, "referencia_a")
            rax = _uno(ref, "eje_instancia") if ref is not None else None
            rng = Axis(rax.label) if rax is not None else Axis.O
        else:
            rng = rango_por_tipo.get(td_id, Axis.K)
        cat.register(RoleSignature(rol_id, dom, rng, True, f"campo de esquema ({td_id})"))
```

- [ ] **Step 4: Llamarla al finalizar el universo (seed.py)**

En `prototipo/meta/seed.py`:
- Asegura el import al tope: `from meta.catalogo_app import build_catalog, registrar_firmas_de_esquema` (si ya importa `build_catalog`, añade `registrar_firmas_de_esquema` a esa línea).
- En `build_universe`, **inmediatamente antes de `return u`**, añade:
  ```python
      registrar_firmas_de_esquema(u)
      return u
  ```
- En `abrir_universo`, localiza dónde se obtiene el universo final (la variable que se devuelve, p. ej. `u = storage.load(conn, build_catalog())` o equivalente) y, **antes del `return`**, añade `registrar_firmas_de_esquema(u)` sobre esa variable. Si `abrir_universo` siembra vía `build_universe` y luego recarga de disco, la llamada debe ir sobre el universo **que se devuelve** (el recargado).

- [ ] **Step 5: Correr y ver que pasan**

Run: `PYTHONPATH=prototipo python3 -m unittest meta.tests.test_meta.TestCatalogoComoDato -v`
Expected: PASS (5 tests).

- [ ] **Step 6: Suite meta completa (preservación)**

Run: `PYTHONPATH=prototipo python3 -m unittest meta.tests.test_meta -q`
Expected: OK (los datos sembrados no se re-validan; nada se rompe).

- [ ] **Step 7: Commit**

```bash
git add prototipo/meta/catalogo_app.py prototipo/meta/seed.py prototipo/meta/tests/test_meta.py
git commit -m "feat(meta): derivar y registrar firmas de los campos del esquema (catálogo como dato)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 2: Surfacing de violaciones a 400 en los endpoints de escritura

**Files:** Modify `prototipo/meta/web/server.py`, `prototipo/meta/tests/test_web.py`

- [ ] **Step 1: Tests que fallan**

Añadir a `prototipo/meta/tests/test_web.py` en `class TestWebAPI` (usa el helper `self._post`/`self._url` ya existentes y `urllib.error`):
```python
    def test_guardar_monto_no_numerico_da_400(self):
        req = urllib.request.Request(
            self._url("/api/guardar"),
            data=json.dumps({"entidad": "venta",
                             "valores": {"monto": "abc"}}).encode(),
            headers={"Content-Type": "application/json"}, method="POST")
        with self.assertRaises(urllib.error.HTTPError) as cm:
            urllib.request.urlopen(req)
        self.assertEqual(cm.exception.code, 400)

    def test_guardar_referencia_eje_incorrecto_da_400(self):
        # proveedor está tipado O→Q; pasar un producto (O) viola la firma → 400
        req = urllib.request.Request(
            self._url("/api/guardar"),
            data=json.dumps({"entidad": "compra",
                             "valores": {"proveedor": "laptop"}}).encode(),
            headers={"Content-Type": "application/json"}, method="POST")
        with self.assertRaises(urllib.error.HTTPError) as cm:
            urllib.request.urlopen(req)
        self.assertEqual(cm.exception.code, 400)
```
(Si `test_web.py` no importa `json`, añádelo arriba: `import json`.)

- [ ] **Step 2: Correr y ver que fallan**

Run: `PYTHONPATH=prototipo python3 -m unittest meta.tests.test_web.TestWebAPI.test_guardar_monto_no_numerico_da_400 -v`
Expected: FAIL — hoy una excepción de `guardar` da **500** (HTTPError code 500, no 400).

- [ ] **Step 3: Mapear excepciones de dominio a 400 en `server.py`**

En `prototipo/meta/web/server.py`:
- Añade el import cerca del resto: `from wq import SignatureError`.
- En `do_POST`, en la rama **`/api/guardar`**, envuelve la llamada al motor y la persistencia para que las excepciones de dominio devuelvan 400. La rama debe quedar así (adapta los nombres reales de las variables/imports que ya use el archivo — `estado`, `storage`, `sqlite3`, `_enviar_json`):
  ```python
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
                  try:
                      rid = guardar(u, entidad, valores, datos.get("registro_id"))
                  except (SignatureError, ValueError, KeyError) as e:
                      self._enviar_json({"error": str(e)}, 400)
                      return
                  conn = sqlite3.connect(estado["db_path"])
                  storage.save(u, conn)
                  conn.close()
                  self._enviar_json({"ok": True, "registro_id": rid})
  ```
- En la rama **`/api/abrir_formulario`**, envuelve la construcción del efecto igual:
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
                  try:
                      tipo = u.ind(entidad)
                      ef = efecto_formulario(u, tipo, "Editar " + (tipo.label or entidad), registro_id)
                  except (SignatureError, ValueError, KeyError) as e:
                      self._enviar_json({"error": str(e)}, 400)
                      return
                  self._enviar_json({"efecto": ef})
  ```

- [ ] **Step 4: Correr y ver que pasan**

Run: `PYTHONPATH=prototipo python3 -m unittest meta.tests.test_web -v`
Expected: PASS — los previos + los 2 nuevos (400 en vez de 500).

- [ ] **Step 5: Commit**

```bash
git add prototipo/meta/web/server.py prototipo/meta/tests/test_web.py
git commit -m "feat(meta-web): mapear SignatureError/ValueError/KeyError de escritura a 400

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Verificación final

- [ ] **Suites completas**

Run: `PYTHONPATH=prototipo python3 -m unittest discover -s prototipo/tests -q && PYTHONPATH=prototipo python3 -m unittest meta.tests.test_meta meta.tests.test_web -q`
Expected: ambos OK (wq sin cambios = 23; meta + web con los tests nuevos).

- [ ] **Demostración end-to-end (la validación tipa el dato y rechaza limpio)**

```bash
rm -f prototipo/meta/wq.db
PYTHONPATH=prototipo python3 -c "
import os
from meta.web.server import crear_servidor
httpd,_ = crear_servidor(os.path.join('prototipo','meta','wq.db'),'127.0.0.1',8000)
httpd.serve_forever()" > /tmp/w.log 2>&1 &
SRV=$!; sleep 2
echo "guardar válido (debe ok):"
curl -s -X POST -H "Content-Type: application/json" -d '{"entidad":"producto","valores":{"nombre_producto":"Teclado","precio":"50"}}' http://127.0.0.1:8000/api/guardar
echo; echo "precio no numérico (debe 400):"
curl -s -o /dev/null -w "%{http_code}\n" -X POST -H "Content-Type: application/json" -d '{"entidad":"producto","valores":{"nombre_producto":"X","precio":"abc"}}' http://127.0.0.1:8000/api/guardar
kill $SRV 2>/dev/null
```
Expected: primero `{"ok": true, ...}`; segundo imprime `400`.
