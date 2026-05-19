"""Dominio Universidad — sistema académico.

Stress-test del modelo en un dominio donde lo que predomina son los
tiempos largos y los grafos de dependencia:

- Estructura académica jerárquica: carrera → año → semestre → curso.
- Prerequisitos como grafo dirigido acíclico (DAG).
- Multiples roles de una misma persona: estudiante en una carrera y
  asistente docente en otro curso, eventualmente investigador.
- Calificaciones que se asignan, se reclaman y se rectifican,
  preservando el historial.
- Inscripciones con vigencia (D6).
- Defensa de tesis con director y jurado (múltiples roles Q).
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
# Lexicon del dominio Universidad
# ---------------------------------------------------------------------------

def build_lexicon() -> Lexicon:
    lex = Lexicon()
    for verb, st, obl, opt in [
        ("inscribir", "accion_inscribir",
            ["agente", "tema"],
            ["lugar_de", "momento", "motivado_por"]),
        ("dictar", "accion_dictar_curso",
            ["agente", "tema"],
            ["lugar_de", "momento", "inicio", "fin"]),
        ("evaluar", "accion_evaluar",
            ["agente", "paciente", "tema", "puntaje"],
            ["momento", "instrumento", "lugar_de"]),
        ("reclamar", "accion_reclamar_calificacion",
            ["agente", "tema"],
            ["motivado_por", "momento", "justificado_por"]),
        ("rectificar_nota", "accion_rectificar_calificacion",
            ["agente", "tema", "puntaje"],
            ["motivado_por", "momento"]),
        ("graduar", "accion_graduar",
            ["agente", "beneficiario"],
            ["tema", "momento", "lugar_de"]),
        ("defender_tesis", "accion_defender_tesis",
            ["agente", "tema"],
            ["momento", "lugar_de", "puntaje"]),
    ]:
        lex.register(LexiconEntry(verb=verb, situation_type=st,
                                  obligatory=obl, optional=opt))

    lex.register_domain_dialect("universidad", {
        "estudiante": "agente",
        "docente": "agente",
        "tesista": "agente",
        "director_tesis": "agente",
    })
    return lex


# ---------------------------------------------------------------------------
# Universo
# ---------------------------------------------------------------------------

def build_universe(lex: Lexicon) -> Tuple[Universe, dict]:
    cat = Catalog()
    u = Universe(name="universidad", catalog=cat)

    # === K — Categorías ===
    aprobado = u.add_individual(category("aprobado"))
    desaprobado = u.add_individual(category("desaprobado"))
    en_curso = u.add_individual(category("en_curso"))
    vigente = u.add_individual(category("vigente"))
    cancelada = u.add_individual(category("cancelada"))
    real = u.add_individual(category("real"))
    nota_aprobatoria = u.add_individual(category("nota_aprobatoria"))
    nota_excelente = u.add_individual(category("nota_excelente"))

    # === Q — Personas ===
    universidad = u.add_individual(Individual(
        id="u_central", axis=Axis.Q, label="Universidad Central"))
    decano = u.add_individual(Individual(
        id="prof_garcia", axis=Axis.Q, label="Decano García"))
    dra_lopez = u.add_individual(Individual(
        id="dra_lopez", axis=Axis.Q, label="Dra. López (Profesora)"))
    dr_morales = u.add_individual(Individual(
        id="dr_morales", axis=Axis.Q, label="Dr. Morales (Profesor)"))
    dra_diaz = u.add_individual(Individual(
        id="dra_diaz", axis=Axis.Q, label="Dra. Díaz (Profesora)"))

    # Estudiantes
    ana = u.add_individual(Individual(
        id="est_ana", axis=Axis.Q, label="Ana Ramírez"))
    luis = u.add_individual(Individual(
        id="est_luis", axis=Axis.Q, label="Luis Soto"))
    maria = u.add_individual(Individual(
        id="est_maria", axis=Axis.Q, label="María Yupanqui"))

    # === L — Lugares ===
    facultad_ing = u.add_individual(Individual(
        id="fac_ingenieria", axis=Axis.L,
        label="Facultad de Ingeniería"))
    aula_201 = u.add_individual(Individual(
        id="aula_201", axis=Axis.L, label="Aula 201"))
    aula_315 = u.add_individual(Individual(
        id="aula_315", axis=Axis.L, label="Aula 315"))
    auditorio = u.add_individual(Individual(
        id="auditorio_central", axis=Axis.L, label="Auditorio Central"))

    # ====================================================================
    # CASO 1 — Estructura académica jerárquica
    # ====================================================================
    # Carrera de Ingeniería de Sistemas
    carrera_is = u.add_individual(Individual(
        id="carrera_ing_sistemas", axis=Axis.O,
        label="Ingeniería de Sistemas"))
    u.assert_fact(carrera_is, "instancia_de",
                  u.add_individual(category("tipo_carrera_pregrado")))
    u.assert_fact(carrera_is, "duracion_anios",
                  n(5, "años", "n_5_anios"))
    u.assert_fact(carrera_is, "lugar_de", facultad_ing)

    # Plan de estudios → años → semestres → cursos (parte_de recursivo)
    primer_anio = u.add_individual(Individual(
        id="primer_anio_is", axis=Axis.O, label="Primer año IS"))
    u.assert_fact(primer_anio, "instancia_de",
                  u.add_individual(category("anio_academico")))
    u.assert_fact(primer_anio, "parte_de", carrera_is)
    u.assert_fact(primer_anio, "orden", n(1, "ordinal", "n_1_orden_anio"))

    sem_2026_i = u.add_individual(Individual(
        id="semestre_2026_i", axis=Axis.O, label="Semestre 2026-I"))
    u.assert_fact(sem_2026_i, "instancia_de",
                  u.add_individual(category("semestre_academico")))
    u.assert_fact(sem_2026_i, "parte_de", primer_anio)
    u.assert_fact(sem_2026_i, "inicio", at("2026-03-15T00:00:00+00:00"))
    u.assert_fact(sem_2026_i, "fin", at("2026-07-25T00:00:00+00:00"))

    # Cursos del primer semestre
    mate1 = u.add_individual(Individual(
        id="curso_mate1", axis=Axis.O, label="Matemática I"))
    u.assert_fact(mate1, "instancia_de",
                  u.add_individual(category("curso_universitario")))
    u.assert_fact(mate1, "parte_de", sem_2026_i)
    u.assert_fact(mate1, "creditos", n(5, "créditos", "n_5_creditos"))
    u.assert_fact(mate1, "agente", dra_lopez)   # docente del curso

    intro_prog = u.add_individual(Individual(
        id="curso_intro_prog", axis=Axis.O,
        label="Introducción a la Programación"))
    u.assert_fact(intro_prog, "instancia_de", u.ind("curso_universitario"))
    u.assert_fact(intro_prog, "parte_de", sem_2026_i)
    u.assert_fact(intro_prog, "creditos", n(4, "créditos", "n_4_creditos"))
    u.assert_fact(intro_prog, "agente", dr_morales)

    # Curso del segundo semestre (para mostrar prerequisitos)
    sem_2026_ii = u.add_individual(Individual(
        id="semestre_2026_ii", axis=Axis.O, label="Semestre 2026-II"))
    u.assert_fact(sem_2026_ii, "instancia_de",
                  u.add_individual(category("semestre_academico")))
    u.assert_fact(sem_2026_ii, "parte_de", primer_anio)
    u.assert_fact(sem_2026_ii, "inicio", at("2026-08-15T00:00:00+00:00"))
    u.assert_fact(sem_2026_ii, "fin", at("2026-12-20T00:00:00+00:00"))

    mate2 = u.add_individual(Individual(
        id="curso_mate2", axis=Axis.O, label="Matemática II"))
    u.assert_fact(mate2, "instancia_de", u.ind("curso_universitario"))
    u.assert_fact(mate2, "parte_de", sem_2026_ii)
    u.assert_fact(mate2, "creditos", n(5, "créditos", "n_5_creditos_2"))

    estructuras_datos = u.add_individual(Individual(
        id="curso_estr_datos", axis=Axis.O,
        label="Estructuras de Datos"))
    u.assert_fact(estructuras_datos, "instancia_de", u.ind("curso_universitario"))
    u.assert_fact(estructuras_datos, "parte_de", sem_2026_ii)
    u.assert_fact(estructuras_datos, "creditos",
                  n(5, "créditos", "n_5_creditos_3"))

    # ====================================================================
    # CASO 2 — Prerequisitos como DAG
    # ====================================================================
    # mate2 requiere mate1 aprobada; estr_datos requiere intro_prog
    u.assert_fact(mate2, "requiere_prerequisito", mate1)
    u.assert_fact(estructuras_datos, "requiere_prerequisito", intro_prog)

    # Curso avanzado con doble prerequisito
    algoritmos = u.add_individual(Individual(
        id="curso_algoritmos", axis=Axis.O,
        label="Algoritmos Avanzados"))
    u.assert_fact(algoritmos, "instancia_de", u.ind("curso_universitario"))
    u.assert_fact(algoritmos, "requiere_prerequisito", mate2)
    u.assert_fact(algoritmos, "requiere_prerequisito", estructuras_datos)

    # ====================================================================
    # CASO 3 — Inscripciones con vigencia (D6)
    # ====================================================================
    # Ana se inscribe en Matemática I al inicio del semestre 2026-I
    insc_ana_mate1 = ingest_situation(u, lex, "inscribir", roles={
        "agente": ana,
        "tema": mate1,
        "momento": at("2026-03-10T10:00:00+00:00"),
    }, sit_id="insc_ana_mate1")

    # Estado de la inscripción a lo largo del semestre
    t_insc = datetime(2026, 3, 10, tzinfo=timezone.utc)
    t_fin_semestre = datetime(2026, 7, 25, tzinfo=timezone.utc)
    u.assert_fact(insc_ana_mate1, "estado", vigente,
                  valid_from=t_insc, valid_to=t_fin_semestre)

    insc_ana_prog = ingest_situation(u, lex, "inscribir", roles={
        "agente": ana,
        "tema": intro_prog,
        "momento": at("2026-03-10T10:10:00+00:00"),
    }, sit_id="insc_ana_prog")
    u.assert_fact(insc_ana_prog, "estado", vigente,
                  valid_from=t_insc, valid_to=t_fin_semestre)

    # Luis se inscribió en Mate I pero la canceló al mes
    insc_luis_mate1 = ingest_situation(u, lex, "inscribir", roles={
        "agente": luis,
        "tema": mate1,
        "momento": at("2026-03-12T14:00:00+00:00"),
    }, sit_id="insc_luis_mate1")
    t_cancel_luis = datetime(2026, 4, 15, tzinfo=timezone.utc)
    u.assert_fact(insc_luis_mate1, "estado", vigente,
                  valid_from=datetime(2026, 3, 12, tzinfo=timezone.utc),
                  valid_to=t_cancel_luis)
    u.assert_fact(insc_luis_mate1, "estado", cancelada,
                  valid_from=t_cancel_luis)

    # ====================================================================
    # CASO 4 — Múltiples roles de una misma persona
    # ====================================================================
    # María es estudiante de cuarto año Y asistente docente de Mate I.
    # En el grafo es un solo individuo en Q; sus distintos roles aparecen
    # en distintas situaciones reificadas.
    insc_maria_mate2 = ingest_situation(u, lex, "inscribir", roles={
        "agente": maria,
        "tema": estructuras_datos,
        "momento": at("2026-03-09T08:00:00+00:00"),
    }, sit_id="insc_maria_estr_datos")
    u.assert_fact(insc_maria_mate2, "estado", vigente,
                  valid_from=datetime(2026, 3, 9, tzinfo=timezone.utc))

    # María también es jefa de práctica (TA) del curso intro_prog
    asignacion_ta = u.add_individual(Individual(
        id="asig_ta_maria_intro_prog", axis=Axis.O,
        label="Asignación TA María en Intro Prog"))
    u.assert_fact(asignacion_ta, "instancia_de",
                  u.add_individual(category("asignacion_docente_asistente")))
    u.assert_fact(asignacion_ta, "agente", maria)
    u.assert_fact(asignacion_ta, "tema", intro_prog)
    u.assert_fact(asignacion_ta, "rol_funcional",
                  u.add_individual(category("jefe_de_practica")))
    u.assert_fact(asignacion_ta, "monto_pago",
                  n(800, "USD", "n_800_usd"))

    # ====================================================================
    # CASO 5 — Calificación, reclamo, rectificación
    # ====================================================================
    # Dra. López evalúa el examen final de Ana en Mate I → nota inicial 12
    nota_12 = n(12, "puntos", "n_12_puntos")
    # El examen físico es un objeto (O), no una categoría
    examen_mate1 = u.add_individual(Individual(
        id="examen_final_mate1_001", axis=Axis.O,
        label="Examen final Mate I de Ana"))
    u.assert_fact(examen_mate1, "instancia_de",
                  u.add_individual(category("examen_escrito_final")))

    evaluacion = ingest_situation(u, lex, "evaluar", roles={
        "agente": dra_lopez,
        "paciente": ana,
        "tema": mate1,
        "puntaje": nota_12,
        "momento": at("2026-07-15T16:00:00+00:00"),
        "instrumento": examen_mate1,
    }, sit_id="eval_ana_mate1_001")

    # La calificación inicial es vigente hasta el reclamo
    t_eval = datetime(2026, 7, 15, tzinfo=timezone.utc)
    t_reclamo = datetime(2026, 7, 20, tzinfo=timezone.utc)
    t_rect = datetime(2026, 7, 25, tzinfo=timezone.utc)

    u.assert_fact(evaluacion, "puntaje_vigente", nota_12,
                  valid_from=t_eval, valid_to=t_rect)

    # Ana reclama la nota
    reclamo = ingest_situation(u, lex, "reclamar", roles={
        "agente": ana,
        "tema": evaluacion,
        "momento": at("2026-07-20T11:00:00+00:00"),
        "motivado_por": u.add_individual(Individual(
            id="motivo_pregunta3_mal_corregida", axis=Axis.O,
            label="Pregunta 3 mal corregida")),
    }, sit_id="reclamo_ana_eval_001")

    # La revisión confirma el reclamo → rectificación a 14
    nota_14 = n(14, "puntos", "n_14_puntos")
    rectificacion = ingest_situation(u, lex, "rectificar_nota", roles={
        "agente": dra_lopez,
        "tema": evaluacion,
        "puntaje": nota_14,
        "momento": at("2026-07-25T10:00:00+00:00"),
        "motivado_por": reclamo,
    }, sit_id="rectif_ana_001")
    u.assert_fact(rectificacion, "rectifica", evaluacion)

    # Nueva calificación vigente desde la rectificación
    u.assert_fact(evaluacion, "puntaje_vigente", nota_14,
                  valid_from=t_rect)

    # ====================================================================
    # CASO 6 — Defensa de tesis con director y jurado
    # ====================================================================
    # Una tesis avanzada: la presenta una persona, dirigida por un director
    # y evaluada por un jurado de tres personas.
    tesis = u.add_individual(Individual(
        id="tesis_maria_2026", axis=Axis.O,
        label="Tesis María: ML aplicada a salud pública"))
    u.assert_fact(tesis, "instancia_de",
                  u.add_individual(category("tesis_de_grado")))
    u.assert_fact(tesis, "agente", maria)
    u.assert_fact(tesis, "director_tesis", dra_diaz)
    u.assert_fact(tesis, "inicio",
                  at("2026-01-15T00:00:00+00:00"))

    nota_18 = n(18, "puntos", "n_18_puntos")
    defensa = ingest_situation(u, lex, "defender_tesis", roles={
        "agente": maria,
        "tema": tesis,
        "momento": at("2026-12-10T15:00:00+00:00"),
        "lugar_de": auditorio,
        "puntaje": nota_18,
    }, sit_id="defensa_tesis_maria_001")
    # Múltiples miembros de jurado — roles de dominio
    u.assert_fact(defensa, "jurado_presidente", decano)
    u.assert_fact(defensa, "jurado_vocal", dra_lopez)
    u.assert_fact(defensa, "jurado_secretario", dr_morales)
    u.assert_fact(defensa, "calificacion", nota_excelente)

    # Graduación (resultado de la defensa exitosa)
    graduacion = ingest_situation(u, lex, "graduar", roles={
        "agente": universidad,
        "beneficiario": maria,
        "tema": carrera_is,
        "momento": at("2026-12-20T10:00:00+00:00"),
        "lugar_de": auditorio,
    }, sit_id="grad_maria_001")
    u.assert_fact(graduacion, "justificado_por", defensa)

    handles = {
        # personas
        "decano": decano, "dra_lopez": dra_lopez, "dr_morales": dr_morales,
        "dra_diaz": dra_diaz,
        "ana": ana, "luis": luis, "maria": maria,
        "universidad": universidad,
        # estructura
        "carrera_is": carrera_is, "primer_anio": primer_anio,
        "sem_2026_i": sem_2026_i, "sem_2026_ii": sem_2026_ii,
        "mate1": mate1, "intro_prog": intro_prog,
        "mate2": mate2, "estructuras_datos": estructuras_datos,
        "algoritmos": algoritmos,
        # situaciones
        "insc_ana_mate1": insc_ana_mate1,
        "insc_luis_mate1": insc_luis_mate1,
        "asignacion_ta": asignacion_ta,
        "evaluacion": evaluacion, "reclamo": reclamo,
        "rectificacion": rectificacion,
        "tesis": tesis, "defensa": defensa, "graduacion": graduacion,
        # categorías
        "vigente": vigente, "cancelada": cancelada,
    }
    return u, handles


# ---------------------------------------------------------------------------
# Validaciones
# ---------------------------------------------------------------------------

def run_validations(u: Universe, lex: Lexicon, h: dict):
    results = []

    # V1 — Estructura jerárquica: mate1 → sem_2026_i → primer_anio → carrera
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

    chain = chain_to_root(h["mate1"])
    expected = ["curso_mate1", "semestre_2026_i",
                "primer_anio_is", "carrera_ing_sistemas"]
    results.append((
        "Jerarquía académica: curso → semestre → año → carrera",
        chain == expected,
        f"cadena: {' → '.join(chain)}",
    ))

    # V2 — DAG de prerequisitos: algoritmos requiere mate2 Y estructuras_datos
    prereqs = [f.value.id for f in u.facts_about(h["algoritmos"])
               if f.role == "requiere_prerequisito"]
    results.append((
        "DAG de prerequisitos: algoritmos requiere mate2 + estructuras_datos",
        set(prereqs) == {"curso_mate2", "curso_estr_datos"},
        f"prerequisitos: {sorted(prereqs)}",
    ))

    # V3 — Múltiples roles de María: estudiante Y asistente docente
    # María es agente en inscripción Y en asignación TA
    facts_maria = u.facts_with_value(h["maria"])
    como_agente = [f for f in facts_maria if f.role == "agente"]
    tipos_situ = set()
    for f in como_agente:
        for sf in u.facts_about(f.subject):
            if sf.role == "instancia_de":
                tipos_situ.add(sf.value.id)
    results.append((
        "Múltiples roles de una persona: María es estudiante Y TA Y tesista",
        ("accion_inscribir" in tipos_situ
         and "asignacion_docente_asistente" in tipos_situ
         and "accion_defender_tesis" in tipos_situ),
        f"tipos de situación donde María es agente: {sorted(tipos_situ)}",
    ))

    # V4 — Vigencia D6: la inscripción de Luis estaba vigente el 30/3 y
    # cancelada el 30/4
    t_30_marzo = datetime(2026, 3, 30, tzinfo=timezone.utc)
    t_30_abril = datetime(2026, 4, 30, tzinfo=timezone.utc)
    estado_marzo = [
        f for f in u.facts_about(h["insc_luis_mate1"], at=t_30_marzo)
        if f.role == "estado"
    ]
    estado_abril = [
        f for f in u.facts_about(h["insc_luis_mate1"], at=t_30_abril)
        if f.role == "estado"
    ]
    results.append((
        "D6: inscripción de Luis vigente el 30-Mar, cancelada el 30-Abr",
        (len(estado_marzo) == 1 and estado_marzo[0].value.id == "vigente"
         and len(estado_abril) == 1
         and estado_abril[0].value.id == "cancelada"),
        f"marzo: {[f.value.id for f in estado_marzo]}, "
        f"abril: {[f.value.id for f in estado_abril]}",
    ))

    # V5 — Calificación bitemporal: la nota era 12 el 18 julio, 14 el 30 julio
    t_18_jul = datetime(2026, 7, 18, tzinfo=timezone.utc)
    t_30_jul = datetime(2026, 7, 30, tzinfo=timezone.utc)
    nota_18 = [
        f for f in u.facts_about(h["evaluacion"], at=t_18_jul)
        if f.role == "puntaje_vigente"
    ]
    nota_30 = [
        f for f in u.facts_about(h["evaluacion"], at=t_30_jul)
        if f.role == "puntaje_vigente"
    ]
    results.append((
        "Calificación bitemporal: nota=12 el 18-Jul, nota=14 el 30-Jul (post rectificación)",
        (len(nota_18) == 1 and nota_18[0].value.payload["value"] == 12
         and len(nota_30) == 1 and nota_30[0].value.payload["value"] == 14),
        f"18-jul={nota_18[0].value.payload['value']}, "
        f"30-jul={nota_30[0].value.payload['value']}",
    ))

    # V6 — D7: rectificación motivada por reclamo + rectifica evaluación
    facts_rect = u.facts_about(h["rectificacion"])
    motiv = [f for f in facts_rect if f.role == "motivado_por"]
    rect = [f for f in facts_rect if f.role == "rectifica"]
    results.append((
        "D7: rectificación motivada_por reclamo y rectifica evaluación original",
        (len(motiv) == 1 and motiv[0].value.id == "reclamo_ana_eval_001"
         and len(rect) == 1
         and rect[0].value.id == "eval_ana_mate1_001"),
        f"motiv={[f.value.id for f in motiv]}, "
        f"rect={[f.value.id for f in rect]}",
    ))

    # V7 — Defensa con jurado de 3 personas con roles distintos
    facts_def = u.facts_about(h["defensa"])
    jurado_pres = [f for f in facts_def if f.role == "jurado_presidente"]
    jurado_voc = [f for f in facts_def if f.role == "jurado_vocal"]
    jurado_sec = [f for f in facts_def if f.role == "jurado_secretario"]
    results.append((
        "Defensa de tesis: 3 miembros de jurado con roles distintos",
        (len(jurado_pres) == 1 and len(jurado_voc) == 1
         and len(jurado_sec) == 1),
        f"presidente={[f.value.id for f in jurado_pres]}, "
        f"vocal={[f.value.id for f in jurado_voc]}, "
        f"secretario={[f.value.id for f in jurado_sec]}",
    ))

    # V8 — La graduación está justificada por la defensa exitosa
    facts_grad = u.facts_about(h["graduacion"])
    justif = [f for f in facts_grad if f.role == "justificado_por"]
    results.append((
        "Graduación justificada_por la defensa exitosa",
        len(justif) == 1 and justif[0].value.id == "defensa_tesis_maria_001",
        f"justif: {[f.value.id for f in justif]}",
    ))

    # V9 — WH: ¿quién dicta Matemática I?
    facts_mate1 = u.facts_about(h["mate1"])
    docente = [f for f in facts_mate1 if f.role == "agente"]
    results.append((
        "WH: ¿quién dicta Matemática I?",
        len(docente) == 1 and docente[0].value.id == "dra_lopez",
        f"docente: {[f.value.id for f in docente]}",
    ))

    # V10 — WH bitemporal: ¿cuántos alumnos inscriptos en Mate I el 1-Mayo?
    # (Ana sigue vigente, Luis ya canceló)
    t_1_mayo = datetime(2026, 5, 1, tzinfo=timezone.utc)
    inscripciones_activas = []
    for f in u.facts_with_role("instancia_de", at=t_1_mayo):
        if f.value.id == "accion_inscribir":
            estados = [
                ff for ff in u.facts_about(f.subject, at=t_1_mayo)
                if ff.role == "estado"
            ]
            temas = [
                ff for ff in u.facts_about(f.subject, at=t_1_mayo)
                if ff.role == "tema"
            ]
            if (any(e.value.id == "vigente" for e in estados)
                    and any(t.value.id == "curso_mate1" for t in temas)):
                inscripciones_activas.append(f.subject.id)
    results.append((
        "WH bitemporal: ¿quiénes seguían inscriptos en Mate I el 1-Mayo?",
        set(inscripciones_activas) == {"insc_ana_mate1"},
        f"activos: {sorted(inscripciones_activas)}",
    ))

    # V11 — Política liberal: roles de dominio admitidos
    facts_def = u.facts_about(h["defensa"])
    roles_def = {f.role for f in facts_def}
    expected_roles = {"jurado_presidente", "jurado_vocal", "jurado_secretario"}
    results.append((
        "Política liberal: jurado_presidente / jurado_vocal / jurado_secretario aceptados sin declarar",
        expected_roles.issubset(roles_def),
        f"roles de dominio en la defensa: {sorted(roles_def & expected_roles)}",
    ))

    return results


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main() -> bool:
    lex = build_lexicon()
    u, h = build_universe(lex)

    print("=" * 72)
    print("DOMINIO UNIVERSIDAD — sistema académico")
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
