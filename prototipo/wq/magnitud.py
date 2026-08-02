"""Aritmética dimensional sobre las magnitudes del eje N.

La regla del eje N (capítulo 4) dice que un número nunca viaja sin su unidad.
Este módulo es la consecuencia operativa: si las magnitudes llevan unidad,
operar con ellas exige respetarla. Multiplicar sin mirar unidades produce
hechos numéricamente correctos y dimensionalmente falsos, que es peor que no
calcular.

La física de las unidades NO vive aquí: vive en el grafo, como tripletas
colgando de las categorías de K. Este módulo solo la lee y la aplica.

    (K:ToneladaMetrica,  unidad_base,   K:Gramo)
    (K:ToneladaMetrica,  factor_a_base, 1e6)
    (K:GramoPorTonelada, numerador,     K:Gramo)
    (K:GramoPorTonelada, denominador,   K:ToneladaMetrica)

De ahí se deduce que t × (g/t) da gramos, sin que nadie lo programe. Y que
sumar toneladas con onzas falla, en vez de dar un número.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

from .axes import Axis
from .individual import Individual

# Roles con que una categoría de K describe su propia física.
ROL_UNIDAD_BASE = "unidad_base"
ROL_FACTOR = "factor_a_base"
ROL_NUMERADOR = "numerador"
ROL_DENOMINADOR = "denominador"
ROL_ANCLA = "ancla_qudt"


class ErrorDimensional(Exception):
    """Se intentó una operación que las unidades no permiten."""


# ---------------------------------------------------------------------------
# La unidad, reducida
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class UnidadReducida:
    """Una unidad expresada en unidades base.

    `exponentes` mapea el id de cada unidad base a su exponente; `factor` es
    cuánto vale una de esta unidad medida en las base. La onza troy es
    {K:Gramo: 1} con factor 31.1034768. El gramo por tonelada es {} con factor
    1e-6, porque masa entre masa se cancela y queda un adimensional.
    """

    exponentes: Dict[str, int]
    factor: float

    def es_adimensional(self) -> bool:
        return not self.exponentes

    def __str__(self) -> str:
        if not self.exponentes:
            return "adimensional"
        partes = []
        for base, exp in sorted(self.exponentes.items()):
            partes.append(base if exp == 1 else f"{base}^{exp}")
        return "·".join(partes)


def _limpiar(exponentes: Dict[str, int]) -> Dict[str, int]:
    """Quita los exponentes que se anularon."""
    return {k: v for k, v in exponentes.items() if v != 0}


def reducir_unidad(universe, unidad_id: str,
                   _visitadas: Optional[frozenset] = None) -> UnidadReducida:
    """Reduce una unidad de K a exponentes sobre unidades base y un factor.

    Tres casos:
      - Compuesta: declara `numerador` y `denominador`. Se reducen ambos y se
        restan los exponentes.
      - Derivada: declara `unidad_base` y `factor_a_base`.
      - Base: no declara nada. Es su propia unidad, con factor 1.
    """
    _visitadas = _visitadas or frozenset()
    if unidad_id in _visitadas:
        raise ErrorDimensional(
            f"La unidad '{unidad_id}' se define a sí misma en círculo."
        )
    _visitadas = _visitadas | {unidad_id}

    try:
        unidad = universe.ind(unidad_id)
    except KeyError:
        raise ErrorDimensional(
            f"La unidad '{unidad_id}' no existe en el universo. "
            f"Decláralas antes de operar con magnitudes."
        )
    if unidad.axis is not Axis.K:
        raise ErrorDimensional(
            f"'{unidad_id}' está en {unidad.axis.value}; las unidades viven en K."
        )

    hechos = {f.role: f.value for f in universe.facts_about(unidad)}

    # -- unidad compuesta: una razón entre dos magnitudes ------------------
    if ROL_NUMERADOR in hechos and ROL_DENOMINADOR in hechos:
        num = reducir_unidad(universe, hechos[ROL_NUMERADOR].id, _visitadas)
        den = reducir_unidad(universe, hechos[ROL_DENOMINADOR].id, _visitadas)
        exps = dict(num.exponentes)
        for base, exp in den.exponentes.items():
            exps[base] = exps.get(base, 0) - exp
        return UnidadReducida(_limpiar(exps), num.factor / den.factor)

    # -- unidad derivada de otra por un factor -----------------------------
    if ROL_UNIDAD_BASE in hechos:
        if ROL_FACTOR not in hechos:
            raise ErrorDimensional(
                f"'{unidad_id}' declara unidad_base pero no factor_a_base."
            )
        base = reducir_unidad(universe, hechos[ROL_UNIDAD_BASE].id, _visitadas)
        factor = _numero(hechos[ROL_FACTOR], unidad_id)
        return UnidadReducida(dict(base.exponentes), base.factor * factor)

    # -- adimensional con escala: el porcentaje y sus parientes ------------
    # Un factor sin unidad_base declara una unidad que no mide nada, solo
    # escala: K:Porcentaje es 0.01 y K:Adimensional es 1.
    if ROL_FACTOR in hechos:
        return UnidadReducida({}, _numero(hechos[ROL_FACTOR], unidad_id))

    # -- unidad base: se representa a sí misma -----------------------------
    return UnidadReducida({unidad_id: 1}, 1.0)


def _numero(ind: Individual, contexto: str) -> float:
    """Extrae el valor de una magnitud N."""
    if ind.axis is not Axis.N or not isinstance(ind.payload, dict):
        raise ErrorDimensional(
            f"El factor de '{contexto}' debe ser una magnitud N, y es {ind.id}."
        )
    return float(ind.payload["value"])


# ---------------------------------------------------------------------------
# La magnitud, operable
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Magnitud:
    """Un valor con su unidad, capaz de operar sin perderla."""

    valor: float
    unidad_id: Optional[str]      # None = adimensional puro
    _reducida: UnidadReducida

    # -- construcción ------------------------------------------------------

    @staticmethod
    def de(universe, ind: Individual) -> "Magnitud":
        """Construye una magnitud a partir de un individuo del eje N."""
        if ind.axis is not Axis.N:
            raise ErrorDimensional(
                f"'{ind.id}' no está en N; no es una magnitud."
            )
        if not isinstance(ind.payload, dict) or "value" not in ind.payload:
            raise ErrorDimensional(
                f"La magnitud '{ind.id}' no lleva valor en su payload."
            )
        unidad_id = ind.payload.get("unit")
        if unidad_id is None:
            raise ErrorDimensional(
                f"La magnitud '{ind.id}' viaja sin unidad. "
                f"Un número sin unidad no es información (regla del eje N)."
            )
        return Magnitud(float(ind.payload["value"]), unidad_id,
                        reducir_unidad(universe, unidad_id))

    @property
    def valor_base(self) -> float:
        """El valor expresado en unidades base."""
        return self.valor * self._reducida.factor

    @property
    def dimension(self) -> str:
        return str(self._reducida)

    # -- operaciones -------------------------------------------------------

    def por(self, otra: "Magnitud") -> "Magnitud":
        exps = dict(self._reducida.exponentes)
        for base, exp in otra._reducida.exponentes.items():
            exps[base] = exps.get(base, 0) + exp
        return Magnitud(self.valor_base * otra.valor_base, None,
                        UnidadReducida(_limpiar(exps), 1.0))

    def entre(self, otra: "Magnitud") -> "Magnitud":
        if otra.valor_base == 0:
            raise ErrorDimensional("División por una magnitud nula.")
        exps = dict(self._reducida.exponentes)
        for base, exp in otra._reducida.exponentes.items():
            exps[base] = exps.get(base, 0) - exp
        return Magnitud(self.valor_base / otra.valor_base, None,
                        UnidadReducida(_limpiar(exps), 1.0))

    def mas(self, otra: "Magnitud") -> "Magnitud":
        self._exigir_conmensurable(otra, "sumar")
        return Magnitud(self.valor_base + otra.valor_base, None,
                        UnidadReducida(dict(self._reducida.exponentes), 1.0))

    def menos(self, otra: "Magnitud") -> "Magnitud":
        self._exigir_conmensurable(otra, "restar")
        return Magnitud(self.valor_base - otra.valor_base, None,
                        UnidadReducida(dict(self._reducida.exponentes), 1.0))

    def _exigir_conmensurable(self, otra: "Magnitud", verbo: str) -> None:
        if self._reducida.exponentes != otra._reducida.exponentes:
            raise ErrorDimensional(
                f"No se puede {verbo} {self.dimension} con {otra.dimension}: "
                f"no son conmensurables."
            )

    def convertir_a(self, universe, unidad_destino: str) -> "Magnitud":
        """Reexpresa la magnitud en otra unidad de la misma dimensión."""
        destino = reducir_unidad(universe, unidad_destino)
        if destino.exponentes != self._reducida.exponentes:
            raise ErrorDimensional(
                f"No se puede expresar {self.dimension} en "
                f"'{unidad_destino}' ({destino}): dimensiones distintas."
            )
        return Magnitud(self.valor_base / destino.factor, unidad_destino, destino)

    def __repr__(self) -> str:
        u = self.unidad_id or self.dimension
        return f"Magnitud({self.valor:g} {u})"
