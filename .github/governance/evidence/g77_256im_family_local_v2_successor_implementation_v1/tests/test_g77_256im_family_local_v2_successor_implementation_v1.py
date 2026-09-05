from __future__ import annotations

import ast
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
IM_ROOT = ROOT / ".github/governance/evidence/g77_256im_family_local_v2_successor_implementation_v1"
FORMALIZER = IM_ROOT / "analysis/G77_256IM_FAMILY_LOCAL_V2_IMPLEMENTATION_GATE_FORMALIZER_V1.py"
TERMINAL = IM_ROOT / "G77_256IM_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
REPORT = IM_ROOT / "G77_256IM_G48_IMPLEMENTATION_REPORT_V1.md"


def _load():
    spec = importlib.util.spec_from_file_location("g77_256im_gate", FORMALIZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


IM = _load()


def test_exact_il_entry_ancestry_remote_tracking_and_nested_authority() -> None:
    entry = IM.authenticate_entry(ROOT)
    assert (entry["head"], entry["tree"], entry["remote_tracking_head"]) == (IM.IL_HEAD, IM.IL_TREE, IM.IL_HEAD)
    assert entry["index"] == ""
    assert entry["nested"]["head"] == IM.NESTED_HEAD
    assert entry["nested"]["branch"] == entry["nested"]["status"] == ""


def test_committed_il_bytes_blobs_canonical_seal_and_frontier_reconstruct() -> None:
    result = IM.reconstruct_il(ROOT)
    assert result["status"] == "VERIFIED"
    assert result["artifact_count"] == 4
    assert result["canonical_json"] == result["inner_seal"] == "VERIFIED"
    assert result["frontier"]["successor_version_identifier"] == "VERIFIED__EXACT_V2"


def test_human_option_b_identity_filesystem_and_dispatch_decisions_bind() -> None:
    policy = IM.human_decisions()
    assert policy["schema_selection"].startswith("B__NESTED")
    assert (policy["major"], policy["semver"], policy["identity_suffix"]) == (2, "2.0.0", "V2")
    assert policy["filesystem_layout"].startswith("VERSIONED_SIBLING")
    assert policy["dispatch_owners"] == {"DU": "DU_FAMILY_LOCAL", "EB": "EB_FAMILY_LOCAL", "EE": "EE_FAMILY_LOCAL"}
    assert policy["human_operational_authority"] == 0


def test_six_v2_counterpart_owner_files_and_sibling_namespaces_derive() -> None:
    result = IM.derive_file_set(ROOT)
    assert result["namespace_set"] == {
        "DU": IM.DU_V2.as_posix(), "EB": IM.EB_V2.as_posix(), "EE": IM.EE_V2.as_posix()
    }
    assert result["derivable_v2_owner_file_count"] == 6
    assert len(result["derivable_v2_owner_files"]) == 6
    assert all(row["create_or_modify"] == "CREATE" for row in result["derivable_v2_owner_files"])
    assert all(row["v2_identity"].endswith("V2") for row in result["derivable_v2_owner_files"])


def test_v1_architecture_requires_no_separate_profile_or_du_producer_file() -> None:
    result = IM.derive_file_set(ROOT)
    assert result["embedded_profile_representation"].startswith("VERIFIED")
    assert result["separate_du_producer_file"].startswith("NOT_APPLICABLE")


def test_dispatch_family_is_unique_but_exact_file_realization_is_not() -> None:
    result = IM.derive_file_set(ROOT)
    assert result["dispatch_owner_family_assignment"] == "VERIFIED__DU_EB_EE_FAMILY_LOCAL"
    assert result["dispatch_realization_count_per_family"] == 2
    assert set(result["dispatch_realization_alternatives"]) == {"DU", "EB", "EE"}
    for alternatives in result["dispatch_realization_alternatives"].values():
        assert {row["shape"] for row in alternatives} == {
            "DISTINCT_DISPATCH_OWNER_MODULE", "V2_VALIDATOR_OWNS_EXPLICIT_DISPATCH_ENTRYPOINT"
        }
    assert result["dispatcher_identity_status"].startswith("NOT_PROVEN")


def test_exact_file_set_and_owner_uniqueness_fail_closed() -> None:
    result = IM.derive_file_set(ROOT)
    assert result["exact_implementation_file_set"].startswith("NOT_PROVEN")
    assert result["owner_uniqueness_status"].startswith("NOT_PROVEN")
    assert result["unowned_file_count"].startswith("NOT_PROVEN")
    assert result["owner_conflict_count"].startswith("NOT_PROVEN")


def test_preimplementation_gate_rejects_before_materialization() -> None:
    gate = IM.preimplementation_gate(ROOT)
    assert gate["predicates"]["exact_v2_sibling_namespaces"] == "VERIFIED"
    assert gate["predicates"]["exact_implementation_file_set"].startswith("NOT_PROVEN")
    assert gate["result"] == "REJECT__IMPLEMENTATION_FORBIDDEN"
    assert gate["implementation_entered"] is False


def test_no_v2_owner_directory_was_materialized() -> None:
    assert not IM.DU_V2.exists()
    assert not IM.EB_V2.exists()
    assert not IM.EE_V2.exists()


def test_v1_p11_fm_route_and_authority_boundaries_remain_zero_delta() -> None:
    reduction = IM.terminal_reduction(ROOT)
    assert reduction["compatibility"]["v1_semantics_reinterpreted"] == "VERIFIED__NO"
    assert reduction["compatibility"]["v1_schema_mutation_count"] == "VERIFIED__0"
    assert reduction["boundaries"]["p11_core_change_count"] == "VERIFIED__0"
    assert reduction["boundaries"]["fm_runtime_owner_mutation"] == "VERIFIED__0"
    assert reduction["boundaries"]["production_route_delta"] == "VERIFIED__0"
    assert reduction["boundaries"]["global_version_registry"] == "VERIFIED__NO"


def test_runtime_target_and_certification_baseline_remain_separate() -> None:
    provenance = IM.terminal_reduction(ROOT)["provenance"]
    assert provenance["runtime_target"] == {"head": IM.IF_HEAD, "tree": IM.IF_TREE}
    assert provenance["certification_baseline"] == {"head": IM.IL_HEAD, "tree": IM.IL_TREE}
    assert provenance["runtime_target"] != provenance["certification_baseline"]
    assert subprocess.check_output(["git", "rev-parse", f"{IM.IF_HEAD}^{{tree}}"], cwd=ROOT, text=True).strip() == IM.IF_TREE
    assert subprocess.check_output(["git", "rev-parse", f"{IM.IL_HEAD}^{{tree}}"], cwd=ROOT, text=True).strip() == IM.IL_TREE


def test_future_vector_is_preserved_and_vector_neutral() -> None:
    future = IM.terminal_reduction(ROOT)["future_semantics"]
    assert (future["evaluation"], future["valid_from"], future["valid_until"]) == (500, 600, 1000)
    assert future["evaluation"] < future["valid_from"] < future["valid_until"]
    assert future["future_semantic_mutation_count"] == future["wall_clock_dependency_count"] == "VERIFIED__0"


def test_ex_reuse_and_terminal_b_control_are_exact() -> None:
    reduction = IM.terminal_reduction(ROOT)
    assert reduction["ex"] == {
        "ex_reused": "VERIFIED__17_OF_17", "ex_reconstructed": "VERIFIED__0",
        "proof_reuse_efficiency": "VERIFIED__EX_17_OF_17_REUSED__0_RECONSTRUCTED",
    }
    control = reduction["terminal_control"]
    assert control["v2_implementation_status"] == "NOT_PROVEN__IMPLEMENTATION_BLOCKED"
    assert control["minimum_legal_next_delta"] == "HUMAN_GOVERNANCE_DECISION_REQUIRED"
    assert control["auto_continuable"] is control["next_generation_started"] is False
    assert control["human_review_required"] is True


def test_operational_counters_and_e05_remain_zero_and_10_of_18() -> None:
    reduction = IM.terminal_reduction(ROOT)
    assert set(reduction["operational_counters"].values()) == {0}
    assert reduction["e05"] == {"before": "10/18", "after": "10/18", "satisfied": 10, "remaining": 8, "credit": 0}


def test_terminal_is_canonical_duplicate_safe_and_inner_sealed(tmp_path: Path) -> None:
    envelope = IM.load_canonical(TERMINAL)
    assert TERMINAL.read_bytes() == IM.canonical_bytes(envelope)
    assert envelope["reduction_sha256"] == IM.sha256_bytes(IM.canonical_bytes(envelope["reduction"]))
    assert envelope == IM.terminal_envelope(ROOT)
    duplicate = tmp_path / "duplicate.json"
    duplicate.write_text('{"x":1,"x":2}\n')
    with pytest.raises(IM.IMGateError, match="DUPLICATE_JSON_KEY"):
        IM.load_canonical(duplicate)


def test_ast_report_headings_and_mutation_scope() -> None:
    tree = ast.parse(FORMALIZER.read_text())
    assert any(isinstance(node, ast.FunctionDef) and node.name == "preimplementation_gate" for node in ast.walk(tree))
    headings = [line for line in REPORT.read_text().splitlines() if line.startswith("# ")]
    assert headings == [
        "# 1. Implementation Summary", "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment", "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary", "# 6. Certification Verdict",
    ]
    status = subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=all"], cwd=ROOT, text=True).splitlines()
    assert status and all(line[3:].startswith(IM.IM_ROOT.as_posix() + "/") for line in status)
    assert subprocess.check_output(["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True) == ""


def test_direct_execution_has_no_readiness_or_operational_path() -> None:
    result = subprocess.run([sys.executable, str(FORMALIZER)], cwd=ROOT, text=True, capture_output=True)
    assert result.returncode == 2
    assert result.stdout == ""
    assert "NO_OPERATIONAL_PATH" in result.stderr
