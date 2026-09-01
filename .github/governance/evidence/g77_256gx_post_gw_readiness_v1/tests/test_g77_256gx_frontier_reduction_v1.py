#!/usr/bin/env python3
"""Repository-only regression for the post-GW E05 frontier reduction."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

import pytest


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
REDUCTION_PATH = ROOT / (
    ".github/governance/evidence/g77_256gx_post_gw_readiness_v1/"
    "G77_256GX_SPCE_TERMINAL_FRONTIER_REDUCTION_V1.json"
)
GF_PATH = ROOT / (
    ".github/governance/evidence/g77_256gf_post_commit_live_binding_v1/binding/"
    "G77_256GF_POST_COMMIT_LIVE_EXECUTION_BINDING_V1.py"
)
EM_PATH = ROOT / (
    ".github/governance/evidence/g77_256em_post_ek_frontier_reduction_v1/"
    "G77_256EM_SPCE_PHASE_D_REDUCTION_CHECKPOINT_V1.json"
)
FA_PATH = ROOT / (
    ".github/governance/evidence/g77_256fa_consumed_operational_v1/"
    "G77_256FA_SPCE_FINAL_EXECUTION_SEAL_V1.json"
)
GV_PATH = ROOT / (
    ".github/governance/evidence/g77_256gv_wrong_attempt_operational_v1/"
    "G77_256GV_SPCE_TERMINAL_REDUCTION_V1.json"
)
GW_TEST = ROOT / (
    ".github/governance/evidence/g77_256gw_host_checkpoint_serialization_boundary_v1/"
    "tests/test_g77_256gw_future_host_checkpoint_owner_binding_v1.py"
)
REPORT_PATH = ROOT / (
    "docs/governance/G77_256GX_FRESH_WORKER_POST_GW_E05_FRONTIER_REDUCTION_V1.md"
)
SATISFIED = {
    "POSITIVE_AUTHORITY_BASELINE",
    "STATE_TRANSITION",
    "CONCURRENCY",
    "UNKNOWN",
    "WRONG_CALLER",
    "CONSUMED",
    "WRONG_ATTEMPT",
}
REMAINING = {
    "AMBIGUOUS",
    "STALE",
    "FUTURE",
    "EXPIRED",
    "REVOKED",
    "SUPERSEDED",
    "WRONG_SCOPE",
    "WRONG_INPUT",
    "WRONG_PROVENANCE",
    "WRONG_CONTRACT",
    "COHERENT_COPY",
}
COMMITTED_VECTOR_CASE_CLASSES = {
    "E05_NEGATIVE_AUTHORITY_CONSUMED",
    "E05_NEGATIVE_AUTHORITY_UNKNOWN",
    "E05_NEGATIVE_AUTHORITY_WRONG_ATTEMPT",
    "E05_NEGATIVE_AUTHORITY_WRONG_CALLER",
}


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def parse_unique(path: Path) -> Any:
    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result

    return json.loads(path.read_bytes(), object_pairs_hook=unique)


def load_unique(path: Path) -> dict[str, Any]:
    value = parse_unique(path)
    assert isinstance(value, dict)
    return value


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def selected_case_classes(value: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        selected = value.get("selected_case")
        if isinstance(selected, dict) and isinstance(selected.get("case_class"), str):
            found.add(selected["case_class"])
        for child in value.values():
            found.update(selected_case_classes(child))
    elif isinstance(value, list):
        for child in value:
            found.update(selected_case_classes(child))
    return found


def test_exact_gw_entry_checkpoint_and_lineage_are_committed_ancestors() -> None:
    assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip() == (
        "8bf25e396a92582d4a6193dcff0cbb6e1df49dc8"
    )
    assert subprocess.check_output(
        ["git", "rev-parse", "HEAD^{tree}"], cwd=ROOT, text=True
    ).strip() == "40f459bbe73e315584fa10db9fc7883897061e4a"
    ancestors = (
        "e3068a2c23b98421f3bac020a1663951966cfe2a",
        "9f22ffe33626db267460fd731ad3fd23b7cbfbd5",
        "de2fcd66f61e3263e243949f18b0a2cef3a94f8b",
        "b93d7f13e20bca0f4018a76732d50d2686051fd9",
        "394ac2f0776a49d6ac1afabc1e21cc7fee6f7994",
        "84a5f0b34ac400603051b92c923bdc4ef29cd41b",
        "1357c5194fefadfdbcb4fb633f5d2bdf9aec3945",
        "99d8e889ae36d75af9f64e3db977aa452d83dd1e",
        "39939a2146f3f3ddbcb43bc757b945ebc772f7e9",
        "5eddad9cfaec82f2d0cd67258138bd773983d939",
        "49061f145736c9cdddbe7a54c5d8d3e7a5711729",
        "9dc91fc93cb0d5131ecf2350211b106c60bcead5",
        "0b8d73800c619a2659beab57563728d0b9104286",
    )
    for ancestor in ancestors:
        assert subprocess.run(
            ["git", "merge-base", "--is-ancestor", ancestor, "HEAD"], cwd=ROOT
        ).returncode == 0


def test_reduction_is_canonical_unique_key_json_with_valid_inner_seal() -> None:
    envelope = load_unique(REDUCTION_PATH)
    assert REDUCTION_PATH.read_bytes() == canonical_bytes(envelope)
    assert set(envelope) == {"schema_id", "reduction", "reduction_sha256"}
    assert hashlib.sha256(canonical_bytes(envelope["reduction"])).hexdigest() == envelope[
        "reduction_sha256"
    ]


def test_authoritative_e05_reconstruction_is_seven_of_eighteen() -> None:
    em = load_unique(EM_PATH)["checkpoint"]
    base = {
        row["obligation_id"].split("/")[-1]
        for row in em["obligation_matrix"]
        if row["satisfaction_state"] == "SATISFIED"
    }
    assert base == SATISFIED - {"CONSUMED", "WRONG_ATTEMPT"}
    assert load_unique(GV_PATH)["reduction"]["e05"] == {
        "after": "7/18",
        "before": "6/18",
        "credit_awarded": 1,
        "evidence_result": "PASS__INDEPENDENT_P11_CHE_FK_REDUCTION",
        "remaining": 11,
        "wrong_attempt_state": "SATISFIED",
    }
    fa = load_unique(FA_PATH)
    assert "CONSUMED" in json.dumps(fa)
    reduction_e05 = load_unique(REDUCTION_PATH)["reduction"]["e05"]
    assert set(reduction_e05["satisfied_obligations"]) == SATISFIED
    assert set(reduction_e05["remaining_obligations"]) == REMAINING
    assert reduction_e05["total"] == 18
    assert reduction_e05["satisfied_count"] == 7
    assert reduction_e05["remaining_count"] == 11
    assert reduction_e05["before"] == reduction_e05["after"] == "7/18"
    assert reduction_e05["credit_awarded"] == 0


def test_no_remaining_vector_has_a_committed_selected_case_or_python_producer() -> None:
    evidence_root = ROOT / ".github/governance/evidence"
    found_case_classes: set[str] = set()
    for path in evidence_root.rglob("*.json"):
        if "g77_256gx_post_gw_readiness_v1" in path.parts:
            continue
        value = parse_unique(path)
        if not isinstance(value, dict):
            continue
        found_case_classes.update(selected_case_classes(value))
    assert found_case_classes & {
        f"E05_NEGATIVE_AUTHORITY_{vector}" for vector in REMAINING
    } == set()
    assert found_case_classes & COMMITTED_VECTOR_CASE_CLASSES == COMMITTED_VECTOR_CASE_CLASSES

    for path in evidence_root.rglob("*.py"):
        if "g77_256gx_post_gw_readiness_v1" in path.parts:
            continue
        source = path.read_text(encoding="utf-8", errors="replace")
        for vector in REMAINING:
            assert f"E05_NEGATIVE_AUTHORITY_{vector}" not in source
            assert f"NEGATIVE_AUTHORITY/{vector}" not in source


def test_scanner_skips_only_valid_non_object_json_and_rejects_malformed_json(
    tmp_path: Path,
) -> None:
    argv_path = ROOT / (
        ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/raw/"
        "G77_256FM_QEMU_ARGV_V1.json"
    )
    assert isinstance(parse_unique(argv_path), list)
    duplicate = tmp_path / "duplicate.json"
    duplicate.write_text('{"evidence":1,"evidence":2}\n', encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate JSON key"):
        parse_unique(duplicate)


def test_gf_rebinds_one_wrong_attempt_template_and_rejects_relabeling() -> None:
    gf = load_module(GF_PATH, "g77_256gx_gf_review")
    template = gf.authenticate_certified_template(ROOT)
    assert template["manifest"]["selected_case"]["case_class"] == (
        "E05_NEGATIVE_AUTHORITY_WRONG_ATTEMPT"
    )
    assert "WRONG_ATTEMPT" in template["manifest"]["generation_identity"]
    relabeled = deepcopy(template)
    relabeled["manifest"]["selected_case"] = {
        "case_class": "E05_NEGATIVE_AUTHORITY_WRONG_INPUT",
        "case_id": "G77_256GX_SYNTHETIC_WRONG_INPUT_DENIAL_001",
    }
    relabeled["manifest_sha256"] = hashlib.sha256(
        canonical_bytes(relabeled["manifest"])
    ).hexdigest()
    with pytest.raises(gf.LiveBindingError, match="CANDIDATE_SEMANTICS_CHANGED"):
        gf.validate_candidate_semantics(relabeled, template)


def test_gw_owner_binding_and_historical_gv_immutability_remain_preserved() -> None:
    source = GW_TEST.read_text(encoding="utf-8")
    assert "HOST_PRE_TEARDOWN" in source and "HOST_TEARDOWN" in source
    assert "owner.persist(" in source and "owner.authenticate_path(" in source
    assert "G77_256GV_SPCE_HOST_PRE_TEARDOWN_CHECKPOINT_V1.json" in source
    assert "G77_256GV_SPCE_HOST_TEARDOWN_CHECKPOINT_V1.json" in source


def test_terminal_control_is_fail_closed_and_zero_operation() -> None:
    reduction = load_unique(REDUCTION_PATH)["reduction"]
    assert reduction["preoperational_readiness"]["status"] == "NOT_PROVEN"
    assert reduction["e05"]["selected_e05_obligation"].startswith("NOT_PROVEN")
    assert reduction["e05"]["preferred_next_development_candidate"].startswith(
        "WRONG_INPUT__VERIFIED"
    )
    assert set(reduction["operational_counters"].values()) == {0}
    assert reduction["next_development_specification"]["human_review_required"] is True
    assert reduction["next_development_specification"]["auto_continuable"] is False
    assert reduction["reuse_impact"]["production_route_delta"] == 0


def test_g48_report_has_exactly_six_sections_and_matches_terminal_reduction() -> None:
    report = REPORT_PATH.read_text(encoding="utf-8")
    headings = [line for line in report.splitlines() if line.startswith("# ")]
    assert headings == [
        "# 1. Implementation Summary",
        "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment",
        "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary",
        "# 6. Certification Verdict",
    ]
    reduction = load_unique(REDUCTION_PATH)["reduction"]
    assert reduction["terminal_control"]["verdict"] in report
    assert "PREFERRED_NEXT_DEVELOPMENT_CANDIDATE = WRONG_INPUT" in report
    assert "SAME_WORKER_PROVIDER_RESET_RESUME" in report
