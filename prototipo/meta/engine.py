"""Motor headless del menú meta-driven: MenuSession.

Toda la lógica de navegación vive aquí, una sola vez. Los handlers devuelven un
efecto (no imprimen) y mutan el stack. CLI y web son pieles delgadas sobre este motor.
"""


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
