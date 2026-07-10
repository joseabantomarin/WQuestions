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
from wq import Pattern, Var, query, category
from wq.axes import Axis, is_value_axis

_N_REQUIRES_UNIT_MSG = (
    "N magnitudes require a numeric `value` and a `unit` in K "
    "(e.g. value=25, unit='pen'). Do not encode the unit in the id or "
    "label, and do not assume a unit — ask for it if missing."
)

_AXIS_NAMES = {
    "Q": ("who", "agents"),
    "O": ("what", "objects / reified situations"),
    "L": ("where", "places"),
    "T": ("when", "time points / intervals"),
    "N": ("how-much", "magnitudes with unit"),
    "K": ("which", "atemporal categories / types / states"),
    "M": ("how", "predicates that connect individuals"),
}

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
                {"code": code, "name": name, "description": desc,
                 **_AXIS_GUIDE.get(code, {})}
                for code, (name, desc) in _AXIS_NAMES.items()
            ]
        }

    def list_roles(self) -> Dict[str, Any]:
        # Reads a private attr: the engine exposes no public roles iterator,
        # and it's intentionally left unmodified (see Global Constraints).
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
        return {
            "roles": roles,
            "policy": "Roles are open-world: unknown roles are accepted, not "
                      "validated — invent domain roles freely. Declared roles "
                      "carry a typed signature (domain axis -> range axis) and a "
                      "functional flag (functional=one value per subject).",
            "common": ["agente", "cliente", "tema", "momento", "lugar_de",
                       "por_cuanto", "unidad", "instancia_de", "estatus_factual"],
        }

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
                raise ValueError(_N_REQUIRES_UNIT_MSG)
            return Individual(
                id=entity_id, axis=Axis.N,
                label=label or f"{value} {unit_ind.label or unit_ind.id}",
                payload={"value": value, "unit": unit_ind.id},
            )
        if value is not None or unit_ind is not None:
            raise ValueError(f"`value`/`unit` only apply to axis N, not {axis}.")
        return Individual(id=entity_id, axis=ax, label=label or entity_id)

    def add_entity(self, entity_id: str, axis: str,
                   label: Optional[str] = None,
                   value: Any = None,
                   unit: Any = None) -> Dict[str, Any]:
        try:
            if axis != "N" and (value is not None or unit is not None):
                raise ValueError("`value`/`unit` only apply to axis N.")
            if axis == "N" and value is None:
                raise ValueError(_N_REQUIRES_UNIT_MSG)
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
            if spec.get("axis") == "N" and spec.get("value") is None:
                raise ValueError(_N_REQUIRES_UNIT_MSG)
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

    def ask(self, fixed: Optional[Dict[str, Any]] = None,
            ask: Optional[List[str]] = None,
            type: Optional[str] = None,
            at: Optional[str] = None) -> Dict[str, Any]:
        try:
            fixed_ind = ({r: self._resolve_value(v) for r, v in fixed.items()}
                         if fixed else {})
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
        except (ValueError, IngestError) as e:
            return {"ok": False, "error": str(e)}
        return {"count": len(results), "results": results}

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
            "legend": "Facts are binary triplets (subject · role · value), the "
                      "projection of reified situations. The store is append-only: "
                      "corrections add facts, they never overwrite.",
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
