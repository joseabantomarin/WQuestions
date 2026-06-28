"""Vistas tabulares del modelo: el grafo proyectado de vuelta a tablas.

Implementa el aplanado del cap. 8 — "De la geometría a la tabla que ya conoces":
tres proyecciones del universo de coordenadas a `pandas.DataFrame`, bajo demanda.

- `tabla_plana`  — Fig 8.2: la hoja dispersa universal (Q/O/L/T/N/K, con códigos).
- `proyeccion`   — Fig 8.4: un reporte legible (filtra K, resuelve etiquetas,
                   proyecta un enlace M como columna).
- `pivote`       — Fig 8.5: el cruce de dos ejes con conteos.

La tabla no es el modelo; es una de sus vistas.
"""

from __future__ import annotations
from datetime import datetime
from typing import Dict, List, Optional, Sequence, Tuple

import pandas as pd

from .axes import Axis
from .individual import Individual
from .universe import Universe


_EJES_VALOR = [Axis.Q, Axis.O, Axis.L, Axis.T, Axis.N, Axis.K]


def _etiqueta(ind: Individual) -> str:
    """Etiqueta humana de un individuo; cae al id si no tiene label."""
    return ind.label or ind.id


def _es_situacion(u: Universe, ind: Individual) -> bool:
    """Una situación reificada vive en O y tiene al menos un `instancia_de`."""
    if ind.axis != Axis.O:
        return False
    return any(f.role == "instancia_de" for f in u.facts_about(ind))


def _situaciones(u: Universe) -> List[Individual]:
    """Todas las situaciones reificadas, en orden de inserción estable."""
    return [ind for ind in u.individuals.values() if _es_situacion(u, ind)]


def tabla_plana(u: Universe,
                subjects: Optional[Sequence[Individual]] = None,
                at: Optional[datetime] = None) -> pd.DataFrame:
    """Fig 8.2 — la hoja dispersa universal.

    Una fila por situación reificada; columnas = los seis ejes de valor
    (Q/O/L/T/N/K); celdas = ids (códigos). Varios valores en un eje se unen
    con "; "; ejes sin valor quedan en "". La columna O es la id de la propia
    situación (los enlaces O→O no se vuelcan ahí).
    """
    sits = list(subjects) if subjects is not None else _situaciones(u)
    columnas = [ax.value for ax in _EJES_VALOR]  # ["Q","O","L","T","N","K"]
    filas: List[Dict[str, str]] = []
    for sit in sits:
        bucket: Dict[str, List[str]] = {c: [] for c in columnas}
        bucket["O"] = [sit.id]
        for f in u.facts_about(sit, at=at):
            ax = f.value.axis.value
            if ax == "O":
                continue
            if ax in bucket:
                bucket[ax].append(f.value.id)
        filas.append({c: "; ".join(bucket[c]) for c in columnas})
    return pd.DataFrame(filas, columns=columnas)


def proyeccion(*args, **kwargs):  # implementado en Task 2
    raise NotImplementedError


def pivote(*args, **kwargs):  # implementado en Task 3
    raise NotImplementedError
