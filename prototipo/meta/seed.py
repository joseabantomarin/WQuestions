"""Construye el menú meta-driven como hechos WQuestions y los persiste a SQLite."""
import sqlite3

from wq import Universe, Individual, Axis, time_point

from .catalogo_app import build_catalog
from . import storage


def _k(id_, label=None):
    return Individual(id=id_, axis=Axis.K, label=label or id_)


def _o(id_, label=None):
    return Individual(id=id_, axis=Axis.O, label=label or id_)


def _n(value):
    return Individual(id=f"n_{value}", axis=Axis.N, label=str(value),
                      payload={"value": value})


def build_universe() -> Universe:
    u = Universe(catalog=build_catalog())

    # Tipos (K)
    t_menu, t_opcion = _k("menu"), _k("opcion")
    # Verbos-primitiva (K)
    v_texto = _k("mostrar_texto")
    v_sub = _k("abrir_submenu")
    v_volver = _k("volver")
    v_salir = _k("salir")
    # Textos (K) — el texto vive en el label
    txt_bien = _k("txt_bienvenida",
                  "¡Bienvenido a la demo meta-driven de WQuestions!")
    txt_idioma = _k("txt_idioma", "Idioma actual: español (es).")
    # Menús (O)
    m_main = _o("menu_principal", "Menú principal")
    m_cfg = _o("menu_config", "Configuración")
    # Opciones (O)
    opt_bien = _o("opt_bienvenida", "Bienvenida")
    opt_cfg = _o("opt_config", "Configuración")
    opt_salir = _o("opt_salir", "Salir")
    opt_idioma = _o("opt_idioma", "Idioma")
    opt_volver = _o("opt_volver", "Volver")
    # Acciones (O)
    acc_bien = _o("acc_bienvenida")
    acc_abrir = _o("acc_abrir_config")
    acc_salir = _o("acc_salir")
    acc_idioma = _o("acc_idioma")
    acc_volver = _o("acc_volver")

    def inst(o, k):
        u.assert_fact(o, "instancia_de", k)

    inst(m_main, t_menu)
    inst(m_cfg, t_menu)
    for o in (opt_bien, opt_cfg, opt_salir, opt_idioma, opt_volver):
        inst(o, t_opcion)
    inst(acc_bien, v_texto)
    inst(acc_abrir, v_sub)
    inst(acc_salir, v_salir)
    inst(acc_idioma, v_texto)
    inst(acc_volver, v_volver)

    # Menú principal y submenú: opciones + orden
    for opt, orden in [(opt_bien, 1), (opt_cfg, 2), (opt_salir, 3)]:
        u.assert_fact(m_main, "tiene_opcion", opt)
        u.assert_fact(opt, "orden", _n(orden))
    for opt, orden in [(opt_idioma, 1), (opt_volver, 2)]:
        u.assert_fact(m_cfg, "tiene_opcion", opt)
        u.assert_fact(opt, "orden", _n(orden))

    # Opción → acción
    for opt, acc in [(opt_bien, acc_bien), (opt_cfg, acc_abrir),
                     (opt_salir, acc_salir), (opt_idioma, acc_idioma),
                     (opt_volver, acc_volver)]:
        u.assert_fact(opt, "tiene_accion", acc)

    # Parámetros de las acciones
    u.assert_fact(acc_bien, "contenido", txt_bien)
    u.assert_fact(acc_idioma, "contenido", txt_idioma)
    u.assert_fact(acc_abrir, "submenu_destino", m_cfg)

    # --- Rama Ventas (permanente) ---
    v_form = _k("abrir_formulario"); v_grilla = _k("abrir_grilla")

    # tipo de entidad + meta-tipo de campo + tipos de dato (K)
    venta = _k("venta", "Venta"); campo = _k("campo")
    t_texto = _k("texto"); t_numero = _k("numero"); t_fecha = _k("fecha")
    t_ref = _k("referencia")
    k_cliente = _k("cliente"); k_producto = _k("producto")  # tipos de entidad

    # esquema de venta: 4 campos (descriptores O)
    def _campo(cid, etiqueta, tipo_k, orden, rol_k, ref_k=None):
        c = _o(cid, etiqueta)
        u.assert_fact(c, "instancia_de", campo)
        u.assert_fact(venta, "tiene_campo", c)
        u.assert_fact(c, "tipo_dato", tipo_k)
        u.assert_fact(c, "orden", _n(orden))
        u.assert_fact(c, "rol", rol_k)
        if ref_k is not None:
            u.assert_fact(c, "referencia_a", ref_k)
        return c
    _campo("campo_fecha",    "Fecha",    t_fecha,  1, t_fecha)
    _campo("campo_cliente",  "Cliente",  t_ref,    2, k_cliente, k_cliente)
    _campo("campo_producto", "Producto", t_ref,    3, k_producto, k_producto)
    _campo("campo_monto",    "Monto",    t_numero, 4, _k("monto"))

    # entidades compartidas: clientes en Q, productos en O (instancia_de via V→K)
    ana = Individual(id="ana", axis=Axis.Q, label="Ana")
    beto = Individual(id="beto", axis=Axis.Q, label="Beto")
    laptop = _o("laptop", "Laptop"); mouse = _o("mouse", "Mouse")
    for ent, tipo in [(ana, k_cliente), (beto, k_cliente),
                      (laptop, k_producto), (mouse, k_producto)]:
        u.assert_fact(ent, "instancia_de", tipo)

    # registros de ejemplo
    def _venta(vid, fecha_iso, cli, prod, monto):
        r = _o(vid, vid)
        u.assert_fact(r, "instancia_de", venta)
        u.assert_fact(r, "fecha", time_point(fecha_iso))
        u.assert_fact(r, "cliente", cli)
        u.assert_fact(r, "producto", prod)
        u.assert_fact(r, "monto", _n(monto))
    _venta("venta_001", "2026-06-01", ana, laptop, 120)
    _venta("venta_002", "2026-06-02", beto, mouse, 25)

    # opción "Ventas" en el menú principal + submenú
    m_ventas = _o("menu_ventas", "Ventas")
    opt_ventas = _o("opt_ventas", "Ventas"); acc_abrir_ventas = _o("acc_abrir_ventas")
    u.assert_fact(opt_ventas, "instancia_de", t_opcion)
    u.assert_fact(m_main, "tiene_opcion", opt_ventas)
    u.assert_fact(opt_ventas, "orden", _n(2.5))   # entre Configuración(2) y Salir(3)
    u.assert_fact(opt_ventas, "tiene_accion", acc_abrir_ventas)
    u.assert_fact(acc_abrir_ventas, "instancia_de", v_sub)
    u.assert_fact(acc_abrir_ventas, "submenu_destino", m_ventas)
    u.assert_fact(m_ventas, "instancia_de", t_menu)

    opt_reg = _o("opt_registro", "Registro"); acc_reg = _o("acc_registro")
    opt_con = _o("opt_consulta", "Consulta"); acc_con = _o("acc_consulta")
    opt_volv = _o("opt_volver_ventas", "Volver"); acc_volv = _o("acc_volver_ventas")
    for o in (opt_reg, opt_con, opt_volv):
        u.assert_fact(o, "instancia_de", t_opcion)
    for o, n in ((opt_reg, 1), (opt_con, 2), (opt_volv, 3)):
        u.assert_fact(m_ventas, "tiene_opcion", o)
        u.assert_fact(o, "orden", _n(n))
    u.assert_fact(opt_reg, "tiene_accion", acc_reg)
    u.assert_fact(acc_reg, "instancia_de", v_form)
    u.assert_fact(acc_reg, "sobre_tipo", venta)
    u.assert_fact(opt_con, "tiene_accion", acc_con)
    u.assert_fact(acc_con, "instancia_de", v_grilla)
    u.assert_fact(acc_con, "sobre_tipo", venta)
    u.assert_fact(opt_volv, "tiene_accion", acc_volv)
    u.assert_fact(acc_volv, "instancia_de", v_volver)

    return u


def seed(conn) -> None:
    """Construye el universo del menú y lo persiste en `conn`."""
    storage.save(build_universe(), conn)


def abrir_universo(db_path):
    """Abre la BD SQLite; si está vacía la siembra; devuelve (conn, universe)."""
    conn = sqlite3.connect(db_path)
    storage.init_db(conn)
    vacio = conn.execute("SELECT COUNT(*) FROM hechos").fetchone()[0] == 0
    if vacio:
        seed(conn)
    u = storage.load(conn, build_catalog())
    return conn, u
