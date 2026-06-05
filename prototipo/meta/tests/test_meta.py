import sqlite3
import unittest

from wq import Individual, Axis, SignatureError, Universe
from meta.catalogo_app import build_catalog
from meta import storage, seed, runtime
from meta.engine import MenuSession


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


    def test_roles_de_entidad_registrados(self):
        cat = build_catalog()
        self.assertEqual(cat.get("tiene_campo").domain, Axis.K)
        self.assertEqual(cat.get("tiene_campo").range, Axis.O)
        self.assertFalse(cat.get("tiene_campo").functional)
        self.assertEqual(cat.get("sobre_tipo").range, Axis.K)
        self.assertEqual(cat.get("tipo_dato").range, Axis.K)
        self.assertEqual(cat.get("rol").range, Axis.K)
        self.assertEqual(cat.get("referencia_a").range, Axis.K)


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


class TestAbrirUniverso(unittest.TestCase):
    def test_siembra_y_carga(self):
        import tempfile, os
        db = os.path.join(tempfile.mkdtemp(), "menu.db")
        conn, u = seed.abrir_universo(db)
        try:
            self.assertEqual(u.ind("menu_principal").label, "Menú principal")
        finally:
            conn.close()


class TestMenuSession(unittest.TestCase):
    def setUp(self):
        self.u = seed.build_universe()

    def test_estado_menu_principal(self):
        e = MenuSession(self.u).estado()
        self.assertEqual(e["titulo"], "Menú principal")
        self.assertFalse(e["es_submenu"])
        self.assertEqual([o["label"] for o in e["opciones"]],
                         ["Bienvenida", "Configuración", "Salir"])

    def test_seleccionar_texto(self):
        r = MenuSession(self.u).seleccionar(1)
        self.assertEqual(r["efecto"]["tipo"], "texto")
        self.assertIn("Bienvenido", r["efecto"]["contenido"])

    def test_seleccionar_abre_y_vuelve(self):
        s = MenuSession(self.u)
        r = s.seleccionar(2)  # Configuración
        self.assertEqual(r["efecto"]["tipo"], "navegado")
        self.assertTrue(r["estado"]["es_submenu"])
        self.assertEqual(r["estado"]["titulo"], "Configuración")
        r2 = s.seleccionar(2)  # Volver
        self.assertEqual(r2["efecto"]["tipo"], "navegado")
        self.assertFalse(r2["estado"]["es_submenu"])

    def test_seleccionar_salir(self):
        r = MenuSession(self.u).seleccionar(3)
        self.assertEqual(r["efecto"]["tipo"], "salir")
        self.assertTrue(r["estado"]["terminada"])

    def test_indice_invalido(self):
        self.assertEqual(MenuSession(self.u).seleccionar(99)["efecto"]["tipo"], "invalido")

    def test_tripletas_visibles_incluye_opciones(self):
        trips = MenuSession(self.u).tripletas_visibles()
        pares = {(t["sujeto"], t["rol"], t["valor"]) for t in trips}
        self.assertIn(("menu_principal", "tiene_opcion", "opt_bienvenida"), pares)
        self.assertIn(("opt_bienvenida", "orden", "n_1"), pares)


class TestSeedVentas(unittest.TestCase):
    def setUp(self):
        self.u = seed.build_universe()

    def test_menu_principal_incluye_ventas(self):
        opts = [f.value.label for f in self.u.facts_about(self.u.ind("menu_principal"))
                if f.role == "tiene_opcion"]
        self.assertIn("Ventas", opts)

    def test_esquema_venta_cuatro_campos(self):
        campos = [f.value for f in self.u.facts_about(self.u.ind("venta"))
                  if f.role == "tiene_campo"]
        roles = set()
        for c in campos:
            rol = [f.value for f in self.u.facts_about(c) if f.role == "rol"][0]
            roles.add(rol.id)
        self.assertEqual(roles, {"fecha", "cliente", "producto", "monto"})

    def test_cliente_es_agente_Q_clasificado(self):
        ana = self.u.ind("ana")
        self.assertEqual(ana.axis, Axis.Q)
        tipos = [f.value.id for f in self.u.facts_about(ana) if f.role == "instancia_de"]
        self.assertIn("cliente", tipos)

    def test_hay_registros_de_ejemplo(self):
        ventas = [f.subject for f in self.u.facts_with_value(self.u.ind("venta"))
                  if f.role == "instancia_de"]
        self.assertGreaterEqual(len(ventas), 2)


if __name__ == "__main__":
    unittest.main()
