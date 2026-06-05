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


def registrar_firmas_de_esquema(u):
    """Deriva y registra en el catálogo la firma de cada campo del esquema.

    dominio = eje_instancia del tipo dueño (default O); rango = de tipo_dato
    (texto→K, numero→N, fecha→T, referencia→eje del referencia_a). Solo registra
    roles que no estén ya en el catálogo (se confía en el núcleo canónico).
    """
    try:
        campo_meta = u.ind("campo")
    except Exception:
        return

    def _uno(subj, rol):
        for f in u.facts_about(subj):
            if f.role == rol:
                return f.value
        return None

    rango_por_tipo = {"texto": Axis.K, "numero": Axis.N, "fecha": Axis.T}
    cat = u.catalog
    campos = [f.subject for f in u.facts_with_value(campo_meta) if f.role == "instancia_de"]
    for c in campos:
        rol = _uno(c, "rol")
        rol_id = rol.id if rol is not None else c.id
        if cat.get(rol_id) is not None:
            continue  # ya tipado (canónico o ya derivado) — se confía en el núcleo
        duenos = [f.subject for f in u.facts_with_value(c) if f.role == "tiene_campo"]
        dom = Axis.O
        if duenos:
            ax = _uno(duenos[0], "eje_instancia")
            if ax is not None:
                dom = Axis(ax.label)
        td = _uno(c, "tipo_dato")
        td_id = td.id if td is not None else "texto"
        if td_id == "referencia":
            ref = _uno(c, "referencia_a")
            rax = _uno(ref, "eje_instancia") if ref is not None else None
            rng = Axis(rax.label) if rax is not None else Axis.O
        else:
            rng = rango_por_tipo.get(td_id, Axis.K)
        cat.register(RoleSignature(rol_id, dom, rng, True, f"campo de esquema ({td_id})"))
