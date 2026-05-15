"""Suite de tests del prototipo WQuestions.

Cubre las capacidades que el libro afirma del modelo, una a una.
Se corre con: PYTHONPATH=. python3 -m unittest tests.test_wq -v
"""

from __future__ import annotations
import unittest
from datetime import datetime, timezone

from wq import (
    Axis, Individual, Universe, Catalog, Lexicon, LexiconEntry,
    Pattern, Var, query, count, ingest_situation, category,
    SignatureError, IngestError,
)


# ===========================================================================
# 1. Ejes e individuos
# ===========================================================================

class TestAxes(unittest.TestCase):
    def test_individual_must_live_in_value_axis(self):
        with self.assertRaises(ValueError):
            Individual(id="x", axis=Axis.P)
        with self.assertRaises(ValueError):
            Individual(id="x", axis=Axis.M)

    def test_value_axis_individuals_ok(self):
        for ax in [Axis.Q, Axis.O, Axis.L, Axis.T, Axis.N, Axis.K]:
            Individual(id=f"x_{ax.value}", axis=ax)


# ===========================================================================
# 2. Validación de signaturas (D7)
# ===========================================================================

class TestSignatures(unittest.TestCase):
    def setUp(self):
        self.cat = Catalog()
        self.u = Universe(catalog=self.cat)
        self.sit = Individual(id="s1", axis=Axis.O, label="s1")
        self.persona = Individual(id="p1", axis=Axis.Q, label="p1")
        self.lugar = Individual(id="l1", axis=Axis.L, label="l1")
        self.cat_k = Individual(id="k1", axis=Axis.K, label="k1")

    def test_agente_rejects_non_Q(self):
        with self.assertRaises(SignatureError):
            self.u.assert_fact(self.sit, "agente", self.lugar)

    def test_lugar_de_rejects_non_L(self):
        with self.assertRaises(SignatureError):
            self.u.assert_fact(self.sit, "lugar_de", self.persona)

    def test_agente_accepts_Q(self):
        f = self.u.assert_fact(self.sit, "agente", self.persona)
        self.assertEqual(f.value.id, "p1")

    def test_instancia_de_requires_K_value(self):
        with self.assertRaises(SignatureError):
            self.u.assert_fact(self.sit, "instancia_de", self.persona)
        # OK con K
        self.u.assert_fact(self.sit, "instancia_de", self.cat_k)

    def test_unknown_role_is_permitted(self):
        """Roles no declarados pasan (política liberal — extensibilidad)."""
        f = self.u.assert_fact(self.sit, "rol_de_dominio_nuevo", self.persona)
        self.assertEqual(f.role, "rol_de_dominio_nuevo")


# ===========================================================================
# 3. Lexicon — polisemia y nominalización
# ===========================================================================

class TestLexicon(unittest.TestCase):
    def setUp(self):
        self.lex = Lexicon()
        self.lex.register(LexiconEntry(
            verb="dar",
            situation_type="accion_dar",
            obligatory=["agente", "tema", "beneficiario"],
        ))
        self.lex.register(LexiconEntry(
            verb="dar",
            situation_type="accion_saludar",
            obligatory=["agente", "paciente"],
            pattern=("la_mano",),
        ))
        self.lex.register(LexiconEntry(
            verb="dar",
            situation_type="evento_exposicion",
            obligatory=["agente", "tema"],
            pattern=("conferencia",),
        ))
        self.lex.register(LexiconEntry(
            verb="llegar",
            situation_type="accion_llegar",
            obligatory=["agente"],
            nominal_forms=["llegada", "arribo"],
        ))

    def test_polysemy_most_specific_first(self):
        e = self.lex.resolve("dar", ["la_mano"])
        self.assertEqual(e.situation_type, "accion_saludar")

        e = self.lex.resolve("dar", ["conferencia"])
        self.assertEqual(e.situation_type, "evento_exposicion")

        # Sin complemento: cae a genérico
        e = self.lex.resolve("dar", [])
        self.assertEqual(e.situation_type, "accion_dar")

    def test_polysemy_returns_none_for_unknown_verb(self):
        self.assertIsNone(self.lex.resolve("voldear", []))

    def test_nominal_resolves_to_verb(self):
        e = self.lex.resolve_nominal("llegada")
        self.assertIsNotNone(e)
        self.assertEqual(e.verb, "llegar")

        e = self.lex.resolve_nominal("arribo")
        self.assertEqual(e.verb, "llegar")

    def test_domain_dialect(self):
        self.lex.register_domain_dialect("sauna_oasis", {
            "cliente": "agente",
            "sesion": "servicio_sauna",
        })
        self.assertEqual(
            self.lex.translate_alias("sauna_oasis", "cliente"),
            "agente",
        )
        self.assertIsNone(self.lex.translate_alias("ventas", "cliente"))


# ===========================================================================
# 4. Ingesta — reificación + validación de obligatorios
# ===========================================================================

class TestIngest(unittest.TestCase):
    def setUp(self):
        self.cat = Catalog()
        self.u = Universe(catalog=self.cat)
        self.lex = Lexicon()
        self.lex.register(LexiconEntry(
            verb="vender",
            situation_type="accion_vender",
            obligatory=["agente", "tema", "comprador", "monto", "unidad"],
            optional=["momento"],
        ))
        self.q1 = Individual(id="vendedor", axis=Axis.Q, label="vendedor")
        self.q2 = Individual(id="comprador1", axis=Axis.Q, label="comprador1")
        self.libro = Individual(id="libro_01", axis=Axis.O, label="libro_01")
        self.usd = Individual(id="USD", axis=Axis.K, label="USD")
        self.precio = Individual(id="n_20_usd", axis=Axis.N, label="20 USD",
                                 payload={"value": 20, "unit": "USD"})

    def test_ingest_reifies_situation_and_facts(self):
        sit = ingest_situation(self.u, self.lex, "vender", roles={
            "agente": self.q1, "tema": self.libro,
            "comprador": self.q2, "monto": self.precio, "unidad": self.usd,
        })
        self.assertEqual(sit.axis, Axis.O)
        facts = self.u.facts_about(sit)
        roles = {f.role for f in facts}
        # debe incluir instancia_de + los 5 obligatorios
        self.assertIn("instancia_de", roles)
        for r in ["agente", "tema", "comprador", "monto", "unidad"]:
            self.assertIn(r, roles)

    def test_ingest_rejects_missing_obligatory(self):
        with self.assertRaises(IngestError):
            ingest_situation(self.u, self.lex, "vender", roles={
                "agente": self.q1, "tema": self.libro,
                # falta comprador, monto, unidad
            })

    def test_ingest_unknown_verb(self):
        with self.assertRaises(IngestError):
            ingest_situation(self.u, self.lex, "voldear", roles={})


# ===========================================================================
# 5. Modales — una sola situación, con decoradores
# ===========================================================================

class TestModales(unittest.TestCase):
    def test_querer_viajar_creates_one_situation(self):
        cat = Catalog()
        u = Universe(catalog=cat)
        lex = Lexicon()
        lex.register(LexiconEntry(
            verb="viajar", situation_type="accion_viajar",
            obligatory=["agente"], optional=["destino", "momento"],
        ))
        juan = Individual(id="juan", axis=Axis.Q, label="Juan")
        cusco = Individual(id="cusco", axis=Axis.L, label="Cusco")
        volitiva = Individual(id="volitiva", axis=Axis.K, label="volitiva")
        intencionado = Individual(id="intencionado", axis=Axis.K,
                                  label="intencionado")

        sit = ingest_situation(u, lex, "viajar", roles={
            "agente": juan, "destino": cusco,
        }, extra={"modalidad": volitiva, "estatus_factual": intencionado})

        # Solo una situación O reificada
        sits_O = [
            ind for ind in u.individuals.values() if ind.axis == Axis.O
        ]
        self.assertEqual(len(sits_O), 1)

        # Tiene los decoradores
        facts = u.facts_about(sit)
        modal = [f for f in facts if f.role == "modalidad"]
        self.assertEqual(modal[0].value.id, "volitiva")


# ===========================================================================
# 6. Consultas WH (proyección)
# ===========================================================================

class TestQueries(unittest.TestCase):
    def setUp(self):
        self.cat = Catalog()
        self.u = Universe(catalog=self.cat)
        self.lex = Lexicon()
        self.lex.register(LexiconEntry(
            verb="dar", situation_type="accion_dar",
            obligatory=["agente", "tema", "beneficiario"],
        ))
        self.juan = Individual(id="juan", axis=Axis.Q, label="Juan")
        self.maria = Individual(id="maria", axis=Axis.Q, label="María")
        self.libro = Individual(id="libro", axis=Axis.O, label="libro")
        ingest_situation(self.u, self.lex, "dar", roles={
            "agente": self.juan, "tema": self.libro,
            "beneficiario": self.maria,
        })

    def test_quien_dio_el_libro_a_maria(self):
        accion_dar = self.u.ind("accion_dar")
        result = query(self.u, Pattern(
            fixed={"tema": self.libro, "beneficiario": self.maria},
            ask={"agente": Var()},
            type_constraint=accion_dar,
        ))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["agente"].id, "juan")

    def test_a_quien_dio_juan_el_libro(self):
        accion_dar = self.u.ind("accion_dar")
        result = query(self.u, Pattern(
            fixed={"agente": self.juan, "tema": self.libro},
            ask={"beneficiario": Var()},
            type_constraint=accion_dar,
        ))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["beneficiario"].id, "maria")

    def test_count_by_pattern(self):
        accion_dar = self.u.ind("accion_dar")
        n = count(self.u, Pattern(
            fixed={"agente": self.juan},
            type_constraint=accion_dar,
        ))
        self.assertEqual(n, 1)


# ===========================================================================
# 7. D9 — vigencia temporal
# ===========================================================================

class TestTemporalValidity(unittest.TestCase):
    def test_query_at_moment_returns_valid_facts(self):
        cat = Catalog()
        u = Universe(catalog=cat)
        marta = Individual(id="marta", axis=Axis.Q, label="Marta")
        ciudad_a = Individual(id="ciudad_a", axis=Axis.L, label="ciudad_a")
        ciudad_b = Individual(id="ciudad_b", axis=Axis.L, label="ciudad_b")

        # Reificamos las dos residencias
        res1 = Individual(id="res1", axis=Axis.O)
        res2 = Individual(id="res2", axis=Axis.O)
        tipo = Individual(id="residencia", axis=Axis.K)

        t1_start = datetime(2010, 1, 1, tzinfo=timezone.utc)
        t1_end = datetime(2025, 12, 31, tzinfo=timezone.utc)
        t2_start = datetime(2026, 1, 1, tzinfo=timezone.utc)

        for role, val in [("instancia_de", tipo), ("agente", marta),
                          ("lugar_de", ciudad_a)]:
            u.assert_fact(res1, role, val,
                          valid_from=t1_start, valid_to=t1_end)
        for role, val in [("instancia_de", tipo), ("agente", marta),
                          ("lugar_de", ciudad_b)]:
            u.assert_fact(res2, role, val, valid_from=t2_start)

        # Consulta en 2018
        t_2018 = datetime(2018, 6, 1, tzinfo=timezone.utc)
        r = query(u, Pattern(
            fixed={"agente": marta},
            ask={"lugar_de": Var()},
            type_constraint=tipo,
        ), at=t_2018)
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0]["lugar_de"].id, "ciudad_a")

        # Consulta en 2027
        t_2027 = datetime(2027, 6, 1, tzinfo=timezone.utc)
        r = query(u, Pattern(
            fixed={"agente": marta},
            ask={"lugar_de": Var()},
            type_constraint=tipo,
        ), at=t_2027)
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0]["lugar_de"].id, "ciudad_b")

    def test_fact_without_validity_is_always_valid(self):
        cat = Catalog()
        u = Universe(catalog=cat)
        sit = Individual(id="s", axis=Axis.O)
        k = Individual(id="tipo", axis=Axis.K)
        u.assert_fact(sit, "instancia_de", k)
        # En cualquier momento debe seguir siendo cierto
        far_past = datetime(1900, 1, 1, tzinfo=timezone.utc)
        far_future = datetime(2100, 1, 1, tzinfo=timezone.utc)
        for t in [far_past, far_future]:
            facts = u.facts_about(sit, at=t)
            self.assertEqual(len(facts), 1)


# ===========================================================================
# 8. Sauna end-to-end
# ===========================================================================

class TestSaunaDomain(unittest.TestCase):
    def test_sauna_demo_passes_all_validations(self):
        from ejemplos.sauna import build_lexicon, build_universe, run_validations
        lex = build_lexicon()
        u, h = build_universe(lex)
        results = run_validations(u, lex, h)
        failed = [(q, c) for q, ok, c in results if not ok]
        self.assertEqual(
            len(failed), 0,
            f"Validaciones fallidas en sauna: {failed}",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
