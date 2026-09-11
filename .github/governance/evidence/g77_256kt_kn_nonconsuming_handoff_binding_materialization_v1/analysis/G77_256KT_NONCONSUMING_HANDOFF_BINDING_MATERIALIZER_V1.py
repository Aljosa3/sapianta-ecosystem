#!/usr/bin/env python3
"""Materialize and verify the exact nonconsuming KN handoff and FM binding.

This controller delegates canonical authority serialization and binding to the
existing FM owners.  It has no consumption or operational entrypoint.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
KT = ROOT / ".github/governance/evidence/g77_256kt_kn_nonconsuming_handoff_binding_materialization_v1"
OUTPUT = KT / "G77_256KT_SPCE_TERMINAL_PRECONSUMPTION_MATERIALIZATION_V1.json"
KN = ROOT / ".github/governance/evidence/g77_256kn_fresh_expired_operational_recommissioning_v1"
SOURCE = KN / "G77_256KN_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt"
REQUEST = KN / "G77_256KN_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
AUTH_PRESENTATION = KN / "G77_256KN_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt"
DECISION_PRESENTATION = KN / "G77_256KN_HUMAN_DECISION_PRESENTATION_V1.txt"
CONTEXT = KN / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
CANDIDATE = KN / "live_binding/candidate/G77_256GD_CANONICAL_CONTINUATION_MANIFEST_BINDING_REISSUE_V1.json"
HANDOFF = KN / "G77_256KN_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json"
BINDING = KN / "G77_256KN_PRECONSUMPTION_INVOCATION_BINDING_V1.json"
CONSUMPTION = KN / "G77_256KN_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1.json"
INVOCATION = KN / "G77_256KN_FM_OPERATIONAL_INVOCATION_ATTEMPT_V1.json"
RESULT = KN / "G77_256KN_FM_OPERATIONAL_INVOCATION_RESULT_V1.json"
PHASE_B_CHECKPOINT = KN / "G77_256KN_PHASE_B_PRECONSUMPTION_READINESS_CHECKPOINT_V1.json"
KO_INSTRUCTION = ROOT / ".github/governance/evidence/g77_256ko_exact_human_source_authentication_bridge_v1/G77_256KO_DIRECT_HUMAN_ACT_INSTRUCTION_V1.txt"
KS_REDUCTION = ROOT / ".github/governance/evidence/g77_256ks_existing_kn_authority_authentication_binding_readiness_v1/G77_256KS_CANONICAL_BINDING_READINESS_V1.json"
FM_PATH = ROOT / ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
KA_CONTROLLER = ROOT / ".github/governance/evidence/g77_256ka_fresh_expired_operational_recommissioning_v1/orchestration/G77_256KA_PHASE_B_CONTROLLER_V1.py"
KG_CONTROLLER = ROOT / ".github/governance/evidence/g77_256kg_fresh_expired_operational_recommissioning_v1/orchestration/G77_256KG_PHASE_B_CONTROLLER_V1.py"
KE_CONTROLLER = ROOT / ".github/governance/evidence/g77_256ke_fresh_expired_operational_recommissioning_v1/orchestration/G77_256KE_PHASE_B_CONTROLLER_V1.py"
JZ_FORMALIZER = ROOT / ".github/governance/evidence/g77_256jz_fm_authority_digest_handoff_repair_v1/analysis/G77_256JZ_PRECONSUMPTION_INVOCATION_BINDING_FORMALIZER_V1.py"
KA_PRECONSUMPTION = ROOT / ".github/governance/evidence/g77_256ka_fresh_expired_operational_recommissioning_v1/G77_256KA_PHASE_B_PRECONSUMPTION_READINESS_CHECKPOINT_V1.json"
KA_CONSUMPTION = ROOT / ".github/governance/evidence/g77_256ka_fresh_expired_operational_recommissioning_v1/G77_256KA_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1.json"
KG_PRECONSUMPTION = ROOT / ".github/governance/evidence/g77_256kg_fresh_expired_operational_recommissioning_v1/G77_256KG_PHASE_B_PRECONSUMPTION_READINESS_CHECKPOINT_V1.json"

HEAD = "55b93edd1e0680f0e2bbe78e4b863557e04c1428"
TREE = "3a328c540352acf6ba3df69e1c811b50f7a4b28d"
SUBJECT = "G77-256KS authenticate KN authority and verify binding readiness"
BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
ANCHOR = "5c972e9960987ab27420395b54ace693df097e7b"
GENERATION = "G77_256KN_ONE_FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATIONAL_COMMISSIONING_V1"
OPERATION = "G77_256KN_E05_EXPIRED_DENIAL_BEFORE_ENTRY_001"
CANDIDATE_SHA256 = "8af5ba1cbf9e396aa2f4f981a6f20b821c5fd1c38e091ed1cb3646c76c953b4a"
CONTEXT_SHA256 = "37f5c7d46b305b6e6e6b912dd136917c96ad4c783341aa62cd1dc4994e6f5b4b"
CONTEXT_FILE_SHA256 = "adafd6cdc2bef25119e098e11a69a79cdc893656bc9471f72e4e6a85ca5e7695"
CANONICAL_ARGV_SHA256 = "96480352c744c6feb9d743fafc7eae111a143ebde6b18cf67160e05ac1e93816"
TEMPORAL_BINDING_SHA256 = "cc46cded2aa3c294ad84c172619092889639fb74dda5f32ec68645508a2a1f56"
REQUEST_SHA256 = "9c5941b007e5939da928b7e1cc6cf0668a8e20b29f75bbe29964520645eb57d5"
REQUEST_FILE_SHA256 = "f980e8cd5ac48c97bbc61a0f891f103e8305f14847a59333b39912024609831d"
AUTH_PRESENTATION_SHA256 = "71cc222249ad75b2b420d749c2d4bd66cf0bd2d982f054102384ddb14993e2ac"
DECISION_PRESENTATION_SHA256 = "9b95f4ad710b607b0c8607da4b2b720d5e8bf94929f4f39dc4e121cc5b5f2f12"
SOURCE_SHA256 = "56a50ef8a69761e492138d4f9f425eb2e845231bd654a731ead02fcbc34fdc96"
KS_FILE_SHA256 = "8a52f07e54fc25da7c887c5e9fba47cb3fd0a73a1e40c0cd92c97cda2dbe2f3e"
KS_INNER_SHA256 = "e5e3aaea56d1a38eb83ec2a9485eb86b6cf7e6b517822203aa440e8f670caea0"
FM_FILE_SHA256 = "e1db7e6d59d81a85ee025b27c3145abe697c1097822694498a4ad686d2406c51"
KA_CONTROLLER_SHA256 = "44cde7913d6fef0a3c48cb7b96b82e7b79605c94a963f2acd0f36b0b0f80e34e"
KG_CONTROLLER_SHA256 = "ba0cb126e0548b6dccf9b2ad353e9cf8b251493085a81079d7e823285cb5297e"
KE_CONTROLLER_SHA256 = "fbbf896c53d05330cd8ef8b8b1a1b3219ca0c3ffa6f6a5fa08b1ded22c4fc8b9"
JZ_FORMALIZER_SHA256 = "3832d64c3e071bfe66926cd545c8fd13d133284fcfe7d40c568b1dfebb9340c5"
KA_PRECONSUMPTION_SHA256 = "d4dac52eace114cdb055c6bf6e0285e56d72d9928182221f71921958c7c35479"
KA_CONSUMPTION_SHA256 = "0f66cd9b094b2ae973ce2cc06cea9a651715046bde57b22db4a17a077b4ab3a5"
KG_PRECONSUMPTION_SHA256 = "0a17fd2cfda793c71c1b89c56d043476746fec84b0bdb6db2ecd86c4cb222cde"
HANDOFF_SHA256 = "f220a240d54c38ecba24fcc2ffd6c9c37b1cc11a69baac5f913964b0d5cff4ae"
AUTHORIZATION_INNER_SHA256 = "e1e21562553bd9b93bbb144336e0baa0fd1fdfc554e62cd65b5e08c6cae5e7c9"
BINDING_FILE_SHA256 = "15b92bd8e07bea489c8128826a7757404489a2ecb1204c963f391a9a992e4135"
BINDING_INNER_SHA256 = "234858e580d12c15f31e4258dd6c3664836c8b4f355d66239294400db4f2fe72"
TERMINAL = "A__KT_EXACT_NONCONSUMING_KN_CANONICAL_HANDOFF_AND_PRECONSUMPTION_BINDING_MATERIALIZED__AUTHORITY_UNCONSUMED__NO_PHASE_B__NO_OPERATION"

GN_FIELDS = {
    "all_operational_counters_zero", "checkpoint_file_sha256",
    "checkpoint_inner_sha256", "checkpoint_path", "complete_deterministic_readiness",
    "gk_receipt_parent_false_positive_blocked", "preauth_final_admission_equivalence",
    "preauth_final_admission_equivalence_file_sha256",
    "receipt_parent_observation_file_sha256", "static_readiness_file_sha256",
}


class KTMaterializationError(RuntimeError):
    """Stable fail-closed KT materialization failure."""


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*arguments: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(["git", *arguments], cwd=cwd, text=True).strip()


def load_envelope(path: Path, inner: str) -> dict[str, Any]:
    raw = path.read_bytes()
    envelope = json.loads(raw)
    if not isinstance(envelope, dict) or raw != canonical_bytes(envelope):
        raise KTMaterializationError(f"NONCANONICAL_JSON:{path.name}")
    value = envelope.get(inner)
    if not isinstance(value, dict) or envelope.get(f"{inner}_sha256") != hashlib.sha256(canonical_bytes(value)).hexdigest():
        raise KTMaterializationError(f"SEAL_MISMATCH:{path.name}")
    return value


def load_fm() -> Any:
    if sha256_path(FM_PATH) != FM_FILE_SHA256:
        raise KTMaterializationError("FM_OWNER_IMMUTABILITY_FAILURE")
    spec = importlib.util.spec_from_file_location("g77_256kt_fm_owner", FM_PATH)
    if spec is None or spec.loader is None:
        raise KTMaterializationError("FM_OWNER_IMPORT_FAILURE")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def exact_human_bytes() -> bytes:
    text = KO_INSTRUCTION.read_text(encoding="utf-8")
    begin = "--- BEGIN EXACT HUMAN-SOURCE BYTES ---\n"
    end = "--- END EXACT HUMAN-SOURCE BYTES ---\n"
    if text.count(begin) != 1 or text.count(end) != 1:
        raise KTMaterializationError("KO_SOURCE_MARKERS_INVALID")
    return text.split(begin, 1)[1].split(end, 1)[0].encode("utf-8")


def authenticate_worktree_scope(*, materialized: bool) -> None:
    """Reject tracked drift and every untracked path outside the bounded KT set."""

    source_name = SOURCE.relative_to(ROOT).as_posix()
    handoff_name = HANDOFF.relative_to(ROOT).as_posix()
    binding_name = BINDING.relative_to(ROOT).as_posix()
    kt_prefix = KT.relative_to(ROOT).as_posix() + "/"
    allowed_exact = {source_name, handoff_name, binding_name}
    for line in git("status", "--porcelain=v1", "--untracked-files=all").splitlines():
        if not line:
            continue
        status, name = line[:2], line[3:]
        if status != "??" or (name not in allowed_exact and not name.startswith(kt_prefix)):
            raise KTMaterializationError(f"KT_BOUNDED_WORKTREE_SCOPE_VIOLATION:{line}")


def zero_counters() -> dict[str, int]:
    return {
        "operational_authorization_count": 0, "authority_consumption_count": 0,
        "pre_operational_invocation_count": 0, "fm_operational_invocation_count": 0,
        "qemu_start_count": 0, "vm_start_count": 0, "operation_attempt_count": 0,
        "operation_request_count": 0, "expired_denial_count": 0, "p11_entry_count": 0,
        "protected_invocation_count": 0, "protected_effect_count": 0,
        "retry_count": 0, "repair_retry_count": 0, "replay_count": 0,
    }


def build_authorization(context: dict[str, Any], fm: Any) -> dict[str, Any]:
    return {
        "schema_id": fm.AUTHORIZATION_SCHEMA, "authorization_present": True,
        "authorization_kind": "FRESH_HUMAN_OPERATIONAL_AUTHORIZATION",
        "authorization_source_sha256": SOURCE_SHA256,
        "authorized_context_sha256": CONTEXT_SHA256,
        "authorized_operation_identity": OPERATION,
        "authorized_generation_identity": GENERATION, "authorized_vector": "EXPIRED",
        "authorized_repository_head": context["repository_head"],
        "authorized_repository_tree": context["repository_tree"],
        "authorized_constitutional_anchor_head": ANCHOR,
        "authorized_candidate_sha256": CANDIDATE_SHA256,
        "authorized_canonical_argv_sha256": CANONICAL_ARGV_SHA256,
        "authorized_wrapper_sha256": context["wrapper_fc_er_che_schema_hashes"]["wrapper"],
        "authorized_fk_adapter_sha256": fm.FK_ADAPTER_SHA256,
        "vm_boot_limit": 1, "qemu_system_execution_limit": 1,
        "expired_operational_attempt_limit": 1, "retry_limit": 0,
        "repair_limit": 0, "replay_limit": 0,
        "receipt_namespace_must_be_unconsumed": True, "network_authorized": False,
        "provider_authorized": False, "trusted_access_authorized": False,
        "authorization_reusable": False, "auto_continuable": False,
    }


def authenticate_common(*, materialized: bool) -> tuple[Any, dict[str, Any]]:
    if (
        git("branch", "--show-current") != BRANCH or git("remote", "get-url", "origin") != ORIGIN
        or git("rev-parse", "HEAD") != HEAD or git("rev-parse", "HEAD^{tree}") != TREE
        or git("log", "-1", "--format=%s") != SUBJECT or git("diff", "--name-only")
        or git("diff", "--cached", "--name-only")
    ):
        raise KTMaterializationError("KS_ENTRY_CHECKPOINT_MISMATCH")
    if subprocess.run(["git", "merge-base", "--is-ancestor", ANCHOR, "HEAD"], cwd=ROOT, check=False).returncode:
        raise KTMaterializationError("STABLE_ANCESTRY_MISMATCH")
    authenticate_worktree_scope(materialized=materialized)
    nested = ROOT / "sapianta_system"
    if (
        git("remote", "get-url", "origin", cwd=nested) != "git@github.com:Aljosa3/sapianta-core.git"
        or git("rev-parse", "HEAD", cwd=nested) != "3183bab71f8f30397c0309dd2e6d846d14a11f66"
        or git("rev-parse", "HEAD^{tree}", cwd=nested) != "7c32ec05efc2be43297849bc38ec8766514a523d"
        or git("branch", "--show-current", cwd=nested) or git("status", "--short", cwd=nested)
        or git("describe", "--tags", "--exact-match", "HEAD", cwd=nested) != "sapianta-system-nested-authority-3183bab-v1"
    ):
        raise KTMaterializationError("NESTED_AUTHORITY_MISMATCH")
    source = SOURCE.read_bytes()
    if (
        len(source) != 1213 or source.count(b"\n") != 14
        or hashlib.sha256(source).hexdigest() != SOURCE_SHA256
        or source.startswith(b"\xef\xbb\xbf") or not source.endswith(b"\n")
        or source != exact_human_bytes() or git("ls-files", "--", SOURCE.relative_to(ROOT).as_posix())
    ):
        raise KTMaterializationError("HUMAN_SOURCE_IMMUTABILITY_FAILURE")
    source.decode("utf-8")

    ks = load_envelope(KS_REDUCTION, "readiness")
    if (
        sha256_path(KS_REDUCTION) != KS_FILE_SHA256
        or json.loads(KS_REDUCTION.read_bytes()).get("readiness_sha256") != KS_INNER_SHA256
        or ks.get("terminal") != "A__KS_EXISTING_KN_HUMAN_AUTHORITY_AUTHENTICATED_AND_CANONICAL_BINDING_READY__UNCONSUMED__NO_PHASE_B__NO_OPERATION"
        or ks.get("human_authority", {}).get("human_source_decision_status") != "VERIFIED__EXACT_EXISTING_KN_HUMAN_DECISION_OBJECT"
        or ks.get("human_authority", {}).get("human_authority_authentication") != "VERIFIED__EXACT_EXISTING_KN_HUMAN_AUTHORITY_AUTHENTICATED__UNBOUND__UNCONSUMED"
        or ks.get("human_authority", {}).get("human_authority_binding_readiness") != "VERIFIED__EXACT_CANONICAL_FM_HANDOFF_SHAPE_AND_DIGEST_READY__NO_HANDOFF_FILE_PERSISTED"
        or ks.get("human_authority", {}).get("human_authority_binding") != "NOT_APPLICABLE__KS_PROVES_READINESS_ONLY_AND_PERSISTS_NO_AUTHORITY_HANDOFF"
        or ks.get("binding_readiness", {}).get("projected_canonical_handoff_file_sha256") != HANDOFF_SHA256
        or ks.get("binding_readiness", {}).get("projected_authorization_inner_sha256") != AUTHORIZATION_INNER_SHA256
        or ks.get("binding_readiness", {}).get("projected_canonical_byte_count") != 1715
        or any(ks.get("operational_counters", {}).values()) or ks.get("phase_b_started") is not False
    ):
        raise KTMaterializationError("KS_TERMINAL_OR_PROJECTION_MISMATCH")

    expected_files = {
        CONTEXT: CONTEXT_FILE_SHA256, CANDIDATE: CANDIDATE_SHA256,
        REQUEST: REQUEST_FILE_SHA256, AUTH_PRESENTATION: AUTH_PRESENTATION_SHA256,
        DECISION_PRESENTATION: DECISION_PRESENTATION_SHA256,
        KA_CONTROLLER: KA_CONTROLLER_SHA256, KG_CONTROLLER: KG_CONTROLLER_SHA256,
        KE_CONTROLLER: KE_CONTROLLER_SHA256,
        JZ_FORMALIZER: JZ_FORMALIZER_SHA256,
        KA_PRECONSUMPTION: KA_PRECONSUMPTION_SHA256,
        KA_CONSUMPTION: KA_CONSUMPTION_SHA256,
        KG_PRECONSUMPTION: KG_PRECONSUMPTION_SHA256,
    }
    if any(sha256_path(path) != expected for path, expected in expected_files.items()):
        raise KTMaterializationError("IMMUTABLE_MECHANISM_OR_KN_COORDINATE_MISMATCH")
    request_envelope = json.loads(REQUEST.read_bytes())
    request = load_envelope(REQUEST, "request")
    context = json.loads(CONTEXT.read_bytes())
    if (
        request_envelope.get("request_sha256") != REQUEST_SHA256
        or set(request.get("preauthorization", {})) != GN_FIELDS
        or len(request.get("preauthorization", {})) != 10
        or context.get("generation_identity") != GENERATION or context.get("operation_identity") != OPERATION
        or context.get("context_sha256") != CONTEXT_SHA256
        or context.get("canonical_argv_sha256") != CANONICAL_ARGV_SHA256
        or context.get("candidate_manifest_sha256") != CANDIDATE_SHA256
        or hashlib.sha256(canonical_bytes(context["preclaim_temporal_binding"])).hexdigest() != TEMPORAL_BINDING_SHA256
    ):
        raise KTMaterializationError("KN_COORDINATE_OR_GN_SCHEMA_MISMATCH")

    ka = KA_CONTROLLER.read_text(encoding="utf-8")
    kg = KG_CONTROLLER.read_text(encoding="utf-8")
    ke = KE_CONTROLLER.read_text(encoding="utf-8")
    jz = JZ_FORMALIZER.read_text(encoding="utf-8")
    if not (
        "def prepare(" in ka and "def consume_and_operate(" in ka
        and ka.index("def prepare(") < ka.index("def consume_and_operate(")
        and "FM.write_authority_handoff(HANDOFF" in ka
        and "persist(BINDING, envelope)" in ka
        and '"authority_state": "GRANTED_UNCONSUMED"' in ka
        and '"authority_state_before": "GRANTED_UNCONSUMED", "authority_state_after": "CONSUMED"' in ka
    ):
        raise KTMaterializationError("KA_PREPARE_CONSUMPTION_SEPARATION_NOT_PROVEN")
    if not (
        'BASE_SHA256 = "f950bb6ee2165169e1598c3d95ceff1cf719ed0a259421f48189ee9de4a14aad"' in ke
        and "C.prepare(arguments)" in ke and "C.consume_and_operate(arguments)" in ke
    ):
        raise KTMaterializationError("KE_ADAPTED_PREPARE_CONSUMPTION_SEPARATION_NOT_PROVEN")
    if not (
        "load_adapted_ke_controller" in kg
        and 'BASE_SHA256 = "fbbf896c53d05330cd8ef8b8b1a1b3219ca0c3ffa6f6a5fa08b1ded22c4fc8b9"' in kg
        and "C.prepare(arguments)" in kg
        and "C.consume_and_operate(arguments)" in kg
    ):
        raise KTMaterializationError("KG_ADAPTED_PREPARE_CONSUMPTION_SEPARATION_NOT_PROVEN")
    if not (
        "does not create or consume Human authority" in jz
        and "or start a\nprocess" in jz
        and "fm.build_preconsumption_invocation_binding(" in jz
        and "fm.validate_preconsumption_invocation_binding(" in jz
    ):
        raise KTMaterializationError("JZ_NONCONSUMING_BINDER_PROOF_MISMATCH")
    ka_pre = load_envelope(KA_PRECONSUMPTION, "checkpoint")
    ka_consumed = load_envelope(KA_CONSUMPTION, "checkpoint")
    kg_pre = load_envelope(KG_PRECONSUMPTION, "checkpoint")
    if (
        ka_pre.get("authority_state") != "GRANTED_UNCONSUMED"
        or ka_pre.get("operational_counters", {}).get("authority_consumption_count") != 0
        or ka_pre.get("operational_counters", {}).get("fm_operational_invocation_count") != 0
        or ka_consumed.get("authority_state_before") != "GRANTED_UNCONSUMED"
        or ka_consumed.get("authority_state_after") != "CONSUMED"
        or ka_consumed.get("operational_counters", {}).get("authority_consumption_count") != 1
        or kg_pre.get("authority_state") != "GRANTED_UNCONSUMED"
        or kg_pre.get("operational_counters", {}).get("authority_consumption_count") != 0
        or kg_pre.get("operational_counters", {}).get("fm_operational_invocation_count") != 0
    ):
        raise KTMaterializationError("PERSISTED_PREPARE_BEFORE_CONSUMPTION_PRECEDENT_MISMATCH")

    expected_presence = (
        HANDOFF.exists() or HANDOFF.is_symlink(),
        BINDING.exists() or BINDING.is_symlink(),
    )
    if expected_presence != ((True, True) if materialized else (False, False)):
        raise KTMaterializationError("HANDOFF_BINDING_NAMESPACE_STATE_MISMATCH")
    if any(path.exists() or path.is_symlink() for path in (CONSUMPTION, INVOCATION, RESULT, PHASE_B_CHECKPOINT)):
        raise KTMaterializationError("CONSUMPTION_OR_OPERATION_NAMESPACE_COLLISION")

    fm = load_fm()
    authorization = build_authorization(context, fm)
    projected = fm.canonical_authority_handoff_bytes(authorization)
    if (
        len(projected) != 1715 or hashlib.sha256(projected).hexdigest() != HANDOFF_SHA256
        or fm.parse_authority_handoff_bytes(projected).get("authorization_sha256") != AUTHORIZATION_INNER_SHA256
    ):
        raise KTMaterializationError("KS_CANONICAL_PROJECTION_MISMATCH")
    return fm, context


def verify_materialized(fm: Any) -> dict[str, Any]:
    handoff, handoff_digest = fm.load_authority(HANDOFF)
    raw = HANDOFF.read_bytes()
    if (
        len(raw) != 1715 or handoff_digest != HANDOFF_SHA256
        or handoff.get("authorization_sha256") != AUTHORIZATION_INNER_SHA256
        or fm.parse_authority_handoff_bytes(raw) != handoff
    ):
        raise KTMaterializationError("MATERIALIZED_HANDOFF_MISMATCH")
    binding_envelope = json.loads(BINDING.read_bytes())
    if BINDING.read_bytes() != canonical_bytes(binding_envelope):
        raise KTMaterializationError("BINDING_NONCANONICAL")
    binding = fm.validate_preconsumption_invocation_binding(
        repository_root=ROOT, operation_context=CONTEXT,
        live_candidate_binding=CANDIDATE, execution_authority=HANDOFF,
        envelope=binding_envelope,
    )
    digest_values = {
        binding["authenticated_canonical_authority_digest"],
        binding["sealed_invocation_authority_digest"],
        binding["final_fm_argv_authority_digest"], handoff_digest,
    }
    if (
        digest_values != {HANDOFF_SHA256} or binding.get("authority_consumption_count") != 0
        or binding.get("fm_operational_invocation_count") != 0
        or binding.get("binding_is_authority") is not False
        or binding.get("execution_authorized_by_binding") is not False
        or binding.get("process_started") is not False
        or binding.get("caller_digest_input_count") != 0
        or binding.get("provider_digest_input_count") != 0
    ):
        raise KTMaterializationError("NONCONSUMING_BINDING_INVARIANT_MISMATCH")
    return {"handoff": handoff, "binding_envelope": binding_envelope, "binding": binding}


def build_reduction(binding_file_sha256: str, binding_inner_sha256: str) -> dict[str, Any]:
    return {
        "schema_id": "G77_256KT_SPCE_TERMINAL_PRECONSUMPTION_MATERIALIZATION_V1",
        "terminal": TERMINAL,
        "mode": "SPCE_PHASE_A__REPOSITORY_ONLY_PRECONSUMPTION_MATERIALIZATION",
        "entry": {"branch": BRANCH, "head": HEAD, "tree": TREE, "subject": SUBJECT, "origin": ORIGIN, "remote_head": HEAD, "remote_equality": "VERIFIED__DIRECT_BRANCH_LS_REMOTE", "ancestry_anchor": ANCHOR, "index_empty": True, "tracked_diff_empty": True},
        "nested_authority": {"origin": "git@github.com:Aljosa3/sapianta-core.git", "immutable_ref": "refs/tags/sapianta-system-nested-authority-3183bab-v1", "head": "3183bab71f8f30397c0309dd2e6d846d14a11f66", "tree": "7c32ec05efc2be43297849bc38ec8766514a523d", "clean": True, "detached": True, "pinned": True, "remote_tag_equal": "VERIFIED__DIRECT_LS_REMOTE"},
        "continuation": {"provider_interruption": "VERIFIED__USAGE_LIMIT_ONLY__NOT_CONSTITUTIONAL_FAILURE", "same_generation_continuation": "VERIFIED__G77_256KT", "previous_worker_memory_required": "VERIFIED__NO", "authenticated_repository_continuation": "VERIFIED__YES", "partial_work_reconstruction_status": "VERIFIED__ONE_GENERATION_LOCAL_MATERIALIZER_RECONSTRUCTED_AS_DEFECTIVE_PARTIAL_WORK", "partial_work_reuse_status": "VERIFIED__REPAIRED_AND_REUSED__NO_SECOND_MATERIALIZER", "partial_work_drift": "VERIFIED__ONE_OWNER_CHAIN_PROOF_CHECK_DEFECT__ZERO_AUTHORITY_OR_OPERATIONAL_DRIFT"},
        "human_source": {"path": SOURCE.relative_to(ROOT).as_posix(), "byte_count": 1213, "lf_count": 14, "utf8_validity": "VERIFIED", "bom_status": "VERIFIED__ABSENT", "final_lf_status": "VERIFIED__PRESENT", "sha256": SOURCE_SHA256, "exact_bytes_status": "VERIFIED__EXACT_KO_BYTE_EQUALITY", "tracked": False},
        "nonconsuming_proof": {
            "handoff_preparation_consumes_authority": "VERIFIED__NO",
            "binding_materialization_consumes_authority": "VERIFIED__NO",
            "preconsumption_handoff_required": "VERIFIED__YES__FM_STRICT_LOADER_REQUIRES_PERSISTED_CANONICAL_AUTHORITY_PATH",
            "preconsumption_binding_required": "VERIFIED__YES__JZ_AND_KA_KG_CONSUMER_REVALIDATE_PERSISTED_DIGEST_PRESERVING_BINDING",
            "consumption_boundary_owner": "VERIFIED__KA_KG_PHASE_B_CONTROLLER_PLUS_FM_FINAL_ADMISSION_AND_P11_ONE_SHOT_CONSUMER",
            "consumption_boundary_artifact": "G77_256KN_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1.json__ABSENT",
            "consumption_boundary_transition": "GRANTED_UNCONSUMED_TO_CONSUMED__NOT_ENTERED",
            "consumption_boundary_preconditions": "EXACT_HANDOFF__EXACT_PRECONSUMPTION_BINDING__FINAL_ADMISSION__UNCONSUMED_RECEIPT_NAMESPACE__EXACT_ONE_SHOT_CLAIM",
        },
        "mechanism": {
            "handoff_producer_owner": "FM.write_authority_handoff",
            "handoff_producer_artifact": FM_PATH.relative_to(ROOT).as_posix(),
            "handoff_schema_owner": "FM.validate_authority_handoff_envelope_shape_AND_FM.parse_authority_handoff_bytes",
            "handoff_schema": "SAPIANTA_CONTEXT_BOUND_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1__SAPIANTA_CONTEXT_BOUND_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_V1",
            "handoff_serialization_rule": "UNIQUE_KEY_CANONICAL_COMPACT_JSON_PLUS_ONE_LF__STRICT_PARSE_ROUND_TRIP",
            "handoff_binding_rule": "EXACT_KN_SOURCE_TO_GENERATION_OPERATION_VECTOR_CONTEXT_REPOSITORY_CANDIDATE_ARGV_WRAPPER_ADAPTER_AND_LIMITS",
            "handoff_digest_rule": "SHA256_EXACT_CANONICAL_HANDOFF_BYTES__DERIVED_BY_OWNER__NO_CALLER_OR_PROVIDER_DIGEST",
            "handoff_collision_guard": "FRESH_PATHS_MUST_BE_ABSENT_BEFORE_EXCLUSIVE_MATERIALIZATION",
            "handoff_replay_guard": "AUTHORIZATION_REUSABLE_FALSE__REPLAY_LIMIT_ZERO__UNCONSUMED_NAMESPACE_REQUIRED",
            "handoff_one_shot_rule": "ONE_VM_BOOT__ONE_QEMU_EXECUTION__ONE_EXPIRED_ATTEMPT__ZERO_RETRY_REPAIR_REPLAY",
            "handoff_consumption_separation": "VERIFIED__KA_KG_PREPARE_PERSISTS_HANDOFF_AND_BINDING_AS_GRANTED_UNCONSUMED__SEPARATE_CONSUME_AND_OPERATE_TRANSITIONS_TO_CONSUMED",
        },
        "human_authority": {
            "human_authority_authentication": "VERIFIED__EXACT_EXISTING_KN_HUMAN_AUTHORITY_AUTHENTICATED_BY_KS_AND_REAUTHENTICATED",
            "human_authority_handoff_materialized": "VERIFIED__EXACT_NONCONSUMING_CANONICAL_HANDOFF",
            "human_authority_binding": "VERIFIED__EXACT_KN_PRECONSUMPTION_BINDING",
            "human_authority_consumption_status": "VERIFIED__UNCONSUMED",
        },
        "materialized_handoff": {
            "materialized_handoff_path": HANDOFF.relative_to(ROOT).as_posix(),
            "materialized_handoff_byte_count": 1715,
            "materialized_handoff_sha256": HANDOFF_SHA256,
            "materialized_authorization_inner_sha256": AUTHORIZATION_INNER_SHA256,
            "materialized_canonical_json_status": "VERIFIED__UNIQUE_KEY_CANONICAL_COMPACT_JSON_PLUS_ONE_LF",
            "materialized_schema_status": "VERIFIED__EXACT_FM_AUTHORITY_ENVELOPE_AND_AUTHORIZATION_SCHEMAS",
            "materialized_strict_parse_status": "VERIFIED__FM_STRICT_PARSE_ROUND_TRIP_EQUAL",
        },
        "preconsumption_binding": {
            "path": BINDING.relative_to(ROOT).as_posix(),
            "file_sha256": binding_file_sha256,
            "inner_sha256": binding_inner_sha256,
            "binding_phase": "BEFORE_AUTHORITY_CONSUMPTION_AND_FM_INVOCATION",
            "authority_digest_equality": "VERIFIED__CANONICAL_EQUALS_SEALED_EQUALS_FINAL_ARGV",
            "caller_digest_input_count": 0, "provider_digest_input_count": 0,
            "binding_is_authority": False, "execution_authorized_by_binding": False,
            "process_started": False, "authority_consumption_count": 0,
            "fm_operational_invocation_count": 0,
            "bindings": {"generation": GENERATION, "operation": OPERATION, "vector": "EXPIRED", "human_source_sha256": SOURCE_SHA256, "human_decision_presentation_sha256": DECISION_PRESENTATION_SHA256, "candidate_sha256": CANDIDATE_SHA256, "request_identity_sha256": REQUEST_SHA256, "context_sha256": CONTEXT_SHA256, "context_file_sha256": CONTEXT_FILE_SHA256, "repository_head": "1141f9f1dd2069e250c6ad44dc90164597366ffe", "repository_tree": "70aa2a12af3d9806e0d6ddc73f7f751292413e52", "canonical_argv_sha256": CANONICAL_ARGV_SHA256, "temporal_binding_sha256": TEMPORAL_BINDING_SHA256, "scope": "ONE_KN_GENERATION__ONE_KN_OPERATION__ONE_AUTHORITY_CONSUMPTION_MAXIMUM__ONE_OPERATIONAL_ATTEMPT_MAXIMUM", "route": "FM_TO_ER_TO_P11", "retry_limit": 0, "repair_retry_limit": 0, "replay_limit": 0},
        },
        "failure_novelty_and_convergence_check": {
            "failure_class": "PROOF_GAP",
            "novelty": "VERIFIED__NEW_REQUIRED_PERSISTED_PRECONSUMPTION_EDGE__DISTINCT_FROM_KS_IN_MEMORY_READINESS",
            "affected_invariant": "EXACT_PERSISTED_CANONICAL_HANDOFF_AND_DIGEST_PRESERVING_BINDING_MUST_EXIST_AND_REVALIDATE_BEFORE_ONE_SHOT_CONSUMPTION",
            "previous_closest_edge": "KS_IN_MEMORY_CANONICAL_HANDOFF_PROJECTION_AND_BINDING_READINESS",
            "semantic_difference": "VERIFIED__KT_PERSISTS_AND_STRICTLY_RELOADS_THE_EXACT_HANDOFF_AND_BINDING_REQUIRED_BY_THE_EXISTING_CONSUMER__KS_DID_NOT",
            "production_behavior_impact": "VERIFIED__NONE__REPOSITORY_ONLY_PRECONSUMPTION",
            "new_capability_required": "NOT_PROVEN__EXISTING_FM_JZ_KA_KG_MECHANISM_REUSED",
            "new_proof_required": "VERIFIED__PERSISTED_CANONICAL_BYTE_EQUALITY__STRICT_RELOAD__DIGEST_PRESERVING_BINDING__UNCONSUMED_STATE",
            "convergence_signal": "VERIFIED__KS_FIRST_BROKEN_EDGE_CLOSED_WITH_EXACT_TWO_EXISTING_MECHANISM_ARTIFACTS",
            "repetition_pressure": "VERIFIED__HIGH__KN_THROUGH_KT_HAS_NO_E05_MOVEMENT",
            "verification_amplification_risk": "ESTIMATED__LOW_AFTER_MATERIALIZATION__NEXT_EDGE_IS_CONSUMPTION_AND_OPERATION_NOT_MORE_PHASE_A_PROOF",
            "classification_evidence": "VERIFIED__KS_FRONTIER__FM_STRICT_LOADER__JZ_BINDER__KA_KG_SEPARATE_PREPARE_AND_CONSUME_FUNCTIONS",
            "classification_confidence": "VERIFIED__HIGH",
            "acceptance_requirement_forcing_continuation": "VERIFIED__KA_KG_CONSUMER_LOADS_AND_REVALIDATES_PERSISTED_HANDOFF_AND_BINDING_BEFORE_SEPARATE_CONSUMPTION_TRANSITION",
        },
        "cross_vector_reuse_assessment": {"cross_vector_reuse_scope": "MULTI_VECTOR_REUSABLE", "reusable_component": "DIRECT_HUMAN_UTF8_SOURCE_BYTES_TO_DERIVED_DIGEST_TO_CANONICAL_HANDOFF_TO_ONE_SHOT_CONSUMPTION_PATTERN", "reuse_invariant": "EXPLICIT_HUMAN_DECISION_SOURCE_AND_EXACT_BYTES_MUST_PRECEDE_AUTHORITY_BINDING_AND_CONSUMPTION", "applicable_vectors": ["EXPIRED", "FUTURE", "WRONG_ATTEMPT", "WRONG_CONTRACT", "WRONG_INPUT", "WRONG_PROVENANCE"], "vector_specific_residue": "KT_HANDOFF_IS_KN_EXPIRED_SPECIFIC__SOURCE_PRESENTATION_SCOPE_TEMPORAL_AUTHORITY_OPERATIONAL_ACCEPTANCE_AND_E05_REMAIN_VECTOR_LOCAL", "reuse_preconditions": "PER_GENERATION_EXACT_BINDINGS__FRESH_NAMESPACE__STRICT_RELOAD__NO_AUTHORITY_OR_E05_TRANSFER", "revalidation_required": "VERIFIED__PER_GENERATION_VECTOR_HUMAN_ACT_BINDING_AND_OPERATION", "expected_future_proof_reduction": "ESTIMATED__REUSE_SERIALIZER_BINDER_COLLISION_REPLAY_AND_ONE_SHOT_GUARDS__NO_AUTHORITY_OR_E05_TRANSFER"},
        "frontier": {"last_verified_operational_edge": "EXACT_HUMAN_AUTHORITY_AUTHENTICATED_JZ_BOUND_CONSUMED_ONCE_AND_ONE_NO_NETWORK_VM_BOOT_REACHED_GUEST_CUSTODY_LOAD", "first_unverified_operational_edge": "FRESH_HUMAN_AUTHORIZED_EXPIRED_DENIAL_BEFORE_P11_ENTRY_AFTER_KF_REPAIR", "last_verified_edge": "KT_EXACT_KN_HANDOFF_AND_PRECONSUMPTION_BINDING_MATERIALIZED_AND_UNCONSUMED", "first_broken_edge": "ONE_EXACT_AUTHORITY_CONSUMPTION_AND_ONE_EXACT_KN_OPERATIONAL_PHASE_B_ATTEMPT", "current_real_blocker": "VERIFIED__HUMAN_REVIEW_AND_COMMITTED_KT_CHECKPOINT_REQUIRED_BEFORE_ANY_CONSUMPTION__OPERATIONAL_HEAD_ADMISSION_MUST_BE_REAUTHENTICATED", "minimum_missing_capability": "NOT_PROVEN__NO_NEW_CAPABILITY_GAP__ONE_GOVERNED_CONSUMPTION_AND_OPERATIONAL_OBSERVATION_REMAIN", "minimum_legal_next_delta": "AFTER_COMMITTED_KT_AND_HUMAN_REVIEW__REAUTHENTICATE_CONTEXT_BOUND_OPERATIONAL_ENTRY__THEN_IF_PASS_ONE_CONSUMPTION_AND_ONE_KN_PHASE_B_ATTEMPT__NO_RETRY"},
        "governance": {"project_state": "VERIFIED__KT_HANDOFF_AND_BINDING_MATERIALIZED__AUTHORITY_UNCONSUMED__STOPPED", "project_progress": "VERIFIED__KS_PERSISTED_PRECONSUMPTION_EDGE_CLOSED_WITH_EXISTING_MECHANISM", "project_progress_estimate": "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR", "informal_project_progress_estimate": "ESTIMATED__ONE_REVIEWED_CONSUMPTION_AND_OPERATIONAL_EXPIRED_OBSERVATION_EDGE_REMAINS", "constitutional_health_evidence": "VERIFIED__STRICT_CANONICAL_RELOAD__DIGEST_EQUALITY__UNCONSUMED__NO_PROCESS__ONE_ROUTE", "shadow_automation_status": "NOT_APPLICABLE__NO_NEW_AUTOMATION_OR_AUTHORITY_MECHANISM", "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR", "governance_efficiency": "ESTIMATED__HIGH__TWO_REQUIRED_EXISTING_MECHANISM_ARTIFACTS_CLOSE_THE_PRECONSUMPTION_EDGE", "overengineering_risk": "ESTIMATED__LOW__NO_NEW_SCHEMA_OWNER_ROUTE_REGISTRY_OR_ABSTRACTION", "cognition_provenance": "VERIFIED__COMMITTED_KS_KR_KQ_KO_KN_FM_JZ_KA_KG_AND_DETERMINISTIC_MATERIALIZED_BYTES", "cognition_assisted_handoff": "VERIFIED__COMMISSION_TO_AUTHENTICATED_REPOSITORY_CONTINUATION__NO_MEMORY_DEPENDENCY", "candidate_capability": "VERIFIED__EXACT_KN_NONCONSUMING_HANDOFF_AND_PRECONSUMPTION_BINDING__NOT_OPERATIONAL", "shadow_design_target": "VERIFIED__SEPARATE_ONE_SHOT_CONSUMPTION_THEN_FM_ER_P11_EXPIRED_ATTEMPT__NOT_ENTERED", "constitutional_continuation_progress": "VERIFIED__AUTHENTICATED_AUTHORITY_ADVANCED_FROM_BINDING_READINESS_TO_ACTUAL_UNCONSUMED_BINDING"},
        "e05": {"state": "VERIFIED__11_OF_18", "frontier": "VERIFIED__7_UNSATISFIED_OF_18", "credit": "VERIFIED__0", "kn_e05_credit": "VERIFIED__0", "expired": "NOT_PROVEN_OPERATIONALLY", "potential_future_after_qualifying_observation": "NOT_PROVEN__12_OF_18"},
        "ex": {"ex_reused": "VERIFIED__17_OF_17", "ex_reconstructed": "VERIFIED__0"},
        "architecture": {"production_mutation_count": 0, "p11_implementation_mutation_count": 0, "new_owner_count": 0, "new_route_count": 0, "new_registry_count": 0, "new_generic_abstraction_count": 0, "new_constitutional_concept_count": 0, "production_route_before": 1, "production_route_after": 1, "parallel_flow": "NO"},
        "proof_yield": {"new_verified_capability_count": "VERIFIED__0", "new_operational_capability_count": "VERIFIED__0", "new_blocker_localized_count": "VERIFIED__0", "new_blocker_closed_count": "VERIFIED__1__PERSISTED_PRECONSUMPTION_EDGE", "new_false_or_superseded_blocker_removed_count": "VERIFIED__0", "new_classification_result_count": "VERIFIED__1__NONCONSUMING_MATERIALIZATION_REQUIRED_AND_COMPLETE", "handoff_materialization_edge_count": "VERIFIED__1", "preconsumption_binding_edge_count": "VERIFIED__1", "proof_reuse_count": "VERIFIED__17__EX_COMMON_COMPONENTS"},
        "ccwim": {"ccwim_maturity_level": "ESTIMATED__L4_LIKE__NO_GOVERNED_CERTIFICATION", "authenticated_repository_continuation": "VERIFIED__YES", "previous_worker_conversation_required": "VERIFIED__NO", "previous_worker_memory_required": "VERIFIED__NO", "handoff_reconstruction_success": "VERIFIED__YES", "handoff_ambiguity_count": "VERIFIED__0", "observed_artifact_level_cross_worker_drift": "VERIFIED__0"},
        "hac_hai_hae": "NOT_PROVEN__AUTHENTICATED_HAC_HAI_HAE_DEFINITIONS_NOT_LOCATED",
        "operational_counters": zero_counters(), "phase_b_started": False,
        "auto_continuable": False, "human_review_required": True,
    }


def reduction_envelope(binding_file_sha256: str, binding_inner_sha256: str) -> dict[str, Any]:
    reduction = build_reduction(binding_file_sha256, binding_inner_sha256)
    return {"schema_id": "G77_256KT_SPCE_TERMINAL_PRECONSUMPTION_MATERIALIZATION_ENVELOPE_V1", "reduction": reduction, "reduction_sha256": hashlib.sha256(canonical_bytes(reduction)).hexdigest()}


def materialize() -> None:
    fm, _ = authenticate_common(materialized=False)
    if OUTPUT.exists() or OUTPUT.is_symlink():
        raise KTMaterializationError("KT_REDUCTION_COLLISION")
    authorization = build_authorization(json.loads(CONTEXT.read_bytes()), fm)
    result = fm.write_authority_handoff(HANDOFF, authorization)
    if result != {"authority_file_sha256": HANDOFF_SHA256, "authority_inner_sha256": AUTHORIZATION_INNER_SHA256, "canonical_byte_count": 1715}:
        raise KTMaterializationError("EXISTING_OWNER_HANDOFF_RESULT_MISMATCH")
    binding_envelope = fm.build_preconsumption_invocation_binding(
        repository_root=ROOT, operation_context=CONTEXT,
        live_candidate_binding=CANDIDATE, execution_authority=HANDOFF,
    )
    if BINDING.exists() or BINDING.is_symlink():
        raise KTMaterializationError("BINDING_COLLISION_AFTER_HANDOFF")
    fm.write_atomic(BINDING, binding_envelope)
    verified = verify_materialized(fm)
    binding_file = sha256_path(BINDING)
    binding_inner = binding_envelope["invocation_binding_sha256"]
    OUTPUT.write_bytes(canonical_bytes(reduction_envelope(binding_file, binding_inner)))
    print(TERMINAL)


def verify() -> None:
    fm, _ = authenticate_common(materialized=True)
    verified = verify_materialized(fm)
    binding_file = sha256_path(BINDING)
    binding_inner = verified["binding_envelope"]["invocation_binding_sha256"]
    if BINDING_FILE_SHA256.startswith("TO_BE_") or BINDING_INNER_SHA256.startswith("TO_BE_"):
        raise KTMaterializationError("BINDING_HASHES_NOT_FINALIZED")
    if binding_file != BINDING_FILE_SHA256 or binding_inner != BINDING_INNER_SHA256:
        raise KTMaterializationError("FINAL_BINDING_HASH_MISMATCH")
    if load_envelope(OUTPUT, "reduction") != build_reduction(binding_file, binding_inner):
        raise KTMaterializationError("KT_REDUCTION_CONTENT_MISMATCH")
    print(TERMINAL)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("materialize", "verify"))
    args = parser.parse_args()
    materialize() if args.mode == "materialize" else verify()


if __name__ == "__main__":
    main()
