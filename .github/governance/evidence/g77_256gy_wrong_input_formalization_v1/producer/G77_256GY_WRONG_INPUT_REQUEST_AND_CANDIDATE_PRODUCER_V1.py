#!/usr/bin/env python3
"""Produce one isolated WRONG_INPUT request and one DU candidate instance."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
from types import ModuleType
from typing import Any, Mapping


sys.dont_write_bytecode = True
GENERATION_ID = "G77_256GY_REPOSITORY_ONLY_WRONG_INPUT_FORMALIZATION_V1"
CASE_ID = "G77_256GY_E05_WRONG_INPUT_DENIAL_BEFORE_ENTRY_001"
SELECTED_VECTOR = "P11-E05/NEGATIVE_AUTHORITY/WRONG_INPUT"
CANDIDATE_IDENTITY = "G77_256GY_WRONG_INPUT_CANONICAL_CANDIDATE_TEMPLATE_V1"
SPECIFICATION_INNER_SHA256 = (
    "434bcecf4665fb97be0095996f17927c5408e4597f77280f3c28172ee97af037"
)
TARGET_COORDINATE = "input_identity"
DEPENDENT_COORDINATES = ("record_identity",)
EXPECTED_DIFFERING_FIELDS = ("input_identity", "record_identity")
EXPECTED_DENIAL_BOUNDARY = (
    "D2_PRECLAIM_AUTHORITY_BINDING_VALIDATION_BEFORE_PRECLAIM_LEDGER_APPEND_"
    "CLAIM_ENTRY_INVOCATION_OR_EFFECT"
)
EXPECTED_ERROR_TYPE = "FailClosedRuntimeError"
EXPECTED_ERROR_REASON = "operational Human act input_record_identity binding is invalid"
IDENTITY_RE = re.compile(r"^[A-Z0-9][A-Z0-9_.:-]{7,255}$")

DU_PATH = Path(
    ".github/governance/evidence/g77_256du_continuation_manifest_contract_v1/"
    "validator/G77_256DU_CONTINUATION_MANIFEST_COMPATIBILITY_VALIDATOR_V1.py"
)
DU_SHA256 = "27457993a4e6b778cc65356cd9b17a1bf2665f4e6147608d27dc233ff512304d"
SUBSTRATE_PATH = Path("tests/p11_da_disposable_substrate_v1.py")
SUBSTRATE_SHA256 = "a1b58fa8ddedb5058393aa23d815262c92c8b185c0b193764f77420313af0bab"
SPECIFICATION_PATH = Path(
    ".github/governance/evidence/g77_256gy_wrong_input_formalization_v1/"
    "G77_256GY_WRONG_INPUT_FORMAL_SPECIFICATION_V1.json"
)
PRODUCER_PATH = Path(
    ".github/governance/evidence/g77_256gy_wrong_input_formalization_v1/producer/"
    "G77_256GY_WRONG_INPUT_REQUEST_AND_CANDIDATE_PRODUCER_V1.py"
)
REDUCER_PATH = Path(
    ".github/governance/evidence/g77_256gy_wrong_input_formalization_v1/reducer/"
    "G77_256GY_WRONG_INPUT_TERMINAL_ACCEPTANCE_REDUCER_V1.py"
)
GF_PATH = Path(
    ".github/governance/evidence/g77_256gf_post_commit_live_binding_v1/binding/"
    "G77_256GF_POST_COMMIT_LIVE_EXECUTION_BINDING_V1.py"
)
GN_PATH = Path(
    ".github/governance/evidence/g77_256gn_human_authorization_presentation_binding_v1/"
    "presentation/G77_256GN_SEALED_REQUEST_HUMAN_AUTHORIZATION_PRESENTATION_V1.py"
)
FM_PATH = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
GW_PATH = Path(
    ".github/governance/evidence/g77_256gw_host_checkpoint_serialization_boundary_v1/"
    "G77_256GW_FUTURE_HOST_CHECKPOINT_OWNER_BINDING_V1.md"
)
GX_PATH = Path(
    ".github/governance/evidence/g77_256gx_post_gw_readiness_v1/"
    "G77_256GX_SPCE_TERMINAL_FRONTIER_REDUCTION_V1.json"
)
EX_PATH = Path(
    ".github/governance/evidence/g77_256ex_common_substrate_certification_v1/"
    "G77_256EX_P11_SPCE_COMMON_SUBSTRATE_CERTIFICATION_V1.json"
)
G48_PATH = Path("docs/governance/G48_00_CONSTITUTIONAL_EVIDENCE_REPORTING_STANDARD_V1.md")


class WrongInputProducerError(ValueError):
    """One deterministic repository-only producer rejection."""


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_module(path: Path, identity: str) -> ModuleType:
    specification = importlib.util.spec_from_file_location(identity, path)
    if specification is None or specification.loader is None:
        raise WrongInputProducerError(f"MODULE_LOAD_FAILED__{identity}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


def authenticate_existing_owner(root: Path, path: Path, expected: str) -> None:
    if sha256_path(root / path) != expected:
        raise WrongInputProducerError(f"EXISTING_OWNER_HASH_MISMATCH__{path.name}")


def authenticate_formal_specification(root: Path) -> dict[str, Any]:
    envelope = json.loads((root / SPECIFICATION_PATH).read_bytes())
    if set(envelope) != {"schema_id", "specification", "specification_sha256"}:
        raise WrongInputProducerError("FORMAL_SPECIFICATION_ENVELOPE_INVALID")
    if envelope["schema_id"] != "G77_256GY_WRONG_INPUT_FORMAL_SPECIFICATION_ENVELOPE_V1":
        raise WrongInputProducerError("FORMAL_SPECIFICATION_SCHEMA_INVALID")
    inner = sha256_bytes(canonical_bytes(envelope["specification"]))
    if inner != envelope["specification_sha256"] or inner != SPECIFICATION_INNER_SHA256:
        raise WrongInputProducerError("FORMAL_SPECIFICATION_SEAL_INVALID")
    return envelope


def load_substrate(root: Path) -> ModuleType:
    authenticate_existing_owner(root, SUBSTRATE_PATH, SUBSTRATE_SHA256)
    return load_module(root / SUBSTRATE_PATH, "g77_256gy_existing_input_identity_owner")


def produce_wrong_input_request(
    *,
    repository_root: Path,
    authorized_input_canonical_bytes: bytes,
    wrong_input_identity: str,
    request_identity: str,
) -> dict[str, Any]:
    """Mutate only input_identity and recompute its dependent record identity."""

    root = repository_root.resolve()
    if IDENTITY_RE.fullmatch(wrong_input_identity) is None:
        raise WrongInputProducerError("WRONG_INPUT_IDENTITY_INVALID")
    if IDENTITY_RE.fullmatch(request_identity) is None:
        raise WrongInputProducerError("REQUEST_IDENTITY_INVALID")
    substrate = load_substrate(root)
    authorized = substrate.validate_input_record_bytes(authorized_input_canonical_bytes)
    if authorized[TARGET_COORDINATE] == wrong_input_identity:
        raise WrongInputProducerError("WRONG_INPUT_IDENTITY_NOT_DISTINCT")
    supplied_value = dict(authorized)
    supplied_value["record_identity"] = ""
    supplied_value[TARGET_COORDINATE] = wrong_input_identity
    supplied_bytes = substrate.bind_record_identity(supplied_value)
    supplied = substrate.validate_input_record_bytes(supplied_bytes)
    differing = tuple(
        sorted(key for key in authorized if authorized[key] != supplied[key])
    )
    if differing != EXPECTED_DIFFERING_FIELDS:
        raise WrongInputProducerError(
            f"WRONG_INPUT_MUTATION_NOT_ISOLATED__{','.join(differing)}"
        )
    preserved = {
        key: authorized[key] == supplied[key]
        for key in sorted(authorized)
        if key not in EXPECTED_DIFFERING_FIELDS
    }
    if not preserved or set(preserved.values()) != {True}:
        raise WrongInputProducerError("NON_TARGET_DIMENSION_CHANGED")
    return {
        "schema_id": "G77_256GY_WRONG_INPUT_REQUEST_V1",
        "case_id": CASE_ID,
        "selected_vector": SELECTED_VECTOR,
        "request_identity": request_identity,
        "target_mutated_coordinate": TARGET_COORDINATE,
        "dependent_recomputation_fields": list(DEPENDENT_COORDINATES),
        "semantic_mutation_count": 1,
        "authorized_input_record": authorized,
        "supplied_input_record": supplied,
        "authorized_input_canonical_utf8": authorized_input_canonical_bytes.decode("utf-8"),
        "supplied_input_canonical_utf8": supplied_bytes.decode("utf-8"),
        "differing_input_fields": list(differing),
        "preserved_dimension_proof": preserved,
        "expected_denial_boundary": EXPECTED_DENIAL_BOUNDARY,
        "expected_error_type": EXPECTED_ERROR_TYPE,
        "expected_error_reason": EXPECTED_ERROR_REASON,
        "request_is_authority": False,
        "request_is_operational_execution": False,
    }


def _git(root: Path, *arguments: str) -> str:
    return subprocess.check_output(["git", *arguments], cwd=root, text=True).strip()


def _lineage_binding(root: Path, identity: str, path: Path) -> dict[str, str]:
    relative = path.as_posix()
    return {
        "identity": identity,
        "path": relative,
        "sha256": sha256_path(root / path),
        "git_blob": _git(root, "rev-parse", f"HEAD:{relative}"),
    }


def _file_binding(root: Path, identity: str, path: Path) -> dict[str, str]:
    return {
        "identity": identity,
        "path": path.as_posix(),
        "sha256": sha256_path(root / path),
    }


def build_candidate(repository_root: Path) -> dict[str, Any]:
    """Build one current-checkpoint DU candidate from the existing DU owner."""

    root = repository_root.resolve()
    authenticate_existing_owner(root, DU_PATH, DU_SHA256)
    authenticate_formal_specification(root)
    du = load_module(root / DU_PATH, "g77_256gy_existing_du_owner")
    envelope = du.build_du_fixture(root)
    manifest = envelope["manifest"]
    manifest.update({
        "generation_identity": GENERATION_ID,
        "required_head": _git(root, "rev-parse", "HEAD"),
        "source_tree": _git(root, "rev-parse", "HEAD^{tree}"),
        "current_spce_phase": "PHASE_G_REPOSITORY_ONLY_WRONG_INPUT_FORMALIZATION_COMPLETE",
        "phase_sequence": 0,
        "prior_manifest_sha256": None,
        "completed_phase_seals": [],
        "case_counters": {
            "e05_case_execution_count": 0,
            "wrong_input_case_count": 0,
        },
        "authority_state": {
            "lifecycle_state": "NOT_CREATED",
            "act_identity": None,
            "owner_revision": None,
            "authority_survives": False,
            "transferable": False,
            "reusable": False,
        },
        "lineage_bindings": [
            _lineage_binding(root, "G77_256GX_TERMINAL_FRONTIER", GX_PATH),
            _lineage_binding(root, "G77_256EX_COMMON_SUBSTRATE_CERTIFICATE", EX_PATH),
            _lineage_binding(root, "G48_REPORTING_STANDARD", G48_PATH),
        ],
        "frontier_state": {
            "constitutional_frontier": "WRONG_INPUT_FORMALIZED__POST_COMMIT_LIVE_BINDING_REQUIRED",
            "exact_next_legal_action": "HUMAN_REVIEW_AND_OPTIONAL_COMMIT__THEN_REGENERATE_ONE_CURRENT_HEAD_WRONG_INPUT_LIVE_BINDING__NO_OPERATION",
            "continuation_mode": "HUMAN_REVIEW_ONLY",
            "requires_human_review": True,
        },
        "selected_case": {
            "case_class": "E05_NEGATIVE_AUTHORITY_WRONG_INPUT",
            "case_id": CASE_ID,
        },
        "first_failure_or_current_result": "PASS__WRONG_INPUT_REPOSITORY_FORMALIZATION__NO_OPERATION__NO_E05_CREDIT",
        "teardown_state": "NOT_APPLICABLE",
        "final_execution_seal": None,
        "observations": [
            f"CANDIDATE_IDENTITY__{CANDIDATE_IDENTITY}",
            f"FORMAL_SPECIFICATION_INNER_SHA256__{SPECIFICATION_INNER_SHA256}",
            "WRONG_INPUT_INPUT_IDENTITY_MUTATION_ONLY",
            "RECORD_IDENTITY_DEPENDENT_RECOMPUTATION_ONLY",
            "SEMANTIC_MUTATION_COUNT__ONE",
            "PRESERVED_NON_TARGET_DIMENSIONS_BOUND_BY_FORMAL_SPECIFICATION_HASH",
            f"EXPECTED_P11_DENIAL_BOUNDARY__{EXPECTED_DENIAL_BOUNDARY}",
            "EXPECTED_COUNTERS__REQUEST_1__P11_ENTRY_0__PROTECTED_INVOCATION_0__PROTECTED_EFFECT_0",
            "WRONG_ATTEMPT_SEMANTICS_PRESERVED",
            "CANDIDATE_SEMANTICS_CHANGED_GUARD_REQUIRED",
            "BINDING_CLASSIFICATION__NEW_VECTOR_SPECIFIC_BINDING_OWNER_REQUIRED__GF_PATTERN_REUSED_WITHOUT_GF_GENERALIZATION",
            "POST_COMMIT_LIVE_BINDING_REQUIRED",
            "REQUEST_NOT_ENTRY_NOT_INVOCATION_NOT_EFFECT",
            "E05_REMAINS_SEVEN_OF_EIGHTEEN",
        ],
        "extension_bindings": [
            _file_binding(root, "G77_256GY_WRONG_INPUT_FORMAL_SPECIFICATION", SPECIFICATION_PATH),
            _file_binding(root, "G77_256GY_WRONG_INPUT_REQUEST_AND_CANDIDATE_PRODUCER", PRODUCER_PATH),
            _file_binding(root, "G77_256GY_WRONG_INPUT_TERMINAL_ACCEPTANCE_REDUCER", REDUCER_PATH),
            _file_binding(root, "G77_256GF_REPOSITORY_IDENTITY_REBINDING_MECHANICS", GF_PATH),
            _file_binding(root, "G77_256GN_AUTHORITY_PRESENTATION_OWNER", GN_PATH),
            _file_binding(root, "G77_256FM_EXISTING_LAUNCHER_OWNER", FM_PATH),
            _file_binding(root, "G77_256GW_HOST_CHECKPOINT_OWNER_BINDING", GW_PATH),
        ],
    })
    envelope["manifest_sha256"] = sha256_bytes(canonical_bytes(manifest))
    du.validate_envelope(envelope, root, expected_head=manifest["required_head"])
    return envelope


if __name__ == "__main__":
    raise SystemExit("repository-only module; invoke through focused tests or the post-commit binder")
