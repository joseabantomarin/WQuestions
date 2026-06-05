import sqlite3
import unittest

from wq import Individual, Axis, SignatureError
from meta.catalogo_app import build_catalog


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


from meta import storage


class TestStorage(unittest.TestCase):
    def _universo_minimo(self):
        from wq import Universe
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


from meta import seed


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
