# WQuestions MCP Server (Fase 0) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a WQuestions MCP server that lets an LLM client (Claude Desktop / Cursor) model any domain on the 7 WQuestions axes and query it — the viral "gancho" of Fase 0.

**Architecture:** A thin MCP layer over the existing `wq` engine. The LLM client does natural-language → structured roles (the engine deliberately leaves NL to the LLM); the server exposes stateful tools that translate JSON args into `wq` calls (`ingest_situation`, `query`) against a per-session in-memory `Universe`. All testable logic lives in a plain-Python `WQSession` class; `server.py` is a thin FastMCP wrapper with no logic of its own.

**Tech Stack:** Python 3.10+, the official MCP Python SDK (`mcp`, FastMCP), the existing `wq` engine (pure Python), `pytest`.

## Global Constraints

- Language of all user-facing strings, tool names, docstrings, and README: **English** (this is the public dev-facing artifact; the Spanish book is the deep-dive layer only).
- Python floor: **3.10+** (MCP SDK requirement).
- Do **not** rewrite or "fix" the `wq` engine. Wrap it as-is. Engine edge-cases get documented, not polished, before launch.
- The 7 axes are exactly: `Q` (who), `O` (what), `L` (where), `T` (when), `N` (how-much), `K` (which/kind), `M` (how/predicates). Value axes (can hold entities): Q, O, L, T, N, K. `M` and `V` are NOT valid for entities.
- Reuse the engine's **liberal role policy**: unknown roles are allowed (no signature error). Never add per-domain roles to `catalog.py`.
- Package/distribution name: `wquestions-mcp`. Console entry point: `wquestions-mcp`. Python package: `wquestions_mcp`.
- Acceptance for "Fase 0 code done": a clean-machine user can `uvx wquestions-mcp` (or pip install + run), wire it into Claude Desktop with a copy-paste config block, and model + query a domain end-to-end in under 5 minutes.
- **Local environment (this machine):** the repo has a uv-managed venv at `<repo>/.venv` (Python 3.12). The system `python3` is 3.9 and MUST NOT be used. Run every `python`/`pip`/`pytest` in this plan through the venv by explicit path — `<repo>/.venv/bin/python`, `<repo>/.venv/bin/pytest` — or via `uv pip install --python <repo>/.venv ...`. Shell state does not persist between commands, so never rely on `source .venv/bin/activate`; use explicit binary paths every time. `uv` lives at `~/.local/bin/uv` (add `~/.local/bin` to PATH in the command if needed).

---

## File Structure

```
prototipo/
  pyproject.toml          # NEW — makes the `wq` engine pip-installable (dist: wquestions-engine)
mcp-server/               # NEW — the shippable MCP package (seed of the public repo)
  pyproject.toml          # package metadata, deps (mcp, wquestions-engine), entry point
  README.md               # English quickstart + Claude Desktop config block (Task 8)
  wquestions_mcp/
    __init__.py
    session.py            # WQSession — ALL logic, fully unit-tested
    examples.py           # prebuilt demo universes (spa)
    server.py             # thin FastMCP wrapper: one @mcp.tool per WQSession method
  tests/
    test_session.py       # unit tests for WQSession
  DEMO.md                 # exact scripted scenario to record the 30-60s GIF (Task 8)
```

`session.py` holds one responsibility: translate JSON-friendly args into `wq`
calls against a session `Universe`, and JSON-friendly results back out.
`server.py` holds one responsibility: register those methods as MCP tools.
Splitting them keeps the logic testable without an MCP runtime.

---

## Task 1: Engine packaging + MCP scaffold + reference tools

**Files:**
- Create: `prototipo/pyproject.toml`
- Create: `mcp-server/pyproject.toml`
- Create: `mcp-server/wquestions_mcp/__init__.py`
- Create: `mcp-server/wquestions_mcp/session.py`
- Test: `mcp-server/tests/test_session.py`

**Interfaces:**
- Consumes: `wq` engine — `from wq.axes import Axis, VALUE_AXES`, `from wq import Catalog`.
- Produces: `WQSession` class with `reset() -> dict`, `list_axes() -> dict`, `list_roles() -> dict`. Later tasks add methods to this same class.

- [ ] **Step 1: Make the engine installable**

Create `prototipo/pyproject.toml` so the MCP package can depend on `wq` (pandas is only needed by `vistas.py`, which the MCP never imports — but `wq/__init__.py` imports it, so keep it a dependency for now):

```toml
[build-system]
requires = ["setuptools>=61"]
build-backend = "setuptools.build_meta"

[project]
name = "wquestions-engine"
version = "0.1.0"
description = "WQuestions core engine: 7-axis fact model, ingest and query."
requires-python = ">=3.10"
dependencies = ["pandas>=2.0,<2.3"]

[tool.setuptools]
packages = ["wq"]
```

- [ ] **Step 2: Create the MCP package metadata**

Create `mcp-server/pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=61"]
build-backend = "setuptools.build_meta"

[project]
name = "wquestions-mcp"
version = "0.1.0"
description = "Model any domain in 7 questions — a WQuestions MCP server."
requires-python = ">=3.10"
dependencies = ["mcp>=1.2", "wquestions-engine>=0.1.0"]

[project.scripts]
wquestions-mcp = "wquestions_mcp.server:main"

[tool.setuptools]
packages = ["wquestions_mcp"]
```

Create empty `mcp-server/wquestions_mcp/__init__.py` with:

```python
"""WQuestions MCP server — model any domain in 7 questions."""
__version__ = "0.1.0"
```

- [ ] **Step 3: Write the failing test for reference tools**

Create `mcp-server/tests/test_session.py`:

```python
from wquestions_mcp.session import WQSession


def test_list_axes_returns_seven_axes():
    s = WQSession()
    out = s.list_axes()
    codes = [a["code"] for a in out["axes"]]
    assert codes == ["Q", "O", "L", "T", "N", "K", "M"]


def test_list_roles_includes_agente_with_signature():
    s = WQSession()
    roles = {r["name"]: r for r in s.list_roles()["roles"]}
    assert roles["agente"]["domain"] == "O"
    assert roles["agente"]["range"] == "Q"
    assert roles["agente"]["functional"] is True


def test_reset_gives_empty_universe():
    s = WQSession()
    s.reset()
    assert len(s.universe.facts) == 0
```

- [ ] **Step 4: Run tests to verify they fail**

Run (from `mcp-server/`, with both packages installed editable — see Step 6):
`pytest tests/test_session.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'wquestions_mcp.session'`

- [ ] **Step 5: Implement `WQSession` reference tools**

Create `mcp-server/wquestions_mcp/session.py`:

```python
"""WQSession — all MCP tool logic over a per-session wq Universe.

The LLM client does natural-language -> structured roles. This class turns
JSON-friendly arguments into wq engine calls and JSON-friendly results back.
No MCP types here: this module is pure Python and fully unit-tested.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional

from wq import Catalog, Lexicon, Universe
from wq.axes import Axis

_AXIS_NAMES = {
    "Q": ("who", "agents"),
    "O": ("what", "objects / reified situations"),
    "L": ("where", "places"),
    "T": ("when", "time points / intervals"),
    "N": ("how-much", "magnitudes with unit"),
    "K": ("which", "atemporal categories / types / states"),
    "M": ("how", "predicates that connect individuals"),
}


class WQSession:
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> Dict[str, Any]:
        self.catalog = Catalog()
        self.universe = Universe(name="session", catalog=self.catalog)
        self.lexicon = Lexicon()
        return {"ok": True}

    def list_axes(self) -> Dict[str, Any]:
        return {
            "axes": [
                {"code": code, "name": name, "description": desc}
                for code, (name, desc) in _AXIS_NAMES.items()
            ]
        }

    def list_roles(self) -> Dict[str, Any]:
        roles = [
            {
                "name": sig.name,
                "domain": sig.domain.value,
                "range": sig.range.value,
                "functional": sig.functional,
                "description": sig.description,
            }
            for sig in self.catalog._roles.values()
        ]
        return {"roles": roles}
```

- [ ] **Step 6: Install both packages editable and run tests to verify they pass**

Run:
```bash
python3 -m pip install -e ./prototipo -e ./mcp-server
cd mcp-server && pytest tests/test_session.py -v
```
Expected: 3 passed.

- [ ] **Step 7: Commit**

```bash
git add prototipo/pyproject.toml mcp-server/
git commit -m "feat(mcp): scaffold WQuestions MCP package + reference tools"
```

---

## Task 2: `add_entity` — place individuals on the axes

**Files:**
- Modify: `mcp-server/wquestions_mcp/session.py`
- Test: `mcp-server/tests/test_session.py`

**Interfaces:**
- Produces: `WQSession.add_entity(entity_id: str, axis: str, label: str | None = None) -> dict`
  returning `{"ok": True, "entity": {"id","axis","label"}}`. Rejects non-value axes with `{"ok": False, "error": "..."}`. Also a private helper `_individual(entity_id, axis, label) -> Individual` reused by later tasks.

- [ ] **Step 1: Write the failing tests**

Add to `mcp-server/tests/test_session.py`:

```python
def test_add_entity_registers_individual():
    s = WQSession()
    out = s.add_entity("ana", "Q", "Ana")
    assert out["ok"] is True
    assert s.universe.individuals["ana"].axis.value == "Q"


def test_add_entity_rejects_predicate_axis():
    s = WQSession()
    out = s.add_entity("bad", "M", "nope")
    assert out["ok"] is False
    assert "axis" in out["error"].lower()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_session.py -k add_entity -v`
Expected: FAIL with `AttributeError: 'WQSession' object has no attribute 'add_entity'`

- [ ] **Step 3: Implement `add_entity` and `_individual`**

Add these imports at the top of `session.py`:

```python
from wq import Individual
from wq.axes import is_value_axis
```

Add to `WQSession`:

```python
    def _individual(self, entity_id: str, axis: str,
                    label: Optional[str] = None) -> Individual:
        try:
            ax = Axis[axis]
        except KeyError:
            raise ValueError(f"Unknown axis '{axis}'. Use one of Q,O,L,T,N,K.")
        if not is_value_axis(ax):
            raise ValueError(
                f"Axis '{axis}' cannot hold entities. Value axes: Q,O,L,T,N,K."
            )
        return Individual(id=entity_id, axis=ax, label=label or entity_id)

    def add_entity(self, entity_id: str, axis: str,
                   label: Optional[str] = None) -> Dict[str, Any]:
        try:
            ind = self._individual(entity_id, axis, label)
        except ValueError as e:
            return {"ok": False, "error": str(e)}
        self.universe.add_individual(ind)
        return {"ok": True,
                "entity": {"id": ind.id, "axis": ind.axis.value, "label": ind.label}}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_session.py -k add_entity -v`
Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
git add mcp-server/wquestions_mcp/session.py mcp-server/tests/test_session.py
git commit -m "feat(mcp): add_entity tool places individuals on value axes"
```

---

## Task 3: `define_verb` — register situation types in the lexicon

**Files:**
- Modify: `mcp-server/wquestions_mcp/session.py`
- Test: `mcp-server/tests/test_session.py`

**Interfaces:**
- Produces: `WQSession.define_verb(verb: str, situation_type: str, obligatory: list[str] | None = None, optional: list[str] | None = None) -> dict` returning `{"ok": True, "verb": verb}`.

- [ ] **Step 1: Write the failing test**

Add to `test_session.py`:

```python
def test_define_verb_registers_entry():
    s = WQSession()
    out = s.define_verb("visit", "action_visit",
                        obligatory=["agente"], optional=["lugar_de", "momento"])
    assert out["ok"] is True
    entry = s.lexicon.resolve("visit")
    assert entry is not None
    assert entry.situation_type == "action_visit"
    assert entry.obligatory == ["agente"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_session.py -k define_verb -v`
Expected: FAIL with `AttributeError: ... 'define_verb'`

- [ ] **Step 3: Implement `define_verb`**

Add the import at the top of `session.py`:

```python
from wq import LexiconEntry
```

Add to `WQSession`:

```python
    def define_verb(self, verb: str, situation_type: str,
                    obligatory: Optional[List[str]] = None,
                    optional: Optional[List[str]] = None) -> Dict[str, Any]:
        self.lexicon.register(LexiconEntry(
            verb=verb,
            situation_type=situation_type,
            obligatory=obligatory or [],
            optional=optional or [],
        ))
        return {"ok": True, "verb": verb}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_session.py -k define_verb -v`
Expected: 1 passed.

- [ ] **Step 5: Commit**

```bash
git add mcp-server/wquestions_mcp/session.py mcp-server/tests/test_session.py
git commit -m "feat(mcp): define_verb registers situation types in the lexicon"
```

---

## Task 4: `assert_situation` — the core ingest tool

**Files:**
- Modify: `mcp-server/wquestions_mcp/session.py`
- Test: `mcp-server/tests/test_session.py`

**Interfaces:**
- Produces: `WQSession.assert_situation(verb, roles, extra=None, valid_from=None, valid_to=None) -> dict`.
  - `roles`: `dict[str, str | dict]` — role name → either an existing entity id, or an inline spec `{"id","axis","label"}` (auto-created).
  - `extra`: same shape as `roles`, for non-signature facts (`modalidad`, etc.).
  - `valid_from`/`valid_to`: ISO-8601 strings or `None`.
  - Returns `{"ok": True, "situation_id": str, "facts": [{"subject","role","value"}]}` or `{"ok": False, "error": str}`.
  - If `verb` is not yet in the lexicon, auto-registers a permissive entry (`situation_type=f"action_{verb}"`, no obligatory roles) so the LLM can model without a separate `define_verb` round-trip.

- [ ] **Step 1: Write the failing tests**

Add to `test_session.py`:

```python
def test_assert_situation_auto_registers_verb_and_ingests():
    s = WQSession()
    s.add_entity("ana", "Q", "Ana")
    s.add_entity("spa_oasis", "L", "Spa Oasis")
    out = s.assert_situation(
        "visit",
        roles={"agente": "ana", "lugar_de": "spa_oasis"},
    )
    assert out["ok"] is True
    # the reified situation carries the agente fact
    roles_seen = {f["role"] for f in out["facts"]}
    assert "agente" in roles_seen and "lugar_de" in roles_seen


def test_assert_situation_creates_inline_entities():
    s = WQSession()
    out = s.assert_situation(
        "visit",
        roles={"agente": {"id": "bob", "axis": "Q", "label": "Bob"}},
    )
    assert out["ok"] is True
    assert "bob" in s.universe.individuals


def test_assert_situation_reports_missing_entity():
    s = WQSession()
    out = s.assert_situation("visit", roles={"agente": "ghost"})
    assert out["ok"] is False
    assert "ghost" in out["error"]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_session.py -k assert_situation -v`
Expected: FAIL with `AttributeError: ... 'assert_situation'`

- [ ] **Step 3: Implement `assert_situation` + `_resolve_value` helper**

Add the import at the top of `session.py`:

```python
from datetime import datetime
from wq import ingest_situation, IngestError
```

Add to `WQSession`:

```python
    def _resolve_value(self, spec: Any) -> Individual:
        """A role value is either an existing entity id (str) or an inline
        spec dict {id, axis, label} to create on the fly."""
        if isinstance(spec, dict):
            ind = self._individual(spec["id"], spec["axis"], spec.get("label"))
            self.universe.add_individual(ind)
            return ind
        if spec in self.universe.individuals:
            return self.universe.individuals[spec]
        raise ValueError(
            f"Unknown entity '{spec}'. Create it with add_entity first, "
            f"or pass an inline spec {{'id','axis','label'}}."
        )

    @staticmethod
    def _parse_ts(value: Optional[str]) -> Optional[datetime]:
        if value is None:
            return None
        return datetime.fromisoformat(value.replace("Z", "+00:00"))

    def assert_situation(self, verb: str, roles: Dict[str, Any],
                         extra: Optional[Dict[str, Any]] = None,
                         valid_from: Optional[str] = None,
                         valid_to: Optional[str] = None) -> Dict[str, Any]:
        if self.lexicon.resolve(verb) is None:
            self.define_verb(verb, f"action_{verb}")
        try:
            resolved = {r: self._resolve_value(v) for r, v in roles.items()}
            resolved_extra = ({r: self._resolve_value(v) for r, v in extra.items()}
                              if extra else None)
            situ = ingest_situation(
                self.universe, self.lexicon, verb, resolved,
                extra=resolved_extra,
                valid_from=self._parse_ts(valid_from),
                valid_to=self._parse_ts(valid_to),
            )
        except (ValueError, IngestError) as e:
            return {"ok": False, "error": str(e)}
        facts = [
            {"subject": f.subject.id, "role": f.role, "value": f.value.id}
            for f in self.universe.facts_about(situ)
        ]
        return {"ok": True, "situation_id": situ.id, "facts": facts}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_session.py -k assert_situation -v`
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add mcp-server/wquestions_mcp/session.py mcp-server/tests/test_session.py
git commit -m "feat(mcp): assert_situation ingests facts (auto-verb, inline entities, validity)"
```

---

## Task 5: `ask` — query by projection over roles

**Files:**
- Modify: `mcp-server/wquestions_mcp/session.py`
- Test: `mcp-server/tests/test_session.py`

**Interfaces:**
- Produces: `WQSession.ask(fixed=None, ask=None, type=None, at=None) -> dict`.
  - `fixed`: `dict[str, str|dict]` — role → entity value that must match (resolved like `assert_situation`).
  - `ask`: `list[str]` — role names to project.
  - `type`: optional category id (K) constraining `instancia_de`.
  - `at`: optional ISO timestamp for temporal (D6) queries.
  - Returns `{"count": int, "results": [ {ask_role: value_id | [value_ids], "_subject": sid}, ... ]}`.

- [ ] **Step 1: Write the failing test**

Add to `test_session.py`:

```python
def test_ask_projects_the_asked_role():
    s = WQSession()
    s.add_entity("ana", "Q", "Ana")
    s.add_entity("spa_oasis", "L", "Spa Oasis")
    s.assert_situation("visit", roles={"agente": "ana", "lugar_de": "spa_oasis"})

    out = s.ask(fixed={"lugar_de": "spa_oasis"}, ask=["agente"])
    assert out["count"] == 1
    assert out["results"][0]["agente"] == "ana"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_session.py -k test_ask -v`
Expected: FAIL with `AttributeError: ... 'ask'`

- [ ] **Step 3: Implement `ask`**

Add the import at the top of `session.py`:

```python
from wq import Pattern, Var, query, category
```

Add to `WQSession`:

```python
    def ask(self, fixed: Optional[Dict[str, Any]] = None,
            ask: Optional[List[str]] = None,
            type: Optional[str] = None,
            at: Optional[str] = None) -> Dict[str, Any]:
        try:
            fixed_ind = ({r: self._resolve_value(v) for r, v in fixed.items()}
                         if fixed else {})
        except ValueError as e:
            return {"ok": False, "error": str(e)}
        pattern = Pattern(
            fixed=fixed_ind,
            ask={role: Var(role) for role in (ask or [])},
            type_constraint=category(type) if type else None,
        )
        bindings = query(self.universe, pattern, at=self._parse_ts(at))
        results = []
        for b in bindings:
            row: Dict[str, Any] = {"_subject": b["_subject"].id}
            for role in (ask or []):
                val = b.get(role)
                if isinstance(val, list):
                    row[role] = [v.id for v in val]
                elif val is not None:
                    row[role] = val.id
            results.append(row)
        return {"count": len(results), "results": results}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_session.py -k test_ask -v`
Expected: 1 passed.

- [ ] **Step 5: Commit**

```bash
git add mcp-server/wquestions_mcp/session.py mcp-server/tests/test_session.py
git commit -m "feat(mcp): ask tool queries by projection over roles (with temporal filter)"
```

---

## Task 6: `show_model` + `load_example` — introspection and instant demo

**Files:**
- Modify: `mcp-server/wquestions_mcp/session.py`
- Create: `mcp-server/wquestions_mcp/examples.py`
- Test: `mcp-server/tests/test_session.py`

**Interfaces:**
- Produces:
  - `WQSession.show_model() -> dict` → `{"summary": str, "entity_count": int, "fact_count": int, "facts": [{"subject","role","value"}]}`.
  - `WQSession.load_example(name: str) -> dict` → `{"ok": True, "loaded": name, "fact_count": int}` or `{"ok": False, "error": str}`.
  - `wquestions_mcp/examples.py`: `build_spa(session) -> None` that populates a session via its public methods, and `EXAMPLES = {"spa": build_spa}`.

- [ ] **Step 1: Write the failing tests**

Add to `test_session.py`:

```python
def test_show_model_reports_counts():
    s = WQSession()
    s.add_entity("ana", "Q", "Ana")
    s.assert_situation("visit", roles={"agente": "ana"})
    out = s.show_model()
    assert out["fact_count"] >= 1
    assert any(f["role"] == "agente" for f in out["facts"])


def test_load_example_spa_populates_model():
    s = WQSession()
    out = s.load_example("spa")
    assert out["ok"] is True
    assert out["fact_count"] > 0


def test_load_example_unknown_name_errors():
    s = WQSession()
    out = s.load_example("does_not_exist")
    assert out["ok"] is False
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_session.py -k "show_model or load_example" -v`
Expected: FAIL with `AttributeError` / `ModuleNotFoundError: ... examples`

- [ ] **Step 3: Create the example builder**

Create `mcp-server/wquestions_mcp/examples.py`:

```python
"""Prebuilt demo universes, populated through WQSession's public API so the
demo path exercises exactly what an LLM client would call."""
from __future__ import annotations


def build_spa(session) -> None:
    """A tiny spa: two clients, three visits across two years."""
    session.add_entity("ana", "Q", "Ana")
    session.add_entity("beto", "Q", "Beto")
    session.add_entity("spa_oasis", "L", "Spa Oasis")
    for agent, when in [("ana", "2024-03-01"),
                        ("ana", "2025-06-10"),
                        ("beto", "2025-06-11")]:
        session.assert_situation(
            "visit",
            roles={"agente": agent, "lugar_de": "spa_oasis"},
            valid_from=when,
        )


EXAMPLES = {"spa": build_spa}
```

- [ ] **Step 4: Implement `show_model` and `load_example`**

Add to `WQSession` in `session.py`:

```python
    def show_model(self) -> Dict[str, Any]:
        facts = [
            {"subject": f.subject.id, "role": f.role, "value": f.value.id}
            for f in self.universe.facts
        ]
        return {
            "summary": self.universe.summary(),
            "entity_count": len(self.universe.individuals),
            "fact_count": len(self.universe.facts),
            "facts": facts,
        }

    def load_example(self, name: str) -> Dict[str, Any]:
        from .examples import EXAMPLES
        builder = EXAMPLES.get(name)
        if builder is None:
            return {"ok": False,
                    "error": f"Unknown example '{name}'. Available: {list(EXAMPLES)}"}
        self.reset()
        builder(self)
        return {"ok": True, "loaded": name, "fact_count": len(self.universe.facts)}
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/test_session.py -v`
Expected: all tests pass (Tasks 1-6).

- [ ] **Step 6: Commit**

```bash
git add mcp-server/wquestions_mcp/session.py mcp-server/wquestions_mcp/examples.py mcp-server/tests/test_session.py
git commit -m "feat(mcp): show_model introspection + load_example demo loader"
```

---

## Task 7: MCP server wiring + entry point

**Files:**
- Create: `mcp-server/wquestions_mcp/server.py`
- Test: manual smoke test (documented below) — the FastMCP wrapper has no logic to unit-test; all logic is already covered in `test_session.py`.

**Interfaces:**
- Consumes: `WQSession` (all methods from Tasks 1-6).
- Produces: `main()` console entry point that runs the server over stdio, and one `@mcp.tool()` per `WQSession` method.

- [ ] **Step 1: Implement the FastMCP wrapper**

Create `mcp-server/wquestions_mcp/server.py`:

```python
"""FastMCP wrapper: one tool per WQSession method. No logic here — all
behaviour lives in (and is tested via) session.py. A single WQSession is
held per server process."""
from __future__ import annotations
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP

from .session import WQSession

mcp = FastMCP("wquestions")
_session = WQSession()


@mcp.tool()
def list_axes() -> Dict[str, Any]:
    """List the 7 WQuestions axes (Q who, O what, L where, T when, N how-much,
    K which, M how) and what each is for."""
    return _session.list_axes()


@mcp.tool()
def list_roles() -> Dict[str, Any]:
    """List the canonical roles with their typed signatures. Unknown roles are
    also allowed (liberal policy) — you may invent domain roles freely."""
    return _session.list_roles()


@mcp.tool()
def add_entity(entity_id: str, axis: str, label: Optional[str] = None) -> Dict[str, Any]:
    """Create an individual on a value axis (Q, O, L, T, N, or K)."""
    return _session.add_entity(entity_id, axis, label)


@mcp.tool()
def define_verb(verb: str, situation_type: str,
                obligatory: Optional[List[str]] = None,
                optional: Optional[List[str]] = None) -> Dict[str, Any]:
    """Register a situation type (verb) and which roles it takes. Optional:
    assert_situation auto-registers unknown verbs permissively."""
    return _session.define_verb(verb, situation_type, obligatory, optional)


@mcp.tool()
def assert_situation(verb: str, roles: Dict[str, Any],
                     extra: Optional[Dict[str, Any]] = None,
                     valid_from: Optional[str] = None,
                     valid_to: Optional[str] = None) -> Dict[str, Any]:
    """Assert a fact: reify a situation for `verb` and attach its roles.
    Each role value is an existing entity id or an inline {id, axis, label}.
    valid_from/valid_to are ISO-8601 for time-varying facts (D6)."""
    return _session.assert_situation(verb, roles, extra, valid_from, valid_to)


@mcp.tool()
def ask(fixed: Optional[Dict[str, Any]] = None,
        ask: Optional[List[str]] = None,
        type: Optional[str] = None,
        at: Optional[str] = None) -> Dict[str, Any]:
    """Query by projection: fix some roles, ask for others. `at` (ISO) queries
    the model as it was valid at that time."""
    return _session.ask(fixed, ask, type, at)


@mcp.tool()
def show_model() -> Dict[str, Any]:
    """Dump the current universe: entity/fact counts and every fact."""
    return _session.show_model()


@mcp.tool()
def load_example(name: str) -> Dict[str, Any]:
    """Load a prebuilt demo universe (e.g. "spa") to try queries instantly."""
    return _session.load_example(name)


@mcp.tool()
def reset() -> Dict[str, Any]:
    """Clear the model and start a fresh empty universe."""
    return _session.reset()


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Smoke-test that the module imports and tools register**

Run (from `mcp-server/`):
```bash
python3 -c "from wquestions_mcp import server; print(sorted(t.name for t in __import__('asyncio').run(server.mcp.list_tools())))"
```
Expected: a list containing `add_entity, ask, assert_situation, define_verb, list_axes, list_roles, load_example, reset, show_model`.
(If the installed `mcp` version's `list_tools()` signature differs, fall back to: `python3 -c "from wquestions_mcp import server; print('import ok')"` and rely on the live client check in Step 3.)

- [ ] **Step 3: Smoke-test the entry point launches**

Run: `wquestions-mcp` — it should start and block waiting on stdio (no crash, no traceback). Stop with Ctrl-C.

- [ ] **Step 4: Commit**

```bash
git add mcp-server/wquestions_mcp/server.py
git commit -m "feat(mcp): FastMCP server wiring + wquestions-mcp entry point"
```

---

## Task 8: README quickstart + recorded-demo script (0.2 + 0.3)

**Files:**
- Create: `mcp-server/README.md`
- Create: `mcp-server/DEMO.md`

**Interfaces:** none (documentation). This is the artifact devs actually see.

- [ ] **Step 1: Write the README**

Create `mcp-server/README.md` with, in this order: a one-line hook ("Model any domain in 7 questions."); the problem (per-domain ontologies don't scale for AI); the 7 axes in a compact table; a placeholder line for the demo GIF (`![demo](docs/demo.gif)`); a **Quickstart** with the copy-paste Claude Desktop config block below; a "How it works" paragraph (LLM does NL→roles, server does ingest/query over the wq engine); and a link to the book as the deep-dive. All English.

Claude Desktop config block to include verbatim:

```json
{
  "mcpServers": {
    "wquestions": {
      "command": "uvx",
      "args": ["wquestions-mcp"]
    }
  }
}
```

- [ ] **Step 2: Write the recorded-demo script**

Create `mcp-server/DEMO.md` — the exact 30-60s scenario to screen-record for the GIF. It MUST be runnable verbatim in Claude Desktop after wiring the server:

```
1. "Load the spa example, then show me the model."      -> load_example("spa") + show_model()
2. "Who visited Spa Oasis?"                              -> ask(fixed={lugar_de: spa_oasis}, ask=[agente])
3. "Now model MY business: a barbershop. Diego cut       -> add_entity + assert_situation calls
    Marco's hair on 2025-06-11 at Barber Kings."
4. "Who did Diego serve, and where?"                     -> ask(...) returns Marco / Barber Kings
```
The point the GIF must land: **the same 7 tools model a spa and a barbershop with zero per-domain schema.**

- [ ] **Step 3: Verify the quickstart on a clean path**

Follow `README.md` yourself from a fresh virtualenv: install, add the config, restart Claude Desktop, run DEMO.md step 1. Confirm `< 5 min` and the tools respond. Fix any friction found (this is the Fase 0 acceptance gate).

- [ ] **Step 4: Commit**

```bash
git add mcp-server/README.md mcp-server/DEMO.md
git commit -m "docs(mcp): README quickstart + recorded-demo script"
```

---

## Manual / user-owned steps (not agent tasks)

These are outward-facing actions Jose performs on his own accounts — the plan
stops at producing everything they need:

- **Record the demo GIF** following `DEMO.md`; drop it at `mcp-server/docs/demo.gif` and confirm the README renders it.
- **Publish to PyPI**: BOTH distributions must be published for `uvx wquestions-mcp`
  to resolve — `wquestions-engine` (from `prototipo/`) AND `wquestions-mcp` (from
  `mcp-server/`), since the latter depends on the former and neither is on PyPI yet
  (alternatively, bundle the engine into the mcp-server wheel so only one dist needs
  publishing) — OR document the `pip install git+…` fallback in the README until
  PyPI is live.
- **Create the public GitHub repo** from `mcp-server/` (0.2) and **enable GitHub Discussions** (0.4). Discord stays off until there's traction.

---

## Self-Review

**Spec coverage:**
- 0.1 MCP server → Tasks 1-7 (tools: model_fact→`assert_situation`, `query`→`ask`, `list_axes`, `list_roles`, `show_model`, `explain_domain`→`load_example`). ✓
- 0.2 repo + README → Task 8 Step 1 + manual repo creation. ✓
- 0.3 demo → Task 8 Step 2 (`DEMO.md`) + manual recording. ✓
- 0.4 Discussions → manual step (user-owned, outward-facing). ✓
- Acceptance (<5 min quickstart) → Task 8 Step 3. ✓

**Placeholder scan:** the only intentional placeholder is the demo-GIF image path (`docs/demo.gif`), which the manual recording step fills — flagged, not a code gap. No TBD/TODO in code steps.

**Type consistency:** `WQSession` method names match between `session.py` (definition) and `server.py` (Task 7 wrappers): `list_axes, list_roles, add_entity, define_verb, assert_situation, ask, show_model, load_example, reset`. `_resolve_value`/`_individual`/`_parse_ts` helpers are defined in Task 2/4 before their reuse in Tasks 4/5. `roles`/`fixed` value shape (`str | {id,axis,label}`) is consistent across `assert_situation` and `ask`.

**Note on `catalog._roles`:** `list_roles` reads the engine's private `_roles` dict — acceptable for a read-only introspection wrapper; if the engine later exposes a public accessor, switch to it.
