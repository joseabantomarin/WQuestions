"""Motor headless del menú meta-driven: MenuSession.

Toda la lógica de navegación vive aquí, una sola vez. Los handlers devuelven un
efecto (no imprimen) y mutan el stack. CLI y web son pieles delgadas sobre este motor.
"""
from wq import Individual, Axis, mint_id, time_point


def _valores(u, subj, rol):
    return [f.value for f in u.facts_about(subj) if f.role == rol]


def _uno(u, subj, rol):
    vs = _valores(u, subj, rol)
    return vs[0] if vs else None


def _orden(u, opt):
    n = _uno(u, opt, "orden")
    return n.payload["value"] if n is not None and n.payload else 0


def _opciones(u, menu):
    return sorted(_valores(u, menu, "tiene_opcion"), key=lambda o: _orden(u, o))


def _ultimo(u, subj, rol):
    vals = [f.value for f in u.facts_about(subj) if f.role == rol]
    return vals[-1] if vals else None


def _campos(u, tipo):
    campos = sorted(_valores(u, tipo, "tiene_campo"), key=lambda c: _orden(u, c))
    out = []
    for c in campos:
        td = _uno(u, c, "tipo_dato")
        rol = _uno(u, c, "rol")
        ref = _uno(u, c, "referencia_a")
        out.append({
            "campo": c.id,
            "rol": rol.id if rol is not None else c.id,
            "etiqueta": c.label,
            "tipo": td.id if td is not None else "texto",
            "orden": _orden(u, c),
            "referencia_a": ref.id if ref is not None else None,
        })
    return out


def _instancias(u, tipo):
    return [f.subject for f in u.facts_with_value(tipo) if f.role == "instancia_de"]


def _opciones_ref(u, tipo_id):
    return [{"id": o.id, "label": o.label} for o in _instancias(u, u.ind(tipo_id))]


def _valor_display(u, reg, rol):
    v = _ultimo(u, reg, rol)
    return v.label if v is not None else ""


def _valor_raw(u, reg, campo):
    v = _ultimo(u, reg, campo["rol"])
    if v is None:
        return ""
    if campo["tipo"] == "referencia":
        return v.id
    if campo["tipo"] == "numero":
        return (v.payload or {}).get("value", v.label)
    return v.label  # fecha (iso) / texto


def efecto_formulario(u, tipo, titulo, registro_id=None):
    campos = _campos(u, tipo)
    for c in campos:
        if c["tipo"] == "referencia" and c["referencia_a"]:
            c["opciones"] = _opciones_ref(u, c["referencia_a"])
    valores = {}
    if registro_id:
        reg = u.ind(registro_id)
        for c in campos:
            valores[c["rol"]] = _valor_raw(u, reg, c)
    return {"tipo": "formulario", "titulo": titulo, "entidad": tipo.id,
            "campos": campos, "registro_id": registro_id, "valores": valores}


def efecto_grilla(u, tipo, titulo):
    campos = _campos(u, tipo)
    columnas = [{"rol": c["rol"], "etiqueta": c["etiqueta"]} for c in campos]
    filas = []
    for reg in _instancias(u, tipo):
        valores = {c["rol"]: _valor_display(u, reg, c["rol"]) for c in campos}
        filas.append({"id": reg.id, "valores": valores})
    return {"tipo": "grilla", "titulo": titulo, "entidad": tipo.id,
            "columnas": columnas, "filas": filas}


def guardar(u, tipo_id, valores, registro_id=None):
    tipo = u.ind(tipo_id)
    campos = _campos(u, tipo)
    if registro_id:
        reg = u.ind(registro_id)
    else:
        ax = _uno(u, tipo, "eje_instancia")
        axis = Axis(ax.label) if ax is not None else Axis.O
        etq = _uno(u, tipo, "campo_etiqueta")
        label = f"{tipo_id} nuevo"
        if etq is not None:
            rol_etq_ind = _uno(u, etq, "rol")
            rol_etq = rol_etq_ind.id if rol_etq_ind is not None else etq.id
            label = str(valores.get(rol_etq, label))
        reg = Individual(id=mint_id(tipo_id), axis=axis, label=label)
        u.assert_fact(reg, "instancia_de", tipo)
    for c in campos:
        raw = valores.get(c["rol"])
        if raw is None or raw == "":
            continue
        if c["tipo"] == "referencia":
            valor = u.ind(raw)                       # individuo existente (compartido)
        elif c["tipo"] == "numero":
            valor = Individual(id=mint_id("n"), axis=Axis.N, label=str(raw),
                               payload={"value": float(raw)})
        elif c["tipo"] == "fecha":
            valor = time_point(str(raw))
        else:
            valor = Individual(id=mint_id("k"), axis=Axis.K, label=str(raw))
        u.assert_fact(reg, c["rol"], valor)
    return reg.id


def _h_abrir_formulario(sess, accion):
    tipo = _uno(sess.u, accion, "sobre_tipo")
    return efecto_formulario(sess.u, tipo, None)


def _h_abrir_grilla(sess, accion):
    tipo = _uno(sess.u, accion, "sobre_tipo")
    return efecto_grilla(sess.u, tipo, None)


def _h_mostrar_texto(sess, accion):
    txt = _uno(sess.u, accion, "contenido")
    return {"tipo": "texto", "contenido": txt.label if txt is not None else ""}


def _h_abrir_submenu(sess, accion):
    destino = _uno(sess.u, accion, "submenu_destino")
    if destino is not None:
        sess.stack.append(destino)
    return {"tipo": "navegado"}


def _h_volver(sess, accion):
    if len(sess.stack) > 1:
        sess.stack.pop()
    return {"tipo": "navegado"}


def _h_salir(sess, accion):
    sess.terminada = True
    return {"tipo": "salir"}


_DISPATCH = {
    "mostrar_texto": _h_mostrar_texto,
    "abrir_submenu": _h_abrir_submenu,
    "volver": _h_volver,
    "salir": _h_salir,
    "abrir_formulario": _h_abrir_formulario,
    "abrir_grilla": _h_abrir_grilla,
}


class MenuSession:
    """Una sesión de navegación: el universo + un stack de menús."""

    def __init__(self, universe, menu_inicial="menu_principal"):
        self.u = universe
        self.stack = [universe.ind(menu_inicial)]
        self.terminada = False

    def estado(self):
        menu = self.stack[-1]
        opciones = _opciones(self.u, menu)
        return {
            "menu_id": menu.id,
            "titulo": menu.label,
            "es_submenu": len(self.stack) > 1,
            "terminada": self.terminada,
            "opciones": [{"indice": i, "id": o.id, "label": o.label}
                         for i, o in enumerate(opciones, 1)],
        }

    def seleccionar(self, indice):
        if self.terminada:
            return {"efecto": {"tipo": "terminada"}, "estado": self.estado()}
        opciones = _opciones(self.u, self.stack[-1])
        if not isinstance(indice, int) or not (1 <= indice <= len(opciones)):
            return {"efecto": {"tipo": "invalido"}, "estado": self.estado()}
        opcion = opciones[indice - 1]
        accion = _uno(self.u, opcion, "tiene_accion")
        if accion is None:
            return {"efecto": {"tipo": "sin_accion"}, "estado": self.estado()}
        verbo = _uno(self.u, accion, "instancia_de")
        handler = _DISPATCH.get(verbo.id) if verbo is not None else None
        if handler is None:
            return {"efecto": {"tipo": "desconocido"}, "estado": self.estado()}
        efecto = handler(self, accion)
        if efecto.get("tipo") in ("formulario", "grilla"):
            efecto["titulo"] = opcion.label
        return {"efecto": efecto, "estado": self.estado()}

    def tripletas_visibles(self):
        menu = self.stack[-1]
        nodos = [menu]
        for o in _opciones(self.u, menu):
            nodos.append(o)
            acc = _uno(self.u, o, "tiene_accion")
            if acc is not None:
                nodos.append(acc)
        vistos = set()
        out = []
        for n in nodos:
            if n.id in vistos:
                continue
            vistos.add(n.id)
            for f in self.u.facts_about(n):
                out.append({
                    "sujeto": f.subject.id, "rol": f.role, "valor": f.value.id,
                    "sujeto_label": f.subject.label, "valor_label": f.value.label,
                })
        return out
