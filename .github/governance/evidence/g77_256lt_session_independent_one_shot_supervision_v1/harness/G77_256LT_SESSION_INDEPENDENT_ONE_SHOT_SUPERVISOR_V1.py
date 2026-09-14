#!/usr/bin/env python3
"""Generation-local, fail-closed supervision for one exact future FM binding.

This harness is not an authority or receipt owner.  Its append-only journal
only records host process supervision.  A claimed launch slot is never
reopened, including after UNKNOWN, malformed state, or supervisor restart.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import stat
import subprocess
import sys
import time
from typing import Any


sys.dont_write_bytecode = True

CAPABILITY_ID = (
    "SESSION_INDEPENDENT_ONE_SHOT_FM_PROCESS_SUPERVISION_AND_"
    "DURABLE_TERMINAL_HANDOFF_V1"
)
BINDING_SCHEMA = "G77_256LT_ONE_SHOT_INVOCATION_BINDING_ENVELOPE_V1"
BINDING_INNER_SCHEMA = "G77_256LT_ONE_SHOT_INVOCATION_BINDING_V1"
EVENT_SCHEMA = "G77_256LT_SUPERVISION_EVENT_ENVELOPE_V1"
EXECUTION_CLASSES = {
    "SYNTHETIC_NON_OPERATIONAL_TEST",
    "FUTURE_SEPARATELY_AUTHORIZED_FM_INVOCATION",
}
STATES = (
    "NOT_STARTED",
    "STARTED",
    "RUNNING",
    "TERMINATED_WITH_STATUS",
    "INTERRUPTED_OR_LOST__UNKNOWN",
)
TERMINAL_STATES = {"TERMINATED_WITH_STATUS", "INTERRUPTED_OR_LOST__UNKNOWN"}
EVENT_NAMES = {
    "NOT_STARTED": "00_NOT_STARTED.json",
    "STARTED": "01_STARTED.json",
    "RUNNING": "02_RUNNING.json",
    "TERMINATED_WITH_STATUS": "03_TERMINATED_WITH_STATUS.json",
    "INTERRUPTED_OR_LOST__UNKNOWN": "03_INTERRUPTED_OR_LOST__UNKNOWN.json",
}
EXPECTED_BINDING_FIELDS = {
    "schema_id",
    "capability_id",
    "lifecycle_id",
    "invocation_id",
    "invocation_binding_identity",
    "fm_input_identity",
    "admission_identity",
    "authority_binding_sha256",
    "execution_class",
    "working_directory",
    "argv",
    "argv_sha256",
    "attempt_limit",
    "retry_limit",
    "authority_effect",
    "receipt_semantics",
}


class SupervisionError(RuntimeError):
    """Fail-closed harness rejection."""


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def _is_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _regular_file_bytes(path: Path) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise SupervisionError(f"UNSAFE_OR_MISSING_FILE:{path}")
    mode = path.stat().st_mode
    if not stat.S_ISREG(mode):
        raise SupervisionError(f"NOT_REGULAR_FILE:{path}")
    return path.read_bytes()


def load_binding(path: Path) -> tuple[dict[str, Any], str, str]:
    raw = _regular_file_bytes(path)
    try:
        envelope = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SupervisionError("MALFORMED_INVOCATION_BINDING") from exc
    if not isinstance(envelope, dict) or raw != canonical_bytes(envelope):
        raise SupervisionError("NONCANONICAL_INVOCATION_BINDING")
    binding = envelope.get("binding")
    if (
        envelope.get("schema_id") != BINDING_SCHEMA
        or not isinstance(binding, dict)
        or envelope.get("binding_sha256") != sha256_bytes(canonical_bytes(binding))
    ):
        raise SupervisionError("INVOCATION_BINDING_SEAL_MISMATCH")
    if set(binding) != EXPECTED_BINDING_FIELDS:
        raise SupervisionError("INVOCATION_BINDING_FIELD_SET_MISMATCH")
    argv = binding.get("argv")
    working_directory = binding.get("working_directory")
    text_fields = (
        "lifecycle_id",
        "invocation_id",
        "invocation_binding_identity",
        "fm_input_identity",
        "admission_identity",
    )
    if (
        binding.get("schema_id") != BINDING_INNER_SCHEMA
        or binding.get("capability_id") != CAPABILITY_ID
        or any(not isinstance(binding.get(field), str) or not binding[field] for field in text_fields)
        or not _is_sha256(binding.get("authority_binding_sha256"))
        or binding.get("execution_class") not in EXECUTION_CLASSES
        or not isinstance(working_directory, str)
        or not Path(working_directory).is_absolute()
        or not isinstance(argv, list)
        or not argv
        or any(not isinstance(item, str) or not item for item in argv)
        or binding.get("argv_sha256") != sha256_bytes(canonical_bytes(argv))
        or binding.get("attempt_limit") != 1
        or binding.get("retry_limit") != 0
        or binding.get("authority_effect") != "NONE"
        or binding.get("receipt_semantics") != "NONAUTHORITY_SUPERVISION_ONLY__NO_SYNTHETIC_POST"
    ):
        raise SupervisionError("INVOCATION_BINDING_CONTRACT_MISMATCH")
    if binding["execution_class"] == "SYNTHETIC_NON_OPERATIONAL_TEST" and any(
        "qemu" in item.lower() or "one_shot_qemu_launcher" in item.lower()
        for item in argv
    ):
        raise SupervisionError("OPERATIONAL_ROUTE_FORBIDDEN_IN_SYNTHETIC_BINDING")
    return binding, envelope["binding_sha256"], sha256_bytes(raw)


def build_binding(
    *,
    lifecycle_id: str,
    invocation_id: str,
    invocation_binding_identity: str,
    fm_input_identity: str,
    admission_identity: str,
    authority_binding_sha256: str,
    execution_class: str,
    working_directory: Path,
    argv: list[str],
) -> dict[str, Any]:
    """Build a sealed fixture/future binding; this creates no authority."""
    binding = {
        "schema_id": BINDING_INNER_SCHEMA,
        "capability_id": CAPABILITY_ID,
        "lifecycle_id": lifecycle_id,
        "invocation_id": invocation_id,
        "invocation_binding_identity": invocation_binding_identity,
        "fm_input_identity": fm_input_identity,
        "admission_identity": admission_identity,
        "authority_binding_sha256": authority_binding_sha256,
        "execution_class": execution_class,
        "working_directory": str(working_directory.resolve()),
        "argv": argv,
        "argv_sha256": sha256_bytes(canonical_bytes(argv)),
        "attempt_limit": 1,
        "retry_limit": 0,
        "authority_effect": "NONE",
        "receipt_semantics": "NONAUTHORITY_SUPERVISION_ONLY__NO_SYNTHETIC_POST",
    }
    return {
        "schema_id": BINDING_SCHEMA,
        "binding": binding,
        "binding_sha256": sha256_bytes(canonical_bytes(binding)),
    }


def write_binding_once(path: Path, envelope: dict[str, Any]) -> None:
    _write_exclusive(path, canonical_bytes(envelope), mode=0o600)


def _fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _write_exclusive(path: Path, payload: bytes, *, mode: int = 0o600) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags, mode)
    except FileExistsError as exc:
        raise SupervisionError(f"ONE_SHOT_ARTIFACT_COLLISION:{path.name}") from exc
    completed = False
    try:
        view = memoryview(payload)
        while view:
            written = os.write(descriptor, view)
            if written <= 0:
                raise OSError("short durable write")
            view = view[written:]
        os.fsync(descriptor)
        completed = True
    finally:
        os.close(descriptor)
    if completed:
        _fsync_directory(path.parent)


def _boot_id() -> str:
    path = Path("/proc/sys/kernel/random/boot_id")
    value = _regular_file_bytes(path).decode("ascii").strip()
    if not value:
        raise SupervisionError("BOOT_ID_UNAVAILABLE")
    return value


def process_identity(pid: int, argv_sha256: str) -> dict[str, Any]:
    try:
        stat_text = Path(f"/proc/{pid}/stat").read_text(encoding="utf-8")
        cmdline = Path(f"/proc/{pid}/cmdline").read_bytes()
        close = stat_text.rfind(")")
        tail = stat_text[close + 2 :].split()
        start_ticks = int(tail[19])
    except (OSError, ValueError, IndexError) as exc:
        raise SupervisionError(f"PROCESS_IDENTITY_UNAVAILABLE:{pid}") from exc
    return {
        "pid": pid,
        "boot_id": _boot_id(),
        "proc_start_ticks": start_ticks,
        "proc_cmdline_sha256": sha256_bytes(cmdline),
        "argv_sha256": argv_sha256,
    }


def process_identity_is_live(identity: object) -> bool:
    if not isinstance(identity, dict):
        return False
    try:
        observed = process_identity(int(identity["pid"]), str(identity["argv_sha256"]))
    except (KeyError, TypeError, ValueError, SupervisionError):
        return False
    return observed == identity


def _event_payload(
    *,
    state: str,
    binding: dict[str, Any],
    binding_sha256: str,
    binding_file_sha256: str,
    previous_event_sha256: str | None,
    details: dict[str, Any],
) -> dict[str, Any]:
    if state not in STATES:
        raise SupervisionError("UNKNOWN_SUPERVISION_STATE")
    return {
        "schema_id": "G77_256LT_SUPERVISION_EVENT_V1",
        "capability_id": CAPABILITY_ID,
        "state": state,
        "lifecycle_id": binding["lifecycle_id"],
        "invocation_id": binding["invocation_id"],
        "invocation_binding_identity": binding["invocation_binding_identity"],
        "binding_sha256": binding_sha256,
        "binding_file_sha256": binding_file_sha256,
        "wall_time_unix_ns": time.time_ns(),
        "monotonic_ns": time.monotonic_ns(),
        "previous_event_sha256": previous_event_sha256,
        "attempt_limit": 1,
        "retry_count": 0,
        "authority_effect": "NONE",
        "consumability": "NONAUTHORITY",
        "evidence_semantics": "HOST_SUPERVISION_ONLY__NOT_FM_PRE_OR_POST",
        "details": details,
    }


def append_event(
    state_dir: Path,
    *,
    state: str,
    binding: dict[str, Any],
    binding_sha256: str,
    binding_file_sha256: str,
    previous_event_sha256: str | None,
    details: dict[str, Any],
) -> dict[str, Any]:
    event = _event_payload(
        state=state,
        binding=binding,
        binding_sha256=binding_sha256,
        binding_file_sha256=binding_file_sha256,
        previous_event_sha256=previous_event_sha256,
        details=details,
    )
    envelope = {
        "schema_id": EVENT_SCHEMA,
        "event": event,
        "event_sha256": sha256_bytes(canonical_bytes(event)),
    }
    _write_exclusive(state_dir / EVENT_NAMES[state], canonical_bytes(envelope))
    return envelope


def read_journal(state_dir: Path) -> list[dict[str, Any]]:
    if state_dir.is_symlink() or not state_dir.is_dir():
        raise SupervisionError("MISSING_OR_UNSAFE_STATE_DIRECTORY")
    paths = sorted(state_dir.glob("*.json"))
    expected_names = set(EVENT_NAMES.values())
    if not paths or any(path.name not in expected_names for path in paths):
        raise SupervisionError("MALFORMED_DURABLE_STATE_NAMESPACE")
    events: list[dict[str, Any]] = []
    previous: str | None = None
    identities: tuple[object, ...] | None = None
    for path in paths:
        raw = _regular_file_bytes(path)
        try:
            envelope = json.loads(raw)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise SupervisionError("MALFORMED_DURABLE_STATE") from exc
        event = envelope.get("event") if isinstance(envelope, dict) else None
        if (
            raw != canonical_bytes(envelope)
            or envelope.get("schema_id") != EVENT_SCHEMA
            or not isinstance(event, dict)
            or envelope.get("event_sha256") != sha256_bytes(canonical_bytes(event))
            or event.get("state") not in STATES
            or path.name != EVENT_NAMES[event["state"]]
            or event.get("previous_event_sha256") != previous
            or event.get("capability_id") != CAPABILITY_ID
            or event.get("attempt_limit") != 1
            or event.get("retry_count") != 0
            or event.get("authority_effect") != "NONE"
            or event.get("consumability") != "NONAUTHORITY"
            or event.get("evidence_semantics") != "HOST_SUPERVISION_ONLY__NOT_FM_PRE_OR_POST"
        ):
            raise SupervisionError("DURABLE_STATE_SEAL_OR_CHAIN_MISMATCH")
        current_identities = (
            event.get("lifecycle_id"),
            event.get("invocation_id"),
            event.get("invocation_binding_identity"),
            event.get("binding_sha256"),
            event.get("binding_file_sha256"),
        )
        if identities is None:
            identities = current_identities
        elif identities != current_identities:
            raise SupervisionError("DURABLE_STATE_BINDING_DRIFT")
        previous = envelope["event_sha256"]
        events.append(envelope)
    sequence = [envelope["event"]["state"] for envelope in events]
    valid = (
        ["NOT_STARTED"],
        ["NOT_STARTED", "STARTED"],
        ["NOT_STARTED", "STARTED", "RUNNING"],
        ["NOT_STARTED", "STARTED", "TERMINATED_WITH_STATUS"],
        ["NOT_STARTED", "STARTED", "INTERRUPTED_OR_LOST__UNKNOWN"],
        ["NOT_STARTED", "STARTED", "RUNNING", "TERMINATED_WITH_STATUS"],
        ["NOT_STARTED", "STARTED", "RUNNING", "INTERRUPTED_OR_LOST__UNKNOWN"],
        ["NOT_STARTED", "INTERRUPTED_OR_LOST__UNKNOWN"],
    )
    if sequence not in valid:
        raise SupervisionError("INVALID_SUPERVISION_STATE_TRANSITION")
    return events


def reserve_once(state_dir: Path, binding_path: Path) -> dict[str, Any]:
    binding, binding_sha256, binding_file_sha256 = load_binding(binding_path)
    if state_dir.exists() or state_dir.is_symlink():
        raise SupervisionError("ONE_SHOT_STATE_ALREADY_EXISTS__NO_RELAUNCH")
    try:
        os.mkdir(state_dir, 0o700)
        _fsync_directory(state_dir.parent)
    except FileExistsError as exc:
        raise SupervisionError("CONCURRENT_ONE_SHOT_RESERVATION_REJECTED") from exc
    return append_event(
        state_dir,
        state="NOT_STARTED",
        binding=binding,
        binding_sha256=binding_sha256,
        binding_file_sha256=binding_file_sha256,
        previous_event_sha256=None,
        details={
            "launch_right_reserved": True,
            "child_start_attempted": False,
            "relaunch_permitted": False,
        },
    )


def launch_detached(state_dir: Path, binding_path: Path) -> dict[str, Any]:
    """Reserve once, then detach one supervisor from the calling session."""
    reservation = reserve_once(state_dir, binding_path)
    binding_file_sha256 = reservation["event"]["binding_file_sha256"]
    log_path = state_dir / "supervisor.log"
    try:
        descriptor = os.open(log_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "wb", closefd=True) as output:
            process = subprocess.Popen(
                [
                    sys.executable,
                    str(Path(__file__).resolve()),
                    "_supervise",
                    "--state-dir",
                    str(state_dir.resolve()),
                    "--binding",
                    str(binding_path.resolve()),
                    "--expected-binding-file-sha256",
                    binding_file_sha256,
                ],
                cwd=str(Path(__file__).resolve().parents[5]),
                stdin=subprocess.DEVNULL,
                stdout=output,
                stderr=subprocess.STDOUT,
                close_fds=True,
                start_new_session=True,
            )
        return {
            "capability_id": CAPABILITY_ID,
            "state_at_reservation": "NOT_STARTED",
            "supervisor_pid": process.pid,
            "session_independent_handoff": True,
            "relaunch_permitted": False,
        }
    except BaseException as exc:
        binding, binding_sha256, observed_file_sha256 = load_binding(binding_path)
        try:
            append_event(
                state_dir,
                state="INTERRUPTED_OR_LOST__UNKNOWN",
                binding=binding,
                binding_sha256=binding_sha256,
                binding_file_sha256=observed_file_sha256,
                previous_event_sha256=reservation["event_sha256"],
                details={
                    "reason": f"SUPERVISOR_HANDOFF_FAILED:{type(exc).__name__}",
                    "child_start_attempted": False,
                    "relaunch_permitted": False,
                },
            )
        finally:
            raise SupervisionError("SUPERVISOR_HANDOFF_FAILED__NO_RELAUNCH") from exc


_INTERRUPTION_SIGNAL: int | None = None


def _record_interruption(signum: int, _frame: object) -> None:
    global _INTERRUPTION_SIGNAL
    _INTERRUPTION_SIGNAL = signum


def supervise(
    state_dir: Path,
    binding_path: Path,
    expected_binding_file_sha256: str,
    *,
    popen_factory: Any = subprocess.Popen,
    before_child_start: Any = None,
    after_child_start: Any = None,
) -> int:
    """Spend the reserved launch right and observe one child, never retrying."""
    events = read_journal(state_dir)
    if [item["event"]["state"] for item in events] != ["NOT_STARTED"]:
        raise SupervisionError("SUPERVISOR_RESTART_OR_DUPLICATE_REJECTED__NO_RELAUNCH")
    binding, binding_sha256, binding_file_sha256 = load_binding(binding_path)
    reservation = events[0]
    if (
        binding_file_sha256 != expected_binding_file_sha256
        or reservation["event"]["binding_file_sha256"] != binding_file_sha256
        or reservation["event"]["binding_sha256"] != binding_sha256
        or reservation["event"]["invocation_binding_identity"]
        != binding["invocation_binding_identity"]
    ):
        raise SupervisionError("STALE_OR_MISMATCHED_INVOCATION_BINDING")
    global _INTERRUPTION_SIGNAL
    _INTERRUPTION_SIGNAL = None
    prior_handlers: dict[int, Any] = {}
    child: subprocess.Popen[Any] | None = None
    launch_right_spent_by_this_supervisor = False
    try:
        supervisor = process_identity(os.getpid(), sha256_bytes(canonical_bytes(sys.argv)))
        started = append_event(
            state_dir,
            state="STARTED",
            binding=binding,
            binding_sha256=binding_sha256,
            binding_file_sha256=binding_file_sha256,
            previous_event_sha256=reservation["event_sha256"],
            details={
                "launch_attempt_count": 1,
                "child_start_attempted": True,
                "supervisor_identity": supervisor,
                "relaunch_permitted": False,
            },
        )
        launch_right_spent_by_this_supervisor = True
        confirmed = read_journal(state_dir)
        if (
            [item["event"]["state"] for item in confirmed]
            != ["NOT_STARTED", "STARTED"]
            or confirmed[-1]["event_sha256"] != started["event_sha256"]
        ):
            raise SupervisionError("STARTED_HANDOFF_NOT_EXCLUSIVE__NO_CHILD_LAUNCH")
        if before_child_start is not None:
            before_child_start()
        for signum in (signal.SIGHUP, signal.SIGINT, signal.SIGTERM):
            prior_handlers[signum] = signal.signal(signum, _record_interruption)
        working_directory = Path(binding["working_directory"])
        if working_directory.is_symlink() or not working_directory.is_dir():
            raise SupervisionError("WORKING_DIRECTORY_UNAVAILABLE")
        log_descriptor = os.open(
            state_dir / "child.log", os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600
        )
        with os.fdopen(log_descriptor, "wb", closefd=True) as output:
            child = popen_factory(
                binding["argv"],
                cwd=str(working_directory),
                stdin=subprocess.DEVNULL,
                stdout=output,
                stderr=subprocess.STDOUT,
                close_fds=True,
                start_new_session=False,
            )
        child_identity = process_identity(child.pid, binding["argv_sha256"])
        running = append_event(
            state_dir,
            state="RUNNING",
            binding=binding,
            binding_sha256=binding_sha256,
            binding_file_sha256=binding_file_sha256,
            previous_event_sha256=started["event_sha256"],
            details={
                "launch_attempt_count": 1,
                "child_identity": child_identity,
                "supervisor_identity": supervisor,
                "relaunch_permitted": False,
            },
        )
        if after_child_start is not None:
            after_child_start(child)
        while child.poll() is None:
            if _INTERRUPTION_SIGNAL is not None:
                append_event(
                    state_dir,
                    state="INTERRUPTED_OR_LOST__UNKNOWN",
                    binding=binding,
                    binding_sha256=binding_sha256,
                    binding_file_sha256=binding_file_sha256,
                    previous_event_sha256=running["event_sha256"],
                    details={
                        "reason": "SUPERVISOR_INTERRUPTED_BEFORE_AUTHENTICATED_CHILD_TERMINAL",
                        "supervisor_signal": _INTERRUPTION_SIGNAL,
                        "child_identity": child_identity,
                        "relaunch_permitted": False,
                    },
                )
                return 125
            time.sleep(0.02)
        returncode = child.wait()
        append_event(
            state_dir,
            state="TERMINATED_WITH_STATUS",
            binding=binding,
            binding_sha256=binding_sha256,
            binding_file_sha256=binding_file_sha256,
            previous_event_sha256=running["event_sha256"],
            details={
                "launch_attempt_count": 1,
                "child_identity": child_identity,
                "process_exit_status": returncode,
                "termination_signal": -returncode if returncode < 0 else None,
                "relaunch_permitted": False,
            },
        )
        return returncode
    except BaseException as exc:
        try:
            current = read_journal(state_dir)[-1]
            if (
                launch_right_spent_by_this_supervisor
                and current["event"]["state"] not in TERMINAL_STATES
            ):
                append_event(
                    state_dir,
                    state="INTERRUPTED_OR_LOST__UNKNOWN",
                    binding=binding,
                    binding_sha256=binding_sha256,
                    binding_file_sha256=binding_file_sha256,
                    previous_event_sha256=current["event_sha256"],
                    details={
                        "reason": f"OBSERVATION_LOST:{type(exc).__name__}",
                        "child_may_have_started": child is not None,
                        "relaunch_permitted": False,
                    },
                )
        except BaseException:
            # Existing STARTED/RUNNING state still permanently spends launch right.
            pass
        if isinstance(exc, SupervisionError):
            raise
        raise SupervisionError("SUPERVISION_OBSERVATION_LOST__NO_RELAUNCH") from exc
    finally:
        for signum, handler in prior_handlers.items():
            signal.signal(signum, handler)


def reconcile_without_relaunch(state_dir: Path, binding_path: Path) -> dict[str, Any]:
    """On recovery, finalize ambiguity as UNKNOWN; never start a process."""
    events = read_journal(state_dir)
    latest = events[-1]
    if latest["event"]["state"] in TERMINAL_STATES:
        return latest
    binding, binding_sha256, binding_file_sha256 = load_binding(binding_path)
    if (
        latest["event"]["binding_file_sha256"] != binding_file_sha256
        or latest["event"]["binding_sha256"] != binding_sha256
    ):
        raise SupervisionError("STALE_OR_MISMATCHED_INVOCATION_BINDING")
    supervisor_identity = latest["event"].get("details", {}).get("supervisor_identity")
    if process_identity_is_live(supervisor_identity):
        return latest
    return append_event(
        state_dir,
        state="INTERRUPTED_OR_LOST__UNKNOWN",
        binding=binding,
        binding_sha256=binding_sha256,
        binding_file_sha256=binding_file_sha256,
        previous_event_sha256=latest["event_sha256"],
        details={
            "reason": "SUPERVISOR_IDENTITY_NOT_AUTHENTICATED_LIVE_ON_RECOVERY",
            "prior_state": latest["event"]["state"],
            "process_identity_reuse_treated_as_unknown": True,
            "relaunch_permitted": False,
        },
    )


def latest_state(state_dir: Path) -> dict[str, Any]:
    return read_journal(state_dir)[-1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("launch", "status", "reconcile", "_supervise"))
    parser.add_argument("--state-dir", required=True, type=Path)
    parser.add_argument("--binding", type=Path)
    parser.add_argument("--expected-binding-file-sha256")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.action == "status":
        print(canonical_bytes(latest_state(args.state_dir)).decode("utf-8"), end="")
        return 0
    if args.binding is None:
        raise SupervisionError("BINDING_REQUIRED")
    if args.action == "launch":
        print(canonical_bytes(launch_detached(args.state_dir, args.binding)).decode("utf-8"), end="")
        return 0
    if args.action == "reconcile":
        print(
            canonical_bytes(reconcile_without_relaunch(args.state_dir, args.binding)).decode("utf-8"),
            end="",
        )
        return 0
    if not _is_sha256(args.expected_binding_file_sha256):
        raise SupervisionError("EXPECTED_BINDING_FILE_SHA256_REQUIRED")
    return supervise(args.state_dir, args.binding, args.expected_binding_file_sha256)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SupervisionError as error:
        print(f"FAIL_CLOSED:{error}", file=sys.stderr)
        raise SystemExit(126)
