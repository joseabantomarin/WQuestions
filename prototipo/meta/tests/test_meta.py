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
