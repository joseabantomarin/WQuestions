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


def test_correct_rejects_non_situation_subject():
    s = WQSession()
    s.add_entity("ana", "Q", "Ana")
    out = s.correct("ana", "agente", "ana")  # ana is Q, not a situation (O)
    assert out["ok"] is False
    assert "situation" in out["error"].lower()


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
