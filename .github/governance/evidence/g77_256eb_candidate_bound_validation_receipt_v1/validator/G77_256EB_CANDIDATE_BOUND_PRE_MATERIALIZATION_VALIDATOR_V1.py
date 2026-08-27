#!/usr/bin/env python3
"""Candidate-bound successor for the immutable DU Canonical V1 validator."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from types import ModuleType
from typing import Any, Callable


RECEIPT_ENVELOPE_SCHEMA_ID = "SAPIANTA_CANDIDATE_BOUND_VALIDATION_RECEIPT_ENVELOPE_V1"
RECEIPT_SCHEMA_ID = "SAPIANTA_CANDIDATE_BOUND_VALIDATION_RECEIPT_V1"
RECEIPT_VERSION = "1.0.0"
GENERATION_IDENTITY = (
    "G77_256EB_CANDIDATE_BOUND_PRE_MATERIALIZATION_VALIDATION_RECEIPT_HARDENING_V1"
)
VALIDATION_MODE = "CANDIDATE_VALIDATION"
VALIDATION_PROFILE = "CANONICAL_V1_PRE_MATERIALIZATION_FOUR_GATE_CANDIDATE_BOUND_V1"
VALIDATOR_IDENTITY = "G77_256EB_CANDIDATE_BOUND_PRE_MATERIALIZATION_VALIDATOR_V1"
DU_VALIDATOR_IDENTITY = "G77_256DU_PRE_MATERIALIZATION_CONSUMER_VALIDATOR_V1"
DU_SCHEMA_IDENTITY = "SAPIANTA_SPCE_CONTINUATION_MANIFEST_SCHEMA_V1"
RECEIPT_SCHEMA_IDENTITY = (
    "SAPIANTA_CANDIDATE_BOUND_PRE_MATERIALIZATION_VALIDATION_RECEIPT_SCHEMA_V1"
)
VALIDATOR_RELATIVE_PATH = (
    ".github/governance/evidence/g77_256eb_candidate_bound_validation_receipt_v1/"
    "validator/G77_256EB_CANDIDATE_BOUND_PRE_MATERIALIZATION_VALIDATOR_V1.py"
)
DU_VALIDATOR_RELATIVE_PATH = (
    ".github/governance/evidence/g77_256du_continuation_manifest_contract_v1/"
    "validator/G77_256DU_CONTINUATION_MANIFEST_COMPATIBILITY_VALIDATOR_V1.py"
)
DU_SCHEMA_RELATIVE_PATH = (
    ".github/governance/evidence/g77_256du_continuation_manifest_contract_v1/"
    "G77_256DU_CANONICAL_CONTINUATION_MANIFEST_SCHEMA_V1.json"
)
RECEIPT_SCHEMA_RELATIVE_PATH = (
    ".github/governance/evidence/g77_256eb_candidate_bound_validation_receipt_v1/"
    "G77_256EB_CANDIDATE_BOUND_VALIDATION_RECEIPT_SCHEMA_V1.json"
)
DU_VALIDATOR_SHA256 = "27457993a4e6b778cc65356cd9b17a1bf2665f4e6147608d27dc233ff512304d"
DU_SCHEMA_SHA256 = "a21ba1567c65101a5f178afdfefb5d500c97fc2cc6a9eb9da6c9fb4cc914478e"
GATE_FIELDS = (
    "manifest_authenticity_gate",
    "manifest_schema_validity_gate",
    "manifest_semantic_compatibility_gate",
    "manifest_constitutional_admissibility_gate",
)
RECEIPT_FIELDS = frozenset({
    "schema_id",
    "receipt_version",
    "generation_identity",
    "candidate_binding",
    "validator_binding",
    "canonical_v1_contract_validator_binding",
    "candidate_manifest_schema_binding",
    "receipt_schema_binding",
    "validation_mode",
    "validation_profile",
    "canonical_argument_vector",
    "validation_command_identity_sha256",
    "process_exit_status",
    "gate_results",
    "overall_result",
    "required_head",
    "required_tree",
    "receipt_is_authority",
    "auto_continuable",
})
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
GIT_OBJECT_RE = re.compile(r"^[0-9a-f]{40}$")


class ReceiptError(ValueError):
    """One deterministic fail-closed receipt or mode rejection."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"
    ).encode()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def _fail(code: str, message: str) -> None:
    raise ReceiptError(code, message)


def _git(repository_root: Path, *arguments: str) -> str:
    try:
        return subprocess.check_output(
            ["git", *arguments], cwd=repository_root, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except subprocess.CalledProcessError as exc:
        raise ReceiptError("GIT_BINDING_UNAVAILABLE", "Git binding could not be resolved") from exc


def _repository_path(repository_root: Path, raw_path: Any, field: str) -> tuple[str, Path]:
    if not isinstance(raw_path, str) or not raw_path:
        _fail("RECEIPT_SCHEMA_INVALID", f"{field} must be a non-empty repository path")
    relative = Path(raw_path)
    if relative.is_absolute() or ".." in relative.parts:
        _fail("PATH_OUTSIDE_REPOSITORY", f"{field} must be repository-relative")
    root = repository_root.resolve()
    path = (root / relative).resolve()
    try:
        normalized = str(path.relative_to(root))
    except ValueError:
        _fail("PATH_OUTSIDE_REPOSITORY", f"{field} escapes repository")
    if normalized != raw_path:
        _fail("PATH_NOT_CANONICAL", f"{field} is not a canonical repository path")
    if not path.is_file():
        _fail("BOUND_FILE_ABSENT", f"{field} does not identify a file")
    return normalized, path


def _relative_path(repository_root: Path, path: Path) -> str:
    root = repository_root.resolve()
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(root))
    except ValueError:
        _fail("PATH_OUTSIDE_REPOSITORY", "candidate must be repository-resident")


def _load_du_validator(repository_root: Path) -> ModuleType:
    path = repository_root / DU_VALIDATOR_RELATIVE_PATH
    if sha256_path(path) != DU_VALIDATOR_SHA256:
        _fail("DU_VALIDATOR_HASH_MISMATCH", "immutable DU validator bytes differ")
    schema_path = repository_root / DU_SCHEMA_RELATIVE_PATH
    if sha256_path(schema_path) != DU_SCHEMA_SHA256:
        _fail("DU_SCHEMA_HASH_MISMATCH", "immutable DU schema bytes differ")
    spec = importlib.util.spec_from_file_location("g77_256du_validator_v1", path)
    if spec is None or spec.loader is None:
        _fail("DU_VALIDATOR_IMPORT_FAILED", "immutable DU validator could not be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _command_vector(candidate_path: str, required_head: str, required_tree: str) -> list[str]:
    return [
        "--mode",
        VALIDATION_MODE,
        "--candidate",
        candidate_path,
        "--required-head",
        required_head,
        "--required-tree",
        required_tree,
        "--profile",
        VALIDATION_PROFILE,
    ]


def _authenticate_git_baseline(
    repository_root: Path, required_head: str, required_tree: str
) -> None:
    if not isinstance(required_head, str) or GIT_OBJECT_RE.fullmatch(required_head) is None:
        _fail("REQUIRED_HEAD_FORMAT_INVALID", "required HEAD must be a Git object identity")
    if not isinstance(required_tree, str) or GIT_OBJECT_RE.fullmatch(required_tree) is None:
        _fail("REQUIRED_TREE_FORMAT_INVALID", "required tree must be a Git object identity")
    actual_head = _git(repository_root, "rev-parse", "HEAD")
    if actual_head != required_head:
        _fail("REQUIRED_HEAD_MISMATCH", "actual HEAD differs from receipt baseline")
    head_tree = _git(repository_root, "rev-parse", f"{required_head}^{{tree}}")
    actual_tree = _git(repository_root, "rev-parse", "HEAD^{tree}")
    if required_tree != head_tree or actual_tree != required_tree:
        _fail("REQUIRED_TREE_MISMATCH", "required tree does not belong to actual HEAD")


def _candidate_canonical_bytes(du: ModuleType, candidate_path: Path) -> bytes:
    raw = candidate_path.read_bytes()
    value = du.load_json_bytes(raw)
    if raw != du.canonical_bytes(value):
        _fail(
            "CANDIDATE_CANONICAL_SERIALIZATION_INVALID",
            "candidate bytes are not canonical V1 JSON",
        )
    return raw


def _gate_results(du_result: dict[str, str]) -> dict[str, str]:
    mapping = {
        "manifest_authenticity_gate": "cryptographic_authenticity",
        "manifest_schema_validity_gate": "structural_schema_validity",
        "manifest_semantic_compatibility_gate": "semantic_contract_compatibility",
        "manifest_constitutional_admissibility_gate": "constitutional_admissibility",
    }
    result = {gate: du_result[source] for gate, source in mapping.items()}
    if any(result[gate] != "PASS" for gate in GATE_FIELDS):
        _fail("FOUR_GATE_RESULT_NOT_PASS", "DU did not return four independent PASS results")
    return result


def _run_du_validation(
    du: ModuleType,
    candidate_path: Path,
    repository_root: Path,
    required_head: str,
) -> dict[str, str]:
    try:
        return du.validate_file(
            candidate_path,
            repository_root,
            expected_head=required_head,
        )
    except Exception as exc:
        code = getattr(exc, "code", "DU_CANONICAL_V1_VALIDATION_FAILED")
        raise ReceiptError(code, "DU Canonical V1 candidate validation failed") from exc


def validate_candidate(
    repository_root: Path,
    candidate: Path,
    *,
    required_head: str,
    required_tree: str,
    validation_profile: str = VALIDATION_PROFILE,
) -> dict[str, Any]:
    """Validate one exact candidate and return a self-authenticating receipt."""
    if validation_profile != VALIDATION_PROFILE:
        _fail("VALIDATION_PROFILE_INVALID", "only the canonical EB profile is admissible")
    _authenticate_git_baseline(repository_root, required_head, required_tree)
    candidate_relative = _relative_path(repository_root, candidate)
    _, candidate_path = _repository_path(
        repository_root, candidate_relative, "candidate_binding.path"
    )
    du = _load_du_validator(repository_root)
    raw = _candidate_canonical_bytes(du, candidate_path)
    du_result = _run_du_validation(du, candidate_path, repository_root, required_head)
    gates = _gate_results(du_result)
    argument_vector = _command_vector(candidate_relative, required_head, required_tree)
    receipt = {
        "schema_id": RECEIPT_SCHEMA_ID,
        "receipt_version": RECEIPT_VERSION,
        "generation_identity": GENERATION_IDENTITY,
        "candidate_binding": {
            "path": candidate_relative,
            "file_sha256": sha256_bytes(raw),
            "canonical_serialization_state": "CANONICAL_V1_JSON",
        },
        "validator_binding": {
            "identity": VALIDATOR_IDENTITY,
            "path": VALIDATOR_RELATIVE_PATH,
            "file_sha256": sha256_path(repository_root / VALIDATOR_RELATIVE_PATH),
        },
        "canonical_v1_contract_validator_binding": {
            "identity": DU_VALIDATOR_IDENTITY,
            "path": DU_VALIDATOR_RELATIVE_PATH,
            "file_sha256": DU_VALIDATOR_SHA256,
        },
        "candidate_manifest_schema_binding": {
            "identity": DU_SCHEMA_IDENTITY,
            "path": DU_SCHEMA_RELATIVE_PATH,
            "file_sha256": DU_SCHEMA_SHA256,
        },
        "receipt_schema_binding": {
            "identity": RECEIPT_SCHEMA_IDENTITY,
            "path": RECEIPT_SCHEMA_RELATIVE_PATH,
            "file_sha256": sha256_path(repository_root / RECEIPT_SCHEMA_RELATIVE_PATH),
        },
        "validation_mode": VALIDATION_MODE,
        "validation_profile": VALIDATION_PROFILE,
        "canonical_argument_vector": argument_vector,
        "validation_command_identity_sha256": sha256_bytes(canonical_bytes(argument_vector)),
        "process_exit_status": 0,
        "gate_results": gates,
        "overall_result": "PASS",
        "required_head": required_head,
        "required_tree": required_tree,
        "receipt_is_authority": False,
        "auto_continuable": False,
    }
    return {
        "schema_id": RECEIPT_ENVELOPE_SCHEMA_ID,
        "receipt": receipt,
        "receipt_inner_sha256": sha256_bytes(canonical_bytes(receipt)),
    }


def _require_exact_fields(value: Any, expected: frozenset[str], field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        _fail("RECEIPT_SCHEMA_INVALID", f"{field} must be an object")
    missing = expected - value.keys()
    unknown = value.keys() - expected
    if missing:
        _fail("REQUIRED_RECEIPT_FIELD_ABSENT", f"{field} missing {sorted(missing)}")
    if unknown:
        _fail("UNKNOWN_RECEIPT_FIELD", f"{field} has unknown fields {sorted(unknown)}")
    return value


def _require_hash(value: Any, field: str) -> str:
    if not isinstance(value, str) or SHA256_RE.fullmatch(value) is None:
        _fail("RECEIPT_SCHEMA_INVALID", f"{field} must be lowercase SHA-256")
    return value


def _verify_implementation_binding(
    repository_root: Path,
    value: Any,
    field: str,
    *,
    expected_identity: str,
    expected_path: str,
    hash_error: str,
) -> None:
    binding = _require_exact_fields(
        value, frozenset({"identity", "path", "file_sha256"}), field
    )
    if binding["identity"] != expected_identity or binding["path"] != expected_path:
        _fail("IMPLEMENTATION_BINDING_MISMATCH", f"{field} identity or path differs")
    _, path = _repository_path(repository_root, binding["path"], f"{field}.path")
    expected_sha = _require_hash(binding["file_sha256"], f"{field}.file_sha256")
    if sha256_path(path) != expected_sha:
        _fail(hash_error, f"{field} file SHA-256 differs")


def verify_receipt_envelope(
    repository_root: Path, envelope: Any
) -> dict[str, str]:
    """Independently reauthenticate every candidate-bound PASS claim."""
    value = _require_exact_fields(
        envelope,
        frozenset({"schema_id", "receipt", "receipt_inner_sha256"}),
        "envelope",
    )
    if value["schema_id"] != RECEIPT_ENVELOPE_SCHEMA_ID:
        _fail("RECEIPT_SCHEMA_INVALID", "receipt envelope schema identity differs")
    receipt = _require_exact_fields(value["receipt"], RECEIPT_FIELDS, "receipt")
    embedded_inner = _require_hash(value["receipt_inner_sha256"], "receipt_inner_sha256")
    if sha256_bytes(canonical_bytes(receipt)) != embedded_inner:
        _fail("RECEIPT_INNER_HASH_MISMATCH", "receipt inner SHA-256 differs")
    if (
        receipt["schema_id"] != RECEIPT_SCHEMA_ID
        or receipt["receipt_version"] != RECEIPT_VERSION
        or receipt["generation_identity"] != GENERATION_IDENTITY
    ):
        _fail("RECEIPT_SCHEMA_INVALID", "receipt identity or version differs")
    if receipt["validation_mode"] != VALIDATION_MODE:
        _fail("SELF_TEST_SUBSTITUTION_REJECTED", "receipt is not candidate-validation mode")
    if receipt["validation_profile"] != VALIDATION_PROFILE:
        _fail("VALIDATION_PROFILE_INVALID", "receipt validation profile differs")
    if receipt["process_exit_status"] != 0:
        _fail("PROCESS_EXIT_STATUS_INVALID", "PASS receipt requires process exit status zero")
    if receipt["receipt_is_authority"] is not False or receipt["auto_continuable"] is not False:
        _fail("AUTHORITY_SEMANTICS_INVALID", "receipt cannot be authority or auto-continuable")
    if receipt["overall_result"] != "PASS":
        _fail("OVERALL_RESULT_INVALID", "candidate validation receipt is not PASS")

    gates = _require_exact_fields(receipt["gate_results"], frozenset(GATE_FIELDS), "gate_results")
    if any(gates[gate] != "PASS" for gate in GATE_FIELDS):
        _fail("OVERALL_PASS_WITH_NON_PASS_GATE", "overall PASS requires all four gates PASS")

    required_head = receipt["required_head"]
    required_tree = receipt["required_tree"]
    _authenticate_git_baseline(repository_root, required_head, required_tree)
    _verify_implementation_binding(
        repository_root,
        receipt["validator_binding"],
        "validator_binding",
        expected_identity=VALIDATOR_IDENTITY,
        expected_path=VALIDATOR_RELATIVE_PATH,
        hash_error="VALIDATOR_FILE_SHA256_MISMATCH",
    )
    _verify_implementation_binding(
        repository_root,
        receipt["canonical_v1_contract_validator_binding"],
        "canonical_v1_contract_validator_binding",
        expected_identity=DU_VALIDATOR_IDENTITY,
        expected_path=DU_VALIDATOR_RELATIVE_PATH,
        hash_error="DU_VALIDATOR_HASH_MISMATCH",
    )
    _verify_implementation_binding(
        repository_root,
        receipt["candidate_manifest_schema_binding"],
        "candidate_manifest_schema_binding",
        expected_identity=DU_SCHEMA_IDENTITY,
        expected_path=DU_SCHEMA_RELATIVE_PATH,
        hash_error="SCHEMA_FILE_SHA256_MISMATCH",
    )
    _verify_implementation_binding(
        repository_root,
        receipt["receipt_schema_binding"],
        "receipt_schema_binding",
        expected_identity=RECEIPT_SCHEMA_IDENTITY,
        expected_path=RECEIPT_SCHEMA_RELATIVE_PATH,
        hash_error="RECEIPT_SCHEMA_FILE_SHA256_MISMATCH",
    )

    candidate = _require_exact_fields(
        receipt["candidate_binding"],
        frozenset({"path", "file_sha256", "canonical_serialization_state"}),
        "candidate_binding",
    )
    _, candidate_path = _repository_path(
        repository_root, candidate["path"], "candidate_binding.path"
    )
    candidate_sha = _require_hash(candidate["file_sha256"], "candidate_binding.file_sha256")
    if sha256_path(candidate_path) != candidate_sha:
        _fail(
            "CANDIDATE_FILE_SHA256_MISMATCH",
            "candidate bytes differ from the validated candidate binding",
        )
    if candidate["canonical_serialization_state"] != "CANONICAL_V1_JSON":
        _fail("CANDIDATE_CANONICAL_STATE_INVALID", "candidate canonical state differs")

    expected_vector = _command_vector(candidate["path"], required_head, required_tree)
    if receipt["canonical_argument_vector"] != expected_vector:
        _fail("CANONICAL_ARGUMENT_VECTOR_MISMATCH", "canonical argument vector differs")
    command_identity = _require_hash(
        receipt["validation_command_identity_sha256"],
        "validation_command_identity_sha256",
    )
    if command_identity != sha256_bytes(canonical_bytes(expected_vector)):
        _fail("VALIDATION_COMMAND_IDENTITY_MISMATCH", "command identity differs")

    du = _load_du_validator(repository_root)
    _candidate_canonical_bytes(du, candidate_path)
    observed_gates = _gate_results(
        _run_du_validation(du, candidate_path, repository_root, required_head)
    )
    if observed_gates != gates:
        _fail("GATE_REAUTHENTICATION_MISMATCH", "recomputed gates differ")
    return {
        "candidate_binding_authenticity": "PASS",
        "validator_binding_authenticity": "PASS",
        "schema_binding_authenticity": "PASS",
        "git_head_tree_binding_authenticity": "PASS",
        "receipt_inner_authenticity": "PASS",
        "four_gate_reexecution": "PASS",
        "overall_result": "PASS",
    }


def verify_receipt_file(repository_root: Path, receipt_path: Path) -> dict[str, str]:
    raw = receipt_path.read_bytes()
    try:
        envelope = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ReceiptError("RECEIPT_JSON_INVALID", "receipt is not UTF-8 JSON") from exc
    if raw != canonical_bytes(envelope):
        _fail("RECEIPT_CANONICAL_SERIALIZATION_INVALID", "receipt bytes are not canonical JSON")
    return verify_receipt_envelope(repository_root, envelope)


def _rehash_receipt(envelope: dict[str, Any]) -> None:
    envelope["receipt_inner_sha256"] = sha256_bytes(canonical_bytes(envelope["receipt"]))


def _negative_case(
    case_id: str,
    expected_code: str,
    operation: Callable[[], None],
) -> dict[str, Any]:
    try:
        operation()
    except ReceiptError as exc:
        return {
            "case_id": case_id,
            "expected_rejection": expected_code,
            "observed_rejection": exc.code,
            "result": "PASS" if exc.code == expected_code else "FAIL",
        }
    return {
        "case_id": case_id,
        "expected_rejection": expected_code,
        "observed_rejection": "NOT_REJECTED",
        "result": "FAIL",
    }


def run_self_test(repository_root: Path, positive_fixture: Path) -> dict[str, Any]:
    """Run the EB positive fixture and all twelve required negative regressions."""
    required_head = _git(repository_root, "rev-parse", "HEAD")
    required_tree = _git(repository_root, "rev-parse", "HEAD^{tree}")
    positive = validate_candidate(
        repository_root,
        positive_fixture,
        required_head=required_head,
        required_tree=required_tree,
    )
    positive_verification = verify_receipt_envelope(repository_root, positive)
    cases: list[dict[str, Any]] = [{
        "case_id": "POSITIVE_CANONICAL_FIXTURE_PASS",
        "expected_result": "PASS",
        "observed_result": positive_verification["overall_result"],
        "result": "PASS",
    }]

    def mutated(mutator: Callable[[dict[str, Any]], None]) -> Callable[[], None]:
        def operation() -> None:
            value = deepcopy(positive)
            mutator(value)
            _rehash_receipt(value)
            verify_receipt_envelope(repository_root, value)
        return operation

    with tempfile.TemporaryDirectory(prefix=".g77_256eb_selftest_", dir=repository_root) as raw_tmp:
        temporary_root = Path(raw_tmp)
        changed_candidate = temporary_root / "candidate.json"
        changed_candidate.write_bytes(positive_fixture.read_bytes())
        changed_receipt = validate_candidate(
            repository_root,
            changed_candidate,
            required_head=required_head,
            required_tree=required_tree,
        )
        changed_candidate.write_bytes(changed_candidate.read_bytes() + b" ")
        cases.append(_negative_case(
            "CANDIDATE_BYTES_CHANGED_AFTER_VALIDATION",
            "CANDIDATE_FILE_SHA256_MISMATCH",
            lambda: verify_receipt_envelope(repository_root, changed_receipt),
        ))
        cases.append(_negative_case(
            "CANDIDATE_SHA_DOES_NOT_MATCH_RECEIPT",
            "CANDIDATE_FILE_SHA256_MISMATCH",
            mutated(lambda value: value["receipt"]["candidate_binding"].update(
                {"file_sha256": "0" * 64}
            )),
        ))
        cases.append(_negative_case(
            "VALIDATOR_SHA_DOES_NOT_MATCH",
            "VALIDATOR_FILE_SHA256_MISMATCH",
            mutated(lambda value: value["receipt"]["validator_binding"].update(
                {"file_sha256": "0" * 64}
            )),
        ))
        cases.append(_negative_case(
            "SCHEMA_SHA_DOES_NOT_MATCH",
            "SCHEMA_FILE_SHA256_MISMATCH",
            mutated(lambda value: value["receipt"]["candidate_manifest_schema_binding"].update(
                {"file_sha256": "0" * 64}
            )),
        ))
        cases.append(_negative_case(
            "REQUIRED_HEAD_MISMATCH",
            "REQUIRED_HEAD_MISMATCH",
            mutated(lambda value: value["receipt"].update({"required_head": "0" * 40})),
        ))
        cases.append(_negative_case(
            "REQUIRED_TREE_MISMATCH",
            "REQUIRED_TREE_MISMATCH",
            mutated(lambda value: value["receipt"].update({"required_tree": "0" * 40})),
        ))
        cases.append(_negative_case(
            "SELF_TEST_RESULT_SUBSTITUTED_FOR_CANDIDATE_VALIDATION",
            "SELF_TEST_SUBSTITUTION_REJECTED",
            mutated(lambda value: value["receipt"].update({"validation_mode": "SELF_TEST"})),
        ))

        ambiguous = subprocess.run(
            [
                sys.executable,
                str((repository_root / VALIDATOR_RELATIVE_PATH).resolve()),
                "--repo-root",
                str(repository_root),
                "--self-test",
                "--validate-candidate",
                str(positive_fixture),
            ],
            cwd=repository_root,
            text=True,
            capture_output=True,
            check=False,
        )
        ambiguous_output = ambiguous.stdout + ambiguous.stderr
        pass_claim_emitted = (
            '"candidate_validation_result":"PASS"' in ambiguous_output
            or '"overall_result":"PASS"' in ambiguous_output
        )
        cases.append({
            "case_id": "SELF_TEST_PLUS_VALIDATE_AMBIGUITY",
            "expected_rejection": "ARGPARSE_MUTUALLY_EXCLUSIVE_MODE_REJECTION",
            "observed_exit_status": ambiguous.returncode,
            "candidate_validation_pass_claim_emitted": pass_claim_emitted,
            "result": "PASS" if ambiguous.returncode == 2 and not pass_claim_emitted else "FAIL",
        })

        noncanonical = temporary_root / "noncanonical.json"
        noncanonical.write_text(
            json.dumps(json.loads(positive_fixture.read_bytes()), indent=2) + "\n",
            encoding="utf-8",
        )
        cases.append(_negative_case(
            "NON_CANONICAL_CANDIDATE_BYTES",
            "CANDIDATE_CANONICAL_SERIALIZATION_INVALID",
            lambda: validate_candidate(
                repository_root,
                noncanonical,
                required_head=required_head,
                required_tree=required_tree,
            ),
        ))
        cases.append(_negative_case(
            "MISSING_ONE_OF_FOUR_GATE_RESULTS",
            "REQUIRED_RECEIPT_FIELD_ABSENT",
            mutated(lambda value: value["receipt"]["gate_results"].pop(
                "manifest_semantic_compatibility_gate"
            )),
        ))
        cases.append(_negative_case(
            "OVERALL_PASS_WHILE_ANY_GATE_IS_NOT_PASS",
            "OVERALL_PASS_WITH_NON_PASS_GATE",
            mutated(lambda value: value["receipt"]["gate_results"].update(
                {"manifest_authenticity_gate": "FAIL"}
            )),
        ))

        def inner_hash_mismatch() -> None:
            value = deepcopy(positive)
            value["receipt_inner_sha256"] = "0" * 64
            verify_receipt_envelope(repository_root, value)

        cases.append(_negative_case(
            "RECEIPT_INNER_HASH_MISMATCH",
            "RECEIPT_INNER_HASH_MISMATCH",
            inner_hash_mismatch,
        ))

    aggregate = "PASS" if all(case["result"] == "PASS" for case in cases) else "FAIL"
    return {
        "schema_id": "G77_256EB_CANDIDATE_BOUND_VALIDATION_REGRESSION_EVIDENCE_V1",
        "test_mode": "SELF_TEST",
        "candidate_validation_result": "NOT_CLAIMED_BY_SELF_TEST",
        "positive_fixture_path": _relative_path(repository_root, positive_fixture),
        "positive_fixture_sha256": sha256_path(positive_fixture),
        "required_head": required_head,
        "required_tree": required_tree,
        "case_count": len(cases),
        "cases": cases,
        "self_test_plus_validate_ambiguity": "REJECTED_BEFORE_ANY_CANDIDATE_VALIDATION_PASS_CLAIM",
        "overall_self_test_result": aggregate,
        "auto_continuable": False,
    }


def _failure_output(error: ReceiptError) -> bytes:
    return canonical_bytes({
        "schema_id": "G77_256EB_CANDIDATE_VALIDATION_FAILURE_V1",
        "failure_code": error.code,
        "candidate_validation_pass_claimed": False,
        "overall_result": "FAIL_CLOSED",
    })


def main() -> int:
    parser = argparse.ArgumentParser(
        description="G77-256EB candidate-bound Canonical V1 validator and receipt verifier"
    )
    parser.add_argument(
        "--repo-root", type=Path, default=Path(__file__).resolve().parents[5]
    )
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--validate-candidate", type=Path)
    modes.add_argument("--verify-receipt", type=Path)
    modes.add_argument("--self-test", action="store_true")
    parser.add_argument("--receipt-output", type=Path)
    parser.add_argument("--evidence-output", type=Path)
    parser.add_argument("--positive-fixture", type=Path)
    parser.add_argument("--required-head")
    parser.add_argument("--required-tree")
    parser.add_argument("--validation-profile", default=VALIDATION_PROFILE)
    args = parser.parse_args()
    repository_root = args.repo_root.resolve()

    try:
        if args.validate_candidate is not None:
            if args.receipt_output is None or args.required_head is None or args.required_tree is None:
                parser.error(
                    "--validate-candidate requires --receipt-output, --required-head, and --required-tree"
                )
            if args.evidence_output is not None or args.positive_fixture is not None:
                parser.error("candidate-validation mode does not accept self-test outputs")
            envelope = validate_candidate(
                repository_root,
                args.validate_candidate,
                required_head=args.required_head,
                required_tree=args.required_tree,
                validation_profile=args.validation_profile,
            )
            args.receipt_output.write_bytes(canonical_bytes(envelope))
            print(canonical_bytes(envelope).decode(), end="")
            return 0
        if args.verify_receipt is not None:
            if any(value is not None for value in (
                args.receipt_output,
                args.evidence_output,
                args.positive_fixture,
                args.required_head,
                args.required_tree,
            )):
                parser.error("receipt-verification mode accepts no generation arguments")
            result = verify_receipt_file(repository_root, args.verify_receipt)
            print(canonical_bytes(result).decode(), end="")
            return 0
        if args.positive_fixture is None:
            parser.error("--self-test requires --positive-fixture")
        if any(value is not None for value in (
            args.receipt_output,
            args.required_head,
            args.required_tree,
        )):
            parser.error("self-test mode does not accept candidate-validation arguments")
        evidence = run_self_test(repository_root, args.positive_fixture)
        if args.evidence_output is not None:
            args.evidence_output.write_bytes(canonical_bytes(evidence))
        print(canonical_bytes(evidence).decode(), end="")
        return 0 if evidence["overall_self_test_result"] == "PASS" else 1
    except ReceiptError as exc:
        print(_failure_output(exc).decode(), end="")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
