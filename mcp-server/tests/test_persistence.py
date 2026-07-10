import os
from wquestions_mcp.session import resolve_log_path, DEFAULT_LOG_PATH


def test_resolve_unset_uses_expanded_default():
    assert resolve_log_path(None) == os.path.expanduser(DEFAULT_LOG_PATH)


def test_resolve_off_sentinels_disable():
    for raw in ["off", "OFF", "none", ":memory:", "", "  "]:
        assert resolve_log_path(raw) is None


def test_resolve_explicit_path_is_expanded():
    assert resolve_log_path("/tmp/u.jsonl") == "/tmp/u.jsonl"
    assert resolve_log_path("~/x.jsonl") == os.path.expanduser("~/x.jsonl")
