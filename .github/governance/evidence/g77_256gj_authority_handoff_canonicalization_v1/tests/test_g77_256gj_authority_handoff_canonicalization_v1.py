from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
from unittest import mock

import pytest


REPOSITORY_ROOT = Path(__file__).resolve().parents[5]
LAUNCHER_PATH = REPOSITORY_ROOT / (
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
SPEC = importlib.util.spec_from_file_location("g77_256gj_fm_owner", LAUNCHER_PATH)
assert SPEC is not None and SPEC.loader is not None
LAUNCHER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(LAUNCHER)


def context_for(root: Path, prefix: str = "G77_256GJFIXTURE") -> dict:
    return LAUNCHER.build_operation_context(
        repository_root=REPOSITORY_ROOT,
        repository_head="a" * 40,
        repository_tree="b" * 40,
        generation_identity=(
            f"{prefix}_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_ATTEMPT_"
            "OPERATIONAL_COMMISSIONING_V1"
        ),
        operation_identity=f"{prefix}_OPERATION_001",
        identity_namespace_prefix=prefix,
        operation_evidence_root=root / "operation",
        transient_root=root / "transient",
    )


def fixture_for(context: dict) -> dict:
    return LAUNCHER.preauthority_serialization_fixture(
        context,
        request_sha256="c" * 64,
        checkpoint_sha256="d" * 64,
    )


def assert_rejected(raw: bytes) -> None:
    with pytest.raises(RuntimeError):
        LAUNCHER.parse_authority_handoff_bytes(raw)


def test_repository_fixture_producer_loader_bytes_and_semantics_are_exact():
    with tempfile.TemporaryDirectory(prefix="g77_256gj_repository_fixture_") as temporary:
        context = context_for(Path(temporary))
        authorization = fixture_for(context)
        envelope = LAUNCHER.build_authority_handoff(authorization)
        payload = LAUNCHER.canonical_authority_handoff_bytes(authorization)
        assert payload == LAUNCHER.canonical_bytes(envelope)
        assert payload.endswith(b"\n") and not payload.endswith(b"\n\n")
        assert LAUNCHER.parse_authority_handoff_bytes(payload) == envelope
        assert json.loads(payload)["authorization"] == authorization
        assert envelope["authorization_sha256"] == LAUNCHER.authority_sha256(authorization)
        assert authorization["authorization_present"] is False
        assert authorization["authorization_kind"] == (
            "TEST_ONLY_NON_AUTHORITY_SERIALIZATION_FIXTURE"
        )


@pytest.mark.parametrize("prefix", ["G77_256GJSYNTHA", "G77_256GJSYNTHB"])
def test_fresh_synthetic_namespaces_prove_deterministic_equivalence(prefix: str):
    with tempfile.TemporaryDirectory(prefix="g77_256gj_synthetic_") as temporary:
        context = context_for(Path(temporary), prefix)
        first = LAUNCHER.canonical_authority_handoff_bytes(fixture_for(context))
        second = LAUNCHER.canonical_authority_handoff_bytes(fixture_for(context))
        assert first == second
        assert hashlib.sha256(first).hexdigest() == hashlib.sha256(second).hexdigest()


def test_existing_atomic_writer_and_unchanged_loader_are_equivalent_without_qemu():
    with tempfile.TemporaryDirectory(prefix="g77_256gj_writer_") as temporary:
        root = Path(temporary)
        context = context_for(root)
        authorization = fixture_for(context)
        path = root / "authority.json"
        with mock.patch.object(
            LAUNCHER.subprocess,
            "run",
            side_effect=AssertionError("QEMU/process execution is prohibited"),
        ):
            result = LAUNCHER.write_authority_handoff(path, authorization)
        loaded, loaded_sha256 = LAUNCHER.load_authority(path)
        assert loaded == LAUNCHER.build_authority_handoff(authorization)
        assert loaded_sha256 == result["authority_file_sha256"]
        assert path.read_bytes() == LAUNCHER.canonical_authority_handoff_bytes(authorization)


def test_preauthority_static_proof_is_nonauthority_and_complete():
    with tempfile.TemporaryDirectory(prefix="g77_256gj_preauthority_") as temporary:
        proof = LAUNCHER.prove_authority_handoff_canonicalization(
            context_for(Path(temporary))
        )
        assert proof["result"] == "PREAUTHORITY_CANONICAL_AUTHORITY_HANDOFF_PROOF_PASS"
        assert proof["fixture_classification"] == (
            "TEST_ONLY__NON_AUTHORITY__NON_OPERATIONAL"
        )
        assert proof["loader_producer_canonicalization_equivalence"] == "VERIFIED"
        assert proof["no_pretty_print_reencoding_path"] == "VERIFIED"
        assert proof["no_second_serializer_path"] == "VERIFIED"
        assert proof["producer_output_sha256"] == proof["loader_expectation_sha256"]
        assert proof["producer_output_sha256"] == proof["deterministic_repeat_sha256"]
        assert proof["human_operational_authorization_count"] == 0
        assert proof["qemu_execution_count"] == 0


def test_noncanonical_and_malformed_byte_matrix_fails_closed():
    with tempfile.TemporaryDirectory(prefix="g77_256gj_bytes_") as temporary:
        context = context_for(Path(temporary))
        envelope = LAUNCHER.build_authority_handoff(fixture_for(context))
        canonical = LAUNCHER.canonical_bytes(envelope)
        variants = {
            "pretty_printed_envelope": (
                json.dumps(envelope, sort_keys=True, indent=2) + "\n"
            ).encode(),
            "unsorted_key_order": (
                json.dumps(envelope, sort_keys=False, separators=(",", ":")) + "\n"
            ).encode(),
            "missing_lf": canonical[:-1],
            "extra_whitespace": canonical[:-1] + b" \n",
            "duplicate_keys": b'{"schema_id":"x","schema_id":"y"}\n',
            "malformed_json": b"{\n",
            "non_object_envelope": b"[]\n",
            "same_semantic_json_noncanonical_outer": (
                json.dumps(json.loads(canonical), sort_keys=True) + "\n"
            ).encode(),
        }
        for name, raw in variants.items():
            with pytest.raises(RuntimeError):
                assert name
                LAUNCHER.parse_authority_handoff_bytes(raw)


def test_request_checkpoint_and_context_binding_negative_matrix_fails_closed():
    with tempfile.TemporaryDirectory(prefix="g77_256gj_bindings_") as temporary:
        context = context_for(Path(temporary))
        baseline = fixture_for(context)
        for name, field, value in (
            ("wrong_generation", "authorized_generation_identity", "G77_256STALE"),
            ("wrong_operation", "authorized_operation_identity", "G77_256STALE_OP"),
            ("wrong_head", "authorized_repository_head", "0" * 40),
            ("wrong_tree", "authorized_repository_tree", "1" * 40),
            ("wrong_candidate", "authorized_candidate_sha256", "2" * 64),
            ("wrong_context", "authorized_context_sha256", "3" * 64),
            ("wrong_argv", "authorized_canonical_argv_sha256", "4" * 64),
            ("stale_authority_identity", "authorization_source_sha256", "5" * 64),
        ):
            mutated = copy.deepcopy(baseline)
            mutated[field] = value
            with pytest.raises(RuntimeError, match="fixture binding mismatch"):
                LAUNCHER.validate_preauthority_serialization_fixture(
                    context,
                    mutated,
                    request_sha256="c" * 64,
                    checkpoint_sha256="d" * 64,
                )
            assert name
        with pytest.raises(RuntimeError, match="fixture binding mismatch"):
            LAUNCHER.validate_preauthority_serialization_fixture(
                context,
                baseline,
                request_sha256="6" * 64,
                checkpoint_sha256="d" * 64,
            )
        with pytest.raises(RuntimeError, match="fixture binding mismatch"):
            LAUNCHER.validate_preauthority_serialization_fixture(
                context,
                baseline,
                request_sha256="c" * 64,
                checkpoint_sha256="7" * 64,
            )


def test_schema_unknown_field_inner_seal_and_post_serialization_mutation_rejected():
    with tempfile.TemporaryDirectory(prefix="g77_256gj_envelope_") as temporary:
        context = context_for(Path(temporary))
        envelope = LAUNCHER.build_authority_handoff(fixture_for(context))
        variants = []
        wrong_version = copy.deepcopy(envelope)
        wrong_version["schema_id"] = "WRONG_ENVELOPE_VERSION"
        variants.append(wrong_version)
        unknown_outer = copy.deepcopy(envelope)
        unknown_outer["unknown"] = True
        variants.append(unknown_outer)
        unknown_inner = copy.deepcopy(envelope)
        unknown_inner["authorization"]["unknown"] = True
        unknown_inner["authorization_sha256"] = LAUNCHER.authority_sha256(
            unknown_inner["authorization"]
        )
        variants.append(unknown_inner)
        semantic_modified_after_canonicalization = copy.deepcopy(envelope)
        semantic_modified_after_canonicalization["authorization"][
            "authorized_repository_head"
        ] = "8" * 40
        variants.append(semantic_modified_after_canonicalization)
        canonical_envelope_modified_after_seal = copy.deepcopy(envelope)
        canonical_envelope_modified_after_seal["authorization_sha256"] = "9" * 64
        variants.append(canonical_envelope_modified_after_seal)
        for variant in variants:
            assert_rejected(LAUNCHER.canonical_bytes(variant))


def test_gi_inner_canonical_outer_pretty_failure_is_reproduced_and_blocked():
    gi_path = REPOSITORY_ROOT / (
        ".github/governance/evidence/g77_256gi_wrong_attempt_operational_v1/"
        "G77_256GI_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json"
    )
    raw = gi_path.read_bytes()
    envelope = json.loads(raw)
    assert envelope["authorization_sha256"] == LAUNCHER.authority_sha256(
        envelope["authorization"]
    )
    assert raw != LAUNCHER.canonical_bytes(envelope)
    assert_rejected(raw)
    corrected = LAUNCHER.canonical_authority_handoff_bytes(envelope["authorization"])
    assert corrected == LAUNCHER.canonical_bytes(envelope)
    assert LAUNCHER.parse_authority_handoff_bytes(corrected) == envelope


def test_second_serializer_path_cannot_match_or_be_accepted():
    with tempfile.TemporaryDirectory(prefix="g77_256gj_second_serializer_") as temporary:
        context = context_for(Path(temporary))
        envelope = LAUNCHER.build_authority_handoff(fixture_for(context))
        producer = LAUNCHER.canonical_authority_handoff_bytes(envelope["authorization"])
        second_serializer = (json.dumps(envelope, sort_keys=True, indent=1) + "\n").encode()
        assert producer != second_serializer
        assert_rejected(second_serializer)
