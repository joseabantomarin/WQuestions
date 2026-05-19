"""Hechos atómicos: la unidad mínima del modelo.

Cada hecho es una tupla `(sujeto, rol, valor)` donde:
- `sujeto` y `valor` son `Individual` (viven en algún eje de valor).
- `rol` es una etiqueta del catálogo canónico (D8) o de su capa lexicon.

D6 — vigencia temporal: cada hecho lleva opcionalmente un rango
`[valid_from, valid_to)` que indica desde cuándo y hasta cuándo es cierto en
el mundo. Si `valid_to is None`, está abierto al futuro.

Adicionalmente registramos `tx_time` (transaction time): el momento en el que
el hecho entró al sistema. Esto da bitemporalidad ligera, suficiente para
auditoría.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from .individual import Individual


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class Fact:
    subject: Individual
    role: str
    value: Individual
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    tx_time: datetime = field(default_factory=_utcnow)

    def is_valid_at(self, moment: datetime) -> bool:
        """¿Este hecho es cierto en el mundo en `moment`?

        Reglas:
        - Si no hay vigencia, el hecho es atemporal: vale siempre.
        - `valid_from` inclusivo, `valid_to` exclusivo.
        - `valid_to is None` significa "abierto al futuro".
        """
        if self.valid_from is None and self.valid_to is None:
            return True
        if self.valid_from is not None and moment < self.valid_from:
            return False
        if self.valid_to is not None and moment >= self.valid_to:
            return False
        return True

    def __repr__(self) -> str:
        s = self.subject.label or self.subject.id
        v = self.value.label or self.value.id
        base = f"({s}, {self.role}, {v})"
        if self.valid_from or self.valid_to:
            f = self.valid_from.isoformat() if self.valid_from else "-∞"
            t = self.valid_to.isoformat() if self.valid_to else "+∞"
            base += f"  [{f} .. {t})"
        return base
