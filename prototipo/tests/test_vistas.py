"""Tests del aplanado a tablas (wq/vistas.py).

Correr con: PYTHONPATH=. python3 -m unittest tests.test_vistas -v
"""

from __future__ import annotations
import unittest

from wq import Axis, Individual, Universe, Catalog
from wq.vistas import tabla_plana


def _mini():
    """Universo mínimo: una venta con agente, lugar y clase."""
    u = Universe(catalog=Catalog())
    persona = Individual(id="q1", axis=Axis.Q, label="Ana")
    zona = Individual(id="l1", axis=Axis.L, label="Centro")
    clase = Individual(id="k_venta", axis=Axis.K, label="Venta")
    s = Individual(id="s1", axis=Axis.O, label="Venta #1")
    u.add_individual(s)
    u.assert_fact(s, "instancia_de", clase)
    u.assert_fact(s, "agente", persona)
    u.assert_fact(s, "lugar_de", zona)
    return u, s


class TestTablaPlana(unittest.TestCase):
    def test_una_fila_por_situacion_con_codigos(self):
        u, s = _mini()
        df = tabla_plana(u)
        self.assertEqual(list(df.columns), ["Q", "O", "L", "T", "N", "K"])
        self.assertEqual(len(df), 1)
        fila = df.iloc[0]
        self.assertEqual(fila["O"], "s1")
        self.assertEqual(fila["Q"], "q1")
        self.assertEqual(fila["L"], "l1")
        self.assertEqual(fila["K"], "k_venta")
        self.assertEqual(fila["T"], "")
        self.assertEqual(fila["N"], "")

    def test_multivalor_en_un_eje_se_une_con_punto_y_coma(self):
        u, s = _mini()
        estado = Individual(id="aprobada", axis=Axis.K, label="Aprobada")
        u.assert_fact(s, "estado", estado)  # estado: rol no canónico (política liberal)
        df = tabla_plana(u)
        self.assertEqual(df.iloc[0]["K"], "k_venta; aprobada")


if __name__ == "__main__":
    unittest.main()
