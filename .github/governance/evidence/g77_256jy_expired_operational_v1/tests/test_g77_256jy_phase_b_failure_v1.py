from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[5]
JY = ROOT / ".github/governance/evidence/g77_256jy_expired_operational_v1"
CONTROLLER = JY / "orchestration/G77_256JY_AUTHORITY_CONSUMPTION_CONTROLLER_V1.py"
SOURCE = JY / "G77_256JY_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt"
HANDOFF = JY / "G77_256JY_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json"
CONSUMPTION = JY / "G77_256JY_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1.json"
FAILURE = JY / "G77_256JY_PHASE_B_FM_INVOCATION_FAILURE_V1.json"
REDUCTION = JY / "G77_256JY_SPCE_TERMINAL_FAILURE_REDUCTION_V1.json"
CLOSURE = JY / "G77_256JY_PROVIDER_LIMIT_RECOVERY_TERMINAL_CLOSURE_V1.json"
CONTEXT = JY / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
REPORT = JY / "G77_256JY_G48_IMPLEMENTATION_REPORT_V1.md"


def load(path: Path, name: str):
    specification = importlib.util.spec_from_file_location(name, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


C = load(CONTROLLER, "g77_256jy_phase_b_test_controller")


def canonical(path: Path) -> dict:
    raw = path.read_bytes()
    value = json.loads(raw, object_pairs_hook=C.C.MATERIALIZER.M.unique_object)
    assert raw == C.C.FM.canonical_bytes(value)
    return value


def assert_seal(path: Path, inner: str) -> dict:
    envelope = canonical(path)
    value = envelope[inner]
    assert envelope[f"{inner}_sha256"] == hashlib.sha256(
        C.C.FM.canonical_bytes(value)
    ).hexdigest()
    return value


def test_human_source_is_exact_and_authenticated() -> None:
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == (
        "413d0c8164a240b9853d2a95d215128dedca2cc86fa95da3dff7e41c8bafffd4"
    )
    assert SOURCE.read_text(encoding="utf-8").replace("\\_", "_") == (
        C.C.EXPECTED_NORMALIZED_GRANT
    )


def test_authority_handoff_and_consumption_are_exactly_once() -> None:
    authorization = assert_seal(HANDOFF, "authorization")
    checkpoint = assert_seal(CONSUMPTION, "checkpoint")
    assert hashlib.sha256(HANDOFF.read_bytes()).hexdigest() == (
        "7211842d95639b2d869a19af1c0848d61197b2dae66c931cf5dd1e9aa5584d9d"
    )
    assert authorization["authorization_source_sha256"] == (
        "413d0c8164a240b9853d2a95d215128dedca2cc86fa95da3dff7e41c8bafffd4"
    )
    assert authorization["authorization_reusable"] is False
    assert checkpoint["human_grant_binding_status"] == "VERIFIED"
    assert checkpoint["authority_state_before"] == "GRANTED_UNCONSUMED"
    assert checkpoint["authority_state_after"] == "CONSUMED"
    assert checkpoint["authority_consumed"] == 1


def test_single_fm_failure_is_exact_and_before_pre() -> None:
    failure = assert_seal(FAILURE, "failure")
    assert failure["invocation_count"] == 1
    assert failure["process_exit_status"] == 1
    assert failure["supplied_digest_length"] == 63
    assert failure["supplied_execution_authority_sha256"] + "d" == (
        failure["actual_authority_file_sha256"]
    )
    assert failure["exact_exception"] == (
        "supplied execution authority hash malformed"
    )
    assert failure["failure_boundary"] == "FM_FINAL_ADMISSION_BEFORE_PRE_RECEIPT"
    assert failure["pre_receipt_exists"] is False
    assert failure["post_receipt_exists"] is False
    assert failure["qemu_started"] is False
    assert failure["vm_started"] is False
    assert failure["operation_started"] is False


def test_terminal_reduction_has_exact_counters_e05_and_frontier() -> None:
    reduction = assert_seal(REDUCTION, "reduction")
    assert reduction["terminal"] == (
        "M__FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATION_BLOCKED_AT_FM_"
        "SUPPLIED_AUTHORITY_HASH_SYNTAX_BEFORE_PRE"
    )
    assert reduction["operational_counters"] == {
        "operational_authorization_count": 1,
        "authority_consumption_count": 1,
        "pre_operational_count": 0,
        "fm_operational_invocation_count": 1,
        "qemu_count": 0,
        "vm_count": 0,
        "operation_attempt_count": 0,
        "operational_request_count": 0,
        "expired_denial_count": 0,
        "p11_entry_count": 0,
        "protected_invocation_count": 0,
        "protected_effect_count": 0,
        "retry_count": 0,
        "repair_retry_count": 0,
        "replay_count": 0,
    }
    assert reduction["e05"] == {
        "before": "VERIFIED__11_OF_18",
        "after": "VERIFIED__11_OF_18",
        "credit": "VERIFIED__0",
        "frontier_before": "VERIFIED__7_UNSATISFIED_OF_18",
        "frontier_after": "VERIFIED__7_UNSATISFIED_OF_18",
    }
    assert reduction["frontier"]["first_broken_edge"] == (
        "FM_FINAL_ADMISSION_SUPPLIED_AUTHORITY_HASH_SYNTAX_GATE"
    )
    assert reduction["auto_continuable"] is False
    assert reduction["human_review_required"] is True


def test_provider_limit_recovery_closes_without_operation_or_history_change() -> None:
    closure = assert_seal(CLOSURE, "closure")
    assert closure["terminal"] == (
        "M__JY_TERMINAL_FAILURE_REDUCED_TO_CALLER_CONSTRUCTED_TRUNCATED_"
        "FM_AUTHORITY_DIGEST_ARGUMENT_BEFORE_PRE"
    )
    assert closure["recovery"] == {
        "recovery_type": "SAME_GENERATION_SAME_ACCOUNT_PROVIDER_LIMIT_RESET_RECOVERY",
        "same_generation": "VERIFIED__YES",
        "same_codex_account": "VERIFIED__YES",
        "provider_limit_reset": "VERIFIED__YES",
        "evidence_recovery_only": "VERIFIED__YES",
        "cross_account_recovery": "VERIFIED__NO",
        "provider_capacity_is_execution_authority": False,
        "additional_authority_count": 0,
        "additional_consumption_count": 0,
        "additional_fm_invocation_count": 0,
        "additional_pre_count": 0,
        "additional_qemu_count": 0,
        "additional_vm_count": 0,
        "additional_operation_attempt_count": 0,
    }
    assert closure["entry"]["recovery_entry_file_count"] == 29
    assert closure["entry"]["recovery_entry_inventory_sha256"] == (
        "c2dcb6ea10de3b1e716095b0ac67fad06203fc148b4e431a54544867dc9b1f73"
    )
    localization = closure["failure_localization"]
    assert localization["exact_difference"] == "FINAL_HEX_CHARACTER_D_OMITTED"
    assert localization["introduction_boundary"] == (
        "EXTERNAL_CODEX_EXEC_COMMAND_ARGUMENT_CONSTRUCTION"
    )
    assert localization["orchestration_materialization"] == (
        "VERIFIED__CORRECT_64_HEX_HANDOFF_FILE_DIGEST"
    )
    assert localization["shell_cli_transport"] == (
        "VERIFIED__PRESERVED_CALLER_SUPPLIED_63_HEX_LITERAL"
    )
    assert localization["fm_validation"] == (
        "VERIFIED__CORRECT_FAIL_CLOSED_HEX_64_REJECTION"
    )
    assert closure["operational_counters"] == assert_seal(
        REDUCTION, "reduction"
    )["operational_counters"]
    assert closure["frontier"] == {
        "last_verified_edge": "ONE_FRESH_JY_HUMAN_AUTHORITY_AUTHENTICATED_CONSUMED_AND_FM_INVOKED_ONCE",
        "first_broken_edge": "FM_SUPPLIED_AUTHORITY_DIGEST_SYNTAX_BINDING_BEFORE_PRE",
        "minimum_missing_capability": "EXACT_AUTHENTICATED_AUTHORITY_DIGEST_PRESERVING_FM_INVOCATION_BINDING",
        "minimum_legal_next_delta": "SEPARATE_REPOSITORY_ONLY_AUTHORITY_DIGEST_HANDOFF_REPAIR_GENERATION",
    }
    assert closure["jy_closed_for_operation"] is True


def test_no_pre_qemu_vm_operation_or_replay_artifact_exists() -> None:
    context = canonical(CONTEXT)
    assert not Path(context["pre_receipt_path"]).exists()
    assert not Path(context["post_receipt_path"]).exists()
    names = [path.name for path in JY.rglob("*") if path.is_file()]
    assert not any("SERIAL" in name for name in names)
    assert not any("EXECUTION_SEAL" in name for name in names)


def test_production_baseline_p11_route_and_index_remain_unchanged() -> None:
    assert subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip() == "939d7eda8ff333b6cf0dfbd54d274aabefcba698"
    assert subprocess.check_output(
        ["git", "rev-parse", "HEAD^{tree}"], cwd=ROOT, text=True
    ).strip() == "bce9f2863a7314a1e5e088066efeea52615d989d"
    assert subprocess.check_output(
        ["git", "diff", "--name-only"], cwd=ROOT, text=True
    ).strip() == ""
    assert subprocess.check_output(
        ["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True
    ).strip() == ""
    assert hashlib.sha256(
        (ROOT / "tests/p11_da_operational_consumer_v1.py").read_bytes()
    ).hexdigest() == "38399ab9d1eb74dc2a231eb3a363064ba8b90077d6cdbf1d3494ca937b2127f5"


def test_g48_has_exact_six_h1_and_five_exact_questions() -> None:
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
