"""Driver CLI sobre el motor headless `MenuSession`.

Mantiene la firma `run(u, leer, escribir, menu_inicial)` para no romper los tests
existentes. La lógica de navegación vive en engine.MenuSession; aquí solo se traduce
el motor a print/input. Reexporta los helpers por compatibilidad.
"""
from .engine import MenuSession, _valores, _uno, _orden, _opciones  # noqa: F401 (reexport)


def run(u, leer=input, escribir=print, menu_inicial="menu_principal"):
    """Corre el menú en la terminal. `leer`/`escribir` son inyectables para tests."""
    sess = MenuSession(u, menu_inicial)
    while not sess.terminada:
        e = sess.estado()
        escribir(f"\n== {e['titulo']} ==")
        for o in e["opciones"]:
            escribir(f"  {o['indice']}. {o['label']}")
        entrada = str(leer("> ")).strip()
        if not entrada.isdigit():
            escribir("Opción inválida.")
            continue
        ef = sess.seleccionar(int(entrada))["efecto"]
        tipo = ef["tipo"]
        if tipo == "texto":
            escribir(ef["contenido"])
        elif tipo == "invalido":
            escribir("Opción inválida.")
        elif tipo == "sin_accion":
            escribir("(opción sin acción)")
        elif tipo == "desconocido":
            escribir("(sin handler para esa acción)")
        # navegado / salir: nada que imprimir
