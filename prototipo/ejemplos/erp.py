"""Dominio ERP — sistema empresarial integral.

Stress-test multi-módulo:
- Jerarquía organizacional recursiva con `reporta_a`.
- BOM (Bill of Materials) — producto compuesto por subproductos
  conectados con `parte_de`.
- Venta cross-módulo: una sola venta genera tres sub-situaciones
  (movimiento de inventario, asiento contable, comisión del vendedor)
  ligadas por `parte_de`.
- Workflow de aprobación con estados bitemporales (D6).
- Orden de producción que consume materia prima y genera producto terminado.
- Audit trail bitemporal del salario de un empleado.
"""

from __future__ import annotations
from datetime import datetime, timezone
from typing import Tuple

from wq import (
    Axis, Individual, Universe, Catalog, Lexicon, LexiconEntry,
    Pattern, Var, query, count, ingest_situation, category,
)


# ---------------------------------------------------------------------------
# Lexicon del dominio ERP
# ---------------------------------------------------------------------------

def build_lexicon() -> Lexicon:
    lex = Lexicon()
    for verb, st, obl, opt in [
        ("vender", "accion_vender",
            ["agente", "tema", "cliente", "monto", "unidad"],
            ["momento", "lugar_de", "por_cuanto"]),
        ("ordenar_compra", "accion_ordenar_compra",
            ["agente", "tema", "monto", "unidad", "beneficiario"],
            ["momento", "justificado_por", "motivado_por"]),
        ("aprobar", "accion_aprobar",
            ["agente", "tema"],
            ["motivado_por", "justificado_por", "momento"]),
        ("producir", "accion_producir",
            ["agente", "tema", "cantidad", "unidad"],
            ["momento", "lugar_de", "instrumento"]),
        ("contratar", "accion_contratar",
            ["agente", "beneficiario", "tema", "monto", "unidad"],
            ["momento", "lugar_de", "duracion"]),
        ("ajustar_salario", "accion_ajustar_salario",
            ["agente", "beneficiario", "monto", "unidad"],
            ["momento", "motivado_por", "justificado_por"]),
    ]:
        lex.register(LexiconEntry(verb=verb, situation_type=st,
                                  obligatory=obl, optional=opt))

    lex.register_domain_dialect("erp", {
        "vendedor": "agente",
        "comprador": "cliente",
        "producto": "tema",
        "departamento": "lugar_de",
    })
    return lex


# ---------------------------------------------------------------------------
# Universo
# ---------------------------------------------------------------------------

def at(iso: str) -> Individual:
    dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    return Individual(id=f"t_{iso}", axis=Axis.T, label=iso, payload=dt)


def n(value: float, unit: str, vid: str) -> Individual:
    return Individual(id=vid, axis=Axis.N,
                      label=f"{value} {unit}",
                      payload={"value": value, "unit": unit})


def build_universe(lex: Lexicon) -> Tuple[Universe, dict]:
    cat = Catalog()
    u = Universe(name="erp", catalog=cat)

    # === K — Categorías ===
    usd = u.add_individual(category("Currency:USD"))
    unidad_pza = u.add_individual(category("Unit:Pieza"))
    unidad_kg = u.add_individual(category("Unit:Kilogramo"))
    unidad_hr = u.add_individual(category("Unit:Hora"))
    real = u.add_individual(category("real"))
    activo = u.add_individual(category("activo"))
    borrador = u.add_individual(category("borrador"))
    pendiente_aprob = u.add_individual(category("pendiente_aprobacion"))
    aprobada = u.add_individual(category("aprobada"))
    finalizada = u.add_individual(category("finalizada"))

    # === Q — Empleados y la empresa ===
    empresa = u.add_individual(Individual(
        id="empresa_acme", axis=Axis.Q, label="ACME S.A."))
    carlos = u.add_individual(Individual(
        id="emp_carlos", axis=Axis.Q, label="Carlos Director"))
    maria = u.add_individual(Individual(
        id="emp_maria", axis=Axis.Q, label="María Gerente"))
    pedro = u.add_individual(Individual(
        id="emp_pedro", axis=Axis.Q, label="Pedro Vendedor"))
    laura = u.add_individual(Individual(
        id="emp_laura", axis=Axis.Q, label="Laura Producción"))
    cliente_betauto = u.add_individual(Individual(
        id="cliente_betauto", axis=Axis.Q, label="BetAuto S.A."))
    proveedor_acero = u.add_individual(Individual(
        id="prov_acero_norte", axis=Axis.Q, label="Acero del Norte"))

    # === L — Departamentos y lugares físicos ===
    dpto_ventas = u.add_individual(Individual(
        id="dpto_ventas", axis=Axis.L, label="Departamento de Ventas"))
    dpto_produccion = u.add_individual(Individual(
        id="dpto_produccion", axis=Axis.L, label="Departamento de Producción"))
    almacen_central = u.add_individual(Individual(
        id="almacen_central", axis=Axis.L, label="Almacén Central"))

    # ====================================================================
    # CASO 1 — Jerarquía organizacional (reporta_a recursivo)
    # ====================================================================
    # Pedro y Laura reportan a María; María reporta a Carlos.
    u.assert_fact(pedro, "reporta_a", maria)
    u.assert_fact(laura, "reporta_a", maria)
    u.assert_fact(maria, "reporta_a", carlos)
    u.assert_fact(carlos, "reporta_a", empresa)

    # Asignación a departamentos
    u.assert_fact(pedro, "trabaja_en", dpto_ventas)
    u.assert_fact(laura, "trabaja_en", dpto_produccion)
    u.assert_fact(maria, "trabaja_en", dpto_ventas)

    # ====================================================================
    # CASO 2 — BOM (Bill of Materials) recursivo: una bicicleta
    # ====================================================================
    bicicleta = u.add_individual(Individual(
        id="prod_bicicleta_mtb", axis=Axis.O,
        label="Bicicleta MTB modelo X"))
    u.assert_fact(bicicleta, "instancia_de",
                  u.add_individual(category("tipo_producto_terminado")))

    cuadro = u.add_individual(Individual(
        id="prod_cuadro_aluminio", axis=Axis.O, label="Cuadro de aluminio"))
    u.assert_fact(cuadro, "instancia_de",
                  u.add_individual(category("tipo_subproducto")))
    u.assert_fact(cuadro, "parte_de", bicicleta)

    rueda = u.add_individual(Individual(
        id="prod_rueda_completa", axis=Axis.O, label="Rueda completa"))
    u.assert_fact(rueda, "instancia_de",
                  u.add_individual(category("tipo_subproducto")))
    u.assert_fact(rueda, "parte_de", bicicleta)
    # Una bicicleta lleva dos ruedas → modelamos la cantidad sobre el enlace
    u.assert_fact(rueda, "cantidad_en_bom", n(2, "unidades", "n_2_uds_rueda"))

    llanta = u.add_individual(Individual(
        id="prod_llanta_26", axis=Axis.O, label="Llanta 26 pulgadas"))
    u.assert_fact(llanta, "instancia_de",
                  u.add_individual(category("tipo_componente")))
    u.assert_fact(llanta, "parte_de", rueda)

    rayos = u.add_individual(Individual(
        id="prod_rayos", axis=Axis.O, label="Set de 36 rayos"))
    u.assert_fact(rayos, "instancia_de",
                  u.add_individual(category("tipo_componente")))
    u.assert_fact(rayos, "parte_de", rueda)

    # Materia prima a nivel más bajo: acero para los rayos
    acero = u.add_individual(Individual(
        id="mp_acero_inox", axis=Axis.O, label="Acero inoxidable"))
    u.assert_fact(acero, "instancia_de",
                  u.add_individual(category("tipo_materia_prima")))
    u.assert_fact(acero, "parte_de", rayos)

    # ====================================================================
    # CASO 3 — Venta cross-módulo (3 sub-situaciones simultáneas)
    # ====================================================================
    venta = ingest_situation(u, lex, "vender", roles={
        "agente": pedro,
        "tema": bicicleta,
        "cliente": cliente_betauto,
        "monto": n(7500, "USD", "n_7500_usd"),
        "unidad": usd,
        "momento": at("2026-07-15T11:20:00+00:00"),
        "lugar_de": dpto_ventas,
    }, extra={"estatus_factual": real}, sit_id="venta_001")
    # La venta fue de 5 unidades (registrado como sub-fact)
    u.assert_fact(venta, "cantidad_vendida", n(5, "unidades", "n_5_uds_venta"))

    # 3.1 — Sub-situación: movimiento de inventario (salida del almacén)
    mov_inv = u.add_individual(Individual(
        id="mov_inventario_001", axis=Axis.O,
        label="Movimiento de inventario"))
    u.assert_fact(mov_inv, "instancia_de",
                  u.add_individual(category("movimiento_inventario_salida")))
    u.assert_fact(mov_inv, "parte_de", venta)
    u.assert_fact(mov_inv, "tema", bicicleta)
    u.assert_fact(mov_inv, "cantidad", n(5, "unidades", "n_5_uds_mov"))
    u.assert_fact(mov_inv, "origen", almacen_central)

    # 3.2 — Sub-situación: asiento contable (registra ingreso)
    asiento = u.add_individual(Individual(
        id="asiento_venta_001", axis=Axis.O,
        label="Asiento contable de la venta"))
    u.assert_fact(asiento, "instancia_de",
                  u.add_individual(category("asiento_contable")))
    u.assert_fact(asiento, "parte_de", venta)
    u.assert_fact(asiento, "monto", n(7500, "USD", "n_7500_usd_asnt"))
    u.assert_fact(asiento, "unidad", usd)
    u.assert_fact(asiento, "tipo_movimiento",
                  u.add_individual(category("ingreso_por_venta")))

    # 3.3 — Sub-situación: comisión del vendedor (5% sobre la venta)
    comision = u.add_individual(Individual(
        id="comision_pedro_001", axis=Axis.O,
        label="Comisión Pedro venta 001"))
    u.assert_fact(comision, "instancia_de",
                  u.add_individual(category("comision_vendedor")))
    u.assert_fact(comision, "parte_de", venta)
    u.assert_fact(comision, "beneficiario", pedro)
    u.assert_fact(comision, "monto", n(375, "USD", "n_375_usd"))
    u.assert_fact(comision, "unidad", usd)
    u.assert_fact(comision, "calculado_segun",
                  u.add_individual(category("politica_comisiones_v2")))

    # ====================================================================
    # CASO 4 — Workflow de aprobación con estados bitemporales (D6)
    # ====================================================================
    oc = ingest_situation(u, lex, "ordenar_compra", roles={
        "agente": laura,
        "tema": acero,
        "monto": n(48000, "USD", "n_48000_usd"),
        "unidad": usd,
        "beneficiario": proveedor_acero,
        "momento": at("2026-07-20T09:00:00+00:00"),
        "motivado_por": u.add_individual(Individual(
            id="forecast_q3_001", axis=Axis.O,
            label="Pronóstico producción Q3")),
    }, sit_id="oc_001")

    # Estados del ciclo de vida: borrador → pendiente → aprobada
    t_creacion = datetime(2026, 7, 20, 9, 0, tzinfo=timezone.utc)
    t_envio_aprob = datetime(2026, 7, 20, 11, 0, tzinfo=timezone.utc)
    t_aprobacion = datetime(2026, 7, 21, 15, 30, tzinfo=timezone.utc)

    u.assert_fact(oc, "estado", borrador,
                  valid_from=t_creacion, valid_to=t_envio_aprob)
    u.assert_fact(oc, "estado", pendiente_aprob,
                  valid_from=t_envio_aprob, valid_to=t_aprobacion)
    u.assert_fact(oc, "estado", aprobada,
                  valid_from=t_aprobacion)

    # La política que justifica el flujo: órdenes >$30k requieren aprobación del director
    politica_aprobacion = u.add_individual(Individual(
        id="politica_aprob_oc_v4", axis=Axis.O,
        label="Política aprobación OC >$30k"))
    u.assert_fact(politica_aprobacion, "instancia_de",
                  u.add_individual(category("politica_corporativa")))
    u.assert_fact(politica_aprobacion, "umbral",
                  n(30000, "USD", "n_30000_usd"))

    # La aprobación reificada como situación propia
    aprobacion = ingest_situation(u, lex, "aprobar", roles={
        "agente": carlos,
        "tema": oc,
        "momento": at("2026-07-21T15:30:00+00:00"),
        "justificado_por": politica_aprobacion,
    }, sit_id="aprobacion_oc_001")

    # ====================================================================
    # CASO 5 — Orden de producción que consume materia prima
    # ====================================================================
    op = ingest_situation(u, lex, "producir", roles={
        "agente": laura,
        "tema": bicicleta,
        "cantidad": n(50, "unidades", "n_50_uds_op"),
        "unidad": unidad_pza,
        "momento": at("2026-08-05T08:00:00+00:00"),
        "lugar_de": dpto_produccion,
    }, sit_id="op_001")

    # La orden consume materia prima — modelado como sub-situaciones de consumo
    consumo_acero = u.add_individual(Individual(
        id="consumo_acero_op_001", axis=Axis.O,
        label="Consumo de acero para OP 001"))
    u.assert_fact(consumo_acero, "instancia_de",
                  u.add_individual(category("consumo_materia_prima")))
    u.assert_fact(consumo_acero, "parte_de", op)
    u.assert_fact(consumo_acero, "tema", acero)
    u.assert_fact(consumo_acero, "cantidad", n(120, "kg", "n_120_kg"))
    u.assert_fact(consumo_acero, "unidad", unidad_kg)

    # Horas de trabajo invertidas también son una sub-situación de consumo
    consumo_hh = u.add_individual(Individual(
        id="consumo_hh_op_001", axis=Axis.O,
        label="Horas hombre OP 001"))
    u.assert_fact(consumo_hh, "instancia_de",
                  u.add_individual(category("consumo_mano_de_obra")))
    u.assert_fact(consumo_hh, "parte_de", op)
    u.assert_fact(consumo_hh, "cantidad", n(180, "horas", "n_180_hr"))
    u.assert_fact(consumo_hh, "unidad", unidad_hr)
    u.assert_fact(consumo_hh, "ejecutado_por", laura)

    # ====================================================================
    # CASO 6 — Audit trail bitemporal del salario de Pedro
    # ====================================================================
    # Pedro fue contratado con $2.500 mensuales. Subió a $2.800 en abril
    # y luego a $3.200 en agosto. Las consultas bitemporales recuperan el
    # valor vigente en cualquier momento del pasado.
    t_contrato = datetime(2026, 1, 10, tzinfo=timezone.utc)
    t_aumento1 = datetime(2026, 4, 1, tzinfo=timezone.utc)
    t_aumento2 = datetime(2026, 8, 1, tzinfo=timezone.utc)

    u.assert_fact(pedro, "salario_mensual",
                  n(2500, "USD", "n_2500_usd"),
                  valid_from=t_contrato, valid_to=t_aumento1)
    u.assert_fact(pedro, "salario_mensual",
                  n(2800, "USD", "n_2800_usd"),
                  valid_from=t_aumento1, valid_to=t_aumento2)
    u.assert_fact(pedro, "salario_mensual",
                  n(3200, "USD", "n_3200_usd"),
                  valid_from=t_aumento2)

    # Razón del segundo aumento
    eval_desempeno_pedro = u.add_individual(Individual(
        id="eval_desempeno_pedro_q2", axis=Axis.O,
        label="Evaluación de desempeño Q2"))
    u.assert_fact(eval_desempeno_pedro, "instancia_de",
                  u.add_individual(category("evaluacion_desempeno")))
    u.assert_fact(eval_desempeno_pedro, "calificacion",
                  u.add_individual(category("excelente")))
    u.assert_fact(eval_desempeno_pedro, "paciente", pedro)

    ajuste_2 = ingest_situation(u, lex, "ajustar_salario", roles={
        "agente": maria,
        "beneficiario": pedro,
        "monto": n(3200, "USD", "n_3200_usd_aj"),
        "unidad": usd,
        "momento": at("2026-08-01T00:00:00+00:00"),
        "motivado_por": eval_desempeno_pedro,
    }, sit_id="ajuste_salario_pedro_001")

    handles = {
        # personas
        "carlos": carlos, "maria": maria, "pedro": pedro,
        "laura": laura, "cliente_betauto": cliente_betauto,
        "proveedor_acero": proveedor_acero,
        # estructura
        "empresa": empresa, "dpto_ventas": dpto_ventas,
        "dpto_produccion": dpto_produccion,
        # productos
        "bicicleta": bicicleta, "rueda": rueda, "llanta": llanta,
        "rayos": rayos, "acero": acero, "cuadro": cuadro,
        # situaciones
        "venta": venta, "mov_inv": mov_inv, "asiento": asiento,
        "comision": comision, "oc": oc, "aprobacion": aprobacion,
        "op": op, "consumo_acero": consumo_acero, "consumo_hh": consumo_hh,
        "ajuste_2": ajuste_2, "eval_desempeno_pedro": eval_desempeno_pedro,
        # categorías
        "borrador": borrador, "pendiente_aprob": pendiente_aprob,
        "aprobada": aprobada, "usd": usd,
    }
    return u, handles


# ---------------------------------------------------------------------------
# Validaciones
# ---------------------------------------------------------------------------

def run_validations(u: Universe, lex: Lexicon, h: dict):
    results = []

    # V1 — Jerarquía organizacional: Pedro → María → Carlos
    pedro_jefe = [f for f in u.facts_about(h["pedro"]) if f.role == "reporta_a"]
    maria_jefe = [f for f in u.facts_about(h["maria"]) if f.role == "reporta_a"]
    results.append((
        "Jerarquía: Pedro reporta a María, María a Carlos",
        len(pedro_jefe) == 1 and pedro_jefe[0].value.id == "emp_maria"
        and len(maria_jefe) == 1 and maria_jefe[0].value.id == "emp_carlos",
        f"Pedro→{[f.value.id for f in pedro_jefe]}, "
        f"María→{[f.value.id for f in maria_jefe]}",
    ))

    # V2 — BOM recursivo: el acero está parte_de rayos parte_de rueda parte_de bicicleta
    def chain_to_root(start: Individual) -> list:
        """Recorre `parte_de` recursivamente hasta el tope."""
        chain = [start.id]
        cur = start
        for _ in range(10):  # tope contra ciclos
            ups = [f.value for f in u.facts_about(cur) if f.role == "parte_de"]
            if not ups:
                break
            cur = ups[0]
            chain.append(cur.id)
        return chain

    cadena = chain_to_root(h["acero"])
    expected = ["mp_acero_inox", "prod_rayos", "prod_rueda_completa",
                "prod_bicicleta_mtb"]
    results.append((
        "BOM recursivo: acero → rayos → rueda → bicicleta",
        cadena == expected,
        f"cadena: {' → '.join(cadena)}",
    ))

    # V3 — Venta cross-módulo: la venta tiene exactamente 3 sub-situaciones
    sub_situaciones = [
        f.subject for f in u.facts_with_role("parte_de")
        if f.value.id == h["venta"].id
    ]
    tipos_sub = set()
    for sub in sub_situaciones:
        for f in u.facts_about(sub):
            if f.role == "instancia_de":
                tipos_sub.add(f.value.id)
    expected_tipos = {"movimiento_inventario_salida",
                      "asiento_contable",
                      "comision_vendedor"}
    results.append((
        "Venta cross-módulo: 3 sub-situaciones (inventario + asiento + comisión)",
        len(sub_situaciones) == 3 and tipos_sub == expected_tipos,
        f"sub-situaciones: {sorted(s.id for s in sub_situaciones)}",
    ))

    # V4 — D6: el estado de la OC el 20 julio 13h (zona pendiente) es "pendiente"
    t_check_pend = datetime(2026, 7, 20, 13, 0, tzinfo=timezone.utc)
    t_check_aprob = datetime(2026, 7, 22, 10, 0, tzinfo=timezone.utc)
    estado_pend = [f for f in u.facts_about(h["oc"], at=t_check_pend)
                   if f.role == "estado"]
    estado_aprob = [f for f in u.facts_about(h["oc"], at=t_check_aprob)
                    if f.role == "estado"]
    results.append((
        "D6: OC pendiente_aprobacion el 20-Jul 13:00",
        len(estado_pend) == 1
        and estado_pend[0].value.id == "pendiente_aprobacion",
        f"obtenido: {[f.value.id for f in estado_pend]}",
    ))
    results.append((
        "D6: OC aprobada el 22-Jul",
        len(estado_aprob) == 1 and estado_aprob[0].value.id == "aprobada",
        f"obtenido: {[f.value.id for f in estado_aprob]}",
    ))

    # V5 — D7: la aprobación está justificada por la política corporativa
    facts_aprob = u.facts_about(h["aprobacion"])
    justif = [f for f in facts_aprob if f.role == "justificado_por"]
    results.append((
        "D7: la aprobación está justificada_por la política corporativa",
        len(justif) == 1 and justif[0].value.id == "politica_aprob_oc_v4",
        f"justif: {[f.value.id for f in justif]}",
    ))

    # V6 — Producción consume materia prima y mano de obra
    consumos = [
        f.subject for f in u.facts_with_role("parte_de")
        if f.value.id == h["op"].id
    ]
    tipos_consumo = set()
    for c in consumos:
        for f in u.facts_about(c):
            if f.role == "instancia_de":
                tipos_consumo.add(f.value.id)
    results.append((
        "Producción: consume materia prima + mano de obra",
        tipos_consumo == {"consumo_materia_prima", "consumo_mano_de_obra"},
        f"consumos: {sorted(tipos_consumo)}",
    ))

    # V7 — Audit trail bitemporal del salario de Pedro
    t_marzo = datetime(2026, 3, 15, tzinfo=timezone.utc)
    t_junio = datetime(2026, 6, 15, tzinfo=timezone.utc)
    t_septiembre = datetime(2026, 9, 15, tzinfo=timezone.utc)

    def salario_at(when):
        return [
            f for f in u.facts_about(h["pedro"], at=when)
            if f.role == "salario_mensual"
        ]
    s_marzo = salario_at(t_marzo)
    s_junio = salario_at(t_junio)
    s_septiembre = salario_at(t_septiembre)
    ok_audit = (
        len(s_marzo) == 1 and s_marzo[0].value.payload["value"] == 2500
        and len(s_junio) == 1 and s_junio[0].value.payload["value"] == 2800
        and len(s_septiembre) == 1
        and s_septiembre[0].value.payload["value"] == 3200
    )
    results.append((
        "Audit trail bitemporal (D6): salario en marzo=2500, junio=2800, sept=3200",
        ok_audit,
        f"marzo={s_marzo[0].value.payload['value'] if s_marzo else None}, "
        f"junio={s_junio[0].value.payload['value'] if s_junio else None}, "
        f"sept={s_septiembre[0].value.payload['value'] if s_septiembre else None}",
    ))

    # V8 — WH: ¿quién aprobó la OC?
    r = query(u, Pattern(
        fixed={"tema": h["oc"]},
        ask={"agente": Var()},
        type_constraint=u.ind("accion_aprobar"),
    ))
    results.append((
        "WH: ¿quién aprobó la orden de compra?",
        len(r) == 1 and r[0]["agente"].id == "emp_carlos",
        f"agente: {[x['agente'].id for x in r]}",
    ))

    # V9 — WH: ¿cuánto se vendió a BetAuto?
    r = query(u, Pattern(
        fixed={"cliente": h["cliente_betauto"]},
        ask={"monto": Var()},
        type_constraint=u.ind("accion_vender"),
    ))
    results.append((
        "WH: ¿cuánto se le vendió a BetAuto?",
        len(r) == 1 and r[0]["monto"].payload["value"] == 7500,
        f"monto: {[x['monto'].payload['value'] for x in r]}",
    ))

    # V10 — D5: el ajuste de salario tiene a María como agente, no a Pedro
    facts_aj = u.facts_about(h["ajuste_2"])
    agentes_aj = [f.value.id for f in facts_aj if f.role == "agente"]
    benef_aj = [f.value.id for f in facts_aj if f.role == "beneficiario"]
    results.append((
        "D5: ajuste de salario — agente=María, beneficiario=Pedro",
        agentes_aj == ["emp_maria"] and benef_aj == ["emp_pedro"],
        f"agente={agentes_aj}, beneficiario={benef_aj}",
    ))

    # V11 — La comisión del vendedor se calcula contra una política
    facts_com = u.facts_about(h["comision"])
    pol = [f for f in facts_com if f.role == "calculado_segun"]
    results.append((
        "Política liberal: rol de dominio `calculado_segun` admitido sin declarar",
        len(pol) == 1 and pol[0].value.id == "politica_comisiones_v2",
        f"política: {[f.value.id for f in pol]}",
    ))

    return results


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main() -> bool:
    lex = build_lexicon()
    u, h = build_universe(lex)

    print("=" * 72)
    print("DOMINIO ERP — sistema empresarial integral")
    print("=" * 72)
    print()
    print(u.summary())
    print()

    results = run_validations(u, lex, h)
    n_ok = sum(1 for _, ok, _ in results if ok)
    for q, ok, c in results:
        mark = "✓" if ok else "✗"
        print(f"  {mark}  {q}")
        print(f"       {c}")
    print()
    print(f"Resultado: {n_ok}/{len(results)} validaciones pasadas.")
    return n_ok == len(results)


if __name__ == "__main__":
    import sys
    sys.exit(0 if main() else 1)
