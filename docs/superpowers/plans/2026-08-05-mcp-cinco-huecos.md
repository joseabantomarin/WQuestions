# Los cinco huecos del MCP — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Que el servidor `wquestions-mcp` conteste una pregunta de negocio entera sin que nadie tenga que salir del protocolo: encontrar una entidad por su nombre, leer nombres en vez de ids, filtrar por período, agregar, y escribir un atributo sobre una entidad.

**Architecture:** Todo el comportamiento nuevo vive en `WQSession` (`session.py`), que se prueba sin levantar MCP; `server.py` solo declara herramientas y parámetros. En `prototipo/wq/query.py` se toca únicamente el punto 1 de `query()` para admitir rangos. Una **sola** función resuelve "cómo se llama esto" y la comparten `labels` y `find`.

**Tech Stack:** Python 3.10+, pytest, FastMCP, motor `wq` del prototipo (instalación editable).

## Global Constraints

- Los **128 tests actuales deben seguir pasando** (`pytest prototipo/tests mcp-server/tests`). Si alguno compara la respuesta completa de `ask`, se ajusta ese test y se anota por qué en el commit.
- Todo lo nuevo es **aditivo**: una llamada existente devuelve lo mismo más las claves nuevas.
- El motor (`Universe`, `Fact`, `ingest_situation`, `catalog`) **no se toca**. Solo `query.py`, punto 1.
- Los mensajes de error se escriben en **inglés**, como el resto de `session.py`.
- La derivación de `importe` es específica de yaku: va en el script de migración del scratchpad, **nunca** en `wq/` ni en `wquestions_mcp/`.
- Ejecutar los tests con `/Users/joseabanto/WQuestions/.venv/bin/python -m pytest`.

---

### Task 1: Resolución de nombres — la función que comparten `labels` y `find`

**Files:**
- Modify: `mcp-server/wquestions_mcp/session.py`
- Test: `mcp-server/tests/test_session.py`

**Interfaces:**
- Consumes: nada.
- Produces: `WQSession._display(entity_id: str) -> str | dict | None`. Devuelve el nombre legible, o `{"value","unit"}` si la entidad es una magnitud N, o `None` si no aporta nada. Las tareas 2 y 4 dependen de esta firma exacta. Constante módulo `NAME_ROLE = "nombre"`.

- [ ] **Step 1: Escribir los tests que fallan**

Añadir al final de `mcp-server/tests/test_session.py`:

```python
def test_display_uses_label_when_no_name_fact():
    s = WQSession()
    s.add_entity("ana", "Q", "Ana Torres")
    assert s._display("ana") == "Ana Torres"


def test_display_prefers_a_nombre_fact_over_the_label():
    s = WQSession()
    s.add_entity("ana", "Q", "etiqueta vieja")
    s.add_entity("lit_ana", "K", "Ana Torres")
    s.universe.assert_fact(s.universe.individuals["ana"], "nombre",
                           s.universe.individuals["lit_ana"])
    assert s._display("ana") == "Ana Torres"


def test_display_omits_entities_whose_label_is_the_id():
    s = WQSession()
    s.add_entity("pro_783", "O")          # label queda igual al id
    assert s._display("pro_783") is None


def test_display_resolves_a_magnitude_to_value_and_unit():
    s = WQSession()
    s.add_entity("pen", "K", "PEN")
    s.add_entity("n1", "N", value=25.0, unit="pen")
    assert s._display("n1") == {"value": 25.0, "unit": "PEN"}


def test_display_returns_none_for_unknown_entity():
    s = WQSession()
    assert s._display("no_existe") is None
```

- [ ] **Step 2: Ejecutar y ver que fallan**

Run: `/Users/joseabanto/WQuestions/.venv/bin/python -m pytest mcp-server/tests/test_session.py -k display -v`
Expected: FAIL con `AttributeError: 'WQSession' object has no attribute '_display'`

- [ ] **Step 3: Implementar**

En `session.py`, junto a las constantes de módulo (después de `_AXIS_GUIDE`), añadir:

```python
# El rol con que una entidad declara su propio nombre. `labels` y `find` leen
# de aquí antes que del label, para que el nombre sea un hecho y no un adorno
# del individuo.
NAME_ROLE = "nombre"
```

Y como método de `WQSession`, después de `_individual`:

```python
    def _display(self, entity_id: str) -> Any:
        """Cómo se llama esta entidad, para mostrarla o para buscarla.

        Orden: un hecho con rol `nombre` > el label del individuo > nada.
        Una magnitud se resuelve a {value, unit}. Devuelve None cuando el
        individuo no aporta nombre propio (label ausente o igual al id), que es
        el caso de los nodos de situación: no vale la pena gastar tokens en
        repetir un identificador que ya está en la fila.
        """
        ind = self.universe.individuals.get(entity_id)
        if ind is None:
            return None
        if ind.axis is Axis.N and isinstance(ind.payload, dict):
            unit_id = ind.payload.get("unit")
            unit = self.universe.individuals.get(unit_id)
            return {"value": ind.payload.get("value"),
                    "unit": (unit.label or unit_id) if unit else unit_id}
        named = [f for f in self.universe.facts_about(ind) if f.role == NAME_ROLE]
        if named:
            latest = named[0]
            for f in named[1:]:
                if f.tx_time >= latest.tx_time:
                    latest = f
            return latest.value.label or latest.value.id
        if ind.label and ind.label != ind.id:
            return ind.label
        return None
```

- [ ] **Step 4: Ejecutar y ver que pasan**

Run: `/Users/joseabanto/WQuestions/.venv/bin/python -m pytest mcp-server/tests/test_session.py -k display -v`
Expected: 5 passed

- [ ] **Step 5: Comprobar que no rompimos nada y commitear**

```bash
/Users/joseabanto/WQuestions/.venv/bin/python -m pytest prototipo/tests mcp-server/tests -q
git add mcp-server/wquestions_mcp/session.py mcp-server/tests/test_session.py
git commit -m "feat(mcp): una sola definición de cómo se llama una entidad

_display resuelve el nombre en un orden: hecho con rol nombre, label del
individuo, nada. La comparten labels y find, así que si algún día el nombre
sale de otro sitio cambia en un solo lugar."
```

---

### Task 2: `labels` — el diccionario de nombres en la respuesta de `ask`

**Files:**
- Modify: `mcp-server/wquestions_mcp/session.py` (método `ask`)
- Modify: `mcp-server/wquestions_mcp/server.py` (herramienta `ask`)
- Test: `mcp-server/tests/test_session.py`

**Interfaces:**
- Consumes: `WQSession._display(entity_id)` de la Tarea 1.
- Produces: `ask(..., labels: bool = True)` devuelve además la clave `labels: dict[str, str | dict]`. Las tareas 5 y 6 devuelven la misma clave.

- [ ] **Step 1: Escribir los tests que fallan**

```python
def test_ask_returns_a_labels_dictionary():
    s = WQSession()
    s.add_entity("ana", "Q", "Ana Torres")
    s.add_entity("pen", "K", "PEN")
    s.assert_situation("vender", {
        "agente": "ana",
        "tema": {"id": "libro", "axis": "O", "label": "Libro"},
        "por_cuanto": {"id": "n1", "axis": "N", "value": 20.0, "unit": "pen"}})
    out = s.ask(fixed={"agente": "ana"}, ask=["tema", "por_cuanto"])
    assert out["labels"]["libro"] == "Libro"
    assert out["labels"]["n1"] == {"value": 20.0, "unit": "PEN"}


def test_ask_labels_omit_situation_nodes():
    s = WQSession()
    s.add_entity("ana", "Q", "Ana Torres")
    s.assert_situation("vender", {"agente": "ana",
                                  "tema": {"id": "libro", "axis": "O",
                                           "label": "Libro"}})
    out = s.ask(fixed={"agente": "ana"}, ask=["tema"])
    sid = out["results"][0]["_subject"]
    assert sid not in out["labels"]


def test_ask_labels_name_each_id_once():
    s = WQSession()
    s.add_entity("ana", "Q", "Ana Torres")
    s.add_entity("libro", "O", "Libro")
    for _ in range(5):
        s.assert_situation("vender", {"agente": "ana", "tema": "libro"})
    out = s.ask(fixed={"agente": "ana"}, ask=["tema"])
    assert out["count"] == 5
    assert list(out["labels"]).count("libro") == 1


def test_ask_labels_can_be_switched_off():
    s = WQSession()
    s.add_entity("ana", "Q", "Ana Torres")
    s.assert_situation("vender", {"agente": "ana",
                                  "tema": {"id": "libro", "axis": "O",
                                           "label": "Libro"}})
    out = s.ask(fixed={"agente": "ana"}, ask=["tema"], labels=False)
    assert "labels" not in out
```

- [ ] **Step 2: Ejecutar y ver que fallan**

Run: `/Users/joseabanto/WQuestions/.venv/bin/python -m pytest mcp-server/tests/test_session.py -k "ask_labels or ask_returns_a_labels" -v`
Expected: FAIL con `KeyError: 'labels'` / `TypeError: ask() got an unexpected keyword argument 'labels'`

- [ ] **Step 3: Implementar**

En `session.py`, añadir el método auxiliar justo antes de `ask`:

```python
    def _labels_for(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Nombres de todos los ids que aparecen en las filas, una sola vez.

        Diccionario aparte y no anotación por fila: un producto que sale en 300
        filas se nombra una vez, no trescientas.
        """
        out: Dict[str, Any] = {}
        for row in results:
            for value in row.values():
                for vid in (value if isinstance(value, list) else [value]):
                    if isinstance(vid, str) and vid not in out:
                        name = self._display(vid)
                        if name is not None:
                            out[vid] = name
        return out
```

Cambiar la firma de `ask` y su retorno:

```python
    def ask(self, fixed: Optional[Dict[str, Any]] = None,
            ask: Optional[List[str]] = None,
            type: Optional[str] = None,
            at: Optional[str] = None,
            history: bool = False,
            labels: bool = True) -> Dict[str, Any]:
```

y sustituir el `return` final por:

```python
        out: Dict[str, Any] = {"count": len(results), "results": results}
        if labels:
            out["labels"] = self._labels_for(results)
        return out
```

En `server.py`, añadir el parámetro a la herramienta `ask`:

```python
@mcp.tool()
def ask(fixed: Optional[Dict[str, Any]] = None,
        ask: Optional[List[str]] = None,
        type: Optional[str] = None,
        at: Optional[str] = None,
        history: bool = False,
        labels: bool = True) -> Dict[str, Any]:
    """Query by projection: fix some roles, ask for others. Returns the CURRENT
    value of each asked role (the latest correction wins for single-valued roles);
    pass history=true for the full time-ordered trail. `type` filters to a category
    id (auto-registered verbs get `action_<verb>`). `at` (ISO-8601) reads the
    model's valid-time as of that moment. Results carry ids; `labels` maps each id
    to its readable name once (magnitudes to {value, unit}). Pass labels=false to
    skip it when you only need to chain ids."""
    return _session.ask(fixed, ask, type, at, history, labels)
```

- [ ] **Step 4: Ejecutar y ver que pasan**

Run: `/Users/joseabanto/WQuestions/.venv/bin/python -m pytest mcp-server/tests/test_session.py -q`
Expected: todos pasan

- [ ] **Step 5: Suite completa y commit**

```bash
/Users/joseabanto/WQuestions/.venv/bin/python -m pytest prototipo/tests mcp-server/tests -q
git add mcp-server/wquestions_mcp/session.py mcp-server/wquestions_mcp/server.py mcp-server/tests/test_session.py
git commit -m "feat(mcp): ask devuelve un diccionario de nombres

Las filas siguen llevando ids; labels los traduce una sola vez cada uno.
Los nodos de situación se omiten: su label es su id y repetirlo no informa."
```

---

### Task 3: `assert_fact` — escribir una tripleta sobre cualquier entidad

**Files:**
- Modify: `mcp-server/wquestions_mcp/session.py` (métodos `assert_fact`, `correct`, `_replay`)
- Modify: `mcp-server/wquestions_mcp/server.py`
- Test: `mcp-server/tests/test_session.py`, `mcp-server/tests/test_persistence.py`

**Interfaces:**
- Consumes: `_resolve_value`, `_parse_ts`, `_append_event` (ya existen).
- Produces: `WQSession.assert_fact(subject, role, value, valid_from=None, valid_to=None) -> {"ok", "fact"|"error"}`. La Tarea 4 invalida su índice desde aquí.

- [ ] **Step 1: Escribir los tests que fallan**

En `test_session.py`:

```python
def test_assert_fact_writes_an_attribute_on_a_q_entity():
    s = WQSession()
    s.add_entity("juan", "Q", "juan")
    out = s.assert_fact("juan", "nombre",
                        {"id": "lit_juan", "axis": "K", "label": "Juan Pérez"})
    assert out["ok"] is True
    assert out["fact"] == {"subject": "juan", "role": "nombre",
                           "value": "lit_juan"}
    assert s._display("juan") == "Juan Pérez"


def test_assert_fact_rejects_an_unknown_subject():
    s = WQSession()
    out = s.assert_fact("fantasma", "nombre",
                        {"id": "lit", "axis": "K", "label": "X"})
    assert out["ok"] is False
    assert "fantasma" in out["error"]


def test_assert_fact_enforces_the_catalog_signature():
    s = WQSession()
    s.add_entity("juan", "Q", "Juan")
    s.add_entity("t1", "T", "2026-01-01")
    out = s.assert_fact("juan", "momento", "t1")   # momento es O->T
    assert out["ok"] is False


def test_correct_accepts_a_non_situation_subject():
    s = WQSession()
    s.add_entity("juan", "Q", "Juan")
    s.assert_fact("juan", "nombre",
                  {"id": "lit_v", "axis": "K", "label": "Juan Viejo"})
    out = s.correct("juan", "nombre",
                    {"id": "lit_n", "axis": "K", "label": "Juan Nuevo"})
    assert out["ok"] is True
    assert s._display("juan") == "Juan Nuevo"
```

En `test_persistence.py`:

```python
def test_assert_fact_survives_a_replay(tmp_path):
    from wquestions_mcp.session import WQSession
    log = str(tmp_path / "u.jsonl")
    s = WQSession(log_path=log)
    s.add_entity("juan", "Q", "juan")
    s.assert_fact("juan", "nombre",
                  {"id": "lit_juan", "axis": "K", "label": "Juan Pérez"})
    del s
    s2 = WQSession(log_path=log)
    assert s2._skipped_lines == 0
    assert s2._display("juan") == "Juan Pérez"
```

- [ ] **Step 2: Ejecutar y ver que fallan**

Run: `/Users/joseabanto/WQuestions/.venv/bin/python -m pytest mcp-server/tests -k "assert_fact or correct_accepts" -v`
Expected: FAIL con `AttributeError: 'WQSession' object has no attribute 'assert_fact'`

- [ ] **Step 3: Implementar**

En `session.py`, añadir el método después de `define_verb`:

```python
    def assert_fact(self, subject: str, role: str, value: Any,
                    valid_from: Optional[str] = None,
                    valid_to: Optional[str] = None) -> Dict[str, Any]:
        """Asienta una tripleta binaria sobre una entidad existente, del eje que
        sea. Es la escritura que el motor siempre soportó y que el MCP tapaba
        tras la reificación obligatoria: un atributo de una persona no necesita
        un nodo intermedio, solo su vigencia."""
        subj = self.universe.individuals.get(subject)
        if subj is None:
            return {"ok": False,
                    "error": f"Unknown entity '{subject}'. Create it with "
                             f"add_entity first."}
        try:
            val = self._resolve_value(value)
            self.universe.assert_fact(
                subj, role, val,
                valid_from=self._parse_ts(valid_from),
                valid_to=self._parse_ts(valid_to))
        except (ValueError, IngestError) as e:
            return {"ok": False, "error": str(e)}
        self._append_event("assert_fact", {"subject": subject, "role": role,
                                           "value": value,
                                           "valid_from": valid_from,
                                           "valid_to": valid_to})
        return {"ok": True,
                "fact": {"subject": subj.id, "role": role, "value": val.id}}
```

En `correct`, borrar el bloque que exige eje O:

```python
        if situ.axis is not Axis.O:
            return {"ok": False,
                    "error": f"'{situation_id}' is in axis {situ.axis.value}, not "
                             f"a situation (O). Corrections attach to situations."}
```

y cambiar el mensaje de sujeto desconocido para que no hable solo de situaciones:

```python
        situ = self.universe.individuals.get(situation_id)
        if situ is None:
            return {"ok": False,
                    "error": f"Unknown entity '{situation_id}'. Pass a situation_id "
                             f"from assert_situation, or any existing entity id."}
```

En `_replay`, añadir la op al despacho:

```python
        dispatch = {
            "add_entity": self.add_entity,
            "define_verb": self.define_verb,
            "assert_situation": self.assert_situation,
            "assert_fact": self.assert_fact,
            "correct": self.correct,
            "load_example": self.load_example,
            "reset": self.reset,
        }
```

En `server.py`, añadir la herramienta después de `assert_situation`:

```python
@mcp.tool()
def assert_fact(subject: str, role: str, value: Any,
                valid_from: Optional[str] = None,
                valid_to: Optional[str] = None) -> Dict[str, Any]:
    """Assert one binary triplet (subject · role · value) directly on an existing
    entity of ANY axis — no situation is minted. Use it for properties of a thing
    (a person's name, a product's barcode) where there is nothing to reify. Use
    assert_situation instead when several participants take part in one fact. The
    role is checked against the catalog: `nombre` is Q->K, so it attaches to the
    person, not to a node about the person."""
    return _session.assert_fact(subject, role, value, valid_from, valid_to)
```

- [ ] **Step 4: Ejecutar y ver que pasan**

Run: `/Users/joseabanto/WQuestions/.venv/bin/python -m pytest mcp-server/tests -k "assert_fact or correct" -v`
Expected: todos pasan

- [ ] **Step 5: Suite completa y commit**

```bash
/Users/joseabanto/WQuestions/.venv/bin/python -m pytest prototipo/tests mcp-server/tests -q
git add mcp-server/wquestions_mcp/session.py mcp-server/wquestions_mcp/server.py mcp-server/tests/
git commit -m "feat(mcp): assert_fact escribe una tripleta sobre cualquier entidad

El catálogo declara nombre como Q->K pero no había forma de expresarlo:
assert_situation siempre mintea sujeto en O. Ahora un atributo cuelga de su
entidad y correct deja de exigir sujeto en O. Medido sobre yaku: ahorra
18.830 nodos-ficha y 37.660 hechos de andamiaje."
```

---

### Task 4: `find` — encontrar una entidad por su nombre

**Files:**
- Modify: `mcp-server/wquestions_mcp/session.py`
- Modify: `mcp-server/wquestions_mcp/server.py`
- Test: `mcp-server/tests/test_session.py`

**Interfaces:**
- Consumes: `WQSession._display(entity_id)` de la Tarea 1; `assert_fact` de la Tarea 3.
- Produces: `WQSession.find(text, axis=None, limit=20) -> {"count", "results", "truncated"}` donde cada resultado es `{"id", "axis", "label"}`.

- [ ] **Step 1: Escribir los tests que fallan**

```python
def test_find_matches_a_substring_ignoring_case_and_accents():
    s = WQSession()
    s.add_entity("cli_1", "Q", "ROMERO AZAÑERO, MARCELA")
    out = s.find("azanero")
    assert out["count"] == 1
    assert out["results"][0]["id"] == "cli_1"
    assert out["results"][0]["axis"] == "Q"
    assert out["results"][0]["label"] == "ROMERO AZAÑERO, MARCELA"


def test_find_can_filter_by_axis():
    s = WQSession()
    s.add_entity("cli_1", "Q", "SAUNA PLUS")     # una persona así llamada
    s.add_entity("pro_1", "O", "SAUNA PLUS")
    assert s.find("sauna")["count"] == 2
    out = s.find("sauna", axis="O")
    assert out["count"] == 1
    assert out["results"][0]["id"] == "pro_1"


def test_find_truncates_and_says_so():
    s = WQSession()
    for i in range(30):
        s.add_entity(f"cli_{i}", "Q", f"CLIENTE {i}")
    out = s.find("cliente", limit=10)
    assert len(out["results"]) == 10
    assert out["truncated"] is True
    assert out["count"] == 30


def test_find_sees_entities_added_after_the_first_search():
    s = WQSession()
    s.add_entity("cli_1", "Q", "Ana")
    assert s.find("beto")["count"] == 0        # construye el índice
    s.add_entity("cli_2", "Q", "Beto")
    assert s.find("beto")["count"] == 1        # y lo invalida al escribir


def test_find_uses_a_nombre_fact_over_the_label():
    s = WQSession()
    s.add_entity("juan", "Q", "juan")
    s.assert_fact("juan", "nombre",
                  {"id": "lit_j", "axis": "K", "label": "Juan Pérez"})
    assert s.find("perez")["count"] == 1


def test_find_rejects_an_empty_query():
    s = WQSession()
    out = s.find("   ")
    assert out["ok"] is False


def test_find_does_not_build_the_index_until_it_is_called():
    s = WQSession()
    s.add_entity("cli_1", "Q", "Ana")
    assert s._name_idx is None
    s.find("ana")
    assert s._name_idx is not None
```

- [ ] **Step 2: Ejecutar y ver que fallan**

Run: `/Users/joseabanto/WQuestions/.venv/bin/python -m pytest mcp-server/tests/test_session.py -k find -v`
Expected: FAIL con `AttributeError: 'WQSession' object has no attribute 'find'`

- [ ] **Step 3: Implementar**

En `session.py`, añadir el import arriba:

```python
import unicodedata
```

y la función de módulo junto a `NAME_ROLE`:

```python
def _norm(text: str) -> str:
    """Texto comparable: sin acentos y en mayúsculas. Sin esto, `azañero` no
    encuentra a AZAÑERO y media agenda peruana queda inalcanzable."""
    plain = unicodedata.normalize("NFD", text or "")
    return "".join(c for c in plain
                   if unicodedata.category(c) != "Mn").upper()
```

En `__init__`, antes de `self._fresh()`, y también dentro de `_fresh()`:

```python
        self._name_idx: Optional[Dict[str, List[str]]] = None
```

(en `__init__` basta declararlo; `_fresh` debe volver a ponerlo a `None`).

Añadir los métodos:

```python
    def _invalidate_name_index(self) -> None:
        self._name_idx = None

    def _name_index(self) -> Dict[str, List[str]]:
        """Índice nombre-normalizado -> ids, construido la primera vez que se
        busca y no al arrancar: sobre 539 k entidades cuesta ~2,6 s, y un
        universo que nunca busca no debe pagarlos."""
        if self._name_idx is None:
            idx: Dict[str, List[str]] = {}
            for eid in self.universe.individuals:
                name = self._display(eid)
                if isinstance(name, str):
                    idx.setdefault(_norm(name), []).append(eid)
            self._name_idx = idx
        return self._name_idx

    def find(self, text: str, axis: Optional[str] = None,
             limit: int = 20) -> Dict[str, Any]:
        """Busca entidades por su nombre. Subcadena, sin distinguir mayúsculas
        ni acentos."""
        needle = _norm(text).strip()
        if not needle:
            return {"ok": False,
                    "error": "Pass some text to search for."}
        if axis is not None and axis not in _AXIS_NAMES:
            return {"ok": False,
                    "error": f"Unknown axis '{axis}'. Use one of Q,O,L,T,N,K."}
        hits: List[Dict[str, Any]] = []
        for key, ids in self._name_index().items():
            if needle not in key:
                continue
            for eid in ids:
                ind = self.universe.individuals.get(eid)
                if ind is None or (axis is not None and ind.axis.value != axis):
                    continue
                hits.append({"id": eid, "axis": ind.axis.value,
                             "label": self._display(eid)})
        hits.sort(key=lambda h: (len(h["label"]), h["id"]))
        return {"count": len(hits), "results": hits[:limit],
                "truncated": len(hits) > limit}
```

Invalidar el índice en cada escritura. Al final de `add_entity` (justo antes del `return {"ok": True, ...}`), de `assert_fact`, de `correct` y de `assert_situation`, añadir:

```python
        self._invalidate_name_index()
```

En `server.py`:

```python
@mcp.tool()
def find(text: str, axis: Optional[str] = None,
         limit: int = 20) -> Dict[str, Any]:
    """Find entities by name — the way in when you know what something is called
    but not its id. Matches a substring, ignoring case and accents ("azanero"
    finds AZAÑERO). `axis` narrows to one value axis (Q for people, O for things).
    Returns {id, axis, label}; feed those ids to `ask`. `truncated` says there
    were more matches than `limit`."""
    return _session.find(text, axis, limit)
```

- [ ] **Step 4: Ejecutar y ver que pasan**

Run: `/Users/joseabanto/WQuestions/.venv/bin/python -m pytest mcp-server/tests/test_session.py -k find -v`
Expected: 7 passed

- [ ] **Step 5: Suite completa y commit**

```bash
/Users/joseabanto/WQuestions/.venv/bin/python -m pytest prototipo/tests mcp-server/tests -q
git add mcp-server/wquestions_mcp/session.py mcp-server/wquestions_mcp/server.py mcp-server/tests/test_session.py
git commit -m "feat(mcp): find encuentra una entidad por su nombre

Era el hueco que tapiaba la puerta por dentro: labels dejaba salir los
nombres pero no entrar por ellos. Índice normalizado y perezoso: el escaneo
lineal sobre 539k entidades cuesta ~1s, el índice 13,5 ms."
```

---

### Task 5: Rangos en `fixed`

**Files:**
- Modify: `prototipo/wq/query.py`
- Modify: `mcp-server/wquestions_mcp/session.py` (método `ask`)
- Test: `prototipo/tests/test_wq.py`, `mcp-server/tests/test_session.py`

**Interfaces:**
- Consumes: `Pattern`, `query` de `wq.query`.
- Produces: `wq.query.Rango(desde=None, hasta=None)`, aceptado dentro de `Pattern.fixed`. `session.ask` traduce `{"desde":…, "hasta":…}` a `Rango`.

- [ ] **Step 1: Escribir los tests que fallan**

En `prototipo/tests/test_wq.py`:

```python
def test_rango_sobre_t_filtra_por_periodo():
    from wq import Universe, Catalog, Individual, Pattern, Var, query
    from wq.query import Rango
    from wq.axes import Axis
    u = Universe(name="t", catalog=Catalog())
    ana = u.add_individual(Individual(id="ana", axis=Axis.Q, label="Ana"))
    for dia in ("2025-06-01", "2026-03-15", "2026-11-02"):
        t = u.add_individual(Individual(id=f"t_{dia}", axis=Axis.T, label=dia))
        s = u.add_individual(Individual(id=f"s_{dia}", axis=Axis.O,
                                        label=f"s_{dia}"))
        u.assert_fact(s, "agente", ana)
        u.assert_fact(s, "momento", t)
    p = Pattern(fixed={"agente": ana,
                       "momento": Rango(desde="2026-01-01", hasta="2026-12-31")},
                ask={"momento": Var("momento")})
    assert len(query(u, p)) == 2


def test_rango_sobre_n_filtra_por_valor():
    from wq import Universe, Catalog, Individual, Pattern, Var, query
    from wq.query import Rango
    from wq.axes import Axis
    u = Universe(name="t", catalog=Catalog())
    ana = u.add_individual(Individual(id="ana", axis=Axis.Q, label="Ana"))
    for i, val in enumerate((10.0, 150.0, 900.0)):
        n = u.add_individual(Individual(id=f"n{i}", axis=Axis.N, label=str(val),
                                        payload={"value": val, "unit": "pen"}))
        s = u.add_individual(Individual(id=f"s{i}", axis=Axis.O, label=f"s{i}"))
        u.assert_fact(s, "agente", ana)
        u.assert_fact(s, "por_cuanto", n)
    p = Pattern(fixed={"agente": ana, "por_cuanto": Rango(desde=100)},
                ask={"por_cuanto": Var("por_cuanto")})
    assert len(query(u, p)) == 2
```

En `mcp-server/tests/test_session.py`:

```python
def test_ask_accepts_a_range_on_momento():
    s = WQSession()
    s.add_entity("ana", "Q", "Ana")
    for dia in ("2025-06-01", "2026-03-15", "2026-11-02"):
        s.add_entity(f"t_{dia}", "T", dia)
        s.assert_situation("vender", {"agente": "ana", "momento": f"t_{dia}"})
    out = s.ask(fixed={"agente": "ana",
                       "momento": {"desde": "2026-01-01", "hasta": "2026-12-31"}},
                ask=["momento"])
    assert out["count"] == 2


def test_ask_range_on_an_axis_without_order_is_an_error():
    s = WQSession()
    s.add_entity("ana", "Q", "Ana")
    s.assert_situation("vender", {"agente": "ana"})
    out = s.ask(fixed={"agente": {"desde": "a", "hasta": "z"}}, ask=["agente"])
    assert out["ok"] is False
```

- [ ] **Step 2: Ejecutar y ver que fallan**

Run: `/Users/joseabanto/WQuestions/.venv/bin/python -m pytest prototipo/tests/test_wq.py -k rango mcp-server/tests/test_session.py -k range -v`
Expected: FAIL con `ImportError: cannot import name 'Rango'`

- [ ] **Step 3: Implementar en `query.py`**

Añadir después de la clase `Var`:

```python
@dataclass
class Rango:
    """Un extremo abierto o cerrado sobre un eje ordenado (T o N).

    `desde` y `hasta` son inclusivos y cualquiera puede faltar. Sobre T se
    compara el `datetime` del payload si lo hay y la cadena ISO del label si no;
    sobre N, el valor numérico del payload.
    """
    desde: Any = None
    hasta: Any = None


def _comparable(ind: Individual) -> Any:
    """El valor ordenable de un individuo, o None si su eje no ordena."""
    if ind.axis is Axis.N and isinstance(ind.payload, dict):
        return ind.payload.get("value")
    if ind.axis is Axis.T:
        return ind.payload if ind.payload is not None else (ind.label or ind.id)
    return None


def _coerce(extremo: Any, muestra: Any) -> Any:
    """Lleva el extremo al tipo del valor con que se va a comparar."""
    if isinstance(muestra, datetime) and isinstance(extremo, str):
        return datetime.fromisoformat(extremo.replace("Z", "+00:00"))
    if isinstance(muestra, (int, float)) and isinstance(extremo, str):
        return float(extremo)
    if isinstance(muestra, str) and isinstance(extremo, datetime):
        return extremo.isoformat()
    return extremo


def _en_rango(ind: Individual, rango: Rango) -> bool:
    valor = _comparable(ind)
    if valor is None:
        return False
    if rango.desde is not None and valor < _coerce(rango.desde, valor):
        return False
    if rango.hasta is not None and valor > _coerce(rango.hasta, valor):
        return False
    return True
```

Añadir el import de `Axis` arriba del módulo (junto a los que ya hay):

```python
from .axes import Axis
```

En `query()`, el punto 1 debe ignorar los rangos al elegir ancla:

```python
    exactos = {r: v for r, v in pattern.fixed.items()
               if not isinstance(v, Rango)}
    rangos = {r: v for r, v in pattern.fixed.items()
              if isinstance(v, Rango)}

    if exactos:
        # Ancla: de los roles fijos de valor exacto, el que tiene el VALOR más
        # selectivo. Se indexa por valor, no por rol.
        role0, val0 = min(
            exactos.items(),
            key=lambda rv: len(universe._by_value.get(rv[1].id, ())),
        )
        candidate_subjects = {
            f.subject.id
            for f in universe.facts_with_value(val0, at=at)
            if f.role == role0
        }
    elif pattern.type_constraint is not None:
        candidate_subjects = {
            f.subject.id
            for f in universe.facts_with_role("instancia_de", at=at)
            if f.value.id == pattern.type_constraint.id
        }
    elif rangos:
        # Sin ningún valor exacto: se recorren los hechos del primer rol acotado.
        role0 = next(iter(rangos))
        candidate_subjects = {f.subject.id
                              for f in universe.facts_with_role(role0, at=at)}
    else:
        candidate_subjects = set(universe.individuals.keys())
```

Y en el punto 2, sustituir el chequeo de roles fijos por uno que distinga:

```python
        ok = True
        for role, expected in pattern.fixed.items():
            vals = roles_map.get(role, [])
            if isinstance(expected, Rango):
                if not any(_en_rango(v, expected) for v in vals):
                    ok = False
                    break
            elif not any(v.id == expected.id for v in vals):
                ok = False
                break
        if not ok:
            continue
```

Exportar `Rango` en `prototipo/wq/__init__.py`: añadirlo al import de `.query` y a `__all__`.

- [ ] **Step 4: Implementar en `session.py`**

En `ask`, antes de construir el `Pattern`, traducir los dicts de rango:

```python
            fixed_ind: Dict[str, Any] = {}
            for role, spec in (fixed or {}).items():
                if isinstance(spec, dict) and ("desde" in spec or "hasta" in spec):
                    fixed_ind[role] = Rango(desde=spec.get("desde"),
                                            hasta=spec.get("hasta"))
                else:
                    fixed_ind[role] = self._resolve_value(spec)
```

Importar `Rango` arriba:

```python
from wq import Pattern, Var, query, category, Rango
```

El error del eje sin orden sale solo: `_en_rango` devuelve `False` para Q/K y la consulta no encuentra nada. Para que sea un error explícito y no un cero silencioso, validar en `ask` justo después de traducir:

```python
            for role, spec in fixed_ind.items():
                if isinstance(spec, Rango):
                    sig = self.catalog.get(role)
                    if sig is not None and sig.range.value not in ("T", "N"):
                        raise ValueError(
                            f"Role '{role}' ranges over {sig.range.value}; only "
                            f"T and N are ordered. Pass an exact value instead.")
```

- [ ] **Step 5: Ejecutar y commitear**

```bash
/Users/joseabanto/WQuestions/.venv/bin/python -m pytest prototipo/tests mcp-server/tests -q
git add prototipo/wq/query.py prototipo/wq/__init__.py mcp-server/wquestions_mcp/session.py prototipo/tests/test_wq.py mcp-server/tests/test_session.py
git commit -m "feat(mcp): rangos en fixed para T y N

ask fijaba valores exactos, así que 'los consumos de este año' no se podía
expresar. El ancla sigue prefiriendo los roles de valor exacto y el rango se
aplica como filtro; solo escanea cuando es la única condición."
```

---

### Task 6: `agrupar_por` / `medir` — agregación

**Files:**
- Modify: `mcp-server/wquestions_mcp/session.py`
- Modify: `mcp-server/wquestions_mcp/server.py`
- Test: `mcp-server/tests/test_session.py`

**Interfaces:**
- Consumes: `_labels_for` (Tarea 2), `Rango` (Tarea 5), `wq.magnitud.Magnitud`.
- Produces: `ask(..., agrupar_por=None, medir=None, orden=None, limite=None)`.

- [ ] **Step 1: Escribir los tests que fallan**

```python
def _universo_de_ventas():
    s = WQSession()
    s.add_entity("pen", "K", "PEN")
    s.add_entity("ana", "Q", "Ana")
    s.add_entity("sauna", "O", "SAUNA")
    s.add_entity("agua", "O", "AGUA")
    for tema, precio in (("sauna", 25.0), ("sauna", 25.0), ("agua", 2.5)):
        s.assert_situation("vender", {
            "agente": "ana", "tema": tema,
            "por_cuanto": {"id": f"n_{tema}_{precio}", "axis": "N",
                           "value": precio, "unit": "pen"}})
    return s


def test_ask_groups_and_counts():
    s = _universo_de_ventas()
    out = s.ask(type="action_vender", agrupar_por="tema",
                medir={"veces": "count"})
    filas = {r["tema"]: r["veces"] for r in out["results"]}
    assert filas == {"sauna": 2, "agua": 1}
    assert out["labels"]["sauna"] == "SAUNA"


def test_ask_sums_magnitudes_with_their_unit():
    s = _universo_de_ventas()
    out = s.ask(type="action_vender", agrupar_por="tema",
                medir={"importe": {"sum": "por_cuanto"}})
    filas = {r["tema"]: r["importe"] for r in out["results"]}
    assert filas["sauna"] == {"value": 50.0, "unit": "PEN"}


def test_ask_orders_and_limits_groups():
    s = _universo_de_ventas()
    out = s.ask(type="action_vender", agrupar_por="tema",
                medir={"veces": "count"}, orden="-veces", limite=1)
    assert [r["tema"] for r in out["results"]] == ["sauna"]


def test_ask_refuses_to_sum_incommensurable_units():
    s = _universo_de_ventas()
    s.add_entity("kg", "K", "KG")
    s.assert_situation("vender", {
        "agente": "ana", "tema": "sauna",
        "por_cuanto": {"id": "n_kg", "axis": "N", "value": 3.0, "unit": "kg"}})
    out = s.ask(type="action_vender", agrupar_por="tema",
                medir={"importe": {"sum": "por_cuanto"}})
    assert out["ok"] is False
    assert "unit" in out["error"].lower()


def test_ask_without_agrupar_por_gives_a_grand_total():
    s = _universo_de_ventas()
    out = s.ask(type="action_vender", medir={"veces": "count"})
    assert out["results"] == [{"veces": 3}]
```

- [ ] **Step 2: Ejecutar y ver que fallan**

Run: `/Users/joseabanto/WQuestions/.venv/bin/python -m pytest mcp-server/tests/test_session.py -k "groups or sums or orders_and_limits or incommensurable or grand_total" -v`
Expected: FAIL con `TypeError: ask() got an unexpected keyword argument 'agrupar_por'`

- [ ] **Step 3: Implementar**

Importar arriba de `session.py`:

```python
from wq.magnitud import Magnitud, ErrorDimensional
```

Añadir los métodos auxiliares antes de `ask`:

```python
    def _sumar(self, valores: List[Individual]) -> Dict[str, Any]:
        """Suma magnitudes respetando la unidad. Sumar soles con kilos da error,
        no un número: la regla del eje N aplicada a la consulta."""
        unidades = {v.payload.get("unit") for v in valores
                    if isinstance(v.payload, dict)}
        if len(unidades) != len(valores) and not unidades:
            raise ErrorDimensional("Cannot sum values that are not magnitudes.")
        if len(unidades) == 1:
            uid = unidades.pop()
            ind = self.universe.individuals.get(uid)
            return {"value": sum(float(v.payload["value"]) for v in valores),
                    "unit": (ind.label or uid) if ind else uid}
        destino = valores[0].payload["unit"]
        total = Magnitud.de(self.universe, valores[0])
        for v in valores[1:]:
            total = total.mas(Magnitud.de(self.universe, v))
        conv = total.convertir_a(self.universe, destino)
        ind = self.universe.individuals.get(destino)
        return {"value": conv.valor,
                "unit": (ind.label or destino) if ind else destino}

    def _medida(self, spec: Any, valores: List[Individual]) -> Any:
        if spec == "count":
            return len(valores)
        if not isinstance(spec, dict) or len(spec) != 1:
            raise ValueError(
                f"Bad measure {spec!r}. Use \"count\" or {{\"sum\"|\"min\"|"
                f"\"max\"|\"avg\": \"<role>\"}}.")
        op = next(iter(spec))
        if not valores:
            return None
        if op == "sum":
            return self._sumar(valores)
        nums = [float(v.payload["value"]) for v in valores
                if isinstance(v.payload, dict) and "value" in v.payload]
        if not nums:
            raise ValueError(f"'{op}' needs magnitudes with a numeric value.")
        if op == "min":
            return min(nums)
        if op == "max":
            return max(nums)
        if op == "avg":
            return sum(nums) / len(nums)
        raise ValueError(f"Unknown measure '{op}'.")
```

Y el agregador, también antes de `ask`:

```python
    def _agregar(self, bindings, agrupar_por, medir, orden, limite, at):
        """Agrupa las situaciones candidatas y calcula las medidas pedidas."""
        grupos: Dict[Any, Dict[str, List[Individual]]] = {}
        for b in bindings:
            facts = self.universe.facts_about(b["_subject"], at=at)
            roles: Dict[str, List[Individual]] = {}
            for f in facts:
                roles.setdefault(f.role, []).append(f.value)
            clave = None
            if agrupar_por is not None:
                vals = roles.get(agrupar_por, [])
                if not vals:
                    continue
                clave = vals[-1].id
            bucket = grupos.setdefault(clave, {"_n": []})
            bucket["_n"].append(b["_subject"])
            for nombre, spec in medir.items():
                if isinstance(spec, dict):
                    rol = next(iter(spec.values()))
                    bucket.setdefault(nombre, []).extend(roles.get(rol, []))

        filas = []
        for clave, bucket in grupos.items():
            fila: Dict[str, Any] = {}
            if agrupar_por is not None:
                fila[agrupar_por] = clave
            for nombre, spec in medir.items():
                fila[nombre] = self._medida(
                    spec, bucket["_n"] if spec == "count"
                    else bucket.get(nombre, []))
            filas.append(fila)

        if orden:
            desc = orden.startswith("-")
            campo = orden[1:] if desc else orden
            def clave_orden(f):
                v = f.get(campo)
                return v["value"] if isinstance(v, dict) else (v or 0)
            filas.sort(key=clave_orden, reverse=desc)
        if limite:
            filas = filas[:limite]
        return filas
```

Extender la firma de `ask` y su cuerpo:

```python
    def ask(self, fixed: Optional[Dict[str, Any]] = None,
            ask: Optional[List[str]] = None,
            type: Optional[str] = None,
            at: Optional[str] = None,
            history: bool = False,
            labels: bool = True,
            agrupar_por: Optional[str] = None,
            medir: Optional[Dict[str, Any]] = None,
            orden: Optional[str] = None,
            limite: Optional[int] = None) -> Dict[str, Any]:
```

Dentro del `try`, después de obtener `bindings`, bifurcar:

```python
            if medir is not None:
                if ask:
                    raise ValueError(
                        "Use either `ask` (project rows) or `medir` (aggregate "
                        "groups), not both.")
                results = self._agregar(bindings, agrupar_por, medir,
                                        orden, limite, at_dt)
            else:
                results = []
                for b in bindings:
                    ...   # el bucle que ya existe, sin tocar
```

y capturar también el error dimensional:

```python
        except (ValueError, IngestError, ErrorDimensional) as e:
            return {"ok": False, "error": str(e)}
```

En `server.py`, extender la herramienta `ask`:

```python
@mcp.tool()
def ask(fixed: Optional[Dict[str, Any]] = None,
        ask: Optional[List[str]] = None,
        type: Optional[str] = None,
        at: Optional[str] = None,
        history: bool = False,
        labels: bool = True,
        agrupar_por: Optional[str] = None,
        medir: Optional[Dict[str, Any]] = None,
        orden: Optional[str] = None,
        limite: Optional[int] = None) -> Dict[str, Any]:
    """Query by projection or by aggregation.

    PROJECT: fix some roles, ask for others. A value in `fixed` may be an id or a
    range {"desde":…, "hasta":…} over T or N. Results carry ids; `labels` maps
    each id to its readable name once.

    AGGREGATE: pass `medir` instead of `ask` — {"veces":"count",
    "importe":{"sum":"por_cuanto"}} — optionally with `agrupar_por` (a role),
    `orden` ("-importe" for descending) and `limite`. Sums check units: adding
    soles to kilos is an error, not a number. Without `agrupar_por` you get one
    grand-total row."""
    return _session.ask(fixed, ask, type, at, history, labels,
                        agrupar_por, medir, orden, limite)
```

- [ ] **Step 4: Ejecutar y ver que pasan**

Run: `/Users/joseabanto/WQuestions/.venv/bin/python -m pytest mcp-server/tests/test_session.py -q`
Expected: todos pasan

- [ ] **Step 5: Suite completa y commit**

```bash
/Users/joseabanto/WQuestions/.venv/bin/python -m pytest prototipo/tests mcp-server/tests -q
git add mcp-server/wquestions_mcp/session.py mcp-server/wquestions_mcp/server.py mcp-server/tests/test_session.py
git commit -m "feat(mcp): agrupar_por y medir — agregación con unidades

Un 'top N productos' exigía traer 243k filas por el protocolo. Las sumas
comprueban unidad: sumar soles con kilos devuelve error, no un número."
```

---

### Task 7: Derivar `importe` por línea en la migración yaku

**Files:**
- Modify: `/private/tmp/claude-501/-Users-joseabanto-WQuestions/0f6cba1f-a730-4590-abce-5aac52bbd3bb/scratchpad/yaku_migrar2.py`
- Test: verificación extremo a extremo contra el SQL, no pytest.

**Interfaces:**
- Consumes: `assert_fact` (Tarea 3), `agrupar_por`/`medir` (Tarea 6).
- Produces: un hecho `(linea, importe, N)` por cada situación `accion_vender`.

- [ ] **Step 1: Declarar la unidad de conteo como adimensional**

En el bloque de vocabulario de `yaku_migrar2.py`, sustituir `s.add_entity(UND, "K", "unidad")` por una declaración con física:

```python
    # Contar no tiene dimensión. Sin esto, `pen * unidad` da la dimensión
    # compuesta pen·unidad y no convierte a pen. Verificado.
    from wq.derivacion import declarar_unidad, declarar_unidades_base
    declarar_unidades_base(s.universe)
    declarar_unidad(s.universe, UND, label="unidad", factor=1.0)
```

- [ ] **Step 2: Declarar la regla como entidad del grafo**

Justo después, en el mismo bloque:

```python
    s.add_entity("regla_de_derivacion", "K", "regla de derivación")
    s.add_entity("regla_importe_linea", "O", "importe = precio x cantidad")
    s.add_entity("expr_importe", "K", "por_cuanto * cantidad")
    for rol, val in (("instancia_de", "regla_de_derivacion"),
                     ("expresion", "expr_importe"),
                     ("unidad_destino", "pen")):
        r = s.assert_fact("regla_importe_linea", rol, val)
        if not r.get("ok"):
            print("ERROR regla:", r); sys.exit(1)
```

- [ ] **Step 3: Derivar el importe al asentar cada línea**

En el bloque de `ventadet`, después de `res = asentar(s, "vender", roles)` y solo cuando la línea tiene precio y cantidad:

```python
            if res.get("ok") and precio is not None and roles.get("cantidad"):
                from wq.derivacion import evaluar
                from wq.magnitud import ErrorDimensional
                try:
                    m = evaluar(s.universe, "por_cuanto * cantidad",
                                s.universe.individuals[res["situation_id"]])
                    imp = m.convertir_a(s.universe, "pen")
                    s.assert_fact(res["situation_id"], "importe",
                                  c.magnitud(imp.valor, PEN))
                    n_importe += 1
                except ErrorDimensional as e:
                    err_importe.append(str(e))
```

Inicializar los contadores junto a los demás (`n_vender = n_cobrar = n_mov = 0`):

```python
    n_importe = 0
    err_importe = []
```

y reportarlos en el resumen:

```python
    print(f"    hechos `importe` derivados .... {n_importe:>10,}")
    if err_importe:
        print(f"    !! errores dimensionales ...... {len(err_importe):,}"
              f"  ej: {err_importe[0][:70]}")
```

- [ ] **Step 4: Correr la migración y verificar contra el SQL**

```bash
cd /private/tmp/claude-501/-Users-joseabanto-WQuestions/0f6cba1f-a730-4590-abce-5aac52bbd3bb/scratchpad
/Users/joseabanto/WQuestions/.venv/bin/python yaku_migrar2.py --log
```

Expected: `hechos importe derivados` ≈ 243.000 y **cero** errores dimensionales.

Después, comprobar que la agregación por MCP da el mismo total que el SQL:

```python
out = s.ask(type="accion_vender", agrupar_por="tema",
            medir={"importe": {"sum": "importe"}},
            orden="-importe", limite=5)
```

El primer grupo debe ser SAUNA con S/ 1.436.853,69 — el número que salió al recorrer el universo a mano.

- [ ] **Step 5: Publicar el universo nuevo y commitear el script**

```bash
cp yaku_v2.jsonl ~/.wquestions/yaku.jsonl
git add docs/superpowers/plans/2026-08-05-mcp-cinco-huecos.md
git commit -m "feat(yaku): deriva importe por línea con el motor de derivación

sum(por_cuanto) sumaría precios unitarios; el importe real es precio x
cantidad. La aritmética vive en los datos, no en el lenguaje de consulta.
Exige declarar la unidad de conteo como adimensional."
```

---

### Task 8: Cerrar el círculo — las cinco preguntas que no se podían contestar

**Files:**
- Create: `/private/tmp/claude-501/-Users-joseabanto-WQuestions/0f6cba1f-a730-4590-abce-5aac52bbd3bb/scratchpad/yaku_mcp_e2e.py`

**Interfaces:**
- Consumes: todo lo anterior.
- Produces: nada; es la comprobación de que el objetivo se cumplió.

- [ ] **Step 1: Escribir el guion extremo a extremo**

```python
#!/usr/bin/env python3
"""Las cinco preguntas que ayer exigieron salir del MCP, ahora dentro de él."""
import sys, time
sys.path.insert(0, "/Users/joseabanto/WQuestions/prototipo")
sys.path.insert(0, "/Users/joseabanto/WQuestions/mcp-server")
from wquestions_mcp.session import WQSession

s = WQSession(log_path="/Users/joseabanto/.wquestions/yaku.jsonl")

def paso(titulo, fn):
    t0 = time.perf_counter()
    out = fn()
    print(f"\n▸ {titulo}  ({(time.perf_counter()-t0)*1000:.1f} ms)")
    return out

r = paso("1. encontrar al cliente por su nombre",
         lambda: s.find("abanto marin, jose", axis="Q"))
print(f"   {r['count']} fichas: {[x['label'] for x in r['results'][:3]]}")
cid = r["results"][0]["id"]

r = paso("2. sus consumos, con nombres",
         lambda: s.ask(fixed={"beneficiario": cid}, ask=["tema"],
                       type="accion_vender"))
print(f"   {r['count']} lineas · {len(r['labels'])} nombres resueltos")

r = paso("3. solo los de 2026",
         lambda: s.ask(fixed={"beneficiario": cid,
                              "momento": {"desde": "2026-01-01",
                                          "hasta": "2026-12-31"}},
                       ask=["tema"], type="accion_vender"))
print(f"   {r['count']} lineas de 2026")

r = paso("4. cuanto suma eso",
         lambda: s.ask(fixed={"beneficiario": cid,
                              "momento": {"desde": "2026-01-01",
                                          "hasta": "2026-12-31"}},
                       type="accion_vender",
                       medir={"importe": {"sum": "importe"}}))
print(f"   {r['results']}")

r = paso("5. el producto record",
         lambda: s.ask(type="accion_vender", agrupar_por="tema",
                       medir={"veces": "count",
                              "importe": {"sum": "importe"}},
                       orden="-importe", limite=5))
for fila in r["results"]:
    nombre = r["labels"].get(fila["tema"], fila["tema"])
    print(f"   {nombre[:34]:<36} {fila['veces']:>7,} x  "
          f"S/ {fila['importe']['value']:>12,.2f}")
print()
```

- [ ] **Step 2: Ejecutarlo**

```bash
/Users/joseabanto/WQuestions/.venv/bin/python yaku_mcp_e2e.py
```

Expected: las cinco preguntas responden con nombres legibles. La 5 debe encabezarla SAUNA con ~S/ 1.436.853,69, y la 4 debe dar S/ 622,50 (el consumo de 2026 sin los cobros, que son otro verbo).

- [ ] **Step 3: Actualizar el README del servidor**

En `mcp-server/README.md`, añadir a la tabla de herramientas las dos nuevas filas, después de `ask`:

```markdown
| `find` | Find entities by name (substring, ignores case and accents) — the way in when you know the name but not the id |
| `assert_fact` | Assert one triplet directly on an existing entity of any axis, for properties that need no situation |
```

y en la fila de `ask`, sustituir su descripción por:

```markdown
| `ask` | Query by projection or aggregation: fix roles (exact values or `{desde,hasta}` ranges over T/N), project with `ask` or group with `agrupar_por`/`medir`; returns a `labels` dictionary naming every id once |
```

- [ ] **Step 4: Commit final**

```bash
/Users/joseabanto/WQuestions/.venv/bin/python -m pytest prototipo/tests mcp-server/tests -q
git add mcp-server/README.md
git commit -m "docs(mcp): documenta find, assert_fact y el ask ampliado"
```

---

## Self-Review

**Cobertura del spec:**

| sección del spec | tarea |
|---|---|
| 1. `assert_fact` + `correct` sin exigir O | 3 |
| 1bis. `find` con índice perezoso | 4 |
| 2. `labels` en `ask` | 2 (resolución en 1) |
| 3. Rangos en `fixed` | 5 |
| 4. `agrupar_por` / `medir` | 6 |
| 5. Derivar `importe` | 7 |
| Compatibilidad (128 tests) | paso final de cada tarea |
| Pruebas enumeradas en el spec | 1-6, más el e2e en 8 |

**Consistencia de tipos:** `_display` devuelve `str | dict | None` y así lo consumen `_labels_for` (Tarea 2) y `_name_index` (Tarea 4, que filtra con `isinstance(name, str)` para no indexar magnitudes). `Rango` se define en `query.py` (Tarea 5) y se importa en `session.py` en la misma tarea. `_medida` recibe `spec` tal cual viene de `medir`, y `_agregar` le pasa la lista de sujetos cuando es `"count"` y la lista de valores del rol cuando es un dict.

**Riesgo conocido:** el spec pedía que un rango sobre un eje sin orden diera error explícito. La validación por catálogo solo alcanza a los roles declarados; un rol libre con rango sobre Q devolverá cero resultados en vez de error. Se acepta y se anota aquí: endurecerlo exigiría tipar los roles libres, que es la fricción #2 del stress test y queda fuera.
