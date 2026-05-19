"""Dominio Municipalidad — gobierno local.

Stress-test del modelo en un dominio donde la autoridad normativa
está en cada paso:

- Licencia de funcionamiento: solicitud → revisión → emisión, todas
  justificadas por ordenanzas.
- Subdivisiones territoriales (L jerárquica: distrito → barrio → manzana → lote).
- Denuncia ciudadana que dispara un expediente con varios actos administrativos.
- Multa de tránsito con cadena causal completa.
- Recurso de reconsideración que rectifica una resolución previa.
"""

from __future__ import annotations
from datetime import datetime, timezone
from typing import Tuple

from wq import (
    Axis, Individual, Universe, Catalog, Lexicon, LexiconEntry,
    Pattern, Var, query, count, ingest_situation, category,
)


def at(iso: str) -> Individual:
    dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    return Individual(id=f"t_{iso}", axis=Axis.T, label=iso, payload=dt)


def n(value: float, unit: str, vid: str) -> Individual:
    return Individual(id=vid, axis=Axis.N,
                      label=f"{value} {unit}",
                      payload={"value": value, "unit": unit})


# ---------------------------------------------------------------------------
# Lexicon municipal
# ---------------------------------------------------------------------------

def build_lexicon() -> Lexicon:
    lex = Lexicon()
    for verb, st, obl, opt in [
        ("solicitar", "accion_solicitar_licencia",
            ["agente", "tipo_solicitado", "beneficiario"],
            ["momento", "lugar_de", "motivado_por"]),
        ("revisar", "accion_revisar_solicitud",
            ["agente", "tema"],
            ["momento", "conclusion"]),
        ("emitir", "accion_emitir_licencia",
            ["agente", "tipo_emitido", "beneficiario"],
            ["momento", "justificado_por", "valido_desde",
             "valido_hasta"]),
        ("denunciar", "accion_denunciar",
            ["agente", "tema"],
            ["paciente", "lugar_de", "momento", "motivado_por"]),
        ("inspeccionar", "accion_inspeccionar",
            ["agente", "inspeccionado"],
            ["lugar_de", "momento", "conclusion"]),
        ("multar", "accion_multar",
            ["agente", "paciente", "monto", "unidad"],
            ["motivado_por", "justificado_por", "momento",
             "lugar_de", "instrumento"]),
        ("resolver", "accion_resolver_recurso",
            ["agente", "tema", "conclusion"],
            ["motivado_por", "justificado_por", "momento"]),
    ]:
        lex.register(LexiconEntry(verb=verb, situation_type=st,
                                  obligatory=obl, optional=opt))

    lex.register_domain_dialect("municipalidad", {
        "ciudadano": "agente",
        "vecino": "agente",
        "denunciante": "agente",
        "denunciado": "paciente",
        "infractor": "paciente",
    })
    return lex


# ---------------------------------------------------------------------------
# Universo
# ---------------------------------------------------------------------------

def build_universe(lex: Lexicon) -> Tuple[Universe, dict]:
    cat = Catalog()
    u = Universe(name="municipalidad", catalog=cat)

    # === K — Categorías ===
    en_revision = u.add_individual(category("en_revision"))
    aprobada = u.add_individual(category("aprobada"))
    denegada = u.add_individual(category("denegada"))
    real = u.add_individual(category("real"))
    vigente = u.add_individual(category("vigente"))
    suspendida = u.add_individual(category("suspendida"))
    revocada = u.add_individual(category("revocada"))
    procedente = u.add_individual(category("procedente"))
    improcedente = u.add_individual(category("improcedente"))

    # === Q — Personas y entidades ===
    municipalidad = u.add_individual(Individual(
        id="mun_central", axis=Axis.Q,
        label="Municipalidad de Ciudad Norte"))
    alcalde = u.add_individual(Individual(
        id="alcalde_paredes", axis=Axis.Q, label="Alcalde Paredes"))
    inspector1 = u.add_individual(Individual(
        id="insp_torres", axis=Axis.Q, label="Inspector Torres"))
    inspector2 = u.add_individual(Individual(
        id="insp_quispe", axis=Axis.Q, label="Inspector Quispe"))
    policia_mun = u.add_individual(Individual(
        id="poli_mun_001", axis=Axis.Q,
        label="Policía municipal nº 001"))

    # Ciudadanos
    juan = u.add_individual(Individual(
        id="ciud_juan", axis=Axis.Q, label="Juan Mendoza"))
    sofia = u.add_individual(Individual(
        id="ciud_sofia", axis=Axis.Q, label="Sofía Romero"))
    cafe_norte = u.add_individual(Individual(
        id="empresa_cafe_norte", axis=Axis.Q,
        label="Café del Norte SAC"))

    # === L — Subdivisiones territoriales (jerárquicas) ===
    ciudad_norte = u.add_individual(Individual(
        id="ciudad_norte", axis=Axis.L, label="Ciudad Norte"))
    distrito_centro = u.add_individual(Individual(
        id="distrito_centro", axis=Axis.L,
        label="Distrito Centro"))
    barrio_san_jose = u.add_individual(Individual(
        id="barrio_san_jose", axis=Axis.L,
        label="Barrio San José"))
    manzana_12 = u.add_individual(Individual(
        id="manzana_12_sj", axis=Axis.L,
        label="Manzana 12 (San José)"))
    lote_4 = u.add_individual(Individual(
        id="lote_4_m12", axis=Axis.L,
        label="Lote 4 (Mz 12, San José)"))
    av_principal = u.add_individual(Individual(
        id="av_principal", axis=Axis.L,
        label="Avenida Principal"))

    # Jerarquía territorial — `parte_de` canónico es O→O, así que usamos
    # `dentro_de` como rol de dominio (L→L) admitido por política liberal.
    u.assert_fact(distrito_centro, "dentro_de", ciudad_norte)
    u.assert_fact(barrio_san_jose, "dentro_de", distrito_centro)
    u.assert_fact(manzana_12, "dentro_de", barrio_san_jose)
    u.assert_fact(lote_4, "dentro_de", manzana_12)
    u.assert_fact(av_principal, "dentro_de", distrito_centro)

    # ====================================================================
    # CASO 1 — Ordenanzas como autoridad normativa
    # ====================================================================
    # Las ordenanzas viven en O — son objetos normativos con vigencia
    ordenanza_funcionamiento = u.add_individual(Individual(
        id="ord_237_2024_funcionamiento", axis=Axis.O,
        label="Ordenanza 237-2024 (licencias de funcionamiento)"))
    u.assert_fact(ordenanza_funcionamiento, "instancia_de",
                  u.add_individual(category("ordenanza_municipal")))
    u.assert_fact(ordenanza_funcionamiento, "valido_desde",
                  at("2024-06-15T00:00:00+00:00"))
    u.assert_fact(ordenanza_funcionamiento, "emitida_por", municipalidad)
    u.assert_fact(ordenanza_funcionamiento, "tema_normativo",
                  u.add_individual(category("licencias_comerciales")))

    ordenanza_transito = u.add_individual(Individual(
        id="ord_158_2023_transito", axis=Axis.O,
        label="Ordenanza 158-2023 (tránsito y estacionamiento)"))
    u.assert_fact(ordenanza_transito, "instancia_de",
                  u.ind("ordenanza_municipal"))
    u.assert_fact(ordenanza_transito, "valido_desde",
                  at("2023-04-10T00:00:00+00:00"))

    articulo_42 = u.add_individual(Individual(
        id="art_42_ord_158", axis=Axis.O,
        label="Artículo 42 (estacionamiento prohibido)"))
    u.assert_fact(articulo_42, "instancia_de",
                  u.add_individual(category("articulo_ordenanza")))
    u.assert_fact(articulo_42, "parte_de", ordenanza_transito)
    u.assert_fact(articulo_42, "monto_multa", n(450, "USD", "n_450_usd"))

    # ====================================================================
    # CASO 2 — Licencia de funcionamiento: solicitud → revisión → emisión
    # ====================================================================
    # Café del Norte solicita una licencia para operar en el lote 4
    solicitud = ingest_situation(u, lex, "solicitar", roles={
        "agente": cafe_norte,
        "tipo_solicitado": u.add_individual(
            category("licencia_funcionamiento")),
        "beneficiario": municipalidad,
        "lugar_de": lote_4,
        "momento": at("2026-03-05T09:30:00+00:00"),
    }, sit_id="solic_licencia_001")
    u.assert_fact(solicitud, "estado", en_revision,
                  valid_from=datetime(2026, 3, 5, tzinfo=timezone.utc),
                  valid_to=datetime(2026, 3, 25, tzinfo=timezone.utc))
    u.assert_fact(solicitud, "estado", aprobada,
                  valid_from=datetime(2026, 3, 25, tzinfo=timezone.utc))

    # Revisión técnica con inspección al lote
    inspeccion = ingest_situation(u, lex, "inspeccionar", roles={
        "agente": inspector1,
        "inspeccionado": cafe_norte,
        "lugar_de": lote_4,
        "momento": at("2026-03-20T11:00:00+00:00"),
        "conclusion": u.add_individual(category("apto_para_operar")),
    }, sit_id="inspeccion_001")
    u.assert_fact(inspeccion, "motivado_por", solicitud)

    # Emisión de la licencia — justificada por la ordenanza
    licencia = ingest_situation(u, lex, "emitir", roles={
        "agente": municipalidad,
        "tipo_emitido": u.add_individual(
            category("licencia_funcionamiento")),
        "beneficiario": cafe_norte,
        "momento": at("2026-03-25T16:00:00+00:00"),
        "justificado_por": ordenanza_funcionamiento,
        "valido_desde": at("2026-04-01T00:00:00+00:00"),
        "valido_hasta": at("2027-03-31T23:59:59+00:00"),
    }, sit_id="licencia_001")
    u.assert_fact(licencia, "motivado_por", solicitud)
    u.assert_fact(licencia, "motivado_por", inspeccion)
    u.assert_fact(licencia, "vigente_en", lote_4)

    # ====================================================================
    # CASO 3 — Denuncia ciudadana que abre un expediente
    # ====================================================================
    # Sofía denuncia ruidos molestos del local del Café del Norte
    motivo_denuncia = u.add_individual(Individual(
        id="ruido_molesto_001", axis=Axis.O,
        label="Ruido molesto del local Café del Norte"))
    u.assert_fact(motivo_denuncia, "instancia_de",
                  u.add_individual(category("ruido_molesto_nocturno")))
    u.assert_fact(motivo_denuncia, "lugar_de", lote_4)
    u.assert_fact(motivo_denuncia, "momento_observado",
                  at("2026-06-15T23:40:00+00:00"))

    denuncia = ingest_situation(u, lex, "denunciar", roles={
        "agente": sofia,
        "tema": motivo_denuncia,
        "paciente": cafe_norte,
        "lugar_de": lote_4,
        "momento": at("2026-06-16T09:00:00+00:00"),
    }, sit_id="denuncia_001")

    # El expediente reificado agrupa la denuncia con sus diligencias
    expediente = u.add_individual(Individual(
        id="exp_2026_001", axis=Axis.O,
        label="Expediente 2026-001 (ruido nocturno)"))
    u.assert_fact(expediente, "instancia_de",
                  u.add_individual(category("expediente_administrativo")))
    u.assert_fact(expediente, "inicio",
                  at("2026-06-16T09:00:00+00:00"))
    u.assert_fact(expediente, "motivado_por", denuncia)

    # Inspección de verificación
    insp_nocturna = ingest_situation(u, lex, "inspeccionar", roles={
        "agente": inspector2,
        "inspeccionado": cafe_norte,
        "lugar_de": lote_4,
        "momento": at("2026-06-20T23:30:00+00:00"),
        "conclusion": u.add_individual(category("ruido_confirmado")),
    }, sit_id="inspeccion_nocturna_001")
    u.assert_fact(insp_nocturna, "parte_de", expediente)

    # ====================================================================
    # CASO 4 — Multa de tránsito con cadena causal completa
    # ====================================================================
    vehiculo_juan = u.add_individual(Individual(
        id="vehiculo_xyz_456", axis=Axis.O,
        label="Vehículo XYZ-456 (de Juan)"))
    u.assert_fact(vehiculo_juan, "instancia_de",
                  u.add_individual(category("vehiculo_particular")))
    u.assert_fact(vehiculo_juan, "agente", juan)

    # Infracción de tránsito como evento reificado
    infraccion = u.add_individual(Individual(
        id="infraccion_estac_001", axis=Axis.O,
        label="Estacionamiento prohibido"))
    u.assert_fact(infraccion, "instancia_de",
                  u.add_individual(
                      category("infraccion_estacionamiento_prohibido")))
    u.assert_fact(infraccion, "tema", vehiculo_juan)
    u.assert_fact(infraccion, "lugar_de", av_principal)
    u.assert_fact(infraccion, "momento",
                  at("2026-07-08T14:32:00+00:00"))

    multa = ingest_situation(u, lex, "multar", roles={
        "agente": policia_mun,
        "paciente": juan,
        "monto": n(450, "USD", "n_450_usd_multa"),
        "unidad": u.add_individual(category("Currency:USD")),
        "instrumento": u.add_individual(Individual(
            id="papeleta_001", axis=Axis.O,
            label="Papeleta 001")),
        "momento": at("2026-07-08T14:35:00+00:00"),
        "lugar_de": av_principal,
        "causado_por": infraccion,
        "justificado_por": articulo_42,
    }, sit_id="multa_001")

    # ====================================================================
    # CASO 5 — Recurso de reconsideración: Juan apela la multa
    # ====================================================================
    # Juan presenta un recurso argumentando que el área no estaba
    # debidamente señalizada
    recurso = u.add_individual(Individual(
        id="recurso_juan_001", axis=Axis.O,
        label="Recurso reconsideración Juan"))
    u.assert_fact(recurso, "instancia_de",
                  u.add_individual(category("recurso_reconsideracion")))
    u.assert_fact(recurso, "agente", juan)
    u.assert_fact(recurso, "tema", multa)
    u.assert_fact(recurso, "momento",
                  at("2026-07-15T10:00:00+00:00"))
    u.assert_fact(recurso, "motivado_por",
                  u.add_individual(Individual(
                      id="motivo_falta_senalizacion_001", axis=Axis.O,
                      label="Argumento: falta de señalización clara")))

    # Resolución del recurso por el alcalde — declarado procedente
    resolucion = ingest_situation(u, lex, "resolver", roles={
        "agente": alcalde,
        "tema": recurso,
        "conclusion": procedente,
        "momento": at("2026-08-05T16:00:00+00:00"),
        "justificado_por": u.add_individual(Individual(
            id="art_15_norma_proc_admin", axis=Axis.O,
            label="Artículo 15 (procedimiento administrativo)")),
    }, sit_id="resolucion_recurso_001")

    # La resolución rectifica la multa: la deja sin efecto
    u.assert_fact(resolucion, "rectifica", multa)
    u.assert_fact(multa, "estado", revocada,
                  valid_from=datetime(2026, 8, 5, 16, tzinfo=timezone.utc))

    handles = {
        # personas
        "alcalde": alcalde, "inspector1": inspector1, "inspector2": inspector2,
        "policia_mun": policia_mun, "juan": juan, "sofia": sofia,
        "cafe_norte": cafe_norte, "municipalidad": municipalidad,
        # territorio
        "distrito_centro": distrito_centro, "barrio_san_jose": barrio_san_jose,
        "manzana_12": manzana_12, "lote_4": lote_4, "ciudad_norte": ciudad_norte,
        "av_principal": av_principal,
        # ordenanzas
        "ordenanza_funcionamiento": ordenanza_funcionamiento,
        "ordenanza_transito": ordenanza_transito, "articulo_42": articulo_42,
        # situaciones
        "solicitud": solicitud, "inspeccion": inspeccion, "licencia": licencia,
        "denuncia": denuncia, "expediente": expediente,
        "insp_nocturna": insp_nocturna,
        "infraccion": infraccion, "multa": multa, "recurso": recurso,
        "resolucion": resolucion,
        # categorías
        "procedente": procedente, "vigente": vigente, "revocada": revocada,
    }
    return u, handles


# ---------------------------------------------------------------------------
# Validaciones
# ---------------------------------------------------------------------------

def run_validations(u: Universe, lex: Lexicon, h: dict):
    results = []

    # V1 — Jerarquía territorial: lote → manzana → barrio → distrito → ciudad
    def chain_to_root(start: Individual) -> list:
        chain = [start.id]
        cur = start
        for _ in range(10):
            ups = [f.value for f in u.facts_about(cur) if f.role == "parte_de"]
            if not ups:
                break
            cur = ups[0]
            chain.append(cur.id)
        return chain

    def chain_to_root_terr(start: Individual) -> list:
        """Recorre la jerarquía territorial usando `dentro_de` (L→L)."""
        chain = [start.id]
        cur = start
        for _ in range(10):
            ups = [f.value for f in u.facts_about(cur) if f.role == "dentro_de"]
            if not ups:
                break
            cur = ups[0]
            chain.append(cur.id)
        return chain

    chain = chain_to_root_terr(h["lote_4"])
    expected = ["lote_4_m12", "manzana_12_sj", "barrio_san_jose",
                "distrito_centro", "ciudad_norte"]
    results.append((
        "Subdivisión territorial: lote → manzana → barrio → distrito → ciudad",
        chain == expected,
        f"cadena: {' → '.join(chain)}",
    ))

    # V2 — La licencia está justificada por la ordenanza correspondiente
    facts_lic = u.facts_about(h["licencia"])
    justif = [f for f in facts_lic if f.role == "justificado_por"]
    results.append((
        "D7: licencia justificada_por la ordenanza 237-2024",
        len(justif) == 1
        and justif[0].value.id == "ord_237_2024_funcionamiento",
        f"justif: {[f.value.id for f in justif]}",
    ))

    # V3 — La licencia tiene dos motivos: la solicitud y la inspección previa
    motivos = [f for f in facts_lic if f.role == "motivado_por"]
    motivo_ids = {f.value.id for f in motivos}
    results.append((
        "D7: licencia motivada_por solicitud + inspección",
        motivo_ids == {"solic_licencia_001", "inspeccion_001"},
        f"motivos: {sorted(motivo_ids)}",
    ))

    # V4 — D6: la solicitud estaba en_revision el 15-Mar, aprobada el 1-Abr
    t_15_mar = datetime(2026, 3, 15, tzinfo=timezone.utc)
    t_1_abr = datetime(2026, 4, 1, tzinfo=timezone.utc)
    e_15_mar = [
        f for f in u.facts_about(h["solicitud"], at=t_15_mar)
        if f.role == "estado"
    ]
    e_1_abr = [
        f for f in u.facts_about(h["solicitud"], at=t_1_abr)
        if f.role == "estado"
    ]
    results.append((
        "D6: solicitud en_revision el 15-Mar, aprobada el 1-Abr",
        (len(e_15_mar) == 1 and e_15_mar[0].value.id == "en_revision"
         and len(e_1_abr) == 1 and e_1_abr[0].value.id == "aprobada"),
        f"15-Mar: {[f.value.id for f in e_15_mar]}, "
        f"1-Abr: {[f.value.id for f in e_1_abr]}",
    ))

    # V5 — La multa tiene cadena causal completa: causado_por + justificado_por
    facts_multa = u.facts_about(h["multa"])
    causa = [f for f in facts_multa if f.role == "causado_por"]
    just = [f for f in facts_multa if f.role == "justificado_por"]
    results.append((
        "Cadena causal de la multa: causado_por infracción + justificado_por art.42",
        (len(causa) == 1 and causa[0].value.id == "infraccion_estac_001"
         and len(just) == 1 and just[0].value.id == "art_42_ord_158"),
        f"causa={[f.value.id for f in causa]}, "
        f"justif={[f.value.id for f in just]}",
    ))

    # V6 — Expediente administrativo motivado_por la denuncia
    facts_exp = u.facts_about(h["expediente"])
    mot_exp = [f for f in facts_exp if f.role == "motivado_por"]
    results.append((
        "Expediente administrativo motivado_por la denuncia ciudadana",
        len(mot_exp) == 1 and mot_exp[0].value.id == "denuncia_001",
        f"motivos: {[f.value.id for f in mot_exp]}",
    ))

    # V7 — La inspección nocturna está parte_de el expediente
    parte = [f.value.id for f in u.facts_about(h["insp_nocturna"])
             if f.role == "parte_de"]
    results.append((
        "Inspección nocturna parte_de el expediente 2026-001",
        parte == ["exp_2026_001"],
        f"parte_de: {parte}",
    ))

    # V8 — Recurso resuelto procedente → multa queda revocada
    t_post_resol = datetime(2026, 8, 6, tzinfo=timezone.utc)
    estado_multa = [
        f for f in u.facts_about(h["multa"], at=t_post_resol)
        if f.role == "estado"
    ]
    results.append((
        "Recurso procedente → multa revocada (D6 + rectifica)",
        len(estado_multa) == 1 and estado_multa[0].value.id == "revocada",
        f"estado de la multa post-resolución: "
        f"{[f.value.id for f in estado_multa]}",
    ))

    # V9 — La resolución rectifica la multa
    rect = [f for f in u.facts_about(h["resolucion"]) if f.role == "rectifica"]
    results.append((
        "Resolución rectifica la multa original",
        len(rect) == 1 and rect[0].value.id == "multa_001",
        f"rectifica: {[f.value.id for f in rect]}",
    ))

    # V10 — WH: ¿qué autoridad emitió la licencia de Café del Norte?
    r = query(u, Pattern(
        fixed={"beneficiario": h["cafe_norte"]},
        ask={"agente": Var()},
        type_constraint=u.ind("accion_emitir_licencia"),
    ))
    results.append((
        "WH: ¿quién emitió la licencia a Café del Norte?",
        len(r) == 1 and r[0]["agente"].id == "mun_central",
        f"agente: {[x['agente'].id for x in r]}",
    ))

    # V11 — Política liberal: roles de dominio admitidos
    facts_lic = u.facts_about(h["licencia"])
    roles_lic = {f.role for f in facts_lic}
    dominio_roles = {"valido_desde", "valido_hasta", "vigente_en"}
    results.append((
        "Política liberal: valido_desde/valido_hasta/vigente_en admitidos sin declarar",
        dominio_roles.issubset(roles_lic),
        f"roles de dominio en la licencia: {sorted(roles_lic & dominio_roles)}",
    ))

    return results


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main() -> bool:
    lex = build_lexicon()
    u, h = build_universe(lex)

    print("=" * 72)
    print("DOMINIO MUNICIPALIDAD — gobierno local")
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
