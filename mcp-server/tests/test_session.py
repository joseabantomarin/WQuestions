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
