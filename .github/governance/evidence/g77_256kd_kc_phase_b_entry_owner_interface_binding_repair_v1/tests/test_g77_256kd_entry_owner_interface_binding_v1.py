from __future__ import annotations

import hashlib
import importlib.util
import inspect
import json
from copy import deepcopy
from pathlib import Path
import subprocess
import sys
from types import ModuleType

import pytest


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
KD = ROOT / ".github/governance/evidence/g77_256kd_kc_phase_b_entry_owner_interface_binding_repair_v1"
FORMALIZER = KD / "analysis/G77_256KD_ENTRY_OWNER_INTERFACE_FORMALIZER_V1.py"
REDUCTION = KD / "G77_256KD_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
REPORT = KD / "G77_256KD_G48_IMPLEMENTATION_REPORT_V1.md"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


F = load(FORMALIZER, "g77_256kd_test_formalizer")


def test_pre_repair_failure_is_exact_and_repository_only() -> None:
    proof = F.reproduce_pre_repair()
    assert proof["result"] == "VERIFIED__EXACT_REPOSITORY_ONLY_REPRODUCTION"
    assert proof["exact_exception"] == (
        "AttributeError: module 'g77_256kc_phase_b_materializer' has no attribute 'A'"
    )


def test_post_repair_resolves_exact_authoritative_owner() -> None:
    proof = F.verify_post_repair()
    assert proof["caller"] == "G77_256KC_PHASE_B_CONTROLLER_V1.authenticate"
    assert proof["argument_names"] == ["remote_head", "nested_remote_tag"]
    assert proof["authoritative_function_identity"] == (
        "K.A.authenticate_entry IS K.A.M.authenticate_entry"
    )
    assert proof["post_repair_resolution"].startswith("VERIFIED__")
    assert "ENTRY_MISMATCH" in proof["repository_identity_negative"]


def fresh_controller_and_wrapper(case: str):
    current = load(F.CONTROLLER if F.CONTROLLER.is_absolute() else ROOT / F.CONTROLLER, f"g77_256kd_controller_{case}")
    wrapper = load(F.MATERIALIZER if F.MATERIALIZER.is_absolute() else ROOT / F.MATERIALIZER, f"g77_256kd_wrapper_{case}")
    probe = ModuleType(f"g77_256kd_probe_{case}")
    probe.MATERIALIZER = wrapper
    return current, probe, wrapper


@pytest.mark.parametrize("case", ("missing_owner", "wrong_owner", "missing_interface", "malformed_interface"))
def test_owner_and_interface_substitutions_fail_closed(case: str) -> None:
    current, probe, wrapper = fresh_controller_and_wrapper(case)
    if case == "missing_owner":
        del wrapper.K
    elif case == "wrong_owner":
        wrapper.K = ModuleType("caller_selected_wrong_owner")
    elif case == "missing_interface":
        wrapper.K.A = ModuleType("missing_entry_interface")
    else:
        fake = ModuleType("malformed_entry_interface")
        fake.authenticate_entry = lambda only_one: None
        fake.M = fake
        wrapper.K.A = fake
    with pytest.raises(current.KCPhaseBError):
        current._bind_kc_phase_b_materializer_owner(probe)


def test_no_caller_provider_or_unsealed_fallback_surface() -> None:
    current = load(ROOT / F.CONTROLLER, "g77_256kd_controller_surface")
    assert tuple(inspect.signature(current._bind_kc_phase_b_materializer_owner).parameters) == ("controller",)
    binder = (ROOT / F.KC / "orchestration/G77_256KC_POSTHUMAN_INVOCATION_BINDER_V1.py").read_text()
    assert "caller_digest" not in binder
    assert "provider_digest" not in binder
    assert "FM.validate_preconsumption_invocation_binding" in binder
    assert "subprocess.run" not in binder


def test_generation_and_context_substitutions_fail_closed() -> None:
    owner_path = ROOT / (
        ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
        "sapianta_fresh_operation_context_v1.py"
    )
    owner = load(owner_path, "g77_256kd_context_owner")
    context_path = ROOT / F.KC / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
    context = json.loads(context_path.read_bytes())

    unsealed = deepcopy(context)
    unsealed["context_sha256"] = "f" * 64
    with pytest.raises(owner.ContextError, match="context seal mismatch"):
        owner.validate_context(unsealed, repository_root=ROOT)

    wrong_generation = deepcopy(context)
    del wrong_generation["context_sha256"]
    wrong_generation["generation_identity"] = (
        "G77_256KC_ONE_FRESH_HUMAN_AUTHORIZED_FUTURE_OPERATIONAL_COMMISSIONING_V1"
    )
    wrong_generation = owner.seal_context(wrong_generation)
    with pytest.raises(owner.ContextError):
        owner.validate_context(wrong_generation, repository_root=ROOT)


def test_terminal_reduction_is_canonical_sealed_and_replayable() -> None:
    raw = REDUCTION.read_bytes()
    envelope = json.loads(raw)
    canonical = F.canonical_bytes(envelope)
    assert raw == canonical
    reduction = envelope["reduction"]
    assert envelope["reduction_sha256"] == hashlib.sha256(F.canonical_bytes(reduction)).hexdigest()
    assert reduction == F.build_reduction(F.HEAD, F.NESTED_HEAD)
    assert set(reduction["operational_counters"].values()) == {0}


def test_kc_authority_and_operation_artifacts_remain_absent() -> None:
    names = (
        "G77_256KC_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json",
        "G77_256KC_PRECONSUMPTION_INVOCATION_BINDING_V1.json",
        "G77_256KC_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1.json",
        "G77_256KC_FM_OPERATIONAL_INVOCATION_ATTEMPT_V1.json",
    )
    assert all(not (ROOT / F.KC / name).exists() for name in names)
    receipts = ROOT / F.KC / "operation_state/receipts"
    assert not any(receipts.iterdir())


def test_p11_route_g48_ria_and_index_are_preserved() -> None:
    assert F.sha256(F.P11) == F.P11_SHA256
    assert F.sha256(F.FM) == F.FM_SHA256
    report = REPORT.read_text()
    assert [line for line in report.splitlines() if line.startswith("# ")] == [
        "# 1. Implementation Summary", "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment", "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary", "# 6. Certification Verdict",
    ]
    questions = (
        "Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?",
        "Katere nove zmogljivosti (če sploh) nastanejo?",
        "Ali katera obstoječa zmogljivost postane nedosegljiva?",
        "Ali implementacija ustvarja vzporedni tok?",
        "Ali zmanjšuje ali povečuje število produkcijskih poti?",
    )
    assert all(report.count(question) == 1 for question in questions)
    assert subprocess.check_output(["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True).strip() == ""
