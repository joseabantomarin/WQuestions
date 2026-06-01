"""Los 7 ejes de WQuestions.

Seis ejes de valor (contienen individuos):
    Q — quién — agentes
    O — qué  — objetos / situaciones reificadas
    L — dónde — lugares
    T — cuándo — momentos / intervalos
    N — cuánto — magnitudes con unidad
    K — cuál — categorías atemporales (tipos, unidades, estados, vocabularios)

Un eje estructural (contiene etiquetas con signatura):
    M — cómo — predicados/cables que conectan individuos. Cada predicado
        declara su cardinalidad en la signatura (`functional`: un solo valor
        por sujeto, o múltiple). La cardinalidad es un atributo del predicado,
        no un eje aparte.
"""

from enum import Enum


class Axis(Enum):
    Q = "Q"  # quién
    O = "O"  # qué (objectum)
    L = "L"  # dónde
    T = "T"  # cuándo (tempus)
    N = "N"  # cuánto
    K = "K"  # cuál (categórico)
    M = "M"  # cómo / predicados (modus)


VALUE_AXES = {Axis.Q, Axis.O, Axis.L, Axis.T, Axis.N, Axis.K}
PREDICATE_AXES = {Axis.M}


def is_value_axis(axis: Axis) -> bool:
    return axis in VALUE_AXES
