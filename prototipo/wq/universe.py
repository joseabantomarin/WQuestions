"""El universo V — unión disjunta de los ejes de valor.

`Universe` es el almacenamiento en memoria del prototipo: una lista de
individuos y una lista de hechos, con índices para consulta eficiente.

Diseño:
- Se accede vía `add_individual`, `assert_fact`, `query`.
- La validación de signatura ocurre al insertar el hecho (delegada al Catalog).
- Los hechos son inmutables; "cambios" se modelan como nuevas situaciones
  o como rangos de vigencia (D6).

No persiste a disco — el prototipo es en memoria. Para tests y demos basta.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Iterator, Tuple, Any

from .axes import Axis
from .individual import Individual
from .fact import Fact


@dataclass
class Universe:
    name: str = "default"
    individuals: Dict[str, Individual] = field(default_factory=dict)
    facts: List[Fact] = field(default_factory=list)
    catalog: Any = None  # Catalog inyectado opcionalmente para validación

    # Índices
    _by_subject: Dict[str, List[int]] = field(default_factory=dict)
    _by_value: Dict[str, List[int]] = field(default_factory=dict)
    _by_role: Dict[str, List[int]] = field(default_factory=dict)

    # --- registro de individuos --------------------------------------------

    def add_individual(self, ind: Individual) -> Individual:
        existing = self.individuals.get(ind.id)
        if existing is not None:
            if existing.axis != ind.axis:
                raise ValueError(
                    f"Conflicto de eje para {ind.id}: ya existe en {existing.axis} "
                    f"y se intenta registrar en {ind.axis}."
                )
            return existing
        self.individuals[ind.id] = ind
        return ind

    def ind(self, id_or_label: str) -> Individual:
        """Recupera un individuo por id."""
        if id_or_label in self.individuals:
            return self.individuals[id_or_label]
        raise KeyError(f"Individuo no registrado: {id_or_label}")

    # --- afirmación de hechos ----------------------------------------------

    def assert_fact(
        self,
        subject: Individual,
        role: str,
        value: Individual,
        valid_from: Optional[datetime] = None,
        valid_to: Optional[datetime] = None,
    ) -> Fact:
        """Afirma un hecho atómico. Valida la signatura si hay catálogo."""
        self.add_individual(subject)
        self.add_individual(value)

        if self.catalog is not None:
            self.catalog.validate(role, subject, value)

        fact = Fact(
            subject=subject,
            role=role,
            value=value,
            valid_from=valid_from,
            valid_to=valid_to,
        )
        idx = len(self.facts)
        self.facts.append(fact)
        self._by_subject.setdefault(subject.id, []).append(idx)
        self._by_value.setdefault(value.id, []).append(idx)
        self._by_role.setdefault(role, []).append(idx)
        return fact

    # --- recuperación ------------------------------------------------------

    def facts_about(self, individual: Individual,
                    at: Optional[datetime] = None) -> List[Fact]:
        """Todos los hechos donde `individual` es el sujeto."""
        idxs = self._by_subject.get(individual.id, [])
        result = [self.facts[i] for i in idxs]
        if at is not None:
            result = [f for f in result if f.is_valid_at(at)]
        return result

    def facts_with_role(self, role: str,
                        at: Optional[datetime] = None) -> List[Fact]:
        idxs = self._by_role.get(role, [])
        result = [self.facts[i] for i in idxs]
        if at is not None:
            result = [f for f in result if f.is_valid_at(at)]
        return result

    def facts_with_value(self, individual: Individual,
                         at: Optional[datetime] = None) -> List[Fact]:
        idxs = self._by_value.get(individual.id, [])
        result = [self.facts[i] for i in idxs]
        if at is not None:
            result = [f for f in result if f.is_valid_at(at)]
        return result

    # --- utilidades --------------------------------------------------------

    def __len__(self) -> int:
        return len(self.facts)

    def summary(self) -> str:
        n_by_axis: Dict[Axis, int] = {}
        for ind in self.individuals.values():
            n_by_axis[ind.axis] = n_by_axis.get(ind.axis, 0) + 1
        parts = [f"Universe '{self.name}'",
                 f"  individuos: {len(self.individuals)}"]
        for ax in Axis:
            if ax in n_by_axis:
                parts.append(f"    {ax.value}: {n_by_axis[ax]}")
        parts.append(f"  hechos:     {len(self.facts)}")
        return "\n".join(parts)
