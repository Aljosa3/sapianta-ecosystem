from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[5]
JU = ROOT / ".github/governance/evidence/g77_256ju_expired_operational_v1"
REDUCER_PATH = JU / "analysis/G77_256JU_PREAUTHORIZATION_REQUEST_SCHEMA_BLOCKER_REDUCER_V1.py"
MATERIALIZER_PATH = JU / "orchestration/G77_256JU_PREAUTHORIZATION_MATERIALIZER_V1.py"
REDUCTION = JU / "G77_256JU_SPCE_PREAUTHORIZATION_BLOCKER_REDUCTION_V1.json"
REPORT = JU / "G77_256JU_G48_IMPLEMENTATION_REPORT_V1.md"


def load(path: Path, name: str):
    specification = importlib.util.spec_from_file_location(name, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


R = load(REDUCER_PATH, "g77_256ju_test_reducer")


def test_exact_entry_jt_and_stable_checkout_authenticate() -> None:
    proof = R.authenticate_boundary()
    assert proof["entry"]["head"] == R.M.HEAD
    assert proof["entry"]["tree"] == R.M.TREE
    assert proof["jt"]["terminal"] == R.M.JT_TERMINAL
    assert proof["jt"]["ex_reused"] == "VERIFIED__17_OF_17"
    assert proof["jt"]["ex_reconstructed"] == "VERIFIED__0"
    assert proof["jt"]["stable_checkout"] == {
        "head": R.M.JR_HEAD,
        "tree": R.M.JR_TREE,
    }


def test_exact_gn_schema_blocker_is_reproduced() -> None:
    proof = R.authenticate_boundary()
    assert proof["gn_rejection"] == "SEALED_REQUEST_FIELDS_INVALID"
    assert proof["request_schema_difference"] == {
        "request_extra_fields": ["expired_execution_count"],
        "request_missing_fields": ["wrong_attempt_execution_count"],
        "live_binding_extra_fields": [
            "expired_adapter_sha256",
            "temporal_binding_sha256",
        ],
        "live_binding_missing_fields": ["du", "eb", "ee"],
    }


def test_reduction_is_canonical_inner_sealed_and_reproducible() -> None:
    raw = REDUCTION.read_bytes()
    envelope = json.loads(raw, object_pairs_hook=R.unique_object)
    assert raw == R.canonical_bytes(envelope)
    assert envelope["reduction_sha256"] == hashlib.sha256(
        R.canonical_bytes(envelope["reduction"])
    ).hexdigest()
    assert envelope["reduction"] == R.build_reduction()
    assert envelope["reduction"]["terminal"] == R.TERMINAL


def test_authority_and_operational_firewalls_remain_zero() -> None:
    reduction = json.loads(REDUCTION.read_bytes())["reduction"]
    assert set(reduction["operational_counters"].values()) == {"VERIFIED__0"}
    assert reduction["authority_boundary"]["human_authority_present"] is False
    assert reduction["authority_boundary"]["authorization_presentation_count"] == "VERIFIED__0"
    assert reduction["e05"]["after"] == "VERIFIED__11_OF_18"
    assert reduction["e05"]["credit"] == "VERIFIED__0"
    forbidden = (
        JU / "G77_256JU_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt",
        JU / "G77_256JU_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt",
        JU / "G77_256JU_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json",
        JU / "G77_256JU_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1.json",
    )
    assert not any(path.exists() or path.is_symlink() for path in forbidden)


def test_expired_semantics_and_materialized_identities_are_exact() -> None:
    reduction = json.loads(REDUCTION.read_bytes())["reduction"]
    assert reduction["expired_semantics"]["truth_table"] == {
        "999": "CURRENT",
        "1000": "EXPIRED",
        "1001": "EXPIRED",
    }
    assert reduction["identities"]["expired_adapter_sha256"] == (
        "96b5a90269cf871f722babbdcf49b0aa067d712c9d07142d0a2acb15510c68c2"
    )
    assert reduction["identities"]["presentation_identity"] == "NOT_MATERIALIZED"


def test_materializer_has_no_authority_consumption_or_operational_launch() -> None:
    source = MATERIALIZER_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(MATERIALIZER_PATH))
    called_attributes = {
        node.func.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }
    assert not {
        "write_authority_handoff",
        "validate_final_admission",
        "claim_and_invoke_once",
        "main",
    } & called_attributes
    assert "qemu-system-x86_64" not in source


def test_architecture_reuse_and_frontier_are_narrow() -> None:
    reduction = json.loads(REDUCTION.read_bytes())["reduction"]
    assert set(reduction["architecture"].values()) <= {
        "VERIFIED__0",
        "VERIFIED__1",
    }
    assert reduction["architecture"]["production_route_before"] == "VERIFIED__1"
    assert reduction["architecture"]["production_route_after"] == "VERIFIED__1"
    assert reduction["proof_yield"]["new_blocker_localized_count"].startswith(
        "VERIFIED__1__GN_EXACT_REQUEST_SCHEMA_MISMATCH"
    )
    assert reduction["frontier"]["first_broken_edge"] == (
        "GN_EXACT_SEALED_REQUEST_VALIDATION"
    )


def test_g48_has_exact_six_h1_and_five_slovenian_questions() -> None:
    text = REPORT.read_text(encoding="utf-8")
    assert [line for line in text.splitlines() if line.startswith("# ")] == [
        "# 1. Implementation Summary",
        "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment",
        "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary",
        "# 6. Certification Verdict",
    ]
    for question in (
        "Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?",
        "Katere nove zmogljivosti (če sploh) nastanejo?",
        "Ali katera obstoječa zmogljivost postane nedosegljiva?",
        "Ali implementacija ustvarja vzporedni tok?",
        "Ali zmanjšuje ali povečuje število produkcijskih poti?",
    ):
        assert text.count(question) == 1
    assert subprocess.check_output(
        ["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True
    ).strip() == ""
