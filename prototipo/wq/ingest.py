"""Ingesta: traduce una "oración" (estructurada) a hechos en el universo.

Para el prototipo no parsear español real — eso es trabajo del LLM.
En su lugar exponemos una API de ingesta que recibe verbo + roles ya
identificados y aplica el pipeline:
    1. Resolver lexicon (con polisemia / forma nominal)
    2. Reificar la situación en O
    3. Asentar instancia_de = tipo_situacion
    4. Asentar cada rol como hecho atómico
    5. Validar contra el catálogo D8
    6. Verificar obligatorios

Devuelve la situación reificada para que el caller pueda enriquecerla.
"""

from __future__ import annotations
from datetime import datetime
from typing import Dict, Optional, Any, List

from .axes import Axis
from .individual import Individual, mint_id, category
from .universe import Universe
from .lexicon import Lexicon, LexiconEntry


class IngestError(ValueError):
    pass


def ingest_situation(
    universe: Universe,
    lexicon: Lexicon,
    verb: str,
    roles: Dict[str, Individual],
    *,
    complements: Optional[List[str]] = None,
    nominal: bool = False,
    valid_from: Optional[datetime] = None,
    valid_to: Optional[datetime] = None,
    extra: Optional[Dict[str, Individual]] = None,
    sit_id: Optional[str] = None,
) -> Individual:
    """Ingesta una situación a partir de un verbo y sus roles.

    `roles` mapea NOMBRE_CANÓNICO → Individual (el caller ya resolvió aliases).
    `complements` lista patrones de complemento que disparan polisemia
    (p. ej. ['la_mano'] para `dar la mano`).
    `nominal=True` indica que el "verbo" es en realidad una forma nominal
    ("llegada") y debe buscarse vía `resolve_nominal`.
    `extra` agrega hechos adicionales que no están en la signatura (p. ej.
    `modalidad`, `estatus_factual`, `calificacion`, ...).

    Devuelve la situación reificada en O.
    """
    entry = (
        lexicon.resolve_nominal(verb, complements)
        if nominal else
        lexicon.resolve(verb, complements)
    )
    if entry is None:
        raise IngestError(
            f"Lexicon no tiene entrada para '{verb}' "
            f"con complementos {complements}."
        )

    # Verificar obligatorios
    missing = [r for r in entry.obligatory if r not in roles]
    if missing:
        raise IngestError(
            f"Faltan roles obligatorios para '{verb}': {missing}"
        )

    # Reificar la situación
    sid = sit_id or mint_id(entry.situation_type)
    situ = Individual(id=sid, axis=Axis.O, label=sid)
    universe.add_individual(situ)

    # instancia_de
    tipo = category(entry.situation_type)
    universe.assert_fact(situ, "instancia_de", tipo,
                         valid_from=valid_from, valid_to=valid_to)

    # Roles obligatorios y opcionales
    for role, value in roles.items():
        # No exigimos que esté declarado en la entrada — la entrada es
        # informativa; los extras se admiten. (Política liberal.)
        universe.assert_fact(situ, role, value,
                             valid_from=valid_from, valid_to=valid_to)

    # Extras (modalidad, calificación, ...)
    if extra:
        for role, value in extra.items():
            universe.assert_fact(situ, role, value,
                                 valid_from=valid_from, valid_to=valid_to)

    return situ
