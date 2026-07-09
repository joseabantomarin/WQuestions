"""WQSession — all MCP tool logic over a per-session wq Universe.

The LLM client does natural-language -> structured roles. This class turns
JSON-friendly arguments into wq engine calls and JSON-friendly results back.
No MCP types here: this module is pure Python and fully unit-tested.
"""
from __future__ import annotations
from datetime import datetime
from typing import Any, Dict, List, Optional

from wq import Catalog, Individual, Lexicon, Universe
from wq import LexiconEntry
from wq import ingest_situation, IngestError
from wq.axes import Axis, is_value_axis

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
            self.universe.add_individual(ind)
        except ValueError as e:
            return {"ok": False, "error": str(e)}
        return {"ok": True,
                "entity": {"id": ind.id, "axis": ind.axis.value, "label": ind.label}}

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

    def _resolve_value(self, spec: Any) -> Individual:
        """A role value is either an existing entity id (str) or an inline
        spec dict {id, axis, label} to create on the fly."""
        if isinstance(spec, dict):
            if "id" not in spec or "axis" not in spec:
                raise ValueError(
                    "Inline entity spec needs 'id' and 'axis' "
                    f"(got keys: {sorted(spec.keys())})"
                )
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
