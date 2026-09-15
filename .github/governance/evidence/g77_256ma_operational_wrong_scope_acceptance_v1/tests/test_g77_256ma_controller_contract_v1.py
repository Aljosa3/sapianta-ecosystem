from pathlib import Path
import ast
import hashlib
import json


ROOT = Path(__file__).resolve().parents[5]
CONTROLLER = ROOT / ".github/governance/evidence/g77_256ma_operational_wrong_scope_acceptance_v1/orchestration/G77_256MA_ONE_SHOT_LT_FM_CONTROLLER_V1.py"
TERMINALIZER = ROOT / ".github/governance/evidence/g77_256ma_operational_wrong_scope_acceptance_v1/orchestration/G77_256MA_POSTOP_TERMINALIZER_V1.py"
REDUCTION = ROOT / ".github/governance/evidence/g77_256ma_operational_wrong_scope_acceptance_v1/G77_256MA_OPERATIONAL_EVIDENCE_REDUCTION_V1.json"
DECISION = ROOT / ".github/governance/evidence/g77_256ma_operational_wrong_scope_acceptance_v1/G77_256MA_TERMINAL_DECISION_V1.json"
REPORT = ROOT / ".github/governance/evidence/g77_256ma_operational_wrong_scope_acceptance_v1/G77_256MA_G48_IMPLEMENTATION_REPORT_V1.md"


def canonical_bytes(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False) + "\n").encode()


def test_sources_parse_and_preserve_one_shot_order():
    controller = CONTROLLER.read_text(encoding="utf-8")
    terminalizer = TERMINALIZER.read_text(encoding="utf-8")
    ast.parse(controller)
    ast.parse(terminalizer)
    consumption = controller.index("persist(CONSUMPTION")
    reservation = controller.index("LT.launch_detached")
    ly_prepare = controller.index("LY.prepare_lt_parent_readiness")
    authority_creation = controller.index("FM.write_authority_handoff")
    final_admission = controller.rindex("validate_admission(context, handoff")
    ly_reobserve = controller.index("LY.reobserve_before_authority_consumption")
    reobservation_persist = controller.index("LY_REOBSERVATION,", ly_reobserve)
    assert ly_prepare < authority_creation
    assert final_admission < ly_reobserve < reobservation_persist < consumption
    assert consumption < reservation
    assert controller.count("LT.launch_detached") == 1
    assert "retry_limit\": 0" in controller
    assert "subprocess.run(argv" not in controller
    assert "INTERRUPTED_OR_LOST__UNKNOWN" not in controller
    assert controller.count("FM.write_authority_handoff") == 1
    assert '"human_authorizes_presented_scope": False' in controller


def test_terminalizer_requires_guest_counters_not_host_exit_alone():
    source = TERMINALIZER.read_text(encoding="utf-8")
    for token in ("wrong_scope_denial_complete", "b6_p11_entry_counter", "b6_invocation_counter", "b6_protected_effect_counter", "producer_consumer_agreement"):
        assert token in source
    assert '"DENIAL_CLASS": "UNKNOWN"' in source
    assert '"PROTECTED_EFFECT_COUNT": "UNKNOWN"' in source
    assert '"MA_E05_CREDIT": 1' in source
    assert "LY_PRECONSUMPTION_REOBSERVATION" in source
    assert '"operation_completed": complete' in source
    assert '"acceptance_satisfied": result["WRONG_SCOPE_STATUS"] == "SAT"' in source
    assert '"FAILURE_CLASS": "HARNESS_OR_TEST_ARTIFACT"' in source
    assert '"NOVELTY": "NEW_SEMANTIC_EDGE"' in source
    assert 'preclaim_time < valid_from < valid_until' in source
    assert '"MINIMUM_LEGAL_NEXT_DELTA": "INDEPENDENT_HUMAN_AUTHENTICATION_OF_MA_TERMINAL"' in source


def test_terminal_artifacts_separate_completion_from_acceptance_and_seal_exactly():
    reduction_envelope = json.loads(REDUCTION.read_bytes())
    reduction = reduction_envelope["reduction"]
    assert reduction_envelope["reduction_sha256"] == hashlib.sha256(canonical_bytes(reduction)).hexdigest()
    assert reduction["operation_completed"] is True
    assert reduction["acceptance_satisfied"] is False
    assert reduction["FAILURE_CLASS"] == "HARNESS_OR_TEST_ARTIFACT"
    assert reduction["NOVELTY"] == "NEW_SEMANTIC_EDGE"
    assert reduction["DENIAL_CLASS"] == "FUTURE"
    assert reduction["OBSERVED_PRECLAIM_TIME_UNIX_NS"] < reduction["ACT_VALID_FROM_UNIX_NS"] < reduction["ACT_VALID_UNTIL_UNIX_NS"]
    assert reduction["P11_ENTRY_COUNT"] == reduction["PROTECTED_INVOCATION_COUNT"] == reduction["PROTECTED_EFFECT_COUNT"] == 0
    assert reduction["MA_E05_CREDIT"] == 0
    assert reduction["E05_AFTER"] == "12/18"
    assert reduction["WRONG_SCOPE_STATUS"] == "UNSAT"
    decision_envelope = json.loads(DECISION.read_bytes())
    decision = decision_envelope["decision"]
    assert decision_envelope["decision_sha256"] == hashlib.sha256(canonical_bytes(decision)).hexdigest()
    assert decision["operational_reduction_sha256"] == hashlib.sha256(REDUCTION.read_bytes()).hexdigest()
    assert decision["AUTHORITY_CREATED_COUNT"] == decision["AUTHORITY_CONSUMED_COUNT"] == 1
    assert decision["AUTHORITY_REUSABLE"] == "NO"
    assert decision["LT_RESERVATION_COUNT"] == decision["LT_CHILD_LAUNCH_COUNT"] == 1
    assert decision["FM_OPERATION_COUNT"] == decision["QEMU_COUNT"] == decision["VM_COUNT"] == 1
    assert decision["RETRY_COUNT"] == 0
    assert decision["OPERATIONAL_RETRY_AUTHORIZED"] == "NO"


def test_g48_report_has_exact_structure_and_questions_once():
    report = REPORT.read_text(encoding="utf-8")
    assert [line for line in report.splitlines() if line.startswith("# ")] == [
        "# 1. Implementation Summary",
        "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment",
        "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary",
        "# 6. Certification Verdict",
    ]
    questions = (
        "Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?",
        "Katere nove zmogljivosti (če sploh) nastanejo?",
        "Ali katera obstoječa zmogljivost postane nedosegljiva?",
        "Ali implementacija ustvarja vzporedni tok?",
        "Ali zmanjšuje ali povečuje število produkcijskih poti?",
    )
    assert all(report.count(question) == 1 for question in questions)
