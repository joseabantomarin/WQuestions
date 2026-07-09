"""Prebuilt demo universes, populated through WQSession's public API so the
demo path exercises exactly what an LLM client would call."""
from __future__ import annotations


def build_spa(session) -> None:
    """A tiny spa: two clients, three visits across two years."""
    session.add_entity("ana", "Q", "Ana")
    session.add_entity("beto", "Q", "Beto")
    session.add_entity("spa_oasis", "L", "Spa Oasis")
    for agent, when in [("ana", "2024-03-01"),
                        ("ana", "2025-06-10"),
                        ("beto", "2025-06-11")]:
        session.assert_situation(
            "visit",
            roles={"agente": agent, "lugar_de": "spa_oasis"},
            valid_from=when,
        )


EXAMPLES = {"spa": build_spa}
