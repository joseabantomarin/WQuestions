"""Catálogo del app meta-driven: los roles propios sobre el catálogo canónico de wq.

Parte del `Catalog` de wq (que ya trae `instancia_de`, etc.) y añade los 5 roles
que el menú necesita. `submenu_destino` se llama así (no `destino`) para no chocar
con el rol canónico `destino` (O→L).
"""
from wq import Catalog, RoleSignature, Axis


def build_catalog() -> Catalog:
    cat = Catalog()
    roles = [
        RoleSignature("tiene_opcion", Axis.O, Axis.O, False, "menú → opción"),
        RoleSignature("orden", Axis.O, Axis.N, True, "opción → posición"),
        RoleSignature("tiene_accion", Axis.O, Axis.O, True, "opción → acción"),
        RoleSignature("submenu_destino", Axis.O, Axis.O, True,
                      "acción abrir_submenu → menú destino"),
        RoleSignature("contenido", Axis.O, Axis.K, True,
                      "acción mostrar_texto → texto (individuo K)"),
    ]
    for sig in roles:
        cat.register(sig)
    return cat
