from pathlib import Path

from sapianta_bridge.provider_connectors.bounded_runtime_state import (
    bounded_runtime_state_env,
    create_bounded_runtime_state,
    runtime_state_path_for,
    validate_bounded_runtime_state,
    validate_bounded_runtime_state_env,
)


def test_runtime_state_path_is_deterministic_and_inside_root(tmp_path):
    first = create_bounded_runtime_state(
        provider_id="codex_cli",
        invocation_id="INV-1",
        replay_identity="REPLAY-1",
        runtime_state_root=tmp_path,
    ).to_dict()
    second = create_bounded_runtime_state(
        provider_id="codex_cli",
        invocation_id="INV-1",
        replay_identity="REPLAY-1",
        runtime_state_root=tmp_path,
    ).to_dict()

    assert first == second
    assert Path(first["runtime_state_dir"]).is_relative_to(tmp_path)
    assert first["home_directory_mutation_allowed"] is False
    assert validate_bounded_runtime_state(first)["valid"] is True


def test_runtime_state_rejects_parent_traversal(tmp_path):
    state = create_bounded_runtime_state(
        provider_id="codex_cli",
        invocation_id="INV-1",
        replay_identity="REPLAY-1",
        runtime_state_root=tmp_path,
    ).to_dict()
    state["runtime_state_dir"] = str(tmp_path / ".." / "escape")

    validation = validate_bounded_runtime_state(state)

    assert validation["valid"] is False
    assert any(error["field"] == "runtime_state_dir" for error in validation["errors"])


def test_runtime_state_rejects_non_deterministic_path(tmp_path):
    state = create_bounded_runtime_state(
        provider_id="codex_cli",
        invocation_id="INV-1",
        replay_identity="REPLAY-1",
        runtime_state_root=tmp_path,
    ).to_dict()
    state["runtime_state_dir"] = str(tmp_path / "OTHER-SESSION")

    validation = validate_bounded_runtime_state(state)

    assert validation["valid"] is False
    assert any("deterministic" in error["reason"] for error in validation["errors"])


def test_runtime_state_env_is_bounded_to_state_dir(tmp_path):
    state = create_bounded_runtime_state(
        provider_id="codex_cli",
        invocation_id="INV-1",
        replay_identity="REPLAY-1",
        runtime_state_root=tmp_path,
    ).to_dict()
    env = bounded_runtime_state_env(state)

    assert set(env) == {"HOME", "XDG_CACHE_HOME", "XDG_CONFIG_HOME", "TMPDIR"}
    assert all(Path(path).is_relative_to(Path(state["runtime_state_dir"])) for path in env.values())
    assert validate_bounded_runtime_state_env(env, state)["valid"] is True


def test_runtime_state_env_rejects_extra_key(tmp_path):
    state = create_bounded_runtime_state(
        provider_id="codex_cli",
        invocation_id="INV-1",
        replay_identity="REPLAY-1",
        runtime_state_root=tmp_path,
    ).to_dict()
    env = bounded_runtime_state_env(state)
    env["PATH"] = "/usr/bin"

    validation = validate_bounded_runtime_state_env(env, state)

    assert validation["valid"] is False
    assert any(error["field"] == "runtime_state_env" for error in validation["errors"])
