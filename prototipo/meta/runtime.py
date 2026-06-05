"""Evaluador genérico del menú meta-driven.

No conoce ninguna opción por nombre: lee el menú actual desde el grafo, lo muestra,
y despacha cada acción según su tipo-K (`instancia_de`). Agregar una primitiva nueva
= un individuo K + una entrada en DISPATCH.
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


# --- handlers: (u, accion, stack, escribir) -> bool "seguir corriendo" -------

def _h_mostrar_texto(u, accion, stack, escribir):
    txt = _uno(u, accion, "contenido")
    escribir(txt.label if txt is not None else "")
    return True


def _h_abrir_submenu(u, accion, stack, escribir):
    destino = _uno(u, accion, "submenu_destino")
    if destino is not None:
        stack.append(destino)
    return True


def _h_volver(u, accion, stack, escribir):
    if len(stack) > 1:
        stack.pop()
    return True


def _h_salir(u, accion, stack, escribir):
    return False


DISPATCH = {
    "mostrar_texto": _h_mostrar_texto,
    "abrir_submenu": _h_abrir_submenu,
    "volver": _h_volver,
    "salir": _h_salir,
}


def run(u, leer=input, escribir=print, menu_inicial="menu_principal"):
    """Corre el menú. `leer`/`escribir` son inyectables para testear sin teclado."""
    stack = [u.ind(menu_inicial)]
    seguir = True
    while seguir:
        menu = stack[-1]
        opciones = _opciones(u, menu)
        escribir(f"\n== {menu.label} ==")
        for i, opt in enumerate(opciones, 1):
            escribir(f"  {i}. {opt.label}")

        entrada = str(leer("> ")).strip()
        if not entrada.isdigit() or not (1 <= int(entrada) <= len(opciones)):
            escribir("Opción inválida.")
            continue

        opcion = opciones[int(entrada) - 1]
        accion = _uno(u, opcion, "tiene_accion")
        verbo = _uno(u, accion, "instancia_de")
        handler = DISPATCH.get(verbo.id) if verbo is not None else None
        if handler is None:
            escribir(f"(sin handler para '{verbo.id if verbo else '?'}')")
            continue
        seguir = handler(u, accion, stack, escribir)
