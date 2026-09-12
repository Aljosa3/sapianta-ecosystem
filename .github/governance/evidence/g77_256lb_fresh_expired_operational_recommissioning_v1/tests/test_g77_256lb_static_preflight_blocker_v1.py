from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[5]
LB = Path(
    ".github/governance/evidence/"
    "g77_256lb_fresh_expired_operational_recommissioning_v1"
)
FORMALIZER = LB / "analysis/G77_256LB_STATIC_PREFLIGHT_BLOCKER_FORMALIZER_V1.py"
REDUCTION = LB / "G77_256LB_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
REPORT = LB / "G77_256LB_G48_IMPLEMENTATION_REPORT_V1.md"


def load_formalizer():
    specification = importlib.util.spec_from_file_location(
        "g77_256lb_static_preflight_blocker", ROOT / FORMALIZER
    )
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


F = load_formalizer()


def load_reduction() -> tuple[dict, dict]:
    raw = (ROOT / REDUCTION).read_bytes()
    envelope = json.loads(raw)
    assert raw == F.canonical_bytes(envelope)
    reduction = envelope["reduction"]
    assert envelope["reduction_sha256"] == hashlib.sha256(
        F.canonical_bytes(reduction)
    ).hexdigest()
    return envelope, reduction


def test_reduction_is_deterministic_canonical_and_sealed() -> None:
    envelope, _ = load_reduction()
    expected = F.build_reduction()
    assert envelope == {
        "schema_id": "G77_256LB_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_ENVELOPE_V1",
        "reduction": expected,
        "reduction_sha256": hashlib.sha256(F.canonical_bytes(expected)).hexdigest(),
    }


def test_exact_current_and_presented_digests_are_authenticated() -> None:
    _, reduction = load_reduction()
    blocker = reduction["static_blocker"]
    assert blocker["expected_launcher_adapter_digest"] == (
        "df87b85f40ab9b6a286c8114c931cedc90f485c0e9992271aef92cbf1549e344"
    )
    assert blocker["presented_cloud_init_adapter_digest"] == (
        "f24d696ee3ab1f1b5d5feef2fa29e155e971f1aa1b8d890c98734011fb40e1d7"
    )
    assert blocker["expected_launcher_adapter_digest"] != blocker[
        "presented_cloud_init_adapter_digest"
    ]
    assert blocker["mismatch"].startswith("VERIFIED__")


def test_nocloud_user_data_is_exact_jx_cloud_init_projection() -> None:
    _, reduction = load_reduction()
    cloud = ROOT / reduction["static_blocker"]["generated_projection"]
    seed = ROOT / reduction["static_blocker"]["sealed_or_hashed_artifact"]
    projected = subprocess.check_output(
        ["isoinfo", "-i", str(seed), "-R", "-x", "/user-data"],
        stderr=subprocess.DEVNULL,
    )
    assert projected == cloud.read_bytes()
    assert reduction["static_blocker"]["nocloud_user_data_equals_cloud_init"] == (
        "VERIFIED"
    )


def test_failure_class_and_convergence_do_not_expand_capability_scope() -> None:
    _, reduction = load_reduction()
    classification = reduction["classification"]
    assert classification["failure_class"] == "HARNESS_OR_TEST_ARTIFACT"
    assert classification["new_capability_required"].startswith("VERIFIED__NO")
    assert reduction["convergence"]["authenticated_explanation"].startswith(
        "C__EXISTING_JX_PROJECTION_BECAME_STALE_AT_KZ"
    )
    assert reduction["convergence"]["la_proof_invalidated"].startswith(
        "VERIFIED__NO"
    )


def test_cross_vector_reuse_preserves_vector_specific_defect_scope() -> None:
    _, reduction = load_reduction()
    reuse = reduction["cross_vector_reuse_assessment"]
    assert reuse["applicable_vectors"] == [
        "EXPIRED",
        "FUTURE",
        "WRONG_ATTEMPT",
        "WRONG_CONTRACT",
        "WRONG_INPUT",
        "WRONG_PROVENANCE",
    ]
    assert reuse["affected_vectors"] == ["EXPIRED"]
    assert reuse["shared_defect"].startswith("VERIFIED__NO")
    assert reuse["shared_required_delta"].startswith("VERIFIED__NO")
    assert reuse["authority_transfer"] == "VERIFIED__NO"


def test_no_authority_operation_repair_retry_or_credit() -> None:
    _, reduction = load_reduction()
    assert not any(reduction["operational_counters"].values())
    assert reduction["lifecycle_decision"]["selected_scope"].startswith(
        "A__LB_DISCOVERY"
    )
    assert reduction["e05"] == {
        "state": "VERIFIED__11_OF_18",
        "frontier": "VERIFIED__7_UNSATISFIED_OF_18",
        "expired_status": "NOT_PROVEN_OPERATIONALLY",
        "current_generation_credit": "VERIFIED__0",
    }
    assert reduction["reuse"] == {
        "ex_reused": "VERIFIED__17_OF_17",
        "ex_reconstructed": "VERIFIED__0",
    }
    assert reduction["auto_continuable"] is False
    assert reduction["human_review_required"] is True


def test_lb_mutation_is_evidence_only_and_readiness_is_blocked() -> None:
    _, reduction = load_reduction()
    assert reduction["architecture"] == {
        "production_mutation": 0,
        "p11_mutation": 0,
        "new_owner": 0,
        "new_route": 0,
        "new_registry": 0,
        "new_generic_abstraction": 0,
        "new_constitutional_concept": 0,
        "parallel_flow": "NO",
        "production_route": "1_TO_1",
    }
    assert reduction["frontier"]["fresh_operational_attempt_readiness"] == (
        "NOT_READY"
    )
    assert reduction["frontier"]["static_pre_operational_chain_complete"].startswith(
        "NOT_PROVEN__"
    )


def test_g48_structure_and_python_syntax() -> None:
    report = (ROOT / REPORT).read_text(encoding="utf-8")
    assert re.findall(r"^# .+$", report, flags=re.MULTILINE) == [
        "# 1. Implementation Summary",
        "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment",
        "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary",
        "# 6. Certification Verdict",
    ]
    assert re.findall(r"^\d+\. .+\?$", report, flags=re.MULTILINE) == [
        "1. Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?",
        "2. Katere nove zmogljivosti (če sploh) nastanejo?",
        "3. Ali katera obstoječa zmogljivost postane nedosegljiva?",
        "4. Ali implementacija ustvarja vzporedni tok?",
        "5. Ali zmanjšuje ali povečuje število produkcijskih poti?",
    ]
    for path in (FORMALIZER, Path(__file__).resolve().relative_to(ROOT)):
        ast.parse((ROOT / path).read_text(encoding="utf-8"))
