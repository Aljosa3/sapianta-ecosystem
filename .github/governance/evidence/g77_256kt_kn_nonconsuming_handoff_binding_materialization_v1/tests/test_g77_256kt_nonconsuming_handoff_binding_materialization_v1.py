from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

import pytest


ROOT = Path(__file__).resolve().parents[5]
KT = ROOT / ".github/governance/evidence/g77_256kt_kn_nonconsuming_handoff_binding_materialization_v1"
MATERIALIZER = KT / "analysis/G77_256KT_NONCONSUMING_HANDOFF_BINDING_MATERIALIZER_V1.py"
REDUCTION = KT / "G77_256KT_SPCE_TERMINAL_PRECONSUMPTION_MATERIALIZATION_V1.json"
REPORT = KT / "G77_256KT_G48_IMPLEMENTATION_REPORT_V1.md"


def load_materializer():
    spec = importlib.util.spec_from_file_location("g77_256kt_test_materializer", MATERIALIZER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_authenticated_materialized_state_and_terminal_are_exact() -> None:
    module = load_materializer()
    fm, _ = module.authenticate_common(materialized=True)
    observed = module.verify_materialized(fm)
    assert observed["handoff"]["authorization_sha256"] == module.AUTHORIZATION_INNER_SHA256
    assert module.HANDOFF.read_bytes() == fm.canonical_authority_handoff_bytes(
        module.build_authorization(json.loads(module.CONTEXT.read_bytes()), fm)
    )
    assert module.sha256_path(module.HANDOFF) == module.HANDOFF_SHA256
    assert module.sha256_path(module.BINDING) == module.BINDING_FILE_SHA256


def test_human_source_is_exact_ko_bytes_and_remains_untracked() -> None:
    module = load_materializer()
    raw = module.SOURCE.read_bytes()
    assert len(raw) == 1213 and raw.count(b"\n") == 14
    assert raw.decode("utf-8").encode("utf-8") == raw
    assert not raw.startswith(b"\xef\xbb\xbf") and raw.endswith(b"\n")
    assert hashlib.sha256(raw).hexdigest() == module.SOURCE_SHA256
    assert raw == module.exact_human_bytes()
    assert module.git("ls-files", "--", module.SOURCE.relative_to(ROOT).as_posix()) == ""


def test_fm_strict_parser_rejects_noncanonical_and_duplicate_json() -> None:
    module = load_materializer()
    fm = module.load_fm()
    envelope = json.loads(module.HANDOFF.read_bytes())
    pretty = (json.dumps(envelope, indent=2, sort_keys=True) + "\n").encode()
    with pytest.raises(RuntimeError, match="not unique-key canonical JSON"):
        fm.parse_authority_handoff_bytes(pretty)
    duplicate = module.HANDOFF.read_bytes().replace(b'{"authorization":', b'{"authorization":{},"authorization":', 1)
    with pytest.raises(RuntimeError, match="duplicate JSON keys"):
        fm.parse_authority_handoff_bytes(duplicate)


def test_binding_is_owner_derived_digest_preserving_and_nonconsuming() -> None:
    module = load_materializer()
    fm = module.load_fm()
    observed = module.verify_materialized(fm)
    binding = observed["binding"]
    assert {
        binding["authenticated_canonical_authority_digest"],
        binding["sealed_invocation_authority_digest"],
        binding["final_fm_argv_authority_digest"],
    } == {module.HANDOFF_SHA256}
    assert binding["caller_digest_input_count"] == binding["provider_digest_input_count"] == 0
    assert binding["authority_consumption_count"] == binding["fm_operational_invocation_count"] == 0
    assert binding["binding_is_authority"] is binding["execution_authorized_by_binding"] is False
    assert binding["process_started"] is False


def test_persisted_ka_kg_precedent_proves_prepare_before_consume() -> None:
    module = load_materializer()
    ka_pre = module.load_envelope(module.KA_PRECONSUMPTION, "checkpoint")
    ka_consumed = module.load_envelope(module.KA_CONSUMPTION, "checkpoint")
    kg_pre = module.load_envelope(module.KG_PRECONSUMPTION, "checkpoint")
    assert ka_pre["authority_state"] == kg_pre["authority_state"] == "GRANTED_UNCONSUMED"
    assert ka_pre["operational_counters"]["authority_consumption_count"] == 0
    assert kg_pre["operational_counters"]["authority_consumption_count"] == 0
    assert ka_consumed["authority_state_before"] == "GRANTED_UNCONSUMED"
    assert ka_consumed["authority_state_after"] == "CONSUMED"
    assert ka_consumed["operational_counters"]["authority_consumption_count"] == 1


def test_reduction_is_canonical_sealed_deterministic_and_unconsumed() -> None:
    module = load_materializer()
    raw = REDUCTION.read_bytes()
    envelope = json.loads(raw)
    reduction = envelope["reduction"]
    assert raw == module.canonical_bytes(envelope)
    assert envelope["reduction_sha256"] == hashlib.sha256(module.canonical_bytes(reduction)).hexdigest()
    assert reduction == module.build_reduction(module.BINDING_FILE_SHA256, module.BINDING_INNER_SHA256)
    assert reduction["terminal"] == module.TERMINAL
    assert len(reduction["operational_counters"]) == 15
    assert set(reduction["operational_counters"].values()) == {0}
    assert reduction["phase_b_started"] is reduction["auto_continuable"] is False
    assert reduction["human_review_required"] is True


def test_no_consumption_operation_or_collision_namespace_exists() -> None:
    module = load_materializer()
    assert all(not path.exists() and not path.is_symlink() for path in (
        module.CONSUMPTION, module.INVOCATION, module.RESULT, module.PHASE_B_CHECKPOINT,
    ))
    assert module.HANDOFF.is_file() and not module.HANDOFF.is_symlink()
    assert module.BINDING.is_file() and not module.BINDING.is_symlink()
    with pytest.raises(module.KTMaterializationError, match="HANDOFF_BINDING_NAMESPACE_STATE_MISMATCH"):
        module.authenticate_common(materialized=False)


def test_e05_ex_architecture_classification_and_continuation() -> None:
    reduction = load_materializer().load_envelope(REDUCTION, "reduction")
    assert reduction["failure_novelty_and_convergence_check"]["failure_class"] == "PROOF_GAP"
    assert reduction["e05"] == {
        "state": "VERIFIED__11_OF_18", "frontier": "VERIFIED__7_UNSATISFIED_OF_18",
        "credit": "VERIFIED__0", "kn_e05_credit": "VERIFIED__0",
        "expired": "NOT_PROVEN_OPERATIONALLY",
        "potential_future_after_qualifying_observation": "NOT_PROVEN__12_OF_18",
    }
    assert reduction["ex"] == {"ex_reused": "VERIFIED__17_OF_17", "ex_reconstructed": "VERIFIED__0"}
    architecture = reduction["architecture"]
    assert architecture["production_route_before"] == architecture["production_route_after"] == 1
    assert architecture["parallel_flow"] == "NO"
    assert set(value for key, value in architecture.items() if key.endswith("_count")) == {0}
    continuation = reduction["continuation"]
    assert continuation["same_generation_continuation"] == "VERIFIED__G77_256KT"
    assert continuation["previous_worker_memory_required"] == "VERIFIED__NO"


def test_python_ast_and_exact_g48_ria_structure() -> None:
    ast.parse(MATERIALIZER.read_text(encoding="utf-8"))
    ast.parse(Path(__file__).read_text(encoding="utf-8"))
    report = REPORT.read_text(encoding="utf-8")
    assert re.findall(r"^# (.+)$", report, flags=re.MULTILINE) == [
        "1. Implementation Summary", "2. Code Evidence",
        "3. Constitutional Self-Assessment", "4. Validation Matrix",
        "5. Repository Mutation Summary", "6. Certification Verdict",
    ]
    assert re.findall(r"^[1-5]\. (.+\?)$", report, flags=re.MULTILINE) == [
        "Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?",
        "Katere nove zmogljivosti (če sploh) nastanejo?",
        "Ali katera obstoječa zmogljivost postane nedosegljiva?",
        "Ali implementacija ustvarja vzporedni tok?",
        "Ali zmanjšuje ali povečuje število produkcijskih poti?",
    ]
