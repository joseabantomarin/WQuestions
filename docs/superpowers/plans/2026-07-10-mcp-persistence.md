# WQuestions MCP Persistence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the modeled universe survive server restarts automatically by writing every mutating op to an append-only JSONL log and replaying it on startup — no survival ritual, engine untouched.

**Architecture:** All logic in `WQSession` (`session.py`). A per-session log path (resolved from `WQUESTIONS_LOG`, on by default); each mutating method appends a JSON event on success; `__init__` replays the file. Situation ids are MCP-controlled and stored in events so replay is a pure function of the log. `server.py` only wires the resolved path in.

**Tech Stack:** Python 3.12 (venv), stdlib `json`/`os`, the `wq` engine (via its public `ingest_situation(sit_id=...)`), pytest.

## Global Constraints

- **Implement the fidelity plan first** (`2026-07-10-mcp-wquestions-fidelity.md`). This plan wraps the final method signatures: `correct(...)`, `add_entity(..., value, unit)`, `ask(..., history)`, and the enriched `show_model`.
- **Do NOT modify the `wq` engine.** Use only public API (`ingest_situation` with its existing `sit_id` param, `universe.*`).
- **All user-facing strings English.**
- **`WQSession()` stays in-memory by default** (`log_path=None`) so every existing and fidelity test is unaffected and never touches disk. Default-on persistence lives only in `server.py`.
- **Run through the venv:** `cd /Users/joseabanto/WQuestions/mcp-server && /Users/joseabanto/WQuestions/.venv/bin/pytest ...`. System `python3` (3.9) MUST NOT be used.
- **Non-goals:** no log compaction, no multi-writer/concurrency, no cross-version migration.

## File Structure

- `mcp-server/wquestions_mcp/session.py` — gains: module `import os, json`; `DEFAULT_LOG_PATH`; `resolve_log_path`; `WQSession.__init__(log_path)`, `_fresh`, `_append_event`, `_replay`, `_bump_sit_seq`; `_sit_seq`/`_suppress_log`/`_log_path`/`_replayed_events`/`_skipped_lines` state; `_append_event` calls in every mutating method; MCP-controlled situation id in `assert_situation`; `persistence` block in `show_model`.
- `mcp-server/wquestions_mcp/server.py` — build `_session` with `resolve_log_path(os.environ.get("WQUESTIONS_LOG"))`.
- `mcp-server/tests/test_persistence.py` — NEW: resolution, round-trip, reset marker, load_example, in-memory default, tolerance.

---

### Task 1: Log-path resolution (pure function)

**Files:**
- Modify: `mcp-server/wquestions_mcp/session.py`
- Test: `mcp-server/tests/test_persistence.py` (create)

**Interfaces:**
- Produces: `DEFAULT_LOG_PATH: str` and `resolve_log_path(raw: Optional[str]) -> Optional[str]`. `None` (unset) → expanded default; `off`/`none`/`:memory:`/empty (case-insensitive) → `None`; anything else → `os.path.expanduser(raw)`.

- [ ] **Step 1: Write the failing test**

Create `mcp-server/tests/test_persistence.py`:

```python
import os
from wquestions_mcp.session import resolve_log_path, DEFAULT_LOG_PATH


def test_resolve_unset_uses_expanded_default():
    assert resolve_log_path(None) == os.path.expanduser(DEFAULT_LOG_PATH)


def test_resolve_off_sentinels_disable():
    for raw in ["off", "OFF", "none", ":memory:", "", "  "]:
        assert resolve_log_path(raw) is None


def test_resolve_explicit_path_is_expanded():
    assert resolve_log_path("/tmp/u.jsonl") == "/tmp/u.jsonl"
    assert resolve_log_path("~/x.jsonl") == os.path.expanduser("~/x.jsonl")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /Users/joseabanto/WQuestions/mcp-server && /Users/joseabanto/WQuestions/.venv/bin/pytest tests/test_persistence.py -v`
Expected: FAIL with `ImportError: cannot import name 'resolve_log_path'`.

- [ ] **Step 3: Add the resolver to `session.py`**

At the top of `session.py`, add `import os` and `import json` to the imports, then add near the top (after the imports, before `_AXIS_NAMES`):

```python
DEFAULT_LOG_PATH = "~/.wquestions/universe.jsonl"


def resolve_log_path(raw: Optional[str]) -> Optional[str]:
    """Resolve the persistence log path. None (env unset) -> default file;
    off/none/:memory:/empty -> None (pure in-memory); else the expanded path."""
    if raw is None:
        raw = DEFAULT_LOG_PATH
    if raw.strip().lower() in ("", "off", "none", ":memory:"):
        return None
    return os.path.expanduser(raw)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /Users/joseabanto/WQuestions/mcp-server && /Users/joseabanto/WQuestions/.venv/bin/pytest tests/test_persistence.py -v`
Expected: PASS (3 tests).

- [ ] **Step 5: Commit**

```bash
cd /Users/joseabanto/WQuestions && git add mcp-server/wquestions_mcp/session.py mcp-server/tests/test_persistence.py
git commit -m "$(printf 'feat(mcp): resolve_log_path — persistence path resolution (on by default, off-able)\n\nCo-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>')"
```

---

### Task 2: Persistence core — log on mutation, replay on startup

**Files:**
- Modify: `mcp-server/wquestions_mcp/session.py` (`__init__`, `_fresh`, `reset`, `_append_event`, `_replay`, `_bump_sit_seq`, and `_append_event` wiring in `add_entity`/`define_verb`/`assert_situation`/`correct`/`load_example`; MCP-controlled situation id)
- Modify: `mcp-server/wquestions_mcp/server.py` (wire resolved path)
- Test: `mcp-server/tests/test_persistence.py`

**Interfaces:**
- Consumes: `resolve_log_path` (Task 1); `wq.ingest_situation(sit_id=...)`.
- Produces: `WQSession(log_path: Optional[str] = None)`; on the same `log_path` a fresh session reconstructs the universe. Event line format `{"v": 1, "op": <op>, "args": {...}}`. Situation ids are `{situation_type}_{NNNNNN}`, assigned by the session and stored in the `assert_situation` event under `_sit_id`.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_persistence.py`:

```python
from wquestions_mcp.session import WQSession


def test_in_memory_session_writes_no_file(tmp_path):
    s = WQSession(log_path=None)
    s.add_entity("ana", "Q", "Ana")
    s.assert_situation("visit", roles={"agente": "ana"})
    assert list(tmp_path.iterdir()) == []  # nothing written anywhere we own


def test_round_trip_rebuilds_universe_and_corrections(tmp_path):
    p = str(tmp_path / "u.jsonl")
    s = WQSession(log_path=p)
    s.add_entity("ana", "Q", "Ana")
    s.add_entity("beto", "Q", "Beto")
    s.add_entity("spa", "L", "Spa")
    out = s.assert_situation("visit", roles={"agente": "ana", "lugar_de": "spa"})
    s.correct(out["situation_id"], "agente", "beto")

    s2 = WQSession(log_path=p)  # simulates a restart
    assert "ana" in s2.universe.individuals and "beto" in s2.universe.individuals
    res = s2.ask(fixed={"lugar_de": "spa"}, ask=["agente"])
    assert res["results"][0]["agente"] == "beto"          # correction survived
    hist = s2.ask(fixed={"lugar_de": "spa"}, ask=["agente"], history=True)
    assert hist["results"][0]["agente"] == ["ana", "beto"]


def test_reset_marker_keeps_only_post_reset_state(tmp_path):
    p = str(tmp_path / "u.jsonl")
    s = WQSession(log_path=p)
    s.add_entity("ana", "Q", "Ana")
    s.reset()
    s.add_entity("beto", "Q", "Beto")

    s2 = WQSession(log_path=p)
    assert "beto" in s2.universe.individuals
    assert "ana" not in s2.universe.individuals


def test_load_example_round_trips_as_single_event(tmp_path):
    p = str(tmp_path / "u.jsonl")
    s = WQSession(log_path=p)
    s.load_example("spa")
    facts_before = s.show_model()["fact_count"]

    s2 = WQSession(log_path=p)
    assert s2.show_model()["fact_count"] == facts_before
    with open(p, encoding="utf-8") as f:
        ops = [__import__("json").loads(ln)["op"] for ln in f if ln.strip()]
    assert ops.count("load_example") == 1
    assert "add_entity" not in ops  # inner builder calls were not double-logged
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/joseabanto/WQuestions/mcp-server && /Users/joseabanto/WQuestions/.venv/bin/pytest tests/test_persistence.py -k "round_trip or reset_marker or load_example or in_memory" -v`
Expected: FAIL — `WQSession() takes no keyword argument 'log_path'`.

- [ ] **Step 3: Rework construction, `_fresh`, and `reset`**

In `session.py`, replace `__init__` and `reset` with:

```python
    def __init__(self, log_path: Optional[str] = None) -> None:
        self._log_path = log_path
        self._suppress_log = False
        self._sit_seq = 1
        self._replayed_events = 0
        self._skipped_lines = 0
        self._fresh()
        if self._log_path and os.path.exists(self._log_path):
            self._replay()

    def _fresh(self) -> None:
        self.catalog = Catalog()
        self.universe = Universe(name="session", catalog=self.catalog)
        self.lexicon = Lexicon()
        self._sit_seq = 1

    def reset(self) -> Dict[str, Any]:
        self._fresh()
        self._append_event("reset", {})
        return {"ok": True}
```

- [ ] **Step 4: Add the log/replay helpers**

In `session.py`, add these methods to `WQSession` (place them right after `reset`):

```python
    def _append_event(self, op: str, args: Dict[str, Any]) -> None:
        if not self._log_path or self._suppress_log:
            return
        parent = os.path.dirname(self._log_path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(self._log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"v": 1, "op": op, "args": args}) + "\n")
            f.flush()

    def _bump_sit_seq(self, sit_id: str) -> None:
        try:
            n = int(sit_id.rsplit("_", 1)[-1])
        except (ValueError, IndexError):
            return
        if n >= self._sit_seq:
            self._sit_seq = n + 1

    def _replay(self) -> None:
        dispatch = {
            "add_entity": self.add_entity,
            "define_verb": self.define_verb,
            "assert_situation": self.assert_situation,
            "correct": self.correct,
            "load_example": self.load_example,
            "reset": self.reset,
        }
        prev = self._suppress_log
        self._suppress_log = True
        try:
            with open(self._log_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        evt = json.loads(line)
                        method = dispatch.get(evt.get("op"))
                        if method is None:
                            raise ValueError(f"unknown op {evt.get('op')!r}")
                        result = method(**evt.get("args", {}))
                        if isinstance(result, dict) and result.get("ok") is False:
                            raise ValueError(result.get("error", "replay failed"))
                    except Exception:
                        self._skipped_lines += 1
                        continue
                    self._replayed_events += 1
        finally:
            self._suppress_log = prev
```

- [ ] **Step 5: Log events from the mutating methods**

In `add_entity`, immediately before `return {"ok": True, "entity": ...}`, insert:

```python
        self._append_event("add_entity", {"entity_id": entity_id, "axis": axis,
                                           "label": label, "value": value,
                                           "unit": unit})
```

In `define_verb`, immediately before `return {"ok": True, "verb": verb}`, insert:

```python
        self._append_event("define_verb", {"verb": verb,
                                            "situation_type": situation_type,
                                            "obligatory": obligatory,
                                            "optional": optional})
```

In `correct`, immediately before the success `return {"ok": True, "situation_id": ...}`, insert:

```python
        self._append_event("correct", {"situation_id": situation_id, "role": role,
                                        "value": value, "valid_from": valid_from,
                                        "valid_to": valid_to})
```

Replace `load_example` with (suppress inner calls, log one event, `_fresh` instead of `reset`):

```python
    def load_example(self, name: str) -> Dict[str, Any]:
        from .examples import EXAMPLES
        builder = EXAMPLES.get(name)
        if builder is None:
            return {"ok": False,
                    "error": f"Unknown example '{name}'. Available: {list(EXAMPLES)}"}
        prev = self._suppress_log
        self._suppress_log = True
        try:
            self._fresh()
            builder(self)
        finally:
            self._suppress_log = prev
        self._append_event("load_example", {"name": name})
        return {"ok": True, "loaded": name, "fact_count": len(self.universe.facts)}
```

- [ ] **Step 6: MCP-control the situation id in `assert_situation` and log the event**

In `session.py`, replace the `assert_situation` method body so it assigns the id, passes `sit_id`, accepts a replay `_sit_id`, bumps the sequence, and logs (keep the fidelity docstring/behavior; only the id handling and the log line are new):

```python
    def assert_situation(self, verb: str, roles: Dict[str, Any],
                         extra: Optional[Dict[str, Any]] = None,
                         valid_from: Optional[str] = None,
                         valid_to: Optional[str] = None,
                         _sit_id: Optional[str] = None) -> Dict[str, Any]:
        if self.lexicon.resolve(verb) is None:
            self.define_verb(verb, f"action_{verb}")
        try:
            resolved = {r: self._resolve_value(v) for r, v in roles.items()}
            resolved_extra = ({r: self._resolve_value(v) for r, v in extra.items()}
                              if extra else None)
            entry = self.lexicon.resolve(verb)
            sid = _sit_id or f"{entry.situation_type}_{self._sit_seq:06d}"
            situ = ingest_situation(
                self.universe, self.lexicon, verb, resolved,
                extra=resolved_extra,
                valid_from=self._parse_ts(valid_from),
                valid_to=self._parse_ts(valid_to),
                sit_id=sid,
            )
        except (ValueError, IngestError) as e:
            return {"ok": False, "error": str(e)}
        self._bump_sit_seq(situ.id)
        self._append_event("assert_situation",
                           {"verb": verb, "roles": roles, "extra": extra,
                            "valid_from": valid_from, "valid_to": valid_to,
                            "_sit_id": situ.id})
        facts = [
            {"subject": f.subject.id, "role": f.role, "value": f.value.id}
            for f in self.universe.facts_about(situ)
        ]
        return {"ok": True, "situation_id": situ.id, "facts": facts}
```

- [ ] **Step 7: Wire the resolved path into `server.py`**

In `server.py`, add `import os` at the top and update the imports + session construction:

```python
from .session import WQSession, resolve_log_path

mcp = FastMCP("wquestions", instructions=INSTRUCTIONS)
_session = WQSession(log_path=resolve_log_path(os.environ.get("WQUESTIONS_LOG")))
```

- [ ] **Step 8: Run the persistence tests**

Run: `cd /Users/joseabanto/WQuestions/mcp-server && /Users/joseabanto/WQuestions/.venv/bin/pytest tests/test_persistence.py -v`
Expected: PASS (all resolution + round-trip + reset + load_example + in-memory tests).

- [ ] **Step 9: Run the FULL suite (no existing test may regress)**

Run: `cd /Users/joseabanto/WQuestions/mcp-server && /Users/joseabanto/WQuestions/.venv/bin/pytest -q`
Expected: PASS — every fidelity/session/server test still green (they use `WQSession()` = in-memory, so nothing touches disk).

- [ ] **Step 10: Commit**

```bash
cd /Users/joseabanto/WQuestions && git add mcp-server/wquestions_mcp/session.py mcp-server/wquestions_mcp/server.py mcp-server/tests/test_persistence.py
git commit -m "$(printf 'feat(mcp): durable persistence via append-only JSONL event log + replay\n\nEvery mutating op appends an event; a fresh session replays the log on startup.\nSituation ids are MCP-controlled and stored in events, so replay is a pure\nfunction of the log. On by default via WQUESTIONS_LOG; WQSession() stays in-memory.\n\nCo-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>')"
```

---

### Task 3: Observability + tolerant replay

**Files:**
- Modify: `mcp-server/wquestions_mcp/session.py` (`show_model` persistence block)
- Test: `mcp-server/tests/test_persistence.py`

**Interfaces:**
- Consumes: `_log_path`, `_replayed_events`, `_skipped_lines`.
- Produces: `show_model()` gains a `persistence` key: `{"path", "replayed_events", "skipped_lines"}` when a log is active, else `{"enabled": False}`. (Tolerant replay already skips+counts malformed lines from Task 2; this task asserts it.)

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_persistence.py`:

```python
def test_show_model_reports_persistence_when_active(tmp_path):
    p = str(tmp_path / "u.jsonl")
    s = WQSession(log_path=p)
    s.add_entity("ana", "Q", "Ana")
    s2 = WQSession(log_path=p)
    pers = s2.show_model()["persistence"]
    assert pers["path"] == p
    assert pers["replayed_events"] == 1
    assert pers["skipped_lines"] == 0


def test_show_model_reports_disabled_in_memory():
    s = WQSession(log_path=None)
    assert s.show_model()["persistence"] == {"enabled": False}


def test_replay_skips_and_counts_a_corrupt_line(tmp_path):
    p = tmp_path / "u.jsonl"
    s = WQSession(log_path=str(p))
    s.add_entity("ana", "Q", "Ana")
    s.add_entity("beto", "Q", "Beto")
    # simulate a half-written trailing line from a crash
    with open(p, "a", encoding="utf-8") as f:
        f.write('{"v": 1, "op": "add_entity", "args": {"entity_id": "cor')

    s2 = WQSession(log_path=str(p))
    assert "ana" in s2.universe.individuals and "beto" in s2.universe.individuals
    pers = s2.show_model()["persistence"]
    assert pers["replayed_events"] == 2
    assert pers["skipped_lines"] == 1
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/joseabanto/WQuestions/mcp-server && /Users/joseabanto/WQuestions/.venv/bin/pytest tests/test_persistence.py -k "persistence_when_active or disabled_in_memory or corrupt_line" -v`
Expected: FAIL with `KeyError: 'persistence'`.

- [ ] **Step 3: Add the persistence block to `show_model`**

In `session.py`, in `show_model`, build the block and add it to the returned dict (keep every existing key, including the fidelity `legend`):

```python
        persistence = (
            {"path": self._log_path,
             "replayed_events": self._replayed_events,
             "skipped_lines": self._skipped_lines}
            if self._log_path else {"enabled": False}
        )
```

and add `"persistence": persistence,` to the returned dict.

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/joseabanto/WQuestions/mcp-server && /Users/joseabanto/WQuestions/.venv/bin/pytest tests/test_persistence.py -v`
Expected: PASS (all persistence tests).

- [ ] **Step 5: Run the FULL suite as the final gate**

Run: `cd /Users/joseabanto/WQuestions/mcp-server && /Users/joseabanto/WQuestions/.venv/bin/pytest -q`
Expected: PASS (fidelity + session + server + persistence all green).

- [ ] **Step 6: Manual smoke (real restart)**

Point a throwaway log at a temp file and drive the server twice to confirm cross-restart survival:

Run:
```bash
cd /Users/joseabanto/WQuestions/mcp-server && \
WQUESTIONS_LOG=/tmp/wq_smoke.jsonl /Users/joseabanto/WQuestions/.venv/bin/python -c "
from wquestions_mcp.session import WQSession, resolve_log_path
import os
p = resolve_log_path(os.environ['WQUESTIONS_LOG'])
s = WQSession(log_path=p); s.reset()
s.add_entity('ana','Q','Ana'); s.assert_situation('visit', roles={'agente':'ana'})
print('session1 facts:', s.show_model()['fact_count'])
s2 = WQSession(log_path=p)
print('session2 (restart) facts:', s2.show_model()['fact_count'], s2.show_model()['persistence'])
"; rm -f /tmp/wq_smoke.jsonl
```
Expected: session2 shows the same fact_count as session1 and a `persistence` block with `replayed_events > 0`.

- [ ] **Step 7: Commit**

```bash
cd /Users/joseabanto/WQuestions && git add mcp-server/wquestions_mcp/session.py mcp-server/tests/test_persistence.py
git commit -m "$(printf 'feat(mcp): show_model reports persistence status; assert tolerant replay\n\nCo-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>')"
```

---

## Self-Review

**Spec coverage:**
- Append-only JSONL log of mutating ops → Task 2 (`_append_event` in every mutating method). ✓
- Replay on startup → Task 2 (`__init__` → `_replay`). ✓
- Reset marker semantics → Task 2 (`reset` logs marker; `_replay` re-runs `reset`→`_fresh`); tested `test_reset_marker_keeps_only_post_reset_state`. ✓
- Valid-time preserved / correction order → Task 2 round-trip test asserts current + history. ✓
- MCP-controlled situation ids stored + replayed → Task 2 Step 6; round-trip correction test depends on it. ✓
- On-by-default / off-able / in-memory isolation → Task 1 `resolve_log_path`; Task 2 server wiring + `test_in_memory_session_writes_no_file`. ✓
- Tolerant load (skip+count) → Task 2 `_replay`; Task 3 `test_replay_skips_and_counts_a_corrupt_line`. ✓
- Observability (`show_model.persistence`) → Task 3. ✓
- load_example single event / no double-log → Task 2 `test_load_example_round_trips_as_single_event`. ✓

**Placeholder scan:** none — every code step shows full code; commands are exact with expected output.

**Type consistency:** `resolve_log_path(raw) -> Optional[str]`, `WQSession(log_path=None)`, `_append_event(op, args)`, `_replay()`, `_bump_sit_seq(sit_id)`, `assert_situation(..., _sit_id=None)` used consistently across tasks and the `server.py` wiring. Event `op` strings match the `_replay` dispatch keys exactly (`add_entity`, `define_verb`, `assert_situation`, `correct`, `load_example`, `reset`). ✓

**Global constraints:** engine untouched (only `ingest_situation(sit_id=...)` + public `universe`); English strings; `WQSession()` in-memory default keeps prior suites green; venv path in every command. ✓
