import sqlite3
import unittest

from wq import Individual, Axis, SignatureError, Universe
from meta.catalogo_app import build_catalog
from meta import storage, seed, runtime


class TestCatalogo(unittest.TestCase):
    def test_roles_del_app_registrados(self):
        cat = build_catalog()
        sig = cat.get("tiene_opcion")
        self.assertIsNotNone(sig)
        self.assertEqual(sig.domain, Axis.O)
        self.assertEqual(sig.range, Axis.O)
        self.assertFalse(sig.functional)  # múltiple

        orden = cat.get("orden")
        self.assertEqual(orden.range, Axis.N)
        self.assertTrue(orden.functional)

        # submenu_destino existe y es O->O (no choca con el canónico 'destino' O->L)
        self.assertEqual(cat.get("submenu_destino").range, Axis.O)
        self.assertEqual(cat.get("contenido").range, Axis.K)
        # el canónico 'destino' sigue intacto
        self.assertEqual(cat.get("destino").range, Axis.L)


class TestStorage(unittest.TestCase):
    def _universo_minimo(self):
        cat = build_catalog()
        u = Universe(catalog=cat)
        m = Individual(id="m1", axis=Axis.O, label="Menú")
        o = Individual(id="o1", axis=Axis.O, label="Opción 1")
        u.assert_fact(m, "tiene_opcion", o)
        return u

    def test_storage_roundtrip(self):
        u = self._universo_minimo()
        conn = sqlite3.connect(":memory:")
        storage.save(u, conn)
        u2 = storage.load(conn, build_catalog())
        self.assertEqual(len(u2.individuals), len(u.individuals))
        self.assertEqual(len(u2.facts), len(u.facts))
        valores = [f.value.id for f in u2.facts_about(u2.ind("m1"))
                   if f.role == "tiene_opcion"]
        self.assertEqual(valores, ["o1"])
        self.assertEqual(u2.ind("o1").label, "Opción 1")


def _valores(u, subj_id, rol):
    s = u.ind(subj_id)
    return [f.value for f in u.facts_about(s) if f.role == rol]


def _uno(u, subj_id, rol):
    vs = _valores(u, subj_id, rol)
    return vs[0] if vs else None


def _orden(u, opt):
    n = _uno(u, opt.id, "orden")
    return n.payload["value"] if n and n.payload else 0


class TestSeed(unittest.TestCase):
    def setUp(self):
        self.u = seed.build_universe()

    def test_menu_principal_tres_opciones_ordenadas(self):
        opts = sorted(_valores(self.u, "menu_principal", "tiene_opcion"),
                      key=lambda o: _orden(self.u, o))
        self.assertEqual([o.id for o in opts],
                         ["opt_bienvenida", "opt_config", "opt_salir"])

    def test_config_abre_submenu(self):
        acc = _uno(self.u, "opt_config", "tiene_accion")
        verbo = _uno(self.u, acc.id, "instancia_de")
        self.assertEqual(verbo.id, "abrir_submenu")
        destino = _uno(self.u, acc.id, "submenu_destino")
        self.assertEqual(destino.id, "menu_config")

    def test_submenu_config_dos_opciones(self):
        opts = sorted(_valores(self.u, "menu_config", "tiene_opcion"),
                      key=lambda o: _orden(self.u, o))
        self.assertEqual([o.id for o in opts], ["opt_idioma", "opt_volver"])

    def test_bienvenida_tiene_texto(self):
        acc = _uno(self.u, "opt_bienvenida", "tiene_accion")
        txt = _uno(self.u, acc.id, "contenido")
        self.assertEqual(txt.axis, Axis.K)
        self.assertIn("Bienvenido", txt.label)


class TestSignatura(unittest.TestCase):
    def test_signatura_protege(self):
        u = seed.build_universe()
        k = Individual(id="x_k", axis=Axis.K, label="x")
        menu = u.ind("menu_principal")
        # tiene_opcion espera valor en O; un K debe ser rechazado
        with self.assertRaises(SignatureError):
            u.assert_fact(menu, "tiene_opcion", k)


class TestNavegacion(unittest.TestCase):
    def test_navegacion_completa(self):
        u = seed.build_universe()
        entradas = iter(["1", "2", "2", "3"])  # Bienvenida, Configuración, Volver, Salir
        salida = []
        runtime.run(
            u,
            leer=lambda *_: next(entradas),
            escribir=lambda s: salida.append(str(s)),
        )
        texto = "\n".join(salida)
        self.assertIn("Bienvenido", texto)       # opción 1 mostró el texto
        self.assertIn("Menú principal", texto)    # se mostró el menú principal
        self.assertIn("Idioma", texto)            # el submenú mostró sus opciones

    def test_entrada_invalida_no_rompe(self):
        u = seed.build_universe()
        entradas = iter(["9", "x", "3"])  # fuera de rango, no-número, luego Salir
        salida = []
        runtime.run(
            u,
            leer=lambda *_: next(entradas),
            escribir=lambda s: salida.append(str(s)),
        )
        self.assertIn("inválida", "\n".join(salida).lower())


class TestOpcionSinAccion(unittest.TestCase):
    def test_opcion_sin_accion_no_rompe(self):
        u = Universe(catalog=build_catalog())
        t_menu = Individual(id="menu", axis=Axis.K, label="menu")
        t_opcion = Individual(id="opcion", axis=Axis.K, label="opcion")
        v_salir = Individual(id="salir", axis=Axis.K, label="salir")
        m = Individual(id="m", axis=Axis.O, label="M")
        o_mala = Individual(id="o_mala", axis=Axis.O, label="Sin acción")
        o_salir = Individual(id="o_salir", axis=Axis.O, label="Salir")
        acc_salir = Individual(id="acc_salir", axis=Axis.O, label="acc_salir")
        u.assert_fact(m, "instancia_de", t_menu)
        u.assert_fact(o_mala, "instancia_de", t_opcion)
        u.assert_fact(o_salir, "instancia_de", t_opcion)
        u.assert_fact(acc_salir, "instancia_de", v_salir)
        u.assert_fact(m, "tiene_opcion", o_mala)
        u.assert_fact(m, "tiene_opcion", o_salir)
        u.assert_fact(o_mala, "orden",
                      Individual(id="n_1", axis=Axis.N, label="1", payload={"value": 1}))
        u.assert_fact(o_salir, "orden",
                      Individual(id="n_2", axis=Axis.N, label="2", payload={"value": 2}))
        u.assert_fact(o_salir, "tiene_accion", acc_salir)
        entradas = iter(["1", "2"])  # opción sin acción, luego salir
        salida = []
        runtime.run(u, leer=lambda *_: next(entradas),
                    escribir=lambda s: salida.append(str(s)), menu_inicial="m")
        self.assertIn("opción sin acción", "\n".join(salida).lower())


if __name__ == "__main__":
    unittest.main()
