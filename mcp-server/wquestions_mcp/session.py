"""WQSession — all MCP tool logic over a per-session wq Universe.

The LLM client does natural-language -> structured roles. This class turns
JSON-friendly arguments into wq engine calls and JSON-friendly results back.
No MCP types here: this module is pure Python and fully unit-tested.
"""
from __future__ import annotations
import json
import os
import unicodedata
from datetime import datetime
from typing import Any, Dict, List, Optional

from wq import Catalog, Individual, Lexicon, Universe
from wq import LexiconEntry
from wq import ingest_situation, IngestError
from wq import Pattern, Var, Rango, query, category
from wq.axes import Axis, is_value_axis
from wq.magnitud import Magnitud, ErrorDimensional

DEFAULT_LOG_PATH = "~/.wquestions/universe.jsonl"


def resolve_log_path(raw: Optional[str]) -> Optional[str]:
    """Resolve the persistence log path. None (env unset) -> default file;
    off/none/:memory:/empty (case-insensitive, whitespace-only counts as empty)
    -> None (pure in-memory); else the expanded path."""
    if raw is None:
        raw = DEFAULT_LOG_PATH
    if raw.strip().lower() in ("", "off", "none", ":memory:"):
        return None
    return os.path.expanduser(raw)

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


# El rol con que una entidad declara su propio nombre. `labels` y `find` leen de
# aquí antes que del label, para que el nombre sea un hecho y no un adorno del
# individuo.
NAME_ROLE = "nombre"


def _norm(text: str) -> str:
    """Texto comparable: sin acentos y en mayúsculas. Sin esto, `azañero` no
    encuentra a AZAÑERO y media agenda peruana queda inalcanzable."""
    plain = unicodedata.normalize("NFD", text or "")
    return "".join(c for c in plain if unicodedata.category(c) != "Mn").upper()


class WQSession:
    def __init__(self, log_path: Optional[str] = None) -> None:
        self._log_path = log_path
        self._suppress_log = False
        self._sit_seq = 1
        self._replayed_events = 0
        self._skipped_lines = 0
        self._name_idx: Optional[Dict[str, List[str]]] = None
        self._fresh()
        if self._log_path and os.path.exists(self._log_path):
            self._replay()

    def _fresh(self) -> None:
        self.catalog = Catalog()
        self.universe = Universe(name="session", catalog=self.catalog)
        self.lexicon = Lexicon()
        self._sit_seq = 1
        self._name_idx = None

    def reset(self) -> Dict[str, Any]:
        self._fresh()
        self._append_event("reset", {})
        return {"ok": True}

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
            "assert_fact": self.assert_fact,
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

    def _invalidate_name_index(self) -> None:
        self._name_idx = None

    def _display(self, entity_id: str) -> Any:
        """Cómo se llama esta entidad, para mostrarla o para buscarla.

        Orden: un hecho con rol `nombre` > el label del individuo > nada. Una
        magnitud se resuelve a {value, unit}. Devuelve None cuando el individuo
        no aporta nombre propio (label ausente o igual al id), que es el caso de
        los nodos de situación: no vale la pena gastar tokens en repetir un
        identificador que ya está en la fila.
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
        self._append_event("add_entity", {"entity_id": entity_id, "axis": axis,
                                           "label": label, "value": value,
                                           "unit": unit})
        self._invalidate_name_index()
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
        self._append_event("define_verb", {"verb": verb,
                                            "situation_type": situation_type,
                                            "obligatory": obligatory,
                                            "optional": optional})
        return {"ok": True, "verb": verb}

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
        self._invalidate_name_index()
        return {"ok": True,
                "fact": {"subject": subj.id, "role": role, "value": val.id}}

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
        self._invalidate_name_index()
        self._append_event("assert_situation",
                           {"verb": verb, "roles": roles, "extra": extra,
                            "valid_from": valid_from, "valid_to": valid_to,
                            "_sit_id": situ.id})
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
                    "error": f"Unknown entity '{situation_id}'. Pass a "
                             f"situation_id from assert_situation, or any "
                             f"existing entity id."}
        try:
            val = self._resolve_value(value)
            self.universe.assert_fact(
                situ, role, val,
                valid_from=self._parse_ts(valid_from),
                valid_to=self._parse_ts(valid_to),
            )
        except (ValueError, IngestError) as e:
            return {"ok": False, "error": str(e)}
        self._invalidate_name_index()
        self._append_event("correct", {"situation_id": situation_id, "role": role,
                                        "value": value, "valid_from": valid_from,
                                        "valid_to": valid_to})
        return {"ok": True, "situation_id": situ.id, "role": role, "value": val.id,
                "note": "Appended, not overwritten. ask returns this (latest) "
                        "value; ask(history=true) shows prior ones."}

    def _sumar(self, valores: List[Individual]) -> Dict[str, Any]:
        """Suma magnitudes respetando la unidad. Sumar soles con kilos da error,
        no un número: la regla del eje N aplicada a la consulta."""
        magnitudes = [v for v in valores if isinstance(v.payload, dict)
                      and "value" in v.payload]
        if not magnitudes:
            raise ValueError("`sum` needs magnitudes with a numeric value.")
        unidades = {v.payload.get("unit") for v in magnitudes}
        if len(unidades) == 1:
            uid = unidades.pop()
            ind = self.universe.individuals.get(uid)
            return {"value": sum(float(v.payload["value"]) for v in magnitudes),
                    "unit": (ind.label or uid) if ind else uid}
        destino = magnitudes[0].payload["unit"]
        total = Magnitud.de(self.universe, magnitudes[0])
        for v in magnitudes[1:]:
            total = total.mas(Magnitud.de(self.universe, v))
        conv = total.convertir_a(self.universe, destino)
        ind = self.universe.individuals.get(destino)
        return {"value": conv.valor,
                "unit": (ind.label or destino) if ind else destino}

    def _medida(self, spec: Any, valores: List[Any]) -> Any:
        if spec == "count":
            return len(valores)
        if not isinstance(spec, dict) or len(spec) != 1:
            raise ValueError(
                f"Bad measure {spec!r}. Use \"count\" or "
                f"{{\"sum\"|\"min\"|\"max\"|\"avg\": \"<role>\"}}.")
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

    def _agregar(self, bindings, agrupar_por, medir, orden, limite, at):
        """Agrupa las situaciones candidatas y calcula las medidas pedidas."""
        grupos: Dict[Any, Dict[str, List[Any]]] = {}
        for b in bindings:
            roles: Dict[str, List[Individual]] = {}
            for f in self.universe.facts_about(b["_subject"], at=at):
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
        try:
            fixed_ind: Dict[str, Any] = {}
            for role, spec in (fixed or {}).items():
                if isinstance(spec, dict) and ("desde" in spec or "hasta" in spec):
                    fixed_ind[role] = Rango(desde=spec.get("desde"),
                                            hasta=spec.get("hasta"))
                    sig = self.catalog.get(role)
                    if sig is not None and sig.range.value not in ("T", "N"):
                        raise ValueError(
                            f"Role '{role}' ranges over {sig.range.value}; only "
                            f"T and N are ordered. Pass an exact value instead.")
                elif isinstance(spec, (list, tuple)):
                    fixed_ind[role] = [self._resolve_value(v) for v in spec]
                else:
                    fixed_ind[role] = self._resolve_value(spec)
            at_dt = self._parse_ts(at)
            pattern = Pattern(
                fixed=fixed_ind,
                ask={role: Var(role) for role in (ask or [])},
                type_constraint=category(type) if type else None,
            )
            # `history` gobierna las DOS mitades: filtrar por todo el
            # rastro y proyectarlo. Por defecto, solo lo vigente.
            bindings = query(self.universe, pattern, at=at_dt,
                             vigente_solo=not history)
            if medir is not None:
                if ask:
                    raise ValueError(
                        "Use either `ask` (project rows) or `medir` (aggregate "
                        "groups), not both.")
                results = self._agregar(bindings, agrupar_por, medir,
                                        orden, limite, at_dt)
                out: Dict[str, Any] = {"count": len(results),
                                       "results": results}
                if labels:
                    out["labels"] = self._labels_for(results)
                return out
            results = []
            for b in bindings:
                subj = b["_subject"]
                row: Dict[str, Any] = {"_subject": subj.id}
                subj_facts = self.universe.facts_about(subj, at=at_dt)
                for role in (ask or []):
                    role_facts = [f for f in subj_facts if f.role == role]
                    row[role] = self._project_role(role, role_facts, history)
                results.append(row)
        except (ValueError, IngestError, ErrorDimensional) as e:
            return {"ok": False, "error": str(e)}
        out = {"count": len(results), "results": results}
        if labels:
            out["labels"] = self._labels_for(results)
        return out

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
        # role_facts is non-empty here: query() only yields subjects that have the asked role
        latest = role_facts[0]
        for f in role_facts[1:]:
            if f.tx_time >= latest.tx_time:  # >= so later insertion wins ties
                latest = f
        return latest.value.id

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
        """Busca entidades por su nombre: subcadena, sin distinguir mayúsculas
        ni acentos. Es la puerta de entrada — sin esto hay que conocer los
        identificadores de antemano."""
        needle = _norm(text).strip()
        if not needle:
            return {"ok": False, "error": "Pass some text to search for."}
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

    def identidades(self, entity_id: str) -> Dict[str, Any]:
        """Todos los identificadores que son la MISMA cosa, siguiendo `mismo_que`
        en los dos sentidos y de forma transitiva.

        Una persona puede estar registrada con su DNI y con su RUC sin que
        ninguno de los dos sea un error: son dos identidades legítimas. Enlazarlas
        con `mismo_que` conserva cada hecho como se registró —y por tanto
        consultable por el identificador con que ocurrió— y deja que la pregunta
        por la persona los recorra todos.
        """
        if entity_id not in self.universe.individuals:
            return {"ok": False, "error": f"Unknown entity '{entity_id}'."}
        vistos, pend = set(), [entity_id]
        while pend:
            eid = pend.pop()
            if eid in vistos:
                continue
            vistos.add(eid)
            ind = self.universe.individuals.get(eid)
            if ind is None:
                continue
            for f in self.universe.facts_about(ind):
                if f.role == "mismo_que":
                    pend.append(f.value.id)
            for f in self.universe.facts_with_value(ind):
                if f.role == "mismo_que":
                    pend.append(f.subject.id)
        ids = sorted(vistos)
        return {"count": len(ids), "ids": ids,
                "labels": {i: self._display(i) for i in ids
                           if self._display(i) is not None}}

    def show_model(self) -> Dict[str, Any]:
        facts = [
            {"subject": f.subject.id, "role": f.role, "value": f.value.id}
            for f in self.universe.facts
        ]
        persistence = (
            {"path": self._log_path,
             "replayed_events": self._replayed_events,
             "skipped_lines": self._skipped_lines}
            if self._log_path else {"enabled": False}
        )
        return {
            "summary": self.universe.summary(),
            "entity_count": len(self.universe.individuals),
            "fact_count": len(self.universe.facts),
            "facts": facts,
            "legend": "Facts are binary triplets (subject · role · value), the "
                      "projection of reified situations. The store is append-only: "
                      "corrections add facts, they never overwrite.",
            "persistence": persistence,
        }

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
