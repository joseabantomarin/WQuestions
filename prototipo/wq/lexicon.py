"""Lexicon: diccionario verbo → tipo de situación + roles + aliases.

Implementa el paradigma del capítulo 13: cada entrada declara una
signatura (qué roles obligatorios y opcionales), un tipo de situación en K,
y aliases naturales por rol y por dominio. La resolución de polisemia
elige la entrada más específica que coincide con el patrón de complemento.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class LexiconEntry:
    verb: str                          # "vender", "dar", ...
    situation_type: str                # K id, ej. "accion_vender"
    obligatory: List[str] = field(default_factory=list)
    optional: List[str] = field(default_factory=list)
    aliases: Dict[str, List[str]] = field(default_factory=dict)
    nominal_forms: List[str] = field(default_factory=list)
    pattern: Optional[Tuple[str, ...]] = None  # complementos clave para polisemia
    notes: str = ""
    example: str = ""

    def specificity(self) -> int:
        """Cuanto más largo el patrón, más específica la entrada."""
        return 0 if self.pattern is None else len(self.pattern)

    def matches(self, observed_complements: List[str]) -> bool:
        """¿Esta entrada coincide con los complementos vistos en la oración?

        Una entrada con `pattern=None` siempre coincide (entrada genérica).
        Una entrada con patrón coincide si TODOS sus elementos aparecen
        entre los complementos.
        """
        if self.pattern is None:
            return True
        obs = set(observed_complements)
        return all(p in obs for p in self.pattern)


class Lexicon:
    """Lexicon con resolución de polisemia.

    Las entradas se registran por verbo; varias entradas pueden compartir
    verbo (polisemia). `resolve(verb, complements)` devuelve la entrada
    más específica que coincide.
    """

    def __init__(self):
        self._by_verb: Dict[str, List[LexiconEntry]] = {}
        # Aliases globales de dominio: nombre_usuario → rol_canonico
        self._domain_aliases: Dict[str, Dict[str, str]] = {}
        # Aliases nominales globales: forma_nominal → verbo
        self._nominal_index: Dict[str, str] = {}

    # --- registro ----------------------------------------------------------

    def register(self, entry: LexiconEntry) -> None:
        self._by_verb.setdefault(entry.verb, []).append(entry)
        # Orden por especificidad decreciente: más específico primero.
        self._by_verb[entry.verb].sort(key=lambda e: -e.specificity())
        for nf in entry.nominal_forms:
            self._nominal_index[nf] = entry.verb

    def register_domain_dialect(self, domain: str,
                                aliases: Dict[str, str]) -> None:
        """Agrega un dialecto de dominio: nombre_usuario → rol_canónico."""
        self._domain_aliases.setdefault(domain, {}).update(aliases)

    # --- resolución --------------------------------------------------------

    def resolve(self, verb: str,
                complements: Optional[List[str]] = None) -> Optional[LexiconEntry]:
        """Devuelve la entrada más específica que coincide con el verbo
        y los complementos observados. None si no hay match.
        """
        candidates = self._by_verb.get(verb, [])
        comps = complements or []
        for entry in candidates:  # ya ordenadas más específico → más general
            if entry.matches(comps):
                return entry
        return None

    def resolve_nominal(self, nominal_form: str,
                        complements: Optional[List[str]] = None
                        ) -> Optional[LexiconEntry]:
        """Resolución por forma nominal (nominalización).

        *"la llegada del avión"* → verbo `llegar` → entrada de llegar.
        """
        verb = self._nominal_index.get(nominal_form)
        if verb is None:
            return None
        return self.resolve(verb, complements)

    def translate_alias(self, domain: str, user_term: str) -> Optional[str]:
        """Traduce un término de usuario al rol canónico vía dialecto."""
        return self._domain_aliases.get(domain, {}).get(user_term)

    def alias_for_role(self, verb: str, role: str) -> List[str]:
        """Aliases declarados para un rol de una entrada específica."""
        entries = self._by_verb.get(verb, [])
        for e in entries:
            if role in e.aliases:
                return e.aliases[role]
        return []

    # --- introspección -----------------------------------------------------

    def verbs(self) -> List[str]:
        return list(self._by_verb.keys())

    def entries_for(self, verb: str) -> List[LexiconEntry]:
        return list(self._by_verb.get(verb, []))
