"""Dominio historia clínica — el modelo aplicado a un dominio nuevo.

Stress-test de:
- Densidad semántica: diagnóstico, prescripción, contraindicación con
  estructura intrínseca.
- D9 (vigencia): un diagnóstico activo desde T0 hasta T1; una medicación
  con frecuencia y duración.
- Cadenas causales: síntoma → diagnóstico → prescripción → control_futuro.
- Modalidad epistémica: un diagnóstico "probable" vs "confirmado".
- Contraindicaciones: justificado_por reglas de farmacovigilancia.
- Metodología de elicitación: cómo se elige qué reificar y qué no.
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
        ("consultar",  "consulta_medica", ["agente", "paciente"],
            ["lugar_de", "momento", "motivo"]),
        ("diagnosticar", "accion_diagnosticar", ["agente", "paciente"],
            ["tema", "momento", "modalidad", "estatus_factual"]),
        ("prescribir", "accion_prescribir",
            ["agente", "paciente", "medicamento_prescrito"],
            ["frecuencia", "duracion", "momento"]),
        ("medir",      "accion_medir",   ["agente", "paciente"],
            ["tema", "monto", "unidad", "momento"]),
        ("controlar",  "control_clinico", ["paciente"],
            ["agente", "momento", "estatus_factual"]),
    ]:
        lex.register(LexiconEntry(verb=verb, situation_type=st,
                                  obligatory=obl, optional=opt))
    lex.register_domain_dialect("clinica", {
        "doctor": "agente",
        "paciente": "paciente",
        "diagnostico": "tema",
        "medicamento": "tema",
    })
    return lex


def build_universe(lex: Lexicon) -> Tuple[Universe, dict]:
    cat = Catalog()
    u = Universe(name="historia_clinica", catalog=cat)

    # Q
    dra_torres = u.add_individual(Individual(id="dra_torres", axis=Axis.Q,
                                             label="Dra. Torres"))
    paciente = u.add_individual(Individual(id="maria_g", axis=Axis.Q,
                                           label="María Gonzales"))

    # L
    consultorio = u.add_individual(Individual(id="consultorio_03", axis=Axis.L,
                                              label="Consultorio 03"))

    # K — categorías
    hta_g1 = u.add_individual(category("hipertension_grado_1"))
    enalapril = u.add_individual(category("enalapril_10mg"))
    cefalea = u.add_individual(category("cefalea_persistente"))
    confirmado = u.add_individual(category("confirmado"))
    probable = u.add_individual(category("probable"))
    real = u.add_individual(category("real"))
    epistemica = u.add_individual(category("epistemica"))
    cada_manana = u.add_individual(category("cada_manana"))
    mmHg = u.add_individual(category("Pressure:mmHg"))

    # T — momentos
    t_consulta = datetime(2026, 5, 14, 10, 30, tzinfo=timezone.utc)
    def at(delta_days: int = 0) -> Individual:
        m = t_consulta + timedelta(days=delta_days)
        return Individual(id=f"t_{m.isoformat()}", axis=Axis.T,
                          label=m.isoformat(), payload=m)

    # ------------------------------------------------------------------
    # La consulta: situación articuladora
    # ------------------------------------------------------------------
    consulta = ingest_situation(u, lex, "consultar", roles={
        "agente": dra_torres, "paciente": paciente,
        "lugar_de": consultorio, "momento": at(0),
        "motivo": cefalea,
    }, extra={"estatus_factual": real}, sit_id="cons_001")

    # ------------------------------------------------------------------
    # Síntoma reificado
    # ------------------------------------------------------------------
    sintoma = u.add_individual(Individual(id="sintoma_001", axis=Axis.O))
    u.assert_fact(sintoma, "instancia_de", cefalea)
    u.assert_fact(sintoma, "experimentador", paciente)
    u.assert_fact(sintoma, "parte_de", consulta)
    u.assert_fact(sintoma, "momento", at(-3))  # 3 días antes

    # ------------------------------------------------------------------
    # Medición: presión arterial 145/92 mmHg
    # ------------------------------------------------------------------
    medicion = ingest_situation(u, lex, "medir", roles={
        "agente": dra_torres, "paciente": paciente,
        "monto": Individual(id="n_145_mmhg", axis=Axis.N,
                            label="145/92 mmHg",
                            payload={"systolic": 145, "diastolic": 92,
                                     "unit": "mmHg"}),
        "unidad": mmHg,
        "momento": at(0),
    }, sit_id="med_pa_001")
    u.assert_fact(medicion, "parte_de", consulta)
    # `tema: O → O` rechaza K — usamos rol de dominio para "qué se midió"
    u.assert_fact(medicion, "medida_de",
                  u.add_individual(category("presion_arterial")))

    # ------------------------------------------------------------------
    # Diagnóstico (modalidad epistémica: "confirmado")
    # ------------------------------------------------------------------
    diag = ingest_situation(u, lex, "diagnosticar", roles={
        "agente": dra_torres, "paciente": paciente,
        "tema": medicion,  # basado en la medición
        "momento": at(0),
    }, extra={"modalidad": epistemica, "estatus_factual": confirmado},
        sit_id="diag_hta_001")
    u.assert_fact(diag, "parte_de", consulta)
    # La condición diagnosticada se asienta más abajo con vigencia (D9).

    # ------------------------------------------------------------------
    # Prescripción
    # ------------------------------------------------------------------
    # `tema` rechaza K (enalapril es categoría). Usamos rol de dominio
    # `medicamento_prescrito: O → K`, registrado como obligatorio del verbo.
    pres = ingest_situation(u, lex, "prescribir", roles={
        "agente": dra_torres, "paciente": paciente,
        "medicamento_prescrito": enalapril,
        "frecuencia": cada_manana,
        "duracion": u.add_individual(category("indefinida")),
        "momento": at(0),
    }, sit_id="pres_001",
        valid_from=t_consulta,
        valid_to=None)  # tratamiento abierto al futuro
    u.assert_fact(pres, "parte_de", consulta)
    u.assert_fact(pres, "motivado_por", diag)
    # con_finalidad apunta a una situación-objetivo (estado futuro reificado).
    objetivo = u.add_individual(Individual(
        id="objetivo_reducir_pa_maria", axis=Axis.O,
        label="reducir PA de María a <140"))
    u.assert_fact(objetivo, "instancia_de",
                  u.add_individual(category("objetivo_terapeutico")))
    u.assert_fact(objetivo, "paciente", paciente)
    u.assert_fact(objetivo, "estatus_factual",
                  u.add_individual(category("previsto")))
    u.assert_fact(pres, "con_finalidad", objetivo)

    # ------------------------------------------------------------------
    # Control futuro previsto (estatus_factual: previsto)
    # ------------------------------------------------------------------
    previsto = u.add_individual(category("previsto"))
    control = ingest_situation(u, lex, "controlar", roles={
        "paciente": paciente,
        "agente": dra_torres,
        "momento": at(30),
    }, extra={"estatus_factual": previsto}, sit_id="control_001")
    u.assert_fact(control, "parte_de", consulta)
    u.assert_fact(control, "motivado_por", diag)

    # ------------------------------------------------------------------
    # D9: el diagnóstico HTA cambió de grado (g1 → g2) seis meses después
    # ------------------------------------------------------------------
    # El primer diagnóstico era HTA g1; vigente hasta diciembre 2026.
    # En enero 2027 se rediagnostica como g2 (más severo).
    t_redx = datetime(2027, 1, 10, tzinfo=timezone.utc)
    hta_g2 = u.add_individual(category("hipertension_grado_2"))

    diag2 = ingest_situation(u, lex, "diagnosticar", roles={
        "agente": dra_torres, "paciente": paciente,
        "momento": Individual(id="t_redx", axis=Axis.T, payload=t_redx,
                              label=t_redx.isoformat()),
    }, extra={"modalidad": epistemica, "estatus_factual": confirmado},
        sit_id="diag_hta_002",
        valid_from=t_redx)
    u.assert_fact(diag2, "diagnosticado_como", hta_g2,
                  valid_from=t_redx)
    u.assert_fact(diag2, "rectifica", diag)

    # El diagnóstico original tiene vigencia limitada
    u.assert_fact(diag, "diagnosticado_como", hta_g1,
                  valid_from=t_consulta, valid_to=t_redx)

    # ------------------------------------------------------------------
    # Contraindicación reificada como regla
    # ------------------------------------------------------------------
    regla_contra = u.add_individual(Individual(
        id="contraindicacion_enalapril_embarazo", axis=Axis.O,
        label="No enalapril durante embarazo"))
    u.assert_fact(regla_contra, "instancia_de",
                  u.add_individual(category("contraindicacion")))
    u.assert_fact(regla_contra, "medicamento_prescrito", enalapril)
    u.assert_fact(regla_contra, "condicion",
                  u.add_individual(category("estado_embarazo")))
    u.assert_fact(regla_contra, "consecuente",
                  u.add_individual(category("evitar_medicamento")))
    # La prescripción debería poder ser justificada/cuestionada vs esta regla
    u.assert_fact(pres, "verificado_contra", regla_contra)

    h = {
        "doctora": dra_torres, "paciente": paciente,
        "consulta": consulta, "diag": diag, "diag2": diag2,
        "pres": pres, "control": control,
        "hta_g1": hta_g1, "hta_g2": hta_g2,
        "enalapril": enalapril, "regla_contra": regla_contra,
        "t_consulta": t_consulta, "t_redx": t_redx,
        "previsto": previsto, "real": real,
    }
    return u, h


def run_validations(u: Universe, lex: Lexicon, h: dict):
    results = []

    # V1: 5 sub-situaciones parte_de la consulta
    partes = [f for f in u.facts_with_role("parte_de")
              if f.value.id == h["consulta"].id]
    results.append(("Sub-situaciones parte_de la consulta",
                    len(partes) == 5,
                    f"obtenidas {len(partes)} (síntoma, medición, diag, "
                    f"pres, control)"))

    # V2: la prescripción está motivada_por el diagnóstico
    facts_pres = u.facts_about(h["pres"])
    motivos = [f for f in facts_pres if f.role == "motivado_por"]
    results.append(("Prescripción motivada_por diagnóstico",
                    len(motivos) == 1
                    and motivos[0].value.id == h["diag"].id,
                    f"motivado_por: {[f.value.id for f in motivos]}"))

    # V3: el control futuro tiene estatus_factual: previsto
    estatus = [f for f in u.facts_about(h["control"])
               if f.role == "estatus_factual"]
    results.append(("Control futuro con estatus_factual: previsto",
                    len(estatus) == 1 and estatus[0].value.id == "previsto",
                    f"estatus: {[f.value.id for f in estatus]}"))

    # V4: D9 — diagnóstico actual en distintos momentos
    t_mid_2026 = datetime(2026, 8, 1, tzinfo=timezone.utc)
    t_mid_2027 = datetime(2027, 3, 1, tzinfo=timezone.utc)
    diag_at_2026 = u.facts_about(h["diag"], at=t_mid_2026)
    diag_at_2026_dx = [f for f in diag_at_2026
                      if f.role == "diagnosticado_como"]
    diag2_at_2027 = u.facts_about(h["diag2"], at=t_mid_2027)
    diag2_at_2027_dx = [f for f in diag2_at_2027
                       if f.role == "diagnosticado_como"]
    ok_2026 = (len(diag_at_2026_dx) == 1
               and diag_at_2026_dx[0].value.id == "hipertension_grado_1")
    ok_2027 = (len(diag2_at_2027_dx) == 1
               and diag2_at_2027_dx[0].value.id == "hipertension_grado_2")
    results.append(("D9: diagnóstico HTA-g1 vigente en agosto 2026",
                    ok_2026,
                    f"vigente: {[f.value.id for f in diag_at_2026_dx]}"))
    results.append(("D9: diagnóstico HTA-g2 vigente en marzo 2027",
                    ok_2027,
                    f"vigente: {[f.value.id for f in diag2_at_2027_dx]}"))

    # V5: la prescripción está verificada contra una contraindicación
    facts_pres = u.facts_about(h["pres"])
    verif = [f for f in facts_pres if f.role == "verificado_contra"]
    results.append(("Prescripción verificada contra contraindicación",
                    len(verif) == 1,
                    f"verificado_contra: {[f.value.id for f in verif]}"))

    # V6: el rediagnóstico rectifica el original
    facts_diag2 = u.facts_about(h["diag2"])
    rect = [f for f in facts_diag2 if f.role == "rectifica"]
    results.append(("Rediagnóstico rectifica el original",
                    len(rect) == 1 and rect[0].value.id == h["diag"].id,
                    f"rectifica: {[f.value.id for f in rect]}"))

    # V7: cadena causal: prescripción con_finalidad reducir_presion
    finalidad = [f for f in u.facts_about(h["pres"])
                if f.role == "con_finalidad"]
    results.append(("Cadena causal: prescripción con_finalidad explicita",
                    len(finalidad) == 1,
                    f"con_finalidad: {[f.value.id for f in finalidad]}"))

    return results


def main():
    lex = build_lexicon()
    u, h = build_universe(lex)

    print("=" * 72)
    print("DOMINIO HISTORIA CLÍNICA — densidad semántica + D9")
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
