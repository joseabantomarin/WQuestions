"""Motor de consulta: las preguntas-WH como proyecciones.

Una consulta es un `Pattern`: un diccionario de roles fijos con valores
conocidos, y al menos un rol marcado como `Var(...)` (la pregunta).
El motor busca todas las situaciones del universo que satisfacen los
roles fijos y proyecta el valor del rol pregunta.

Soporta:
- Consultas puntuales: ¿quién vendió X?
- Consultas temporales: ¿quién era el dueño de X en T0?  (D6)
- Filtros por tipo (instancia_de = K).
- Agregaciones: count, list.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any

from .axes import Axis
from .individual import Individual
from .universe import Universe


@dataclass
class Var:
    """Marcador de variable en un patrón de consulta."""
    name: str = "?"


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


def _en_rango(ind: Individual, rango: "Rango") -> bool:
    valor = _comparable(ind)
    if valor is None:
        return False
    if rango.desde is not None and valor < _coerce(rango.desde, valor):
        return False
    if rango.hasta is not None and valor > _coerce(rango.hasta, valor):
        return False
    return True


@dataclass
class Pattern:
    """Patrón de consulta sobre una situación.

    `fixed`: roles cuyo valor está dado (Individual).
    `ask`:   uno o más roles cuyo valor queremos descubrir (Var).
    """
    fixed: Dict[str, Individual] = field(default_factory=dict)
    ask: Dict[str, Var] = field(default_factory=dict)
    type_constraint: Optional[Individual] = None  # filtra por instancia_de = K

    def __post_init__(self):
        # `ask` vacío es válido: cuenta/lista candidatos sin proyección.
        # En ese caso el binding contiene solo `_subject`.
        pass


def _valores(universe: Universe, hechos: List[Any], role: str,
             vigente_solo: bool) -> List[Individual]:
    """Los valores de un rol: los vigentes, o todo el rastro.

    Con `vigente_solo` se aplica la MISMA regla que usa la proyección: un rol
    no-funcional del catálogo admite varios valores a la vez y todos valen; los
    demás se quedan con el último por `tx_time`. Así filtrar y proyectar dicen
    lo mismo, que hoy no ocurre.
    """
    if not hechos:
        return []
    if not vigente_solo:
        return [f.value for f in hechos]
    sig = universe.catalog.get(role) if universe.catalog is not None else None
    if sig is not None and not sig.functional:
        return [f.value for f in hechos]
    latest = hechos[0]
    for f in hechos[1:]:
        if f.tx_time >= latest.tx_time:
            latest = f
    return [latest.value]


def _casa(valores: List[Individual], esperado: Any) -> bool:
    """¿Alguno de los valores satisface lo esperado? `esperado` es un rango, un
    individuo, o una lista de individuos (cualquiera de ellos sirve)."""
    if isinstance(esperado, Rango):
        return any(_en_rango(v, esperado) for v in valores)
    admitidos = ({e.id for e in esperado} if isinstance(esperado, (list, tuple))
                 else {esperado.id})
    return any(v.id in admitidos for v in valores)


def _anclas(esperado: Any) -> List[Individual]:
    return list(esperado) if isinstance(esperado, (list, tuple)) else [esperado]


def query(universe: Universe, pattern: Pattern,
          at: Optional[datetime] = None,
          vigente_solo: bool = True) -> List[Dict[str, Any]]:
    """Ejecuta el patrón contra el universo. Devuelve una lista de bindings.

    Cada binding es un dict con las claves de `pattern.ask` y los valores
    encontrados (Individual). Las situaciones-candidatas son los sujetos
    que tienen *todos* los roles fijos del patrón (con sus valores) y, si
    aplica, instancia_de = type_constraint.
    """
    # Punto 1: buscar candidatas — sujetos en O que tienen todos los roles
    # del patrón. Tomamos el primer rol fijo (o type_constraint) como ancla
    # para reducir el espacio.

    exactos = {r: v for r, v in pattern.fixed.items()
               if not isinstance(v, Rango)}
    rangos = {r: v for r, v in pattern.fixed.items() if isinstance(v, Rango)}

    if exactos:
        # Ancla: de los roles fijos de valor exacto, el que tiene el VALOR más
        # selectivo. Se indexa por valor, no por rol — preguntar por un cliente
        # concreto recorre los hechos de ese cliente, no todos los que usan ese
        # rol. Vale también con type_constraint: el punto 2 filtra por tipo, y un
        # valor concreto casi siempre discrimina más que un tipo entero.
        role0, val0 = min(
            exactos.items(),
            key=lambda rv: sum(len(universe._by_value.get(v.id, ()))
                               for v in _anclas(rv[1])),
        )
        candidate_subjects = {
            f.subject.id
            for v in _anclas(val0)
            for f in universe.facts_with_value(v, at=at)
            if f.role == role0
        }
    elif pattern.type_constraint is not None:
        # Sujetos cuya instancia_de == type_constraint
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
        # Si solo hay ask, buscamos sobre todas las situaciones (raro).
        candidate_subjects = set(universe.individuals.keys())

    # Punto 2: filtrar candidatas por todos los roles fijos
    results: List[Dict[str, Any]] = []
    for sid in candidate_subjects:
        subject = universe.individuals[sid]
        sit_facts = universe.facts_about(subject, at=at)

        # Map role → hechos de este sujeto (los hechos, no solo los valores:
        # hace falta tx_time para saber cuál es el vigente)
        roles_facts: Dict[str, List[Any]] = {}
        for f in sit_facts:
            roles_facts.setdefault(f.role, []).append(f)

        def vals_de(role: str) -> List[Individual]:
            return _valores(universe, roles_facts.get(role, []), role,
                            vigente_solo)

        roles_map = {r: vals_de(r) for r in roles_facts}

        # Chequear roles fijos
        ok = True
        for role, expected_val in pattern.fixed.items():
            if not _casa(roles_map.get(role, []), expected_val):
                ok = False
                break
        if not ok:
            continue

        # Chequear type_constraint si está
        if pattern.type_constraint is not None:
            instancia_vals = roles_map.get("instancia_de", [])
            if not any(v.id == pattern.type_constraint.id for v in instancia_vals):
                continue

        # Extraer valores para los roles preguntados
        binding: Dict[str, Any] = {"_subject": subject}
        all_present = True
        for ask_role in pattern.ask:
            vals = roles_map.get(ask_role, [])
            if not vals:
                all_present = False
                break
            # Si hay más de uno, devolvemos lista; si uno, el individuo.
            binding[ask_role] = vals[0] if len(vals) == 1 else list(vals)
        if all_present:
            results.append(binding)
    return results


def count(universe: Universe, pattern: Pattern,
          at: Optional[datetime] = None) -> int:
    """Cuenta sujetos que satisfacen el patrón."""
    return len(query(universe, pattern, at=at))
