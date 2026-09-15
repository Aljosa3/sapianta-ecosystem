from pathlib import Path
import ast


ROOT = Path(__file__).resolve().parents[5]
CONTROLLER = ROOT / ".github/governance/evidence/g77_256lw_operational_wrong_scope_denial_v1/orchestration/G77_256LW_ONE_SHOT_LT_FM_CONTROLLER_V1.py"
TERMINALIZER = ROOT / ".github/governance/evidence/g77_256lw_operational_wrong_scope_denial_v1/orchestration/G77_256LW_POSTOP_TERMINALIZER_V1.py"


def test_sources_parse_and_preserve_one_shot_order():
    controller = CONTROLLER.read_text(encoding="utf-8")
    terminalizer = TERMINALIZER.read_text(encoding="utf-8")
    ast.parse(controller)
    ast.parse(terminalizer)
    consumption = controller.index("persist(CONSUMPTION")
    reservation = controller.index("LT.launch_detached")
    assert consumption < reservation
    assert controller.count("LT.launch_detached") == 1
    assert "retry_limit\": 0" in controller
    assert "subprocess.run(argv" not in controller
    assert "INTERRUPTED_OR_LOST__UNKNOWN" not in controller


def test_terminalizer_requires_guest_counters_not_host_exit_alone():
    source = TERMINALIZER.read_text(encoding="utf-8")
    for token in ("wrong_scope_denial_complete", "b6_p11_entry_counter", "b6_invocation_counter", "b6_protected_effect_counter", "producer_consumer_agreement"):
        assert token in source
    assert '"DENIAL_CLASS": "UNKNOWN"' in source
    assert '"PROTECTED_EFFECT_COUNT": "UNKNOWN"' in source
