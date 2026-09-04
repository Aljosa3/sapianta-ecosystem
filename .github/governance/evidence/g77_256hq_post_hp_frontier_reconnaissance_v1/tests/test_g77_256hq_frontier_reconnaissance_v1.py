from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[5]
EVIDENCE = ROOT / (
    ".github/governance/evidence/"
    "g77_256hq_post_hp_frontier_reconnaissance_v1/"
    "G77_256HQ_E05_FRONTIER_INVENTORY_V1.json"
)
REPORT = ROOT / "docs/governance/G77_256HQ_POST_HP_E05_FRONTIER_RECONNAISSANCE_V1.md"
HP = ROOT / (
    ".github/governance/evidence/g77_256hp_wrong_input_operational_v1/"
    "G77_256HP_SPCE_TERMINAL_REDUCTION_V1.json"
)
EX = ROOT / (
    ".github/governance/evidence/g77_256ex_common_substrate_certification_v1/"
    "G77_256EX_P11_SPCE_COMMON_SUBSTRATE_CERTIFICATION_V1.json"
)
P11 = ROOT / "tests/p11_da_operational_consumer_v1.py"
EXPECTED_HEAD = "fc7c4ad58722ac280fd3a6bed6bd7f41856c4ffb"
EXPECTED_TREE = "a5381bf86e2e63c15dc41e6516bcf6190abd7878"
EXPECTED_REMAINING = {
    "AMBIGUOUS",
    "STALE",
    "FUTURE",
    "EXPIRED",
    "REVOKED",
    "SUPERSEDED",
    "WRONG_SCOPE",
    "WRONG_PROVENANCE",
    "WRONG_CONTRACT",
    "COHERENT_COPY",
}
REQUIRED_INVENTORY_FIELDS = {
    "obligation_id",
    "obligation_status",
    "authoritative_spec_source",
    "ex_reuse",
    "ex_reconstruction_required",
    "existing_producer",
    "existing_reducer",
    "existing_semantic_vector",
    "existing_adapter",
    "existing_context_support",
    "existing_runtime_projection_support",
    "existing_bootstrap_support",
    "existing_guest_harness_support",
    "existing_authority_presentation_support",
    "existing_pre_support",
    "existing_fm_route_support",
    "existing_qemu_route_support",
    "existing_evidence_normalization_support",
    "existing_independent_reduction_support",
    "existing_test_support",
    "production_owner_change_required",
    "new_runtime_owner_required",
    "new_authority_layer_required",
    "new_production_route_required",
    "new_generic_framework_required",
    "new_semantic_mutation_required",
    "dependent_recomputation_required",
    "post_commit_live_binding_required",
    "new_operational_proof_required",
    "known_historical_evidence",
    "known_blocker",
    "unknown_blocker_risk",
    "expected_reuse_class",
    "expected_new_infrastructure_class",
    "expected_proof_delta_class",
    "expected_operational_complexity_class",
    "expected_generation_distance_to_credit",
    "capability_reuse_level",
    "proof_reuse_level",
    "semantic_delta_size",
    "infrastructure_delta_size",
    "production_route_delta",
    "authority_layer_delta",
    "runtime_owner_delta",
    "expected_preoperational_generation_count",
    "expected_operational_attempt_count",
    "expected_total_generation_distance",
}


def _git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def _no_duplicate_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    value: dict[str, object] = {}
    for key, item in pairs:
        if key in value:
            raise AssertionError(f"duplicate JSON key: {key}")
        value[key] = item
    return value


def _load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_no_duplicate_object)
    assert isinstance(value, dict)
    return value


def _canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


def test_entry_and_all_bound_sources_authenticate_without_operation() -> None:
    evidence = _load(EVIDENCE)
    assert _git("rev-parse", "HEAD") == EXPECTED_HEAD == evidence["entry"]["head"]
    assert _git("rev-parse", "HEAD^{tree}") == EXPECTED_TREE == evidence["entry"]["tree"]
    assert _git("diff", "--cached", "--name-only") == ""
    assert _git("merge-base", "--is-ancestor", evidence["entry"]["stable_ancestry_anchor"], "HEAD") == ""
    for binding in evidence["authoritative_sources"]:
        path = ROOT / binding["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == binding["sha256"]
        assert _git("rev-parse", f"HEAD:{binding['path']}") == binding["git_blob"]


def test_hp_terminal_reduction_authenticates_eight_of_eighteen() -> None:
    evidence = _load(EVIDENCE)
    hp = _load(HP)["reduction"]
    expected = evidence["hp_terminal_authentication"]
    assert hp["generation_identity"].startswith("G77_256HP_")
    assert hp["operation_identity"] == expected["operation"]
    assert hp["e05"] == {"after": "8/18", "before": "7/18", "credit": 1}
    assert hp["reducers"]["authoritative_gy_reducer_status"] == "VERIFIED"
    assert hp["reducers"]["independent_reducer_status"] == "VERIFIED"
    assert hp["reducers"]["reducer_agreement_status"] == "VERIFIED"
    assert hp["request_entry_invocation_effect_separation"] == {
        "p11_entry": 0,
        "protected_effect": 0,
        "protected_invocation": 0,
        "request": 1,
    }
    assert hp["proof_reuse"] == {"ex_reconstructed": 0, "ex_reused": "17/17"}


def test_authoritative_set_difference_and_complete_capability_inventory() -> None:
    evidence = _load(EVIDENCE)
    assert EVIDENCE.read_bytes() == _canonical_bytes(evidence)
    frontier = evidence["e05_frontier"]
    required = set(frontier["authoritative_required_set"])
    satisfied = set(frontier["verified_satisfied_set"])
    remaining = set(frontier["remaining_constitutional_frontier"])
    assert len(required) == 18
    assert len(satisfied) == 8
    assert required - satisfied == remaining == EXPECTED_REMAINING
    inventory = evidence["obligations"]
    assert len(inventory) == 10
    assert {item["obligation_id"].rsplit("/", 1)[-1] for item in inventory} == EXPECTED_REMAINING
    assert all(REQUIRED_INVENTORY_FIELDS <= set(item) for item in inventory)
    assert all(item["obligation_status"] == "VERIFIED__UNSATISFIED" for item in inventory)


def test_ex_and_p11_support_are_authenticated_without_claim_or_invocation() -> None:
    evidence = _load(EVIDENCE)
    ex = _load(EX)["certificate"]
    matrix = ex["component_certification_matrix"]
    assert len(matrix) == 22
    assert {item["component_id"] for item in matrix} == set(range(1, 23))
    assert ex["component_counts"] == {
        "CERTIFIED": 17,
        "EVIDENCE_SUPPORTED": 0,
        "REQUIRES_HARDENING": 2,
        "VECTOR_SPECIFIC": 3,
    }
    assert sum(item["proposed_ex_classification"] == "CERTIFIED" for item in matrix) == 17
    assert evidence["common_certified_substrate"]["ex_reused"] == "17/17"
    assert evidence["common_certified_substrate"]["ex_reconstructed"] == 0
    source = P11.read_text(encoding="utf-8")
    ast.parse(source, str(P11))
    for marker in (
        '"contract_identity": input_record["contract_identity"]',
        '"contract_version": input_record["contract_version"]',
        '"contract_content_sha256": input_record["contract_content_sha256"]',
        '"provenance_identity": input_record["provenance_identity"]',
        'if validated_act.authority_scope != OPERATIONAL_AUTHORITY_SCOPE:',
        'if preclaim_time >= available.binding.valid_until_unix_ns:',
        "CustodyOperation.REQUEST_REVOCATION",
        "CustodyOperation.REQUEST_SUPERSESSION",
    ):
        assert marker in source


def test_ranking_selects_one_unimplemented_candidate_and_preserves_zero_counters() -> None:
    evidence = _load(EVIDENCE)
    ranking = evidence["ranking"]
    assert [item["rank"] for item in ranking] == list(range(1, 11))
    assert {item["obligation"] for item in ranking} == EXPECTED_REMAINING
    selection = evidence["selection"]
    assert ranking[0]["obligation"] == selection["selected_next_e05_candidate"] == "WRONG_CONTRACT"
    assert evidence["terminal_control"]["selected_candidate_implemented"] is False
    assert evidence["terminal_control"]["operation_performed"] is False
    assert set(evidence["hq_counters"].values()) == {0}
    assert evidence["e05_frontier"]["before_hq"] == "8/18"
    assert evidence["e05_frontier"]["after_hq"] == "8/18"


def test_g48_report_has_exactly_six_top_level_headings() -> None:
    headings = [line for line in REPORT.read_text(encoding="utf-8").splitlines() if line.startswith("# ")]
    assert headings == [
        "# 1. Implementation Summary",
        "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment",
        "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary",
        "# 6. Certification Verdict",
    ]
