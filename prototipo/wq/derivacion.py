"""Derivación: calcular un hecho a partir de otros, y dejar dicho de dónde sale.

Es la primera rebanada del motor de inferencia (Frente 1). No evalúa
condiciones ni dispara reglas con antecedente: calcula una magnitud a partir de
otras magnitudes de la misma situación, respetando las unidades, y escribe el
resultado con sus cables de procedencia puestos.

La regla es una entidad del grafo, no código:

    (regla_oro_fino, instancia_de,   regla_de_derivacion)
    (regla_oro_fino, expresion,      "monto * ley_mineral")
    (regla_oro_fino, unidad_destino, K:OnzaTroy)

Y lo que la derivación escribe lleva su origen encima:

    (prod_oro_extr_001, monto,           685.7 K:OnzaTroy)
    (prod_oro_extr_001, calculado_de,    extr_001)
    (prod_oro_extr_001, justificado_por, regla_oro_fino)
"""

from __future__ import annotations

import re
from typing import Optional

from .axes import Axis
from .individual import Individual
from .magnitud import ErrorDimensional, Magnitud, reducir_unidad

ROL_EXPRESION = "expresion"
ROL_UNIDAD_DESTINO = "unidad_destino"
ROL_CALCULADO_DE = "calculado_de"
ROL_JUSTIFICADO_POR = "justificado_por"

_TOKEN = re.compile(r"\s*([*/])\s*")


class ErrorDerivacion(Exception):
    """La regla no se pudo aplicar a la situación."""


# ---------------------------------------------------------------------------
# Declarar unidades: la física de las unidades, como tripletas
# ---------------------------------------------------------------------------

def declarar_unidad(universe, unidad_id: str, *,
                    label: Optional[str] = None,
                    base: Optional[str] = None,
                    factor: Optional[float] = None,
                    numerador: Optional[str] = None,
                    denominador: Optional[str] = None,
                    qudt: Optional[str] = None) -> Individual:
    """Crea una unidad en K y le cuelga su física.

    Cuatro formas, según lo que se pase:
      - base + factor        → derivada (tonelada = 1e6 gramos)
      - numerador + denominador → compuesta (g/t)
      - factor solo          → adimensional con escala (porcentaje = 0.01)
      - nada                 → unidad base (gramo)
    """
    unidad = universe.add_individual(
        Individual(id=unidad_id, axis=Axis.K, label=label or unidad_id))

    if qudt is not None:
        universe.add_individual(Individual(id=qudt, axis=Axis.K, label=qudt))
        universe.assert_fact(unidad, "ancla_qudt", universe.ind(qudt))

    if numerador is not None or denominador is not None:
        if numerador is None or denominador is None:
            raise ErrorDimensional(
                f"'{unidad_id}' necesita numerador y denominador, no uno solo.")
        universe.assert_fact(unidad, "numerador", universe.ind(numerador))
        universe.assert_fact(unidad, "denominador", universe.ind(denominador))
        return unidad

    if base is not None:
        if factor is None:
            raise ErrorDimensional(
                f"'{unidad_id}' declara una unidad base pero no su factor.")
        universe.assert_fact(unidad, "unidad_base", universe.ind(base))

    if factor is not None:
        universe.assert_fact(unidad, "factor_a_base",
                             _factor_individual(universe, unidad_id, factor))

    return unidad


def _factor_individual(universe, unidad_id: str, factor: float) -> Individual:
    """El factor es una magnitud adimensional, como cualquier otra magnitud."""
    return Individual(
        id=f"n_factor_{unidad_id.replace(':', '_')}",
        axis=Axis.N,
        label=f"{factor:g}",
        payload={"value": float(factor), "unit": "K:Adimensional"},
    )


def declarar_unidades_base(universe) -> None:
    """La unidad adimensional, que todo factor necesita para no viajar sola."""
    universe.add_individual(
        Individual(id="K:Adimensional", axis=Axis.K, label="adimensional"))


# ---------------------------------------------------------------------------
# Evaluar la expresión de una regla
# ---------------------------------------------------------------------------

def _magnitud_del_rol(universe, situacion: Individual, rol: str) -> Magnitud:
    valores = [f.value for f in universe.facts_about(situacion)
               if f.role == rol]
    if not valores:
        raise ErrorDerivacion(
            f"La situación '{situacion.id}' no tiene el rol '{rol}' que la "
            f"regla necesita."
        )
    return Magnitud.de(universe, valores[-1])


def evaluar(universe, expresion: str, situacion: Individual) -> Magnitud:
    """Evalúa una expresión de roles, de izquierda a derecha.

    Solo producto y cociente, sin paréntesis y sin constantes: si hace falta un
    número, se declara como magnitud y se referencia por su rol. La restricción
    es deliberada, para que la regla siga siendo legible dentro del grafo.
    """
    piezas = [p for p in _TOKEN.split(expresion.strip()) if p]
    if not piezas:
        raise ErrorDerivacion("La regla no trae expresión que evaluar.")

    acumulado = _magnitud_del_rol(universe, situacion, piezas[0])
    i = 1
    while i < len(piezas):
        operador, rol = piezas[i], piezas[i + 1] if i + 1 < len(piezas) else None
        if rol is None:
            raise ErrorDerivacion(
                f"La expresión '{expresion}' termina en un operador suelto.")
        siguiente = _magnitud_del_rol(universe, situacion, rol)
        acumulado = (acumulado.por(siguiente) if operador == "*"
                     else acumulado.entre(siguiente))
        i += 2
    return acumulado


# ---------------------------------------------------------------------------
# Derivar
# ---------------------------------------------------------------------------

def derivar(universe, regla: Individual, sobre: Individual,
            destino_id: str, rol_destino: str = "monto",
            label: Optional[str] = None) -> Individual:
    """Aplica una regla a una situación y escribe el hecho derivado.

    Devuelve la entidad creada, que lleva el valor calculado y los dos cables
    que dicen de dónde sale: `calculado_de` a la situación de origen y
    `justificado_por` a la regla que lo autoriza.
    """
    hechos = {f.role: f.value for f in universe.facts_about(regla)}

    if ROL_EXPRESION not in hechos:
        raise ErrorDerivacion(
            f"La regla '{regla.id}' no declara `expresion`.")
    expresion = hechos[ROL_EXPRESION].label or hechos[ROL_EXPRESION].id

    if ROL_UNIDAD_DESTINO not in hechos:
        raise ErrorDerivacion(
            f"La regla '{regla.id}' no declara `unidad_destino`. Sin ella el "
            f"resultado sería un número sin unidad.")
    unidad_destino = hechos[ROL_UNIDAD_DESTINO].id

    resultado = evaluar(universe, expresion, sobre).convertir_a(
        universe, unidad_destino)

    destino = universe.add_individual(Individual(
        id=destino_id, axis=Axis.O,
        label=label or f"{rol_destino} derivado de {sobre.id}"))

    magnitud = Individual(
        id=f"n_{destino_id}", axis=Axis.N,
        label=f"{resultado.valor:g} {unidad_destino}",
        payload={"value": resultado.valor, "unit": unidad_destino})

    universe.assert_fact(destino, rol_destino, magnitud)
    universe.assert_fact(destino, ROL_CALCULADO_DE, sobre)
    universe.assert_fact(destino, ROL_JUSTIFICADO_POR, regla)
    return destino
