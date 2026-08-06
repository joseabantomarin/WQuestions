from wquestions_mcp.session import WQSession


def test_list_axes_returns_seven_axes():
    s = WQSession()
    out = s.list_axes()
    codes = [a["code"] for a in out["axes"]]
    assert codes == ["Q", "O", "L", "T", "N", "K", "M"]


def test_list_roles_includes_agente_with_signature():
    s = WQSession()
    roles = {r["name"]: r for r in s.list_roles()["roles"]}
    assert roles["agente"]["domain"] == "O"
    assert roles["agente"]["range"] == "Q"
    assert roles["agente"]["functional"] is True


def test_reset_gives_empty_universe():
    s = WQSession()
    s.reset()
    assert len(s.universe.facts) == 0


def test_add_entity_registers_individual():
    s = WQSession()
    out = s.add_entity("ana", "Q", "Ana")
    assert out["ok"] is True
    assert s.universe.individuals["ana"].axis.value == "Q"


def test_add_entity_rejects_predicate_axis():
    s = WQSession()
    out = s.add_entity("bad", "M", "nope")
    assert out["ok"] is False
    assert "axis" in out["error"].lower()


def test_define_verb_registers_entry():
    s = WQSession()
    out = s.define_verb("visit", "action_visit",
                        obligatory=["agente"], optional=["lugar_de", "momento"])
    assert out["ok"] is True
    entry = s.lexicon.resolve("visit")
    assert entry is not None
    assert entry.situation_type == "action_visit"
    assert entry.obligatory == ["agente"]


def test_assert_situation_auto_registers_verb_and_ingests():
    s = WQSession()
    s.add_entity("ana", "Q", "Ana")
    s.add_entity("spa_oasis", "L", "Spa Oasis")
    out = s.assert_situation(
        "visit",
        roles={"agente": "ana", "lugar_de": "spa_oasis"},
    )
    assert out["ok"] is True
    # the reified situation carries the agente fact
    roles_seen = {f["role"] for f in out["facts"]}
    assert "agente" in roles_seen and "lugar_de" in roles_seen


def test_assert_situation_creates_inline_entities():
    s = WQSession()
    out = s.assert_situation(
        "visit",
        roles={"agente": {"id": "bob", "axis": "Q", "label": "Bob"}},
    )
    assert out["ok"] is True
    assert "bob" in s.universe.individuals


def test_assert_situation_reports_missing_entity():
    s = WQSession()
    out = s.assert_situation("visit", roles={"agente": "ghost"})
    assert out["ok"] is False
    assert "ghost" in out["error"]


def test_add_entity_axis_conflict_returns_error():
    s = WQSession()
    s.add_entity("x", "Q")
    out = s.add_entity("x", "O")
    assert out["ok"] is False
    assert "error" in out


def test_assert_situation_inline_spec_missing_axis_returns_error():
    s = WQSession()
    out = s.assert_situation("visit", roles={"agente": {"id": "bob"}})
    assert out["ok"] is False
    assert "error" in out


def test_ask_projects_the_asked_role():
    s = WQSession()
    s.add_entity("ana", "Q", "Ana")
    s.add_entity("spa_oasis", "L", "Spa Oasis")
    s.assert_situation("visit", roles={"agente": "ana", "lugar_de": "spa_oasis"})

    out = s.ask(fixed={"lugar_de": "spa_oasis"}, ask=["agente"])
    assert out["count"] == 1
    assert out["results"][0]["agente"] == "ana"


def test_show_model_reports_counts():
    s = WQSession()
    s.add_entity("ana", "Q", "Ana")
    s.assert_situation("visit", roles={"agente": "ana"})
    out = s.show_model()
    assert out["fact_count"] >= 1
    assert any(f["role"] == "agente" for f in out["facts"])


def test_load_example_spa_populates_model():
    s = WQSession()
    out = s.load_example("spa")
    assert out["ok"] is True
    assert out["fact_count"] > 0


def test_load_example_unknown_name_errors():
    s = WQSession()
    out = s.load_example("does_not_exist")
    assert out["ok"] is False


def test_ask_malformed_at_returns_error():
    s = WQSession()
    out = s.ask(fixed=None, ask=["agente"], at="not-a-date")
    assert out["ok"] is False
    assert "error" in out


def test_list_axes_teaches_n_needs_unit_and_m_is_predicate():
    s = WQSession()
    axes = {a["code"]: a for a in s.list_axes()["axes"]}
    assert "unit" in axes["N"]["how_to_use"].lower()
    assert "predicate" in axes["M"]["how_to_use"].lower()
    assert axes["O"]["gotcha"]  # non-empty


def test_list_roles_states_open_policy_and_common_roles():
    s = WQSession()
    out = s.list_roles()
    assert "open" in out["policy"].lower()
    assert "agente" in out["common"] and "por_cuanto" in out["common"]


def test_show_model_has_append_only_legend():
    s = WQSession()
    out = s.show_model()
    assert "append-only" in out["legend"].lower()


def test_add_entity_n_without_unit_is_rejected():
    s = WQSession()
    out = s.add_entity("price", "N", value=25)
    assert out["ok"] is False
    assert "unit" in out["error"].lower()


def test_add_entity_n_with_inline_unit_builds_payload():
    s = WQSession()
    out = s.add_entity("price_25", "N", value=25,
                       unit={"id": "pen", "axis": "K", "label": "PEN"})
    assert out["ok"] is True
    ind = s.universe.individuals["price_25"]
    assert ind.axis.value == "N"
    assert ind.payload == {"value": 25, "unit": "pen"}
    assert "pen" in s.universe.individuals  # unit auto-created in K


def test_add_entity_n_with_existing_unit_id():
    s = WQSession()
    s.add_entity("pen", "K", "PEN")
    out = s.add_entity("price_30", "N", value=30, unit="pen")
    assert out["ok"] is True
    assert s.universe.individuals["price_30"].payload["unit"] == "pen"


def test_value_unit_rejected_on_non_n_axis():
    s = WQSession()
    out = s.add_entity("ana", "Q", value=5)
    assert out["ok"] is False
    assert "axis n" in out["error"].lower()


def test_assert_situation_inline_n_without_unit_is_rejected():
    s = WQSession()
    out = s.assert_situation(
        "charge", roles={"por_cuanto": {"id": "p", "axis": "N", "value": 25}})
    assert out["ok"] is False
    assert "unit" in out["error"].lower()


def test_rejected_n_add_entity_creates_no_phantom_unit():
    s = WQSession()
    out = s.add_entity("price", "N", unit={"id": "pen", "axis": "K", "label": "PEN"})
    assert out["ok"] is False
    assert "pen" not in s.universe.individuals  # rejection is atomic — nothing created


def test_rejected_inline_n_creates_no_phantom_unit():
    s = WQSession()
    out = s.assert_situation(
        "charge",
        roles={"por_cuanto": {"id": "p", "axis": "N",
                              "unit": {"id": "usd", "axis": "K", "label": "USD"}}},
    )
    assert out["ok"] is False
    assert "usd" not in s.universe.individuals


def test_correct_appends_fact_to_existing_situation():
    s = WQSession()
    s.add_entity("ana", "Q", "Ana")
    s.add_entity("beto", "Q", "Beto")
    out = s.assert_situation("visit", roles={"agente": "ana"})
    sid = out["situation_id"]
    c = s.correct(sid, "agente", "beto")
    assert c["ok"] is True
    agente = [f for f in s.universe.facts
              if f.subject.id == sid and f.role == "agente"]
    assert {f.value.id for f in agente} == {"ana", "beto"}


def test_correct_unknown_situation_errors():
    s = WQSession()
    out = s.correct("nope", "agente", "ana")
    assert out["ok"] is False
    assert "nope" in out["error"]


def test_correct_on_a_non_situation_still_obeys_the_catalog():
    # `correct` used to refuse any subject outside O. It no longer does: an
    # attribute of a person is as correctable as a role of a situation, and
    # assert_fact made that write expressible. What still rejects this call is
    # the catalog — `agente` is O->Q, so it cannot hang off a Q entity.
    s = WQSession()
    s.add_entity("ana", "Q", "Ana")
    out = s.correct("ana", "agente", "ana")
    assert out["ok"] is False
    assert "eje" in out["error"].lower() or "axis" in out["error"].lower()


def test_ask_returns_latest_value_after_correction():
    s = WQSession()
    s.add_entity("ana", "Q", "Ana")
    s.add_entity("beto", "Q", "Beto")
    s.add_entity("spa", "L", "Spa")
    out = s.assert_situation("visit", roles={"agente": "ana", "lugar_de": "spa"})
    s.correct(out["situation_id"], "agente", "beto")
    res = s.ask(fixed={"lugar_de": "spa"}, ask=["agente"])
    assert res["results"][0]["agente"] == "beto"  # functional role: latest wins


def test_ask_history_returns_full_trail():
    s = WQSession()
    s.add_entity("ana", "Q", "Ana")
    s.add_entity("beto", "Q", "Beto")
    s.add_entity("spa", "L", "Spa")
    out = s.assert_situation("visit", roles={"agente": "ana", "lugar_de": "spa"})
    s.correct(out["situation_id"], "agente", "beto")
    res = s.ask(fixed={"lugar_de": "spa"}, ask=["agente"], history=True)
    assert res["results"][0]["agente"] == ["ana", "beto"]  # tx_time order


def test_ask_nonfunctional_role_returns_all_values():
    s = WQSession()
    s.add_entity("ana", "Q", "Ana")
    out = s.assert_situation("visit", roles={"agente": "ana"})
    # instancia_de is catalog non-functional -> genuinely multi-valued
    s.correct(out["situation_id"], "instancia_de",
              {"id": "special", "axis": "K", "label": "special"})
    res = s.ask(fixed={"agente": "ana"}, ask=["instancia_de"])
    vals = res["results"][0]["instancia_de"]
    assert isinstance(vals, list)
    assert "special" in vals and "action_visit" in vals


def test_barbershop_correction_scenario_end_to_end():
    """The exact friction from the stress test: a mis-recorded exchange rate is
    corrected by re-assertion, priced in unit-bearing N, no auditing vocabulary."""
    s = WQSession()
    s.add_entity("marcos", "Q", "Marcos")
    s.add_entity("pablo", "Q", "Pablo")
    s.add_entity("shave", "O", "Shave service")
    out = s.assert_situation("serve", roles={
        "agente": "marcos", "cliente": "pablo", "tema": "shave",
        "por_cuanto": {"id": "usd_12", "axis": "N", "value": 12,
                       "unit": {"id": "usd", "axis": "K", "label": "USD"}},
    })
    sid = out["situation_id"]

    # exchange rate recorded wrong (3.33) then corrected (3.39) — no status role
    s.correct(sid, "tipo_cambio",
              {"id": "tc_333", "axis": "N", "value": 3.33,
               "unit": {"id": "pen_per_usd", "axis": "K", "label": "PEN/USD"}})
    s.correct(sid, "tipo_cambio",
              {"id": "tc_339", "axis": "N", "value": 3.39, "unit": "pen_per_usd"})

    current = s.ask(fixed={"cliente": "pablo"}, ask=["tipo_cambio"])
    assert current["results"][0]["tipo_cambio"] == "tc_339"  # current wins

    trail = s.ask(fixed={"cliente": "pablo"}, ask=["tipo_cambio"], history=True)
    assert trail["results"][0]["tipo_cambio"] == ["tc_333", "tc_339"]

    # the magnitude kept its unit as structured data, not baked into a label
    assert s.universe.individuals["usd_12"].payload == {"value": 12, "unit": "usd"}


def test_display_uses_label_when_no_name_fact():
    s = WQSession()
    s.add_entity("ana", "Q", "Ana Torres")
    assert s._display("ana") == "Ana Torres"


def test_display_prefers_a_nombre_fact_over_the_label():
    s = WQSession()
    s.add_entity("ana", "Q", "etiqueta vieja")
    s.add_entity("lit_ana", "K", "Ana Torres")
    s.universe.assert_fact(s.universe.individuals["ana"], "nombre",
                           s.universe.individuals["lit_ana"])
    assert s._display("ana") == "Ana Torres"


def test_display_omits_entities_whose_label_is_the_id():
    s = WQSession()
    s.add_entity("pro_783", "O")
    assert s._display("pro_783") is None


def test_display_resolves_a_magnitude_to_value_and_unit():
    s = WQSession()
    s.add_entity("pen", "K", "PEN")
    s.add_entity("n1", "N", value=25.0, unit="pen")
    assert s._display("n1") == {"value": 25.0, "unit": "PEN"}


def test_display_returns_none_for_unknown_entity():
    s = WQSession()
    assert s._display("no_existe") is None


def test_ask_returns_a_labels_dictionary():
    s = WQSession()
    s.add_entity("ana", "Q", "Ana Torres")
    s.add_entity("pen", "K", "PEN")
    s.assert_situation("vender", {
        "agente": "ana",
        "tema": {"id": "libro", "axis": "O", "label": "Libro"},
        "por_cuanto": {"id": "n1", "axis": "N", "value": 20.0, "unit": "pen"}})
    out = s.ask(fixed={"agente": "ana"}, ask=["tema", "por_cuanto"])
    assert out["labels"]["libro"] == "Libro"
    assert out["labels"]["n1"] == {"value": 20.0, "unit": "PEN"}


def test_ask_labels_omit_situation_nodes():
    s = WQSession()
    s.add_entity("ana", "Q", "Ana Torres")
    s.assert_situation("vender", {"agente": "ana",
                                  "tema": {"id": "libro", "axis": "O",
                                           "label": "Libro"}})
    out = s.ask(fixed={"agente": "ana"}, ask=["tema"])
    sid = out["results"][0]["_subject"]
    assert sid not in out["labels"]


def test_ask_labels_name_each_id_once():
    s = WQSession()
    s.add_entity("ana", "Q", "Ana Torres")
    s.add_entity("libro", "O", "Libro")
    for _ in range(5):
        s.assert_situation("vender", {"agente": "ana", "tema": "libro"})
    out = s.ask(fixed={"agente": "ana"}, ask=["tema"])
    assert out["count"] == 5
    assert list(out["labels"]).count("libro") == 1


def test_ask_labels_can_be_switched_off():
    s = WQSession()
    s.add_entity("ana", "Q", "Ana Torres")
    s.assert_situation("vender", {"agente": "ana",
                                  "tema": {"id": "libro", "axis": "O",
                                           "label": "Libro"}})
    out = s.ask(fixed={"agente": "ana"}, ask=["tema"], labels=False)
    assert "labels" not in out


def test_assert_fact_writes_an_attribute_on_a_q_entity():
    s = WQSession()
    s.add_entity("juan", "Q", "juan")
    out = s.assert_fact("juan", "nombre",
                        {"id": "lit_juan", "axis": "K", "label": "Juan Pérez"})
    assert out["ok"] is True
    assert out["fact"] == {"subject": "juan", "role": "nombre",
                           "value": "lit_juan"}
    assert s._display("juan") == "Juan Pérez"


def test_assert_fact_rejects_an_unknown_subject():
    s = WQSession()
    out = s.assert_fact("fantasma", "nombre",
                        {"id": "lit", "axis": "K", "label": "X"})
    assert out["ok"] is False
    assert "fantasma" in out["error"]


def test_assert_fact_enforces_the_catalog_signature():
    s = WQSession()
    s.add_entity("juan", "Q", "Juan")
    s.add_entity("t1", "T", "2026-01-01")
    out = s.assert_fact("juan", "momento", "t1")
    assert out["ok"] is False


def test_correct_accepts_a_non_situation_subject():
    s = WQSession()
    s.add_entity("juan", "Q", "Juan")
    s.assert_fact("juan", "nombre",
                  {"id": "lit_v", "axis": "K", "label": "Juan Viejo"})
    out = s.correct("juan", "nombre",
                    {"id": "lit_n", "axis": "K", "label": "Juan Nuevo"})
    assert out["ok"] is True
    assert s._display("juan") == "Juan Nuevo"


def test_find_matches_a_substring_ignoring_case_and_accents():
    s = WQSession()
    s.add_entity("cli_1", "Q", "ROMERO AZAÑERO, MARCELA")
    out = s.find("azanero")
    assert out["count"] == 1
    assert out["results"][0]["id"] == "cli_1"
    assert out["results"][0]["axis"] == "Q"
    assert out["results"][0]["label"] == "ROMERO AZAÑERO, MARCELA"


def test_find_can_filter_by_axis():
    s = WQSession()
    s.add_entity("cli_1", "Q", "SAUNA PLUS")
    s.add_entity("pro_1", "O", "SAUNA PLUS")
    assert s.find("sauna")["count"] == 2
    out = s.find("sauna", axis="O")
    assert out["count"] == 1
    assert out["results"][0]["id"] == "pro_1"


def test_find_truncates_and_says_so():
    s = WQSession()
    for i in range(30):
        s.add_entity(f"cli_{i}", "Q", f"CLIENTE {i}")
    out = s.find("cliente", limit=10)
    assert len(out["results"]) == 10
    assert out["truncated"] is True
    assert out["count"] == 30


def test_find_sees_entities_added_after_the_first_search():
    s = WQSession()
    s.add_entity("cli_1", "Q", "Ana")
    assert s.find("beto")["count"] == 0
    s.add_entity("cli_2", "Q", "Beto")
    assert s.find("beto")["count"] == 1


def test_find_uses_a_nombre_fact_over_the_label():
    # La entidad `juan` tiene label "juan", que no la haría encontrable. El
    # hecho `nombre` sí. (El literal K también se llama así y también aparece:
    # es correcto, se llama de verdad "Juan Pérez". Por eso se filtra por eje.)
    s = WQSession()
    s.add_entity("juan", "Q", "juan")
    s.assert_fact("juan", "nombre",
                  {"id": "lit_j", "axis": "K", "label": "Juan Pérez"})
    out = s.find("perez", axis="Q")
    assert out["count"] == 1
    assert out["results"][0]["id"] == "juan"


def test_find_rejects_an_empty_query():
    s = WQSession()
    out = s.find("   ")
    assert out["ok"] is False


def test_find_does_not_build_the_index_until_it_is_called():
    s = WQSession()
    s.add_entity("cli_1", "Q", "Ana")
    assert s._name_idx is None
    s.find("ana")
    assert s._name_idx is not None


def test_ask_accepts_a_range_on_momento():
    s = WQSession()
    s.add_entity("ana", "Q", "Ana")
    for dia in ("2025-06-01", "2026-03-15", "2026-11-02"):
        s.add_entity(f"t_{dia}", "T", dia)
        s.assert_situation("vender", {"agente": "ana", "momento": f"t_{dia}"})
    out = s.ask(fixed={"agente": "ana",
                       "momento": {"desde": "2026-01-01", "hasta": "2026-12-31"}},
                ask=["momento"])
    assert out["count"] == 2


def test_ask_range_with_only_one_open_end():
    s = WQSession()
    s.add_entity("pen", "K", "PEN")
    s.add_entity("ana", "Q", "Ana")
    for i, val in enumerate((10.0, 150.0, 900.0)):
        s.assert_situation("vender", {
            "agente": "ana",
            "por_cuanto": {"id": f"n{i}", "axis": "N", "value": val,
                           "unit": "pen"}})
    out = s.ask(fixed={"agente": "ana", "por_cuanto": {"desde": 100}},
                ask=["por_cuanto"])
    assert out["count"] == 2


def test_ask_range_on_an_axis_without_order_is_an_error():
    s = WQSession()
    s.add_entity("ana", "Q", "Ana")
    s.assert_situation("vender", {"agente": "ana"})
    out = s.ask(fixed={"agente": {"desde": "a", "hasta": "z"}}, ask=["agente"])
    assert out["ok"] is False
    assert "ordered" in out["error"].lower()


def _universo_de_ventas():
    s = WQSession()
    s.add_entity("pen", "K", "PEN")
    s.add_entity("ana", "Q", "Ana")
    s.add_entity("sauna", "O", "SAUNA")
    s.add_entity("agua", "O", "AGUA")
    for tema, precio in (("sauna", 25.0), ("sauna", 25.0), ("agua", 2.5)):
        s.assert_situation("vender", {
            "agente": "ana", "tema": tema,
            "por_cuanto": {"id": f"n_{tema}_{precio}", "axis": "N",
                           "value": precio, "unit": "pen"}})
    return s


def test_ask_groups_and_counts():
    s = _universo_de_ventas()
    out = s.ask(type="action_vender", agrupar_por="tema",
                medir={"veces": "count"})
    filas = {r["tema"]: r["veces"] for r in out["results"]}
    assert filas == {"sauna": 2, "agua": 1}
    assert out["labels"]["sauna"] == "SAUNA"


def test_ask_sums_magnitudes_with_their_unit():
    s = _universo_de_ventas()
    out = s.ask(type="action_vender", agrupar_por="tema",
                medir={"importe": {"sum": "por_cuanto"}})
    filas = {r["tema"]: r["importe"] for r in out["results"]}
    assert filas["sauna"] == {"value": 50.0, "unit": "PEN"}


def test_ask_orders_and_limits_groups():
    s = _universo_de_ventas()
    out = s.ask(type="action_vender", agrupar_por="tema",
                medir={"veces": "count"}, orden="-veces", limite=1)
    assert [r["tema"] for r in out["results"]] == ["sauna"]


def test_ask_refuses_to_sum_incommensurable_units():
    s = _universo_de_ventas()
    s.add_entity("kg", "K", "KG")
    s.assert_situation("vender", {
        "agente": "ana", "tema": "sauna",
        "por_cuanto": {"id": "n_kg", "axis": "N", "value": 3.0, "unit": "kg"}})
    out = s.ask(type="action_vender", agrupar_por="tema",
                medir={"importe": {"sum": "por_cuanto"}})
    assert out["ok"] is False
    assert "conmensurable" in out["error"].lower() or "unit" in out["error"].lower()


def test_ask_without_agrupar_por_gives_a_grand_total():
    s = _universo_de_ventas()
    out = s.ask(type="action_vender", medir={"veces": "count"})
    assert out["results"] == [{"veces": 3}]


def test_ask_refuses_project_and_aggregate_at_once():
    s = _universo_de_ventas()
    out = s.ask(type="action_vender", ask=["tema"], medir={"veces": "count"})
    assert out["ok"] is False


def test_fixed_no_longer_matches_a_corrected_away_value():
    s = WQSession()
    s.add_entity("ana", "Q", "Ana")
    s.add_entity("beto", "Q", "Beto")
    s.add_entity("libro", "O", "Libro")
    r = s.assert_situation("vender", {"beneficiario": "ana", "tema": "libro"})
    s.correct(r["situation_id"], "beneficiario", "beto")
    assert s.ask(fixed={"beneficiario": "beto"}, ask=["tema"])["count"] == 1
    assert s.ask(fixed={"beneficiario": "ana"}, ask=["tema"])["count"] == 0


def test_history_true_reopens_the_past_on_both_halves():
    s = WQSession()
    s.add_entity("ana", "Q", "Ana")
    s.add_entity("beto", "Q", "Beto")
    s.add_entity("libro", "O", "Libro")
    r = s.assert_situation("vender", {"beneficiario": "ana", "tema": "libro"})
    s.correct(r["situation_id"], "beneficiario", "beto")
    out = s.ask(fixed={"beneficiario": "ana"}, ask=["beneficiario"], history=True)
    assert out["count"] == 1
    assert out["results"][0]["beneficiario"] == ["ana", "beto"]


def test_fixed_accepts_a_list_of_ids():
    s = WQSession()
    s.add_entity("libro", "O", "Libro")
    for q in ("ana", "beto", "caro"):
        s.add_entity(q, "Q", q.title())
        s.assert_situation("vender", {"beneficiario": q, "tema": "libro"})
    out = s.ask(fixed={"beneficiario": ["ana", "caro"]}, medir={"n": "count"})
    assert out["results"][0]["n"] == 2


def test_identidades_follows_mismo_que_both_ways():
    s = WQSession()
    for q in ("dni", "ruc", "carnet"):
        s.add_entity(q, "Q", q.upper())
    s.assert_fact("ruc", "mismo_que", "dni")
    s.assert_fact("carnet", "mismo_que", "ruc")
    out = s.identidades("dni")
    assert out["ids"] == ["carnet", "dni", "ruc"]


def test_identidades_of_an_unlinked_entity_is_just_itself():
    s = WQSession()
    s.add_entity("ana", "Q", "Ana")
    assert s.identidades("ana")["ids"] == ["ana"]


def test_identidades_plus_fixed_list_totals_the_person():
    s = WQSession()
    s.add_entity("pen", "K", "PEN")
    s.add_entity("libro", "O", "Libro")
    for q, precio in (("dni", 10.0), ("ruc", 5.0)):
        s.add_entity(q, "Q", q.upper())
        s.assert_situation("vender", {
            "beneficiario": q, "tema": "libro",
            "por_cuanto": {"id": f"n_{q}", "axis": "N", "value": precio,
                           "unit": "pen"}})
    s.assert_fact("ruc", "mismo_que", "dni")
    ids = s.identidades("dni")["ids"]
    out = s.ask(fixed={"beneficiario": ids},
                medir={"n": "count", "t": {"sum": "por_cuanto"}})
    assert out["results"][0]["n"] == 2
    assert out["results"][0]["t"] == {"value": 15.0, "unit": "PEN"}
