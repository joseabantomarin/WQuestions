"""Tests del aplanado a tablas (wq/vistas.py).

Correr con: PYTHONPATH=. python3 -m unittest tests.test_vistas -v
"""

from __future__ import annotations
import unittest

from wq import Axis, Individual, Universe, Catalog
from wq.vistas import tabla_plana, proyeccion, pivote


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


class TestProyeccion(unittest.TestCase):
    def test_resuelve_etiquetas_y_subject(self):
        u, s = _mini()
        cols = [("Cliente (Q)", "agente"),
                ("Operación (O)", "_subject"),
                ("Zona (L)", "lugar_de")]
        df = proyeccion(u, cols)
        self.assertEqual(list(df.columns),
                         ["Cliente (Q)", "Operación (O)", "Zona (L)"])
        self.assertEqual(df.iloc[0].tolist(), ["Ana", "Venta #1", "Centro"])

    def test_rol_ausente_queda_vacio(self):
        u, s = _mini()
        df = proyeccion(u, [("Costo (N)", "monto")])
        self.assertEqual(df.iloc[0]["Costo (N)"], "")

    def test_filtro_k_recorta(self):
        u, s = _mini()
        s2 = Individual(id="s2", axis=Axis.O, label="Compra #1")
        u.add_individual(s2)
        u.assert_fact(s2, "instancia_de",
                      Individual(id="k_compra", axis=Axis.K, label="Compra"))
        df = proyeccion(u, [("Op (O)", "_subject")], filtro_k="k_venta")
        self.assertEqual(df["Op (O)"].tolist(), ["Venta #1"])

    def test_subjects_explicito_respeta_orden(self):
        u, s = _mini()
        s2 = Individual(id="s2", axis=Axis.O, label="Compra #1")
        u.add_individual(s2)
        u.assert_fact(s2, "instancia_de",
                      Individual(id="k_compra", axis=Axis.K, label="Compra"))
        df = proyeccion(u, [("Op (O)", "_subject")], subjects=[s2, s])
        self.assertEqual(df["Op (O)"].tolist(), ["Compra #1", "Venta #1"])


class TestPivote(unittest.TestCase):
    def _cruce(self):
        u = Universe(catalog=Catalog())
        kA = Individual(id="kA", axis=Axis.K, label="A")
        kB = Individual(id="kB", axis=Axis.K, label="B")
        lx = Individual(id="lx", axis=Axis.L, label="X")
        ly = Individual(id="ly", axis=Axis.L, label="Y")

        def sit(i, k, l):
            s = Individual(id=f"s{i}", axis=Axis.O, label=f"s{i}")
            u.add_individual(s)
            u.assert_fact(s, "instancia_de", k)
            u.assert_fact(s, "lugar_de", l)
            return s

        sit(1, kA, lx)
        sit(2, kA, lx)
        sit(3, kA, ly)
        sit(4, kB, lx)
        return u

    def test_cuenta_el_cruce_k_por_l(self):
        u = self._cruce()
        df = pivote(u, orden_filas=["kA", "kB"], orden_cols=["lx", "ly"])
        self.assertEqual(int(df.loc["A", "X"]), 2)
        self.assertEqual(int(df.loc["A", "Y"]), 1)
        self.assertEqual(int(df.loc["B", "X"]), 1)
        self.assertEqual(int(df.loc["B", "Y"]), 0)

    def test_resolver_l_a_zona_sube_por_dentro_de(self):
        u = Universe(catalog=Catalog())
        k = Individual(id="k", axis=Axis.K, label="K")
        zona = Individual(id="zona", axis=Axis.L, label="Zona")
        calle = Individual(id="calle", axis=Axis.L, label="Calle 1")
        u.add_individual(zona)
        u.add_individual(calle)
        u.assert_fact(calle, "dentro_de", zona)
        s = Individual(id="s1", axis=Axis.O, label="s1")
        u.add_individual(s)
        u.assert_fact(s, "instancia_de", k)
        u.assert_fact(s, "lugar_de", calle)
        df = pivote(u, orden_filas=["k"], orden_cols=["zona"],
                    resolver_l_a_zona=True)
        self.assertEqual(int(df.loc["K", "Zona"]), 1)


if __name__ == "__main__":
    unittest.main()
