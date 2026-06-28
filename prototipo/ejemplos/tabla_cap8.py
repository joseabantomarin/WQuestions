"""Seed del cap. 8 — las tres vistas tabulares sobre datos reales.

Construye un universo municipal con ~336 trámites distribuidos exactamente como
la Fig 8.5, más tres trámites destacados (Juan, Carla, Marta) con los atributos
literales de la Fig 8.4. Corre las tres vistas y verifica que el código reproduce
las figuras publicadas: el capítulo y el prototipo dan los mismos números.

    PYTHONPATH=. python3 ejemplos/tabla_cap8.py
"""

from __future__ import annotations
from typing import Dict, Tuple

from wq import Axis, Individual, Universe, Catalog
from wq.vistas import tabla_plana, proyeccion, pivote


# Distribución exacta de la Fig 8.5 (clase K × zona L → conteo).
DISTRIBUCION = {
    "licencia_construccion":   {"zona_centro": 45,  "zona_norte": 12, "zona_sur": 8},
    "licencia_funcionamiento": {"zona_centro": 120, "zona_norte": 54, "zona_sur": 30},
    "multa_fiscalizacion":     {"zona_centro": 15,  "zona_norte": 42, "zona_sur": 10},
}

ETIQUETA_CLASE = {
    "licencia_construccion": "Licencias de construcción",
    "licencia_funcionamiento": "Licencias de funcionamiento",
    "multa_fiscalizacion": "Multas de fiscalización",
    "licencia_micromov": "Licencias de micromovilidad",
}
ETIQUETA_ZONA = {"zona_centro": "Centro", "zona_norte": "Norte", "zona_sur": "Sur"}
COD_CLASE = {"licencia_construccion": "constr",
             "licencia_funcionamiento": "func",
             "multa_fiscalizacion": "multa"}
COD_ZONA = {"zona_centro": "centro", "zona_norte": "norte", "zona_sur": "sur"}

COLUMNAS_PROYECCION = [
    ("Ciudadano (Q)", "agente"),
    ("Expediente (O)", "_subject"),
    ("Ubicación (L)", "lugar_de"),
    ("Fecha (T)", "momento"),
    ("Costo (N)", "monto"),
    ("Estado (M)", "estado"),
]

PIVOTE_ESPERADA = [[45, 12, 8], [120, 54, 30], [15, 42, 10]]
PROYECCION_ESPERADA = [
    ["Juan", "Licencia de funcionamiento", "Jr. Trujillo 450, Centro",
     "22-06-2026", "S/ 450,00", "Solicitado"],
    ["Carla", "Licencia de micromovilidad", "Av. Perú 1200, Norte",
     "23-06-2026", "S/ 300,00", "En revisión"],
    ["Marta", "Remodelación de local", "Jr. Lima 88, Centro",
     "24-06-2026", "S/ 520,00", "Aprobada"],
]


def _t(u, label, tid):
    return u.add_individual(Individual(id=tid, axis=Axis.T, label=label))


def _n(u, valor, label, nid):
    return u.add_individual(Individual(id=nid, axis=Axis.N, label=label,
                                       payload={"value": valor, "unit": "PEN"}))


def _estado(u, eid, label):
    return u.add_individual(Individual(id=eid, axis=Axis.K, label=label))


def _generico(u, clase, zona, sid):
    """Un trámite del grueso: solo clase (K) y zona (L)."""
    s = u.add_individual(Individual(id=sid, axis=Axis.O, label=sid))
    u.assert_fact(s, "instancia_de", clase)
    u.assert_fact(s, "lugar_de", zona)
    return s


def _tramite_juan(u, clases, zonas):
    direccion = u.add_individual(Individual(
        id="dir_juan", axis=Axis.L, label="Jr. Trujillo 450, Centro"))
    u.assert_fact(direccion, "dentro_de", zonas["zona_centro"])
    juan = u.add_individual(Individual(id="juan", axis=Axis.Q, label="Juan"))
    s = u.add_individual(Individual(id="tram_juan_func_centro", axis=Axis.O,
                                    label="Licencia de funcionamiento"))
    u.assert_fact(s, "instancia_de", clases["licencia_funcionamiento"])
    u.assert_fact(s, "agente", juan)
    u.assert_fact(s, "lugar_de", direccion)
    u.assert_fact(s, "momento", _t(u, "22-06-2026", "t_2026-06-22"))
    u.assert_fact(s, "monto", _n(u, 450.0, "S/ 450,00", "n_450_pen"))
    u.assert_fact(s, "estado", _estado(u, "solicitado", "Solicitado"))
    return s


def _tramite_marta(u, clases, zonas):
    direccion = u.add_individual(Individual(
        id="dir_marta", axis=Axis.L, label="Jr. Lima 88, Centro"))
    u.assert_fact(direccion, "dentro_de", zonas["zona_centro"])
    marta = u.add_individual(Individual(id="marta", axis=Axis.Q, label="Marta"))
    s = u.add_individual(Individual(id="tram_marta_constr_centro", axis=Axis.O,
                                    label="Remodelación de local"))
    u.assert_fact(s, "instancia_de", clases["licencia_construccion"])
    u.assert_fact(s, "agente", marta)
    u.assert_fact(s, "lugar_de", direccion)
    u.assert_fact(s, "momento", _t(u, "24-06-2026", "t_2026-06-24"))
    u.assert_fact(s, "monto", _n(u, 520.0, "S/ 520,00", "n_520_pen"))
    u.assert_fact(s, "estado", _estado(u, "aprobada", "Aprobada"))
    return s


def _tramite_carla(u, clases, zonas):
    direccion = u.add_individual(Individual(
        id="dir_carla", axis=Axis.L, label="Av. Perú 1200, Norte"))
    u.assert_fact(direccion, "dentro_de", zonas["zona_norte"])
    carla = u.add_individual(Individual(id="carla", axis=Axis.Q, label="Carla"))
    s = u.add_individual(Individual(id="tram_carla_micromov", axis=Axis.O,
                                    label="Licencia de micromovilidad"))
    u.assert_fact(s, "instancia_de", clases["licencia_micromov"])
    u.assert_fact(s, "agente", carla)
    u.assert_fact(s, "lugar_de", direccion)
    u.assert_fact(s, "momento", _t(u, "23-06-2026", "t_2026-06-23"))
    u.assert_fact(s, "monto", _n(u, 300.0, "S/ 300,00", "n_300_pen"))
    u.assert_fact(s, "estado", _estado(u, "en_revision", "En revisión"))
    return s


def build_universe() -> Tuple[Universe, Dict[str, Individual]]:
    u = Universe(name="cap8_tablas", catalog=Catalog())

    clases = {cid: u.add_individual(Individual(
                  id=cid, axis=Axis.K, label=ETIQUETA_CLASE[cid]))
              for cid in list(DISTRIBUCION) + ["licencia_micromov"]}
    zonas = {lid: u.add_individual(Individual(
                 id=lid, axis=Axis.L, label=ETIQUETA_ZONA[lid]))
             for lid in ("zona_centro", "zona_norte", "zona_sur")}

    destacados: Dict[str, Individual] = {}
    for cid, por_zona in DISTRIBUCION.items():
        for lid, total in por_zona.items():
            for i in range(total):
                if i == 0 and cid == "licencia_funcionamiento" and lid == "zona_centro":
                    destacados["juan_t"] = _tramite_juan(u, clases, zonas)
                elif i == 0 and cid == "licencia_construccion" and lid == "zona_centro":
                    destacados["marta_t"] = _tramite_marta(u, clases, zonas)
                else:
                    sid = f"tram_{COD_CLASE[cid]}_{COD_ZONA[lid]}_{i:03d}"
                    _generico(u, clases[cid], zonas[lid], sid)

    destacados["carla_t"] = _tramite_carla(u, clases, zonas)

    h: Dict[str, Individual] = {
        "constr": clases["licencia_construccion"],
        "func": clases["licencia_funcionamiento"],
        "multa": clases["multa_fiscalizacion"],
        "micromov": clases["licencia_micromov"],
        "zc": zonas["zona_centro"], "zn": zonas["zona_norte"], "zs": zonas["zona_sur"],
    }
    h.update(destacados)
    return u, h


def vista_plana(u, h):
    # Muestra de la hoja dispersa: los tres destacados (cross-clase), con códigos.
    return tabla_plana(u, subjects=[h["juan_t"], h["carla_t"], h["marta_t"]])


def vista_proyeccion(u, h):
    # Reporte legible de los tres trámites destacados (la Fig 8.4 es muestra de 3).
    return proyeccion(u, COLUMNAS_PROYECCION,
                      subjects=[h["juan_t"], h["carla_t"], h["marta_t"]])


def vista_pivote(u, h):
    return pivote(
        u,
        filtro_k=[h["constr"].id, h["func"].id, h["multa"].id],
        orden_filas=[h["constr"].id, h["func"].id, h["multa"].id],
        orden_cols=[h["zc"].id, h["zn"].id, h["zs"].id],
        resolver_l_a_zona=True,
    )


def main() -> bool:
    u, h = build_universe()
    print("=" * 72)
    print("CAP. 8 — De la geometría a la tabla que ya conoces")
    print("=" * 72)
    print()
    print(u.summary())
    print()

    plana = vista_plana(u, h)
    proj = vista_proyeccion(u, h)
    piv = vista_pivote(u, h)

    print("Fig 8.2 — hoja dispersa (códigos):")
    print(plana.to_string(index=False))
    print()
    print("Fig 8.4 — proyección legible:")
    print(proj.to_string(index=False))
    print()
    print("Fig 8.5 — pivote (conteos):")
    print(piv.to_string())
    print()

    ok_piv = piv.values.tolist() == PIVOTE_ESPERADA
    ok_proj = [proj.iloc[i].tolist()
               for i in range(len(proj))] == PROYECCION_ESPERADA
    print(f"  {'✓' if ok_piv else '✗'}  pivote reproduce la Fig 8.5")
    print(f"  {'✓' if ok_proj else '✗'}  proyección reproduce la Fig 8.4")
    return ok_piv and ok_proj


if __name__ == "__main__":
    import sys
    sys.exit(0 if main() else 1)
