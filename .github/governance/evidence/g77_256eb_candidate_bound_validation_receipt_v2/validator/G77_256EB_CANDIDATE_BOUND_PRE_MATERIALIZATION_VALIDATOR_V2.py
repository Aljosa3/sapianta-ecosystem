#!/usr/bin/env python3
"""Candidate-bound successor for the immutable DU Canonical V2 validator."""
from __future__ import annotations
import argparse
import ast
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
RECEIPT_ENVELOPE_SCHEMA_ID = "SAPIANTA_CANDIDATE_BOUND_VALIDATION_RECEIPT_ENVELOPE_V2"
RECEIPT_SCHEMA_ID = "SAPIANTA_CANDIDATE_BOUND_VALIDATION_RECEIPT_V2"
RECEIPT_VERSION = "2.0.0"
GENERATION_IDENTITY = (
    "G77_256EB_CANDIDATE_BOUND_PRE_MATERIALIZATION_VALIDATION_RECEIPT_HARDENING_V2"
)
VALIDATION_MODE = "CANDIDATE_VALIDATION"
VALIDATION_PROFILE = "CANONICAL_V2_PRE_MATERIALIZATION_FOUR_GATE_CANDIDATE_BOUND_V2"
VALIDATOR_IDENTITY = "G77_256EB_CANDIDATE_BOUND_PRE_MATERIALIZATION_VALIDATOR_V2"
DU_VALIDATOR_IDENTITY = "G77_256DU_PRE_MATERIALIZATION_CONSUMER_VALIDATOR_V2"
DU_SCHEMA_IDENTITY = "SAPIANTA_SPCE_CONTINUATION_MANIFEST_SCHEMA_V2"
RECEIPT_SCHEMA_IDENTITY = (
    "SAPIANTA_CANDIDATE_BOUND_PRE_MATERIALIZATION_VALIDATION_RECEIPT_SCHEMA_V2"
)
VALIDATOR_RELATIVE_PATH = (
    ".github/governance/evidence/g77_256eb_candidate_bound_validation_receipt_v2/"
    "validator/G77_256EB_CANDIDATE_BOUND_PRE_MATERIALIZATION_VALIDATOR_V2.py"
)
DU_VALIDATOR_RELATIVE_PATH = (
    ".github/governance/evidence/g77_256du_continuation_manifest_contract_v2/"
    "validator/G77_256DU_CONTINUATION_MANIFEST_COMPATIBILITY_VALIDATOR_V2.py"
)
DU_SCHEMA_RELATIVE_PATH = (
    ".github/governance/evidence/g77_256du_continuation_manifest_contract_v2/"
    "G77_256DU_CANONICAL_CONTINUATION_MANIFEST_SCHEMA_V2.json"
)
RECEIPT_SCHEMA_RELATIVE_PATH = (
    ".github/governance/evidence/g77_256eb_candidate_bound_validation_receipt_v2/"
    "G77_256EB_CANDIDATE_BOUND_VALIDATION_RECEIPT_SCHEMA_V2.json"
)
DU_VALIDATOR_SHA256 = "b7ac6207173cdf8d448db676ac9452a5df60cb695bba1379f6ab3a54df89734c"
DU_SCHEMA_SHA256 = "09a9124bba387903ec80778e515cf87d8277de6effba8a5715c0c0b1d0d2d57f"
FM_LAUNCHER_IDENTITY = "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1"
FM_LAUNCHER_RELATIVE_PATH = (
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/"
    "launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
IF_CONTEXT_IDENTITY = "G77_256IH_AUTHENTICATED_IF_RUNTIME_TARGET_CONTEXT_V1"
IF_CONTEXT_RELATIVE_PATH = (
    ".github/governance/evidence/g77_256ih_future_if_identity_rebind_v1/"
    "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
)
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
    "runtime_target_selection_binding",
    "validator_binding",
    "canonical_v2_contract_validator_binding",
    "candidate_manifest_schema_binding",
    "receipt_schema_binding",
    "validation_mode",
    "validation_profile",
    "canonical_argument_vector",
    "validation_command_identity_sha256",
    "process_exit_status",
    "gate_results",
    "overall_result",
    "certification_baseline",
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
def _duplicate_free_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            _fail("DUPLICATE_KEY", f"duplicate JSON key: {key}")
        value[key] = item
    return value
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
    spec = importlib.util.spec_from_file_location("g77_256du_validator_v2", path)
    if spec is None or spec.loader is None:
        _fail("DU_VALIDATOR_IMPORT_FAILED", "immutable DU validator could not be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
def _command_vector(candidate_path: str) -> list[str]:
    return [
        "--mode",
        VALIDATION_MODE,
        "--candidate",
        candidate_path,
        "--certification-baseline-current",
        "--profile",
        VALIDATION_PROFILE,
    ]
def _current_certification_baseline(repository_root: Path) -> dict[str, str]:
    head = _git(repository_root, "rev-parse", "HEAD")
    tree = _git(repository_root, "rev-parse", "HEAD^{tree}")
    return {"head": head, "tree": tree}
def _authenticate_git_baseline(
    repository_root: Path, baseline: Any
) -> tuple[str, str]:
    value = _require_exact_fields(
        baseline, frozenset({"head", "tree"}), "certification_baseline"
    )
    head = value["head"]
    tree = value["tree"]
    if not isinstance(head, str) or GIT_OBJECT_RE.fullmatch(head) is None:
        _fail("CERTIFICATION_BASELINE_HEAD_FORMAT_INVALID", "baseline head must be lowercase Git identity")
    if not isinstance(tree, str) or GIT_OBJECT_RE.fullmatch(tree) is None:
        _fail("CERTIFICATION_BASELINE_TREE_FORMAT_INVALID", "baseline tree must be lowercase Git identity")
    try:
        head_tree = _git(repository_root, "rev-parse", f"{head}^{{tree}}")
    except ReceiptError as exc:
        raise ReceiptError(
            "CERTIFICATION_BASELINE_COMMIT_NONEXISTENT",
            "baseline head is unavailable",
        ) from exc
    if head_tree != tree:
        _fail("CERTIFICATION_BASELINE_TREE_MISMATCH", "baseline tree does not belong to baseline head")
    actual = _current_certification_baseline(repository_root)
    if value != actual:
        _fail("CERTIFICATION_BASELINE_STALE", "receipt baseline is not the current certification repository")
    return head, tree
def _literal_assignment(tree: ast.Module, name: str) -> str:
    values = [
        node.value.value
        for node in tree.body
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == name for target in node.targets)
        and isinstance(node.value, ast.Constant)
        and isinstance(node.value.value, str)
    ]
    if len(values) != 1:
        _fail("RUNTIME_TARGET_LAUNCHER_BINDING_INVALID", f"launcher {name} is not unique")
    return values[0]
def _authenticated_runtime_target(repository_root: Path) -> dict[str, Any]:
    launcher = repository_root / FM_LAUNCHER_RELATIVE_PATH
    context_path = repository_root / IF_CONTEXT_RELATIVE_PATH
    for relative in (FM_LAUNCHER_RELATIVE_PATH, IF_CONTEXT_RELATIVE_PATH):
        try:
            committed_blob = _git(repository_root, "rev-parse", f"HEAD:{relative}")
            worktree_blob = _git(repository_root, "hash-object", relative)
        except ReceiptError as exc:
            raise ReceiptError(
                "RUNTIME_TARGET_SELECTION_GIT_PROVENANCE_INVALID",
                f"target-selection owner is not committed: {relative}",
            ) from exc
        if worktree_blob != committed_blob:
            _fail(
                "RUNTIME_TARGET_SELECTION_WORKTREE_DRIFT",
                f"target-selection owner differs from committed bytes: {relative}",
            )
    try:
        launcher_tree = ast.parse(launcher.read_text(encoding="utf-8"))
        context_raw = context_path.read_bytes()
        context = json.loads(context_raw, object_pairs_hook=_duplicate_free_object)
    except (OSError, UnicodeDecodeError, SyntaxError, json.JSONDecodeError) as exc:
        raise ReceiptError(
            "RUNTIME_TARGET_SELECTION_EVIDENCE_INVALID",
            "FM launcher or IF context could not be authenticated",
        ) from exc
    if context_raw != canonical_bytes(context):
        _fail("RUNTIME_TARGET_CONTEXT_NONCANONICAL", "IF context is not canonical JSON")
    inner = context.get("context_sha256")
    unsealed = {key: value for key, value in context.items() if key != "context_sha256"}
    if not isinstance(inner, str) or inner != sha256_bytes(canonical_bytes(unsealed)):
        _fail("RUNTIME_TARGET_CONTEXT_SEAL_INVALID", "IF context inner seal differs")
    head = _literal_assignment(launcher_tree, "CHECKOUT_HEAD")
    tree = _literal_assignment(launcher_tree, "CHECKOUT_TREE")
    checkout = context.get("qemu_executable_base_seed_checkout_bindings", {}).get("checkout", {})
    if (
        context.get("repository_head") != head
        or context.get("repository_tree") != tree
        or checkout.get("head") != head
        or checkout.get("tree") != tree
        or checkout.get("clean") is not True
        or checkout.get("detached") is not True
        or checkout.get("read_only_mount") is not True
    ):
        _fail("RUNTIME_TARGET_SELECTION_DISAGREEMENT", "FM launcher and IF context differ")
    if GIT_OBJECT_RE.fullmatch(head or "") is None or GIT_OBJECT_RE.fullmatch(tree or "") is None:
        _fail("RUNTIME_TARGET_FORMAT_INVALID", "runtime target is not a Git pair")
    try:
        observed_tree = _git(repository_root, "rev-parse", f"{head}^{{tree}}")
    except ReceiptError as exc:
        raise ReceiptError("RUNTIME_TARGET_COMMIT_NONEXISTENT", "runtime target is unavailable") from exc
    if observed_tree != tree:
        _fail("RUNTIME_TARGET_TREE_MISMATCH", "runtime target tree does not belong to head")
    return {
        "head": head,
        "tree": tree,
        "launcher_binding": {
            "identity": FM_LAUNCHER_IDENTITY,
            "path": FM_LAUNCHER_RELATIVE_PATH,
            "file_sha256": sha256_path(launcher),
        },
        "context_binding": {
            "identity": IF_CONTEXT_IDENTITY,
            "path": IF_CONTEXT_RELATIVE_PATH,
            "file_sha256": sha256_bytes(context_raw),
            "inner_sha256": inner,
        },
    }
def _candidate_canonical_bytes(du: ModuleType, candidate_path: Path) -> bytes:
    raw = candidate_path.read_bytes()
    value = du.load_json_bytes(raw)
    if raw != du.canonical_bytes(value):
        _fail(
            "CANDIDATE_CANONICAL_SERIALIZATION_INVALID",
            "candidate bytes are not canonical V2 JSON",
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
        code = getattr(exc, "code", "DU_CANONICAL_V2_VALIDATION_FAILED")
        raise ReceiptError(code, "DU Canonical V2 candidate validation failed") from exc
def validate_candidate(
    repository_root: Path,
    candidate: Path,
    *,
    validation_profile: str = VALIDATION_PROFILE,
) -> dict[str, Any]:
    """Validate one exact candidate and return a self-authenticating receipt."""
    if validation_profile != VALIDATION_PROFILE:
        _fail("VALIDATION_PROFILE_INVALID", "only the canonical EB profile is admissible")
    certification_baseline = _current_certification_baseline(repository_root)
    _authenticate_git_baseline(repository_root, certification_baseline)
    runtime_target = _authenticated_runtime_target(repository_root)
    candidate_relative = _relative_path(repository_root, candidate)
    _, candidate_path = _repository_path(
        repository_root, candidate_relative, "candidate_binding.path"
    )
    du = _load_du_validator(repository_root)
    raw = _candidate_canonical_bytes(du, candidate_path)
    du_result = _run_du_validation(
        du, candidate_path, repository_root, runtime_target["head"]
    )
    gates = _gate_results(du_result)
    argument_vector = _command_vector(candidate_relative)
    receipt = {
        "schema_id": RECEIPT_SCHEMA_ID,
        "receipt_version": RECEIPT_VERSION,
        "generation_identity": GENERATION_IDENTITY,
        "candidate_binding": {
            "path": candidate_relative,
            "file_sha256": sha256_bytes(raw),
            "canonical_serialization_state": "CANONICAL_V2_JSON",
        },
        "runtime_target_selection_binding": runtime_target,
        "validator_binding": {
            "identity": VALIDATOR_IDENTITY,
            "path": VALIDATOR_RELATIVE_PATH,
            "file_sha256": sha256_path(repository_root / VALIDATOR_RELATIVE_PATH),
        },
        "canonical_v2_contract_validator_binding": {
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
        "certification_baseline": certification_baseline,
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
    _authenticate_git_baseline(
        repository_root, receipt["certification_baseline"]
    )
    runtime_target = _authenticated_runtime_target(repository_root)
    if receipt["runtime_target_selection_binding"] != runtime_target:
        _fail(
            "RUNTIME_TARGET_SELECTION_BINDING_MISMATCH",
            "receipt runtime target differs from authenticated FM/IF selection",
        )
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
        receipt["canonical_v2_contract_validator_binding"],
        "canonical_v2_contract_validator_binding",
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
    if candidate["canonical_serialization_state"] != "CANONICAL_V2_JSON":
        _fail("CANDIDATE_CANONICAL_STATE_INVALID", "candidate canonical state differs")
    expected_vector = _command_vector(candidate["path"])
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
        _run_du_validation(du, candidate_path, repository_root, runtime_target["head"])
    )
    if observed_gates != gates:
        _fail("GATE_REAUTHENTICATION_MISMATCH", "recomputed gates differ")
    return {
        "candidate_binding_authenticity": "PASS",
        "validator_binding_authenticity": "PASS",
        "schema_binding_authenticity": "PASS",
        "git_head_tree_binding_authenticity": "PASS",
        "runtime_target_selection_binding_authenticity": "PASS",
        "receipt_inner_authenticity": "PASS",
        "four_gate_reexecution": "PASS",
        "overall_result": "PASS",
    }
def verify_receipt_file(repository_root: Path, receipt_path: Path) -> dict[str, str]:
    raw = receipt_path.read_bytes()
    try:
        envelope = json.loads(raw, object_pairs_hook=_duplicate_free_object)
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
    positive = validate_candidate(
        repository_root,
        positive_fixture,
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
            "CERTIFICATION_BASELINE_COMMIT_NONEXISTENT",
            "CERTIFICATION_BASELINE_COMMIT_NONEXISTENT",
            mutated(lambda value: value["receipt"]["certification_baseline"].update({"head": "0" * 40})),
        ))
        cases.append(_negative_case(
            "CERTIFICATION_BASELINE_TREE_MISMATCH",
            "CERTIFICATION_BASELINE_TREE_MISMATCH",
            mutated(lambda value: value["receipt"]["certification_baseline"].update({"tree": "0" * 40})),
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
        "schema_id": "G77_256EB_CANDIDATE_BOUND_VALIDATION_REGRESSION_EVIDENCE_V2",
        "test_mode": "SELF_TEST",
        "candidate_validation_result": "NOT_CLAIMED_BY_SELF_TEST",
        "positive_fixture_path": _relative_path(repository_root, positive_fixture),
        "positive_fixture_sha256": sha256_path(positive_fixture),
        "certification_baseline": _current_certification_baseline(repository_root),
        "case_count": len(cases),
        "cases": cases,
        "self_test_plus_validate_ambiguity": "REJECTED_BEFORE_ANY_CANDIDATE_VALIDATION_PASS_CLAIM",
        "overall_self_test_result": aggregate,
        "auto_continuable": False,
    }
def _failure_output(error: ReceiptError) -> bytes:
    return canonical_bytes({
        "schema_id": "G77_256EB_CANDIDATE_VALIDATION_FAILURE_V2",
        "failure_code": error.code,
        "candidate_validation_pass_claimed": False,
        "overall_result": "FAIL_CLOSED",
    })

V1_VALIDATOR_RELATIVE_PATH = (
    ".github/governance/evidence/g77_256eb_candidate_bound_validation_receipt_v1/"
    "validator/G77_256EB_CANDIDATE_BOUND_PRE_MATERIALIZATION_VALIDATOR_V1.py"
)
V1_VALIDATOR_SHA256 = "8e8171f757213f064cec463868408364175772e766615bd276ed7f0e28306b43"
DISPATCH_FIELDS = frozenset({
    "family", "schema_identity", "version", "validator_identity",
    "receipt_profile", "issuer_implementation_identity",
})
V1_CONTRACT_TUPLE = {
    "family": "EB",
    "schema_identity": "SAPIANTA_CANDIDATE_BOUND_PRE_MATERIALIZATION_VALIDATION_RECEIPT_SCHEMA_V1",
    "version": "1.0.0",
    "validator_identity": "G77_256EB_CANDIDATE_BOUND_PRE_MATERIALIZATION_VALIDATOR_V1",
    "receipt_profile": "CANONICAL_V1_PRE_MATERIALIZATION_FOUR_GATE_CANDIDATE_BOUND_V1",
    "issuer_implementation_identity": "G77_256EB_CANDIDATE_BOUND_PRE_MATERIALIZATION_VALIDATOR_V1",
}
V2_CONTRACT_TUPLE = {
    "family": "EB",
    "schema_identity": RECEIPT_SCHEMA_IDENTITY,
    "version": RECEIPT_VERSION,
    "validator_identity": VALIDATOR_IDENTITY,
    "receipt_profile": VALIDATION_PROFILE,
    "issuer_implementation_identity": VALIDATOR_IDENTITY,
}
def dispatch_verify_receipt(
    repository_root: Path, envelope: Any, *, contract_tuple: Any
) -> dict[str, str]:
    """Dispatch only an exact governed EB V1 or V2 identity tuple."""
    if not isinstance(contract_tuple, dict) or set(contract_tuple) != DISPATCH_FIELDS:
        _fail("DISPATCH_TUPLE_INVALID", "EB dispatch requires one closed governed tuple")
    if contract_tuple == V2_CONTRACT_TUPLE:
        return verify_receipt_envelope(repository_root, envelope)
    if contract_tuple == V1_CONTRACT_TUPLE:
        path = repository_root / V1_VALIDATOR_RELATIVE_PATH
        if sha256_path(path) != V1_VALIDATOR_SHA256:
            _fail("V1_VALIDATOR_HASH_MISMATCH", "immutable EB V1 validator bytes differ")
        spec = importlib.util.spec_from_file_location("g77_256eb_dispatch_v1", path)
        if spec is None or spec.loader is None:
            _fail("V1_VALIDATOR_IMPORT_FAILED", "immutable EB V1 validator could not load")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.verify_receipt_envelope(repository_root, envelope)
    _fail("DISPATCH_TUPLE_UNKNOWN", "unknown, mixed, downgraded, or cross-family EB tuple")

def main() -> int:
    parser = argparse.ArgumentParser(
        description="G77-256EB candidate-bound Canonical V2 validator and receipt verifier"
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
    parser.add_argument("--validation-profile", default=VALIDATION_PROFILE)
    args = parser.parse_args()
    repository_root = args.repo_root.resolve()
    try:
        if args.validate_candidate is not None:
            if args.receipt_output is None:
                parser.error("--validate-candidate requires --receipt-output")
            if args.evidence_output is not None or args.positive_fixture is not None:
                parser.error("candidate-validation mode does not accept self-test outputs")
            envelope = validate_candidate(
                repository_root,
                args.validate_candidate,
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
            )):
                parser.error("receipt-verification mode accepts no generation arguments")
            result = verify_receipt_file(repository_root, args.verify_receipt)
            print(canonical_bytes(result).decode(), end="")
            return 0
        if args.positive_fixture is None:
            parser.error("--self-test requires --positive-fixture")
        if args.receipt_output is not None:
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
