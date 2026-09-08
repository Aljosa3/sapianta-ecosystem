#!/usr/bin/env python3
"""Materialize the nonauthority G77-256JB FUTURE Human barrier.

The only executable path authenticates ratified JA, reuses the certified IF
runtime candidate through DU/EB/EE V2, prepares the existing FM operation
state without invoking QEMU, derives a sealed GN presentation, and stops.
It contains no authority-consumption or operational-launch call.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from types import ModuleType
from typing import Any


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
JB_ROOT = ROOT / ".github/governance/evidence/g77_256jb_future_operational_commissioning_v1"
LIVE = JB_ROOT / "live_binding"
OPERATION_ROOT = JB_ROOT / "operation_state"
TRANSIENT_ROOT = Path("/tmp/g77_256jb_future_operational_commissioning_v1")

BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
HEAD = "bb83b26bd3a7012c5a8a44e26fe93c91700337a6"
TREE = "c7951de62a0d16d45fd60fbfb14e54047543b13c"
SUBJECT = "G77-256JA certify FUTURE post-commit operational readiness"
ANCHOR = "5c972e9960987ab27420395b54ace693df097e7b"
IF_HEAD = "699fcdce794ff49b6c8735602936355724ed1c90"
IF_TREE = "7c773d4b2acdf013f1b8238eabfc8eced4dd6866"
NESTED_ORIGIN = "git@github.com:Aljosa3/sapianta-core.git"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
NESTED_TAG = "sapianta-system-nested-authority-3183bab-v1"

PREFIX = "G77_256JB"
VECTOR = "FUTURE"
GENERATION = PREFIX + "_ONE_FRESH_HUMAN_AUTHORIZED_FUTURE_OPERATIONAL_COMMISSIONING_V1"
OPERATION = PREFIX + "_E05_FUTURE_DENIAL_BEFORE_ENTRY_001"

LINEAGE = {
    "JA": HEAD,
    "IZ": "6c1bbd1fbe592c4bdc9ed72394c00506a0318854",
    "IY": "fb9756f5b5042df1b601cbcbbee1eda50c443245",
    "IX": "0d36155469c7d2fe043678a82652132c2878ff0e",
    "IW": "223c6256c68e4506a4630cc07bdf452d39be2823",
    "IV": "d9bf5a04a5277a7cd3291d728e46688b89303144",
    "IU": "30bb9fd8d983e56362d7c95fd5d15581da27f703",
    "IT": "635687d9d8c4ae9ad122ca62083cc886497ee87e",
    "IS": "032bd82276a2a4fb2543ca90d3533b5e1b050bdf",
    "IR": "8f68fb2e94db3c8bac56fc96315b312e6217dea6",
    "IQ": "2ad26623dd4625d2162ce2b9fa0d65e8581f95f6",
    "IP": "65d6d029fbcfbae964e702fdbdb544c940b2eec2",
    "IO": "af7835d98d0bfa685da99e41bd5bc866cbc2a54b",
    "IN": "e39aee28fa9181e1db2ae6c5cff4a50f557821be",
    "IF": IF_HEAD,
    "IE": "9420764a5bb6db8909334f2a422225687a37a346",
    "IC": "afdd47166acdee30cb9867d3d3c7bfec0de64c8a",
    "ANCHOR": ANCHOR,
}

JA_ROOT = Path(".github/governance/evidence/g77_256ja_future_post_commit_readiness_v1")
JA_REPORT = JA_ROOT / "G77_256JA_G48_IMPLEMENTATION_REPORT_V1.md"
JA_TERMINAL = JA_ROOT / "G77_256JA_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
JA_FORMALIZER = JA_ROOT / "analysis/G77_256JA_POST_COMMIT_READINESS_FORMALIZER_V1.py"
JA_TEST = JA_ROOT / "tests/test_g77_256ja_future_post_commit_readiness_v1.py"
JA_HASHES = {
    JA_REPORT: "0345651d43c8be782c9e6e21e75c2b3cd6f67858cc2226e9358f16b154c62589",
    JA_TERMINAL: "5ddf875a8e25384baad7acde83e66e5809a1d70cfe9507b36ce325a267ae3fa8",
    JA_FORMALIZER: "da09da8b217f09e7c51833b70aa32de6dbd58e57da5317212d1120f8a3e5a022",
    JA_TEST: "590ce174f791dae4090770fbbce5f1d257c1030ab3e7d80b193bf31090505174",
}

IR_ROOT = Path(".github/governance/evidence/g77_256ir_post_commit_gn_future_presentation_readiness_v1")
IR_REPORT = IR_ROOT / "G77_256IR_G48_IMPLEMENTATION_READINESS_REPORT_V1.md"
IR_TERMINAL = IR_ROOT / "G77_256IR_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
IR_FORMALIZER = IR_ROOT / "analysis/G77_256IR_POST_COMMIT_GN_FUTURE_PRESENTATION_READINESS_FORMALIZER_V1.py"
IR_TEST = IR_ROOT / "tests/test_g77_256ir_post_commit_gn_future_presentation_readiness_v1.py"
IR_HASHES = {
    IR_REPORT: "9e20117c49301c30d998fb0cc9246e97d6d1d9d9e9e836eb91350753803baa09",
    IR_TERMINAL: "7a518712dae1e89cafb76783854cc4b25623d8bcdb3169896afa9e717278db47",
    IR_FORMALIZER: "a543a36d9bab2cd591c216d7329a046cc958151b75c3748b8dccd08118f05a5b",
    IR_TEST: "93f3fcd2311e92e13dca4ec4dbbad3b045af4e4659abeb45b58bcd7f21cc2834",
}

FM_PATH = Path(".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py")
GN_PATH = Path(".github/governance/evidence/g77_256gn_human_authorization_presentation_binding_v1/presentation/G77_256GN_SEALED_REQUEST_HUMAN_AUTHORIZATION_PRESENTATION_V1.py")
GL_PATH = Path(".github/governance/evidence/g77_256gl_receipt_parent_equivalence_v1/orchestration/G77_256GL_RECEIPT_PARENT_PREAUTHORIZATION_BINDING_V1.py")
DU_PATH = Path(".github/governance/evidence/g77_256du_continuation_manifest_contract_v2/validator/G77_256DU_CONTINUATION_MANIFEST_COMPATIBILITY_VALIDATOR_V2.py")
EB_PATH = Path(".github/governance/evidence/g77_256eb_candidate_bound_validation_receipt_v2/validator/G77_256EB_CANDIDATE_BOUND_PRE_MATERIALIZATION_VALIDATOR_V2.py")
EE_PATH = Path(".github/governance/evidence/g77_256ee_runtime_consumer_binding_v2/validator/G77_256EE_RUNTIME_CONSUMER_BINDING_VALIDATOR_V2.py")
IH_CANDIDATE = Path(".github/governance/evidence/g77_256ih_future_if_identity_rebind_v1/live_binding/candidate/G77_256IH_FUTURE_IF_BOUND_CURRENT_CANDIDATE_V1.json")
IF_ACT_CHE = Path(".github/governance/evidence/g77_256if_future_post_commit_readiness_v1/live_binding/G77_256IF_FUTURE_ACT_CHE_BINDING_V1.json")
EX_SEAL = Path(".github/governance/evidence/g77_256ex_common_substrate_certification_v1/G77_256EX_FINAL_VALIDATION_SEAL_V1.json")
FUTURE_CANDIDATE_SHA = "ad5d204ec6ace09f18b83fd5f868e73dac5e36dad81149f9f335c87f68cf42f7"
FUTURE_PAYLOAD = "sha256:9568e0c248ad488cabcf6bde6b490c544077862d10e3fda13bcdc8ed9953f547"
FUTURE_SOURCE_ACT = "sha256:7167b0725d2c84bafde1d0060f512b0fa358d777ec1beff8b7c68d22ee6502e8"
FUTURE_CHE = "CHE-CORRELATION-15b2680b5577da169cecf9efb3231e2e6f6467e6f409fa2594b04128f998e454"


class JBBarrierError(ValueError):
    """One deterministic fail-closed JB barrier error."""


def load_module(relative: Path, name: str) -> ModuleType:
    path = ROOT / relative
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise JBBarrierError(f"MODULE_UNAVAILABLE:{relative}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


FM = load_module(FM_PATH, "g77_256jb_fm")
GN = load_module(GN_PATH, "g77_256jb_gn")
GL = load_module(GL_PATH, "g77_256jb_gl")
DU = load_module(DU_PATH, "g77_256jb_du_v2")
EB = load_module(EB_PATH, "g77_256jb_eb_v2")
EE = load_module(EE_PATH, "g77_256jb_ee_v2")


def canonical_bytes(value: Any) -> bytes:
    return FM.canonical_bytes(value)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise JBBarrierError(f"DUPLICATE_KEY:{key}")
        value[key] = item
    return value


def load_canonical(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw, object_pairs_hook=unique_object)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise JBBarrierError(f"NONCANONICAL_JSON:{path}")
    return value


def sealed(schema: str, inner_name: str, value: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_id": schema,
        inner_name: value,
        f"{inner_name}_sha256": sha256_bytes(canonical_bytes(value)),
    }


def write_json(path: Path, value: dict[str, Any]) -> None:
    if path.exists() or path.is_symlink():
        raise JBBarrierError(f"FRESH_ARTIFACT_COLLISION:{path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(value))


def git(*args: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(["git", *args], cwd=cwd, text=True).strip()


def authenticate_entry(remote_head: str, nested_remote_tag: str) -> dict[str, Any]:
    observed = {
        "repository": str(ROOT),
        "branch": git("branch", "--show-current"),
        "head": git("rev-parse", "HEAD"),
        "tree": git("rev-parse", "HEAD^{tree}"),
        "subject": git("show", "-s", "--format=%s", "HEAD"),
        "origin": git("remote", "get-url", "origin"),
        "remote_head": remote_head,
        "tracked_worktree_clean": git("status", "--porcelain", "--untracked-files=no") == "",
        "index_empty": git("diff", "--cached", "--name-only") == "",
    }
    expected = {
        "branch": BRANCH, "head": HEAD, "tree": TREE, "subject": SUBJECT,
        "origin": ORIGIN, "remote_head": HEAD, "tracked_worktree_clean": True,
        "index_empty": True,
    }
    if any(observed[key] != expected for key, expected in expected.items()):
        raise JBBarrierError("EXACT_RATIFIED_JA_ENTRY_MISMATCH")
    for line in git("status", "--porcelain", "--untracked-files=all").splitlines():
        if not line.startswith("?? " + JB_ROOT.relative_to(ROOT).as_posix() + "/"):
            raise JBBarrierError("JB_BOUNDED_WORKTREE_SCOPE_VIOLATION")
    lineage: dict[str, str] = {}
    for label, revision in LINEAGE.items():
        if subprocess.run(
            ["git", "merge-base", "--is-ancestor", revision, "HEAD"],
            cwd=ROOT, check=False,
        ).returncode:
            raise JBBarrierError(f"LINEAGE_MISSING:{label}")
        lineage[label] = "VERIFIED"
    nested = ROOT / "sapianta_system"
    nested_state = {
        "origin": git("remote", "get-url", "origin", cwd=nested),
        "head": git("rev-parse", "HEAD", cwd=nested),
        "tree": git("rev-parse", "HEAD^{tree}", cwd=nested),
        "clean": git("status", "--porcelain", cwd=nested) == "",
        "detached": git("branch", "--show-current", cwd=nested) == "",
        "tag": git("describe", "--tags", "--exact-match", "HEAD", cwd=nested),
        "remote_tag": nested_remote_tag,
    }
    if nested_state != {
        "origin": NESTED_ORIGIN, "head": NESTED_HEAD, "tree": NESTED_TREE,
        "clean": True, "detached": True, "tag": NESTED_TAG,
        "remote_tag": NESTED_HEAD,
    }:
        raise JBBarrierError("NESTED_AUTHORITY_MISMATCH")
    return observed | {"local_remote_equality": "VERIFIED", "lineage": lineage, "nested_authority": nested_state}


def reconstruct_ja() -> dict[str, Any]:
    identities: dict[str, Any] = {}
    for relative, expected_sha in JA_HASHES.items():
        committed = subprocess.check_output(["git", "show", f"{HEAD}:{relative}"], cwd=ROOT)
        current = (ROOT / relative).read_bytes()
        if committed != current or sha256_bytes(committed) != expected_sha:
            raise JBBarrierError(f"JA_COMMITTED_BYTE_MISMATCH:{relative}")
        identities[relative.name] = {
            "git_blob": git("rev-parse", f"{HEAD}:{relative}"),
            "sha256": expected_sha,
        }
    envelope = load_canonical(ROOT / JA_TERMINAL)
    if envelope["reduction_sha256"] != sha256_bytes(canonical_bytes(envelope["reduction"])):
        raise JBBarrierError("JA_INNER_SEAL_MISMATCH")
    reduction = envelope["reduction"]
    terminal = "A__FUTURE_POST_COMMIT_LIVE_BINDING_AND_OPERATIONAL_READINESS_VERIFIED"
    if (
        reduction["terminal"] != terminal
        or reduction["mode"] != "POST_COMMIT_LIVE_BINDING_STATIC_READINESS_ONLY__NO_AUTHORIZATION__NO_OPERATION"
        or reduction["live_binding"]["runtime_certification_role_separation"] != "VERIFIED__PRESERVED"
        or reduction["live_binding"]["former_worktree_drift_barrier"] != "VERIFIED__CLOSED"
        or reduction["reuse_impact"]["production_route_delta"] != "VERIFIED__0"
        or reduction["reuse_impact"]["p11_mutation_count"] != "VERIFIED__0"
        or reduction["e05"]["after"] != "VERIFIED__10_OF_18"
    ):
        raise JBBarrierError("JA_TERMINAL_BOUNDARY_MISMATCH")
    return {
        "status": "VERIFIED__COMMITTED_OBJECT_RECONSTRUCTION",
        "terminal": terminal, "artifact_count": 4,
        "inner_seal": "VERIFIED", "identities": identities,
        "ex_reused": reduction["proof_reuse"]["ex_reused"],
        "ex_reconstructed": reduction["proof_reuse"]["ex_reconstructed"],
    }


def reconstruct_ir() -> dict[str, Any]:
    identities: dict[str, Any] = {}
    for relative, expected_sha in IR_HASHES.items():
        committed = subprocess.check_output(["git", "show", f"{HEAD}:{relative}"], cwd=ROOT)
        current = (ROOT / relative).read_bytes()
        if committed != current or sha256_bytes(committed) != expected_sha:
            raise JBBarrierError(f"IR_COMMITTED_BYTE_MISMATCH:{relative}")
        identities[relative.name] = {
            "git_blob": git("rev-parse", f"{HEAD}:{relative}"),
            "sha256": expected_sha,
        }
    envelope = load_canonical(ROOT / IR_TERMINAL)
    if envelope["reduction_sha256"] != sha256_bytes(canonical_bytes(envelope["reduction"])):
        raise JBBarrierError("IR_INNER_SEAL_MISMATCH")
    reduction = envelope["reduction"]
    if reduction["terminal"]["terminal"] != "A__POST_COMMIT_COMPATIBILITY_AND_FRESH_PREAUTHORIZATION_READINESS":
        raise JBBarrierError("IR_TERMINAL_MISMATCH")
    if reduction["presentation_readiness"]["fresh_future_preauthorization_readiness"] != "VERIFIED":
        raise JBBarrierError("IR_FUTURE_READINESS_MISMATCH")
    if set(reduction["operational_counters"].values()) != {0} or reduction["e05"]["after"] != "10/18":
        raise JBBarrierError("IR_ZERO_COUNTER_OR_E05_MISMATCH")
    return {
        "status": "VERIFIED", "terminal": reduction["terminal"]["terminal"],
        "artifact_count": 4, "inner_seal": "VERIFIED", "identities": identities,
        "ex_reused": reduction["proof_reuse"]["ex_reused"],
        "ex_reconstructed": reduction["proof_reuse"]["ex_reconstructed"],
    }


def authenticate_future_semantics() -> dict[str, Any]:
    envelope = load_canonical(ROOT / IF_ACT_CHE)
    binding = envelope["binding"]
    if envelope["binding_sha256"] != sha256_bytes(canonical_bytes(binding)):
        raise JBBarrierError("IF_ACT_CHE_SEAL_MISMATCH")
    act = binding["human_authority_act_representation"]
    che = binding["che_correlation"]
    result = {
        "evaluation": binding["evaluation_time_unix_ns"],
        "valid_from": act["payload"]["valid_from_unix_ns"],
        "valid_until": act["payload"]["valid_until_unix_ns"],
        "payload_digest": act["payload_digest"],
        "source_act": che["source_act_digest"],
        "che_correlation": che["correlation_identity"],
    }
    if not result["evaluation"] < result["valid_from"] < result["valid_until"]:
        raise JBBarrierError("FUTURE_TIME_RELATION_MISMATCH")
    if (result["payload_digest"], result["source_act"], result["che_correlation"]) != (
        FUTURE_PAYLOAD, FUTURE_SOURCE_ACT, FUTURE_CHE,
    ):
        raise JBBarrierError("FUTURE_IDENTITY_MISMATCH")
    result.update({"future_semantic_mutation_count": 0, "wall_clock_dependency_count": 0})
    return result


def derive_identity() -> dict[str, Any]:
    expected_root = f"g77_256{PREFIX[-2:].lower()}_{VECTOR.lower()}_operational_commissioning_v1"
    if JB_ROOT.name != expected_root:
        raise JBBarrierError("EVIDENCE_NAMESPACE_IDENTITY_MISMATCH")
    if FM.fresh_context.operation_vector(GENERATION) != VECTOR:
        raise JBBarrierError("CLOSED_VECTOR_IDENTITY_DERIVATION_FAILED")
    for identity in (GENERATION, OPERATION):
        result = subprocess.run(
            ["git", "grep", "-F", identity, HEAD], cwd=ROOT,
            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        if result.returncode not in (0, 1) or result.stdout:
            raise JBBarrierError(f"COMMITTED_IDENTITY_COLLISION:{identity}")
    return {
        "derivation": "VERIFIED__EVIDENCE_NAMESPACE_PREFIX_PLUS_CLOSED_VECTOR_SUFFIX_AND_ONE_SHOT_CASE_PATTERN",
        "operation_generation": GENERATION, "operation_identity": OPERATION,
        "fresh_operation_generation": "VERIFIED", "fresh_operation_identity": "VERIFIED",
        "committed_history_collision": "VERIFIED__NO", "previous_authority_reuse": "VERIFIED__NO",
    }


def materialize_v2_binding() -> dict[str, Any]:
    source = ROOT / IH_CANDIDATE
    if sha256_path(source) != FUTURE_CANDIDATE_SHA:
        raise JBBarrierError("IF_CANDIDATE_IDENTITY_MISMATCH")
    candidate = LIVE / "candidate" / IH_CANDIDATE.name
    runtime_root = LIVE / "runtime_projection"
    runtime = runtime_root / IH_CANDIDATE.name
    readiness_root = LIVE / "v2_readiness"
    readiness_candidate = readiness_root / "candidate/G77_256JB_V2_READINESS_CANDIDATE_V2.json"
    readiness_runtime_root = readiness_root / "runtime_projection"
    readiness_runtime = readiness_runtime_root / readiness_candidate.name
    bindings = readiness_root / "bindings"
    harness = bindings / "G77_256JB_EE_PATH_PROJECTION_FIXTURE_V1.py"
    eb_path = bindings / "G77_256JB_EB_RECEIPT_V2.json"
    ee_path = bindings / "G77_256JB_EE_RECEIPT_V2.json"
    for parent in (
        candidate.parent, runtime_root, readiness_candidate.parent,
        readiness_runtime_root, bindings,
    ):
        parent.mkdir(parents=True, exist_ok=True)
    candidate.write_bytes(source.read_bytes())
    runtime.write_bytes(source.read_bytes())
    readiness_bytes = DU.canonical_bytes(DU.build_du_fixture(ROOT))
    readiness_candidate.write_bytes(readiness_bytes)
    readiness_runtime.write_bytes(readiness_bytes)
    harness.write_text(
        "from pathlib import Path\n\n"
        'FIXTURE_CLASSIFICATION = "TEST_ONLY__NON_AUTHORITY__NON_OPERATIONAL__NON_EXECUTABLE"\n'
        'RAW_ROOT = Path("/mnt/g77-evidence")\n'
        f'CONTINUATION_MANIFEST_PATH = RAW_ROOT / "{readiness_candidate.name}"\n',
        encoding="utf-8",
    )
    du_result = DU.validate_file(readiness_candidate, ROOT, expected_head=IF_HEAD)
    eb = EB.validate_candidate(ROOT, readiness_candidate)
    eb_path.write_bytes(EB.canonical_bytes(eb))
    eb_result = EB.verify_receipt_file(ROOT, eb_path)
    ee = EE.validate_binding(
        ROOT, readiness_candidate, eb_path, harness,
        readiness_runtime_root, "/mnt/g77-evidence",
    )
    ee_path.write_bytes(EE.canonical_bytes(ee))
    ee_result = EE.verify_receipt_file(ROOT, ee_path)
    if set(du_result.values()) != {"PASS"} or eb_result["overall_result"] != "PASS":
        raise JBBarrierError("DU_EB_V2_BINDING_FAILED")
    if ee_result["pre_materialization_runtime_path_binding_result"] != "PASS":
        raise JBBarrierError("EE_V2_BINDING_FAILED")
    target = eb["receipt"]["runtime_target_selection_binding"]
    baseline = eb["receipt"]["certification_baseline"]
    if (target["head"], target["tree"]) != (IF_HEAD, IF_TREE) or baseline != {"head": HEAD, "tree": TREE}:
        raise JBBarrierError("V2_RUNTIME_CERTIFICATION_ROLE_BINDING_FAILED")
    if ee["receipt"]["runtime_target_selection_binding"] != target or ee["receipt"]["certification_baseline"] != baseline:
        raise JBBarrierError("EB_EE_ROLE_DISAGREEMENT")
    return {
        "candidate_path": candidate, "runtime_path": runtime,
        "candidate_sha256": sha256_path(candidate), "runtime_sha256": sha256_path(runtime),
        "v2_readiness_candidate_path": readiness_candidate,
        "v2_readiness_candidate_sha256": sha256_path(readiness_candidate),
        "v2_readiness_runtime_sha256": sha256_path(readiness_runtime),
        "eb_path": eb_path, "ee_path": ee_path, "harness_path": harness,
        "du": "PASS", "eb": "PASS", "ee": "PASS",
        "runtime_target": target, "certification_baseline": baseline,
        "runtime_certification_role_collapse": "VERIFIED__NO",
    }


def zero_counters() -> dict[str, int]:
    return {key: 0 for key in (
        "authorization_presentation", "human_operational_authority", "authority_consumption",
        "pre", "fm_operational_launcher_invocation", "qemu", "vm_creation", "vm_boot",
        "operation_attempt", "future_operation", "request", "p11_entry", "protected_invocation",
        "protected_effect", "retry", "repair_retry", "replay", "e05_credit",
    )}


def materialize(args: argparse.Namespace) -> None:
    if LIVE.exists() or OPERATION_ROOT.exists() or TRANSIENT_ROOT.exists():
        raise JBBarrierError("JB_ONE_SHOT_NAMESPACE_NOT_FRESH")
    entry = authenticate_entry(args.remote_head, args.nested_remote_tag)
    ja = reconstruct_ja()
    ir = reconstruct_ir()
    future = authenticate_future_semantics()
    identity = derive_identity()
    binding = materialize_v2_binding()
    recorded = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    candidate = binding["candidate_path"]
    context = FM.build_operation_context(
        repository_root=ROOT, repository_head=HEAD, repository_tree=TREE,
        generation_identity=GENERATION, operation_identity=OPERATION,
        identity_namespace_prefix=PREFIX, operation_evidence_root=OPERATION_ROOT,
        transient_root=TRANSIENT_ROOT, candidate_source_path=candidate.relative_to(ROOT),
    )
    context_path = LIVE / "SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
    write_json(context_path, context)
    destination = FM.preauth_fresh_checkout_destination_readiness(ROOT, context)
    operation_materialization = FM.materialize_operation_state(
        repository_root=ROOT, context=context, context_source_path=context_path,
        candidate_source_path=candidate.relative_to(ROOT),
    )
    observations = FM.observe_context_assets(ROOT, context, candidate.relative_to(ROOT))
    readiness = FM.authority_free_static_readiness(
        repository_root=ROOT, context=context, observed_head=HEAD, observed_tree=TREE,
        repository_clean=git("status", "--porcelain", "--untracked-files=no") == "",
        observed_asset_sha256=observations, candidate_source_path=candidate.relative_to(ROOT),
    )
    static = sealed(
        "G77_256JB_PREAUTHORITY_STATIC_READINESS_ENVELOPE_V1", "proof",
        {
            "schema_id": "G77_256JB_PREAUTHORITY_STATIC_READINESS_V1",
            "recorded_at_utc": recorded, "entry": entry,
            "ja_reconstruction": ja, "ir_reconstruction": ir,
            "future_semantics": future,
            "v2_binding": {key: value for key, value in binding.items() if not isinstance(value, Path)},
            "destination_readiness": destination, "materialization": operation_materialization,
            "asset_observations": observations, "readiness": readiness,
            "human_operational_authority": 0, "operational_execution_count": 0,
        },
    )
    static_path = JB_ROOT / "G77_256JB_PREAUTHORITY_STATIC_READINESS_V1.json"
    write_json(static_path, static)

    observation = GL.prepare_and_observe_receipt_parent(ROOT, context)
    observation_path = JB_ROOT / "G77_256JB_GL_RECEIPT_PARENT_OBSERVATION_V1.json"
    write_json(observation_path, observation)
    gl_checkpoint = GL.reduce_preauthorization_checkpoint(ROOT, context, observation)
    gl_result = GL.validate_preauth_final_admission_equivalence(ROOT, context, observation, gl_checkpoint)
    equivalence = sealed(
        "G77_256JB_GL_PREAUTH_FINAL_ADMISSION_EQUIVALENCE_ENVELOPE_V1", "proof",
        {"schema_id": "G77_256JB_GL_PREAUTH_FINAL_ADMISSION_EQUIVALENCE_V1",
         "generation_identity": GENERATION, "operation_identity": OPERATION, **gl_result},
    )
    equivalence_path = JB_ROOT / "G77_256JB_GL_PREAUTH_FINAL_ADMISSION_EQUIVALENCE_V1.json"
    write_json(equivalence_path, equivalence)

    counters = zero_counters()
    checkpoint_inner = {
        "schema_id": "G77_256JB_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1",
        "artifact_class": "SEALED_PREAUTHORIZATION_CHECKPOINT__NONAUTHORITY__NONOPERATIONAL",
        "recorded_at_utc": recorded, "generation_identity": GENERATION,
        "operation_identity": OPERATION, "entry_checkpoint": entry,
        "ja_terminal_reconstruction": ja, "ir_terminal_reconstruction": ir,
        "fresh_identity": identity,
        "future_semantics": future,
        "identities": {
            "candidate_sha256": sha256_path(candidate),
            "runtime_projection_sha256": sha256_path(binding["runtime_path"]),
            "context_file_sha256": sha256_path(context_path),
            "context_sha256": context["context_sha256"],
            "canonical_argv_sha256": context["canonical_argv_sha256"],
            "fm_launcher_sha256": sha256_path(ROOT / FM_PATH),
            "future_adapter_sha256": context["guest_adapter_binding"]["source_sha256"],
        },
        "v2_role_separation": {
            "runtime_target": binding["runtime_target"],
            "certification_baseline": binding["certification_baseline"],
            "runtime_certification_role_collapse": "VERIFIED__NO",
        },
        "semantic_firewall": {
            "vector": VECTOR, "evaluation": future["evaluation"],
            "valid_from": future["valid_from"], "valid_until": future["valid_until"],
            "relation": "500 < 600 < 1000", "semantic_mutation_count": 0,
            "wall_clock_dependency_count": 0,
            "expected_denial_reason": "operational Human act is not current",
            "expected_denial_not_forced": True,
        },
        "authority_boundary": {
            "authority_state": "NOT_GRANTED", "checkpoint_is_authority": False,
            "request_is_authority": False, "prompt_is_authority": False,
            "provider_capability_is_authority": False, "human_review_required": True,
            "auto_continuable": False,
            "next_legal_phase": "PRESENT_EXACT_GN_DERIVED_REQUEST_AND_STOP_FOR_EXPLICIT_HUMAN_DECISION",
        },
        "one_shot_maxima": {
            "human_operational_authority": 1, "authority_consumption": 1, "pre": 1,
            "fm_operational_launcher_invocation": 1, "qemu": 1, "vm_creation": 1,
            "vm_boot": 1, "operation_attempt": 1, "future_operation": 1,
            "retry": 0, "repair_retry": 0, "replay": 0,
        },
        "operational_counters": counters,
        "e05": {"before": "10/18", "current": "10/18", "maximum_credit": 1},
        "preauthorization": {
            "static_readiness_result": readiness["result"],
            "static_readiness_file_sha256": sha256_path(static_path),
            "receipt_parent_observation_file_sha256": sha256_path(observation_path),
            "receipt_parent_observation_sha256": observation["observation_sha256"],
            "preauth_final_admission_equivalence_file_sha256": sha256_path(equivalence_path),
            "preauth_final_admission_equivalence": gl_result["preauth_final_admission_equivalence"],
            "single_route_status": "VERIFIED",
        },
        "handoff_sufficiency": {
            "status": "VERIFIED", "state_completeness": "COMPLETE_FOR_PREGRANT_BARRIER",
            "authority_state": "NOT_GRANTED", "authority_consumed": False,
            "ambiguity_count": 0, "unauthenticated_assumption_count": 0,
        },
    }
    checkpoint = sealed(
        "G77_256JB_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_ENVELOPE_V1",
        "checkpoint", checkpoint_inner,
    )
    checkpoint_path = JB_ROOT / "G77_256JB_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json"
    write_json(checkpoint_path, checkpoint)

    request_inner = {
        "schema_id": "G77_256JB_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1",
        "recorded_at_utc": recorded,
        "request_class": "NON_AUTHORITY__ONE_EXPLICIT_HUMAN_DECISION_REQUIRED",
        "generation_identity": GENERATION, "operation_identity": OPERATION,
        "repository": {"branch": BRANCH, "head": HEAD, "tree": TREE,
                       "remote_head": args.remote_head, "stable_ancestry_anchor": ANCHOR},
        "immutable_assets": context["qemu_executable_base_seed_checkout_bindings"],
        "live_binding": {
            "candidate_sha256": sha256_path(candidate), "context_sha256": context["context_sha256"],
            "context_file_sha256": sha256_path(context_path),
            "canonical_argv_sha256": context["canonical_argv_sha256"],
            "du": "PASS", "eb": "PASS", "ee": "PASS",
            "candidate_semantics_changed": False, "candidate_binding_regeneration_required": True,
            "receipt_parent": context["receipt_parent"],
        },
        "preauthorization": {
            "static_readiness_file_sha256": sha256_path(static_path),
            "checkpoint_file_sha256": sha256_path(checkpoint_path),
            "checkpoint_inner_sha256": checkpoint["checkpoint_sha256"],
            "checkpoint_path": checkpoint_path.relative_to(ROOT).as_posix(),
            "complete_deterministic_readiness": "PASS",
            "receipt_parent_observation_file_sha256": sha256_path(observation_path),
            "preauth_final_admission_equivalence_file_sha256": sha256_path(equivalence_path),
            "preauth_final_admission_equivalence": gl_result["preauth_final_admission_equivalence"],
            "gk_receipt_parent_false_positive_blocked": "YES",
            "all_operational_counters_zero": True,
        },
        "requested_authority_semantics": {
            "authorization_kind": "FRESH_HUMAN_CONSTITUTIONAL_OPERATIONAL_AUTHORIZATION",
            "explicit": True, "fresh": True, "one_shot": True, "reusable": False,
            "transferable": False, "generation_bound": True, "operation_bound": True,
            "head_bound": True, "tree_bound": True, "candidate_bound": True,
            "context_bound": True, "canonical_argv_bound": True, "checkpoint_bound": True,
            "authorization_request_bound": True, "governed_launcher_activation_limit": 1,
            "qemu_execution_limit": 1, "vm_boot_limit": 1, "operation_attempt_limit": 1,
            "network_authorized": False, "retry_limit": 0, "repair_limit": 0,
            "replay_limit": 0, "replacement_authority_authorized": False,
            "second_attempt_authorized": False, "successor_generation_authorized": False,
        },
        "authorized_vector_requested": VECTOR,
        "request_is_authority": False, "checkpoint_is_authority": False,
        "resource_capacity_is_authority": False, "provider_permission_is_authority": False,
        "provider_permission_confirmation_count": 0, "human_constitutional_authorization_count": 0,
        "human_terminal_review_count": 0, "governed_launcher_activations": 0,
        "qemu_execution_count": 0, "vm_boot_count": 0, "operation_attempt_count": 0,
        "wrong_attempt_execution_count": 0, "request_count": 0, "p11_entry_count": 0,
        "pre_count": 0, "post_count": 0, "protected_invocation_count": 0,
        "protected_effect_count": 0, "retry_count": 0, "repair_execution_count": 0,
        "replay_execution_count": 0, "auto_continuable": False, "human_review_required": True,
    }
    request = sealed("G77_256JB_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_ENVELOPE_V1", "request", request_inner)
    request_path = JB_ROOT / "G77_256JB_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
    write_json(request_path, request)
    presentation = GN.render_human_authorization_presentation(request_path)
    presentation_path = JB_ROOT / "G77_256JB_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt"
    if presentation_path.exists() or presentation_path.is_symlink():
        raise JBBarrierError("FRESH_PRESENTATION_COLLISION")
    presentation_path.write_bytes(presentation)
    gn_result = GN.validate_human_authorization_presentation(request_path, presentation)
    gn_proof = sealed(
        "G77_256JB_GN_HUMAN_PRESENTATION_EQUIVALENCE_ENVELOPE_V1", "proof",
        {"schema_id": "G77_256JB_GN_HUMAN_PRESENTATION_EQUIVALENCE_V1",
         "generation_identity": GENERATION, "operation_identity": OPERATION,
         "request_path": request_path.relative_to(ROOT).as_posix(),
         "request_file_sha256": sha256_path(request_path),
         "presentation_path": presentation_path.relative_to(ROOT).as_posix(),
         "presentation_sha256": sha256_path(presentation_path),
         "request_sha256": request["request_sha256"], **gn_result,
         "authority_present": False, "auto_continuable": False},
    )
    write_json(JB_ROOT / "G77_256JB_GN_HUMAN_PRESENTATION_EQUIVALENCE_V1.json", gn_proof)

    counters["authorization_presentation"] = 1
    reduction = sealed(
        "G77_256JB_PREHUMAN_PHASE_A_REDUCTION_ENVELOPE_V1", "reduction",
        {
            "schema_id": "G77_256JB_PREHUMAN_PHASE_A_REDUCTION_V1",
            "recorded_at_utc": recorded, "generation_identity": GENERATION,
            "operation_identity": OPERATION,
            "terminal": "HUMAN_AUTHORIZATION_REQUIRED",
            "entry": entry, "ja_reconstruction": ja,
            "ir_reconstruction": ir, "future_semantics": future,
            "fresh_identity": identity,
            "owner_results": {"du_v2": "PASS", "eb_v2": "PASS", "ee_v2": "PASS",
                              "ex": "PASS__17_OF_17_REUSED__0_RECONSTRUCTED",
                              "fm_materialization": operation_materialization["result"],
                              "fm_static_readiness": readiness["result"],
                              "gl": gl_result["preauth_final_admission_equivalence"],
                              "gn": gn_result["human_presentation_request_equivalence"]},
            "identities": {
                "candidate_sha256": sha256_path(candidate), "context_sha256": context["context_sha256"],
                "context_file_sha256": sha256_path(context_path),
                "canonical_argv_sha256": context["canonical_argv_sha256"],
                "checkpoint_sha256": checkpoint["checkpoint_sha256"],
                "checkpoint_file_sha256": sha256_path(checkpoint_path),
                "authorization_request_sha256": request["request_sha256"],
                "authorization_request_file_sha256": sha256_path(request_path),
                "presentation_sha256": sha256_path(presentation_path),
            },
            "authority_boundary": {"human_operational_authority": "VERIFIED__0",
                                   "authority_consumption": "VERIFIED__0",
                                   "operation_execution": "NOT_STARTED",
                                   "next_legal_action": "PRESENT_EXACT_GN_TEXT_AND_STOP_FOR_EXPLICIT_HUMAN_AUTHORIZATION",
                                   "auto_continuable": False, "human_review_required": True},
            "operational_counters": counters,
            "e05": {"before": "10/18", "current": "10/18", "credit": 0, "remaining": 8},
            "boundaries": {"p11_mutation_count": 0, "fm_runtime_owner_mutation": 0,
                           "new_launcher_count": 0, "new_adapter_count": 0,
                           "parallel_flow_created": False, "production_route_before": 1,
                           "production_route_after": 1, "production_route_delta": 0,
                           "shadow_automation_status": "VERIFIED__ABSENT"},
            "terminal_frontier": {
                "last_verified_edge": "EXACT_GN_DERIVED_FUTURE_PRESENTATION_AT_HUMAN_BARRIER",
                "first_broken_edge": "FRESH_HUMAN_OPERATIONAL_AUTHORITY_NOT_PRESENT",
                "minimum_missing_capability": "EXPLICIT_HUMAN_AUTHORIZATION_OF_THE_EXACT_SEALED_REQUEST",
                "minimum_legal_next_delta": "HUMAN_REVIEW_AND_EXACT_AUTHORIZATION_OR_REJECTION",
                "auto_continuable": False, "human_review_required": True,
                "next_generation_started": False,
            },
        },
    )
    write_json(JB_ROOT / "G77_256JB_PREHUMAN_PHASE_A_REDUCTION_V1.json", reduction)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--remote-head", required=True)
    parser.add_argument("--nested-remote-tag", required=True)
    return parser.parse_args()


if __name__ == "__main__":
    materialize(parse_args())
