"""WQuestions — prototipo de validación en Python.

Implementa el modelo descrito en `WQuestions.md` y discutido en el libro:
- 7 ejes (Q, O, L, T, N, K, M)
- hechos atómicos con signatura tipada
- situaciones reificadas (D4, D5)
- catálogo canónico de roles (D8)
- lexicon con resolución de polisemia (D9)
- vigencia temporal por reificación (D6)
- consultas como proyecciones sobre roles (preguntas-WH)

Se prioriza claridad sobre rendimiento. La meta es validar la arquitectura,
no servir producción.
"""

from .axes import Axis
from .individual import Individual, mint_id, category, quantity, time_point
from .fact import Fact
from .universe import Universe
from .catalog import Catalog, RoleSignature, SignatureError
from .lexicon import Lexicon, LexiconEntry
from .query import Pattern, Var, Rango, query, count
from .ingest import ingest_situation, IngestError
from .vistas import tabla_plana, proyeccion, pivote
from .magnitud import Magnitud, UnidadReducida, reducir_unidad, ErrorDimensional
from .derivacion import (declarar_unidad, declarar_unidades_base,
                         evaluar, derivar, ErrorDerivacion)
from .formas import (declarar_forma, evaluar_formas, formas_declaradas,
                     Violacion, ErrorDeForma)

__all__ = [
    "Magnitud", "UnidadReducida", "reducir_unidad", "ErrorDimensional",
    "declarar_unidad", "declarar_unidades_base", "evaluar", "derivar",
    "ErrorDerivacion",
    "declarar_forma", "evaluar_formas", "formas_declaradas",
    "Violacion", "ErrorDeForma",
    "Axis", "Individual", "mint_id", "category", "quantity", "time_point",
    "Fact", "Universe",
    "Catalog", "RoleSignature", "SignatureError",
    "Lexicon", "LexiconEntry",
    "Pattern", "Var", "Rango", "query", "count",
    "ingest_situation", "IngestError",
    "tabla_plana", "proyeccion", "pivote",
]
