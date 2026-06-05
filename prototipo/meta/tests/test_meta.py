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

    def test_roles_de_maestros_registrados(self):
        cat = build_catalog()
        self.assertEqual(cat.get("eje_instancia").domain, Axis.K)
        self.assertEqual(cat.get("eje_instancia").range, Axis.K)
        self.assertEqual(cat.get("campo_etiqueta").domain, Axis.K)
        self.assertEqual(cat.get("campo_etiqueta").range, Axis.O)


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
                         ["opt_bienvenida", "opt_config", "opt_menu_ventas",
                          "opt_menu_compras", "opt_menu_maestros", "opt_salir"])

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
        entradas = iter(["1", "2", "2", "6"])  # Bienvenida, Configuración, Volver, Salir
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
        entradas = iter(["9", "x", "6"])  # fuera de rango, no-número, luego Salir
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
                         ["Bienvenida", "Configuración", "Ventas", "Compras", "Maestros", "Salir"])

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
        r = MenuSession(self.u).seleccionar(6)
        self.assertEqual(r["efecto"]["tipo"], "salir")
        self.assertTrue(r["estado"]["terminada"])

    def test_indice_invalido(self):
        self.assertEqual(MenuSession(self.u).seleccionar(99)["efecto"]["tipo"], "invalido")

    def test_tripletas_visibles_incluye_opciones(self):
        trips = MenuSession(self.u).tripletas_visibles()
        pares = {(t["sujeto"], t["rol"], t["valor"]) for t in trips}
        self.assertIn(("menu_principal", "tiene_opcion", "opt_bienvenida"), pares)
        self.assertIn(("opt_bienvenida", "orden", "n_1"), pares)


from meta import engine as _engine


class TestGuardarGeneralizado(unittest.TestCase):
    def _mini(self):
        from wq import Universe, Individual, Axis
        from meta.catalogo_app import build_catalog
        u = Universe(catalog=build_catalog())

        def K(i, l=None):
            ind = Individual(id=i, axis=Axis.K, label=l or i); u.add_individual(ind); return ind

        def O(i, l=None):
            ind = Individual(id=i, axis=Axis.O, label=l or i); u.add_individual(ind); return ind

        def N(v):
            ind = Individual(id=f"n_{v}", axis=Axis.N, label=str(v), payload={"value": v}); u.add_individual(ind); return ind

        persona = K("persona", "Persona"); campo = K("campo"); texto = K("texto"); eje_q = K("eje_q", "Q")
        cn = O("campo_persona_nombre", "Nombre")
        u.assert_fact(cn, "instancia_de", campo)
        u.assert_fact(persona, "tiene_campo", cn)
        u.assert_fact(cn, "tipo_dato", texto)
        u.assert_fact(cn, "orden", N(1))
        u.assert_fact(cn, "rol", K("nombre"))
        u.assert_fact(persona, "eje_instancia", eje_q)
        u.assert_fact(persona, "campo_etiqueta", cn)
        return u

    def test_guardar_usa_eje_instancia_y_campo_etiqueta(self):
        u = self._mini()
        rid = _engine.guardar(u, "persona", {"nombre": "Ana"})
        reg = u.ind(rid)
        self.assertEqual(reg.axis, Axis.Q)      # eje_instancia → Q
        self.assertEqual(reg.label, "Ana")      # campo_etiqueta → "Ana"

    def test_guardar_default_axis_O_sin_eje_instancia(self):
        u = self._mini()
        # un tipo sin eje_instancia ni campo_etiqueta → O y label genérico
        from wq import Individual, Axis
        cosa = Individual(id="cosa", axis=Axis.K, label="Cosa"); u.add_individual(cosa)
        rid = _engine.guardar(u, "cosa", {})
        self.assertEqual(u.ind(rid).axis, Axis.O)


class TestEntidad(unittest.TestCase):
    def setUp(self):
        self.u = seed.build_universe()

    def test_campos_ordenados(self):
        campos = _engine._campos(self.u, self.u.ind("venta"))
        self.assertEqual([c["rol"] for c in campos],
                         ["fecha", "cliente", "producto", "monto"])
        self.assertEqual(campos[1]["tipo"], "referencia")
        self.assertEqual(campos[1]["referencia_a"], "persona")

    def test_opciones_ref_lista_personas(self):
        ops = _engine._opciones_ref(self.u, "persona")
        self.assertEqual({o["id"] for o in ops}, {"ana", "beto"})

    def test_efecto_grilla_tiene_filas_legibles(self):
        ef = _engine.efecto_grilla(self.u, self.u.ind("venta"), "Consulta")
        self.assertEqual(ef["tipo"], "grilla")
        self.assertEqual({c["rol"] for c in ef["columnas"]},
                         {"fecha", "cliente", "producto", "monto"})
        fila = next(f for f in ef["filas"] if f["id"] == "venta_001")
        self.assertEqual(fila["valores"]["cliente"], "Ana")
        self.assertEqual(fila["valores"]["producto"], "Laptop")

    def test_guardar_crea_y_comparte_referencia(self):
        rid = _engine.guardar(self.u, "venta",
                              {"fecha": "2026-06-03", "cliente": "ana",
                               "producto": "mouse", "monto": "300"})
        # el cliente referenciado es el MISMO individuo ana (compartido)
        cli = [f.value for f in self.u.facts_about(self.u.ind(rid))
               if f.role == "cliente"][-1]
        self.assertEqual(cli.id, "ana")
        self.assertEqual(cli.axis, Axis.Q)

    def test_guardar_actualiza_ultimo_gana(self):
        _engine.guardar(self.u, "venta", {"monto": "999"}, registro_id="venta_001")
        ef = _engine.efecto_grilla(self.u, self.u.ind("venta"), "Consulta")
        fila = next(f for f in ef["filas"] if f["id"] == "venta_001")
        self.assertEqual(fila["valores"]["monto"], "999")

    def test_efecto_formulario_precargado(self):
        ef = _engine.efecto_formulario(self.u, self.u.ind("venta"), "Editar",
                                       registro_id="venta_001")
        self.assertEqual(ef["valores"]["cliente"], "ana")   # id para el select
        self.assertEqual(ef["valores"]["monto"], 120)
        campo_cli = next(c for c in ef["campos"] if c["rol"] == "cliente")
        self.assertIn({"id": "ana", "label": "Ana"}, campo_cli["opciones"])


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
        self.assertIn("persona", tipos)

    def test_hay_registros_de_ejemplo(self):
        ventas = [f.subject for f in self.u.facts_with_value(self.u.ind("venta"))
                  if f.role == "instancia_de"]
        self.assertGreaterEqual(len(ventas), 2)


class TestMaestrosCompras(unittest.TestCase):
    def setUp(self):
        self.u = seed.build_universe()

    def test_persona_es_Q_clasificada_con_nombre(self):
        ana = self.u.ind("ana")
        self.assertEqual(ana.axis, Axis.Q)
        tipos = [f.value.id for f in self.u.facts_about(ana) if f.role == "instancia_de"]
        self.assertIn("persona", tipos)

    def test_eje_instancia_persona_es_Q(self):
        ax = _engine._uno(self.u, self.u.ind("persona"), "eje_instancia")
        self.assertEqual(ax.label, "Q")

    def test_guardar_persona_crea_en_Q_con_label(self):
        rid = _engine.guardar(self.u, "persona", {"nombre": "Caro"})
        reg = self.u.ind(rid)
        self.assertEqual(reg.axis, Axis.Q)
        self.assertEqual(reg.label, "Caro")

    def test_guardar_producto_con_precio(self):
        rid = _engine.guardar(self.u, "producto",
                              {"nombre_producto": "Teclado", "precio": "50"})
        reg = self.u.ind(rid)
        self.assertEqual(reg.axis, Axis.O)
        self.assertEqual(reg.label, "Teclado")
        precio = [f.value for f in self.u.facts_about(reg) if f.role == "precio"][-1]
        self.assertEqual(precio.axis, Axis.N)

    def test_compra_referencia_persona_y_producto(self):
        campos = _engine._campos(self.u, self.u.ind("compra"))
        prov = next(c for c in campos if c["rol"] == "proveedor")
        self.assertEqual(prov["referencia_a"], "persona")

    def test_persona_compartida_cliente_y_proveedor(self):
        # ana es proveedor en compra_001 (seed) y la usamos como cliente en una venta
        vid = _engine.guardar(self.u, "venta",
                              {"fecha": "2026-06-05", "cliente": "ana",
                               "producto": "laptop", "monto": "300"})
        cli = [f.value for f in self.u.facts_about(self.u.ind(vid)) if f.role == "cliente"][-1]
        prov = [f.value for f in self.u.facts_about(self.u.ind("compra_001")) if f.role == "proveedor"][-1]
        self.assertEqual(cli.id, prov.id)   # mismo individuo persona

    def test_menu_principal_incluye_compras_y_maestros(self):
        opts = [f.value.label for f in self.u.facts_about(self.u.ind("menu_principal"))
                if f.role == "tiene_opcion"]
        self.assertIn("Compras", opts)
        self.assertIn("Maestros", opts)

    def test_maestros_tiene_personas_y_productos(self):
        opts = [f.value.label for f in self.u.facts_about(self.u.ind("menu_maestros"))
                if f.role == "tiene_opcion"]
        self.assertIn("Personas", opts)
        self.assertIn("Productos", opts)


if __name__ == "__main__":
    unittest.main()
