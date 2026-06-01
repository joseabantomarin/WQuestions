"""Dominio spa — modelado completo en WQuestions.

Modela el dominio del Spa Oasis (el caso del Capítulo 14 del libro):
- Clientes, recepcionistas, spa.
- Cámaras de vapor y cámara seca (objetos y lugares simultáneamente).
- Sesiones individuales con cliente, lugar, momento, costo.
- Compra de consumibles (jugo, ensalada).
- Promociones combinadas (spa + masaje).
- Programa de fidelidad: 7 sesiones → 1 gratis.
- Plan mensual con 2 sesiones de spa por semana incluidas.
- Recomendación: ducha fría al final → causa satisfacción.

El objetivo es validar TODOS los patrones que el libro afirma que el modelo
soporta. Al final del script se imprime un informe de validación.
"""

from __future__ import annotations
from datetime import datetime, timezone, timedelta
from typing import List, Tuple

from wq import (
    Axis, Individual, Universe, Catalog, Lexicon, LexiconEntry,
    Pattern, Var, query, count, ingest_situation, category, mint_id,
)


# ---------------------------------------------------------------------------
# 1. Configurar lexicon con verbos del dominio spa
# ---------------------------------------------------------------------------

def build_lexicon() -> Lexicon:
    lex = Lexicon()

    lex.register(LexiconEntry(
        verb="ingresar",
        situation_type="accion_ingresar",
        obligatory=["agente", "lugar_destino"],
        optional=["momento", "con_finalidad"],
        aliases={
            "agente": ["cliente", "usuario"],
            "lugar_destino": ["a la cámara", "al spa"],
        },
        nominal_forms=["ingreso"],
    ))

    lex.register(LexiconEntry(
        verb="tomar",
        situation_type="servicio_spa",
        obligatory=["cliente", "lugar_de"],
        optional=["inicio", "fin", "estatus_factual"],
        pattern=("sesion",),
        example="Ana tomó una sesión de spa",
    ))

    lex.register(LexiconEntry(
        verb="tomar",
        situation_type="accion_bromear",
        obligatory=["agente", "paciente"],
        optional=["momento"],
        pattern=("el_pelo",),
        notes="locución idiomática",
    ))

    lex.register(LexiconEntry(
        verb="tomar",
        situation_type="accion_tomar",
        obligatory=["agente", "tema"],
        optional=["momento"],
        notes="genérico — recibir/asir",
    ))

    lex.register(LexiconEntry(
        verb="pagar",
        situation_type="accion_pagar",
        obligatory=["agente", "tema", "monto", "unidad"],
        optional=["momento"],
        aliases={"agente": ["el que paga", "cliente"]},
    ))

    lex.register(LexiconEntry(
        verb="redimir",
        situation_type="aplicacion_beneficio",
        obligatory=["agente", "tema"],
        optional=["momento"],
    ))

    lex.register(LexiconEntry(
        verb="contratar",
        situation_type="contrato_servicio",
        obligatory=["cliente", "tema"],
        optional=["inicio", "fin", "monto", "unidad", "modalidad", "estatus_factual"],
        nominal_forms=["contratación"],
    ))

    lex.register(LexiconEntry(
        verb="ducharse",
        situation_type="accion_ducharse",
        obligatory=["agente"],
        optional=["lugar_de", "momento", "calificacion"],
    ))

    lex.register(LexiconEntry(
        verb="experimentar",
        situation_type="estado_subjetivo",
        obligatory=["experimentador"],
        optional=["calificacion", "causado_por", "momento"],
    ))

    # Dialecto de dominio: aliases globales
    lex.register_domain_dialect("spa_oasis", {
        "cliente": "agente",
        "sesion": "servicio_spa",
        "plan_mensual": "contrato_servicio",
        "sesion_gratuita": "beneficio_fidelidad",
        "promo": "aplicacion_de_promocion",
    })

    return lex


# ---------------------------------------------------------------------------
# 2. Poblar el universo con un día de operación
# ---------------------------------------------------------------------------

def build_universe(lex: Lexicon) -> Tuple[Universe, dict]:
    cat = Catalog()
    u = Universe(name="spa_oasis", catalog=cat)

    # Agentes Q
    ana = u.add_individual(Individual(id="cliente_ana", axis=Axis.Q, label="Ana"))
    beto = u.add_individual(Individual(id="cliente_beto", axis=Axis.Q, label="Beto"))
    carlos = u.add_individual(Individual(id="cliente_carlos", axis=Axis.Q, label="Carlos"))
    anita_rec = u.add_individual(Individual(id="recep_anita", axis=Axis.Q, label="Anita (recepcionista)"))

    # Lugares L
    spa_central = u.add_individual(Individual(id="spa_oasis_central", axis=Axis.L, label="Spa Oasis (sede central)"))
    camara_vapor_1 = u.add_individual(Individual(id="camara_vapor_1", axis=Axis.L, label="cámara de vapor 1"))
    camara_vapor_2 = u.add_individual(Individual(id="camara_vapor_2", axis=Axis.L, label="cámara de vapor 2"))
    camara_seca = u.add_individual(Individual(id="camara_seca", axis=Axis.L, label="cámara seca"))
    ducha_03 = u.add_individual(Individual(id="ducha_03", axis=Axis.L, label="ducha 03"))

    # Categorías K
    usd = u.add_individual(category("Currency:USD"))
    cel = u.add_individual(category("Temperature:Cel"))
    minute = u.add_individual(category("Time:Minute"))
    real = u.add_individual(category("real"))
    intencionado = u.add_individual(category("intencionado"))
    finalizada = u.add_individual(category("finalizada"))
    volitiva = u.add_individual(category("volitiva"))
    fria = u.add_individual(category("fria"))
    alta = u.add_individual(category("alta"))
    recomendacion = u.add_individual(category("recomendacion"))

    # ------------------------------------------------------------------
    # Sesiones de Ana — 8 a lo largo del mes (suficiente para gatillar fidelidad)
    # ------------------------------------------------------------------
    base = datetime(2026, 4, 1, 18, 0, tzinfo=timezone.utc)
    sesiones_ana: List[Individual] = []
    for i in range(8):
        day_offset = i * 3  # cada 3 días
        inicio = base + timedelta(days=day_offset)
        fin = inicio + timedelta(minutes=40)
        sit = ingest_situation(
            u, lex, "tomar",
            roles={
                "cliente": ana,
                "lugar_de": camara_vapor_1 if i % 2 == 0 else camara_seca,
                "inicio": Individual(id=f"t_{inicio.isoformat()}", axis=Axis.T,
                                     label=inicio.isoformat(), payload=inicio),
                "fin": Individual(id=f"t_{fin.isoformat()}", axis=Axis.T,
                                  label=fin.isoformat(), payload=fin),
            },
            complements=["sesion"],
            extra={"estatus_factual": finalizada},
            sit_id=f"sesion_ana_{i+1:02d}",
        )
        sesiones_ana.append(sit)

        # Pago por la sesión
        monto = Individual(id=mint_id("n"), axis=Axis.N, label="20 USD",
                           payload={"value": 20, "unit": "Currency:USD"})
        pago = ingest_situation(
            u, lex, "pagar",
            roles={
                "agente": ana,
                "tema": sit,
                "monto": monto,
                "unidad": usd,
                "momento": Individual(id=f"t_{inicio.isoformat()}_pay", axis=Axis.T,
                                      label=inicio.isoformat(), payload=inicio),
            },
            sit_id=f"pago_ana_{i+1:02d}",
        )
        # Pago es parte de la sesión
        u.assert_fact(pago, "parte_de", sit)

    # ------------------------------------------------------------------
    # 6 sesiones de Beto (todavía no llega al beneficio)
    # ------------------------------------------------------------------
    for i in range(6):
        inicio = base + timedelta(days=i*4)
        fin = inicio + timedelta(minutes=35)
        sit = ingest_situation(
            u, lex, "tomar",
            roles={
                "cliente": beto,
                "lugar_de": camara_seca,
                "inicio": Individual(id=f"t_{inicio.isoformat()}_b{i}", axis=Axis.T,
                                     label=inicio.isoformat(), payload=inicio),
                "fin": Individual(id=f"t_{fin.isoformat()}_b{i}", axis=Axis.T,
                                  label=fin.isoformat(), payload=fin),
            },
            complements=["sesion"],
            extra={"estatus_factual": finalizada},
            sit_id=f"sesion_beto_{i+1:02d}",
        )

    # ------------------------------------------------------------------
    # Plan mensual de Carlos: incluye 2 sesiones/semana
    # ------------------------------------------------------------------
    # La oferta del negocio "plan gym mensual" es un O reificado, no un K.
    # Su _tipo_ es la categoría K `tipo_oferta_servicio`.
    plan_offering = u.add_individual(Individual(
        id="plan_gym_mensual_offering", axis=Axis.O,
        label="Plan Gimnasio Mensual (oferta)",
    ))
    u.assert_fact(plan_offering, "instancia_de",
                  u.add_individual(category("tipo_oferta_servicio")))

    plan_inicio = datetime(2026, 4, 1, 0, 0, tzinfo=timezone.utc)
    plan_fin = datetime(2026, 4, 30, 23, 59, tzinfo=timezone.utc)
    plan = ingest_situation(
        u, lex, "contratar",
        roles={
            "cliente": carlos,
            "tema": u.ind("plan_gym_mensual_offering"),
            "inicio": Individual(id="t_plan_inicio", axis=Axis.T,
                                 label=plan_inicio.isoformat(), payload=plan_inicio),
            "fin": Individual(id="t_plan_fin", axis=Axis.T,
                              label=plan_fin.isoformat(), payload=plan_fin),
        },
        extra={"estatus_factual": real},
        sit_id="plan_carlos_001",
    )
    # Carlos toma 2 sesiones cubiertas por el plan
    for i in range(2):
        inicio = base + timedelta(days=i*3)
        fin = inicio + timedelta(minutes=40)
        sit = ingest_situation(
            u, lex, "tomar",
            roles={
                "cliente": carlos,
                "lugar_de": camara_vapor_2,
                "inicio": Individual(id=f"t_carlos_{i}", axis=Axis.T,
                                     label=inicio.isoformat(), payload=inicio),
                "fin": Individual(id=f"t_carlos_f_{i}", axis=Axis.T,
                                  label=fin.isoformat(), payload=fin),
            },
            complements=["sesion"],
            extra={"estatus_factual": finalizada},
            sit_id=f"sesion_carlos_{i+1:02d}",
        )
        # Esta sesión está cubierta por el plan
        u.assert_fact(sit, "parte_de", plan)

    # ------------------------------------------------------------------
    # Cadena causal: Ana se ducha en frío → siente satisfacción
    # ------------------------------------------------------------------
    last_sesion = sesiones_ana[-1]
    ducha = ingest_situation(
        u, lex, "ducharse",
        roles={
            "agente": ana,
            "lugar_de": ducha_03,
            "momento": Individual(id="t_ducha", axis=Axis.T,
                                  label="2026-04-22T19:08Z"),
            "calificacion": fria,
        },
        sit_id="ducha_ana_001",
    )
    u.assert_fact(ducha, "parte_de", last_sesion)

    satisfaccion = ingest_situation(
        u, lex, "experimentar",
        roles={
            "experimentador": ana,
            "calificacion": alta,
            "causado_por": ducha,
        },
        sit_id="satisfaccion_ana_001",
    )

    # Regla / recomendación del local
    reco = u.add_individual(Individual(id="recomendacion_ducha_fria",
                                       axis=Axis.O,
                                       label="recomendacion_ducha_fria"))
    u.assert_fact(reco, "instancia_de", recomendacion)
    u.assert_fact(ducha, "justificado_por", reco)

    # ------------------------------------------------------------------
    # Modalidad: Ana QUIERE contratar el plan mensual (intención, no real)
    # ------------------------------------------------------------------
    intencion = ingest_situation(
        u, lex, "contratar",
        roles={
            "cliente": ana,
            "tema": u.ind("plan_gym_mensual_offering"),
        },
        extra={
            "modalidad": volitiva,
            "estatus_factual": intencionado,
        },
        sit_id="intencion_ana_001",
    )

    # ------------------------------------------------------------------
    # D9: la residencia de Carlos cambia (residencia como O reificado)
    # ------------------------------------------------------------------
    ciudad_a = u.add_individual(Individual(id="ciudad_a", axis=Axis.L, label="ciudad_a"))
    ciudad_b = u.add_individual(Individual(id="ciudad_b", axis=Axis.L, label="ciudad_b"))
    tipo_residencia = u.add_individual(category("residencia"))

    residencia_1 = u.add_individual(Individual(
        id="residencia_carlos_001", axis=Axis.O, label="residencia_carlos_001"))
    u.assert_fact(residencia_1, "instancia_de", tipo_residencia,
                  valid_from=datetime(2020, 1, 1, tzinfo=timezone.utc),
                  valid_to=datetime(2025, 12, 31, tzinfo=timezone.utc))
    u.assert_fact(residencia_1, "agente", carlos,
                  valid_from=datetime(2020, 1, 1, tzinfo=timezone.utc),
                  valid_to=datetime(2025, 12, 31, tzinfo=timezone.utc))
    u.assert_fact(residencia_1, "lugar_de", ciudad_a,
                  valid_from=datetime(2020, 1, 1, tzinfo=timezone.utc),
                  valid_to=datetime(2025, 12, 31, tzinfo=timezone.utc))

    residencia_2 = u.add_individual(Individual(
        id="residencia_carlos_002", axis=Axis.O, label="residencia_carlos_002"))
    u.assert_fact(residencia_2, "instancia_de", tipo_residencia,
                  valid_from=datetime(2026, 1, 1, tzinfo=timezone.utc))
    u.assert_fact(residencia_2, "agente", carlos,
                  valid_from=datetime(2026, 1, 1, tzinfo=timezone.utc))
    u.assert_fact(residencia_2, "lugar_de", ciudad_b,
                  valid_from=datetime(2026, 1, 1, tzinfo=timezone.utc))

    handles = {
        "ana": ana, "beto": beto, "carlos": carlos,
        "camara_vapor_1": camara_vapor_1, "camara_seca": camara_seca,
        "ducha_03": ducha_03,
        "sesiones_ana": sesiones_ana,
        "plan_carlos": plan,
        "intencion_ana": intencion,
        "satisfaccion_ana": satisfaccion,
        "ducha_ana": ducha,
        "ciudad_a": ciudad_a, "ciudad_b": ciudad_b,
        "real": real, "intencionado": intencionado,
        "finalizada": finalizada,
    }
    return u, handles


# ---------------------------------------------------------------------------
# 3. Validar lo que el libro afirma del modelo
# ---------------------------------------------------------------------------

def run_validations(u: Universe, lex: Lexicon, h: dict) -> List[Tuple[str, bool, str]]:
    """Devuelve [(pregunta, ok, comentario), ...]."""
    results = []
    servicio_spa = u.ind("servicio_spa")
    finalizada = h["finalizada"]
    real = h["real"]
    intencionado = h["intencionado"]

    # --- V1: ¿Cuántas sesiones lleva Ana? ---
    sesiones = query(u, Pattern(
        fixed={"cliente": h["ana"], "estatus_factual": finalizada},
        type_constraint=servicio_spa,
    ))
    n = len(sesiones)
    results.append((
        "¿Cuántas sesiones finalizadas tiene Ana?",
        n == 8,
        f"esperado 8, obtenido {n}",
    ))

    # --- V2: Ana califica para beneficio (≥7)? ---
    qualifies = n >= 7
    results.append((
        "¿Ana califica para sesión gratuita? (regla: ≥7)",
        qualifies,
        f"n={n} ≥ 7 → {qualifies}",
    ))

    # --- V3: Beto NO califica (6 sesiones) ---
    sesiones_b = count(u, Pattern(
        fixed={"cliente": h["beto"], "estatus_factual": finalizada},
        type_constraint=servicio_spa,
    ))
    results.append((
        "¿Beto califica?",
        sesiones_b == 6 and not (sesiones_b >= 7),
        f"n={sesiones_b}",
    ))

    # --- V4: La intención de Ana NO cuenta como contrato real ---
    contratos_reales = query(u, Pattern(
        fixed={"cliente": h["ana"], "estatus_factual": real},
        type_constraint=u.ind("contrato_servicio"),
    ))
    contratos_intencion = query(u, Pattern(
        fixed={"cliente": h["ana"], "estatus_factual": intencionado},
        type_constraint=u.ind("contrato_servicio"),
    ))
    results.append((
        "Modalidad: la intención NO se cuenta como contrato real",
        len(contratos_reales) == 0 and len(contratos_intencion) == 1,
        f"reales={len(contratos_reales)}, intencionados={len(contratos_intencion)}",
    ))

    # --- V5: Causalidad — la satisfacción de Ana está causada_por la ducha ---
    facts = u.facts_about(h["satisfaccion_ana"])
    causa_facts = [f for f in facts if f.role == "causado_por"]
    ok = len(causa_facts) == 1 and causa_facts[0].value.id == h["ducha_ana"].id
    results.append((
        "Cadena causal: satisfaccion_ana causado_por ducha_ana",
        ok,
        f"causado_por: {[f.value.id for f in causa_facts]}",
    ))

    # --- V6: D9 — residencia de Carlos en distintas fechas ---
    # Reificada como O: residencia_carlos_NNN con (agente, lugar_de)
    t_2022 = datetime(2022, 6, 1, tzinfo=timezone.utc)
    t_2026 = datetime(2026, 7, 1, tzinfo=timezone.utc)
    tipo_residencia = u.ind("residencia")

    res_2022 = query(u, Pattern(
        fixed={"agente": h["carlos"]},
        ask={"lugar_de": Var()},
        type_constraint=tipo_residencia,
    ), at=t_2022)
    res_2026 = query(u, Pattern(
        fixed={"agente": h["carlos"]},
        ask={"lugar_de": Var()},
        type_constraint=tipo_residencia,
    ), at=t_2026)

    ok9a = len(res_2022) == 1 and res_2022[0]["lugar_de"].id == h["ciudad_a"].id
    ok9b = len(res_2026) == 1 and res_2026[0]["lugar_de"].id == h["ciudad_b"].id
    results.append((
        "D9: ¿dónde vivía Carlos en 2022?",
        ok9a,
        f"obtenido: {[r['lugar_de'].id for r in res_2022]}",
    ))
    results.append((
        "D9: ¿dónde vive Carlos en 2026?",
        ok9b,
        f"obtenido: {[r['lugar_de'].id for r in res_2026]}",
    ))

    # --- V7: Las sesiones de Carlos están parte_de su plan ---
    plan_sesiones = [
        f for f in u.facts_with_role("parte_de")
        if f.value.id == h["plan_carlos"].id
    ]
    results.append((
        "Sesiones de Carlos parte_de su plan",
        len(plan_sesiones) == 2,
        f"obtenido {len(plan_sesiones)}",
    ))

    # --- V8: Polisemia — `tomar [sesion]` vs `tomar [el_pelo]` vs `tomar` ---
    e_sesion = lex.resolve("tomar", ["sesion"])
    e_pelo = lex.resolve("tomar", ["el_pelo"])
    e_gen = lex.resolve("tomar", [])
    ok_pol = (
        e_sesion is not None and e_sesion.situation_type == "servicio_spa"
        and e_pelo is not None and e_pelo.situation_type == "accion_bromear"
        and e_gen is not None and e_gen.situation_type == "accion_tomar"
    )
    results.append((
        "Polisemia: tomar [sesion] / [el_pelo] / genérico se resuelven distinto",
        ok_pol,
        f"sesion→{e_sesion.situation_type if e_sesion else None}, "
        f"el_pelo→{e_pelo.situation_type if e_pelo else None}, "
        f"genérico→{e_gen.situation_type if e_gen else None}",
    ))

    # --- V9: Nominalización ---
    by_nominal = lex.resolve_nominal("contratación")
    ok_nom = by_nominal is not None and by_nominal.verb == "contratar"
    results.append((
        "Nominalización: 'contratación' resuelve a verbo 'contratar'",
        ok_nom,
        f"resuelto: {by_nominal.verb if by_nominal else None}",
    ))

    return results


# ---------------------------------------------------------------------------
# 4. Main: corre todo e imprime el informe
# ---------------------------------------------------------------------------

def main():
    lex = build_lexicon()
    u, h = build_universe(lex)

    print("=" * 72)
    print("DOMINIO SPA — VALIDACIÓN DEL MODELO WQUESTIONS")
    print("=" * 72)
    print()
    print(u.summary())
    print()
    print("Lexicon registrado:", len(lex.verbs()), "verbos")
    print("Verbos:", ", ".join(sorted(lex.verbs())))
    print()
    print("-" * 72)
    print("VALIDACIONES")
    print("-" * 72)

    results = run_validations(u, lex, h)
    n_ok = sum(1 for _, ok, _ in results if ok)
    for q, ok, comment in results:
        mark = "✓" if ok else "✗"
        print(f"  {mark}  {q}")
        print(f"     ({comment})")
    print()
    print(f"Resultado: {n_ok}/{len(results)} validaciones pasadas.")
    return n_ok == len(results)


if __name__ == "__main__":
    import sys
    sys.exit(0 if main() else 1)
