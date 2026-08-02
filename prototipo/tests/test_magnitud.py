"""Tests de la aritmética dimensional y de la derivación.

Lo que se prueba no es que las cuentas salgan: es que las cuentas imposibles
NO salgan. Un motor que multiplica sin mirar unidades produce hechos
numéricamente correctos y dimensionalmente falsos.
"""

import unittest

from wq import (Axis, Individual, Universe, Magnitud, declarar_unidad,
                derivar, ErrorDimensional, ErrorDerivacion, evaluar)
from wq.magnitud import reducir_unidad
from wq.unidades import sembrar_si


def magnitud(u, valor, unidad, vid=None):
    ind = Individual(id=vid or f"n_{valor}_{unidad}", axis=Axis.N,
                     payload={"value": valor, "unit": unidad})
    return Magnitud.de(u, ind)


class TestReduccionDeUnidades(unittest.TestCase):
    def setUp(self):
        self.u = Universe()
        sembrar_si(self.u)

    def test_unidad_base_se_representa_a_si_misma(self):
        r = reducir_unidad(self.u, "K:Gramo")
        self.assertEqual(r.exponentes, {"K:Gramo": 1})
        self.assertEqual(r.factor, 1.0)

    def test_unidad_derivada_lleva_su_factor(self):
        r = reducir_unidad(self.u, "K:ToneladaMetrica")
        self.assertEqual(r.exponentes, {"K:Gramo": 1})
        self.assertEqual(r.factor, 1e6)

    def test_la_onza_troy_usa_el_factor_exacto_de_qudt(self):
        """31,1034768 y no 31,1: de ese redondeo salen los descuadres."""
        self.assertEqual(reducir_unidad(self.u, "K:OnzaTroy").factor,
                         31.1034768)

    def test_unidad_compuesta_cancela_dimensiones(self):
        """g/t es masa entre masa: adimensional, con escala 1e-6."""
        r = reducir_unidad(self.u, "K:GramoPorTonelada")
        self.assertEqual(r.exponentes, {})
        self.assertAlmostEqual(r.factor, 1e-6)

    def test_unidad_compuesta_conserva_dimensiones_distintas(self):
        r = reducir_unidad(self.u, "K:ToneladaPorHora")
        self.assertEqual(r.exponentes, {"K:Gramo": 1, "K:Segundo": -1})

    def test_porcentaje_es_adimensional_con_escala(self):
        r = reducir_unidad(self.u, "K:Porcentaje")
        self.assertEqual(r.exponentes, {})
        self.assertEqual(r.factor, 0.01)

    def test_unidad_inexistente_falla_con_mensaje_util(self):
        with self.assertRaises(ErrorDimensional) as ctx:
            reducir_unidad(self.u, "K:Chirimoya")
        self.assertIn("no existe", str(ctx.exception))

    def test_unidad_fuera_de_k_falla(self):
        self.u.add_individual(Individual(id="o_falsa", axis=Axis.O))
        with self.assertRaises(ErrorDimensional) as ctx:
            reducir_unidad(self.u, "o_falsa")
        self.assertIn("viven en K", str(ctx.exception))

    def test_declarar_una_unidad_sobre_una_base_inexistente_falla(self):
        with self.assertRaises(KeyError):
            declarar_unidad(self.u, "K:Codo", base="K:Vara", factor=2)

    def test_unidad_circular_no_cuelga(self):
        """A se define sobre B y B sobre A. Se cuela cableando a mano."""
        a = declarar_unidad(self.u, "K:A")
        b = declarar_unidad(self.u, "K:B")
        factor = Individual(id="n_f", axis=Axis.N,
                            payload={"value": 2.0, "unit": "K:Adimensional"})
        for origen, destino in ((a, b), (b, a)):
            self.u.assert_fact(origen, "unidad_base", destino)
            self.u.assert_fact(origen, "factor_a_base", factor)
        with self.assertRaises(ErrorDimensional) as ctx:
            reducir_unidad(self.u, "K:A")
        self.assertIn("círculo", str(ctx.exception))


class TestAritmetica(unittest.TestCase):
    def setUp(self):
        self.u = Universe()
        sembrar_si(self.u)

    def test_producto_combina_dimensiones(self):
        """El caso del capítulo 23: 2480 t × 8,6 g/t = 21.328 g."""
        t = magnitud(self.u, 2480, "K:ToneladaMetrica")
        ley = magnitud(self.u, 8.6, "K:GramoPorTonelada")
        r = t.por(ley)
        self.assertAlmostEqual(r.valor, 21328.0, places=6)
        self.assertEqual(r.dimension, "K:Gramo")

    def test_conversion_a_onzas_troy(self):
        gramos = magnitud(self.u, 21328, "K:Gramo")
        oz = gramos.convertir_a(self.u, "K:OnzaTroy")
        self.assertAlmostEqual(oz.valor, 685.7111, places=3)

    def test_cociente_invierte_exponentes(self):
        masa = magnitud(self.u, 1000, "K:Kilogramo")
        tiempo = magnitud(self.u, 2, "K:Hora")
        r = masa.entre(tiempo)
        caudal = r.convertir_a(self.u, "K:ToneladaPorHora")
        self.assertAlmostEqual(caudal.valor, 0.5, places=6)

    def test_suma_de_unidades_conmensurables_convierte(self):
        """Una tonelada más un kilo son 1001 kg, no 1001 de nada."""
        r = (magnitud(self.u, 1, "K:ToneladaMetrica")
             .mas(magnitud(self.u, 1, "K:Kilogramo")))
        self.assertAlmostEqual(r.convertir_a(self.u, "K:Kilogramo").valor,
                               1001.0, places=6)

    def test_sumar_masa_con_tiempo_falla(self):
        """La prueba que de verdad importa: lo imposible no debe salir."""
        with self.assertRaises(ErrorDimensional) as ctx:
            magnitud(self.u, 1, "K:Gramo").mas(magnitud(self.u, 1, "K:Segundo"))
        self.assertIn("conmensurables", str(ctx.exception))

    def test_convertir_entre_dimensiones_distintas_falla(self):
        with self.assertRaises(ErrorDimensional):
            magnitud(self.u, 1, "K:Gramo").convertir_a(self.u, "K:Segundo")

    def test_magnitud_sin_unidad_es_rechazada(self):
        """Regla del eje N: un número sin unidad no es información."""
        ind = Individual(id="n_suelto", axis=Axis.N, payload={"value": 42})
        with self.assertRaises(ErrorDimensional) as ctx:
            Magnitud.de(self.u, ind)
        self.assertIn("sin unidad", str(ctx.exception))

    def test_division_por_cero_falla(self):
        with self.assertRaises(ErrorDimensional):
            magnitud(self.u, 1, "K:Gramo").entre(magnitud(self.u, 0, "K:Gramo"))


class TestDerivacion(unittest.TestCase):
    def setUp(self):
        self.u = Universe()
        sembrar_si(self.u)
        self.extr = self.u.add_individual(
            Individual(id="extr_001", axis=Axis.O))
        self.u.assert_fact(self.extr, "monto", Individual(
            id="n_2480", axis=Axis.N,
            payload={"value": 2480.0, "unit": "K:ToneladaMetrica"}))
        self.u.assert_fact(self.extr, "ley_mineral", Individual(
            id="n_86", axis=Axis.N,
            payload={"value": 8.6, "unit": "K:GramoPorTonelada"}))

    def _regla(self, expresion="monto * ley_mineral", destino="K:OnzaTroy",
               rid="regla_oro"):
        r = self.u.add_individual(Individual(id=rid, axis=Axis.O))
        self.u.assert_fact(r, "expresion", self.u.add_individual(
            Individual(id=f"expr_{rid}", axis=Axis.K, label=expresion)))
        if destino:
            self.u.assert_fact(r, "unidad_destino", self.u.ind(destino))
        return r

    def test_evaluar_expresion_de_dos_roles(self):
        m = evaluar(self.u, "monto * ley_mineral", self.extr)
        self.assertAlmostEqual(m.valor, 21328.0, places=6)

    def test_derivar_escribe_valor_y_procedencia(self):
        d = self.u.derive(self._regla(), sobre=self.extr,
                          destino_id="prod_oro_001")
        hechos = {f.role: f.value for f in self.u.facts_about(d)}
        self.assertAlmostEqual(hechos["monto"].payload["value"],
                               685.7111, places=3)
        self.assertEqual(hechos["monto"].payload["unit"], "K:OnzaTroy")
        self.assertEqual(hechos["calculado_de"].id, "extr_001")
        self.assertEqual(hechos["justificado_por"].id, "regla_oro")

    def test_regla_sin_unidad_destino_es_rechazada(self):
        r = self._regla(destino=None, rid="regla_muda")
        with self.assertRaises(ErrorDerivacion) as ctx:
            self.u.derive(r, sobre=self.extr, destino_id="x")
        self.assertIn("unidad_destino", str(ctx.exception))

    def test_rol_ausente_en_la_situacion_es_rechazado(self):
        r = self._regla("monto * densidad", rid="regla_densidad")
        with self.assertRaises(ErrorDerivacion) as ctx:
            self.u.derive(r, sobre=self.extr, destino_id="x")
        self.assertIn("densidad", str(ctx.exception))

    def test_unidad_destino_incoherente_es_rechazada(self):
        """Pedir el resultado en segundos cuando salió en gramos."""
        r = self._regla(destino="K:Segundo", rid="regla_absurda")
        with self.assertRaises(ErrorDimensional):
            self.u.derive(r, sobre=self.extr, destino_id="x")

    def test_el_hecho_derivado_no_altera_la_situacion_de_origen(self):
        antes = len(self.u.facts_about(self.extr))
        self.u.derive(self._regla(), sobre=self.extr, destino_id="prod_x")
        self.assertEqual(len(self.u.facts_about(self.extr)), antes)


if __name__ == "__main__":
    unittest.main(verbosity=2)
