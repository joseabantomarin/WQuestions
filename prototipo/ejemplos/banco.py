"""Dominio banco — el más exigente de todos los modelados.

Stress-test industrial:
- Transferencia con 5 agentes (cliente, sistema, antifraude, beneficiario, banco)
  y 2 asientos contables como sub-situaciones (parte_de).
- Ciclo de vida de préstamo con D9: vigente → mora → reestructurado.
- Investigación de fraude reconstruyendo el pasado.
- Oferta comercial reificada (Visa Platinum) + instancia de tarjeta del cliente.
"""

from __future__ import annotations
from datetime import datetime, timezone, timedelta
from typing import List, Tuple

from wq import (
    Axis, Individual, Universe, Catalog, Lexicon, LexiconEntry,
    Pattern, Var, query, count, ingest_situation, category, mint_id,
)


def build_lexicon() -> Lexicon:
    lex = Lexicon()
    for verb, st, obl, opt in [
        ("transferir",  "accion_transferir",
            ["agente", "beneficiario", "cuenta_origen",
             "cuenta_destino", "monto", "unidad"],
            ["momento", "lugar_de", "verificado_por"]),
        ("autorizar",   "accion_autorizar_tarjeta",
            ["agente", "tarjeta", "monto", "unidad"],
            ["comercio", "lugar_de", "momento",
             "motivado_por", "justificado_por"]),
        ("otorgar",     "accion_otorgar_prestamo",
            ["agente", "cliente", "tipo_producto",
             "monto_otorgado", "unidad", "tasa_anual",
             "plazo_cuotas"],
            ["momento", "lugar_de"]),
        ("pagar_cuota", "accion_pagar_cuota",
            ["agente", "cuota", "monto", "unidad"],
            ["momento", "lugar_de"]),
        ("reestructurar", "accion_reestructurar",
            ["agente", "cliente", "prestamo_original"],
            ["motivado_por", "justificado_por", "momento"]),
        ("investigar",  "investigacion_fraude",
            ["agente"],
            ["motivado_por", "tema", "conclusion", "momento"]),
    ]:
        lex.register(LexiconEntry(verb=verb, situation_type=st,
                                  obligatory=obl, optional=opt))

    lex.register_domain_dialect("banco", {
        "cliente": "agente",
        "deudor": "agente",
    })
    return lex


def build_universe(lex: Lexicon) -> Tuple[Universe, dict]:
    cat = Catalog()
    u = Universe(name="banco", catalog=cat)

    # === Q ===
    ana = u.add_individual(Individual(id="cli_ana", axis=Axis.Q, label="Ana"))
    beto = u.add_individual(Individual(id="cli_beto", axis=Axis.Q, label="Beto"))
    banco_org = u.add_individual(Individual(id="banco_omega", axis=Axis.Q,
                                            label="Banco Omega S.A."))
    motor_antifraude = u.add_individual(Individual(
        id="motor_antifraude_v7", axis=Axis.Q,
        label="Motor antifraude v7"))
    autorizador = u.add_individual(Individual(
        id="autorizador_visa_v3", axis=Axis.Q,
        label="Autorizador Visa v3"))

    # === L ===
    web_banking = u.add_individual(Individual(
        id="canal_web_banking", axis=Axis.L, label="Web banking"))
    sucursal_centro = u.add_individual(Individual(
        id="sucursal_centro", axis=Axis.L, label="Sucursal Centro"))
    las_vegas = u.add_individual(Individual(
        id="loc_las_vegas", axis=Axis.L, label="Las Vegas"))

    # === K ===
    usd = u.add_individual(category("Currency:USD"))
    pct = u.add_individual(category("Unit:Percent"))
    real = u.add_individual(category("real"))
    ejecutada = u.add_individual(category("ejecutada"))
    vigente = u.add_individual(category("vigente"))
    mora_30 = u.add_individual(category("mora_30"))
    mora_60 = u.add_individual(category("mora_60"))
    reestructurado = u.add_individual(category("reestructurado"))
    cancelada = u.add_individual(category("cancelada"))
    activa = u.add_individual(category("activa"))
    debito = u.add_individual(category("debito"))
    credito = u.add_individual(category("credito"))

    # === O — ofertas reificadas ===
    visa_platinum_q1 = u.add_individual(Individual(
        id="visa_platinum_oferta_2026q1", axis=Axis.O,
        label="Visa Platinum 2026Q1"))
    u.assert_fact(visa_platinum_q1, "instancia_de",
                  u.add_individual(category("tipo_oferta_tarjeta")))
    u.assert_fact(visa_platinum_q1, "marca",
                  u.add_individual(category("Visa")))
    u.assert_fact(visa_platinum_q1, "segmento",
                  u.add_individual(category("Platinum")),
                  valid_from=datetime(2026,1,1, tzinfo=timezone.utc),
                  valid_to=datetime(2026,6,30, tzinfo=timezone.utc))

    pp_36m = u.add_individual(Individual(
        id="oferta_pp_tasa_fija_36m", axis=Axis.O,
        label="PP Tasa Fija 36m"))
    u.assert_fact(pp_36m, "instancia_de",
                  u.add_individual(category("tipo_oferta_prestamo")))

    # === O — cuentas ===
    cta_ana = u.add_individual(Individual(id="cta_ana_001", axis=Axis.O,
                                          label="Cuenta ahorros Ana"))
    u.assert_fact(cta_ana, "instancia_de",
                  u.add_individual(category("cuenta_ahorros")))
    u.assert_fact(cta_ana, "cliente", ana)

    cta_beto = u.add_individual(Individual(id="cta_beto_007", axis=Axis.O,
                                           label="Cuenta ahorros Beto"))
    u.assert_fact(cta_beto, "instancia_de", u.ind("cuenta_ahorros"))
    u.assert_fact(cta_beto, "cliente", beto)

    # === T helper ===
    def at(iso: str) -> Individual:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return Individual(id=f"t_{iso}", axis=Axis.T,
                          label=iso, payload=dt)

    # ====================================================================
    # CASO 1 — Transferencia con 5 agentes y 2 asientos contables
    # ====================================================================
    monto_500 = u.add_individual(Individual(
        id="n_500_usd", axis=Axis.N, label="500 USD",
        payload={"value": 500, "unit": "USD"}))

    transf = ingest_situation(u, lex, "transferir", roles={
        "agente": ana,
        "beneficiario": beto,
        "cuenta_origen": cta_ana,
        "cuenta_destino": cta_beto,
        "monto": monto_500,
        "unidad": usd,
        "momento": at("2026-06-12T14:32:00+00:00"),
        "lugar_de": web_banking,
        "verificado_por": motor_antifraude,
    }, extra={"estatus_factual": ejecutada}, sit_id="transferencia_001")
    u.assert_fact(transf, "asentado_por", banco_org)  # rol de dominio

    # Asientos contables como sub-situaciones
    asiento_d = u.add_individual(Individual(
        id="asiento_debito_001", axis=Axis.O, label="Asiento débito"))
    u.assert_fact(asiento_d, "instancia_de",
                  u.add_individual(category("asiento_contable")))
    u.assert_fact(asiento_d, "parte_de", transf)
    u.assert_fact(asiento_d, "cuenta_origen", cta_ana)
    u.assert_fact(asiento_d, "monto", monto_500)
    u.assert_fact(asiento_d, "unidad", usd)
    u.assert_fact(asiento_d, "tipo_movimiento", debito)

    asiento_c = u.add_individual(Individual(
        id="asiento_credito_001", axis=Axis.O, label="Asiento crédito"))
    u.assert_fact(asiento_c, "instancia_de", u.ind("asiento_contable"))
    u.assert_fact(asiento_c, "parte_de", transf)
    u.assert_fact(asiento_c, "cuenta_destino", cta_beto)
    u.assert_fact(asiento_c, "monto", monto_500)
    u.assert_fact(asiento_c, "unidad", usd)
    u.assert_fact(asiento_c, "tipo_movimiento", credito)

    # ====================================================================
    # CASO 2 — Ciclo de vida de préstamo: vigente → mora_30 → reestructurado
    # ====================================================================
    monto_5000 = u.add_individual(Individual(
        id="n_5000_usd", axis=Axis.N, label="5000 USD",
        payload={"value": 5000, "unit": "USD"}))
    tasa_18 = u.add_individual(Individual(
        id="n_18_pct", axis=Axis.N, label="18%",
        payload={"value": 18, "unit": "Percent"}))

    prestamo = ingest_situation(u, lex, "otorgar", roles={
        "agente": banco_org,
        "cliente": ana,
        "tipo_producto": pp_36m,
        "monto_otorgado": monto_5000,
        "unidad": usd,
        "tasa_anual": tasa_18,
        "plazo_cuotas": u.add_individual(Individual(
            id="n_36_cuotas", axis=Axis.N, label="36 cuotas",
            payload={"value": 36, "unit": "cuotas"})),
        "momento": at("2026-01-15T10:00:00+00:00"),
        "lugar_de": sucursal_centro,
    }, sit_id="prestamo_personal_017")

    # D9: cambios de estado del préstamo
    t_vig_start = datetime(2026,1,15, tzinfo=timezone.utc)
    t_mora30 = datetime(2026,8,10, tzinfo=timezone.utc)
    t_mora60 = datetime(2026,9,10, tzinfo=timezone.utc)
    t_reest = datetime(2026,10,15, tzinfo=timezone.utc)

    u.assert_fact(prestamo, "estado", vigente,
                  valid_from=t_vig_start, valid_to=t_mora30)
    u.assert_fact(prestamo, "estado", mora_30,
                  valid_from=t_mora30, valid_to=t_mora60)
    u.assert_fact(prestamo, "estado", mora_60,
                  valid_from=t_mora60, valid_to=t_reest)
    u.assert_fact(prestamo, "estado", reestructurado,
                  valid_from=t_reest)

    # Reestructuración como préstamo nuevo
    politica_reest = u.add_individual(Individual(
        id="politica_reestructuracion_v3", axis=Axis.O,
        label="Política de reestructuración v3"))
    u.assert_fact(politica_reest, "instancia_de",
                  u.add_individual(category("politica_riesgo")))

    mora_017 = u.add_individual(Individual(
        id="mora_017", axis=Axis.O, label="Mora préstamo 017"))
    u.assert_fact(mora_017, "instancia_de", mora_60)
    u.assert_fact(mora_017, "parte_de", prestamo)

    prestamo_re = u.add_individual(Individual(
        id="prestamo_017_re", axis=Axis.O,
        label="Préstamo reestructurado"))
    u.assert_fact(prestamo_re, "instancia_de",
                  u.add_individual(category("prestamo_personal")))
    u.assert_fact(prestamo_re, "agente", banco_org)
    u.assert_fact(prestamo_re, "cliente", ana)
    u.assert_fact(prestamo_re, "motivado_por", mora_017)
    u.assert_fact(prestamo_re, "justificado_por", politica_reest)
    u.assert_fact(prestamo_re, "rectifica", prestamo)

    # ====================================================================
    # CASO 3 — Investigación de fraude
    # ====================================================================
    tarjeta_ana = u.add_individual(Individual(
        id="tarjeta_visa_ana_001", axis=Axis.O,
        label="Tarjeta Visa Ana"))
    u.assert_fact(tarjeta_ana, "instancia_de",
                  u.add_individual(category("tarjeta_credito")))
    u.assert_fact(tarjeta_ana, "cliente", ana)
    u.assert_fact(tarjeta_ana, "cubierto_por", visa_platinum_q1)
    u.assert_fact(tarjeta_ana, "estado", activa,
                  valid_from=datetime(2026,3,15, tzinfo=timezone.utc))

    # Perfil de riesgo con vigencia D9
    perfil_v3 = u.add_individual(Individual(
        id="perfil_riesgo_ana_v3", axis=Axis.O,
        label="Perfil riesgo Ana v3"))
    u.assert_fact(perfil_v3, "instancia_de",
                  u.add_individual(category("perfil_antifraude")),
                  valid_from=datetime(2026,4,10, tzinfo=timezone.utc),
                  valid_to=datetime(2026,5,22, tzinfo=timezone.utc))

    # Autorización (la noche del 20 de mayo)
    monto_1840 = u.add_individual(Individual(
        id="n_1840_usd", axis=Axis.N, label="1840 USD",
        payload={"value": 1840, "unit": "USD"}))
    autorizacion = ingest_situation(u, lex, "autorizar", roles={
        "agente": autorizador,
        "tarjeta": tarjeta_ana,
        "monto": monto_1840,
        "unidad": usd,
        "comercio": u.add_individual(category("Liquor_Store_XX")),
        "lugar_de": las_vegas,
        "momento": at("2026-05-20T21:47:00+00:00"),
        "justificado_por": perfil_v3,
    }, sit_id="autorizacion_001")

    # Reclamo + investigación
    reclamo = u.add_individual(Individual(
        id="reclamo_ana_001", axis=Axis.O, label="Reclamo Ana"))
    u.assert_fact(reclamo, "instancia_de",
                  u.add_individual(category("reclamo_cliente")))
    u.assert_fact(reclamo, "agente", ana)
    u.assert_fact(reclamo, "tema", autorizacion)
    u.assert_fact(reclamo, "momento",
                  at("2026-05-25T09:00:00+00:00"))

    investigacion = ingest_situation(u, lex, "investigar", roles={
        "agente": u.add_individual(Individual(
            id="equipo_fraude", axis=Axis.Q, label="Equipo fraude")),
        "motivado_por": reclamo,
        "tema": autorizacion,
        "conclusion": u.add_individual(category("fraude_confirmado")),
        "momento": at("2026-06-10T10:00:00+00:00"),
    }, sit_id="investigacion_fraude_001")

    # Reverso
    reverso = u.add_individual(Individual(
        id="reverso_autorizacion_001", axis=Axis.O,
        label="Reverso autorización fraudulenta"))
    u.assert_fact(reverso, "instancia_de",
                  u.add_individual(category("reverso_autorizacion")))
    u.assert_fact(reverso, "cancela", autorizacion)
    u.assert_fact(reverso, "justificado_por", investigacion)

    h = {
        "ana": ana, "beto": beto, "banco": banco_org,
        "motor_antifraude": motor_antifraude, "autorizador": autorizador,
        "cta_ana": cta_ana, "cta_beto": cta_beto,
        "transf": transf, "asiento_d": asiento_d, "asiento_c": asiento_c,
        "prestamo": prestamo, "prestamo_re": prestamo_re,
        "mora_017": mora_017, "politica_reest": politica_reest,
        "tarjeta_ana": tarjeta_ana, "visa_platinum_q1": visa_platinum_q1,
        "autorizacion": autorizacion, "investigacion": investigacion,
        "reverso": reverso, "reclamo": reclamo,
        "vigente": vigente, "mora_30": mora_30,
        "reestructurado": reestructurado,
    }
    return u, h


def run_validations(u: Universe, lex: Lexicon, h: dict):
    results = []

    # V1: la transferencia tiene los 5 participantes esperados
    facts_t = u.facts_about(h["transf"])
    roles_t = {f.role for f in facts_t}
    expected = {"agente", "beneficiario", "cuenta_origen",
                "cuenta_destino", "verificado_por", "asentado_por"}
    results.append((
        "Transferencia con 5 participantes (cliente + beneficiario + 2 cuentas + antifraude + banco)",
        expected.issubset(roles_t),
        f"presentes: {sorted(roles_t & expected)}",
    ))

    # V2: los dos asientos contables están parte_de la transferencia
    asientos = [f for f in u.facts_with_role("parte_de")
                if f.value.id == h["transf"].id
                and f.subject.label.startswith("Asiento")]
    results.append((
        "2 asientos contables parte_de la transferencia",
        len(asientos) == 2,
        f"asientos: {[f.subject.id for f in asientos]}",
    ))

    # V3: D9 — el préstamo atraviesa cuatro estados según la fecha
    t_ago_25 = datetime(2026, 8, 25, tzinfo=timezone.utc)   # debería ser mora_30
    t_nov_20 = datetime(2026, 11, 20, tzinfo=timezone.utc)  # debería ser reestructurado
    estado_ago = [f for f in u.facts_about(h["prestamo"], at=t_ago_25)
                  if f.role == "estado"]
    estado_nov = [f for f in u.facts_about(h["prestamo"], at=t_nov_20)
                  if f.role == "estado"]
    ok_ago = (len(estado_ago) == 1
              and estado_ago[0].value.id == "mora_30")
    ok_nov = (len(estado_nov) == 1
              and estado_nov[0].value.id == "reestructurado")
    results.append((
        "D9: préstamo en mora_30 el 25-Ago-2026",
        ok_ago,
        f"obtenido: {[f.value.id for f in estado_ago]}",
    ))
    results.append((
        "D9: préstamo reestructurado el 20-Nov-2026",
        ok_nov,
        f"obtenido: {[f.value.id for f in estado_nov]}",
    ))

    # V4: reestructuración con motivado_por + justificado_por + rectifica
    facts_re = u.facts_about(h["prestamo_re"])
    motivos = [f for f in facts_re if f.role == "motivado_por"]
    justif = [f for f in facts_re if f.role == "justificado_por"]
    rect = [f for f in facts_re if f.role == "rectifica"]
    results.append((
        "Reestructuración: motivado_por mora + justificado_por política + rectifica original",
        (len(motivos) == 1 and motivos[0].value.id == "mora_017"
         and len(justif) == 1
         and justif[0].value.id == "politica_reestructuracion_v3"
         and len(rect) == 1
         and rect[0].value.id == "prestamo_personal_017"),
        f"motivos={[f.value.id for f in motivos]}, "
        f"justif={[f.value.id for f in justif]}, "
        f"rect={[f.value.id for f in rect]}",
    ))

    # V5: la tarjeta de Ana está cubierta_por la oferta Visa Platinum
    facts_t = u.facts_about(h["tarjeta_ana"])
    cubre = [f for f in facts_t if f.role == "cubierto_por"]
    results.append((
        "Tarjeta como instancia: cubierto_por oferta_visa_platinum_2026q1",
        len(cubre) == 1
        and cubre[0].value.id == "visa_platinum_oferta_2026q1",
        f"cubierto_por: {[f.value.id for f in cubre]}",
    ))

    # V6: el reverso cancela la autorización + justificado_por investigación
    facts_r = u.facts_about(h["reverso"])
    cancela = [f for f in facts_r if f.role == "cancela"]
    justif_r = [f for f in facts_r if f.role == "justificado_por"]
    results.append((
        "Reverso del fraude: cancela autorización + justificado_por investigación",
        (len(cancela) == 1
         and cancela[0].value.id == "autorizacion_001"
         and len(justif_r) == 1
         and justif_r[0].value.id == "investigacion_fraude_001"),
        f"cancela={[f.value.id for f in cancela]}, "
        f"justif={[f.value.id for f in justif_r]}",
    ))

    # V7: la autorización original sigue presente en el grafo (hecho inmutable)
    autorizacion_facts = u.facts_about(h["autorizacion"])
    sigue = any(f.role == "monto" for f in autorizacion_facts)
    results.append((
        "Autorización fraudulenta NO se borra: el hecho permanece (cancelado pero presente)",
        sigue,
        "presente en el grafo, anulada por reverso_autorizacion_001",
    ))

    # V8: investigación motivada_por reclamo
    facts_i = u.facts_about(h["investigacion"])
    motivos = [f for f in facts_i if f.role == "motivado_por"]
    results.append((
        "Investigación motivada_por reclamo del cliente",
        len(motivos) == 1 and motivos[0].value.id == h["reclamo"].id,
        f"motivos: {[f.value.id for f in motivos]}",
    ))

    # V9: el motor_antifraude es Q (agente capaz de actuar)
    results.append((
        "D5: el motor antifraude entra a Q como agente verificador",
        h["motor_antifraude"].axis == Axis.Q,
        f"eje: {h['motor_antifraude'].axis}",
    ))

    # V10: WH — ¿quién hizo la transferencia?
    r = query(u, Pattern(
        fixed={"beneficiario": h["beto"]},
        ask={"agente": Var()},
        type_constraint=u.ind("accion_transferir"),
    ))
    results.append((
        "WH: ¿quién le transfirió a Beto?",
        len(r) == 1 and r[0]["agente"].id == "cli_ana",
        f"agente: {[x['agente'].id for x in r]}",
    ))

    return results


def main():
    lex = build_lexicon()
    u, h = build_universe(lex)

    print("=" * 72)
    print("DOMINIO BANCO — el caso más exigente")
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
