#!/usr/bin/env python3
"""Positive, historical, and fail-closed GN presentation-binding proofs."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest


REPOSITORY_ROOT = Path(__file__).resolve().parents[5]
OWNER_PATH = REPOSITORY_ROOT / (
    ".github/governance/evidence/g77_256gn_human_authorization_presentation_binding_v1/"
    "presentation/G77_256GN_SEALED_REQUEST_HUMAN_AUTHORIZATION_PRESENTATION_V1.py"
)
GM_ROOT = REPOSITORY_ROOT / (
    ".github/governance/evidence/g77_256gm_wrong_attempt_operational_v1"
)
GM_REQUEST_PATH = GM_ROOT / "G77_256GM_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
GM_SOURCE_PATH = GM_ROOT / "G77_256GM_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt"
GM_HANDOFF_PATH = GM_ROOT / "G77_256GM_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json"
GM_CHECKPOINT_PATH = GM_ROOT / "G77_256GM_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json"
GM_REDUCTION_PATH = GM_ROOT / "G77_256GM_SPCE_FINAL_FAIL_CLOSED_REDUCTION_V1.json"
GM_REPORT_PATH = REPOSITORY_ROOT / (
    "docs/governance/G77_256GM_ONE_BOUNDED_FRESH_HUMAN_AUTHORIZED_"
    "WRONG_ATTEMPT_OPERATIONAL_COMMISSIONING_V1.md"
)
SEALED_ARGV = "86a2f758047d1b25f81153b76ade2ddc1d321776a9e3ec5ab3545beb3f5f9389"
HISTORICALLY_PRESENTED_ARGV = (
    "5533f3825de28ad98f689a035cd24cbba6b3856ca093f30a679a8797f0f076e4"
)


def load_module(path: Path, name: str):
    specification = importlib.util.spec_from_file_location(name, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


GN = load_module(OWNER_PATH, "g77_256gn_presentation_owner")


def base_envelope() -> dict:
    return json.loads(GM_REQUEST_PATH.read_bytes())


def reseal(envelope: dict) -> None:
    envelope["request_sha256"] = hashlib.sha256(
        GN._canonical_bytes(envelope["request"])
    ).hexdigest()


def write_envelope(path: Path, envelope: dict) -> Path:
    path.write_bytes(GN._canonical_bytes(envelope))
    return path


def synthetic_request(tmp_path: Path, prefix: str, digit: str) -> Path:
    envelope = base_envelope()
    request = envelope["request"]
    envelope["schema_id"] = (
        f"{prefix}_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_ENVELOPE_V1"
    )
    request["schema_id"] = f"{prefix}_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1"
    request["generation_identity"] = f"{prefix}_GENERATION_V1"
    request["operation_identity"] = f"{prefix}_OPERATION_001"
    request["repository"]["head"] = digit * 40
    request["repository"]["remote_head"] = digit * 40
    request["repository"]["tree"] = str((int(digit) + 1) % 10) * 40
    request["live_binding"]["candidate_sha256"] = digit * 64
    request["live_binding"]["context_sha256"] = str((int(digit) + 1) % 10) * 64
    request["live_binding"]["canonical_argv_sha256"] = str(
        (int(digit) + 2) % 10
    ) * 64
    request["preauthorization"]["checkpoint_inner_sha256"] = str(
        (int(digit) + 3) % 10
    ) * 64
    reseal(envelope)
    return write_envelope(tmp_path / f"{prefix}.json", envelope)


def mutate_presentation(raw: bytes, field: str, value) -> bytes:
    lines = raw.decode("utf-8").splitlines()
    index = next(index for index, line in enumerate(lines) if line.startswith(field + " "))
    lines[index] = f"{field} {json.dumps(value, ensure_ascii=False, allow_nan=False)}"
    return ("\n".join(lines) + "\n").encode("utf-8")


def assert_presentation_rejected(request_path: Path, raw: bytes) -> None:
    with pytest.raises(GN.PresentationBindingError):
        GN.validate_human_authorization_presentation(request_path, raw)


def test_two_fresh_synthetic_identities_repeat_and_prove_exact_equivalence(tmp_path: Path):
    first_path = synthetic_request(tmp_path, "G77_256GNTESTA", "1")
    second_path = synthetic_request(tmp_path, "G77_256GNTESTB", "5")
    first_a = GN.render_human_authorization_presentation(first_path)
    first_b = GN.render_human_authorization_presentation(first_path)
    second = GN.render_human_authorization_presentation(second_path)
    assert first_a == first_b
    assert first_a != second
    for request_path, presentation in ((first_path, first_a), (second_path, second)):
        result = GN.validate_human_authorization_presentation(
            request_path, presentation
        )
        assert result["human_presentation_request_equivalence"] == (
            "VERIFIED_WITHIN_EXACT_REVIEWED_AUTHORIZATION_BINDING_BOUNDARY"
        )
        assert result["human_presentation_caller_override_blocked"] is True
        assert result["reviewed_field_count"] == len(GN.PRESENTATION_FIELDS)
        assert result["human_constitutional_authorization_count"] == 0
        assert result["operational_execution_count"] == 0
        assert result["qemu_execution_count"] == 0


def test_historical_gm_failure_class_renders_x_and_cannot_independently_render_y():
    presentation = GN.render_human_authorization_presentation(GM_REQUEST_PATH)
    parsed = GN.parse_human_authorization_presentation(presentation)
    assert parsed["CANONICAL_ARGV_SHA256"] == SEALED_ARGV
    assert SEALED_ARGV.encode() in presentation
    assert HISTORICALLY_PRESENTED_ARGV.encode() not in presentation
    result = GN.validate_human_authorization_presentation(
        GM_REQUEST_PATH, presentation
    )
    assert result["request_sha256"] == (
        "d781ff310a7bd2e0d75c37bc0bff04670e0ccbef32d7aaeee55590107fba0854"
    )


@pytest.mark.parametrize(
    ("field", "wrong"),
    (
        ("GENERATION_ID", "G77_256STALE_GENERATION"),
        ("OPERATION_ID", "G77_256STALE_OPERATION"),
        ("HEAD", "0" * 40),
        ("TREE", "1" * 40),
        ("CANDIDATE_SHA256", "2" * 64),
        ("CONTEXT_SHA256", "3" * 64),
        ("CANONICAL_ARGV_SHA256", HISTORICALLY_PRESENTED_ARGV),
        ("CHECKPOINT_SHA256", "4" * 64),
        ("AUTHORIZATION_REQUEST_SHA256", "5" * 64),
    ),
)
def test_identity_and_hash_divergence_fails_closed(field: str, wrong):
    presentation = GN.render_human_authorization_presentation(GM_REQUEST_PATH)
    assert_presentation_rejected(
        GM_REQUEST_PATH, mutate_presentation(presentation, field, wrong)
    )


@pytest.mark.parametrize(
    ("field", "wrong"),
    (
        ("ONE_SHOT", False),
        ("REUSABLE", True),
        ("TRANSFERABLE", True),
        ("GOVERNED_LAUNCHER_ACTIVATION_LIMIT", 2),
        ("QEMU_EXECUTION_LIMIT", 2),
        ("VM_BOOT_LIMIT", 2),
        ("OPERATION_ATTEMPT_LIMIT", 2),
        ("NETWORK_AUTHORIZED", True),
        ("RETRY_LIMIT", 1),
        ("REPAIR_LIMIT", 1),
        ("REPLAY_LIMIT", 1),
        ("REPLACEMENT_AUTHORITY_AUTHORIZED", True),
        ("SECOND_ATTEMPT_AUTHORIZED", True),
        ("SUCCESSOR_GENERATION_AUTHORIZED", True),
    ),
)
def test_restriction_execution_bound_and_prohibition_divergence_fails_closed(
    field: str, wrong
):
    presentation = GN.render_human_authorization_presentation(GM_REQUEST_PATH)
    assert_presentation_rejected(
        GM_REQUEST_PATH, mutate_presentation(presentation, field, wrong)
    )


def test_missing_duplicate_ambiguous_malformed_and_mutated_presentations_fail_closed():
    presentation = GN.render_human_authorization_presentation(GM_REQUEST_PATH)
    lines = presentation.decode("utf-8").splitlines()
    head_index = next(i for i, line in enumerate(lines) if line.startswith("HEAD "))

    missing = lines[:head_index] + lines[head_index + 1:]
    assert_presentation_rejected(
        GM_REQUEST_PATH, ("\n".join(missing) + "\n").encode()
    )

    duplicate = lines[:head_index + 1] + [lines[head_index]] + lines[head_index + 1:]
    assert_presentation_rejected(
        GM_REQUEST_PATH, ("\n".join(duplicate) + "\n").encode()
    )

    ambiguous = copy.deepcopy(lines)
    ambiguous[head_index] = "HEAD_ALIAS " + json.dumps("0" * 40)
    assert_presentation_rejected(
        GM_REQUEST_PATH, ("\n".join(ambiguous) + "\n").encode()
    )

    malformed = copy.deepcopy(lines)
    malformed[head_index] = 'HEAD "a" "b"'
    assert_presentation_rejected(
        GM_REQUEST_PATH, ("\n".join(malformed) + "\n").encode()
    )

    mutated_notice = presentation.replace(
        GN.PRESENTATION_NOTICE.encode(), b"NONAUTHORITY: mutated after derivation."
    )
    assert_presentation_rejected(GM_REQUEST_PATH, mutated_notice)


def test_malformed_duplicate_noncanonical_invalid_seal_and_schema_drift_fail_closed(
    tmp_path: Path,
):
    malformed = tmp_path / "malformed.json"
    malformed.write_bytes(b"{\n")
    duplicate = tmp_path / "duplicate.json"
    duplicate.write_bytes(b'{"schema_id":"x","schema_id":"y"}\n')
    pretty = tmp_path / "pretty.json"
    pretty.write_text(json.dumps(base_envelope(), indent=2) + "\n", encoding="utf-8")

    invalid_seal_value = base_envelope()
    invalid_seal_value["request"]["operation_identity"] = "G77_256ALTERED"
    invalid_seal = write_envelope(tmp_path / "invalid_seal.json", invalid_seal_value)

    missing_value = base_envelope()
    del missing_value["request"]["live_binding"]["canonical_argv_sha256"]
    reseal(missing_value)
    missing = write_envelope(tmp_path / "missing.json", missing_value)

    unknown_value = base_envelope()
    unknown_value["request"]["unknown_constitutional_override"] = "0" * 64
    reseal(unknown_value)
    unknown = write_envelope(tmp_path / "unknown.json", unknown_value)

    for path in (malformed, duplicate, pretty, invalid_seal, missing, unknown):
        with pytest.raises(GN.PresentationBindingError):
            GN.load_validated_sealed_request(path)


@pytest.mark.parametrize(
    ("field", "wrong"),
    (
        ("one_shot", False),
        ("reusable", True),
        ("transferable", True),
        ("network_authorized", True),
        ("retry_limit", 1),
        ("repair_limit", 1),
        ("replay_limit", 1),
        ("replacement_authority_authorized", True),
        ("second_attempt_authorized", True),
        ("successor_generation_authorized", True),
    ),
)
def test_resealed_request_semantic_drift_is_rejected(
    tmp_path: Path, field: str, wrong
):
    envelope = base_envelope()
    envelope["request"]["requested_authority_semantics"][field] = wrong
    reseal(envelope)
    path = write_envelope(tmp_path / f"wrong_{field}.json", envelope)
    with pytest.raises(GN.PresentationBindingError):
        GN.render_human_authorization_presentation(path)


def test_stale_presentation_cannot_validate_against_a_fresh_request(tmp_path: Path):
    old_request = synthetic_request(tmp_path, "G77_256GNSTALEA", "2")
    fresh_request = synthetic_request(tmp_path, "G77_256GNFRESHB", "6")
    stale_presentation = GN.render_human_authorization_presentation(old_request)
    assert_presentation_rejected(fresh_request, stale_presentation)


def test_caller_cannot_supply_a_constitutional_override():
    with pytest.raises(TypeError):
        GN.render_human_authorization_presentation(
            GM_REQUEST_PATH,
            canonical_argv_sha256=HISTORICALLY_PRESENTED_ARGV,
        )
    source = OWNER_PATH.read_text(encoding="utf-8")
    assert "def render_human_authorization_presentation(request_path: Path)" in source
    assert "CALLER_OVERRIDE=PROHIBITED" in source


def test_exact_gm_terminal_failure_owners_counters_ex_and_e05_reauthenticate():
    envelope = json.loads(GM_REDUCTION_PATH.read_bytes())
    reduction = envelope["reduction"]
    assert reduction["terminal_failure"] == {
        "checkpoint_or_request_defect_proven": False,
        "codex_presentation_defect_proven": True,
        "failure_class": (
            "AUTHORIZATION_PRESENTATION_BINDING_MISMATCH__HUMAN_RESPONSE_"
            "FAITHFULLY_REPEATED_NONCANONICAL_ARGV_HASH"
        ),
        "first_broken_edge": (
            "HUMAN_AUTHORIZATION_PRESENTED_CANONICAL_ARGV_BINDING_TO_SEALED_"
            "GM_CONTEXT_AND_REQUEST"
        ),
        "first_failure": (
            "RuntimeError: execution authority binding mismatch: "
            "authorized_canonical_argv_sha256"
        ),
        "human_source_transcription_defect_proven": False,
        "minimum_safe_correction_owner_set": [
            "FUTURE_GENERATION_SEALED_REQUEST_TO_HUMAN_AUTHORIZATION_TEXT_PRESENTATION",
            "FUTURE_GENERATION_AUTHORIZATION_BINDING_REAUTHENTICATION",
        ],
        "phase": "POST_AUTHORITY__PRE_LAUNCHER_ACTIVATION__FO_FINAL_ADMISSION",
        "rejecting_owner": "UNCHANGED_FO_VALIDATE_EXECUTION_ADMISSION",
        "repair_performed": False,
        "replacement_authority_requested": False,
        "replay_performed": False,
        "retry_performed": False,
        "runtime_only_provable": False,
        "source_owner": "GM_PHASE_H_CODEX_AUTHORIZATION_TEXT_PRESENTATION",
        "statically_provable_before_launcher": True,
        "successor_generation_started": False,
    }
    assert reduction["binding_comparison"]["sealed_context_and_request_canonical_argv_sha256"] == SEALED_ARGV
    assert reduction["binding_comparison"]["presented_and_human_authorized_canonical_argv_sha256"] == HISTORICALLY_PRESENTED_ARGV
    assert reduction["human_authority"]["authorization_consumed"] is True
    assert reduction["human_authority"]["authorization_terminal"] is True
    assert reduction["human_authority"]["authorization_reusable"] is False
    assert reduction["human_authority"]["authorization_transferable"] is False
    counters = reduction["operational_counters"]
    for field in (
        "pre_count", "post_count", "governed_launcher_activations",
        "qemu_execution_count", "vm_boot_count", "wrong_attempt_execution_count",
        "operation_attempt_count", "request_count", "p11_entry_count",
        "protected_invocation_count", "protected_effect_count", "retry_count",
        "repair_execution_count", "replay_execution_count",
    ):
        assert counters[field] == 0, field
    assert reduction["ex"] == {
        "operational_effect": 0, "reconstructed": 0, "reused": "17/17", "status": "PASS"
    }
    assert reduction["e05"]["before"] == "6/18"
    assert reduction["e05"]["after"] == "6/18"
    assert reduction["e05"]["credit_awarded"] == 0


def test_historical_gm_evidence_is_bit_identical_and_immutable():
    expected = {
        GM_REQUEST_PATH: "eaf55ff88b8ba33eafbb05f051f0a1bcee8448ad63c67ddbb674e4aca5b411d7",
        GM_SOURCE_PATH: "3b5bd735c33a66e2b31d8c504e455516a7a9c91691540f7b4090e88464a1b22b",
        GM_HANDOFF_PATH: "1044666b5f547e5c656429c7d6caa669ac0295a8e9c9f1e1c9887d6b3383e01b",
        GM_CHECKPOINT_PATH: "af99bfa33f19bf848ad8ff452bf16bc9bc42c73784d8bcea1656e97b62b4ed55",
        GM_REDUCTION_PATH: "4b8030935557af4e8b630dc5aedce160c6448da79ae7b9b90b2172632a35466d",
        GM_REPORT_PATH: "d982e1c8c7fe64f36d507408648f4e0149361fd0c33c40cdd879f23bd05b23b1",
    }
    for path, expected_sha256 in expected.items():
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected_sha256


def test_bounded_same_class_review_finds_one_general_boundary_not_a_second_owner_defect():
    owner_source = OWNER_PATH.read_text(encoding="utf-8")
    gj_owner = REPOSITORY_ROOT / GN.CANONICAL_OWNER_RELATIVE_PATH
    fo_test = REPOSITORY_ROOT / (
        ".github/governance/evidence/g77_256fo_launcher_authority_binding_v1/"
        "tests/test_g77_256fo_execution_admission_v1.py"
    )
    historical_sources = [
        REPOSITORY_ROOT / (
            f".github/governance/evidence/g77_256{generation.lower()}_wrong_attempt_operational_v1/"
            f"G77_256{generation}_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt"
        )
        for generation in ("GI", "GK", "GM")
    ]
    assert all(path.is_file() for path in historical_sources)
    assert "canonical_bytes" in gj_owner.read_text(encoding="utf-8")
    assert "authorized_canonical_argv_sha256" in fo_test.read_text(encoding="utf-8")
    assert "render_human_authorization_presentation" in owner_source
    assert "subprocess.run" not in owner_source
    assert "qemu-system-x86_64" not in owner_source
    assert "validate_execution_admission" not in owner_source
