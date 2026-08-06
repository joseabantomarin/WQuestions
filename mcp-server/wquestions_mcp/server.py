"""FastMCP wrapper: one tool per WQSession method. No logic here — all
behaviour lives in (and is tested via) session.py. A single WQSession is
held per server process."""
from __future__ import annotations
import os
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP

from .session import WQSession, resolve_log_path

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
- Your universe is persisted to an append-only log and reloaded on restart, so it
  survives across sessions (on by default; show_model reports the log path and how
  many events were replayed). Working state is in-memory within the process and
  nothing is silently lost. Use show_model to inspect and reset to start a fresh
  domain; do not build recovery rituals.
- Start with list_axes and list_roles — they describe the vocabulary and its
  typed signatures.
"""

mcp = FastMCP("wquestions", instructions=INSTRUCTIONS)
_session = WQSession(log_path=resolve_log_path(os.environ.get("WQUESTIONS_LOG")))


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
def add_entity(entity_id: str, axis: str, label: Optional[str] = None,
               value: Optional[float] = None,
               unit: Optional[Any] = None) -> Dict[str, Any]:
    """Create an individual on a value axis (Q, O, L, T, N, K). For N you MUST
    pass `value` (a number) and `unit` (an existing K entity id, or an inline
    {id, axis:'K', label}); a magnitude without a unit is rejected. Never assume
    a unit — ask for it. `value`/`unit` apply only to N."""
    return _session.add_entity(entity_id, axis, label, value, unit)


@mcp.tool()
def define_verb(verb: str, situation_type: str,
                obligatory: Optional[List[str]] = None,
                optional: Optional[List[str]] = None) -> Dict[str, Any]:
    """Register a situation type (verb) and the roles it takes. `obligatory`
    roles ARE enforced: assert_situation rejects a situation missing one. Leaving
    `obligatory` empty makes every role optional — a deliberate choice, not a
    limit. assert_situation also auto-registers unknown verbs permissively."""
    return _session.define_verb(verb, situation_type, obligatory, optional)


@mcp.tool()
def assert_situation(verb: str, roles: Dict[str, Any],
                     extra: Optional[Dict[str, Any]] = None,
                     valid_from: Optional[str] = None,
                     valid_to: Optional[str] = None) -> Dict[str, Any]:
    """Assert a fact. The situation is REIFIED: a new node is minted in axis O
    and each role becomes one binary triplet (situation · role · value) — that is
    what this returns. Each role value is an existing entity id or an inline
    {id, axis, label}; for N pass an inline magnitude {id, axis:'N', value, unit}.
    valid_from/valid_to (ISO-8601) mark a fact true only during a time range;
    read the past with ask(at=...). To correct a value later use `correct`, not a
    new status role."""
    return _session.assert_situation(verb, roles, extra, valid_from, valid_to)


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


@mcp.tool()
def correct(situation_id: str, role: str, value: Any,
            valid_from: Optional[str] = None,
            valid_to: Optional[str] = None) -> Dict[str, Any]:
    """Correct or update a role on an existing situation by re-asserting it.
    Append-only: the prior value is kept as history, never overwritten. ask
    returns the latest value; ask(history=true) shows the full trail. Use this
    instead of inventing status/superseded roles. valid_from/valid_to ISO-8601."""
    return _session.correct(situation_id, role, value, valid_from, valid_to)


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
    model's valid-time as of that moment. Results carry ids; `labels` maps each
    id to its readable name once (magnitudes to {value, unit}). Pass labels=false
    to skip it when you only need to chain ids."""
    return _session.ask(fixed, ask, type, at, history, labels)


@mcp.tool()
def find(text: str, axis: Optional[str] = None,
         limit: int = 20) -> Dict[str, Any]:
    """Find entities by name — the way in when you know what something is called
    but not its id. Matches a substring, ignoring case and accents ("azanero"
    finds AZAÑERO). `axis` narrows to one value axis (Q for people, O for things).
    Returns {id, axis, label}; feed those ids to `ask`. `truncated` says there
    were more matches than `limit`."""
    return _session.find(text, axis, limit)


@mcp.tool()
def show_model() -> Dict[str, Any]:
    """Dump the current universe: entity/fact counts and every fact, plus the
    persistence status (log path, replayed/skipped event counts)."""
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
