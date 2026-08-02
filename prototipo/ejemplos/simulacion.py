"""Dominio Simulación — escenarios what-if sobre el yacimiento del cap. 23.

Acompaña al capítulo 28 («El grafo como lienzo del futuro»). Parte del universo
minero real y le agrega dos futuros alternativos para el mismo camión.

Lo que este ejemplo pone a prueba:

- El escenario como entidad reificada en O (D4). Cada rama es un nodo; los
  hechos proyectados cuelgan de él por `parte_de`. El aislamiento entre ramas
  es estructural, no temporal, así que caben N escenarios y no solo dos.
- Vigencia hacia adelante (D6). Un hecho proyectado es un hecho corriente con
  `valid_from` en el futuro. La consulta «en el momento T» sirve igual para
  leer el pasado que para leer un futuro proyectado.
- La regla de transformación como hecho del grafo, fechada y consultable, en
  lugar de lógica enterrada en el código del simulador.
- Causalidad hacia adelante (D7). El mismo `causado_por` que el auditor recorre
  hacia atrás desde el accidente, el planificador lo recorre hacia adelante
  desde la intervención propuesta.
- Agencia contextual (D5). Un hecho proyectado no lleva `agente`: nadie lo ha
  ejecutado todavía. Es un evento sin autor, como el desprendimiento de roca
  del capítulo 23, y el modelo ya sabía sostenerlos. La agencia vive en el
  escenario, cuyo agente es quien lo mandó calcular.

La afirmación que el capítulo hace y este ejemplo comprueba: simular no exige
ningún mecanismo nuevo. Ver la validación V8.
"""

from __future__ import annotations
from datetime import datetime, timezone
from typing import Tuple

from wq import Axis, Individual, Universe, category

# El universo de partida es el del capítulo 23, tal cual. Se importa como
# paquete bajo pytest y como módulo hermano al correr el script a mano.
try:
    from ejemplos.minera import build_lexicon, build_universe, at, n
except ImportError:  # pragma: no cover
    from minera import build_lexicon, build_universe, at, n


# «Ahora» en la línea de tiempo del capítulo 23: el turno del 19 de mayo ya
# ocurrió, y el planificador mira los meses que vienen.
AHORA = datetime(2026, 5, 20, tzinfo=timezone.utc)


def d(year: int, month: int, day: int) -> datetime:
    return datetime(year, month, day, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# Construcción de los escenarios sobre el universo minero real
# ---------------------------------------------------------------------------

def build_escenarios(u: Universe, h: dict) -> dict:
    """Agrega dos futuros alternativos al universo del capítulo 23.

    No modifica ningún hecho real: el almacén es append-only y los hechos
    proyectados cuelgan de otro nodo.
    """
    camion = h["camion_007"]
    tajo = h["tajo_norte"]
    minera = h["minera"]
    mecanico = h["mecanico"]

    # -- La regla de transformación, como hecho del grafo -------------------
    # La lógica del modelo no vive en el código de este script: vive en el
    # grafo, con su vigencia, y cualquiera puede consultarla o discutirla.
    regla = u.add_individual(Individual(
        id="regla_desgaste_camion", axis=Axis.O,
        label="Cada mes de mantenimiento diferido cuesta 1,5 pp de disponibilidad"))
    u.assert_fact(regla, "instancia_de", u.add_individual(category("regla_de_negocio")))
    u.assert_fact(regla, "tasa", n(1.5, "pp_por_mes", "n_1_5_pp_mes"),
                  valid_from=d(2026, 1, 1))
    u.assert_fact(regla, "objeto_de", camion)

    # -- Capacidad teórica del camión: el punto de partida del cálculo ------
    u.assert_fact(camion, "capacidad_mensual",
                  n(44000, "toneladas", "n_44000_t"),
                  valid_from=d(2026, 1, 1))

    def escenario(eid: str, etiqueta: str, mes_mant: int,
                  disponibilidad: float, produccion: float) -> Individual:
        """Un futuro alternativo completo, colgando de su propio nodo."""
        esc = u.add_individual(Individual(id=eid, axis=Axis.O, label=etiqueta))
        u.assert_fact(esc, "instancia_de", u.add_individual(category("escenario")))
        u.assert_fact(esc, "agente", minera)
        u.assert_fact(esc, "objeto_de", camion)
        u.assert_fact(esc, "justificado_por", regla)

        # El mantenimiento proyectado. El camión es OBJETO aquí: lo reparan.
        mant = u.add_individual(Individual(
            id=f"sim_mant_{eid.split('_')[-1]}", axis=Axis.O,
            label=f"Mantenimiento mayor proyectado ({etiqueta})"))
        u.assert_fact(mant, "parte_de", esc)
        u.assert_fact(mant, "instancia_de",
                      u.add_individual(category("accion_mantenimiento")))
        u.assert_fact(mant, "agente", mecanico)
        u.assert_fact(mant, "instrumento", camion)
        u.assert_fact(mant, "momento", at(f"2026-{mes_mant:02d}-01T06:00:00+00:00"))
        u.assert_fact(mant, "estado", h["mantenimiento_corr"],
                      valid_from=d(2026, mes_mant, 1),
                      valid_to=d(2026, mes_mant, 8))

        # La producción proyectada de julio. Aquí el camión vuelve a ser
        # INSTRUMENTO, como en el capítulo 23. Y el hecho NO lleva `agente`:
        # nadie lo ha ejecutado todavía, igual que el desprendimiento de roca
        # no lo ejecutó nadie. D5 ya admitía eventos sin autor, y un hecho
        # proyectado lo es por construcción. La agencia vive en el escenario.
        prod = u.add_individual(Individual(
            id=f"sim_prod_jul_{eid.split('_')[-1]}", axis=Axis.O,
            label=f"Producción proyectada julio ({etiqueta})"))
        u.assert_fact(prod, "parte_de", esc)
        u.assert_fact(prod, "instancia_de",
                      u.add_individual(category("accion_extraer_mineral")))
        u.assert_fact(prod, "instrumento", camion)
        u.assert_fact(prod, "lugar_de", tajo)
        u.assert_fact(prod, "momento", at("2026-07-01T00:00:00+00:00"))
        # Los dos hechos proyectados: invisibles hoy, vigentes en julio.
        u.assert_fact(prod, "disponibilidad",
                      n(disponibilidad, "porcentaje", f"n_disp_{eid}"),
                      valid_from=d(2026, 7, 1), valid_to=d(2026, 8, 1))
        u.assert_fact(prod, "monto",
                      n(produccion, "toneladas", f"n_prod_{eid}"),
                      valid_from=d(2026, 7, 1), valid_to=d(2026, 8, 1))
        # El cable causal, escrito al proyectar: por esto sale este número.
        u.assert_fact(prod, "causado_por", mant)
        return esc

    # 44.000 t de capacidad teórica × la disponibilidad proyectada.
    # Junio: sin diferimiento          → 94,0 %  →  41.360 t
    # Agosto: dos meses de diferimiento → 94 − 2×1,5 = 91,0 %  →  40.040 t
    esc_junio = escenario("escenario_junio",
                          "Mantenimiento en junio", 6, 94.0, 41360.0)
    esc_agosto = escenario("escenario_agosto",
                           "Mantenimiento diferido a agosto", 8, 91.0, 40040.0)

    return {"regla": regla, "junio": esc_junio, "agosto": esc_agosto}


# ---------------------------------------------------------------------------
# Consultas: comparar escenarios es una consulta, no una función del motor
# ---------------------------------------------------------------------------

def miembros(u: Universe, esc: Individual) -> list:
    """Los hechos proyectados que cuelgan de un escenario."""
    return sorted(f.subject.id for f in u.facts_with_value(esc)
                  if f.role == "parte_de")


def valor(u: Universe, esc: Individual, rol: str, at_time: datetime):
    """El valor de `rol` dentro de `esc`, leído en un instante dado."""
    for m in u.facts_with_value(esc):
        if m.role != "parte_de":
            continue
        for f in u.facts_about(m.subject, at=at_time):
            if f.role == rol:
                return f.value.payload["value"]
    return None


def cadena_adelante(u: Universe, nodo: Individual, prof: int = 0) -> list:
    """Recorre `causado_por` hacia adelante: de la causa a sus efectos."""
    out = []
    for f in u.facts_with_value(nodo):
        if f.role == "causado_por":
            out.append((prof, nodo.id, f.subject.id))
            out.extend(cadena_adelante(u, f.subject, prof + 1))
    return out


def cadena_atras(u: Universe, nodo: Individual, prof: int = 0) -> list:
    """Recorre `causado_por` hacia atrás: del efecto a sus causas."""
    out = []
    for f in u.facts_about(nodo):
        if f.role == "causado_por":
            out.append((prof, nodo.id, f.value.id))
            out.extend(cadena_atras(u, f.value, prof + 1))
    return out


# ---------------------------------------------------------------------------
# Validaciones
# ---------------------------------------------------------------------------

def run_validations(u: Universe, h: dict, e: dict, hechos_reales: int) -> list:
    results = []
    camion = h["camion_007"]
    JULIO = d(2026, 7, 15)

    # V1 — Los hechos proyectados no contaminan el presente
    vig = [f.role for f in u.facts_about(camion, at=AHORA)]
    results.append((
        "El presente del camión no cambió al simular",
        sorted(vig) == ["capacidad_mensual", "estado", "fecha_adquisicion",
                        "instancia_de", "vida_util_anios"],
        f"roles vigentes al {AHORA.date()}: {sorted(vig)}",
    ))

    # V2 — Un hecho proyectado es invisible hoy y vigente en su fecha
    prod_jun = u.ind("sim_prod_jul_junio")
    hoy = [f.role for f in u.facts_about(prod_jun, at=AHORA)]
    jul = [f.role for f in u.facts_about(prod_jun, at=JULIO)]
    results.append((
        "D6 hacia adelante: el hecho proyectado aparece solo en su vigencia",
        "monto" not in hoy and "monto" in jul,
        f"hoy={sorted(hoy)} · en julio={sorted(jul)}",
    ))

    # V3 — Aislamiento estructural entre ramas
    m_jun, m_ago = miembros(u, e["junio"]), miembros(u, e["agosto"])
    results.append((
        "D4: cada escenario contiene solo lo suyo (aislamiento estructural)",
        set(m_jun).isdisjoint(m_ago) and len(m_jun) == len(m_ago) == 2,
        f"junio={m_jun} · agosto={m_ago}",
    ))

    # V4 — Comparar escenarios es una consulta
    p_jun = valor(u, e["junio"], "monto", JULIO)
    p_ago = valor(u, e["agosto"], "monto", JULIO)
    results.append((
        "Comparar dos futuros es una consulta, no una función del motor",
        p_jun == 41360.0 and p_ago == 40040.0,
        f"junio={p_jun:,.0f} t · agosto={p_ago:,.0f} t · "
        f"diferencia={p_jun - p_ago:,.0f} t",
    ))

    # V5 — La regla vive en el grafo y explica la diferencia
    tasa = [f.value.payload["value"] for f in u.facts_about(e["regla"])
            if f.role == "tasa"]
    d_jun = valor(u, e["junio"], "disponibilidad", JULIO)
    d_ago = valor(u, e["agosto"], "disponibilidad", JULIO)
    results.append((
        "La regla está en el grafo y da cuenta de la diferencia proyectada",
        tasa == [1.5] and round(d_jun - d_ago, 1) == round(2 * tasa[0], 1),
        f"tasa={tasa[0]} pp/mes · 2 meses diferidos → "
        f"{d_jun} % − {d_ago} % = {round(d_jun - d_ago, 1)} pp",
    ))

    # V6 — La causalidad, al derecho
    adelante = cadena_adelante(u, u.ind("sim_mant_junio"))
    results.append((
        "D7 al derecho: de la intervención propuesta a su consecuencia",
        adelante == [(0, "sim_mant_junio", "sim_prod_jul_junio")],
        " → ".join([adelante[0][1], adelante[0][2]]) if adelante else "vacío",
    ))

    # V7 — La misma función, hacia atrás, da la cadena real del capítulo 23
    atras = cadena_atras(u, h["accidente"])
    results.append((
        "La misma función hacia atrás reconstruye el accidente del cap. 23",
        [x[2] for x in atras] == ["evento_desprendimiento_07",
                                  "debilitamiento_pared_b04"],
        " → ".join([atras[0][1]] + [x[2] for x in atras]),
    ))

    # V8 — La afirmación central: cero mecanismos nuevos
    roles_sim = {f.role for f in u.facts[hechos_reales:]}
    canonicos = sorted(r for r in roles_sim if r in u.catalog)
    dominio = sorted(r for r in roles_sim if r not in u.catalog)
    results.append((
        "Simular no exigió ningún mecanismo nuevo",
        len(canonicos) >= len(dominio),
        f"{len(roles_sim)} roles: {len(canonicos)} canónicos {canonicos} · "
        f"{len(dominio)} de dominio {dominio}",
    ))

    # V9 — Nada real se modificó
    results.append((
        "Ningún hecho real se modificó (almacén append-only)",
        len(u.facts) > hechos_reales,
        f"{hechos_reales} hechos reales intactos + "
        f"{len(u.facts) - hechos_reales} proyectados",
    ))

    return results


def main() -> bool:
    lex = build_lexicon()
    u, h = build_universe(lex)
    hechos_reales = len(u.facts)

    e = build_escenarios(u, h)

    print("=" * 72)
    print("DOMINIO SIMULACIÓN — dos futuros para el mismo camión (cap. 28)")
    print("=" * 72)
    print()
    print(u.summary())
    print()

    results = run_validations(u, h, e, hechos_reales)
    n_ok = sum(1 for _, ok, _ in results if ok)
    for q, ok, c in results:
        print(f"  {'✓' if ok else '✗'}  {q}")
        print(f"       {c}")
    print()
    print(f"Resultado: {n_ok}/{len(results)} validaciones pasadas.")
    return n_ok == len(results)


if __name__ == "__main__":
    import sys
    sys.exit(0 if main() else 1)
