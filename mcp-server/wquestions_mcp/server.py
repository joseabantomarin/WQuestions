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
    valid_from/valid_to are ISO-8601, for facts that are only valid during
    a time range."""
    return _session.assert_situation(verb, roles, extra, valid_from, valid_to)


@mcp.tool()
def ask(fixed: Optional[Dict[str, Any]] = None,
        ask: Optional[List[str]] = None,
        type: Optional[str] = None,
        at: Optional[str] = None) -> Dict[str, Any]:
    """Query by projection: fix some roles, ask for others. `type` filters to
    situations whose type matches the given category id (auto-registered
    verbs get the id `action_<verb>`). `at` (ISO) queries the model as it
    was valid at that time."""
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
