"""Tests del evaluador de formas.

Lo que se prueba, sobre todo, es lo que el evaluador NO hace: no rechaza
escrituras, no borra nada al cerrar una violación, y no se valida a sí mismo.
"""

import unittest
from datetime import datetime, timezone

from wq import (Axis, Individual, Universe, Catalog, declarar_forma,
                evaluar_formas, formas_declaradas, ErrorDeForma)
from wq.formas import CAT_VIOLACION, EST_ABIERTA, EST_RESUELTA
from wq.unidades import sembrar_si


def D(mes, dia):
    return datetime(2026, mes, dia, tzinfo=timezone.utc)


def pct(valor, vid):
    return Individual(id=vid, axis=Axis.N,
                      payload={"value": valor, "unit": "K:Porcentaje"})


def ton(valor, vid):
    return Individual(id=vid, axis=Axis.N,
                      payload={"value": valor, "unit": "K:ToneladaMetrica"})


class BaseFormas(unittest.TestCase):
    def setUp(self):
        self.u = Universe(catalog=Catalog())
        sembrar_si(self.u)

    def sujeto(self, sid, tipo=None):
        s = self.u.add_individual(Individual(id=sid, axis=Axis.O))
        if tipo:
            self.u.assert_fact(s, "instancia_de", self.u.add_individual(
                Individual(id=tipo, axis=Axis.K)))
        return s

    def forma_rango(self, fid="forma_disp", rol="disponibilidad", **kw):
        return declarar_forma(self.u, fid, tipo="rango", rol=rol,
                              minimo=pct(0, f"n_min_{fid}"),
                              maximo=pct(100, f"n_max_{fid}"), **kw)


class TestRango(BaseFormas):
    def test_valor_dentro_del_rango_no_viola(self):
        self.forma_rango()
        self.u.assert_fact(self.sujeto("s1"), "disponibilidad", pct(94, "n94"))
        self.assertEqual(evaluar_formas(self.u), [])

    def test_valor_por_encima_del_maximo_viola(self):
        self.forma_rango()
        self.u.assert_fact(self.sujeto("s1"), "disponibilidad", pct(140, "n140"))
        v = evaluar_formas(self.u)
        self.assertEqual(len(v), 1)
        self.assertIn("por encima del máximo", v[0].detalle)

    def test_valor_por_debajo_del_minimo_viola(self):
        self.forma_rango()
        self.u.assert_fact(self.sujeto("s1"), "disponibilidad", pct(-5, "nm5"))
        self.assertIn("por debajo del mínimo", evaluar_formas(self.u)[0].detalle)

    def test_el_rango_compara_respetando_unidades(self):
        """Un mínimo en gramos contra un valor en toneladas se compara bien."""
        declarar_forma(self.u, "forma_carga", tipo="rango", rol="carga",
                       minimo=Individual(id="n_min_g", axis=Axis.N,
                                         payload={"value": 500,
                                                  "unit": "K:Gramo"}))
        self.u.assert_fact(self.sujeto("s1"), "carga", ton(1, "n_1t"))
        self.assertEqual(evaluar_formas(self.u), [])   # 1 t > 500 g

    def test_unidades_incomparables_es_error_no_violacion(self):
        declarar_forma(self.u, "forma_absurda", tipo="rango", rol="duracion",
                       minimo=pct(0, "n_0b"))
        self.u.assert_fact(self.sujeto("s1"), "duracion", ton(5, "n_5t"))
        with self.assertRaises(ErrorDeForma):
            evaluar_formas(self.u)

    def test_la_forma_puede_acotarse_a_un_tipo(self):
        self.forma_rango(aplica_a="proyeccion")
        self.u.assert_fact(self.sujeto("otro", tipo="medicion"),
                           "disponibilidad", pct(140, "n140b"))
        self.assertEqual(evaluar_formas(self.u), [])


class TestOtrosTipos(BaseFormas):
    def test_cardinalidad_minima(self):
        declarar_forma(self.u, "forma_agente", tipo="cardinalidad",
                       rol="agente", minimo=pct(1, "n_1"))
        s = self.sujeto("venta")
        self.u.assert_fact(s, "monto", ton(1, "n_1t"))
        self.assertEqual(evaluar_formas(self.u), [])   # sin agente, no aplica

    def test_cardinalidad_maxima_detecta_el_exceso(self):
        declarar_forma(self.u, "forma_agente", tipo="cardinalidad",
                       rol="operador_asignado", maximo=pct(2, "n_2"))
        s = self.sujeto("turno")
        for i in range(3):
            self.u.assert_fact(s, "operador_asignado", self.u.add_individual(
                Individual(id=f"op_{i}", axis=Axis.Q)))
        v = evaluar_formas(self.u)
        self.assertEqual(len(v), 1)
        self.assertIn("tiene 3", v[0].detalle)

    def test_requiere_detecta_el_rol_ausente(self):
        declarar_forma(self.u, "forma_lugar", tipo="requiere",
                       rol="monto", requiere="lugar_de")
        self.u.assert_fact(self.sujeto("v1"), "monto", ton(1, "n_1t"))
        v = evaluar_formas(self.u)
        self.assertEqual(len(v), 1)
        self.assertIn("le falta 'lugar_de'", v[0].detalle)

    def test_requiere_se_satisface(self):
        declarar_forma(self.u, "forma_lugar", tipo="requiere",
                       rol="monto", requiere="lugar_de")
        s = self.sujeto("v1")
        self.u.assert_fact(s, "monto", ton(1, "n_1t"))
        self.u.assert_fact(s, "lugar_de", self.u.add_individual(
            Individual(id="tienda", axis=Axis.L)))
        self.assertEqual(evaluar_formas(self.u), [])

    def test_unicidad_detecta_el_duplicado(self):
        declarar_forma(self.u, "forma_folio", tipo="unicidad", rol="folio")
        for sid in ("f1", "f2"):
            self.u.assert_fact(self.sujeto(sid), "folio",
                               self.u.add_individual(
                                   Individual(id="folio_001", axis=Axis.K)))
        v = evaluar_formas(self.u)
        self.assertEqual(len(v), 1)
        self.assertIn("repite", v[0].detalle)

    def test_tipo_de_forma_desconocido_se_rechaza(self):
        with self.assertRaises(ErrorDeForma):
            declarar_forma(self.u, "f", tipo="telepatia", rol="x")

    def test_forma_de_rango_sin_cotas_se_rechaza(self):
        with self.assertRaises(ErrorDeForma):
            declarar_forma(self.u, "f", tipo="rango", rol="x")


class TestVigenciaYCardinalidad(BaseFormas):
    def test_solo_se_evalua_lo_vigente_en_el_momento(self):
        """Un escenario proyectado se valida en la fecha en que regiría."""
        self.forma_rango()
        self.u.assert_fact(self.sujeto("sim"), "disponibilidad",
                           pct(140, "n140"), valid_from=D(7, 1),
                           valid_to=D(8, 1))
        self.assertEqual(evaluar_formas(self.u, momento=D(5, 20)), [])
        self.assertEqual(len(evaluar_formas(self.u, momento=D(7, 15))), 1)

    def test_un_rol_funcional_se_juzga_por_su_valor_vigente(self):
        """Corregir el hecho apaga la violación; no la acumula."""
        self.forma_rango(rol="monto")
        s = self.sujeto("v1")
        self.u.assert_fact(s, "monto", pct(140, "n140"))
        self.assertEqual(len(evaluar_formas(self.u)), 1)
        self.u.assert_fact(s, "monto", pct(88, "n88"))
        self.assertEqual(evaluar_formas(self.u), [])


class TestRegistro(BaseFormas):
    def test_la_violacion_no_impide_la_escritura(self):
        self.forma_rango()
        s = self.sujeto("s1")
        self.u.assert_fact(s, "disponibilidad", pct(140, "n140"))
        self.u.validate()
        vigentes = [f.value.payload["value"]
                    for f in self.u.facts_about(s) if f.role == "disponibilidad"]
        self.assertEqual(vigentes, [140])

    def test_la_violacion_entra_como_hecho_con_su_procedencia(self):
        forma = self.forma_rango()
        s = self.sujeto("s1")
        self.u.assert_fact(s, "disponibilidad", pct(140, "n140"))
        self.u.validate()
        nodo = self.u.ind("violacion_0001")
        hechos = {f.role: f.value.id for f in self.u.facts_about(nodo)}
        self.assertEqual(hechos["instancia_de"], CAT_VIOLACION)
        self.assertEqual(hechos["sobre"], "s1")
        self.assertEqual(hechos["justificado_por"], forma.id)
        self.assertEqual(hechos["estado"], EST_ABIERTA)

    def test_corregir_el_hecho_cierra_la_violacion_sin_borrarla(self):
        self.forma_rango(rol="monto")
        s = self.sujeto("s1")
        self.u.assert_fact(s, "monto", pct(140, "n140"))
        self.u.validate()
        self.u.assert_fact(s, "monto", pct(88, "n88"))
        informe = self.u.validate()
        self.assertEqual(informe["cerradas"], ["violacion_0001"])
        estados = [f.value.id for f in self.u.facts_about(self.u.ind("violacion_0001"))
                   if f.role == "estado"]
        self.assertEqual(estados, [EST_ABIERTA, EST_RESUELTA])

    def test_validar_dos_veces_no_duplica_la_violacion(self):
        self.forma_rango()
        self.u.assert_fact(self.sujeto("s1"), "disponibilidad", pct(140, "n140"))
        self.u.validate()
        informe = self.u.validate()
        self.assertEqual(informe["abiertas"], [])
        violaciones = [f.subject.id for f in self.u.facts
                       if f.role == "instancia_de" and f.value.id == CAT_VIOLACION]
        self.assertEqual(len(violaciones), 1)

    def test_sin_registrar_no_escribe_nada(self):
        self.forma_rango()
        self.u.assert_fact(self.sujeto("s1"), "disponibilidad", pct(140, "n140"))
        antes = len(self.u.facts)
        self.u.validate(registrar=False)
        self.assertEqual(len(self.u.facts), antes)

    def test_el_evaluador_no_se_valida_a_si_mismo(self):
        """Los hechos que escribe el evaluador no disparan otra evaluación."""
        u = Universe(catalog=Catalog(), validar_al_escribir=True)
        sembrar_si(u)
        declarar_forma(u, "forma_disp", tipo="rango", rol="disponibilidad",
                       minimo=pct(0, "n_0"), maximo=pct(100, "n_100"))
        s = u.add_individual(Individual(id="s1", axis=Axis.O))
        u.assert_fact(s, "disponibilidad", pct(140, "n140"))
        violaciones = [f.subject.id for f in u.facts
                       if f.role == "instancia_de" and f.value.id == CAT_VIOLACION]
        self.assertEqual(len(violaciones), 1)

    def test_el_gancho_de_escritura_registra_al_vuelo(self):
        u = Universe(catalog=Catalog(), validar_al_escribir=True)
        sembrar_si(u)
        declarar_forma(u, "forma_disp", tipo="rango", rol="disponibilidad",
                       minimo=pct(0, "n_0"), maximo=pct(100, "n_100"))
        s = u.add_individual(Individual(id="s1", axis=Axis.O))
        u.assert_fact(s, "disponibilidad", pct(140, "n140"))
        self.assertEqual(
            u.ind("violacion_0001").label,
            "140 K:Porcentaje por encima del máximo 100 K:Porcentaje")

    def test_un_barrido_parcial_no_cierra_violaciones_ajenas(self):
        self.forma_rango(fid="forma_a", rol="disponibilidad")
        declarar_forma(self.u, "forma_b", tipo="unicidad", rol="folio")
        self.u.assert_fact(self.sujeto("s1"), "disponibilidad", pct(140, "n140"))
        for sid in ("f1", "f2"):
            self.u.assert_fact(self.sujeto(sid), "folio", self.u.add_individual(
                Individual(id="folio_001", axis=Axis.K)))
        self.u.validate()
        self.assertEqual(self.u.validate(solo_rol="folio")["cerradas"], [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
