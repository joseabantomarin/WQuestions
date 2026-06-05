"""Construye el menú meta-driven como hechos WQuestions y los persiste a SQLite."""
import sqlite3

from wq import Universe, Individual, Axis, time_point

from .catalogo_app import build_catalog, registrar_firmas_de_esquema
from . import storage
from .engine import literal_texto


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

    # --- Verbos de pantalla + tipos de dato + meta-tipo campo + ejes ---
    v_form = _k("abrir_formulario"); v_grilla = _k("abrir_grilla")
    campo = _k("campo")
    t_texto = _k("texto"); t_numero = _k("numero"); t_fecha = _k("fecha"); t_ref = _k("referencia")
    eje_q = _k("eje_q", "Q"); eje_o = _k("eje_o", "O")

    def _campo(tipo, cid, etiqueta, tipo_k, orden, rol_k, ref_k=None):
        c = _o(cid, etiqueta)
        u.assert_fact(c, "instancia_de", campo)
        u.assert_fact(tipo, "tiene_campo", c)
        u.assert_fact(c, "tipo_dato", tipo_k)
        u.assert_fact(c, "orden", _n(orden))
        u.assert_fact(c, "rol", rol_k)
        if ref_k is not None:
            u.assert_fact(c, "referencia_a", ref_k)
        return c

    # --- Tipos de entidad ---
    persona = _k("persona", "Persona"); producto = _k("producto", "Producto")
    venta = _k("venta", "Venta"); compra = _k("compra", "Compra")
    u.assert_fact(persona, "eje_instancia", eje_q)
    u.assert_fact(producto, "eje_instancia", eje_o)
    # venta/compra sin eje_instancia → default O en guardar

    # esquemas (campos como datos)
    cp_nombre = _campo(persona, "campo_persona_nombre", "Nombre", t_texto, 1, _k("nombre"))
    u.assert_fact(persona, "campo_etiqueta", cp_nombre)

    cpr_nombre = _campo(producto, "campo_producto_nombre", "Nombre", t_texto, 1, _k("nombre_producto"))
    _campo(producto, "campo_producto_precio", "Precio", t_numero, 2, _k("precio"))
    u.assert_fact(producto, "campo_etiqueta", cpr_nombre)

    _campo(venta, "campo_venta_fecha", "Fecha", t_fecha, 1, t_fecha)
    _campo(venta, "campo_venta_cliente", "Cliente", t_ref, 2, _k("cliente"), persona)
    _campo(venta, "campo_venta_producto", "Producto", t_ref, 3, producto, producto)
    _campo(venta, "campo_venta_monto", "Monto", t_numero, 4, _k("monto"))
    _campo(venta, "campo_venta_documento", "Documento", t_texto, 5, _k("documento"))

    _campo(compra, "campo_compra_fecha", "Fecha", t_fecha, 1, t_fecha)
    _campo(compra, "campo_compra_proveedor", "Proveedor", t_ref, 2, _k("proveedor"), persona)
    _campo(compra, "campo_compra_producto", "Producto", t_ref, 3, producto, producto)
    _campo(compra, "campo_compra_monto", "Monto", t_numero, 4, _k("monto"))

    # --- Entidades maestras compartidas ---
    ana = Individual(id="ana", axis=Axis.Q, label="Ana")
    beto = Individual(id="beto", axis=Axis.Q, label="Beto")
    laptop = _o("laptop", "Laptop"); mouse = _o("mouse", "Mouse")
    for p, nom in [(ana, "Ana"), (beto, "Beto")]:
        u.assert_fact(p, "instancia_de", persona)
        u.assert_fact(p, "nombre", literal_texto(nom))
    for pr, nom, pre in [(laptop, "Laptop", 1200), (mouse, "Mouse", 25)]:
        u.assert_fact(pr, "instancia_de", producto)
        u.assert_fact(pr, "nombre_producto", literal_texto(nom))
        u.assert_fact(pr, "precio", _n(pre))

    # --- Registros de ejemplo ---
    def _registro(tipo, rid, **rol_valor):
        r = _o(rid, rid)
        u.assert_fact(r, "instancia_de", tipo)
        for rol, val in rol_valor.items():
            u.assert_fact(r, rol, val)
        return r
    _registro(venta, "venta_001", fecha=time_point("2026-06-01"), cliente=ana, producto=laptop, monto=_n(120))
    _registro(venta, "venta_002", fecha=time_point("2026-06-02"), cliente=beto, producto=mouse, monto=_n(25))
    _registro(compra, "compra_001", fecha=time_point("2026-05-20"), proveedor=ana, producto=laptop, monto=_n(900))

    # --- Menús: Ventas, Compras, Maestros(Personas/Productos) ---
    def _submenu(mid, label, orden_en_padre, padre):
        m = _o(mid, label)
        u.assert_fact(m, "instancia_de", t_menu)
        opt = _o(f"opt_{mid}", label); acc = _o(f"acc_open_{mid}")
        u.assert_fact(opt, "instancia_de", t_opcion)
        u.assert_fact(padre, "tiene_opcion", opt)
        u.assert_fact(opt, "orden", _n(orden_en_padre))
        u.assert_fact(opt, "tiene_accion", acc)
        u.assert_fact(acc, "instancia_de", v_sub)
        u.assert_fact(acc, "submenu_destino", m)
        return m

    def _opcion(menu, oid, label, orden, verbo, **extra):
        opt = _o(oid, label); acc = _o(f"acc_{oid}")
        u.assert_fact(opt, "instancia_de", t_opcion)
        u.assert_fact(menu, "tiene_opcion", opt)
        u.assert_fact(opt, "orden", _n(orden))
        u.assert_fact(opt, "tiene_accion", acc)
        u.assert_fact(acc, "instancia_de", verbo)
        for rol, val in extra.items():
            u.assert_fact(acc, rol, val)
        return opt

    def _pantallas(menu_padre, mid, label, orden_padre, tipo):
        m = _submenu(mid, label, orden_padre, menu_padre)
        _opcion(m, f"opt_{mid}_reg", "Registro", 1, v_form, sobre_tipo=tipo)
        _opcion(m, f"opt_{mid}_con", "Consulta", 2, v_grilla, sobre_tipo=tipo)
        _opcion(m, f"opt_{mid}_vol", "Volver", 3, v_volver)
        return m

    _pantallas(m_main, "menu_ventas", "Ventas", 2.5, venta)
    _pantallas(m_main, "menu_compras", "Compras", 2.6, compra)
    m_maestros = _submenu("menu_maestros", "Maestros", 2.7, m_main)
    _pantallas(m_maestros, "menu_personas", "Personas", 1, persona)
    _pantallas(m_maestros, "menu_productos", "Productos", 2, producto)
    _opcion(m_maestros, "opt_maestros_vol", "Volver", 3, v_volver)

    registrar_firmas_de_esquema(u)
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
    registrar_firmas_de_esquema(u)
    return conn, u
