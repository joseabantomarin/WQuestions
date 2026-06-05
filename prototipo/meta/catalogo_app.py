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
        RoleSignature("sobre_tipo", Axis.O, Axis.K, True,
                      "acción → tipo de entidad sobre el que opera"),
        RoleSignature("tiene_campo", Axis.K, Axis.O, False,
                      "tipo de entidad → campo (descriptor)"),
        RoleSignature("tipo_dato", Axis.O, Axis.K, True,
                      "campo → tipo de dato (texto/numero/fecha/referencia)"),
        RoleSignature("rol", Axis.O, Axis.K, True,
                      "campo → rol; el id de ese K es el predicado en los registros"),
        RoleSignature("referencia_a", Axis.O, Axis.K, True,
                      "campo referencia → tipo de entidad apuntado"),
        RoleSignature("eje_instancia", Axis.K, Axis.K, True,
                      "tipo de entidad → eje (K cuyo label es la letra: Q/O/...) de sus instancias"),
        RoleSignature("campo_etiqueta", Axis.K, Axis.O, True,
                      "tipo de entidad → campo cuyo valor es la etiqueta visible del individuo"),
    ]
    for sig in roles:
        cat.register(sig)
    return cat
