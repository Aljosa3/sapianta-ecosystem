from __future__ import annotations

from copy import deepcopy
import ast
import hashlib
import importlib.util
import inspect
import json
from pathlib import Path
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[5]
JZ = ROOT / (
    ".github/governance/evidence/"
    "g77_256jz_fm_authority_digest_handoff_repair_v1"
)
JY = ROOT / ".github/governance/evidence/g77_256jy_expired_operational_v1"
FM_PATH = ROOT / (
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
P11 = ROOT / "tests/p11_da_operational_consumer_v1.py"
HANDOFF = JY / "G77_256JY_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json"
CONTEXT = JY / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
CANDIDATE = JY / (
    "live_binding/candidate/"
    "G77_256GD_CANONICAL_CONTINUATION_MANIFEST_BINDING_REISSUE_V1.json"
)
JY_FAILURE = JY / "G77_256JY_PHASE_B_FM_INVOCATION_FAILURE_V1.json"
JY_CLOSURE = JY / "G77_256JY_PROVIDER_LIMIT_RECOVERY_TERMINAL_CLOSURE_V1.json"
BINDING = JZ / "G77_256JZ_PRECONSUMPTION_INVOCATION_BINDING_V1.json"
REDUCTION = JZ / "G77_256JZ_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
REPORT = JZ / "G77_256JZ_G48_IMPLEMENTATION_REPORT_V1.md"

AUTHORITY_SHA256 = (
    "7211842d95639b2d869a19af1c0848d61197b2dae66c931cf5dd1e9aa5584d9d"
)
TRUNCATED_SHA256 = (
    "7211842d95639b2d869a19af1c0848d61197b2dae66c931cf5dd1e9aa5584d9"
)
TERMINAL = (
    "A__FM_AUTHORITY_DIGEST_PRESERVING_PRECONSUMPTION_INVOCATION_"
    "BINDING_REPOSITORY_VERIFIED"
)


def load_module(path: Path, name: str):
    specification = importlib.util.spec_from_file_location(name, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


FM = load_module(FM_PATH, "g77_256jz_test_fm")


def canonical(path: Path) -> dict:
    raw = path.read_bytes()
    value = json.loads(raw)
    assert raw == FM.canonical_bytes(value)
    return value


def sealed(path: Path, inner: str) -> dict:
    envelope = canonical(path)
    value = envelope[inner]
    assert envelope[f"{inner}_sha256"] == hashlib.sha256(
        FM.canonical_bytes(value)
    ).hexdigest()
    return value


def build() -> dict:
    return FM.build_preconsumption_invocation_binding(
        repository_root=ROOT,
        operation_context=CONTEXT,
        live_candidate_binding=CANDIDATE,
        execution_authority=HANDOFF,
    )


def validate(envelope: dict) -> dict:
    return FM.validate_preconsumption_invocation_binding(
        repository_root=ROOT,
        operation_context=CONTEXT,
        live_candidate_binding=CANDIDATE,
        execution_authority=HANDOFF,
        envelope=envelope,
    )


def reseal(envelope: dict) -> dict:
    envelope["invocation_binding_sha256"] = hashlib.sha256(
        FM.canonical_bytes(envelope["invocation_binding"])
    ).hexdigest()
    return envelope


def replace_all_digests(envelope: dict, replacement: str) -> dict:
    binding = envelope["invocation_binding"]
    for field in (
        "authenticated_canonical_authority_digest",
        "sealed_invocation_authority_digest",
        "final_fm_argv_authority_digest",
    ):
        binding[field] = replacement
    argv = binding["final_fm_argv"]
    argv[argv.index("--execution-authority-sha256") + 1] = replacement
    binding["final_fm_argv_sha256"] = hashlib.sha256(
        FM.canonical_bytes(argv)
    ).hexdigest()
    return reseal(envelope)


def test_exact_authenticated_digest_is_derived_sealed_and_preserved_in_argv() -> None:
    envelope = build()
    binding = validate(envelope)
    argv = binding["final_fm_argv"]
    argv_digest = argv[argv.index("--execution-authority-sha256") + 1]
    assert hashlib.sha256(HANDOFF.read_bytes()).hexdigest() == AUTHORITY_SHA256
    assert {
        binding["authenticated_canonical_authority_digest"],
        binding["sealed_invocation_authority_digest"],
        binding["final_fm_argv_authority_digest"],
        argv_digest,
    } == {AUTHORITY_SHA256}
    assert binding["binding_phase"] == (
        "BEFORE_AUTHORITY_CONSUMPTION_AND_FM_INVOCATION"
    )
    assert binding["caller_digest_input_count"] == 0
    assert binding["provider_digest_input_count"] == 0
    assert binding["authority_consumption_count"] == 0
    assert binding["fm_operational_invocation_count"] == 0
    assert binding["binding_is_authority"] is False
    assert binding["execution_authorized_by_binding"] is False
    assert binding["process_started"] is False


@pytest.mark.parametrize(
    "substitute",
    [
        TRUNCATED_SHA256,
        AUTHORITY_SHA256 + "d",
        AUTHORITY_SHA256[:-1] + "e",
        AUTHORITY_SHA256[:-1] + "z",
        AUTHORITY_SHA256.upper(),
        " " + AUTHORITY_SHA256,
        AUTHORITY_SHA256 + " ",
        "sha256:" + AUTHORITY_SHA256,
        "prefix" + AUTHORITY_SHA256 + "suffix",
        "0" * 64,
        "f" * 64,
    ],
    ids=[
        "jy-63-hex-truncation",
        "65-char-extension",
        "wrong-final-nibble",
        "nonhex",
        "case-substitution",
        "leading-whitespace",
        "trailing-whitespace",
        "prefix-injection",
        "prefix-suffix-injection",
        "stale-digest",
        "unrelated-authority-digest",
    ],
)
def test_digest_substitution_matrix_fails_closed(substitute: str) -> None:
    with pytest.raises(RuntimeError, match="preconsumption"):
        validate(replace_all_digests(deepcopy(build()), substitute))


def test_missing_digest_argument_fails_closed() -> None:
    envelope = deepcopy(build())
    binding = envelope["invocation_binding"]
    argv = binding["final_fm_argv"]
    index = argv.index("--execution-authority-sha256")
    del argv[index : index + 2]
    binding["final_fm_argv_sha256"] = hashlib.sha256(
        FM.canonical_bytes(argv)
    ).hexdigest()
    with pytest.raises(RuntimeError, match="final FM argv mismatch"):
        validate(reseal(envelope))


def test_handoff_to_sealed_and_sealed_to_argv_mismatches_fail_closed() -> None:
    handoff_to_sealed = deepcopy(build())
    handoff_to_sealed["invocation_binding"][
        "sealed_invocation_authority_digest"
    ] = "f" * 64
    with pytest.raises(RuntimeError, match="sealed_invocation_authority_digest mismatch"):
        validate(reseal(handoff_to_sealed))

    sealed_to_argv = deepcopy(build())
    binding = sealed_to_argv["invocation_binding"]
    argv = binding["final_fm_argv"]
    argv[argv.index("--execution-authority-sha256") + 1] = "f" * 64
    binding["final_fm_argv_sha256"] = hashlib.sha256(
        FM.canonical_bytes(argv)
    ).hexdigest()
    with pytest.raises(RuntimeError, match="final FM argv mismatch"):
        validate(reseal(sealed_to_argv))


@pytest.mark.parametrize(
    "keyword",
    ["caller_digest", "provider_digest", "execution_authority_sha256"],
)
def test_caller_or_provider_cannot_supply_a_digest_to_builder(keyword: str) -> None:
    parameters = inspect.signature(
        FM.build_preconsumption_invocation_binding
    ).parameters
    assert "execution_authority_sha256" not in parameters
    assert "caller_digest" not in parameters
    assert "provider_digest" not in parameters
    with pytest.raises(TypeError):
        FM.build_preconsumption_invocation_binding(
            repository_root=ROOT,
            operation_context=CONTEXT,
            live_candidate_binding=CANDIDATE,
            execution_authority=HANDOFF,
            **{keyword: "f" * 64},
        )


def test_jy_exact_defect_and_fm_hex64_failure_are_reproduced_without_operation() -> None:
    failure = sealed(JY_FAILURE, "failure")
    closure = sealed(JY_CLOSURE, "closure")
    assert failure["supplied_execution_authority_sha256"] == TRUNCATED_SHA256
    assert failure["actual_authority_file_sha256"] == AUTHORITY_SHA256
    assert failure["supplied_digest_length"] == 63
    assert closure["failure_localization"]["exact_difference"] == (
        "FINAL_HEX_CHARACTER_D_OMITTED"
    )
    authority, authority_digest = FM.load_authority(HANDOFF)
    with pytest.raises(RuntimeError, match="supplied execution authority hash malformed"):
        FM.validate_execution_admission(
            context={"repository_head": "a" * 40, "repository_tree": "b" * 40},
            authority=authority,
            authority_file_sha256=authority_digest,
            supplied_authority_sha256=TRUNCATED_SHA256,
            observed_head="a" * 40,
            observed_tree="b" * 40,
            anchor_is_ancestor=True,
            repository_clean=True,
            observed_asset_sha256={},
            argv=[],
            canonical_argv_sha256="",
            receipt_namespace_consumed=False,
        )


def test_committed_binding_and_reduction_are_canonical_and_sealed() -> None:
    assert canonical(BINDING) == build()
    reduction = sealed(REDUCTION, "reduction")
    assert reduction["terminal"] == TERMINAL
    assert set(reduction["operational_counters"].values()) == {0}
    assert reduction["e05"] == {
        "state": "VERIFIED__11_OF_18",
        "frontier": "VERIFIED__7_UNSATISFIED_OF_18",
        "credit": "VERIFIED__0",
        "expired": "NOT_PROVEN_OPERATIONALLY",
    }
    assert reduction["reuse"] == {
        "ex_reused": "VERIFIED__17_OF_17",
        "ex_reconstructed": "VERIFIED__0",
    }


def test_single_production_route_p11_and_no_operation_are_preserved() -> None:
    source = FM_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    run_calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "subprocess"
        and node.func.attr == "run"
        and node.args
        and isinstance(node.args[0], ast.Name)
        and node.args[0].id == "argv"
    ]
    assert len(run_calls) == 1
    assert "subprocess.run" not in inspect.getsource(
        FM.build_preconsumption_invocation_binding
    )
    assert "subprocess.run" not in inspect.getsource(
        FM.validate_preconsumption_invocation_binding
    )
    assert hashlib.sha256(P11.read_bytes()).hexdigest() == (
        "38399ab9d1eb74dc2a231eb3a363064ba8b90077d6cdbf1d3494ca937b2127f5"
    )
    names = [path.name for path in JZ.rglob("*") if path.is_file()]
    assert not any("HUMAN_OPERATIONAL_AUTHORIZATION" in name for name in names)
    assert not any("PRE_RECEIPT" in name or "POST_RECEIPT" in name for name in names)
    assert not any("SERIAL" in name or "EXECUTION_SEAL" in name for name in names)
    assert subprocess.check_output(
        ["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True
    ).strip() == ""


def test_python_ast_and_g48_exact_structure() -> None:
    ast.parse(FM_PATH.read_text(encoding="utf-8"))
    ast.parse(Path(__file__).read_text(encoding="utf-8"))
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
