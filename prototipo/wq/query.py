"""Motor de consulta: las preguntas-WH como proyecciones.

Una consulta es un `Pattern`: un diccionario de roles fijos con valores
conocidos, y al menos un rol marcado como `Var(...)` (la pregunta).
El motor busca todas las situaciones del universo que satisfacen los
roles fijos y proyecta el valor del rol pregunta.

Soporta:
- Consultas puntuales: ¿quién vendió X?
- Consultas temporales: ¿quién era el dueño de X en T0?  (D9)
- Filtros por tipo (instancia_de = K).
- Agregaciones: count, list.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any

from .individual import Individual
from .universe import Universe


@dataclass
class Var:
    """Marcador de variable en un patrón de consulta."""
    name: str = "?"


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


def query(universe: Universe, pattern: Pattern,
          at: Optional[datetime] = None) -> List[Dict[str, Any]]:
    """Ejecuta el patrón contra el universo. Devuelve una lista de bindings.

    Cada binding es un dict con las claves de `pattern.ask` y los valores
    encontrados (Individual). Las situaciones-candidatas son los sujetos
    que tienen *todos* los roles fijos del patrón (con sus valores) y, si
    aplica, instancia_de = type_constraint.
    """
    # Punto 1: buscar candidatas — sujetos en O que tienen todos los roles
    # del patrón. Tomamos el primer rol fijo (o type_constraint) como ancla
    # para reducir el espacio.

    if pattern.type_constraint is not None:
        # Sujetos cuya instancia_de == type_constraint
        candidate_subjects = {
            f.subject.id
            for f in universe.facts_with_role("instancia_de", at=at)
            if f.value.id == pattern.type_constraint.id
        }
    elif pattern.fixed:
        # Tomamos el primer fixed como ancla.
        role0, val0 = next(iter(pattern.fixed.items()))
        candidate_subjects = {
            f.subject.id
            for f in universe.facts_with_role(role0, at=at)
            if f.value.id == val0.id
        }
    else:
        # Si solo hay ask, buscamos sobre todas las situaciones (raro).
        candidate_subjects = set(universe.individuals.keys())

    # Punto 2: filtrar candidatas por todos los roles fijos
    results: List[Dict[str, Any]] = []
    for sid in candidate_subjects:
        subject = universe.individuals[sid]
        sit_facts = universe.facts_about(subject, at=at)

        # Map role → list of values for this subject
        roles_map: Dict[str, List[Individual]] = {}
        for f in sit_facts:
            roles_map.setdefault(f.role, []).append(f.value)

        # Chequear roles fijos
        ok = True
        for role, expected_val in pattern.fixed.items():
            vals = roles_map.get(role, [])
            if not any(v.id == expected_val.id for v in vals):
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
