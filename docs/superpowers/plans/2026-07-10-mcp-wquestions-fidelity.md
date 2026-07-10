# WQuestions MCP Fidelity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the `wquestions` MCP teach and expose WQuestions' real mechanisms so a model holding only the MCP stays inside the standard instead of confabulating parallel structure (hand-rolled auditing, unit roles, provenance).

**Architecture:** Thin MCP layer over the untouched `wq` engine. Two moves: (1) *teach* — a server `instructions` constitution plus enriched return payloads, docstrings, and redirecting errors; (2) *unblock* — close the two affordance gaps (`add_entity` value+unit for N; a `correct` tool + latest-`tx_time` resolution in `ask`). All logic lives in `WQSession` (`session.py`); `server.py` stays a thin wrapper.

**Tech Stack:** Python 3.12 (venv), MCP Python SDK (FastMCP), the `wq` engine (pure Python), pytest.

## Global Constraints

- **Do NOT modify the `wq` engine.** Wrap it as-is via its public API (`quantity`, `assert_fact`, `facts_about`, `Fact.tx_time`, `Catalog.get`). No edits under `prototipo/wq/`.
- **All user-facing strings in English** (server `instructions`, docstrings, enriched returns, error messages). Spanish stays in the book.
- **Liberal role policy preserved:** never register domain roles in `catalog.py`; enrichment only *documents* roles in return payloads.
- **Value axes:** Q, O, L, T, N, K hold entities; M/V do not.
- **Run every command through the venv by explicit path.** System `python3` is 3.9 and MUST NOT be used. Tests run from `mcp-server/`:
  `cd /Users/joseabanto/WQuestions/mcp-server && /Users/joseabanto/WQuestions/.venv/bin/pytest ...`
- **Non-goals:** no provenance/authorship tracking; no durable persistence (in-memory behavior is documented, not changed); no closed vocabulary.

## File Structure

- `mcp-server/wquestions_mcp/server.py` — MCP wrapper. Gains: `INSTRUCTIONS` constant passed to `FastMCP`; new `value`/`unit` params on `add_entity`; new `correct` tool; new `history` param on `ask`; richer docstrings. Stays logic-free.
- `mcp-server/wquestions_mcp/session.py` — all logic. Gains: `_AXIS_GUIDE`; enriched `list_axes`/`list_roles`/`show_model`; N value+unit in `_individual`/`add_entity`/`_resolve_value`; new `correct`; `history` + `_project_role` in `ask`.
- `mcp-server/tests/test_session.py` — extend with tests for every behavior change (session-level, no MCP runtime).
- `mcp-server/tests/test_server.py` — NEW, tiny: asserts the `INSTRUCTIONS` constitution is wired and covers the key mechanisms.

---

### Task 1: Server instructions constitution + core teaching docstrings

**Files:**
- Modify: `mcp-server/wquestions_mcp/server.py`
- Test: `mcp-server/tests/test_server.py` (create)

**Interfaces:**
- Produces: module-level `INSTRUCTIONS: str` in `server.py`; `mcp = FastMCP("wquestions", instructions=INSTRUCTIONS)`.

- [ ] **Step 1: Write the failing test**

Create `mcp-server/tests/test_server.py`:

```python
from wquestions_mcp.server import mcp, INSTRUCTIONS


def test_instructions_cover_key_mechanisms():
    text = INSTRUCTIONS.lower()
    for phrase in ["triplet", "reified", "valid_from", "unit",
                   "append-only", "in-memory", "correct("]:
        assert phrase in text, f"instructions missing: {phrase}"


def test_fastmcp_is_wired_with_instructions():
    assert mcp.instructions
    assert "wquestions" in mcp.instructions.lower()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /Users/joseabanto/WQuestions/mcp-server && /Users/joseabanto/WQuestions/.venv/bin/pytest tests/test_server.py -v`
Expected: FAIL with `ImportError: cannot import name 'INSTRUCTIONS'`.

- [ ] **Step 3: Add the INSTRUCTIONS constant and wire it**

In `server.py`, replace the line `mcp = FastMCP("wquestions")` with the constant plus a wired constructor:

```python
INSTRUCTIONS = """\
WQuestions models any domain as one fact space over 7 axes:
Q who · O what · L where · T when · N how-much · K which/kind · M how (predicates).

HOW STORAGE WORKS
- Everything is stored as binary triplets: subject · role · value. No prose, no
  rows — only triplets.
- A fact with many participants (a sale with seller, buyer, item, price, time) is
  reified: the situation becomes its own node in O and each participant hangs off
  it as one triplet. assert_situation does this and returns the triplets it made.

WHAT IS OPEN — invent freely (this is the point)
- Entities, verbs and roles are open-world. Coin new domain entities (add_entity),
  new verbs (assert_situation auto-registers them) and new roles as you need them.
  No catalog and no permission required.

WHAT THE STANDARD ALREADY HANDLES — do not build it yourself
- Corrections & time. To record that a fact changed in the world over time, set
  valid_from/valid_to and read the past with ask(at=...). To fix a value you
  recorded wrong, call correct(situation_id, role, new_value): it re-asserts the
  role. ask returns the current (latest) value and keeps the previous one as
  history (ask(history=true)). You do not track current-vs-superseded yourself.
- Magnitudes carry a unit. Every N value has a unit that lives in K. Create a
  magnitude with add_entity(id, "N", value=<number>, unit=<K id or spec>). Never
  bake the unit into an id or label, and never assume a currency or unit — if a
  number arrives without one, ask for it.
- Authorship / provenance is out of scope. WQuestions does not track who entered a
  fact or where it came from. Do not model it.

GROUND RULES
- The store is append-only and open-world: it does not check consistency.
  Contradictory facts coexist by design — not an error to fix.
- State is in-memory for this process and does not survive a restart. Use
  show_model to inspect and reset to start clean; do not build recovery rituals.
- Start with list_axes and list_roles — they describe the vocabulary and its
  typed signatures.
"""

mcp = FastMCP("wquestions", instructions=INSTRUCTIONS)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /Users/joseabanto/WQuestions/mcp-server && /Users/joseabanto/WQuestions/.venv/bin/pytest tests/test_server.py -v`
Expected: PASS (2 tests).

- [ ] **Step 5: Upgrade the `assert_situation` and `define_verb` docstrings**

In `server.py`, replace the `assert_situation` tool docstring with:

```python
    """Assert a fact. The situation is REIFIED: a new node is minted in axis O
    and each role becomes one binary triplet (situation · role · value) — that is
    what this returns. Each role value is an existing entity id or an inline
    {id, axis, label}; for N pass an inline magnitude {id, axis:'N', value, unit}.
    valid_from/valid_to (ISO-8601) mark a fact true only during a time range;
    read the past with ask(at=...). To correct a value later use `correct`, not a
    new status role."""
```

Replace the `define_verb` tool docstring with:

```python
    """Register a situation type (verb) and the roles it takes. `obligatory`
    roles ARE enforced: assert_situation rejects a situation missing one. Leaving
    `obligatory` empty makes every role optional — a deliberate choice, not a
    limit. assert_situation also auto-registers unknown verbs permissively."""
```

- [ ] **Step 6: Run the full suite (docstrings must not break imports)**

Run: `cd /Users/joseabanto/WQuestions/mcp-server && /Users/joseabanto/WQuestions/.venv/bin/pytest -q`
Expected: PASS (18 tests: 16 prior + 2 new).

- [ ] **Step 7: Commit**

```bash
cd /Users/joseabanto/WQuestions && git add mcp-server/wquestions_mcp/server.py mcp-server/tests/test_server.py
git commit -m "$(printf 'feat(mcp): server instructions constitution + teaching docstrings\n\nCo-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>')"
```

---

### Task 2: Enrich orientation-tool returns (list_axes, list_roles, show_model)

**Files:**
- Modify: `mcp-server/wquestions_mcp/session.py`
- Test: `mcp-server/tests/test_session.py`

**Interfaces:**
- Consumes: existing `WQSession.list_axes/list_roles/show_model`.
- Produces: `list_axes()` axis dicts gain `how_to_use`/`example`/`gotcha`; `list_roles()` gains `policy` (str) and `common` (list); `show_model()` gains `legend` (str). All existing keys are preserved.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_session.py`:

```python
def test_list_axes_teaches_n_needs_unit_and_m_is_predicate():
    s = WQSession()
    axes = {a["code"]: a for a in s.list_axes()["axes"]}
    assert "unit" in axes["N"]["how_to_use"].lower()
    assert "predicate" in axes["M"]["how_to_use"].lower()
    assert axes["O"]["gotcha"]  # non-empty


def test_list_roles_states_open_policy_and_common_roles():
    s = WQSession()
    out = s.list_roles()
    assert "open" in out["policy"].lower()
    assert "agente" in out["common"] and "por_cuanto" in out["common"]


def test_show_model_has_append_only_legend():
    s = WQSession()
    out = s.show_model()
    assert "append-only" in out["legend"].lower()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/joseabanto/WQuestions/mcp-server && /Users/joseabanto/WQuestions/.venv/bin/pytest tests/test_session.py -k "list_axes_teaches or open_policy or append_only_legend" -v`
Expected: FAIL with `KeyError`.

- [ ] **Step 3: Add the `_AXIS_GUIDE` table**

In `session.py`, right after the `_AXIS_NAMES` dict, add:

```python
_AXIS_GUIDE = {
    "Q": {"how_to_use": "People and agents. add_entity(id, 'Q').",
          "example": "add_entity('ana', 'Q', 'Ana')",
          "gotcha": "Agents enter situations through roles like agente/cliente."},
    "O": {"how_to_use": "Things AND reified situations. Every assert_situation "
                        "mints an O node.",
          "example": "a 'visit' situation lives in O as visit_000001",
          "gotcha": "O is not only physical objects — situations are objects here."},
    "L": {"how_to_use": "Places. add_entity(id, 'L').",
          "example": "add_entity('spa_oasis', 'L', 'Spa Oasis')",
          "gotcha": "Attach with lugar_de / origen / destino."},
    "T": {"how_to_use": "Time points or intervals, ISO-8601.",
          "example": "add_entity('t_2026_07_10', 'T', '2026-07-10')",
          "gotcha": "For world-time validity use valid_from/valid_to on the fact, "
                    "not a T role."},
    "N": {"how_to_use": "Magnitudes. Always a value plus a unit: "
                        "add_entity(id, 'N', value=.., unit=..).",
          "example": "add_entity('p25', 'N', value=25, "
                     "unit={'id':'pen','axis':'K','label':'PEN'})",
          "gotcha": "A number without a unit is rejected. Never bake the unit "
                    "into the id or label; never assume one."},
    "K": {"how_to_use": "Atemporal categories: types, states, units, vocabularies.",
          "example": "add_entity('pen', 'K', 'PEN')",
          "gotcha": "The units of N magnitudes live here."},
    "M": {"how_to_use": "Predicate axis: the roles themselves. You cannot "
                        "add_entity on M.",
          "example": "agente, lugar_de, causado_por, instancia_de ARE M predicates.",
          "gotcha": "M both classifies (instancia_de) and connects situations "
                    "(causado_por, cumple, rectifica)."},
}
```

- [ ] **Step 4: Enrich the three methods**

In `session.py`, replace `list_axes`:

```python
    def list_axes(self) -> Dict[str, Any]:
        return {
            "axes": [
                {"code": code, "name": name, "description": desc,
                 **_AXIS_GUIDE.get(code, {})}
                for code, (name, desc) in _AXIS_NAMES.items()
            ]
        }
```

In `list_roles`, replace the final `return {"roles": roles}` with:

```python
        return {
            "roles": roles,
            "policy": "Roles are open-world: unknown roles are accepted, not "
                      "validated — invent domain roles freely. Declared roles "
                      "carry a typed signature (domain axis -> range axis) and a "
                      "functional flag (functional=one value per subject).",
            "common": ["agente", "cliente", "tema", "momento", "lugar_de",
                       "por_cuanto", "unidad", "instancia_de", "estatus_factual"],
        }
```

In `show_model`, add a `legend` key to the returned dict (keep every existing key):

```python
        return {
            "summary": self.universe.summary(),
            "entity_count": len(self.universe.individuals),
            "fact_count": len(self.universe.facts),
            "facts": facts,
            "legend": "Facts are binary triplets (subject · role · value), the "
                      "projection of reified situations. The store is append-only: "
                      "corrections add facts, they never overwrite.",
        }
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd /Users/joseabanto/WQuestions/mcp-server && /Users/joseabanto/WQuestions/.venv/bin/pytest tests/test_session.py -q`
Expected: PASS (existing `test_list_axes_returns_seven_axes`, `test_list_roles_includes_agente_with_signature`, `test_show_model_reports_counts` still green; 3 new pass).

- [ ] **Step 6: Commit**

```bash
cd /Users/joseabanto/WQuestions && git add mcp-server/wquestions_mcp/session.py mcp-server/tests/test_session.py
git commit -m "$(printf 'feat(mcp): teach via enriched list_axes/list_roles/show_model returns\n\nCo-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>')"
```

---

### Task 3: Magnitudes with units in add_entity (gap 2a)

**Files:**
- Modify: `mcp-server/wquestions_mcp/session.py` (`_individual`, `add_entity`, `_resolve_value`)
- Modify: `mcp-server/wquestions_mcp/server.py` (`add_entity` tool signature + docstring)
- Test: `mcp-server/tests/test_session.py`

**Interfaces:**
- Consumes: `wq.axes.Axis`, `wq.Individual`.
- Produces: `WQSession.add_entity(entity_id, axis, label=None, value=None, unit=None)`; `_individual(entity_id, axis, label=None, value=None, unit_ind=None)`; inline specs accept optional `value`/`unit`. N individuals carry `payload={"value", "unit"}`. Bare N returns `{"ok": False, "error": "N magnitudes require ..."}`.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_session.py`:

```python
def test_add_entity_n_without_unit_is_rejected():
    s = WQSession()
    out = s.add_entity("price", "N", value=25)
    assert out["ok"] is False
    assert "unit" in out["error"].lower()


def test_add_entity_n_with_inline_unit_builds_payload():
    s = WQSession()
    out = s.add_entity("price_25", "N", value=25,
                       unit={"id": "pen", "axis": "K", "label": "PEN"})
    assert out["ok"] is True
    ind = s.universe.individuals["price_25"]
    assert ind.axis.value == "N"
    assert ind.payload == {"value": 25, "unit": "pen"}
    assert "pen" in s.universe.individuals  # unit auto-created in K


def test_add_entity_n_with_existing_unit_id():
    s = WQSession()
    s.add_entity("pen", "K", "PEN")
    out = s.add_entity("price_30", "N", value=30, unit="pen")
    assert out["ok"] is True
    assert s.universe.individuals["price_30"].payload["unit"] == "pen"


def test_value_unit_rejected_on_non_n_axis():
    s = WQSession()
    out = s.add_entity("ana", "Q", value=5)
    assert out["ok"] is False
    assert "n" in out["error"].lower()


def test_assert_situation_inline_n_without_unit_is_rejected():
    s = WQSession()
    out = s.assert_situation(
        "charge", roles={"por_cuanto": {"id": "p", "axis": "N", "value": 25}})
    assert out["ok"] is False
    assert "unit" in out["error"].lower()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/joseabanto/WQuestions/mcp-server && /Users/joseabanto/WQuestions/.venv/bin/pytest tests/test_session.py -k "unit or value_unit" -v`
Expected: FAIL (e.g. `add_entity` got an unexpected keyword `value`).

- [ ] **Step 3: Extend `_individual` to handle N value+unit**

In `session.py`, replace `_individual` with:

```python
    def _individual(self, entity_id: str, axis: str,
                    label: Optional[str] = None,
                    value: Any = None,
                    unit_ind: Optional[Individual] = None) -> Individual:
        try:
            ax = Axis[axis]
        except KeyError:
            raise ValueError(f"Unknown axis '{axis}'. Use one of Q,O,L,T,N,K.")
        if not is_value_axis(ax):
            raise ValueError(
                f"Axis '{axis}' cannot hold entities. Value axes: Q,O,L,T,N,K."
            )
        if ax is Axis.N:
            if value is None or unit_ind is None:
                raise ValueError(
                    "N magnitudes require a numeric `value` and a `unit` in K "
                    "(e.g. value=25, unit='pen'). Do not encode the unit in the "
                    "id or label, and do not assume a unit — ask for it if missing."
                )
            return Individual(
                id=entity_id, axis=Axis.N,
                label=label or f"{value} {unit_ind.label or unit_ind.id}",
                payload={"value": value, "unit": unit_ind.id},
            )
        if value is not None or unit_ind is not None:
            raise ValueError(f"`value`/`unit` only apply to axis N, not {axis}.")
        return Individual(id=entity_id, axis=ax, label=label or entity_id)
```

- [ ] **Step 4: Extend `add_entity` and `_resolve_value` to pass value/unit**

In `session.py`, replace `add_entity` with:

```python
    def add_entity(self, entity_id: str, axis: str,
                   label: Optional[str] = None,
                   value: Any = None,
                   unit: Any = None) -> Dict[str, Any]:
        try:
            if axis != "N" and (value is not None or unit is not None):
                raise ValueError("`value`/`unit` only apply to axis N.")
            unit_ind = self._resolve_value(unit) if unit is not None else None
            if unit_ind is not None and unit_ind.axis is not Axis.K:
                raise ValueError(
                    f"unit must live in K (got {unit_ind.axis.value})."
                )
            ind = self._individual(entity_id, axis, label,
                                   value=value, unit_ind=unit_ind)
            self.universe.add_individual(ind)
        except ValueError as e:
            return {"ok": False, "error": str(e)}
        return {"ok": True,
                "entity": {"id": ind.id, "axis": ind.axis.value, "label": ind.label}}
```

In `session.py`, replace the `isinstance(spec, dict)` branch of `_resolve_value` with:

```python
        if isinstance(spec, dict):
            if "id" not in spec or "axis" not in spec:
                raise ValueError(
                    "Inline entity spec needs 'id' and 'axis' "
                    f"(got keys: {sorted(spec.keys())})"
                )
            unit_ind = (self._resolve_value(spec["unit"])
                        if spec.get("unit") is not None else None)
            if unit_ind is not None and unit_ind.axis is not Axis.K:
                raise ValueError(
                    f"unit must live in K (got {unit_ind.axis.value})."
                )
            ind = self._individual(spec["id"], spec["axis"], spec.get("label"),
                                   value=spec.get("value"), unit_ind=unit_ind)
            self.universe.add_individual(ind)
            return ind
```

- [ ] **Step 5: Update the `add_entity` tool in `server.py`**

Replace the `add_entity` tool with:

```python
@mcp.tool()
def add_entity(entity_id: str, axis: str, label: Optional[str] = None,
               value: Optional[float] = None,
               unit: Optional[Any] = None) -> Dict[str, Any]:
    """Create an individual on a value axis (Q, O, L, T, N, K). For N you MUST
    pass `value` (a number) and `unit` (an existing K entity id, or an inline
    {id, axis:'K', label}); a magnitude without a unit is rejected. Never assume
    a unit — ask for it. `value`/`unit` apply only to N."""
    return _session.add_entity(entity_id, axis, label, value, unit)
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `cd /Users/joseabanto/WQuestions/mcp-server && /Users/joseabanto/WQuestions/.venv/bin/pytest tests/test_session.py -q`
Expected: PASS (all prior + 5 new; `test_add_entity_registers_individual`, `test_add_entity_rejects_predicate_axis`, `test_assert_situation_creates_inline_entities` still green).

- [ ] **Step 7: Commit**

```bash
cd /Users/joseabanto/WQuestions && git add mcp-server/wquestions_mcp/session.py mcp-server/wquestions_mcp/server.py mcp-server/tests/test_session.py
git commit -m "$(printf 'feat(mcp): add_entity requires value+unit for N magnitudes (gap 2a)\n\nUses the engine payload shape; a bare N is rejected with a redirecting error\nso the model stops baking units into ids. Inline role specs accept value/unit too.\n\nCo-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>')"
```

---

### Task 4: The `correct` tool (gap 2b, part 1)

**Files:**
- Modify: `mcp-server/wquestions_mcp/session.py` (new `correct` method)
- Modify: `mcp-server/wquestions_mcp/server.py` (new `correct` tool)
- Test: `mcp-server/tests/test_session.py`

**Interfaces:**
- Consumes: `self.universe.assert_fact`, `self._resolve_value`, `self._parse_ts`, `Axis.O`, `IngestError`.
- Produces: `WQSession.correct(situation_id, role, value, valid_from=None, valid_to=None) -> dict`. On success `{"ok": True, "situation_id", "role", "value", "note"}`; appends a fact to an existing O situation (never overwrites).

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_session.py`:

```python
def test_correct_appends_fact_to_existing_situation():
    s = WQSession()
    s.add_entity("ana", "Q", "Ana")
    s.add_entity("beto", "Q", "Beto")
    out = s.assert_situation("visit", roles={"agente": "ana"})
    sid = out["situation_id"]
    c = s.correct(sid, "agente", "beto")
    assert c["ok"] is True
    agente = [f for f in s.universe.facts
              if f.subject.id == sid and f.role == "agente"]
    assert {f.value.id for f in agente} == {"ana", "beto"}


def test_correct_unknown_situation_errors():
    s = WQSession()
    out = s.correct("nope", "agente", "ana")
    assert out["ok"] is False
    assert "nope" in out["error"]


def test_correct_rejects_non_situation_subject():
    s = WQSession()
    s.add_entity("ana", "Q", "Ana")
    out = s.correct("ana", "agente", "ana")  # ana is Q, not a situation (O)
    assert out["ok"] is False
    assert "situation" in out["error"].lower()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/joseabanto/WQuestions/mcp-server && /Users/joseabanto/WQuestions/.venv/bin/pytest tests/test_session.py -k correct -v`
Expected: FAIL with `AttributeError: 'WQSession' object has no attribute 'correct'`.

- [ ] **Step 3: Implement `correct` in `session.py`**

Add this method to `WQSession` (place it right after `assert_situation`):

```python
    def correct(self, situation_id: str, role: str, value: Any,
                valid_from: Optional[str] = None,
                valid_to: Optional[str] = None) -> Dict[str, Any]:
        """Re-assert a role on an existing situation. Append-only: the prior
        value is kept as history; ask returns the latest. No overwrite, ever."""
        situ = self.universe.individuals.get(situation_id)
        if situ is None:
            return {"ok": False,
                    "error": f"Unknown situation '{situation_id}'. Pass the "
                             f"situation_id returned by a prior assert_situation."}
        if situ.axis is not Axis.O:
            return {"ok": False,
                    "error": f"'{situation_id}' is in axis {situ.axis.value}, not "
                             f"a situation (O). Corrections attach to situations."}
        try:
            val = self._resolve_value(value)
            self.universe.assert_fact(
                situ, role, val,
                valid_from=self._parse_ts(valid_from),
                valid_to=self._parse_ts(valid_to),
            )
        except (ValueError, IngestError) as e:
            return {"ok": False, "error": str(e)}
        return {"ok": True, "situation_id": situ.id, "role": role, "value": val.id,
                "note": "Appended, not overwritten. ask returns this (latest) "
                        "value; ask(history=true) shows prior ones."}
```

- [ ] **Step 4: Add the `correct` tool to `server.py`**

Add after the `assert_situation` tool:

```python
@mcp.tool()
def correct(situation_id: str, role: str, value: Any,
            valid_from: Optional[str] = None,
            valid_to: Optional[str] = None) -> Dict[str, Any]:
    """Correct or update a role on an existing situation by re-asserting it.
    Append-only: the prior value is kept as history, never overwritten. ask
    returns the latest value; ask(history=true) shows the full trail. Use this
    instead of inventing status/superseded roles. valid_from/valid_to ISO-8601."""
    return _session.correct(situation_id, role, value, valid_from, valid_to)
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd /Users/joseabanto/WQuestions/mcp-server && /Users/joseabanto/WQuestions/.venv/bin/pytest tests/test_session.py -k correct -v`
Expected: PASS (3 tests).

- [ ] **Step 6: Run the full suite**

Run: `cd /Users/joseabanto/WQuestions/mcp-server && /Users/joseabanto/WQuestions/.venv/bin/pytest -q`
Expected: PASS (all green).

- [ ] **Step 7: Commit**

```bash
cd /Users/joseabanto/WQuestions && git add mcp-server/wquestions_mcp/session.py mcp-server/wquestions_mcp/server.py mcp-server/tests/test_session.py
git commit -m "$(printf 'feat(mcp): correct tool — append-only role correction on a situation (gap 2b)\n\nCo-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>')"
```

---

### Task 5: `ask` returns the current value, with history (gap 2b, part 2)

**Files:**
- Modify: `mcp-server/wquestions_mcp/session.py` (`ask` + new `_project_role`)
- Modify: `mcp-server/wquestions_mcp/server.py` (`ask` tool `history` param + docstring)
- Test: `mcp-server/tests/test_session.py`

**Interfaces:**
- Consumes: `wq.query`, `wq.Pattern`, `wq.Var`, `wq.category`, `self.universe.facts_about`, `self.catalog.get`, `Fact.tx_time`.
- Produces: `WQSession.ask(fixed=None, ask=None, type=None, at=None, history=False)`; `_project_role(role, role_facts, history)`. Default: functional/unknown roles → single current value (latest `tx_time`); catalog non-functional roles → list of all values. `history=True` → time-ordered list of all values.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_session.py`:

```python
def test_ask_returns_latest_value_after_correction():
    s = WQSession()
    s.add_entity("ana", "Q", "Ana")
    s.add_entity("beto", "Q", "Beto")
    s.add_entity("spa", "L", "Spa")
    out = s.assert_situation("visit", roles={"agente": "ana", "lugar_de": "spa"})
    s.correct(out["situation_id"], "agente", "beto")
    res = s.ask(fixed={"lugar_de": "spa"}, ask=["agente"])
    assert res["results"][0]["agente"] == "beto"  # functional role: latest wins


def test_ask_history_returns_full_trail():
    s = WQSession()
    s.add_entity("ana", "Q", "Ana")
    s.add_entity("beto", "Q", "Beto")
    s.add_entity("spa", "L", "Spa")
    out = s.assert_situation("visit", roles={"agente": "ana", "lugar_de": "spa"})
    s.correct(out["situation_id"], "agente", "beto")
    res = s.ask(fixed={"lugar_de": "spa"}, ask=["agente"], history=True)
    assert res["results"][0]["agente"] == ["ana", "beto"]  # tx_time order


def test_ask_nonfunctional_role_returns_all_values():
    s = WQSession()
    s.add_entity("ana", "Q", "Ana")
    out = s.assert_situation("visit", roles={"agente": "ana"})
    # instancia_de is catalog non-functional -> genuinely multi-valued
    s.correct(out["situation_id"], "instancia_de",
              {"id": "special", "axis": "K", "label": "special"})
    res = s.ask(fixed={"agente": "ana"}, ask=["instancia_de"])
    vals = res["results"][0]["instancia_de"]
    assert isinstance(vals, list)
    assert "special" in vals and "action_visit" in vals
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/joseabanto/WQuestions/mcp-server && /Users/joseabanto/WQuestions/.venv/bin/pytest tests/test_session.py -k "latest_value or history_returns or nonfunctional" -v`
Expected: FAIL — `ask()` got an unexpected keyword `history` (and latest-wins not implemented).

- [ ] **Step 3: Rewrite `ask` and add `_project_role`**

In `session.py`, replace the whole `ask` method with:

```python
    def ask(self, fixed: Optional[Dict[str, Any]] = None,
            ask: Optional[List[str]] = None,
            type: Optional[str] = None,
            at: Optional[str] = None,
            history: bool = False) -> Dict[str, Any]:
        try:
            fixed_ind = ({r: self._resolve_value(v) for r, v in fixed.items()}
                         if fixed else {})
            at_dt = self._parse_ts(at)
            pattern = Pattern(
                fixed=fixed_ind,
                ask={role: Var(role) for role in (ask or [])},
                type_constraint=category(type) if type else None,
            )
            bindings = query(self.universe, pattern, at=at_dt)
            results = []
            for b in bindings:
                subj = b["_subject"]
                row: Dict[str, Any] = {"_subject": subj.id}
                subj_facts = self.universe.facts_about(subj, at=at_dt)
                for role in (ask or []):
                    role_facts = [f for f in subj_facts if f.role == role]
                    row[role] = self._project_role(role, role_facts, history)
                results.append(row)
        except (ValueError, IngestError) as e:
            return {"ok": False, "error": str(e)}
        return {"count": len(results), "results": results}

    def _project_role(self, role: str, role_facts: List[Any],
                      history: bool) -> Any:
        """Resolve a role's value(s). Default: the current value (latest tx_time)
        for functional/unknown roles; all values for catalog non-functional roles.
        history=True: the full time-ordered trail (current + superseded)."""
        if history:
            ordered = sorted(role_facts, key=lambda f: f.tx_time)
            return [f.value.id for f in ordered]
        sig = self.catalog.get(role)
        if sig is not None and not sig.functional:
            return [f.value.id for f in role_facts]
        latest = role_facts[0]
        for f in role_facts[1:]:
            if f.tx_time >= latest.tx_time:  # >= so later insertion wins ties
                latest = f
        return latest.value.id
```

- [ ] **Step 4: Add the `history` param to the `ask` tool in `server.py`**

Replace the `ask` tool with:

```python
@mcp.tool()
def ask(fixed: Optional[Dict[str, Any]] = None,
        ask: Optional[List[str]] = None,
        type: Optional[str] = None,
        at: Optional[str] = None,
        history: bool = False) -> Dict[str, Any]:
    """Query by projection: fix some roles, ask for others. Returns the CURRENT
    value of each asked role (the latest correction wins for single-valued roles);
    pass history=true for the full time-ordered trail. `type` filters to a category
    id (auto-registered verbs get `action_<verb>`). `at` (ISO-8601) reads the
    model's valid-time as of that moment."""
    return _session.ask(fixed, ask, type, at, history)
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd /Users/joseabanto/WQuestions/mcp-server && /Users/joseabanto/WQuestions/.venv/bin/pytest tests/test_session.py -k "latest_value or history_returns or nonfunctional or ask_projects or malformed_at" -v`
Expected: PASS — including the unchanged `test_ask_projects_the_asked_role` (agente still returns the single id `"ana"`) and `test_ask_malformed_at_returns_error`.

- [ ] **Step 6: Run the full suite**

Run: `cd /Users/joseabanto/WQuestions/mcp-server && /Users/joseabanto/WQuestions/.venv/bin/pytest -q`
Expected: PASS (all green).

- [ ] **Step 7: Commit**

```bash
cd /Users/joseabanto/WQuestions && git add mcp-server/wquestions_mcp/session.py mcp-server/wquestions_mcp/server.py mcp-server/tests/test_session.py
git commit -m "$(printf 'feat(mcp): ask resolves current value by tx_time, history=true for the trail (gap 2b)\n\nFunctional/unknown roles collapse to the latest assertion; catalog non-functional\nroles stay multi-valued. Correcting is now just re-asserting — no status vocabulary.\n\nCo-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>')"
```

---

### Task 6: Capstone integration test + full-suite gate + manual replay note

**Files:**
- Test: `mcp-server/tests/test_session.py`

**Interfaces:**
- Consumes: the full `WQSession` public API from Tasks 1–5.
- Produces: one end-to-end test reproducing the barbershop correction scenario, proving no invented vocabulary (`estatus_factual`/`rectifica`/`unidad`/provenance) is needed.

- [ ] **Step 1: Write the capstone integration test**

Append to `tests/test_session.py`:

```python
def test_barbershop_correction_scenario_end_to_end():
    """The exact friction from the stress test: a mis-recorded exchange rate is
    corrected by re-assertion, priced in unit-bearing N, no auditing vocabulary."""
    s = WQSession()
    s.add_entity("marcos", "Q", "Marcos")
    s.add_entity("pablo", "Q", "Pablo")
    s.add_entity("shave", "O", "Shave service")
    out = s.assert_situation("serve", roles={
        "agente": "marcos", "cliente": "pablo", "tema": "shave",
        "por_cuanto": {"id": "usd_12", "axis": "N", "value": 12,
                       "unit": {"id": "usd", "axis": "K", "label": "USD"}},
    })
    sid = out["situation_id"]

    # exchange rate recorded wrong (3.33) then corrected (3.39) — no status role
    s.correct(sid, "tipo_cambio",
              {"id": "tc_333", "axis": "N", "value": 3.33,
               "unit": {"id": "pen_per_usd", "axis": "K", "label": "PEN/USD"}})
    s.correct(sid, "tipo_cambio",
              {"id": "tc_339", "axis": "N", "value": 3.39, "unit": "pen_per_usd"})

    current = s.ask(fixed={"cliente": "pablo"}, ask=["tipo_cambio"])
    assert current["results"][0]["tipo_cambio"] == "tc_339"  # current wins

    trail = s.ask(fixed={"cliente": "pablo"}, ask=["tipo_cambio"], history=True)
    assert trail["results"][0]["tipo_cambio"] == ["tc_333", "tc_339"]

    # the magnitude kept its unit as structured data, not baked into a label
    assert s.universe.individuals["usd_12"].payload == {"value": 12, "unit": "usd"}
```

- [ ] **Step 2: Run the capstone test to verify it passes**

Run: `cd /Users/joseabanto/WQuestions/mcp-server && /Users/joseabanto/WQuestions/.venv/bin/pytest tests/test_session.py::test_barbershop_correction_scenario_end_to_end -v`
Expected: PASS.

- [ ] **Step 3: Run the entire suite as the final gate**

Run: `cd /Users/joseabanto/WQuestions/mcp-server && /Users/joseabanto/WQuestions/.venv/bin/pytest -q`
Expected: PASS (all: 16 original + the new session tests + 2 server tests).

- [ ] **Step 4: Manual replay (real-model acceptance — the north-star check)**

Re-run the barbershop stress test against the updated server: drive a model with **only** the MCP tools and ask it to build a fresh domain and correct a value. Confirm it (a) creates N magnitudes with `value`+`unit`, (b) uses `correct` + `ask` for the fix, and (c) does **not** re-invent `estatus_factual`, a `unidad` role, or provenance triplets. This is behavioral, not a pytest assertion — record the outcome in `docs/fricciones-stress-test-modelo.md`.

- [ ] **Step 5: Commit**

```bash
cd /Users/joseabanto/WQuestions && git add mcp-server/tests/test_session.py
git commit -m "$(printf 'test(mcp): capstone — barbershop correction scenario needs no invented vocabulary\n\nCo-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>')"
```

---

## Self-Review

**Spec coverage:**
- 1a server instructions → Task 1. ✓
- 1b enriched returns (list_axes/list_roles/show_model) → Task 2. ✓
- 1c docstrings: assert_situation/define_verb → Task 1; add_entity → Task 3; correct → Task 4; ask → Task 5. ✓
- 1d redirect errors: bare-N error → Task 3; non-situation `correct` error → Task 4. ✓
- 2a N with unit → Task 3. ✓
- 2b correct tool → Task 4; ask current-value + history + functional disambiguation → Task 5. ✓
- Section 3 friction table: reification (T1 docstring), persistence (T1 instructions), obligatory roles (T1 define_verb docstring), units (T3), corrections (T4/T5), provenance out-of-scope (T1 instructions), M axis (T2 list_axes), contradiction tolerance (T1 instructions). ✓
- Testing: unit tests per task + capstone integration + manual replay → Task 6. ✓

**Placeholder scan:** No TBD/TODO; every code step shows full code; every command shows exact path + expected output. ✓

**Type consistency:** `_individual(entity_id, axis, label, value, unit_ind)`, `add_entity(entity_id, axis, label, value, unit)`, `correct(situation_id, role, value, valid_from, valid_to)`, `ask(fixed, ask, type, at, history)`, `_project_role(role, role_facts, history)` — names and signatures match across session.py and server.py wrappers and across tasks. `payload={"value","unit"}` shape consistent between Task 3 and the Task 6 assertion. ✓

**Global constraints:** engine untouched (only `wq` public API used); all strings English; no catalog role additions; venv path used in every command. ✓
