# Segunda mitad: literal de texto + display derivado — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Formalizar el texto libre como literal K marcado y único (B), y computar el display de las entidades referenciadas desde los hechos en vez del `.label` cacheado (C).

**Architecture:** Dos helpers en `engine.py` — `literal_texto(s)` (mint único + `meta.literal`) y `_etiqueta(u, ind)` (resuelve la etiqueta vía `campo_etiqueta`). `guardar` y el seed usan el primero; `_opciones_ref`/`_valor_display` usan el segundo. UI/API sin cambios.

**Tech Stack:** Python 3.9 stdlib, librería `wq`, `unittest` (NO pytest), `PYTHONPATH=prototipo`. Rama `main`.

**Spec:** `docs/superpowers/specs/2026-06-05-segunda-mitad-literal-display-design.md`

**Entorno:** comandos desde `/Users/joseabanto/WQuestions` con `PYTHONPATH=prototipo`.

---

## File Structure

| Archivo | Cambio |
|---|---|
| `prototipo/meta/engine.py` | MOD: `literal_texto`, `_etiqueta`; `guardar` (rama texto), `_opciones_ref`, `_valor_display`. |
| `prototipo/meta/seed.py` | MOD: valores `nombre` usan `literal_texto`. |
| `prototipo/meta/tests/test_meta.py` | MOD: tests de B y C. |

UI (`web/static/*`) y API (`web/server.py`) **no se tocan**.

---

## Task 1: B — Literal de texto (único y marcado)

**Files:** Modify `prototipo/meta/engine.py`, `prototipo/meta/seed.py`, `prototipo/meta/tests/test_meta.py`

- [ ] **Step 1: Tests que fallan**

Añadir a `prototipo/meta/tests/test_meta.py`:
```python
class TestLiteralTexto(unittest.TestCase):
    def test_literal_unico_y_marcado(self):
        from meta.engine import literal_texto
        a = literal_texto("Ana"); b = literal_texto("Ana")
        self.assertNotEqual(a.id, b.id)          # literales independientes
        self.assertEqual(a.label, "Ana")
        self.assertTrue(a.meta.get("literal"))
        self.assertEqual(a.axis, Axis.K)

    def test_seed_nombre_es_literal(self):
        u = seed.build_universe()
        v = [f.value for f in u.facts_about(u.ind("ana")) if f.role == "nombre"][-1]
        self.assertTrue(v.meta.get("literal"))

    def test_guardar_persona_nombre_es_literal(self):
        u = seed.build_universe()
        rid = _engine.guardar(u, "persona", {"nombre": "Zoe"})
        v = [f.value for f in u.facts_about(u.ind(rid)) if f.role == "nombre"][-1]
        self.assertTrue(v.meta.get("literal"))
        self.assertEqual(v.label, "Zoe")
```

- [ ] **Step 2: Correr y ver que fallan**

Run: `PYTHONPATH=prototipo python3 -m unittest meta.tests.test_meta.TestLiteralTexto -v`
Expected: FAIL (`literal_texto` no existe; los valores `nombre` del seed no están marcados).

- [ ] **Step 3: Añadir `literal_texto` y usarlo en `guardar`**

En `prototipo/meta/engine.py` (ya importa `Individual, Axis, mint_id, time_point` de `wq`),
añadir el helper cerca de los otros (p. ej. tras `_ultimo`):
```python
def literal_texto(s):
    """Un literal de texto libre: K minteado y único, marcado como literal.

    Distinto de una categoría controlada (K nombrada y compartida). El texto no
    es un eje; vive en K con su valor en `label` y la marca `meta.literal`.
    """
    return Individual(id=mint_id("txt"), axis=Axis.K, label=str(s), meta={"literal": True})
```
En `guardar`, la rama de texto:
```python
        else:
            valor = Individual(id=mint_id("k"), axis=Axis.K, label=str(raw))
```
cámbiala por:
```python
        else:
            valor = literal_texto(raw)
```

- [ ] **Step 4: Usar `literal_texto` para los valores `nombre` del seed**

En `prototipo/meta/seed.py`:
- Importa el helper: en la línea `from meta.engine import ...` (si existe) añade
  `literal_texto`; si el seed no importa de engine, añade
  `from meta.engine import literal_texto` cerca de los imports del tope.
- Localiza el bloque de entidades maestras y cambia los valores `nombre`/`nombre_producto`
  de `_k(...)` a `literal_texto(...)`:
  ```python
      for p, nom in [(ana, "Ana"), (beto, "Beto")]:
          u.assert_fact(p, "instancia_de", persona)
          u.assert_fact(p, "nombre", _k(nom))
  ```
  →
  ```python
      for p, nom in [(ana, "Ana"), (beto, "Beto")]:
          u.assert_fact(p, "instancia_de", persona)
          u.assert_fact(p, "nombre", literal_texto(nom))
  ```
  y
  ```python
      for pr, nom, pre in [(laptop, "Laptop", 1200), (mouse, "Mouse", 25)]:
          u.assert_fact(pr, "instancia_de", producto)
          u.assert_fact(pr, "nombre_producto", _k(nom))
          u.assert_fact(pr, "precio", _n(pre))
  ```
  →
  ```python
      for pr, nom, pre in [(laptop, "Laptop", 1200), (mouse, "Mouse", 25)]:
          u.assert_fact(pr, "instancia_de", producto)
          u.assert_fact(pr, "nombre_producto", literal_texto(nom))
          u.assert_fact(pr, "precio", _n(pre))
  ```
  (Si los nombres reales de variables/listas difieren, ajústalos; el cambio es: el **valor**
  de `nombre`/`nombre_producto` pasa de `_k(nom)` a `literal_texto(nom)`.)

**Importante (posible import circular):** `seed.py` importa de `engine`, y `engine` NO debe
importar de `seed`. Verifica que `engine.py` no importe `seed` (no lo hace). Si por el orden
de imports hubiera un ciclo, importa `literal_texto` **dentro** de `build_universe`
(`from meta.engine import literal_texto`) en vez de al tope.

- [ ] **Step 5: Correr y ver que pasan**

Run: `PYTHONPATH=prototipo python3 -m unittest meta.tests.test_meta.TestLiteralTexto -v`
Expected: PASS (3 tests).

- [ ] **Step 6: Suite meta completa**

Run: `PYTHONPATH=prototipo python3 -m unittest meta.tests.test_meta -q`
Expected: OK (los displays sólo dependen del `label`, que no cambia).

- [ ] **Step 7: Commit**

```bash
git add prototipo/meta/engine.py prototipo/meta/seed.py prototipo/meta/tests/test_meta.py
git commit -m "feat(meta): texto libre como literal K único y marcado (literal_texto)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 2: C — Display derivado de hechos (`_etiqueta`)

**Files:** Modify `prototipo/meta/engine.py`, `prototipo/meta/tests/test_meta.py`

- [ ] **Step 1: Tests que fallan**

Añadir a `prototipo/meta/tests/test_meta.py`:
```python
class TestDisplayDerivado(unittest.TestCase):
    def setUp(self):
        self.u = seed.build_universe()

    def test_opciones_ref_usa_nombre_vigente(self):
        rid = _engine.guardar(self.u, "persona", {"nombre": "Caro"})
        labels = {o["id"]: o["label"] for o in _engine._opciones_ref(self.u, "persona")}
        self.assertEqual(labels[rid], "Caro")
        _engine.guardar(self.u, "persona", {"nombre": "Carolina"}, registro_id=rid)
        labels = {o["id"]: o["label"] for o in _engine._opciones_ref(self.u, "persona")}
        self.assertEqual(labels[rid], "Carolina")   # display vigente, no el label cacheado

    def test_grilla_cliente_muestra_nombre_vigente(self):
        ef = _engine.efecto_grilla(self.u, self.u.ind("venta"), "Consulta")
        fila = next(f for f in ef["filas"] if f["id"] == "venta_001")
        self.assertEqual(fila["valores"]["cliente"], "Ana")
        self.assertEqual(fila["valores"]["producto"], "Laptop")
```

- [ ] **Step 2: Correr y ver que el primero falla**

Run: `PYTHONPATH=prototipo python3 -m unittest meta.tests.test_meta.TestDisplayDerivado -v`
Expected: `test_opciones_ref_usa_nombre_vigente` FALLA (hoy `_opciones_ref` usa
`individuo.label`, que queda "Caro" tras editar); el segundo pasa.

- [ ] **Step 3: Añadir `_etiqueta` y usarla en los lectores**

En `prototipo/meta/engine.py`, añadir el helper (usa `_uno` y `_ultimo`, ya existentes):
```python
def _etiqueta(u, ind):
    """Etiqueta visible de un individuo, derivada de hechos.

    Si su tipo declara `campo_etiqueta`, devuelve el valor vigente de ese campo
    (no el `.label` cacheado). Si no, cae al `.label`.
    """
    tipo = _uno(u, ind, "instancia_de")
    if tipo is not None:
        campo_etq = _uno(u, tipo, "campo_etiqueta")
        if campo_etq is not None:
            rol = _uno(u, campo_etq, "rol")
            rol_id = rol.id if rol is not None else campo_etq.id
            val = _ultimo(u, ind, rol_id)
            if val is not None:
                return val.label
    return ind.label
```
Reemplazar `_opciones_ref`:
```python
def _opciones_ref(u, tipo_id):
    return [{"id": o.id, "label": o.label} for o in _instancias(u, u.ind(tipo_id))]
```
por:
```python
def _opciones_ref(u, tipo_id):
    return [{"id": o.id, "label": _etiqueta(u, o)} for o in _instancias(u, u.ind(tipo_id))]
```
Y reemplazar `_valor_display`:
```python
def _valor_display(u, reg, rol):
    v = _ultimo(u, reg, rol)
    return v.label if v is not None else ""
```
por:
```python
def _valor_display(u, reg, rol):
    v = _ultimo(u, reg, rol)
    return _etiqueta(u, v) if v is not None else ""
```

- [ ] **Step 4: Correr y ver que pasan**

Run: `PYTHONPATH=prototipo python3 -m unittest meta.tests.test_meta.TestDisplayDerivado -v`
Expected: PASS (2 tests).

- [ ] **Step 5: Suites completas (preservación)**

Run: `PYTHONPATH=prototipo python3 -m unittest meta.tests.test_meta meta.tests.test_web -q`
Expected: OK. Los displays de los datos actuales ("Ana", "Laptop", números, fechas) no
cambian: para literales N/T/K sin tipo con `campo_etiqueta`, `_etiqueta` cae al `.label`.

- [ ] **Step 6: Commit**

```bash
git add prototipo/meta/engine.py prototipo/meta/tests/test_meta.py
git commit -m "feat(meta): display de referencias derivado de hechos (campo_etiqueta), no del label cacheado

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Verificación final

- [ ] **Suites completas**

Run: `PYTHONPATH=prototipo python3 -m unittest discover -s prototipo/tests -q && PYTHONPATH=prototipo python3 -m unittest meta.tests.test_meta meta.tests.test_web -q`
Expected: ambos OK (wq sin cambios = 23; meta + web con los tests nuevos).

- [ ] **Demostración end-to-end (editar un nombre se refleja en el select)**

```bash
rm -f prototipo/meta/wq.db
PYTHONPATH=prototipo python3 -c "
import os
from meta.web.server import crear_servidor
httpd,_ = crear_servidor(os.path.join('prototipo','meta','wq.db'),'127.0.0.1',8000)
httpd.serve_forever()" > /tmp/w.log 2>&1 &
SRV=$!; sleep 2
echo 'alta persona Caro:'
RID=$(curl -s -X POST -H 'Content-Type: application/json' -d '{"entidad":"persona","valores":{"nombre":"Caro"}}' http://127.0.0.1:8000/api/guardar | python3 -c 'import sys,json;print(json.load(sys.stdin)["registro_id"])')
echo "  rid=$RID"
echo 'edito su nombre a Carolina:'
curl -s -X POST -H 'Content-Type: application/json' -d "{\"entidad\":\"persona\",\"valores\":{\"nombre\":\"Carolina\"},\"registro_id\":\"$RID\"}" http://127.0.0.1:8000/api/guardar >/dev/null
echo 'opciones de proveedor en el form de compra (debe decir Carolina, no Caro):'
curl -s -X POST -H 'Content-Type: application/json' -d '{"entidad":"compra","registro_id":null}' http://127.0.0.1:8000/api/abrir_formulario | python3 -c "import sys,json;ef=json.load(sys.stdin)['efecto'];prov=next(c for c in ef['campos'] if c['rol']=='proveedor');print('  ', [o['label'] for o in prov['opciones']])"
kill $SRV 2>/dev/null
```
Expected: la lista de proveedores incluye **Carolina** (no "Caro") — el display siguió al
hecho editado.
