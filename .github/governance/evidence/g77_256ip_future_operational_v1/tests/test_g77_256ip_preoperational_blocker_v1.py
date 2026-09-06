from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
IP_ROOT = ROOT / ".github/governance/evidence/g77_256ip_future_operational_v1"
FORMALIZER = IP_ROOT / "analysis/G77_256IP_PREOPERATIONAL_BLOCKER_FORMALIZER_V1.py"
TERMINAL = IP_ROOT / "G77_256IP_SPCE_TERMINAL_PREOPERATIONAL_BLOCKER_V1.json"
REPORT = IP_ROOT / "G77_256IP_G48_PREOPERATIONAL_BLOCKER_REPORT_V1.md"


def load_module():
    spec = importlib.util.spec_from_file_location("g77_256ip_blocker", FORMALIZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


IP = load_module()


def test_terminal_is_canonical_duplicate_safe_inner_sealed_and_replayable() -> None:
    envelope = IP.load_canonical(TERMINAL)
    assert envelope["reduction_sha256"] == IP.sha256_bytes(
        IP.canonical_bytes(envelope["reduction"])
    )
    assert envelope == IP.terminal_envelope()
    try:
        IP.unique_object([("schema_id", 1), ("schema_id", 2)])
    except IP.IPBlockerError as exc:
        assert str(exc) == "DUPLICATE_KEY:schema_id"
    else:
        raise AssertionError("duplicate key did not fail closed")


def test_exact_io_entry_nested_authority_and_reconstruction() -> None:
    entry = IP.authenticate_entry()
    assert (entry["head"], entry["tree"], entry["remote_tracking_head"]) == (
        IP.IO_HEAD, IP.IO_TREE, IP.IO_HEAD
    )
    assert entry["nested_authority"]["head"] == IP.NESTED_HEAD
    result = IP.reconstruct_io()
    assert result["status"] == "VERIFIED"
    assert result["artifact_count"] == 4
    assert result["inner_seal"] == "VERIFIED"


def test_current_v2_readiness_preserves_runtime_certification_role_separation() -> None:
    result = IP.current_v2_readiness()
    assert (result["du"], result["eb"], result["ee"]) == ("PASS", "PASS", "PASS")
    assert result["certification_baseline"] == {"head": IP.IO_HEAD, "tree": IP.IO_TREE}
    assert result["runtime_target"]["head"] == IP.IF_HEAD
    assert result["runtime_target"]["tree"] == IP.IF_TREE
    assert result["certification_baseline"] != {
        "head": result["runtime_target"]["head"],
        "tree": result["runtime_target"]["tree"],
    }


def test_future_semantics_and_authenticated_identities_are_unchanged() -> None:
    result = IP.authenticate_future()
    assert (result["evaluation"], result["valid_from"], result["valid_until"]) == (500, 600, 1000)
    assert result["evaluation"] < result["valid_from"] < result["valid_until"]
    assert result["candidate_runtime_sha256"] == IP.FUTURE_CANDIDATE_SHA
    assert result["authenticated_if_context_sha256"] == IP.FUTURE_CONTEXT_SHA
    assert result["future_semantic_mutation_count"] == "VERIFIED__0"
    assert result["wall_clock_dependency_count"] == "VERIFIED__0"


def test_operation_identity_is_fresh_but_gn_rejects_future() -> None:
    identity = IP.derive_operation_identity()
    assert identity["operation_identity"] == "G77_256IP_E05_FUTURE_DENIAL_BEFORE_ENTRY_001"
    assert identity["operation_identity_fresh"] == "VERIFIED"
    blocker = IP.presentation_blocker()
    assert blocker["requested_vector"] == "FUTURE"
    assert "FUTURE" not in blocker["supported_vectors"]
    assert blocker["observed_fail_closed_reason"] == "SEALED_REQUEST_VECTOR_INVALID"
    assert blocker["presentation_derivation"].startswith("NOT_PROVEN")


def test_terminal_c_preserves_operational_zero_and_e05() -> None:
    reduction = IP.terminal_reduction()
    assert set(reduction["operational_counters"].values()) == {0}
    assert reduction["e05"] == {"before": "10/18", "after": "10/18", "credit": 0, "remaining": 8}
    terminal = reduction["terminal"]
    assert terminal["terminal"] == "C__PRE_OPERATIONAL_BLOCKER"
    assert terminal["first_broken_edge"] == "EXISTING_GN_SEALED_REQUEST_VALIDATION_REJECTS_FUTURE_VECTOR"
    assert terminal["auto_continuable"] is False
    assert terminal["human_authorization_action_available"] is False


def test_no_authority_presentation_or_operation_artifact_exists() -> None:
    forbidden = [
        IP_ROOT / "G77_256IP_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json",
        IP_ROOT / "G77_256IP_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt",
        IP_ROOT / "G77_256IP_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt",
        IP_ROOT / "G77_256IP_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json",
        IP_ROOT / "operation_state",
        Path("/tmp/g77_256ip"),
    ]
    assert all(not path.exists() and not path.is_symlink() for path in forbidden)
    source = FORMALIZER.read_text()
    for forbidden_call in (
        "materialize_operation_state(", "validate_final_admission(",
        "write_authority_handoff(", "subprocess.run(argv",
    ):
        assert forbidden_call not in source


def test_g48_has_exactly_six_top_level_headings_and_slovenian_reuse_answers() -> None:
    text = REPORT.read_text()
    headings = [line for line in text.splitlines() if line.startswith("# ")]
    assert headings == [
        "# 1. Implementation Summary", "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment", "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary", "# 6. Certification Verdict",
    ]
    for question in (
        "Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?",
        "Katere nove zmogljivosti (če sploh) nastanejo?",
        "Ali katera obstoječa zmogljivost postane nedosegljiva?",
        "Ali implementacija ustvarja vzporedni tok?",
        "Ali zmanjšuje ali povečuje število produkcijskih poti?",
    ):
        assert question in text
