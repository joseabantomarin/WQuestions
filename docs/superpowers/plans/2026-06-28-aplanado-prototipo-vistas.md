# Aplanado del prototipo a tablas (`wq/vistas.py`) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implementar el aplanado del cap. 8 en el prototipo: tres funciones que proyectan el universo de coordenadas a `pandas.DataFrame` (plana / proyección / pivote) y un seed que reproduce **exactamente** las Figs 8.4 y 8.5 del libro.

**Architecture:** Un módulo nuevo `wq/vistas.py` con tres funciones puras sobre `Universe` (no se toca `query.py`). Un seed `ejemplos/tabla_cap8.py` genera ~336 trámites reales (conteos computados, no hardcodeados) y verifica que el código casa con las figuras publicadas. Tests unitarios sobre un fixture mínimo + un test de integración contra el seed.

**Tech Stack:** Python 3.9, `unittest`, `pandas` (dependencia nueva del prototipo).

## Global Constraints

- **Python 3.9** (sin sintaxis 3.10+ en runtime; `wq/vistas.py` lleva `from __future__ import annotations`).
- **pandas** es dependencia nueva: declarar en `prototipo/requirements.txt` y documentar en `prototipo/README.md`. El núcleo `wq` sigue sin dependencias salvo `vistas.py`.
- Correr todo desde `prototipo/` con `PYTHONPATH=.`.
- **No** modificar `wq/query.py` ni `ejemplos/municipalidad.py`. La suite `tests.test_wq` y `ejemplos/municipalidad.py` deben seguir pasando.
- Identificadores y etiquetas **exactos** del cap. 8: ciudadanos `juan`/`carla`/`marta` (labels "Juan"/"Carla"/"Marta"); clases `licencia_construccion`/`licencia_funcionamiento`/`multa_fiscalizacion`/`licencia_micromov`; zonas `zona_centro`/`zona_norte`/`zona_sur`.
- Prosa y comentarios en español neutro, **sin auto-elogio de honestidad** (nada de "sin maquillaje", "sería deshonesto", etiquetas «Honestidad», etc.).
- El "código" de un individuo es `Individual.id`; la "etiqueta humana" es `Individual.label`. La columna O de la vista plana es la `id` de la propia situación.

## File Structure

- `prototipo/requirements.txt` — **crear**: declara `pandas`.
- `prototipo/wq/vistas.py` — **crear**: las tres funciones + helpers privados.
- `prototipo/wq/__init__.py` — **modificar**: exportar `tabla_plana`, `proyeccion`, `pivote`.
- `prototipo/ejemplos/tabla_cap8.py` — **crear**: seed + vistas + `main()` con asserts.
- `prototipo/ejemplos/__init__.py` — **crear** (vacío): hace `ejemplos` importable para el test de integración.
- `prototipo/tests/test_vistas.py` — **crear**: unitarios + integración.
- `prototipo/README.md` — **modificar**: nota de dependencia + línea de ejecución.

---

### Task 1: Dependencia pandas + `tabla_plana` (Fig 8.2)

**Files:**
- Create: `prototipo/requirements.txt`
- Create: `prototipo/wq/vistas.py`
- Modify: `prototipo/wq/__init__.py`
- Test: `prototipo/tests/test_vistas.py`

**Interfaces:**
- Consumes: `wq.Universe`, `wq.Individual`, `wq.Catalog`, `wq.Axis` (existentes); `Universe.facts_about(ind, at=None)`, `Universe.add_individual`, `Universe.assert_fact`.
- Produces:
  - `tabla_plana(u, subjects=None, at=None) -> pd.DataFrame` con columnas `["Q","O","L","T","N","K"]`, una fila por situación reificada, celdas = ids (códigos), multivalor unido con `"; "`.
  - Helpers privados reutilizados por tareas siguientes: `_etiqueta(ind) -> str`, `_es_situacion(u, ind) -> bool`, `_situaciones(u) -> list`.

- [ ] **Step 1: Declarar la dependencia e instalarla**

Crear `prototipo/requirements.txt`:

```text
pandas>=2.0,<2.3
```

Instalar:

Run: `cd /Users/joseabanto/WQuestions/prototipo && python3 -m pip install -r requirements.txt`
Expected: termina en `Successfully installed ... pandas-2.x ...` (si falla por permisos del Python del sistema, reintentar con `python3 -m pip install --user -r requirements.txt`).

Verificar:

Run: `cd /Users/joseabanto/WQuestions/prototipo && python3 -c "import pandas; print(pandas.__version__)"`
Expected: imprime una versión `2.x`.

- [ ] **Step 2: Escribir el test que falla**

Crear `prototipo/tests/test_vistas.py`:

```python
"""Tests del aplanado a tablas (wq/vistas.py).

Correr con: PYTHONPATH=. python3 -m unittest tests.test_vistas -v
"""

from __future__ import annotations
import unittest

from wq import Axis, Individual, Universe, Catalog
from wq.vistas import tabla_plana


def _mini():
    """Universo mínimo: una venta con agente, lugar y clase."""
    u = Universe(catalog=Catalog())
    persona = Individual(id="q1", axis=Axis.Q, label="Ana")
    zona = Individual(id="l1", axis=Axis.L, label="Centro")
    clase = Individual(id="k_venta", axis=Axis.K, label="Venta")
    s = Individual(id="s1", axis=Axis.O, label="Venta #1")
    u.add_individual(s)
    u.assert_fact(s, "instancia_de", clase)
    u.assert_fact(s, "agente", persona)
    u.assert_fact(s, "lugar_de", zona)
    return u, s


class TestTablaPlana(unittest.TestCase):
    def test_una_fila_por_situacion_con_codigos(self):
        u, s = _mini()
        df = tabla_plana(u)
        self.assertEqual(list(df.columns), ["Q", "O", "L", "T", "N", "K"])
        self.assertEqual(len(df), 1)
        fila = df.iloc[0]
        self.assertEqual(fila["O"], "s1")
        self.assertEqual(fila["Q"], "q1")
        self.assertEqual(fila["L"], "l1")
        self.assertEqual(fila["K"], "k_venta")
        self.assertEqual(fila["T"], "")
        self.assertEqual(fila["N"], "")

    def test_multivalor_en_un_eje_se_une_con_punto_y_coma(self):
        u, s = _mini()
        estado = Individual(id="aprobada", axis=Axis.K, label="Aprobada")
        u.assert_fact(s, "estado", estado)  # estado: rol no canónico (política liberal)
        df = tabla_plana(u)
        self.assertEqual(df.iloc[0]["K"], "k_venta; aprobada")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 3: Correr el test para verificar que falla**

Run: `cd /Users/joseabanto/WQuestions/prototipo && PYTHONPATH=. python3 -m unittest tests.test_vistas -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'wq.vistas'`.

- [ ] **Step 4: Implementar `wq/vistas.py` (helpers + `tabla_plana`)**

Crear `prototipo/wq/vistas.py`:

```python
"""Vistas tabulares del modelo: el grafo proyectado de vuelta a tablas.

Implementa el aplanado del cap. 8 — "De la geometría a la tabla que ya conoces":
tres proyecciones del universo de coordenadas a `pandas.DataFrame`, bajo demanda.

- `tabla_plana`  — Fig 8.2: la hoja dispersa universal (Q/O/L/T/N/K, con códigos).
- `proyeccion`   — Fig 8.4: un reporte legible (filtra K, resuelve etiquetas,
                   proyecta un enlace M como columna).
- `pivote`       — Fig 8.5: el cruce de dos ejes con conteos.

La tabla no es el modelo; es una de sus vistas.
"""

from __future__ import annotations
from datetime import datetime
from typing import Dict, List, Optional, Sequence, Tuple

import pandas as pd

from .axes import Axis
from .individual import Individual
from .universe import Universe


_EJES_VALOR = [Axis.Q, Axis.O, Axis.L, Axis.T, Axis.N, Axis.K]


def _etiqueta(ind: Individual) -> str:
    """Etiqueta humana de un individuo; cae al id si no tiene label."""
    return ind.label or ind.id


def _es_situacion(u: Universe, ind: Individual) -> bool:
    """Una situación reificada vive en O y tiene al menos un `instancia_de`."""
    if ind.axis != Axis.O:
        return False
    return any(f.role == "instancia_de" for f in u.facts_about(ind))


def _situaciones(u: Universe) -> List[Individual]:
    """Todas las situaciones reificadas, en orden de inserción estable."""
    return [ind for ind in u.individuals.values() if _es_situacion(u, ind)]


def tabla_plana(u: Universe,
                subjects: Optional[Sequence[Individual]] = None,
                at: Optional[datetime] = None) -> pd.DataFrame:
    """Fig 8.2 — la hoja dispersa universal.

    Una fila por situación reificada; columnas = los seis ejes de valor
    (Q/O/L/T/N/K); celdas = ids (códigos). Varios valores en un eje se unen
    con "; "; ejes sin valor quedan en "". La columna O es la id de la propia
    situación (los enlaces O→O no se vuelcan ahí).
    """
    sits = list(subjects) if subjects is not None else _situaciones(u)
    columnas = [ax.value for ax in _EJES_VALOR]  # ["Q","O","L","T","N","K"]
    filas: List[Dict[str, str]] = []
    for sit in sits:
        bucket: Dict[str, List[str]] = {c: [] for c in columnas}
        bucket["O"] = [sit.id]
        for f in u.facts_about(sit, at=at):
            ax = f.value.axis.value
            if ax == "O":
                continue
            if ax in bucket:
                bucket[ax].append(f.value.id)
        filas.append({c: "; ".join(bucket[c]) for c in columnas})
    return pd.DataFrame(filas, columns=columnas)
```

Modificar `prototipo/wq/__init__.py` — añadir el import y los nombres a `__all__`. Tras la línea `from .ingest import ingest_situation, IngestError` agregar:

```python
from .vistas import tabla_plana, proyeccion, pivote
```

Y en la lista `__all__`, después de `"ingest_situation", "IngestError",` agregar:

```python
    "tabla_plana", "proyeccion", "pivote",
```

> Nota: `wq/__init__.py` importará `proyeccion` y `pivote`, que aún no existen en `vistas.py`. Por eso este import se agrega aquí pero las funciones se implementan en Task 2 y Task 3. Para que Task 1 corra en verde, **define stubs** temporales al final de `vistas.py` en este step:

```python
def proyeccion(*args, **kwargs):  # implementado en Task 2
    raise NotImplementedError

def pivote(*args, **kwargs):  # implementado en Task 3
    raise NotImplementedError
```

- [ ] **Step 5: Correr el test para verificar que pasa**

Run: `cd /Users/joseabanto/WQuestions/prototipo && PYTHONPATH=. python3 -m unittest tests.test_vistas -v`
Expected: PASS — 2 tests OK.

- [ ] **Step 6: Verificar que no se rompió nada existente**

Run: `cd /Users/joseabanto/WQuestions/prototipo && PYTHONPATH=. python3 -m unittest tests.test_wq -v && PYTHONPATH=. python3 ejemplos/municipalidad.py`
Expected: `test_wq` todo OK; municipalidad imprime `11/11 validaciones pasadas`.

- [ ] **Step 7: Commit**

```bash
git add prototipo/requirements.txt prototipo/wq/vistas.py prototipo/wq/__init__.py prototipo/tests/test_vistas.py
git commit -m "feat(prototipo): vista plana (Fig 8.2) + dependencia pandas"
```

---

### Task 2: `proyeccion` (Fig 8.4)

**Files:**
- Modify: `prototipo/wq/vistas.py`
- Test: `prototipo/tests/test_vistas.py`

**Interfaces:**
- Consumes: helpers de Task 1 (`_etiqueta`, `_situaciones`).
- Produces:
  - `proyeccion(u, columnas, subjects=None, filtro_k=None, at=None) -> pd.DataFrame`.
    `columnas` = lista de `(cabecera, rol)`; el rol especial `"_subject"` proyecta la etiqueta de la situación; otro rol proyecta el label del valor de ese rol (o `""` si no está). `filtro_k` = id de K o iterable de ids. `subjects` = lista de situaciones explícitas.
  - Helper privado `_clases(u, sit, at=None) -> set` (ids de las `instancia_de` de una situación).

- [ ] **Step 1: Escribir los tests que fallan**

Añadir a `prototipo/tests/test_vistas.py` (importar `proyeccion` arriba: cambiar el import a `from wq.vistas import tabla_plana, proyeccion`):

```python
class TestProyeccion(unittest.TestCase):
    def test_resuelve_etiquetas_y_subject(self):
        u, s = _mini()
        cols = [("Cliente (Q)", "agente"),
                ("Operación (O)", "_subject"),
                ("Zona (L)", "lugar_de")]
        df = proyeccion(u, cols)
        self.assertEqual(list(df.columns),
                         ["Cliente (Q)", "Operación (O)", "Zona (L)"])
        self.assertEqual(df.iloc[0].tolist(), ["Ana", "Venta #1", "Centro"])

    def test_rol_ausente_queda_vacio(self):
        u, s = _mini()
        df = proyeccion(u, [("Costo (N)", "monto")])
        self.assertEqual(df.iloc[0]["Costo (N)"], "")

    def test_filtro_k_recorta(self):
        u, s = _mini()
        s2 = Individual(id="s2", axis=Axis.O, label="Compra #1")
        u.add_individual(s2)
        u.assert_fact(s2, "instancia_de",
                      Individual(id="k_compra", axis=Axis.K, label="Compra"))
        df = proyeccion(u, [("Op (O)", "_subject")], filtro_k="k_venta")
        self.assertEqual(df["Op (O)"].tolist(), ["Venta #1"])

    def test_subjects_explicito_respeta_orden(self):
        u, s = _mini()
        s2 = Individual(id="s2", axis=Axis.O, label="Compra #1")
        u.add_individual(s2)
        u.assert_fact(s2, "instancia_de",
                      Individual(id="k_compra", axis=Axis.K, label="Compra"))
        df = proyeccion(u, [("Op (O)", "_subject")], subjects=[s2, s])
        self.assertEqual(df["Op (O)"].tolist(), ["Compra #1", "Venta #1"])
```

- [ ] **Step 2: Correr para verificar que falla**

Run: `cd /Users/joseabanto/WQuestions/prototipo && PYTHONPATH=. python3 -m unittest tests.test_vistas.TestProyeccion -v`
Expected: FAIL — `NotImplementedError` (el stub de Task 1).

- [ ] **Step 3: Implementar `proyeccion` en `wq/vistas.py`**

En `prototipo/wq/vistas.py`, **reemplazar el stub** `def proyeccion(*args, **kwargs): ...` por:

```python
def _clases(u: Universe, sit: Individual,
            at: Optional[datetime] = None) -> set:
    """Ids de las categorías K declaradas con `instancia_de` para `sit`."""
    return {f.value.id for f in u.facts_about(sit, at=at)
            if f.role == "instancia_de"}


def proyeccion(u: Universe,
               columnas: Sequence[Tuple[str, str]],
               subjects: Optional[Sequence[Individual]] = None,
               filtro_k=None,
               at: Optional[datetime] = None) -> pd.DataFrame:
    """Fig 8.4 — el reporte legible.

    `columnas`: lista de (cabecera, rol). El rol "_subject" proyecta la
    etiqueta de la situación; cualquier otro proyecta el label del valor de
    ese rol (o "" si no está). `filtro_k`: id de K o iterable de ids.
    `subjects`: si se da, solo esas situaciones, en ese orden.
    """
    if isinstance(filtro_k, str):
        filtro_k = {filtro_k}
    elif filtro_k is not None:
        filtro_k = set(filtro_k)

    sits = list(subjects) if subjects is not None else _situaciones(u)
    if filtro_k is not None:
        sits = [s for s in sits if _clases(u, s, at) & filtro_k]

    cabeceras = [cab for cab, _ in columnas]
    filas: List[Dict[str, str]] = []
    for sit in sits:
        hechos = u.facts_about(sit, at=at)
        fila: Dict[str, str] = {}
        for cab, rol in columnas:
            if rol == "_subject":
                fila[cab] = _etiqueta(sit)
            else:
                vals = [f.value for f in hechos if f.role == rol]
                fila[cab] = _etiqueta(vals[0]) if vals else ""
        filas.append(fila)
    return pd.DataFrame(filas, columns=cabeceras)
```

- [ ] **Step 4: Correr para verificar que pasa**

Run: `cd /Users/joseabanto/WQuestions/prototipo && PYTHONPATH=. python3 -m unittest tests.test_vistas -v`
Expected: PASS — todos los tests de `TestTablaPlana` y `TestProyeccion` OK.

- [ ] **Step 5: Commit**

```bash
git add prototipo/wq/vistas.py prototipo/tests/test_vistas.py
git commit -m "feat(prototipo): vista proyección legible (Fig 8.4)"
```

---

### Task 3: `pivote` (Fig 8.5)

**Files:**
- Modify: `prototipo/wq/vistas.py`
- Test: `prototipo/tests/test_vistas.py`

**Interfaces:**
- Consumes: helpers `_etiqueta`, `_situaciones`, `_clases`.
- Produces:
  - `pivote(u, eje_filas="instancia_de", eje_cols="lugar_de", orden_filas=None, orden_cols=None, filtro_k=None, resolver_l_a_zona=False, at=None) -> pd.DataFrame` — DataFrame indexado por etiquetas de fila, columnas = etiquetas; celdas = conteos `int` (0 donde no hay).
  - Helpers privados `_subir_a_zona(u, l_ind, zonas, max_saltos=10) -> Individual` y `_orden_aparicion(ids) -> list`.

- [ ] **Step 1: Escribir los tests que fallan**

Añadir a `prototipo/tests/test_vistas.py` (ampliar el import: `from wq.vistas import tabla_plana, proyeccion, pivote`):

```python
class TestPivote(unittest.TestCase):
    def _cruce(self):
        u = Universe(catalog=Catalog())
        kA = Individual(id="kA", axis=Axis.K, label="A")
        kB = Individual(id="kB", axis=Axis.K, label="B")
        lx = Individual(id="lx", axis=Axis.L, label="X")
        ly = Individual(id="ly", axis=Axis.L, label="Y")

        def sit(i, k, l):
            s = Individual(id=f"s{i}", axis=Axis.O, label=f"s{i}")
            u.add_individual(s)
            u.assert_fact(s, "instancia_de", k)
            u.assert_fact(s, "lugar_de", l)
            return s

        sit(1, kA, lx)
        sit(2, kA, lx)
        sit(3, kA, ly)
        sit(4, kB, lx)
        return u

    def test_cuenta_el_cruce_k_por_l(self):
        u = self._cruce()
        df = pivote(u, orden_filas=["kA", "kB"], orden_cols=["lx", "ly"])
        self.assertEqual(int(df.loc["A", "X"]), 2)
        self.assertEqual(int(df.loc["A", "Y"]), 1)
        self.assertEqual(int(df.loc["B", "X"]), 1)
        self.assertEqual(int(df.loc["B", "Y"]), 0)

    def test_resolver_l_a_zona_sube_por_dentro_de(self):
        u = Universe(catalog=Catalog())
        k = Individual(id="k", axis=Axis.K, label="K")
        zona = Individual(id="zona", axis=Axis.L, label="Zona")
        calle = Individual(id="calle", axis=Axis.L, label="Calle 1")
        u.add_individual(zona)
        u.add_individual(calle)
        u.assert_fact(calle, "dentro_de", zona)
        s = Individual(id="s1", axis=Axis.O, label="s1")
        u.add_individual(s)
        u.assert_fact(s, "instancia_de", k)
        u.assert_fact(s, "lugar_de", calle)
        df = pivote(u, orden_filas=["k"], orden_cols=["zona"],
                    resolver_l_a_zona=True)
        self.assertEqual(int(df.loc["K", "Zona"]), 1)
```

- [ ] **Step 2: Correr para verificar que falla**

Run: `cd /Users/joseabanto/WQuestions/prototipo && PYTHONPATH=. python3 -m unittest tests.test_vistas.TestPivote -v`
Expected: FAIL — `NotImplementedError` (el stub de Task 1).

- [ ] **Step 3: Implementar `pivote` en `wq/vistas.py`**

En `prototipo/wq/vistas.py`, **reemplazar el stub** `def pivote(*args, **kwargs): ...` por:

```python
def _subir_a_zona(u: Universe, l_ind: Individual, zonas,
                  max_saltos: int = 10) -> Individual:
    """Sube por `dentro_de` hasta un ancestro cuyo id esté en `zonas`.

    Si `zonas` es None, sube hasta la raíz (primer L sin `dentro_de`). Si el
    propio `l_ind` ya está en `zonas`, lo devuelve tal cual.
    """
    cur = l_ind
    for _ in range(max_saltos):
        if zonas is not None and cur.id in zonas:
            return cur
        ups = [f.value for f in u.facts_about(cur) if f.role == "dentro_de"]
        if not ups:
            return cur
        cur = ups[0]
    return cur


def _orden_aparicion(ids) -> List[str]:
    """Lista de ids únicos en orden de primera aparición."""
    vistos: List[str] = []
    s = set()
    for i in ids:
        if i not in s:
            s.add(i)
            vistos.append(i)
    return vistos


def pivote(u: Universe,
           eje_filas: str = "instancia_de",
           eje_cols: str = "lugar_de",
           orden_filas: Optional[Sequence[str]] = None,
           orden_cols: Optional[Sequence[str]] = None,
           filtro_k=None,
           resolver_l_a_zona: bool = False,
           at: Optional[datetime] = None) -> pd.DataFrame:
    """Fig 8.5 — el cruce de dos ejes con conteos.

    Agrupa cada situación por el valor de `eje_filas` y el de `eje_cols`;
    la celda es el número de situaciones en esa intersección. Con
    `resolver_l_a_zona=True`, el valor de `eje_cols` se sube por `dentro_de`
    hasta una zona de `orden_cols`.
    """
    if isinstance(filtro_k, str):
        filtro_k = {filtro_k}
    elif filtro_k is not None:
        filtro_k = set(filtro_k)

    sits = _situaciones(u)
    if filtro_k is not None:
        sits = [s for s in sits if _clases(u, s, at) & filtro_k]

    zonas = set(orden_cols) if (resolver_l_a_zona and orden_cols) else None

    conteos: Dict[Tuple[str, str], int] = {}
    etiquetas: Dict[str, str] = {}
    for sit in sits:
        hechos = u.facts_about(sit, at=at)
        fila_vals = [f.value for f in hechos if f.role == eje_filas]
        col_vals = [f.value for f in hechos if f.role == eje_cols]
        if not fila_vals or not col_vals:
            continue
        fv = fila_vals[0]
        cv = col_vals[0]
        if resolver_l_a_zona:
            cv = _subir_a_zona(u, cv, zonas)
        etiquetas[fv.id] = _etiqueta(fv)
        etiquetas[cv.id] = _etiqueta(cv)
        clave = (fv.id, cv.id)
        conteos[clave] = conteos.get(clave, 0) + 1

    fila_ids = (list(orden_filas) if orden_filas
                else _orden_aparicion([k[0] for k in conteos]))
    col_ids = (list(orden_cols) if orden_cols
               else _orden_aparicion([k[1] for k in conteos]))

    data = [[conteos.get((fid, cid), 0) for cid in col_ids]
            for fid in fila_ids]
    return pd.DataFrame(
        data,
        index=[etiquetas.get(fid, fid) for fid in fila_ids],
        columns=[etiquetas.get(cid, cid) for cid in col_ids],
    )
```

- [ ] **Step 4: Correr para verificar que pasa**

Run: `cd /Users/joseabanto/WQuestions/prototipo && PYTHONPATH=. python3 -m unittest tests.test_vistas -v`
Expected: PASS — `TestTablaPlana`, `TestProyeccion`, `TestPivote` todos OK.

- [ ] **Step 5: Commit**

```bash
git add prototipo/wq/vistas.py prototipo/tests/test_vistas.py
git commit -m "feat(prototipo): vista pivote con conteos (Fig 8.5)"
```

---

### Task 4: Seed `ejemplos/tabla_cap8.py` + integración + docs

**Files:**
- Create: `prototipo/ejemplos/tabla_cap8.py`
- Create: `prototipo/ejemplos/__init__.py`
- Modify: `prototipo/README.md`
- Test: `prototipo/tests/test_vistas.py`

**Interfaces:**
- Consumes: `tabla_plana`, `proyeccion`, `pivote` (Tasks 1-3).
- Produces (en `ejemplos/tabla_cap8.py`):
  - `build_universe() -> (Universe, dict)` — universo con ~336 trámites + 3 destacados. El dict `h` expone: `constr`/`func`/`multa`/`micromov` (clases K), `zc`/`zn`/`zs` (zonas L), `juan_t`/`carla_t`/`marta_t` (situaciones destacadas).
  - `vista_plana(u, h)`, `vista_proyeccion(u, h)`, `vista_pivote(u, h)` — devuelven los tres DataFrames.
  - `main() -> bool` — imprime las vistas y verifica que coinciden con las Figs 8.4 y 8.5.

- [ ] **Step 1: Crear el paquete `ejemplos` y el seed**

Crear `prototipo/ejemplos/__init__.py` **vacío** (un archivo de 0 bytes).

Crear `prototipo/ejemplos/tabla_cap8.py`:

```python
"""Seed del cap. 8 — las tres vistas tabulares sobre datos reales.

Construye un universo municipal con ~336 trámites distribuidos exactamente como
la Fig 8.5, más tres trámites destacados (Juan, Carla, Marta) con los atributos
literales de la Fig 8.4. Corre las tres vistas y verifica que el código reproduce
las figuras publicadas: el capítulo y el prototipo dan los mismos números.

    PYTHONPATH=. python3 ejemplos/tabla_cap8.py
"""

from __future__ import annotations
from typing import Dict, Tuple

from wq import Axis, Individual, Universe, Catalog
from wq.vistas import tabla_plana, proyeccion, pivote


# Distribución exacta de la Fig 8.5 (clase K × zona L → conteo).
DISTRIBUCION = {
    "licencia_construccion":   {"zona_centro": 45,  "zona_norte": 12, "zona_sur": 8},
    "licencia_funcionamiento": {"zona_centro": 120, "zona_norte": 54, "zona_sur": 30},
    "multa_fiscalizacion":     {"zona_centro": 15,  "zona_norte": 42, "zona_sur": 10},
}

ETIQUETA_CLASE = {
    "licencia_construccion": "Licencias de construcción",
    "licencia_funcionamiento": "Licencias de funcionamiento",
    "multa_fiscalizacion": "Multas de fiscalización",
    "licencia_micromov": "Licencias de micromovilidad",
}
ETIQUETA_ZONA = {"zona_centro": "Centro", "zona_norte": "Norte", "zona_sur": "Sur"}
COD_CLASE = {"licencia_construccion": "constr",
             "licencia_funcionamiento": "func",
             "multa_fiscalizacion": "multa"}
COD_ZONA = {"zona_centro": "centro", "zona_norte": "norte", "zona_sur": "sur"}

COLUMNAS_PROYECCION = [
    ("Ciudadano (Q)", "agente"),
    ("Expediente (O)", "_subject"),
    ("Ubicación (L)", "lugar_de"),
    ("Fecha (T)", "momento"),
    ("Costo (N)", "monto"),
    ("Estado (M)", "estado"),
]

PIVOTE_ESPERADA = [[45, 12, 8], [120, 54, 30], [15, 42, 10]]
PROYECCION_ESPERADA = [
    ["Juan", "Licencia de funcionamiento", "Jr. Trujillo 450, Centro",
     "22-06-2026", "S/ 450,00", "Solicitado"],
    ["Carla", "Licencia de micromovilidad", "Av. Perú 1200, Norte",
     "23-06-2026", "S/ 300,00", "En revisión"],
    ["Marta", "Remodelación de local", "Jr. Lima 88, Centro",
     "24-06-2026", "S/ 520,00", "Aprobada"],
]


def _t(u, label, tid):
    return u.add_individual(Individual(id=tid, axis=Axis.T, label=label))


def _n(u, valor, label, nid):
    return u.add_individual(Individual(id=nid, axis=Axis.N, label=label,
                                       payload={"value": valor, "unit": "PEN"}))


def _estado(u, eid, label):
    return u.add_individual(Individual(id=eid, axis=Axis.K, label=label))


def _generico(u, clase, zona, sid):
    """Un trámite del grueso: solo clase (K) y zona (L)."""
    s = u.add_individual(Individual(id=sid, axis=Axis.O, label=sid))
    u.assert_fact(s, "instancia_de", clase)
    u.assert_fact(s, "lugar_de", zona)
    return s


def _tramite_juan(u, clases, zonas):
    direccion = u.add_individual(Individual(
        id="dir_juan", axis=Axis.L, label="Jr. Trujillo 450, Centro"))
    u.assert_fact(direccion, "dentro_de", zonas["zona_centro"])
    juan = u.add_individual(Individual(id="juan", axis=Axis.Q, label="Juan"))
    s = u.add_individual(Individual(id="tram_juan_func_centro", axis=Axis.O,
                                    label="Licencia de funcionamiento"))
    u.assert_fact(s, "instancia_de", clases["licencia_funcionamiento"])
    u.assert_fact(s, "agente", juan)
    u.assert_fact(s, "lugar_de", direccion)
    u.assert_fact(s, "momento", _t(u, "22-06-2026", "t_2026-06-22"))
    u.assert_fact(s, "monto", _n(u, 450.0, "S/ 450,00", "n_450_pen"))
    u.assert_fact(s, "estado", _estado(u, "solicitado", "Solicitado"))
    return s


def _tramite_marta(u, clases, zonas):
    direccion = u.add_individual(Individual(
        id="dir_marta", axis=Axis.L, label="Jr. Lima 88, Centro"))
    u.assert_fact(direccion, "dentro_de", zonas["zona_centro"])
    marta = u.add_individual(Individual(id="marta", axis=Axis.Q, label="Marta"))
    s = u.add_individual(Individual(id="tram_marta_constr_centro", axis=Axis.O,
                                    label="Remodelación de local"))
    u.assert_fact(s, "instancia_de", clases["licencia_construccion"])
    u.assert_fact(s, "agente", marta)
    u.assert_fact(s, "lugar_de", direccion)
    u.assert_fact(s, "momento", _t(u, "24-06-2026", "t_2026-06-24"))
    u.assert_fact(s, "monto", _n(u, 520.0, "S/ 520,00", "n_520_pen"))
    u.assert_fact(s, "estado", _estado(u, "aprobada", "Aprobada"))
    return s


def _tramite_carla(u, clases, zonas):
    direccion = u.add_individual(Individual(
        id="dir_carla", axis=Axis.L, label="Av. Perú 1200, Norte"))
    u.assert_fact(direccion, "dentro_de", zonas["zona_norte"])
    carla = u.add_individual(Individual(id="carla", axis=Axis.Q, label="Carla"))
    s = u.add_individual(Individual(id="tram_carla_micromov", axis=Axis.O,
                                    label="Licencia de micromovilidad"))
    u.assert_fact(s, "instancia_de", clases["licencia_micromov"])
    u.assert_fact(s, "agente", carla)
    u.assert_fact(s, "lugar_de", direccion)
    u.assert_fact(s, "momento", _t(u, "23-06-2026", "t_2026-06-23"))
    u.assert_fact(s, "monto", _n(u, 300.0, "S/ 300,00", "n_300_pen"))
    u.assert_fact(s, "estado", _estado(u, "en_revision", "En revisión"))
    return s


def build_universe() -> Tuple[Universe, Dict[str, Individual]]:
    u = Universe(name="cap8_tablas", catalog=Catalog())

    clases = {cid: u.add_individual(Individual(
                  id=cid, axis=Axis.K, label=ETIQUETA_CLASE[cid]))
              for cid in list(DISTRIBUCION) + ["licencia_micromov"]}
    zonas = {lid: u.add_individual(Individual(
                 id=lid, axis=Axis.L, label=ETIQUETA_ZONA[lid]))
             for lid in ("zona_centro", "zona_norte", "zona_sur")}

    destacados: Dict[str, Individual] = {}
    for cid, por_zona in DISTRIBUCION.items():
        for lid, total in por_zona.items():
            for i in range(total):
                if i == 0 and cid == "licencia_funcionamiento" and lid == "zona_centro":
                    destacados["juan_t"] = _tramite_juan(u, clases, zonas)
                elif i == 0 and cid == "licencia_construccion" and lid == "zona_centro":
                    destacados["marta_t"] = _tramite_marta(u, clases, zonas)
                else:
                    sid = f"tram_{COD_CLASE[cid]}_{COD_ZONA[lid]}_{i:03d}"
                    _generico(u, clases[cid], zonas[lid], sid)

    destacados["carla_t"] = _tramite_carla(u, clases, zonas)

    h: Dict[str, Individual] = {
        "constr": clases["licencia_construccion"],
        "func": clases["licencia_funcionamiento"],
        "multa": clases["multa_fiscalizacion"],
        "micromov": clases["licencia_micromov"],
        "zc": zonas["zona_centro"], "zn": zonas["zona_norte"], "zs": zonas["zona_sur"],
    }
    h.update(destacados)
    return u, h


def vista_plana(u, h):
    # Muestra de la hoja dispersa: los tres destacados (cross-clase), con códigos.
    return tabla_plana(u, subjects=[h["juan_t"], h["carla_t"], h["marta_t"]])


def vista_proyeccion(u, h):
    # Reporte legible de los tres trámites destacados (la Fig 8.4 es muestra de 3).
    return proyeccion(u, COLUMNAS_PROYECCION,
                      subjects=[h["juan_t"], h["carla_t"], h["marta_t"]])


def vista_pivote(u, h):
    return pivote(
        u,
        filtro_k=[h["constr"].id, h["func"].id, h["multa"].id],
        orden_filas=[h["constr"].id, h["func"].id, h["multa"].id],
        orden_cols=[h["zc"].id, h["zn"].id, h["zs"].id],
        resolver_l_a_zona=True,
    )


def main() -> bool:
    u, h = build_universe()
    print("=" * 72)
    print("CAP. 8 — De la geometría a la tabla que ya conoces")
    print("=" * 72)
    print()
    print(u.summary())
    print()

    plana = vista_plana(u, h)
    proj = vista_proyeccion(u, h)
    piv = vista_pivote(u, h)

    print("Fig 8.2 — hoja dispersa (códigos):")
    print(plana.to_string(index=False))
    print()
    print("Fig 8.4 — proyección legible:")
    print(proj.to_string(index=False))
    print()
    print("Fig 8.5 — pivote (conteos):")
    print(piv.to_string())
    print()

    ok_piv = piv.values.tolist() == PIVOTE_ESPERADA
    ok_proj = [proj.iloc[i].tolist()
               for i in range(len(proj))] == PROYECCION_ESPERADA
    print(f"  {'✓' if ok_piv else '✗'}  pivote reproduce la Fig 8.5")
    print(f"  {'✓' if ok_proj else '✗'}  proyección reproduce la Fig 8.4")
    return ok_piv and ok_proj


if __name__ == "__main__":
    import sys
    sys.exit(0 if main() else 1)
```

- [ ] **Step 2: Correr el seed y verificar que reproduce las figuras**

Run: `cd /Users/joseabanto/WQuestions/prototipo && PYTHONPATH=. python3 ejemplos/tabla_cap8.py; echo "exit=$?"`
Expected: imprime las tres vistas, las dos líneas con `✓`, y `exit=0`. La pivote impresa muestra:
```
                             Centro  Norte  Sur
Licencias de construcción         45     12    8
Licencias de funcionamiento      120     54   30
Multas de fiscalización           15     42   10
```

- [ ] **Step 3: Escribir el test de integración**

Añadir a `prototipo/tests/test_vistas.py`:

```python
class TestSeedCap8(unittest.TestCase):
    def test_reproduce_figuras_del_libro(self):
        from ejemplos import tabla_cap8
        u, h = tabla_cap8.build_universe()
        piv = tabla_cap8.vista_pivote(u, h)
        self.assertEqual(piv.values.tolist(),
                         [[45, 12, 8], [120, 54, 30], [15, 42, 10]])
        self.assertEqual(list(piv.index),
                         ["Licencias de construcción",
                          "Licencias de funcionamiento",
                          "Multas de fiscalización"])
        self.assertEqual(list(piv.columns), ["Centro", "Norte", "Sur"])
        proj = tabla_cap8.vista_proyeccion(u, h)
        self.assertEqual(proj.iloc[0].tolist(),
                         ["Juan", "Licencia de funcionamiento",
                          "Jr. Trujillo 450, Centro", "22-06-2026",
                          "S/ 450,00", "Solicitado"])
        self.assertEqual(proj.iloc[1].tolist(),
                         ["Carla", "Licencia de micromovilidad",
                          "Av. Perú 1200, Norte", "23-06-2026",
                          "S/ 300,00", "En revisión"])
        self.assertEqual(proj.iloc[2].tolist(),
                         ["Marta", "Remodelación de local",
                          "Jr. Lima 88, Centro", "24-06-2026",
                          "S/ 520,00", "Aprobada"])
```

- [ ] **Step 4: Correr toda la suite del aplanado**

Run: `cd /Users/joseabanto/WQuestions/prototipo && PYTHONPATH=. python3 -m unittest tests.test_vistas -v`
Expected: PASS — `TestTablaPlana`, `TestProyeccion`, `TestPivote`, `TestSeedCap8` todos OK.

- [ ] **Step 5: Actualizar el README**

En `prototipo/README.md`, reemplazar la línea 3:

```
Prototipo en Python puro (sin dependencias externas; Python 3.9+) que
```

por:

```
Prototipo en Python (Python 3.9+). El núcleo `wq` no tiene dependencias; el
aplanado a tablas (`wq/vistas.py`) y el ejemplo `tabla_cap8.py` usan `pandas`. Que
```

En el bloque `## Cómo correr`, después de la línea `PYTHONPATH=. python3 ejemplos/dominios_previos.py`, agregar (dentro del bloque ```bash):

```bash

# Instalar la dependencia del aplanado a tablas
python3 -m pip install -r requirements.txt

# Las tres vistas del cap. 8 (plana / proyección / pivote) sobre ~336 trámites
PYTHONPATH=. python3 ejemplos/tabla_cap8.py
```

- [ ] **Step 6: Verificación final — nada roto + todo en verde**

Run: `cd /Users/joseabanto/WQuestions/prototipo && PYTHONPATH=. python3 -m unittest tests.test_wq tests.test_vistas && PYTHONPATH=. python3 ejemplos/municipalidad.py && PYTHONPATH=. python3 ejemplos/tabla_cap8.py`
Expected: `test_wq` + `test_vistas` OK; municipalidad `11/11`; tabla_cap8 con los dos `✓` y exit 0.

- [ ] **Step 7: Commit**

```bash
git add prototipo/ejemplos/tabla_cap8.py prototipo/ejemplos/__init__.py prototipo/tests/test_vistas.py prototipo/README.md
git commit -m "feat(prototipo): seed cap.8 que reproduce las Figs 8.4 y 8.5 + docs"
```

---

## Self-Review

**Spec coverage:**
- `tabla_plana`/`proyeccion`/`pivote` que devuelven DataFrame → Tasks 1-3. ✓
- `subjects=` en `proyeccion` (reporte de los 3 destacados) → Task 2 + usado en Task 4. ✓
- Seed con ~336 trámites, conteos computados, `instancia_de=<clase>` directo → Task 4. ✓
- 3 destacados literales de la Fig 8.4 → Task 4 (`_tramite_juan/marta/carla`). ✓
- Ubicación: dirección de calle como L `dentro_de` zona; pivote resuelve a zona → Task 3 (`_subir_a_zona`) + Task 4. ✓
- pandas como dependencia (requirements.txt + README) → Task 1 + Task 4. ✓
- Tests unitarios sobre fixture + integración contra el seed → Tasks 1-4. ✓
- No romper `test_wq`/`municipalidad.py` → verificado en Task 1 Step 6 y Task 4 Step 6. ✓
- Exportar en `wq/__init__.py` → Task 1. ✓

**Placeholder scan:** sin TBD/TODO; todo el código está completo. Los stubs `NotImplementedError` de Task 1 son intencionales (se reemplazan en Tasks 2-3, indicado explícitamente). ✓

**Type/nombre consistency:** `tabla_plana`/`proyeccion`/`pivote` con las mismas firmas en plan, `__init__.py`, seed y tests. Handles del seed (`constr`/`func`/`multa`/`zc`/`zn`/`zs`/`juan_t`/`carla_t`/`marta_t`) usados consistentemente en `vista_*` y en `TestSeedCap8`. Las etiquetas de clase/zona del seed coinciden con los asserts del test y del `main`. ✓
