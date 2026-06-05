"""Construye el menú meta-driven como hechos WQuestions y los persiste a SQLite."""
import sqlite3

from wq import Universe, Individual, Axis

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
