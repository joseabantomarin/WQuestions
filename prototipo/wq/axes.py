"""Los 8 ejes de WQuestions.

Seis ejes de valor (contienen individuos):
    Q — quién — agentes
    O — qué  — objetos / situaciones reificadas
    L — dónde — lugares
    T — cuándo — momentos / intervalos
    N — cuánto — magnitudes con unidad
    K — clase — categorías atemporales

Dos ejes estructurales (contienen etiquetas con signatura):
    P — predicados funcionales (un valor por sujeto)
    M — predicados no funcionales (varios valores admitidos)
"""

from enum import Enum


class Axis(Enum):
    Q = "Q"  # quien
    O = "O"  # qué (objectum)
    L = "L"  # dónde
    T = "T"  # cuándo (tempus)
    N = "N"  # cuánto
    K = "K"  # clase
    P = "P"  # cuál (funcional)
    M = "M"  # cómo / multi (modus)


VALUE_AXES = {Axis.Q, Axis.O, Axis.L, Axis.T, Axis.N, Axis.K}
PREDICATE_AXES = {Axis.P, Axis.M}


def is_value_axis(axis: Axis) -> bool:
    return axis in VALUE_AXES
