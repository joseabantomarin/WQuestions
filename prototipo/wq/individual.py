"""Individuos del modelo: instancias de cualquier eje de valor.

Cada individuo tiene un identificador estable y vive en uno y solo un eje.
Para sujetos sintéticos usamos un mint determinista (id corto, monótono)
en vez de UUID — la observabilidad gana, la pérdida de globalidad no
importa para un prototipo.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Any, Dict
from itertools import count

from .axes import Axis, is_value_axis


_counter = count(1)


def mint_id(prefix: str = "id") -> str:
    """Genera un id corto y monótono. En producción se reemplazaría por UUID v7."""
    n = next(_counter)
    return f"{prefix}_{n:06d}"


@dataclass(frozen=True)
class Individual:
    """Individuo en un eje de valor.

    `payload` permite alojar valores nativos cuando el "individuo" es en
    realidad un dato (un instante T, una magnitud N, una categoría K). Para
    Q y O suele ser None; el id basta.
    """

    id: str
    axis: Axis
    label: Optional[str] = None
    payload: Any = None
    meta: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not is_value_axis(self.axis):
            raise ValueError(
                f"Un individuo debe vivir en un eje de valor, no en {self.axis}."
            )

    def __repr__(self) -> str:
        tag = self.label or self.id
        return f"<{self.axis.value}:{tag}>"


# --- helpers para individuos "primitivos" -----------------------------------


def time_point(iso: str) -> Individual:
    """Crea un individuo T desde una marca ISO 8601."""
    from datetime import datetime
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    except ValueError as e:
        raise ValueError(f"Marca temporal inválida: {iso}") from e
    return Individual(id=f"t_{iso}", axis=Axis.T, label=iso, payload=dt)


def quantity(value: float, unit_k: "Individual") -> Individual:
    """Crea un individuo N con valor numérico y unidad anclada en K."""
    if unit_k.axis != Axis.K:
        raise ValueError(
            f"La unidad debe vivir en K (recibido: {unit_k.axis})."
        )
    return Individual(
        id=mint_id("n"),
        axis=Axis.N,
        label=f"{value} {unit_k.label or unit_k.id}",
        payload={"value": value, "unit": unit_k.id},
    )


def category(label: str) -> Individual:
    """Crea un individuo K (categoría) con id derivado del label."""
    return Individual(id=label, axis=Axis.K, label=label)
