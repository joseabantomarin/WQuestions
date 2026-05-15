"""WQuestions — prototipo de validación en Python.

Implementa el modelo descrito en `WQuestions.md` y discutido en el libro:
- 8 ejes (Q, O, L, T, N, K, P, M)
- hechos atómicos con signatura tipada
- situaciones reificadas (D2, D5)
- catálogo canónico de roles (D7)
- lexicon con resolución de polisemia (D8)
- vigencia temporal por reificación (D9)
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
from .query import Pattern, Var, query, count
from .ingest import ingest_situation, IngestError

__all__ = [
    "Axis", "Individual", "mint_id", "category", "quantity", "time_point",
    "Fact", "Universe",
    "Catalog", "RoleSignature", "SignatureError",
    "Lexicon", "LexiconEntry",
    "Pattern", "Var", "query", "count",
    "ingest_situation", "IngestError",
]
