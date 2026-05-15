"""Dominio taxi — servicio on-demand con agentes múltiples y cadena de
situaciones.

Stress-test del modelo en lo que el sauna no estresaba:
- D5 al extremo: agencia repartida entre humano-pasajero, humano-conductor,
  app (software), vehículo (artefacto).
- 6 situaciones encadenadas: solicitar → asignar → aceptar → recoger →
  trasladar → completar, con `precede` y `motivado_por`.
- Surge pricing: una tarifa elevada se reifica con `causado_por` apuntando
  a un estado de alta demanda.
- Cancelaciones: una nueva situación `cancela` un viaje anterior.
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
        ("solicitar",   "accion_solicitar",   ["agente"],
            ["origen", "destino", "momento"]),
        ("asignar",     "accion_asignar",     ["agente", "tema", "beneficiario"],
            ["instrumento", "momento"]),
        ("aceptar",     "accion_aceptar",     ["agente", "tema"],
            ["momento"]),
        ("recoger",     "accion_recoger",     ["agente", "paciente", "lugar_de"],
            ["instrumento", "momento"]),
        ("trasladar",   "accion_trasladar",   ["agente", "paciente"],
            ["origen", "destino", "instrumento", "momento"]),
        ("completar",   "accion_completar",   ["agente", "tema"],
            ["lugar_de", "momento"]),
        ("cancelar",    "accion_cancelar",    ["agente", "tema"],
            ["momento"]),
    ]:
        lex.register(LexiconEntry(verb=verb, situation_type=st,
                                  obligatory=obl, optional=opt))

    lex.register_domain_dialect("taxi_app", {
        "pasajero":  "agente",
        "conductor": "beneficiario",
        "carrera":   "viaje",
    })
    return lex


def build_universe(lex: Lexicon) -> Tuple[Universe, dict]:
    cat = Catalog()
    u = Universe(name="taxi_app", catalog=cat)

    # Q — humanos
    valeria = u.add_individual(Individual(id="pasajera_valeria", axis=Axis.Q,
                                          label="Valeria"))
    luis = u.add_individual(Individual(id="conductor_luis", axis=Axis.Q,
                                       label="Luis"))
    # Q — app y vehículo como agentes contextuales (D5)
    app = u.add_individual(Individual(id="app_rideeasy", axis=Axis.Q,
                                      label="App RideEasy"))
    # Vehículo en O (objeto físico). Su "agencia" en mediciones D5 se
    # modelaría con un Q-individual aparte si hiciera falta.
    vehiculo = u.add_individual(Individual(id="vehiculo_abc123", axis=Axis.O,
                                           label="Toyota ABC-123"))
    u.assert_fact(vehiculo, "instancia_de",
                  u.add_individual(category("vehiculo_taxi")))

    # L — ubicaciones
    plaza = u.add_individual(Individual(id="plaza_principal", axis=Axis.L,
                                        label="Plaza principal"))
    aeropuerto = u.add_individual(Individual(id="aeropuerto", axis=Axis.L,
                                             label="Aeropuerto"))

    # K — estados y modalidades
    real = u.add_individual(category("real"))
    cancelado = u.add_individual(category("cancelado"))
    completado = u.add_individual(category("completado"))
    alta_demanda = u.add_individual(category("alta_demanda"))

    # T — momentos puntuales
    t0 = datetime(2026, 5, 16, 14, 30, tzinfo=timezone.utc)
    def at(delta_min: int) -> Individual:
        m = t0 + timedelta(minutes=delta_min)
        return Individual(id=f"t_{m.isoformat()}", axis=Axis.T,
                          label=m.isoformat(), payload=m)

    # --- VIAJE ARTICULADOR ---
    # Reificamos un "viaje" como entidad superior; todas las situaciones
    # de la cadena le cuelgan vía parte_de.
    viaje = u.add_individual(Individual(id="viaje_001", axis=Axis.O,
                                        label="viaje_001"))
    u.assert_fact(viaje, "instancia_de", u.add_individual(category("viaje")))

    # --- CADENA DE 6 SITUACIONES ---
    sol = ingest_situation(u, lex, "solicitar", roles={
        "agente": valeria, "origen": plaza, "destino": aeropuerto,
        "momento": at(0),
    }, sit_id="sol_001")
    u.assert_fact(sol, "parte_de", viaje)

    asig = ingest_situation(u, lex, "asignar", roles={
        "agente": app,                  # ¡APP COMO AGENTE — D5!
        "tema": sol,                    # asigna la solicitud
        "beneficiario": luis,           # al conductor
        "instrumento": vehiculo,        # con el vehículo
        "momento": at(1),
    }, sit_id="asig_001")
    u.assert_fact(asig, "parte_de", viaje)
    u.assert_fact(asig, "motivado_por", sol)

    acep = ingest_situation(u, lex, "aceptar", roles={
        "agente": luis, "tema": asig, "momento": at(2),
    }, sit_id="acep_001")
    u.assert_fact(acep, "parte_de", viaje)

    rec = ingest_situation(u, lex, "recoger", roles={
        "agente": luis, "paciente": valeria, "lugar_de": plaza,
        "instrumento": vehiculo, "momento": at(8),
    }, sit_id="rec_001")
    u.assert_fact(rec, "parte_de", viaje)
    u.assert_fact(rec, "sigue_a", acep)

    tras = ingest_situation(u, lex, "trasladar", roles={
        "agente": luis, "paciente": valeria,
        "origen": plaza, "destino": aeropuerto,
        "instrumento": vehiculo, "momento": at(10),
    }, sit_id="tras_001")
    u.assert_fact(tras, "parte_de", viaje)
    u.assert_fact(tras, "sigue_a", rec)

    comp = ingest_situation(u, lex, "completar", roles={
        "agente": luis, "tema": tras, "lugar_de": aeropuerto,
        "momento": at(35),
    }, sit_id="comp_001")
    u.assert_fact(comp, "parte_de", viaje)
    u.assert_fact(comp, "sigue_a", tras)
    u.assert_fact(viaje, "estatus_factual", completado)

    # --- SURGE PRICING como situación reificada ---
    estado_demanda = u.add_individual(Individual(
        id="alta_demanda_2026_05_16_14_30", axis=Axis.O,
        label="alta demanda 16/5 14:30"))
    u.assert_fact(estado_demanda, "instancia_de", alta_demanda)
    u.assert_fact(estado_demanda, "lugar_de", plaza)
    u.assert_fact(estado_demanda, "momento", at(0))

    tarifa = u.add_individual(Individual(
        id="tarifa_viaje_001", axis=Axis.O, label="tarifa viaje 001"))
    u.assert_fact(tarifa, "instancia_de", u.add_individual(category("tarifa")))
    u.assert_fact(tarifa, "parte_de", viaje)
    u.assert_fact(tarifa, "monto",
                  Individual(id="n_25_usd", axis=Axis.N, label="25 USD",
                             payload={"value": 25, "unit": "USD"}))
    u.assert_fact(tarifa, "unidad", u.add_individual(category("USD")))
    u.assert_fact(tarifa, "causado_por", estado_demanda)

    # --- CANCELACIÓN: un viaje paralelo que se cancela ---
    sol2 = ingest_situation(u, lex, "solicitar", roles={
        "agente": valeria, "origen": aeropuerto, "destino": plaza,
        "momento": at(60),
    }, sit_id="sol_002")
    viaje2 = u.add_individual(Individual(id="viaje_002", axis=Axis.O,
                                         label="viaje_002"))
    u.assert_fact(viaje2, "instancia_de", u.ind("viaje"))
    u.assert_fact(sol2, "parte_de", viaje2)

    canc = ingest_situation(u, lex, "cancelar", roles={
        "agente": valeria, "tema": viaje2, "momento": at(62),
    }, sit_id="canc_001")
    u.assert_fact(canc, "cancela", viaje2)
    u.assert_fact(viaje2, "estatus_factual", cancelado)

    h = {
        "valeria": valeria, "luis": luis, "app": app, "vehiculo": vehiculo,
        "plaza": plaza, "aeropuerto": aeropuerto,
        "viaje": viaje, "viaje2": viaje2,
        "completado": completado, "cancelado": cancelado,
        "tarifa": tarifa, "estado_demanda": estado_demanda,
        "asig": asig, "sol": sol, "comp": comp,
    }
    return u, h


def run_validations(u: Universe, lex: Lexicon, h: dict):
    results = []

    # V1: el app es agente en la asignación (D5)
    facts_asig = u.facts_about(h["asig"])
    agent_facts = [f for f in facts_asig if f.role == "agente"]
    ok = (len(agent_facts) == 1
          and agent_facts[0].value.id == "app_rideeasy")
    results.append(("D5: la app como agente de `asignar`", ok,
                    f"agente: {agent_facts[0].value.id if agent_facts else None}"))

    # V2: 6 situaciones parte_de viaje_001
    parts_viaje = [f for f in u.facts_with_role("parte_de")
                   if f.value.id == "viaje_001"]
    results.append(("6 situaciones encadenadas parte_de viaje_001",
                    len(parts_viaje) >= 6,
                    f"obtenido {len(parts_viaje)}"))

    # V3: la tarifa está causada por la alta demanda
    cau = [f for f in u.facts_about(h["tarifa"]) if f.role == "causado_por"]
    results.append(("Surge: tarifa.causado_por = alta_demanda",
                    len(cau) == 1
                    and cau[0].value.id == h["estado_demanda"].id,
                    f"causado_por: {[f.value.id for f in cau]}"))

    # V4: viaje_002 fue cancelado
    estatus = [f for f in u.facts_about(h["viaje2"])
               if f.role == "estatus_factual"]
    results.append(("viaje_002.estatus_factual = cancelado",
                    len(estatus) == 1 and estatus[0].value.id == "cancelado",
                    f"obtenido: {estatus[0].value.id if estatus else None}"))

    # V5: consulta WH — ¿adónde fue el viaje de Valeria?
    r = query(u, Pattern(
        fixed={"agente": h["luis"], "paciente": h["valeria"]},
        ask={"destino": Var()},
        type_constraint=u.ind("accion_trasladar"),
    ))
    results.append(("WH: ¿adónde traslada Luis a Valeria?",
                    len(r) == 1 and r[0]["destino"].id == "aeropuerto",
                    f"destino: {[x['destino'].id for x in r]}"))

    return results


def main():
    lex = build_lexicon()
    u, h = build_universe(lex)

    print("=" * 72)
    print("DOMINIO TAXI — agentes múltiples + cadena de situaciones")
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
