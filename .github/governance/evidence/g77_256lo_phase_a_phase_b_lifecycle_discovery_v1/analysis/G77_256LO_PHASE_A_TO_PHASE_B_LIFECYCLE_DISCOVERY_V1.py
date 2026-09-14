#!/usr/bin/env python3
"""Read-only proof of the G77-256LO committed Phase-A lifecycle gap.

The verifier never builds Human authority, calls final admission, starts an
operation, or mutates production state.  It authenticates committed evidence
showing that every satisfied operational precedent kept the admission HEAD
unchanged between its operation-specific context/Human binding and execution.
"""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
ENTRY_HEAD = "fcbbacfed226e550f7668265b0de0bde500c37d7"
ENTRY_TREE = "f80ea3829a5e039d7cb5f59d59f80b655916c3c3"
ENTRY_SUBJECT = "G77-256LN seal preauthority admission conflict terminal"
FIRST_LN = "8a18b013e5eaa87c738c504f992d0cf66df4ec49"
LM_HEAD = "027b76b3031acd2214add3e447e0197e884833ec"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
NESTED_TAG = "sapianta-system-nested-authority-3183bab-v1"
TERMINAL = (
    "A__G77_256LO_MINIMUM_PRODUCTION_CAPABILITY_GAP_PROVEN"
    "__ZERO_AUTHORITY__ZERO_OPERATION__STOP_FOR_HUMAN_REVIEW"
)
FAILURE = "sealed route target is not the current repository identity"

LO_REL = Path(
    ".github/governance/evidence/"
    "g77_256lo_phase_a_phase_b_lifecycle_discovery_v1"
)
LO = ROOT / LO_REL
REDUCTION = LO / "G77_256LO_SPCE_TERMINAL_LIFECYCLE_GAP_V1.json"
REPORT = LO / "G77_256LO_G48_IMPLEMENTATION_REPORT_V1.md"
FM_REL = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
KV_REPORT_REL = Path(
    ".github/governance/evidence/"
    "g77_256kv_current_head_operational_binding_owner_and_authority_impact_discovery_v1/"
    "G77_256KV_G48_IMPLEMENTATION_REPORT_V1.md"
)

SOURCE_HASHES = {
    FM_REL: "4bb8151e68aca89dd09e85178e177834a2811211870a37124d3991d757c7c247",
    KV_REPORT_REL: "a71bff3d6fee8171755d887e596a7040a26024bf2e66526db1f312a435b7522b",
    Path(".github/governance/evidence/g77_256li_wrong_scope_current_checkout_binding_v1/G77_256LI_G48_IMPLEMENTATION_REPORT_V1.md"): "e2d880b917930bf570ab3bbed2f11adfd40d05028ea49f046eb82ae766682a02",
    Path(".github/governance/evidence/g77_256lj_wrong_scope_stable_checkout_reuse_v1/G77_256LJ_G48_IMPLEMENTATION_REPORT_V1.md"): "03472b3dc4e663d73b7762cba9ab2587a7d635d9cdd9461d0e5b424eee5e3883",
    Path(".github/governance/evidence/g77_256lk_wrong_scope_fresh_phase_a_decision_v1/G77_256LK_G48_IMPLEMENTATION_REPORT_V1.md"): "9f8ce24cc1ee2deb1fa4e36a4f130475f2c63eeba032cb23cdfcbdfdfbc484c2",
    Path(".github/governance/evidence/g77_256ll_wrong_scope_operational_acceptance_v1/G77_256LL_G48_IMPLEMENTATION_REPORT_V1.md"): "1b53fd8e2f829fffb0f34221defbc445c88aa475bfe1e646d392ced6acc20636",
    Path(".github/governance/evidence/g77_256lm_wrong_scope_receipt_parent_phase_a_v1/G77_256LM_G48_IMPLEMENTATION_REPORT_V1.md"): "3a4ef266a257ce9be9fb3e8b9fe496400f73d5a2c703970c376e8f1fd1890af2",
    Path(".github/governance/evidence/g77_256ln_wrong_scope_operational_acceptance_v1/G77_256LN_G48_IMPLEMENTATION_REPORT_V1.md"): "59b00183d97708035e7419fc690102b315d614d956dd35afec22cd72fa417dcb",
    Path(".github/governance/evidence/g77_256lk_wrong_scope_fresh_phase_a_decision_v1/G77_256LK_SPCE_TERMINAL_REDUCTION_V1.json"): "98d809151a0824d1554c65a09fdeb762ec87fbb59b0594c082883ee1600985a9",
    Path(".github/governance/evidence/g77_256ln_wrong_scope_operational_acceptance_v1/G77_256LN_SPCE_PREAUTHORITY_TERMINAL_REDUCTION_V1.json"): "1d4d2525ee6df0067a3914d293a30755e75b83e848eed4d3a57dbbae0c0c964e",
    Path(".github/governance/evidence/g77_256ej_p11_operational_v1/G77_256EJ_SPCE_PHASE_D_FINAL_CHECKPOINT_V1.json"): "b614094319c68bd7fb5e756ce4ed4ec1f24d65d5a577052044aaea8bf9f9ccc9",
    Path(".github/governance/evidence/g77_256gv_wrong_attempt_operational_v1/G77_256GV_SPCE_TERMINAL_REDUCTION_V1.json"): "86b0db2a01c8641cb3aa81175158b77bef87f330183a86116ecaeb79e15ae705",
    Path(".github/governance/evidence/g77_256hp_wrong_input_operational_v1/G77_256HP_SPCE_TERMINAL_REDUCTION_V1.json"): "37ee9f827ac6a40ed97a1a176cabe87272553aa25d60a4e46389a262bfff21c0",
    Path(".github/governance/evidence/g77_256hx_wrong_contract_operational_v1/G77_256HX_SPCE_TERMINAL_REDUCTION_V1.json"): "630cbb4510c8f9165846de990bc9be022613f95dfb8bc31db9e372b84adaa61a",
    Path(".github/governance/evidence/g77_256ic_wrong_provenance_operational_v1/G77_256IC_SPCE_TERMINAL_REDUCTION_V1.json"): "69d1fc0e69c6d2a4dd8c40232a8d639bcdebfcc40d5a52a1241ea167e899d7bb",
    Path(".github/governance/evidence/g77_256jh_future_fresh_human_authorized_operational_denial_v1/G77_256JH_SPCE_TERMINAL_REDUCTION_V1.json"): "b29cbea1863433f3aa99f487c721411aa79340516ada395de7c0b032a7d8097b",
    Path(".github/governance/evidence/g77_256ld_fresh_expired_operational_recommissioning_v1/G77_256LD_SPCE_TERMINAL_SUCCESS_REDUCTION_V1.json"): "1b36a038fc25b8137bded389e06a8ccd8cf7e7d324d1691d1c1dc4dda3c26624",
    Path(".github/governance/evidence/g77_256gv_wrong_attempt_operational_v1/live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"): "fd357b8220d0a44b37813d63183e5c8577e4544b89afbe9f1daf8074ef3ee955",
    Path(".github/governance/evidence/g77_256gv_wrong_attempt_operational_v1/G77_256GV_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json"): "b06fb75633f496943311071298ae59d2399d1d89841d61e9909fdfcde65d63df",
    Path(".github/governance/evidence/g77_256hp_wrong_input_operational_v1/live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"): "913db3439f30b763c97627a37a24d605cae3809af7a8a38030d379aa5630b81e",
    Path(".github/governance/evidence/g77_256hp_wrong_input_operational_v1/G77_256HP_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json"): "edfaafc5a791dcbab2371ae8da51218f83e2c92ad0f24b74741ecd539de548bc",
    Path(".github/governance/evidence/g77_256hx_wrong_contract_operational_v1/live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"): "befcad4c0303638029e63aae5390755bac5d470bb9cc458f92dadd2ceabf1189",
    Path(".github/governance/evidence/g77_256hx_wrong_contract_operational_v1/G77_256HX_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json"): "69018719e197930d60ee0c7172b19055432197ccc4cab762d7fff58d05695ae9",
    Path(".github/governance/evidence/g77_256ic_wrong_provenance_operational_v1/live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"): "e4ad3878b33f91ca631424e91d461332d61d6b42a0af525aae7836d68a79c4b6",
    Path(".github/governance/evidence/g77_256ic_wrong_provenance_operational_v1/G77_256IC_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json"): "36e67a6845ff6ad1637af66ab27ff1d17380a9a978fcd96641949380bf916ee1",
    Path(".github/governance/evidence/g77_256jh_future_fresh_human_authorized_operational_denial_v1/live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"): "6e2dd8669698442aa4f1b7c2af5e50185a69d821dda3618b8ad3d0eba163aeb5",
    Path(".github/governance/evidence/g77_256jh_future_fresh_human_authorized_operational_denial_v1/G77_256JH_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json"): "d3716d9f6850f3758c107fefd1d7d65975bfb80f0cbd7f9316af4cef00bf3c10",
    Path(".github/governance/evidence/g77_256ld_fresh_expired_operational_recommissioning_v1/live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"): "913b17462f44c152058bb7418beafa21939083ac093e54a1242d78b73e2ef63a",
    Path(".github/governance/evidence/g77_256ld_fresh_expired_operational_recommissioning_v1/G77_256LD_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json"): "67d74841f798cd81f6ddce8779fbea9a7446fc5cad1bb53f493732ba821d6ad4",
}

MODERN_CASES = (
    ("WRONG_ATTEMPT", "g77_256gv_wrong_attempt_operational_v1", "G77_256GV", "9dc91fc93cb0d5131ecf2350211b106c60bcead5", "c01929747475bd3def8a140ec126f170d5432927", "7dce67ec18696ba0bad73130f3f7a84168f25277", "3cb61ec34e9593efb711dce61014dc8fdf0f6dd9"),
    ("WRONG_INPUT", "g77_256hp_wrong_input_operational_v1", "G77_256HP", "fc9bc52bbd708a40f884f2fc006ebe0e3f6e4df8", "9256a995bf9b90714e759dae98d2bed4c3de8f22", "842a0f2cccd53222d11daa698bdeab17f0aac043", "414a5f940e3b5027b6dd86c38d7a134f5c8ab0c4"),
    ("WRONG_CONTRACT", "g77_256hx_wrong_contract_operational_v1", "G77_256HX", "0e2448cb0194d6182085a671ddb28729681a1e75", "adc1453b964d05e3cf41deffcbbc0c856f99a81a", "af44f0afd02be7e21a24e962309e28f6edd17ae0", "fc949a2bbaa0a507edbc25811563dc5e13d18315"),
    ("WRONG_PROVENANCE", "g77_256ic_wrong_provenance_operational_v1", "G77_256IC", "ec2c4997ba62fbaa5e774fc9ba010f6319926c73", "887f329b030582f01a49f6c0c97f54ed4f55a818", "dfea5c58f400edb9472db37390de80a92eda2ad3", "caf8feb24ed4c072dde6c6586fd7cf60d05c4c7d"),
    ("FUTURE", "g77_256jh_future_fresh_human_authorized_operational_denial_v1", "G77_256JH", "7d33c6fb31f90514d590e39d5d410d81ee0f51b0", "b020731686b4fe47a6f2d0ec0d850ad293d1bb97", "699fcdce794ff49b6c8735602936355724ed1c90", "7c773d4b2acdf013f1b8238eabfc8eced4dd6866"),
    ("EXPIRED", "g77_256ld_fresh_expired_operational_recommissioning_v1", "G77_256LD", "98d059beaa148746d397d48bad9e898b1f9c2297", "d1aadf9da3f66b2699f9b4c32647a2fe65c060cc", "304b342e26e92f226afa01db4b4203acfa51f532", "fc0c50e4dd79e900d85d48c5c0aeb53fe9d0c937"),
)


class LOVerificationError(RuntimeError):
    pass


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(["git", *args], cwd=cwd, text=True, stderr=subprocess.DEVNULL).strip()


def is_ancestor(ancestor: str, descendant: str) -> bool:
    return subprocess.run(["git", "merge-base", "--is-ancestor", ancestor, descendant], cwd=ROOT, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0


def committed_path_absent(head: str, relative: Path) -> bool:
    return subprocess.run(["git", "cat-file", "-e", f"{head}:{relative.as_posix()}"], cwd=ROOT, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode != 0


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_bytes())
    if not isinstance(value, dict):
        raise LOVerificationError(f"JSON_ROOT_INVALID:{path}")
    return value


def sealed_inner(path: Path, key: str) -> dict[str, Any]:
    envelope = load_json(path)
    value = envelope.get(key)
    if not isinstance(value, dict) or envelope.get(f"{key}_sha256") != hashlib.sha256(canonical_bytes(value)).hexdigest():
        raise LOVerificationError(f"INNER_SEAL_INVALID:{path}")
    return value


def authenticate_entry() -> dict[str, str]:
    head = git("rev-parse", "HEAD")
    remote = git("rev-parse", f"refs/remotes/origin/{BRANCH}")
    if (
        ROOT != Path("/home/pisarna/work/sapianta-fl")
        or git("branch", "--show-current") != BRANCH
        or git("rev-parse", f"{ENTRY_HEAD}^{{tree}}") != ENTRY_TREE
        or git("show", "-s", "--format=%s", ENTRY_HEAD) != ENTRY_SUBJECT
        or not is_ancestor(LM_HEAD, ENTRY_HEAD)
        or not is_ancestor(FIRST_LN, ENTRY_HEAD)
        or not is_ancestor(ENTRY_HEAD, head)
        or not is_ancestor(ENTRY_HEAD, remote)
    ):
        raise LOVerificationError("LN_ENTRY_OR_SUCCESSOR_AUTHENTICATION_FAILED")
    dirty = git("status", "--porcelain=v1", "--untracked-files=all").splitlines()
    unexpected = [line for line in dirty if not line[3:].startswith(LO_REL.as_posix() + "/")]
    if unexpected:
        raise LOVerificationError(f"UNRELATED_MUTATION:{unexpected}")
    nested = ROOT / "sapianta_system"
    if (
        git("rev-parse", "HEAD", cwd=nested) != NESTED_HEAD
        or git("rev-parse", "HEAD^{tree}", cwd=nested) != NESTED_TREE
        or git("status", "--porcelain=v1", "--untracked-files=all", cwd=nested)
        or git("branch", "--show-current", cwd=nested)
        or git("rev-parse", f"refs/tags/{NESTED_TAG}^{{}}", cwd=nested) != NESTED_HEAD
    ):
        raise LOVerificationError("NESTED_AUTHORITY_MISMATCH")
    return {"entry_head": ENTRY_HEAD, "entry_tree": ENTRY_TREE, "current_head": head, "remote_head": remote}


def authenticate_sources() -> None:
    for relative, expected in SOURCE_HASHES.items():
        path = ROOT / relative
        if path.is_symlink() or not path.is_file() or sha256_path(path) != expected:
            raise LOVerificationError(f"SOURCE_HASH_MISMATCH:{relative}")
        if subprocess.check_output(["git", "show", f"{ENTRY_HEAD}:{relative.as_posix()}"], cwd=ROOT) != path.read_bytes():
            raise LOVerificationError(f"SOURCE_NOT_LN_COMMITTED:{relative}")


def authenticate_fm_identity_model() -> dict[str, Any]:
    source = (ROOT / FM_REL).read_text()
    tree = ast.parse(source)
    names = [node.name for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
    required = {
        "build_operation_context",
        "authenticate_current_committed_jm_route",
        "governed_checkout_identity",
        "authority_free_static_readiness",
        "validate_execution_admission",
        "validate_final_admission",
    }
    if any(names.count(name) != 1 for name in required):
        raise LOVerificationError("FM_OWNER_SET_AMBIGUOUS")
    required_fragments = (
        'raise RuntimeError("sealed route target is not the current repository identity")',
        'if context["repository_head"] != observed_head or context["repository_tree"] != observed_tree:',
        'if authorization["authorized_repository_head"] != observed_head:',
        'if authorization["authorized_repository_tree"] != observed_tree:',
        "static_readiness = authority_free_static_readiness(",
        "authenticate_current_committed_jm_route(",
    )
    if any(fragment not in source for fragment in required_fragments):
        raise LOVerificationError("FM_EXACT_ADMISSION_GUARD_MISSING")
    if "materialization_base_identity" in source or "phase_a_review_object_identity" in source:
        raise LOVerificationError("UNEXPECTED_COMMITTED_REVIEW_IDENTITY_OWNER_PRESENT")
    return {
        "phase_a_repository_identity_owner": "FM_BUILD_OPERATION_CONTEXT__repository_head_tree",
        "current_admission_identity_owner": "FM_AUTHENTICATE_CURRENT_COMMITTED_JM_ROUTE_AND_VALIDATE_EXECUTION_ADMISSION",
        "runtime_checkout_identity_owner": "FM_GOVERNED_CHECKOUT_IDENTITY",
        "constitutional_anchor_owner": "FM_CONSTITUTIONAL_ANCHOR_ANCESTRY_CHECK",
        "committed_review_object_identity_owner": "ABSENT",
        "literal_current_head_equality": "IMPLEMENTATION_OF_EXACT_REVIEWED_CODE_AND_ROUTE_AUTHORIZATION_INVARIANT",
    }


def authenticate_wrong_scope_trace() -> dict[str, Any]:
    reports = {path.name: (ROOT / path).read_text() for path in SOURCE_HASHES if path.name.endswith("G48_IMPLEMENTATION_REPORT_V1.md")}
    combined = "\n".join(reports.values())
    required = (
        "SAME_CURRENT_HEAD_TREE_MISMATCH_RECURS_WHEN_THE_BINDING_REPAIR_COMMIT_ADVANCES_HEAD",
        "current admission repository identity from stable runtime checkout identity",
        "CURRENT_REPOSITORY_HEAD = e3d046cd6ad2f9e4b5e808395d88f56cc03c5a52",
        "G77_256LL_AUTHORITY_BINDING_CONFLICT__STOP",
        "does not substitute advancing HEAD/TREE into the sealed object or rerun FM's",
        "A__G77_256LN_AUTHORITY_BINDING_CONFLICT__STOP",
    )
    if any(fragment not in combined for fragment in required):
        raise LOVerificationError("LI_TO_LN_TRACE_INCOMPLETE")
    return {
        "LI": "LITERAL_CURRENT_HEAD_REBIND_COMMIT_SELF_INVALIDATED",
        "LJ": "CURRENT_ADMISSION_AND_STABLE_RUNTIME_CHECKOUT_SEPARATED_FOR_STATIC_READINESS",
        "LK": "COMMITTED_HUMAN_REVIEWABLE_OBJECT_SEALED_PREDECESSOR_MATERIALIZATION_BASE",
        "LL": "LATER_CURRENT_CONTEXT_USED__STOPPED_PRECONSUMPTION_AT_RECEIPT_PARENT",
        "LM": "COMMITTED_OBJECT_AND_STATIC_SUCCESSOR_REPLAY_SKIPPED_OPERATIONAL_CURRENT_ADMISSION",
        "LN": "OPERATIONAL_FINAL_ADMISSION_REENTRY_REJECTED_SEALED_PREDECESSOR_IDENTITY",
    }


def authenticate_modern_precedents() -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for vector, directory, prefix, head, tree, runtime_head, runtime_tree in MODERN_CASES:
        base = Path(".github/governance/evidence") / directory
        context_rel = base / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
        handoff_rel = base / f"{prefix}_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json"
        context = load_json(ROOT / context_rel)
        handoff = sealed_inner(ROOT / handoff_rel, "authorization")
        checkout = context.get("qemu_executable_base_seed_checkout_bindings", {}).get("checkout", {})
        if (
            git("rev-parse", f"{head}^{{tree}}") != tree
            or context.get("repository_head") != head
            or context.get("repository_tree") != tree
            or checkout.get("head") != runtime_head
            or checkout.get("tree") != runtime_tree
            or handoff.get("authorized_repository_head") != head
            or handoff.get("authorized_repository_tree") != tree
            or not committed_path_absent(head, context_rel)
            or not committed_path_absent(head, handoff_rel)
        ):
            raise LOVerificationError(f"CROSS_VECTOR_IDENTITY_MISMATCH:{vector}")
        results.append({
            "vector": vector,
            "e05_status": "SATISFIED__OPERATIONAL",
            "phase_a_commit_occurred": True,
            "phase_a_preparatory_commit_occurred": True,
            "operation_specific_context_committed_before_human_decision": False,
            "operation_specific_phase_a_committed_before_phase_b": False,
            "human_decision_occurred": True,
            "phase_b_repository_relation": "SAME_COMMIT",
            "phase_b_repository_identity": f"{head}/{tree}",
            "sealed_repository_identity": f"{head}/{tree}",
            "current_admission_identity": f"{head}/{tree}",
            "runtime_checkout_identity": f"{runtime_head}/{runtime_tree}",
            "final_admission": "PASSED_BY_EXACT_CONTEXT_AUTHORITY_OBSERVED_HEAD_TREE_EQUALITY",
            "how_final_admission_passed": "EXACT_CONTEXT_AUTHORITY_OBSERVED_HEAD_TREE_EQUALITY",
            "common_infra_reusable": "YES__DISCOVERY_AND_SAME_HEAD_LIFECYCLE_ONLY",
            "operational_infra_reuse": "FM_TO_ER_TO_P11_COMMON_ROUTE__PER_VECTOR_REVALIDATION_REQUIRED",
            "vector_specific_binding": {
                "WRONG_ATTEMPT": "ATTEMPT",
                "WRONG_INPUT": "INPUT",
                "WRONG_CONTRACT": "CONTRACT",
                "WRONG_PROVENANCE": "PROVENANCE",
                "FUTURE": "TEMPORAL_FUTURE",
                "EXPIRED": "TEMPORAL_EXPIRED",
            }[vector],
            "known_defect": "NONE",
            "mechanism_reusable_for_wrong_scope": "YES_ONLY_WITH_UNCOMMITTED_OPERATION_SPECIFIC_PHASE_A_AND_NO_COMMIT_BEFORE_ADMISSION",
            "authority_transfer": "NO",
            "proof_transfer": "NO",
            "e05_credit_transfer": "NO",
        })
    return results


def authenticate_wrong_caller_precedent() -> dict[str, Any]:
    phase_d = sealed_inner(ROOT / ".github/governance/evidence/g77_256ej_p11_operational_v1/G77_256EJ_SPCE_PHASE_D_FINAL_CHECKPOINT_V1.json", "checkpoint")
    phase_a_rel = Path(".github/governance/evidence/g77_256ej_p11_operational_v1/G77_256EJ_SPCE_PHASE_A_CHECKPOINT_V1.json")
    head = "0d9b72facc30fd4ade8046607c8fb3244ba4a517"
    tree = "9e97364af99784020217ecf5f743f8822195e59d"
    if (
        phase_d.get("required_head") != head
        or phase_d.get("required_tree") != tree
        or phase_d.get("selected_e05_vector") != "WRONG_CALLER"
        or phase_d.get("final_validation") != "PASS"
        or git("rev-parse", f"{head}^{{tree}}") != tree
        or not committed_path_absent(head, phase_a_rel)
    ):
        raise LOVerificationError("WRONG_CALLER_PRECEDENT_MISMATCH")
    return {
        "vector": "WRONG_CALLER",
        "e05_status": "SATISFIED__OPERATIONAL",
        "phase_a_commit_occurred": True,
        "phase_a_preparatory_commit_occurred": True,
        "operation_specific_context_committed_before_human_decision": False,
        "operation_specific_phase_a_committed_before_phase_b": False,
        "human_decision_occurred": "GENERATION_COMMISSION__NO_CANONICAL_HUMAN_AUTHORITY_AT_D1",
        "phase_b_repository_relation": "SAME_COMMIT",
        "phase_b_repository_identity": f"{head}/{tree}",
        "sealed_repository_identity": f"{head}/{tree}",
        "current_admission_identity": f"{head}/{tree}",
        "runtime_checkout_identity": "NOT_SEPARATELY_RECORDED__PRE_FM_CONTEXT_MODEL",
        "final_admission": "D1_WRONG_CALLER_DENIAL_PRECEDED_LATER_AUTHORITY_RESOLUTION",
        "how_final_admission_passed": "D1_DENIAL_PRECEDED_LATER_AUTHORITY_RESOLUTION",
        "common_infra_reusable": "YES__PREBOOT_DENIAL_STRUCTURE_ONLY",
        "operational_infra_reuse": "P11_PREBOOT_DENIAL_ONLY__PRE_FM_AUTHORITY_MODEL",
        "vector_specific_binding": "CALLER",
        "known_defect": "NONE",
        "mechanism_reusable_for_wrong_scope": "NO__OLDER_PRE_FM_AUTHORITY_MODEL__NO_SUCCESSOR_COMMIT_PRECEDENT",
        "authority_transfer": "NO",
        "proof_transfer": "NO",
        "e05_credit_transfer": "NO",
    }


def authenticate_wrong_scope_target_lifecycle() -> dict[str, Any]:
    lk_rel = Path(
        ".github/governance/evidence/g77_256lk_wrong_scope_fresh_phase_a_decision_v1/"
        "G77_256LK_SPCE_TERMINAL_REDUCTION_V1.json"
    )
    ln_rel = Path(
        ".github/governance/evidence/g77_256ln_wrong_scope_operational_acceptance_v1/"
        "G77_256LN_SPCE_PREAUTHORITY_TERMINAL_REDUCTION_V1.json"
    )
    lm_context_rel = Path(
        ".github/governance/evidence/g77_256lm_wrong_scope_receipt_parent_phase_a_v1/"
        "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
    )
    lk = sealed_inner(ROOT / lk_rel, "reduction")
    ln = sealed_inner(ROOT / ln_rel, "reduction")
    human = ln.get("human_decision", {})
    conflict = ln.get("conflict", {})
    if (
        lk.get("phase_a", {}).get("ready_for_human_decision") is not True
        or lk.get("implementation_commit", {}).get("head")
        != "13b1979e0265ed105983a29f2983d3a8c6107491"
        or human.get("present") is not True
        or human.get("approved_decision_object_id")
        != "G77_256LM_WRONG_SCOPE_PHASE_A_DECISION_OBJECT_001"
        or conflict.get("sealed_materialization_head")
        != "ea3781b64cd8780021e8cbb5e65f6b057b1bf649"
        or conflict.get("current_admission_head") != LM_HEAD
        or not committed_path_absent("ea3781b64cd8780021e8cbb5e65f6b057b1bf649", lm_context_rel)
        or committed_path_absent("7368af35f707f75f4d0951133995013211699126", lm_context_rel)
    ):
        raise LOVerificationError("WRONG_SCOPE_TARGET_LIFECYCLE_NOT_AUTHENTICATED")
    return {
        "scope": "WRONG_SCOPE_LK_LM_LN_TARGET_LIFECYCLE_ONLY",
        "committed_operation_specific_phase_a_required": True,
        "universal_constitutional_requirement": "NOT_PROVEN",
        "evidence": "LK_AND_LM_COMMITTED_REVIEW_BYTES_PRECEDED_THE_EXACT_LN_HUMAN_DECISION",
    }


def authenticate_wrong_scope_assessment() -> dict[str, Any]:
    target = authenticate_wrong_scope_target_lifecycle()
    sealed_head = "ea3781b64cd8780021e8cbb5e65f6b057b1bf649"
    sealed_tree = "607e9dae3a562d823d64b17888c11d3e4b881e2f"
    current_head = LM_HEAD
    current_tree = "e4c5c567887bfbfa16ae98a5034cabbad29d4346"
    return {
        "vector": "WRONG_SCOPE",
        "e05_status": "UNSAT__NO_OPERATIONAL_ATTEMPT",
        "phase_a_commit_occurred": True,
        "phase_a_preparatory_commit_occurred": True,
        "operation_specific_context_committed_before_human_decision": True,
        "operation_specific_phase_a_committed_before_phase_b": True,
        "human_decision_occurred": True,
        "phase_b_repository_relation": "SUCCESSOR_COMMIT",
        "phase_b_repository_identity": f"{current_head}/{current_tree}",
        "sealed_repository_identity": f"{sealed_head}/{sealed_tree}",
        "current_admission_identity": f"{current_head}/{current_tree}",
        "runtime_checkout_identity": "f7acd5feb3dec686ca4e2cd359b63e232f6c5fbe/968704d8915edf6d524a8a7705591788d8333bdd",
        "final_admission": "NOT_PASSED__CURRENT_IDENTITY_GATE_REJECTED_PREAUTHORITY",
        "how_final_admission_passed": "DID_NOT_PASS__SEALED_AND_CURRENT_ADMISSION_IDENTITIES_DIFFERED",
        "common_infra_reusable": "YES__FM_GL_GN_FC_ER_P11_EX__DISCOVERY_ONLY",
        "operational_infra_reuse": "AUTHENTICATED_BUT_NOT_INVOKED_IN_LO",
        "vector_specific_binding": "AUTHORITY_SCOPE",
        "known_defect": "COMMITTED_PHASE_A_SEALED_IDENTITY_DIFFERS_FROM_SUCCESSOR_CURRENT_ADMISSION_IDENTITY",
        "mechanism_reusable_for_wrong_scope": "SAME_HEAD_ONLY__NOT_FOR_AUTHENTICATED_COMMITTED_OBJECT_SUCCESSOR_TARGET",
        "authority_transfer": "NO",
        "proof_transfer": "NO",
        "e05_credit_transfer": "NO",
        "target_lifecycle_requirement": target,
    }


def authenticate_kv_precedent() -> None:
    text = (ROOT / KV_REPORT_REL).read_text()
    normalized = " ".join(text.split())
    required = (
        "same repository HEAD/TREE as authority",
        "operate before committing terminal evidence",
        "there was no execution-time transition from Human authority HEAD X to execution HEAD Y",
        "do not commit between the fresh act and operational admission",
    )
    if any(fragment not in normalized for fragment in required):
        raise LOVerificationError("KV_SAME_HEAD_LIFECYCLE_PRECEDENT_MISSING")


def authenticate_zero_lo_authority_operation() -> None:
    forbidden = (
        "*HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE*",
        "*FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF*",
        "*AUTHORITY_VALIDATION_AND_CONSUMPTION*",
        "*OPERATIONAL_INVOCATION_ATTEMPT*",
        "*SERIAL_CONSOLE*",
    )
    for pattern in forbidden:
        if list(LO.rglob(pattern)):
            raise LOVerificationError(f"LO_AUTHORITY_OR_OPERATION_ARTIFACT:{pattern}")


def build_reduction() -> dict[str, Any]:
    target_lifecycle = authenticate_wrong_scope_target_lifecycle()
    assessments = [
        authenticate_wrong_scope_assessment(),
        authenticate_wrong_caller_precedent(),
        *authenticate_modern_precedents(),
    ]
    return {
        "schema_id": "G77_256LO_SPCE_TERMINAL_LIFECYCLE_GAP_V1",
        "generation": "G77-256LO",
        "terminal": TERMINAL,
        "outcome": "E__MINIMUM_PRODUCTION_CAPABILITY_GAP_PROVEN",
        "failure_novelty_and_convergence_check": {
            "failure_class": "DUPLICATE_OR_EQUIVALENT_EDGE",
            "novelty": "LI_CLASS_CURRENT_ADMISSION_IDENTITY_MISMATCH_RECURS_AT_PHASE_B__LIFECYCLE_GAP_NOW_BOUNDED",
            "affected_invariant": "SEALED_OPERATION_CONTEXT_REPOSITORY_IDENTITY_MUST_EQUAL_CURRENT_COMMITTED_ADMISSION_IDENTITY",
            "previous_closest_edge": "G77_256LI_POST_COMMIT_CURRENT_HEAD_TREE_MISMATCH",
            "semantic_difference": "COMMITTED_HUMAN_REVIEW_OBJECT_MUST_SURVIVE_SUCCESSOR_PHASE_B_WHILE_ALL_SUCCESS_PRECEDENTS_AVOIDED_THAT_BOUNDARY",
            "production_behavior_impact": "NONE__LO_IS_AUTHORITY_FREE_AND_NONOPERATIONAL",
            "new_capability_required": "YES__ONLY_FOR_COMMITTED_PHASE_A_OBJECT_TO_SUCCESSOR_PHASE_B_ADMISSION",
            "new_proof_required": "OPERATIONAL_WRONG_SCOPE_DENIAL_BEFORE_P11_ENTRY__STILL_MISSING",
            "convergence_signal": "MINIMUM_FM_OWNED_REPRESENTATION_GAP_LOCALIZED__NO_NAIVE_FIX_APPLIED",
            "repetition_pressure": "HIGH__DO_NOT_REPEAT_LITERAL_BINDING_OR_COMMIT_AFTER_HUMAN_ACT",
            "verification_amplification_risk": "HIGH_UNTIL_COMMITTED_REVIEW_AND_CURRENT_ADMISSION_ROLES_ARE_EXPLICITLY_AUTHENTICATED",
        },
        "identity_owners": authenticate_fm_identity_model(),
        "li_to_ln_trace": authenticate_wrong_scope_trace(),
        "target_lifecycle_requirement": target_lifecycle,
        "cross_vector_reuse_assessment": assessments,
        "cross_vector_precedent_count": 7,
        "cross_vector_assessment_count": 8,
        "primary_answer": {
            "existing_safe_mechanism": "COMMITTED_PREPARATORY_BASELINE__THEN_UNCOMMITTED_EXACT_CONTEXT_AND_HUMAN_ACT__NO_COMMIT_BEFORE_ADMISSION__TERMINAL_EVIDENCE_COMMIT_AFTER_OPERATION",
            "satisfies_committed_phase_a_successor_requirement": False,
            "minimum_gap": "FM_OWNED_EXPLICIT_SEPARATION_AND_VALIDATION_OF_IMMUTABLE_COMMITTED_PHASE_A_REVIEW_OBJECT_IDENTITY_FROM_EXACT_CURRENT_ADMISSION_IDENTITY_WHILE_RETAINING_GOVERNED_RUNTIME_CHECKOUT_IDENTITY",
            "minimum_gap_constraints": "NO_ARBITRARY_ANCESTRY__NO_REBIND__NO_COPY_INHERITANCE__EXACT_ALLOWED_TRANSITION_PROOF__ONE_ROUTE__ONE_OWNER__FRESH_HUMAN_ACT",
            "production_mutation_required": True,
            "implemented": False,
        },
        "non_self_invalidation": {
            "requirements_1_to_4": "PRESERVED_BY_IMMUTABLE_COMMITTED_OBJECT_AND_EXACT_HUMAN_BINDING",
            "requirement_5_successor_authentication": "NOT_SUPPORTED_BY_CURRENT_FM_REPRESENTATION",
            "requirements_6_to_15": "MANDATORY_FOR_FUTURE_HUMAN_REVIEW__NOT_WEAKENED_BY_LO",
            "all_fifteen_proven_for_existing_mechanism": False,
        },
        "security_assessment": {
            "arbitrary_ancestor_acceptance": "REJECT__STALE_CODE_AND_ANCESTRY_AS_AUTHORITY",
            "sealed_object_rebind": "REJECT__HUMAN_OBJECT_IDENTITY_VIOLATION",
            "mutable_branch_identity": "REJECT__NONIMMUTABLE_AND_REPLAY_UNSAFE",
            "fm_bypass": "REJECT__PARALLEL_ROUTE_AND_ADMISSION_BYPASS",
            "wrong_scope_only_route": "REJECT__SECOND_ROUTE_AND_OWNER_PRESSURE",
            "coherent_copy_inherits_approval": "REJECT__COPY_IS_NOT_OBJECT_IDENTITY",
            "existing_same_head_ordering": "SECURE_AND_REUSABLE__BUT_DOES_NOT_MEET_COMMITTED_PHASE_A_SUCCESSOR_REQUIREMENT",
            "future_gap_candidate": "UNIMPLEMENTED__MUST_PRESERVE_EXACT_OBJECT_CURRENT_CODE_RUNTIME_AND_ALLOWED_TRANSITION_BINDINGS",
            "new_attack_surface": "ZERO_FROM_LO__FUTURE_PRODUCTION_DESIGN_REQUIRES_SEPARATE_THREAT_REVIEW",
            "authority_impact": "ZERO_FROM_LO__NO_TRANSFER_OR_REBIND",
            "route_impact": "UNCHANGED__1_TO_1",
            "replay_impact": "UNCHANGED__ONE_SHOT_AND_ZERO_REPLAY",
            "coherent_copy_impact": "FUTURE_PROOFABILITY_PRESERVED__NO_COPY_ACCEPTANCE",
            "stale_identity_impact": "FUTURE_PROOFABILITY_PRESERVED__NO_ANCESTOR_ACCEPTANCE",
        },
        "frontier": {
            "last_verified_edge": "EXACT_LN_CURRENT_ADMISSION_CONFLICT_PLUS_SEVEN_SAME_HEAD_OPERATIONAL_PRECEDENTS_AUTHENTICATED",
            "first_broken_edge": "COMMITTED_PHASE_A_REVIEW_OBJECT_TO_SUCCESSOR_CURRENT_ADMISSION_IDENTITY_TRANSITION",
            "first_unverified_edge": "FRESH_AUTHORITY_CREATION_THEN_CONSUMPTION_AND_OPERATIONAL_WRONG_SCOPE_DENIAL",
            "minimum_missing_capability": "FM_OWNED_COMMITTED_REVIEW_IDENTITY_TO_EXACT_CURRENT_ADMISSION_TRANSITION_VALIDATION_STRONGER_THAN_ANCESTRY",
            "minimum_missing_proof": "OPERATIONAL_WRONG_SCOPE_DENIAL_BEFORE_P11_ENTRY",
            "minimum_legal_next_delta": "STOP_FOR_HUMAN_REVIEW_OF_MINIMUM_PRODUCTION_CAPABILITY_GAP",
        },
        "architecture": {
            "production_mutation": 0,
            "fm_mutation": 0,
            "p11_mutation": 0,
            "er_mutation": 0,
            "ex_mutation": 0,
            "new_owner": 0,
            "new_route": 0,
            "new_registry": 0,
            "new_generic_abstraction": 0,
            "new_constitutional_concept": 0,
            "route_count_before": 1,
            "route_count_after": 1,
        },
        "operational_counters": {
            "HUMAN_AUTHORITY_SOURCE_COUNT": 0,
            "AUTHORITY_CREATION_COUNT": 0,
            "AUTHORITY_CONSUMPTION_COUNT": 0,
            "OPERATION_ATTEMPT_COUNT": 0,
            "QEMU_START_COUNT": 0,
            "VM_START_COUNT": 0,
            "RETRY_COUNT": 0,
            "OPERATIONAL_REPLAY_COUNT": 0,
            "REPAIR_RETRY_COUNT": 0,
            "P11_ENTRY_COUNT": 0,
            "PROTECTED_INVOCATION_COUNT": 0,
            "PROTECTED_EFFECT_COUNT": 0,
        },
        "e05": {"before": "12/18", "lo_credit": 0, "after": "12/18", "wrong_scope": "UNSAT"},
        "ex": {"reused": "VERIFIED__17_OF_17", "reconstructed": "VERIFIED__0"},
        "reuse_impact_assessment": {
            "existing_certified_capabilities_reused": "LI_LJ_LK_LL_LM_LN_KV_GA_GL_FM_GN_FC_ER_P11_EX_AND_SEVEN_OPERATIONAL_PRECEDENTS_READ_ONLY",
            "new_capabilities": "NONE_IMPLEMENTED__ONE_MINIMUM_PRODUCTION_CAPABILITY_GAP_PROVEN",
            "existing_capability_unreachable": False,
            "parallel_flow": False,
            "production_route_effect": "UNCHANGED__1_TO_1",
        },
    }


def verify() -> dict[str, Any]:
    repository = authenticate_entry()
    authenticate_sources()
    authenticate_kv_precedent()
    authenticate_zero_lo_authority_operation()
    reduction = build_reduction()
    envelope = load_json(REDUCTION)
    if envelope.get("reduction") != reduction or envelope.get("reduction_sha256") != hashlib.sha256(canonical_bytes(reduction)).hexdigest():
        raise LOVerificationError("LO_REDUCTION_MISMATCH")
    return {"terminal": TERMINAL, "repository": repository, "reduction": reduction}


if __name__ == "__main__":
    print(verify()["terminal"])
