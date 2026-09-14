from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

import pytest


ROOT = Path(__file__).resolve().parents[5]
HARNESS = ROOT / (
    ".github/governance/evidence/"
    "g77_256lt_session_independent_one_shot_supervision_v1/harness/"
    "G77_256LT_SESSION_INDEPENDENT_ONE_SHOT_SUPERVISOR_V1.py"
)
SPEC = importlib.util.spec_from_file_location("g77_256lt_supervisor", HARNESS)
assert SPEC is not None and SPEC.loader is not None
LT = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = LT
SPEC.loader.exec_module(LT)


def make_binding(
    tmp_path: Path,
    *,
    argv: list[str] | None = None,
    invocation: str = "SYNTHETIC_INVOCATION_001",
    filename: str = "binding.json",
) -> Path:
    if argv is None:
        argv = [sys.executable, "-c", "raise SystemExit(0)"]
    envelope = LT.build_binding(
        lifecycle_id="G77_256LT_SYNTHETIC_LIFECYCLE_001",
        invocation_id=invocation,
        invocation_binding_identity=f"BINDING::{invocation}",
        fm_input_identity=f"SYNTHETIC_FM_INPUT::{invocation}",
        admission_identity=f"SYNTHETIC_ADMISSION::{invocation}",
        authority_binding_sha256="a" * 64,
        execution_class="SYNTHETIC_NON_OPERATIONAL_TEST",
        working_directory=tmp_path,
        argv=argv,
    )
    path = tmp_path / filename
    LT.write_binding_once(path, envelope)
    return path


def state_names(state_dir: Path) -> list[str]:
    return [item["event"]["state"] for item in LT.read_journal(state_dir)]


def wait_terminal(state_dir: Path, timeout: float = 8.0) -> dict:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            latest = LT.latest_state(state_dir)
        except LT.SupervisionError:
            time.sleep(0.02)
            continue
        if latest["event"]["state"] in LT.TERMINAL_STATES:
            return latest
        time.sleep(0.02)
    raise AssertionError(f"terminal state not observed: {state_names(state_dir)}")


def reserve_and_supervise(tmp_path: Path, binding: Path) -> tuple[Path, int]:
    state_dir = tmp_path / "state"
    reservation = LT.reserve_once(state_dir, binding)
    status = LT.supervise(
        state_dir,
        binding,
        reservation["event"]["binding_file_sha256"],
    )
    return state_dir, status


def test_case_a_normal_child_completion(tmp_path: Path) -> None:
    state_dir, status = reserve_and_supervise(tmp_path, make_binding(tmp_path))
    assert status == 0
    assert state_names(state_dir) == [
        "NOT_STARTED", "STARTED", "RUNNING", "TERMINATED_WITH_STATUS"
    ]
    terminal = LT.latest_state(state_dir)["event"]
    assert terminal["details"]["process_exit_status"] == 0
    assert terminal["details"]["relaunch_permitted"] is False


def test_case_b_caller_signal_does_not_end_detached_supervisor(tmp_path: Path) -> None:
    marker = tmp_path / "child-complete"
    binding = make_binding(
        tmp_path,
        argv=[
            sys.executable,
            "-c",
            (
                "import pathlib,time; time.sleep(.35); "
                f"pathlib.Path({str(marker)!r}).write_text('done')"
            ),
        ],
    )
    state_dir = tmp_path / "state"
    caller_code = (
        "import importlib.util,pathlib,sys,time;"
        f"p=pathlib.Path({str(HARNESS)!r});"
        "s=importlib.util.spec_from_file_location('lt_child_launcher',p);"
        "m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m);"
        f"m.launch_detached(pathlib.Path({str(state_dir)!r}),pathlib.Path({str(binding)!r}));"
        "time.sleep(30)"
    )
    caller = subprocess.Popen(
        [sys.executable, "-c", caller_code],
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        if state_dir.exists():
            try:
                if LT.latest_state(state_dir)["event"]["state"] in {"STARTED", "RUNNING"}:
                    break
            except LT.SupervisionError:
                pass
        time.sleep(0.02)
    else:
        caller.kill()
        raise AssertionError("detached supervisor did not start")
    caller.send_signal(signal.SIGTERM)
    caller.wait(timeout=3)
    terminal = wait_terminal(state_dir)
    assert terminal["event"]["state"] == "TERMINATED_WITH_STATUS"
    assert terminal["event"]["details"]["process_exit_status"] == 0
    assert marker.read_text() == "done"


def test_case_c_nonzero_is_terminal_and_never_retried(tmp_path: Path) -> None:
    binding = make_binding(
        tmp_path, argv=[sys.executable, "-c", "raise SystemExit(23)"]
    )
    state_dir, status = reserve_and_supervise(tmp_path, binding)
    terminal = LT.latest_state(state_dir)["event"]
    assert status == 23
    assert terminal["state"] == "TERMINATED_WITH_STATUS"
    assert terminal["details"]["process_exit_status"] == 23
    assert terminal["retry_count"] == 0
    assert terminal["details"]["launch_attempt_count"] == 1


def test_case_d_externally_terminated_child_has_observed_signal(tmp_path: Path) -> None:
    binding = make_binding(
        tmp_path, argv=[sys.executable, "-c", "import time; time.sleep(30)"]
    )
    state_dir = tmp_path / "state"
    reservation = LT.reserve_once(state_dir, binding)

    def terminate(child: subprocess.Popen) -> None:
        child.send_signal(signal.SIGTERM)

    status = LT.supervise(
        state_dir,
        binding,
        reservation["event"]["binding_file_sha256"],
        after_child_start=terminate,
    )
    terminal = LT.latest_state(state_dir)["event"]
    assert status == -signal.SIGTERM
    assert terminal["state"] == "TERMINATED_WITH_STATUS"
    assert terminal["details"]["termination_signal"] == signal.SIGTERM


def test_case_e_lost_observation_becomes_unknown_without_relaunch(tmp_path: Path) -> None:
    binding = make_binding(
        tmp_path, argv=[sys.executable, "-c", "import time; time.sleep(.15)"]
    )
    state_dir = tmp_path / "state"
    reservation = LT.reserve_once(state_dir, binding)

    def lose_observation(_child: subprocess.Popen) -> None:
        raise RuntimeError("synthetic observer loss")

    with pytest.raises(LT.SupervisionError, match="OBSERVATION_LOST"):
        LT.supervise(
            state_dir,
            binding,
            reservation["event"]["binding_file_sha256"],
            after_child_start=lose_observation,
        )
    assert state_names(state_dir) == [
        "NOT_STARTED", "STARTED", "RUNNING", "INTERRUPTED_OR_LOST__UNKNOWN"
    ]
    assert LT.latest_state(state_dir)["event"]["details"]["relaunch_permitted"] is False


def test_case_f_duplicate_invocation_request_fails_closed(tmp_path: Path) -> None:
    binding = make_binding(tmp_path)
    state_dir = tmp_path / "state"
    LT.reserve_once(state_dir, binding)
    with pytest.raises(LT.SupervisionError, match="NO_RELAUNCH"):
        LT.reserve_once(state_dir, binding)
    assert state_names(state_dir) == ["NOT_STARTED"]


def test_case_g_concurrent_duplicate_reservation_has_one_winner(tmp_path: Path) -> None:
    binding = make_binding(tmp_path)
    state_dir = tmp_path / "state"

    def attempt() -> str:
        try:
            LT.reserve_once(state_dir, binding)
            return "WON"
        except LT.SupervisionError:
            return "REJECTED"

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = sorted(pool.map(lambda _: attempt(), range(2)))
    assert outcomes == ["REJECTED", "WON"]
    assert state_names(state_dir) == ["NOT_STARTED"]


def test_case_g_duplicate_supervisor_start_rejected(tmp_path: Path) -> None:
    binding = make_binding(tmp_path)
    state_dir, _ = reserve_and_supervise(tmp_path, binding)
    with pytest.raises(LT.SupervisionError, match="NO_RELAUNCH"):
        LT.supervise(state_dir, binding, hashlib.sha256(binding.read_bytes()).hexdigest())
    assert state_names(state_dir).count("STARTED") == 1


def test_case_g_concurrent_duplicate_supervisors_launch_one_child(tmp_path: Path) -> None:
    counter = tmp_path / "counter"
    binding = make_binding(
        tmp_path,
        argv=[
            sys.executable,
            "-c",
            f"import pathlib,time; pathlib.Path({str(counter)!r}).write_text('one'); time.sleep(.1)",
        ],
    )
    state_dir = tmp_path / "state"
    reservation = LT.reserve_once(state_dir, binding)
    command = [
        sys.executable,
        str(HARNESS),
        "_supervise",
        "--state-dir",
        str(state_dir),
        "--binding",
        str(binding),
        "--expected-binding-file-sha256",
        reservation["event"]["binding_file_sha256"],
    ]
    first = subprocess.Popen(command, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    second = subprocess.Popen(command, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    statuses = sorted((first.wait(timeout=5), second.wait(timeout=5)))
    assert statuses == [0, 126]
    assert counter.read_text() == "one"
    assert state_names(state_dir) == [
        "NOT_STARTED", "STARTED", "RUNNING", "TERMINATED_WITH_STATUS"
    ]


def test_case_h_stale_or_mismatched_binding_rejected(tmp_path: Path) -> None:
    binding = make_binding(tmp_path, invocation="ONE", filename="one.json")
    stale = make_binding(tmp_path, invocation="TWO", filename="two.json")
    state_dir = tmp_path / "state"
    reservation = LT.reserve_once(state_dir, binding)
    with pytest.raises(LT.SupervisionError, match="STALE_OR_MISMATCHED"):
        LT.supervise(
            state_dir,
            stale,
            reservation["event"]["binding_file_sha256"],
        )
    assert state_names(state_dir) == ["NOT_STARTED"]


def test_case_i_post_like_claim_cannot_enter_binding_or_journal(tmp_path: Path) -> None:
    binding = make_binding(tmp_path)
    value = json.loads(binding.read_text())
    value["binding"]["claimed_terminal_evidence"] = {"FM_POST": "PASS"}
    value["binding_sha256"] = LT.sha256_bytes(LT.canonical_bytes(value["binding"]))
    malformed = tmp_path / "post-claim.json"
    malformed.write_bytes(LT.canonical_bytes(value))
    with pytest.raises(LT.SupervisionError, match="FIELD_SET"):
        LT.load_binding(malformed)

    state_dir, _ = reserve_and_supervise(tmp_path, binding)
    journal_text = "".join(path.read_text() for path in state_dir.glob("*.json"))
    assert "FM_POST" not in journal_text
    assert "HOST_SUPERVISION_ONLY__NOT_FM_PRE_OR_POST" in journal_text


def test_case_j_completed_and_unknown_states_cannot_restart(tmp_path: Path) -> None:
    completed_binding = make_binding(tmp_path, invocation="COMPLETE", filename="complete.json")
    completed_state, _ = reserve_and_supervise(tmp_path, completed_binding)
    with pytest.raises(LT.SupervisionError):
        LT.reserve_once(completed_state, completed_binding)

    unknown_binding = make_binding(tmp_path, invocation="UNKNOWN", filename="unknown.json")
    unknown_state = tmp_path / "unknown-state"
    LT.reserve_once(unknown_state, unknown_binding)
    unknown = LT.reconcile_without_relaunch(unknown_state, unknown_binding)
    assert unknown["event"]["state"] == "INTERRUPTED_OR_LOST__UNKNOWN"
    with pytest.raises(LT.SupervisionError):
        LT.reserve_once(unknown_state, unknown_binding)


def test_state_flush_before_child_start_spends_right_and_fails_unknown(tmp_path: Path) -> None:
    binding = make_binding(tmp_path)
    state_dir = tmp_path / "state"
    reservation = LT.reserve_once(state_dir, binding)

    def crash_after_started_flush() -> None:
        raise RuntimeError("synthetic crash after STARTED flush")

    with pytest.raises(LT.SupervisionError):
        LT.supervise(
            state_dir,
            binding,
            reservation["event"]["binding_file_sha256"],
            before_child_start=crash_after_started_flush,
        )
    assert state_names(state_dir) == [
        "NOT_STARTED", "STARTED", "INTERRUPTED_OR_LOST__UNKNOWN"
    ]


def test_started_state_write_failure_does_not_launch_child(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    binding = make_binding(tmp_path)
    state_dir = tmp_path / "state"
    reservation = LT.reserve_once(state_dir, binding)
    real_append = LT.append_event
    popen_count = 0

    def broken_append(*args, **kwargs):
        if kwargs.get("state") == "STARTED":
            raise OSError("synthetic durable write failure")
        return real_append(*args, **kwargs)

    def counted_popen(*args, **kwargs):
        nonlocal popen_count
        popen_count += 1
        return subprocess.Popen(*args, **kwargs)

    monkeypatch.setattr(LT, "append_event", broken_append)
    with pytest.raises(LT.SupervisionError):
        LT.supervise(
            state_dir,
            binding,
            reservation["event"]["binding_file_sha256"],
            popen_factory=counted_popen,
        )
    assert popen_count == 0
    assert state_names(state_dir) == ["NOT_STARTED"]


def test_malformed_state_and_process_identity_reuse_fail_closed(tmp_path: Path) -> None:
    binding = make_binding(tmp_path)
    malformed_state = tmp_path / "malformed-state"
    malformed_state.mkdir()
    (malformed_state / "00_NOT_STARTED.json").write_text("{}\n")
    with pytest.raises(LT.SupervisionError, match="SEAL_OR_CHAIN"):
        LT.reconcile_without_relaunch(malformed_state, binding)

    state_dir = tmp_path / "state"
    reservation = LT.reserve_once(state_dir, binding)
    loaded, binding_sha256, binding_file_sha256 = LT.load_binding(binding)
    stale_identity = LT.process_identity(os.getpid(), loaded["argv_sha256"])
    stale_identity["proc_start_ticks"] += 1
    LT.append_event(
        state_dir,
        state="STARTED",
        binding=loaded,
        binding_sha256=binding_sha256,
        binding_file_sha256=binding_file_sha256,
        previous_event_sha256=reservation["event_sha256"],
        details={
            "launch_attempt_count": 1,
            "child_start_attempted": True,
            "supervisor_identity": stale_identity,
            "relaunch_permitted": False,
        },
    )
    unknown = LT.reconcile_without_relaunch(state_dir, binding)
    assert unknown["event"]["details"]["process_identity_reuse_treated_as_unknown"] is True
    assert unknown["event"]["state"] == "INTERRUPTED_OR_LOST__UNKNOWN"


def test_synthetic_binding_rejects_qemu_and_all_events_are_nonauthority(tmp_path: Path) -> None:
    qemu_binding = make_binding(
        tmp_path,
        argv=["qemu-system-x86_64", "-version"],
        filename="qemu.json",
    )
    with pytest.raises(LT.SupervisionError, match="OPERATIONAL_ROUTE_FORBIDDEN"):
        LT.load_binding(qemu_binding)

    binding = make_binding(tmp_path, filename="safe.json")
    state_dir, _ = reserve_and_supervise(tmp_path, binding)
    for envelope in LT.read_journal(state_dir):
        event = envelope["event"]
        assert event["authority_effect"] == "NONE"
        assert event["consumability"] == "NONAUTHORITY"
        assert event["retry_count"] == 0
        assert event["evidence_semantics"] == "HOST_SUPERVISION_ONLY__NOT_FM_PRE_OR_POST"
