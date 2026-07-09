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
