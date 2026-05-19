"""Dominio Minera — operación minera de gran escala.

Stress-test del modelo en un dominio físico-industrial:

- Estructura espacial jerárquica (yacimiento → tajo → nivel → banco → frente)
  usando `dentro_de` como rol de dominio (L→L).
- Producción con MÚLTIPLES unidades de medida convertibles
  (toneladas, gramos/tonelada, onzas de oro fino).
- Mantenimiento de equipo de larga vida con varios estados temporales (D6).
- Incidente de seguridad SIN agente humano (D5): roca que se desprende
  y lesiona a un trabajador. Cadena causal sin intencionalidad.
- Turno (shift) como entidad articuladora con múltiples trabajadores,
  equipos y producción registrada en él.
- Reporte regulatorio ambiental disparado por umbral excedido.
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
# Lexicon del dominio minero
# ---------------------------------------------------------------------------

def build_lexicon() -> Lexicon:
    lex = Lexicon()
    for verb, st, obl, opt in [
        ("extraer", "accion_extraer_mineral",
            ["agente", "extraido", "monto", "unidad"],
            ["lugar_de", "momento", "ley_mineral", "ley_unidad"]),
        ("operar_equipo", "accion_operar_equipo",
            ["agente", "instrumento"],
            ["lugar_de", "momento", "duracion", "duracion_unidad"]),
        ("dar_mantenimiento", "accion_mantenimiento",
            ["agente", "instrumento"],
            ["tipo_mantenimiento", "momento", "costo", "unidad"]),
        ("medir_calidad", "accion_medir_calidad_ambiental",
            ["agente", "medido_de", "monto", "unidad"],
            ["lugar_de", "momento", "instrumento"]),
        ("reportar", "accion_reportar_regulatorio",
            ["agente", "tema", "beneficiario"],
            ["momento", "motivado_por", "justificado_por"]),
        ("ejecutar_test", "accion_ejecutar_test",
            ["agente", "tema"],
            ["momento", "lugar_de", "valor_medido",
             "valor_medido_unidad", "instrumento"]),
        ("aprobar_checkpoint", "accion_aprobar_checkpoint",
            ["agente", "tema"],
            ["momento", "conclusion", "justificado_por"]),
        ("registrar_punchitem", "accion_registrar_punchitem",
            ["agente", "tema"],
            ["equipo_afectado", "lugar_de", "momento",
             "severidad", "responsable", "verificador",
             "fecha_limite"]),
        ("cerrar_punchitem", "accion_cerrar_punchitem",
            ["agente", "tema"],
            ["momento", "verificado_por", "motivado_por"]),
    ]:
        lex.register(LexiconEntry(verb=verb, situation_type=st,
                                  obligatory=obl, optional=opt))

    lex.register_domain_dialect("minera", {
        "operador": "agente",
        "trabajador": "agente",
        "camion": "instrumento",
        "pala": "instrumento",
    })
    return lex


# ---------------------------------------------------------------------------
# Universo
# ---------------------------------------------------------------------------

def build_universe(lex: Lexicon) -> Tuple[Universe, dict]:
    cat = Catalog()
    u = Universe(name="minera", catalog=cat)

    # === K — Categorías ===
    operativo = u.add_individual(category("operativo"))
    mantenimiento_prog = u.add_individual(category("en_mantenimiento_programado"))
    mantenimiento_corr = u.add_individual(category("en_mantenimiento_correctivo"))
    baja = u.add_individual(category("dado_de_baja"))
    real = u.add_individual(category("real"))
    confirmada = u.add_individual(category("confirmada"))

    # === Q — Personas y empresa ===
    minera_andes = u.add_individual(Individual(
        id="empresa_minera_andes", axis=Axis.Q,
        label="Minera Andes S.A."))
    supervisor = u.add_individual(Individual(
        id="sup_huaman", axis=Axis.Q,
        label="Supervisor Huamán"))
    operador1 = u.add_individual(Individual(
        id="op_quispe", axis=Axis.Q, label="Operador Quispe"))
    operador2 = u.add_individual(Individual(
        id="op_torres", axis=Axis.Q, label="Operador Torres"))
    operador3 = u.add_individual(Individual(
        id="op_mamani", axis=Axis.Q, label="Operador Mamani"))
    mecanico = u.add_individual(Individual(
        id="mec_rodriguez", axis=Axis.Q, label="Mecánico Rodríguez"))
    inspector_amb = u.add_individual(Individual(
        id="insp_ambiental_001", axis=Axis.Q,
        label="Inspector Ambiental"))
    sensor_pm = u.add_individual(Individual(
        id="sensor_pm10_estacion_3", axis=Axis.Q,
        label="Sensor PM10 Estación 3"))
    ente_regulador = u.add_individual(Individual(
        id="oefa_peru", axis=Axis.Q,
        label="OEFA — Organismo regulador ambiental"))

    # === L — Estructura espacial jerárquica ===
    yacimiento = u.add_individual(Individual(
        id="yac_san_marcos", axis=Axis.L,
        label="Yacimiento San Marcos"))
    tajo_norte = u.add_individual(Individual(
        id="tajo_norte", axis=Axis.L, label="Tajo Norte"))
    nivel_4250 = u.add_individual(Individual(
        id="nivel_4250", axis=Axis.L, label="Nivel 4250 m.s.n.m."))
    banco_3 = u.add_individual(Individual(
        id="banco_03_tn", axis=Axis.L, label="Banco 03 (Tajo Norte)"))
    frente_a = u.add_individual(Individual(
        id="frente_a_b03", axis=Axis.L, label="Frente A (Banco 03)"))
    rio_quebrada = u.add_individual(Individual(
        id="rio_quebrada_chica", axis=Axis.L,
        label="Río Quebrada Chica"))
    estacion_monitoreo = u.add_individual(Individual(
        id="estacion_monit_03", axis=Axis.L,
        label="Estación de monitoreo nº 3"))

    # Jerarquía espacial — `dentro_de` (L→L) por política liberal
    u.assert_fact(tajo_norte, "dentro_de", yacimiento)
    u.assert_fact(nivel_4250, "dentro_de", tajo_norte)
    u.assert_fact(banco_3, "dentro_de", nivel_4250)
    u.assert_fact(frente_a, "dentro_de", banco_3)
    u.assert_fact(estacion_monitoreo, "dentro_de", yacimiento)

    # ====================================================================
    # CASO 1 — Equipo de larga vida con varios estados temporales (D6)
    # ====================================================================
    camion_007 = u.add_individual(Individual(
        id="camion_cat_793f_007", axis=Axis.O,
        label="Camión CAT 793F nº 007"))
    u.assert_fact(camion_007, "instancia_de",
                  u.add_individual(category("camion_minero_grande")))
    u.assert_fact(camion_007, "fecha_adquisicion",
                  at("2018-04-10T00:00:00+00:00"))
    u.assert_fact(camion_007, "vida_util_anios",
                  n(15, "años", "n_15_anios"))

    # Estados del camión a lo largo de su vida útil (D6)
    t_op_inicial = datetime(2018, 4, 15, tzinfo=timezone.utc)
    t_mant_2024 = datetime(2024, 3, 10, tzinfo=timezone.utc)
    t_post_mant = datetime(2024, 3, 25, tzinfo=timezone.utc)
    t_falla = datetime(2026, 5, 14, 8, 30, tzinfo=timezone.utc)
    t_post_falla = datetime(2026, 5, 18, tzinfo=timezone.utc)

    u.assert_fact(camion_007, "estado", operativo,
                  valid_from=t_op_inicial, valid_to=t_mant_2024)
    u.assert_fact(camion_007, "estado", mantenimiento_prog,
                  valid_from=t_mant_2024, valid_to=t_post_mant)
    u.assert_fact(camion_007, "estado", operativo,
                  valid_from=t_post_mant, valid_to=t_falla)
    u.assert_fact(camion_007, "estado", mantenimiento_corr,
                  valid_from=t_falla, valid_to=t_post_falla)
    u.assert_fact(camion_007, "estado", operativo,
                  valid_from=t_post_falla)

    # ====================================================================
    # CASO 2 — Turno como entidad articuladora (varios trabajadores,
    #          equipos, producción, todos parte_de el turno)
    # ====================================================================
    turno = u.add_individual(Individual(
        id="turno_dia_2026_05_19", axis=Axis.O,
        label="Turno día 19-May-2026"))
    u.assert_fact(turno, "instancia_de",
                  u.add_individual(category("turno_minero")))
    u.assert_fact(turno, "inicio",
                  at("2026-05-19T06:00:00+00:00"))
    u.assert_fact(turno, "fin",
                  at("2026-05-19T18:00:00+00:00"))
    u.assert_fact(turno, "lugar_de", tajo_norte)
    u.assert_fact(turno, "supervisor", supervisor)

    # Trabajadores asignados al turno (roles de dominio)
    u.assert_fact(turno, "operador_asignado", operador1)
    u.assert_fact(turno, "operador_asignado", operador2)
    u.assert_fact(turno, "operador_asignado", operador3)

    # ====================================================================
    # CASO 3 — Extracción con múltiples unidades (toneladas, ley g/t, onzas)
    # ====================================================================
    onza_troy = u.add_individual(category("Unit:OnzaTroy"))
    tonelada_metr = u.add_individual(category("Unit:ToneladaMetrica"))
    gramo_por_ton = u.add_individual(category("Unit:GramoPorTonelada"))
    mineral_oro = u.add_individual(category("MineralOro"))

    extraccion = ingest_situation(u, lex, "extraer", roles={
        "agente": operador1,
        "extraido": mineral_oro,
        "monto": n(2400, "toneladas", "n_2400_t"),
        "unidad": tonelada_metr,
        "lugar_de": frente_a,
        "momento": at("2026-05-19T09:15:00+00:00"),
        "ley_mineral": n(8.2, "g/t", "n_8_2_gt"),
        "ley_unidad": gramo_por_ton,
    }, sit_id="extr_001")
    u.assert_fact(extraccion, "parte_de", turno)
    u.assert_fact(extraccion, "instrumento", camion_007)

    # Cálculo derivado: 2400 t × 8.2 g/t = 19,680 g = 632.7 onzas troy
    produccion_oro = u.add_individual(Individual(
        id="prod_oro_extr_001", axis=Axis.O,
        label="Oro fino producido por extr_001"))
    u.assert_fact(produccion_oro, "instancia_de",
                  u.add_individual(category("produccion_oro_fino")))
    u.assert_fact(produccion_oro, "parte_de", extraccion)
    u.assert_fact(produccion_oro, "monto",
                  n(632.7, "onzas_troy", "n_632_7_oz"))
    u.assert_fact(produccion_oro, "unidad", onza_troy)
    u.assert_fact(produccion_oro, "calculado_de", extraccion)

    # ====================================================================
    # CASO 4 — Incidente sin agente humano (D5 al extremo)
    # ====================================================================
    # Un desprendimiento de roca lesiona al operador Quispe
    desprendimiento = u.add_individual(Individual(
        id="evento_desprendimiento_001", axis=Axis.O,
        label="Desprendimiento de roca"))
    u.assert_fact(desprendimiento, "instancia_de",
                  u.add_individual(category("evento_fisico_geomecanico")))
    u.assert_fact(desprendimiento, "lugar_de", frente_a)
    u.assert_fact(desprendimiento, "momento",
                  at("2026-05-19T11:40:00+00:00"))
    # NO TIENE agente — fue un evento físico, no lo "hizo" nadie
    # Su causa probable: un debilitamiento estructural previo
    debilitamiento = u.add_individual(Individual(
        id="debilitamiento_pared_b03", axis=Axis.O,
        label="Debilitamiento estructural Banco 03"))
    u.assert_fact(debilitamiento, "instancia_de",
                  u.add_individual(category("condicion_geomecanica")))
    u.assert_fact(desprendimiento, "causado_por", debilitamiento)

    # El accidente que recibe la onda del desprendimiento
    accidente = u.add_individual(Individual(
        id="accidente_quispe_001", axis=Axis.O,
        label="Accidente Quispe (golpe por roca)"))
    u.assert_fact(accidente, "instancia_de",
                  u.add_individual(category("accidente_laboral")))
    u.assert_fact(accidente, "paciente", operador1)
    u.assert_fact(accidente, "lugar_de", frente_a)
    u.assert_fact(accidente, "momento",
                  at("2026-05-19T11:40:30+00:00"))
    u.assert_fact(accidente, "causado_por", desprendimiento)
    u.assert_fact(accidente, "parte_de", turno)
    u.assert_fact(accidente, "tipo_lesion",
                  u.add_individual(category("contusion_brazo_derecho")))

    # ====================================================================
    # CASO 5 — Mantenimiento correctivo motivado por incidente operativo
    # ====================================================================
    # Tras la inspección post-accidente, se hace mantenimiento al camión
    mantenimiento_post = ingest_situation(u, lex, "dar_mantenimiento", roles={
        "agente": mecanico,
        "instrumento": camion_007,
        "tipo_mantenimiento":
            u.add_individual(category("mantenimiento_correctivo_motor")),
        "momento": at("2026-05-14T10:00:00+00:00"),
        "costo": n(18500, "USD", "n_18500_usd"),
        "unidad": u.add_individual(category("Currency:USD")),
    }, sit_id="mant_correctivo_001")

    # ====================================================================
    # CASO 6 — Reporte regulatorio ambiental disparado por umbral
    # ====================================================================
    miligramo_l = u.add_individual(category("Unit:MiligramoPorLitro"))
    arsenico = u.add_individual(category("Quimico:Arsenico"))

    medicion_alta = ingest_situation(u, lex, "medir_calidad", roles={
        "agente": sensor_pm,
        "medido_de": arsenico,
        "monto": n(0.32, "mg/L", "n_0_32_mg_l"),
        "unidad": miligramo_l,
        "lugar_de": estacion_monitoreo,
        "momento": at("2026-05-15T14:00:00+00:00"),
    }, sit_id="medicion_001")

    # Umbral regulatorio: 0.10 mg/L (norma máxima permisible)
    norma_ambiental = u.add_individual(Individual(
        id="ds_004_2017_minam", axis=Axis.O,
        label="DS 004-2017-MINAM (ECA agua)"))
    u.assert_fact(norma_ambiental, "instancia_de",
                  u.add_individual(category("norma_ambiental")))
    u.assert_fact(norma_ambiental, "umbral_arsenico",
                  n(0.10, "mg/L", "n_0_10_mg_l"))

    # El reporte regulatorio se dispara por exceder el umbral
    reporte = ingest_situation(u, lex, "reportar", roles={
        "agente": minera_andes,
        "tema": medicion_alta,
        "beneficiario": ente_regulador,
        "momento": at("2026-05-15T18:00:00+00:00"),
        "motivado_por": medicion_alta,
        "justificado_por": norma_ambiental,
    }, sit_id="reporte_ambiental_001")

    # ====================================================================
    # CASO 7 — Comisionamiento: nuevo molino de bolas con tests encadenados
    # ====================================================================
    # Un nuevo molino se instala y entra en fase de pre-comisionamiento.
    # Antes de la operación comercial debe pasar tres tests, cada uno con
    # criterio de aceptación específico (tolerancia numérica) y firma del
    # contratista, el ingeniero del owner y el inspector QA.
    contratista = u.add_individual(Individual(
        id="empresa_metso_outotec", axis=Axis.Q,
        label="Contratista Metso Outotec"))
    ing_owner = u.add_individual(Individual(
        id="ing_owner_paredes", axis=Axis.Q,
        label="Ing. del owner (Paredes)"))
    qa_inspector = u.add_individual(Individual(
        id="qa_castro", axis=Axis.Q,
        label="QA Inspector Castro"))

    molino_005 = u.add_individual(Individual(
        id="molino_bolas_005", axis=Axis.O,
        label="Molino de bolas nº 005"))
    u.assert_fact(molino_005, "instancia_de",
                  u.add_individual(category("molino_bolas_industrial")))
    u.assert_fact(molino_005, "capacidad_nominal",
                  n(120, "tph", "n_120_tph"))   # toneladas por hora

    # El paquete de comisionamiento como entidad articuladora superior
    comisionamiento = u.add_individual(Individual(
        id="comisionamiento_molino_005", axis=Axis.O,
        label="Comisionamiento del molino 005"))
    u.assert_fact(comisionamiento, "instancia_de",
                  u.add_individual(category("paquete_comisionamiento")))
    u.assert_fact(comisionamiento, "tema", molino_005)
    u.assert_fact(comisionamiento, "agente", contratista)
    u.assert_fact(comisionamiento, "inicio",
                  at("2026-04-01T08:00:00+00:00"))
    u.assert_fact(comisionamiento, "estado",
                  u.add_individual(category("en_proceso")),
                  valid_from=datetime(2026, 4, 1, tzinfo=timezone.utc))

    # --- Test 1 — Acceptance criterion con tolerancia: prueba hidrostática
    # Criterio: presión >= 8 bar sostenida 30 min, caída máxima 2%.
    # El criterio se reifica como objeto con sus límites.
    bar_unit = u.add_individual(category("Unit:Bar"))
    pct_unit = u.add_individual(category("Unit:Percent"))

    criterio_hidro = u.add_individual(Individual(
        id="criterio_hidrostatica_v1", axis=Axis.O,
        label="Criterio prueba hidrostática"))
    u.assert_fact(criterio_hidro, "instancia_de",
                  u.add_individual(category("acceptance_criterion")))
    u.assert_fact(criterio_hidro, "presion_minima",
                  n(8.0, "bar", "n_8_bar"))
    u.assert_fact(criterio_hidro, "duracion_minima",
                  n(30, "min", "n_30_min"))
    u.assert_fact(criterio_hidro, "caida_maxima_pct",
                  n(2.0, "%", "n_2_pct"))

    # El test ejecutado, con su valor medido real
    test_hidro = ingest_situation(u, lex, "ejecutar_test", roles={
        "agente": contratista,
        "tema": molino_005,
        "valor_medido": n(8.4, "bar", "n_8_4_bar"),
        "valor_medido_unidad": bar_unit,
        "momento": at("2026-04-05T10:00:00+00:00"),
    }, sit_id="test_hidro_001")
    u.assert_fact(test_hidro, "parte_de", comisionamiento)
    u.assert_fact(test_hidro, "verifica_criterio", criterio_hidro)
    u.assert_fact(test_hidro, "caida_medida",
                  n(1.3, "%", "n_1_3_pct"))
    u.assert_fact(test_hidro, "duracion_medida",
                  n(32, "min", "n_32_min"))
    # El resultado pasa/falla se asienta como hecho — derivado por la
    # regla de comparación (que el motor de reglas externo evalúa).
    u.assert_fact(test_hidro, "resultado",
                  u.add_individual(category("test_aprobado")))

    # --- Sign-off paralelo: tres firmas independientes sobre el mismo test
    aprob_contratista = ingest_situation(u, lex, "aprobar_checkpoint", roles={
        "agente": contratista,
        "tema": test_hidro,
        "momento": at("2026-04-05T11:00:00+00:00"),
        "conclusion": u.add_individual(category("firmado_aprobado")),
    }, sit_id="signoff_contratista_hidro")

    aprob_owner = ingest_situation(u, lex, "aprobar_checkpoint", roles={
        "agente": ing_owner,
        "tema": test_hidro,
        "momento": at("2026-04-05T15:30:00+00:00"),
        "conclusion": u.add_individual(category("firmado_aprobado")),
    }, sit_id="signoff_owner_hidro")

    aprob_qa = ingest_situation(u, lex, "aprobar_checkpoint", roles={
        "agente": qa_inspector,
        "tema": test_hidro,
        "momento": at("2026-04-06T09:00:00+00:00"),
        "conclusion": u.add_individual(category("firmado_aprobado")),
    }, sit_id="signoff_qa_hidro")

    # --- Test 2 — Performance test (este pasa con holgura)
    test_perf = ingest_situation(u, lex, "ejecutar_test", roles={
        "agente": contratista,
        "tema": molino_005,
        "valor_medido": n(118, "tph", "n_118_tph"),
        "valor_medido_unidad": u.add_individual(
            category("Unit:ToneladaPorHora")),
        "momento": at("2026-04-12T14:00:00+00:00"),
    }, sit_id="test_perf_001")
    u.assert_fact(test_perf, "parte_de", comisionamiento)
    u.assert_fact(test_perf, "resultado",
                  u.add_individual(category("test_aprobado")))

    # ====================================================================
    # CASO 8 — Severidad ordenada en K (A/B/C)
    # ====================================================================
    # Modelamos las categorías de severidad como individuos en K
    # con un atributo numérico `nivel_severidad` que el sistema usa
    # para ordenarlas. El convenio de mining/oil&gas: A > B > C.
    sev_a = u.add_individual(category("severidad_A"))
    u.assert_fact(sev_a, "nivel_severidad",
                  n(1, "ord", "n_1_ord"))
    u.assert_fact(sev_a, "descripcion",
                  u.add_individual(
                      category("crítico_bloquea_comisionamiento")))

    sev_b = u.add_individual(category("severidad_B"))
    u.assert_fact(sev_b, "nivel_severidad",
                  n(2, "ord", "n_2_ord"))
    u.assert_fact(sev_b, "descripcion",
                  u.add_individual(
                      category("debe_resolverse_antes_operacion")))

    sev_c = u.add_individual(category("severidad_C"))
    u.assert_fact(sev_c, "nivel_severidad",
                  n(3, "ord", "n_3_ord"))
    u.assert_fact(sev_c, "descripcion",
                  u.add_individual(
                      category("estetico_no_bloqueante")))

    # ====================================================================
    # CASO 9 — Punchlist: tres items con responsables y verificadores
    # ====================================================================
    abierto = u.add_individual(category("abierto"))
    cerrado = u.add_individual(category("cerrado"))
    en_progreso = u.add_individual(category("en_progreso"))

    # Item 1 — fuga de aceite (severidad A — bloquea)
    fuga = u.add_individual(Individual(
        id="condicion_fuga_aceite_001", axis=Axis.O,
        label="Fuga de aceite del reductor"))
    u.assert_fact(fuga, "instancia_de",
                  u.add_individual(category("defecto_fisico")))
    u.assert_fact(fuga, "lugar_de", tajo_norte)

    punch_001 = ingest_situation(u, lex, "registrar_punchitem", roles={
        "agente": qa_inspector,           # quien lo encontró
        "tema": fuga,                     # qué se encontró
        "equipo_afectado": molino_005,    # qué equipo lo tiene
        "lugar_de": tajo_norte,
        "momento": at("2026-04-15T11:20:00+00:00"),
        "severidad": sev_a,
        "responsable": contratista,
        "verificador": ing_owner,
        "fecha_limite": at("2026-04-22T00:00:00+00:00"),
    }, sit_id="punch_001")
    u.assert_fact(punch_001, "parte_de", comisionamiento)
    u.assert_fact(punch_001, "estado", abierto,
                  valid_from=datetime(2026, 4, 15, tzinfo=timezone.utc),
                  valid_to=datetime(2026, 4, 16, tzinfo=timezone.utc))
    u.assert_fact(punch_001, "estado", en_progreso,
                  valid_from=datetime(2026, 4, 16, tzinfo=timezone.utc),
                  valid_to=datetime(2026, 4, 20, tzinfo=timezone.utc))
    u.assert_fact(punch_001, "estado", cerrado,
                  valid_from=datetime(2026, 4, 20, tzinfo=timezone.utc))

    cierre_punch_001 = ingest_situation(u, lex, "cerrar_punchitem", roles={
        "agente": contratista,
        "tema": punch_001,
        "momento": at("2026-04-20T10:30:00+00:00"),
        "verificado_por": ing_owner,
        "motivado_por": u.add_individual(Individual(
            id="reparacion_fuga_001", axis=Axis.O,
            label="Reparación de fuga ejecutada")),
    }, sit_id="cierre_punch_001")
    u.assert_fact(cierre_punch_001, "rectifica", punch_001)

    # Item 2 — falta etiqueta de equipo (severidad C — no bloquea)
    falta_etiqueta = u.add_individual(Individual(
        id="condicion_falta_etiqueta_001", axis=Axis.O,
        label="Falta placa de identificación"))
    u.assert_fact(falta_etiqueta, "instancia_de",
                  u.add_individual(category("defecto_documental")))

    punch_002 = ingest_situation(u, lex, "registrar_punchitem", roles={
        "agente": qa_inspector,
        "tema": falta_etiqueta,
        "equipo_afectado": molino_005,
        "momento": at("2026-04-15T11:25:00+00:00"),
        "severidad": sev_c,
        "responsable": contratista,
        "verificador": qa_inspector,
        "fecha_limite": at("2026-05-15T00:00:00+00:00"),
    }, sit_id="punch_002")
    u.assert_fact(punch_002, "parte_de", comisionamiento)
    u.assert_fact(punch_002, "estado", abierto,
                  valid_from=datetime(2026, 4, 15, tzinfo=timezone.utc))

    # Item 3 — vibración levemente fuera de spec (severidad B)
    vibracion = u.add_individual(Individual(
        id="condicion_vibracion_alta_001", axis=Axis.O,
        label="Vibración por encima del nominal"))
    u.assert_fact(vibracion, "instancia_de",
                  u.add_individual(category("defecto_dinamico")))
    u.assert_fact(vibracion, "valor_medido",
                  n(4.2, "mm/s", "n_4_2_mms"))
    u.assert_fact(vibracion, "valor_nominal_max",
                  n(3.5, "mm/s", "n_3_5_mms"))

    punch_003 = ingest_situation(u, lex, "registrar_punchitem", roles={
        "agente": ing_owner,
        "tema": vibracion,
        "equipo_afectado": molino_005,
        "momento": at("2026-04-16T15:00:00+00:00"),
        "severidad": sev_b,
        "responsable": contratista,
        "verificador": ing_owner,
        "fecha_limite": at("2026-05-01T00:00:00+00:00"),
    }, sit_id="punch_003")
    u.assert_fact(punch_003, "parte_de", comisionamiento)
    u.assert_fact(punch_003, "estado", abierto,
                  valid_from=datetime(2026, 4, 16, tzinfo=timezone.utc))

    handles = {
        # personas
        "supervisor": supervisor, "operador1": operador1,
        "operador2": operador2, "operador3": operador3,
        "mecanico": mecanico, "inspector_amb": inspector_amb,
        "sensor_pm": sensor_pm, "ente_regulador": ente_regulador,
        "minera": minera_andes,
        "contratista": contratista, "ing_owner": ing_owner,
        "qa_inspector": qa_inspector,
        # lugares
        "yacimiento": yacimiento, "tajo_norte": tajo_norte,
        "nivel_4250": nivel_4250, "banco_3": banco_3,
        "frente_a": frente_a, "estacion_monitoreo": estacion_monitoreo,
        # entidades operativas
        "camion_007": camion_007, "turno": turno,
        "extraccion": extraccion, "produccion_oro": produccion_oro,
        "desprendimiento": desprendimiento, "accidente": accidente,
        "debilitamiento": debilitamiento,
        "mantenimiento_post": mantenimiento_post,
        "medicion_alta": medicion_alta, "norma_ambiental": norma_ambiental,
        "reporte": reporte,
        # comisionamiento y punchlist
        "molino_005": molino_005, "comisionamiento": comisionamiento,
        "criterio_hidro": criterio_hidro, "test_hidro": test_hidro,
        "test_perf": test_perf,
        "aprob_contratista": aprob_contratista,
        "aprob_owner": aprob_owner, "aprob_qa": aprob_qa,
        "punch_001": punch_001, "punch_002": punch_002,
        "punch_003": punch_003, "cierre_punch_001": cierre_punch_001,
        "sev_a": sev_a, "sev_b": sev_b, "sev_c": sev_c,
        # categorías
        "operativo": operativo,
        "mantenimiento_corr": mantenimiento_corr,
        "abierto": abierto, "cerrado": cerrado, "en_progreso": en_progreso,
    }
    return u, handles


# ---------------------------------------------------------------------------
# Validaciones
# ---------------------------------------------------------------------------

def run_validations(u: Universe, lex: Lexicon, h: dict):
    results = []

    # V1 — Jerarquía espacial: frente → banco → nivel → tajo → yacimiento
    def chain_terr(start: Individual) -> list:
        chain = [start.id]
        cur = start
        for _ in range(10):
            ups = [f.value for f in u.facts_about(cur) if f.role == "dentro_de"]
            if not ups:
                break
            cur = ups[0]
            chain.append(cur.id)
        return chain

    chain = chain_terr(h["frente_a"])
    expected = ["frente_a_b03", "banco_03_tn", "nivel_4250",
                "tajo_norte", "yac_san_marcos"]
    results.append((
        "Jerarquía espacial: frente → banco → nivel → tajo → yacimiento",
        chain == expected,
        f"cadena: {' → '.join(chain)}",
    ))

    # V2 — D6: el camión estaba operativo el 1-Mar-2024, en mantenimiento
    # el 15-Mar-2024, operativo nuevamente el 1-Abr-2024
    t_1_mar = datetime(2024, 3, 1, tzinfo=timezone.utc)
    t_15_mar = datetime(2024, 3, 15, tzinfo=timezone.utc)
    t_1_abr = datetime(2024, 4, 1, tzinfo=timezone.utc)
    e_mar = [f for f in u.facts_about(h["camion_007"], at=t_1_mar)
             if f.role == "estado"]
    e_15 = [f for f in u.facts_about(h["camion_007"], at=t_15_mar)
            if f.role == "estado"]
    e_abr = [f for f in u.facts_about(h["camion_007"], at=t_1_abr)
             if f.role == "estado"]
    results.append((
        "D6: camión operativo→mantenimiento→operativo (oct→nov→dic 2024)",
        (len(e_mar) == 1 and e_mar[0].value.id == "operativo"
         and len(e_15) == 1
         and e_15[0].value.id == "en_mantenimiento_programado"
         and len(e_abr) == 1 and e_abr[0].value.id == "operativo"),
        f"1-Mar={[f.value.id for f in e_mar]}, "
        f"15-Mar={[f.value.id for f in e_15]}, "
        f"1-Abr={[f.value.id for f in e_abr]}",
    ))

    # V3 — Turno como articulador: tiene 3 operadores asignados
    facts_turno = u.facts_about(h["turno"])
    operadores = [f for f in facts_turno if f.role == "operador_asignado"]
    results.append((
        "Turno con 3 operadores asignados (rol de dominio multi-valor)",
        len(operadores) == 3,
        f"operadores: {sorted(f.value.id for f in operadores)}",
    ))

    # V4 — Extracción con múltiples unidades: toneladas + ley g/t
    facts_extr = u.facts_about(h["extraccion"])
    monto = [f for f in facts_extr if f.role == "monto"]
    ley = [f for f in facts_extr if f.role == "ley_mineral"]
    results.append((
        "Producción con múltiples unidades: 2400 t @ 8.2 g/t",
        (len(monto) == 1 and monto[0].value.payload["value"] == 2400
         and len(ley) == 1 and ley[0].value.payload["value"] == 8.2),
        f"monto={monto[0].value.payload['value']}, "
        f"ley={ley[0].value.payload['value']}",
    ))

    # V5 — Producción derivada: 632.7 onzas calculadas de la extracción
    facts_prod = u.facts_about(h["produccion_oro"])
    monto_oro = [f for f in facts_prod if f.role == "monto"]
    calc = [f for f in facts_prod if f.role == "calculado_de"]
    results.append((
        "Producción de oro calculada como sub-situación parte_de extracción",
        (len(monto_oro) == 1 and monto_oro[0].value.payload["value"] == 632.7
         and len(calc) == 1 and calc[0].value.id == "extr_001"),
        f"oro={monto_oro[0].value.payload['value']} oz, "
        f"calculado_de={[f.value.id for f in calc]}",
    ))

    # V6 — D5 al extremo: el desprendimiento NO tiene agente
    facts_des = u.facts_about(h["desprendimiento"])
    agente_des = [f for f in facts_des if f.role == "agente"]
    causa_des = [f for f in facts_des if f.role == "causado_por"]
    results.append((
        "D5: desprendimiento de roca SIN agente humano, con causa física",
        (len(agente_des) == 0 and len(causa_des) == 1
         and causa_des[0].value.id == "debilitamiento_pared_b03"),
        f"agente={len(agente_des)} (esperado 0), "
        f"causa={[f.value.id for f in causa_des]}",
    ))

    # V7 — Cadena causal: accidente ← desprendimiento ← debilitamiento
    causa_acc = [f for f in u.facts_about(h["accidente"]) if f.role == "causado_por"]
    cadena_causal = (
        len(causa_acc) == 1
        and causa_acc[0].value.id == "evento_desprendimiento_001"
    )
    results.append((
        "Cadena causal: accidente ← desprendimiento ← debilitamiento estructural",
        cadena_causal,
        f"accidente causado_por: {[f.value.id for f in causa_acc]}",
    ))

    # V8 — El accidente está parte_de el turno (articulador)
    parte_acc = [f.value.id for f in u.facts_about(h["accidente"])
                 if f.role == "parte_de"]
    results.append((
        "Accidente parte_de el turno articulador",
        parte_acc == ["turno_dia_2026_05_19"],
        f"parte_de: {parte_acc}",
    ))

    # V9 — Reporte regulatorio justificado por la norma + motivado por medición
    facts_rep = u.facts_about(h["reporte"])
    just_rep = [f for f in facts_rep if f.role == "justificado_por"]
    mot_rep = [f for f in facts_rep if f.role == "motivado_por"]
    results.append((
        "D7: reporte ambiental motivado_por medición + justificado_por norma",
        (len(just_rep) == 1 and just_rep[0].value.id == "ds_004_2017_minam"
         and len(mot_rep) == 1 and mot_rep[0].value.id == "medicion_001"),
        f"justif={[f.value.id for f in just_rep]}, "
        f"motiv={[f.value.id for f in mot_rep]}",
    ))

    # V10 — D5: el sensor_pm es un agente Q válido (no humano)
    facts_med = u.facts_about(h["medicion_alta"])
    agente_med = [f for f in facts_med if f.role == "agente"]
    results.append((
        "D5: sensor de calidad de aire como agente Q (no humano)",
        (len(agente_med) == 1
         and agente_med[0].value.id == "sensor_pm10_estacion_3"
         and h["sensor_pm"].axis == Axis.Q),
        f"agente: {[f.value.id for f in agente_med]}, "
        f"eje: {h['sensor_pm'].axis}",
    ))

    # V11 — WH: ¿cuántas toneladas de oro se extrajeron en el turno?
    r = query(u, Pattern(
        fixed={"agente": h["operador1"]},
        ask={"monto": Var()},
        type_constraint=u.ind("accion_extraer_mineral"),
    ))
    results.append((
        "WH: ¿cuánto mineral extrajo el operador Quispe?",
        len(r) == 1 and r[0]["monto"].payload["value"] == 2400,
        f"monto: {[x['monto'].payload['value'] for x in r]}",
    ))

    # V12 — Política liberal: roles de dominio admitidos sin declarar
    facts_extr = u.facts_about(h["extraccion"])
    roles_extr = {f.role for f in facts_extr}
    dom_roles = {"ley_mineral", "ley_unidad", "extraido"}
    results.append((
        "Política liberal: ley_mineral / ley_unidad / extraido admitidos sin declarar",
        dom_roles.issubset(roles_extr),
        f"roles de dominio en extracción: {sorted(roles_extr & dom_roles)}",
    ))

    # ========== Validaciones de comisionamiento y punchlist ==========

    # V13 — Acceptance criterion: el criterio y el valor medido son DOS
    # entidades distintas. El criterio tiene tolerancia; el test tiene
    # el valor real.
    crit_facts = u.facts_about(h["criterio_hidro"])
    crit_min = [f for f in crit_facts if f.role == "presion_minima"]
    test_facts = u.facts_about(h["test_hidro"])
    valor = [f for f in test_facts if f.role == "valor_medido"]
    verifica = [f for f in test_facts if f.role == "verifica_criterio"]
    results.append((
        "Acceptance criterion separado del valor medido (8 bar mín. vs 8.4 bar real)",
        (len(crit_min) == 1 and crit_min[0].value.payload["value"] == 8.0
         and len(valor) == 1 and valor[0].value.payload["value"] == 8.4
         and len(verifica) == 1
         and verifica[0].value.id == "criterio_hidrostatica_v1"),
        f"criterio_min={crit_min[0].value.payload['value']} bar, "
        f"medido={valor[0].value.payload['value']} bar",
    ))

    # V14 — Tres sign-offs paralelos sobre el mismo test
    signoffs = [
        s for s in u.facts_with_role("tema")
        if s.value.id == h["test_hidro"].id
    ]
    # Filtramos solo las situaciones de tipo aprobar_checkpoint
    signoff_situs = []
    for f in signoffs:
        for inst in u.facts_about(f.subject):
            if (inst.role == "instancia_de"
                    and inst.value.id == "accion_aprobar_checkpoint"):
                signoff_situs.append(f.subject)
                break
    agentes_so = set()
    for s in signoff_situs:
        for f in u.facts_about(s):
            if f.role == "agente":
                agentes_so.add(f.value.id)
    expected_agentes = {"empresa_metso_outotec", "ing_owner_paredes",
                        "qa_castro"}
    results.append((
        "Tres sign-offs paralelos sobre el mismo test (contratista + owner + QA)",
        agentes_so == expected_agentes,
        f"agentes firmantes: {sorted(agentes_so)}",
    ))

    # V15 — Severidad ordenada en K: A=1 < B=2 < C=3
    nivel_a = [f for f in u.facts_about(h["sev_a"])
               if f.role == "nivel_severidad"]
    nivel_b = [f for f in u.facts_about(h["sev_b"])
               if f.role == "nivel_severidad"]
    nivel_c = [f for f in u.facts_about(h["sev_c"])
               if f.role == "nivel_severidad"]
    ok_orden = (
        len(nivel_a) == 1 and nivel_a[0].value.payload["value"] == 1
        and len(nivel_b) == 1 and nivel_b[0].value.payload["value"] == 2
        and len(nivel_c) == 1 and nivel_c[0].value.payload["value"] == 3
    )
    results.append((
        "Severidad ordenada en K vía atributo `nivel_severidad`: A=1 < B=2 < C=3",
        ok_orden,
        f"A={nivel_a[0].value.payload['value']}, "
        f"B={nivel_b[0].value.payload['value']}, "
        f"C={nivel_c[0].value.payload['value']}",
    ))

    # V16 — Punchitem con 3 roles distintos sobre Q (encontró, responsable,
    # verificador)
    facts_p1 = u.facts_about(h["punch_001"])
    encontro = [f for f in facts_p1 if f.role == "agente"]
    resp = [f for f in facts_p1 if f.role == "responsable"]
    verif = [f for f in facts_p1 if f.role == "verificador"]
    results.append((
        "Punchitem con 3 roles Q distintos: agente (encontró) + responsable + verificador",
        (len(encontro) == 1 and encontro[0].value.id == "qa_castro"
         and len(resp) == 1 and resp[0].value.id == "empresa_metso_outotec"
         and len(verif) == 1 and verif[0].value.id == "ing_owner_paredes"),
        f"encontró={[f.value.id for f in encontro]}, "
        f"responsable={[f.value.id for f in resp]}, "
        f"verificador={[f.value.id for f in verif]}",
    ))

    # V17 — Punchitem 001 cerrado el 25-Abr (D6: pasó por 3 estados)
    t_15_abr = datetime(2026, 4, 15, 12, tzinfo=timezone.utc)
    t_18_abr = datetime(2026, 4, 18, tzinfo=timezone.utc)
    t_25_abr = datetime(2026, 4, 25, tzinfo=timezone.utc)
    e_15 = [f for f in u.facts_about(h["punch_001"], at=t_15_abr)
            if f.role == "estado"]
    e_18 = [f for f in u.facts_about(h["punch_001"], at=t_18_abr)
            if f.role == "estado"]
    e_25 = [f for f in u.facts_about(h["punch_001"], at=t_25_abr)
            if f.role == "estado"]
    results.append((
        "D6: punchitem A pasó por abierto → en_progreso → cerrado",
        (len(e_15) == 1 and e_15[0].value.id == "abierto"
         and len(e_18) == 1 and e_18[0].value.id == "en_progreso"
         and len(e_25) == 1 and e_25[0].value.id == "cerrado"),
        f"15-Abr={[f.value.id for f in e_15]}, "
        f"18-Abr={[f.value.id for f in e_18]}, "
        f"25-Abr={[f.value.id for f in e_25]}",
    ))

    # V18 — Estado agregado derivado: ¿está el comisionamiento listo para
    # operación comercial? La regla: cero punchitems severidad A abiertos.
    # Esto se computa al vuelo (no es un hecho atómico — es lógica de regla).
    open_a = 0
    open_b = 0
    open_c = 0
    for f in u.facts_with_role("instancia_de"):
        if f.value.id == "accion_registrar_punchitem":
            pid = f.subject
            estados = [
                ff for ff in u.facts_about(pid, at=t_25_abr)
                if ff.role == "estado"
            ]
            severidades = [
                ff for ff in u.facts_about(pid)
                if ff.role == "severidad"
            ]
            if estados and severidades and estados[0].value.id != "cerrado":
                sev_id = severidades[0].value.id
                if sev_id == "severidad_A":
                    open_a += 1
                elif sev_id == "severidad_B":
                    open_b += 1
                elif sev_id == "severidad_C":
                    open_c += 1
    listo_para_operacion = (open_a == 0)
    results.append((
        "Estado agregado derivado: comisionamiento OK cuando 0 punchitems A abiertos",
        listo_para_operacion and open_b == 1 and open_c == 1,
        f"abiertos al 25-Abr: A={open_a}, B={open_b}, C={open_c} "
        f"→ listo_para_operacion={listo_para_operacion}",
    ))

    return results


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main() -> bool:
    lex = build_lexicon()
    u, h = build_universe(lex)

    print("=" * 72)
    print("DOMINIO MINERA — operación minera de gran escala")
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
