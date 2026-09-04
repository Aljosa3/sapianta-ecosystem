#!/usr/bin/env python3
"""Focused repository-only proof for G77-256HV."""

from __future__ import annotations

import ast
from copy import deepcopy
import hashlib
import importlib.util
from io import BytesIO
import json
from pathlib import Path
import subprocess
import sys
import tarfile

import pytest


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
HV = ROOT / (
    ".github/governance/evidence/"
    "g77_256hv_wrong_contract_checkout_bootstrap_correction_v1"
)
AUDITOR_PATH = HV / "audit/G77_256HV_WRONG_CONTRACT_CHECKOUT_BOOTSTRAP_AUDITOR_V1.py"
REDUCER_PATH = HV / "audit/G77_256HV_TERMINAL_REDUCER_V1.py"
TERMINAL = HV / "G77_256HV_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
REPORT = ROOT / "docs/governance/G77_256HV_WRONG_CONTRACT_CHECKOUT_BOOTSTRAP_COMMITTED_IDENTITY_CORRECTION_V1.md"
GN_PATH = ROOT / (
    ".github/governance/evidence/g77_256gn_human_authorization_presentation_binding_v1/"
    "presentation/G77_256GN_SEALED_REQUEST_HUMAN_AUTHORIZATION_PRESENTATION_V1.py"
)
HP_REQUEST = ROOT / (
    ".github/governance/evidence/g77_256hp_wrong_input_operational_v1/"
    "G77_256HP_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
)


def load_module(path: Path, identity: str):
    specification = importlib.util.spec_from_file_location(identity, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


AUDITOR = load_module(AUDITOR_PATH, "g77_256hv_test_auditor")
LAUNCHER = load_module(ROOT / AUDITOR.FM_LAUNCHER, "g77_256hv_test_launcher")
OWNER = LAUNCHER.fresh_context
ADAPTER = load_module(ROOT / AUDITOR.ADAPTER, "g77_256hv_test_adapter")
GN = load_module(GN_PATH, "g77_256hv_test_gn")


def git(*arguments: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(["git", *arguments], cwd=cwd, text=True).strip()


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def archive_selected_checkout(destination: Path) -> Path:
    paths = [path.as_posix() for path in AUDITOR.DEPENDENCY_CLOSURE]
    archive = subprocess.check_output(
        ["git", "archive", "--format=tar", AUDITOR.HT_HEAD, "--", *paths], cwd=ROOT
    )
    destination.mkdir(parents=True)
    with tarfile.open(fileobj=BytesIO(archive), mode="r:") as value:
        for member in value.getmembers():
            assert not member.name.startswith("/") and ".." not in Path(member.name).parts
        value.extractall(destination, filter="data")
    return destination


def test_exact_hu_checkpoint_ancestry_remote_and_nested_authority() -> None:
    observed = AUDITOR.authenticate_hu_checkpoint(ROOT)
    assert observed["head"] == AUDITOR.HU_HEAD
    assert observed["tree"] == AUDITOR.HU_TREE
    assert observed["subject"] == AUDITOR.HU_SUBJECT
    assert observed["remote_head"] == AUDITOR.HU_HEAD
    assert observed["index"] == ""
    assert observed["nested"]["head"] == AUDITOR.NESTED_HEAD
    assert observed["nested"]["tree"] == AUDITOR.NESTED_TREE
    assert observed["nested"]["branch"] == observed["nested"]["status"] == ""


def test_hu_blocker_is_reconstructed_from_committed_objects() -> None:
    blocker = AUDITOR.reconstruct_hu_blocker(ROOT)
    assert blocker == blocker | {
        "status": "VERIFIED",
        "hg_head": AUDITOR.HG_HEAD,
        "hg_tree": AUDITOR.HG_TREE,
        "last_verified_edge": (
            "HOST_PROJECTS_COMMITTED_HT_WRONG_CONTRACT_ADAPTER_AND_BINDS_ITS_"
            "EXACT_HASH_IN_COMMITTED_BOOTSTRAP"
        ),
        "first_broken_edge": (
            "GUEST_ADAPTER_LOADS_FM_CONTEXT_OWNER_FROM_HG_PINNED_CHECKOUT_"
            "WHERE_WRONG_CONTRACT_IS_UNSUPPORTED"
        ),
    }
    stale = subprocess.check_output(
        ["git", "show", f"{AUDITOR.HG_HEAD}:{AUDITOR.FM_CONTEXT.as_posix()}"], cwd=ROOT
    )
    assert b"WRONG_CONTRACT" not in stale


def test_ht_is_unique_minimum_coherent_checkout_and_closure_is_complete() -> None:
    selection = AUDITOR.select_checkout(ROOT)
    assert selection["selected_checkout_head"] == AUDITOR.HT_HEAD
    assert selection["selected_checkout_tree"] == AUDITOR.HT_TREE
    assert selection["dependency_closure_status"] == "VERIFIED"
    assert selection["post_ht_route_dependency_required"] is False
    assert set(selection["dependency_identities"]) == {
        path.as_posix() for path in AUDITOR.DEPENDENCY_CLOSURE
    }
    assert git("rev-parse", AUDITOR.HT_HEAD + "^{tree}") == AUDITOR.HT_TREE


def test_fm_checkout_and_wrong_contract_bootstrap_use_exact_ht_pair() -> None:
    correction = AUDITOR.audit_correction(ROOT)
    assert correction["checkout_owner_binding_status"] == "VERIFIED"
    assert correction["wrong_contract_bootstrap_head_tree_status"] == "VERIFIED"
    assert correction["checkout_bootstrap_coherence_status"] == "VERIFIED"
    assert LAUNCHER.CHECKOUT_HEAD == AUDITOR.HT_HEAD
    assert LAUNCHER.CHECKOUT_TREE == AUDITOR.HT_TREE
    bootstrap = LAUNCHER.current_bootstrap_asset_bindings("WRONG_CONTRACT")
    assert bootstrap == {
        "cloud_init_path": LAUNCHER.WRONG_CONTRACT_CLOUD_INIT,
        "cloud_init_sha256": AUDITOR.EXPECTED_CLOUD_INIT_SHA256,
        "seed_path": LAUNCHER.WRONG_CONTRACT_SEED,
        "seed_sha256": AUDITOR.EXPECTED_SEED_SHA256,
    }


def test_expected_harness_adapter_identity_is_preserved_exactly() -> None:
    correction = AUDITOR.audit_correction(ROOT)
    assert correction["expected_harness_binding_preservation_status"] == "VERIFIED"
    assert correction["wrong_contract_expected_harness_sha256"] == (
        correction["committed_wrong_contract_adapter_sha256"]
    ) == AUDITOR.EXPECTED_ADAPTER_SHA256
    assert git("diff", "--name-only", "HEAD", "--", AUDITOR.ADAPTER.as_posix()) == ""


def test_wrong_contract_seed_projects_corrected_source_and_common_metadata() -> None:
    for member, source in {
        "/user-data": ROOT / AUDITOR.CLOUD_INIT,
        "/meta-data": ROOT / AUDITOR.FM_META,
        "/network-config": ROOT / AUDITOR.FM_NETWORK,
    }.items():
        projected = subprocess.check_output(
            ["isoinfo", "-i", str(ROOT / AUDITOR.SEED), "-R", "-x", member],
            stderr=subprocess.DEVNULL,
        )
        assert projected == source.read_bytes()
    assert sha256_path(ROOT / AUDITOR.SEED) == AUDITOR.EXPECTED_SEED_SHA256


@pytest.mark.parametrize("vector", ("WRONG_ATTEMPT", "WRONG_INPUT", "WRONG_CONTRACT"))
def test_host_context_selects_all_exact_vectors(vector: str) -> None:
    assert OWNER.operation_vector(AUDITOR.generation(vector)) == vector
    assert LAUNCHER.current_bootstrap_asset_bindings(vector)
    fields = LAUNCHER.authorization_fields({"authorized_vector": vector})
    assert LAUNCHER.operation_attempt_limit_field(vector) in fields
    assert sum(value.endswith("operational_attempt_limit") for value in fields) == 1


@pytest.mark.parametrize(
    "generation",
    (
        "G77_256HVTEST_ONE_FRESH_HUMAN_AUTHORIZED_UNKNOWN_OPERATIONAL_COMMISSIONING_V1",
        "G77_256HVTEST_WRONG_CONTRACT",
        "",
    ),
)
def test_unknown_and_malformed_contexts_fail_closed(generation: str) -> None:
    with pytest.raises(OWNER.ContextError, match="no exact supported operation vector"):
        OWNER.operation_vector(generation)


def test_selected_guest_checkout_matches_host_vector_semantics(tmp_path: Path) -> None:
    checkout = archive_selected_checkout(tmp_path / "mnt-aigol-static-projection")
    guest_owner = load_module(
        checkout / AUDITOR.FM_CONTEXT, "g77_256hv_selected_guest_context"
    )
    for vector in ("WRONG_ATTEMPT", "WRONG_INPUT", "WRONG_CONTRACT"):
        identity = AUDITOR.generation(vector)
        assert guest_owner.operation_vector(identity) == OWNER.operation_vector(identity) == vector
    for malformed in (
        "G77_256HVTEST_ONE_FRESH_HUMAN_AUTHORIZED_UNKNOWN_OPERATIONAL_COMMISSIONING_V1",
        "MALFORMED",
    ):
        with pytest.raises(guest_owner.ContextError):
            guest_owner.operation_vector(malformed)


def test_selected_guest_checkout_satisfies_adapter_dependencies(tmp_path: Path) -> None:
    checkout = archive_selected_checkout(tmp_path / "mnt-aigol-static-adapter")
    guest_adapter = load_module(
        checkout / AUDITOR.ADAPTER, "g77_256hv_selected_guest_adapter"
    )
    projection = guest_adapter.construct_wrong_contract_payload(
        repository_root=checkout,
        wrong_contract_identity="G77_256HV_DISTINCT_WRONG_CONTRACT_001",
        request_identity="G77_256HV_TEST_ONLY_REQUEST_FIXTURE_001",
    )
    semantics = projection["semantic_binding"]
    assert semantics["target_mutated_coordinate"] == "contract_identity"
    assert semantics["dependent_recomputation_fields"] == ["record_identity"]
    assert semantics["semantic_mutation_count"] == 1
    assert semantics["differing_input_fields"] == ["contract_identity", "record_identity"]
    assert projection["request_is_authority"] is False
    assert projection["adapter_invoked_p11"] is False
    specialized = guest_adapter.specialize_fc_runtime_source(
        repository_root=checkout, identity_namespace_prefix="G77_256HVTEST"
    )
    assert specialized.count('wrong_value["contract_identity"] = WRONG_CONTRACT_ID') == 1
    assert 'wrong_value["input_identity"] = WRONG_CONTRACT_ID' not in specialized
    assert 'wrong_value["attempt_identity"] = WRONG_CONTRACT_ID' not in specialized


def _reseal_request(envelope: dict) -> None:
    envelope["request_sha256"] = hashlib.sha256(
        GN._canonical_bytes(envelope["request"])
    ).hexdigest()


def test_wrong_input_wrong_contract_presentation_substitution_is_rejected(
    tmp_path: Path,
) -> None:
    base = json.loads(HP_REQUEST.read_bytes())
    cases = (
        ("WRONG_INPUT", AUDITOR.generation("WRONG_CONTRACT")),
        ("WRONG_CONTRACT", AUDITOR.generation("WRONG_INPUT")),
    )
    for index, (vector, generation) in enumerate(cases):
        value = deepcopy(base)
        value["request"]["authorized_vector_requested"] = vector
        value["request"]["generation_identity"] = generation
        _reseal_request(value)
        path = tmp_path / f"substitution-{index}.json"
        path.write_bytes(GN._canonical_bytes(value))
        with pytest.raises(
            GN.PresentationBindingError,
            match="SEALED_REQUEST_VECTOR_GENERATION_BINDING_INVALID",
        ):
            GN.render_human_authorization_presentation(path)


def test_wrong_attempt_and_wrong_input_bootstrap_artifacts_are_unchanged() -> None:
    bindings = (
        LAUNCHER.current_bootstrap_asset_bindings("WRONG_ATTEMPT"),
        LAUNCHER.current_bootstrap_asset_bindings("WRONG_INPUT"),
    )
    for binding in bindings:
        cloud_path = Path(binding["cloud_init_path"])
        seed_path = Path(binding["seed_path"])
        cloud = cloud_path.relative_to(ROOT) if cloud_path.is_absolute() else cloud_path
        seed = seed_path.relative_to(ROOT) if seed_path.is_absolute() else seed_path
        assert (ROOT / cloud).read_bytes() == subprocess.check_output(
            ["git", "show", f"{AUDITOR.HU_HEAD}:{cloud.as_posix()}"], cwd=ROOT
        )
        assert (ROOT / seed).read_bytes() == subprocess.check_output(
            ["git", "show", f"{AUDITOR.HU_HEAD}:{seed.as_posix()}"], cwd=ROOT
        )
        assert sha256_path(ROOT / cloud) == binding["cloud_init_sha256"]
        assert sha256_path(ROOT / seed) == binding["seed_sha256"]


def test_one_route_and_exact_tracked_owner_mutation_set() -> None:
    launcher_tree = ast.parse((ROOT / AUDITOR.FM_LAUNCHER).read_text(encoding="utf-8"))
    main = [node for node in launcher_tree.body if isinstance(node, ast.FunctionDef) and node.name == "main"]
    qemu_calls = [
        node
        for node in ast.walk(main[0])
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "subprocess"
        and node.func.attr == "run"
    ]
    assert len(main) == len(qemu_calls) == 1
    assert set(git("diff", "--name-only", "HEAD").splitlines()) == {
        AUDITOR.FM_LAUNCHER.as_posix(),
        AUDITOR.CLOUD_INIT.as_posix(),
        AUDITOR.SEED.as_posix(),
    }
    assert git("diff", "--cached", "--name-only") == ""


def test_ex_is_reused_without_reconstruction() -> None:
    assert AUDITOR.authenticate_ex_reuse(ROOT) == {
        "ex_reused": "17/17",
        "ex_reconstructed": 0,
        "status": "VERIFIED",
    }


def test_terminal_reduction_is_canonical_sealed_and_zero_operation() -> None:
    raw = TERMINAL.read_bytes()
    value = json.loads(raw, object_pairs_hook=AUDITOR._unique_object)
    assert raw == AUDITOR.canonical_bytes(value)
    assert value["reduction_sha256"] == hashlib.sha256(
        AUDITOR.canonical_bytes(value["reduction"])
    ).hexdigest()
    reduction = value["reduction"]
    assert set(reduction["operational_counters"].values()) == {0}
    assert reduction["e05"] == {"before": "8/18", "credit": 0, "after": "8/18"}
    assert set(reduction["readiness"].values()) == {"NOT_PROVEN"}
    assert reduction["terminal_control"]["auto_continuable"] is False
    assert reduction["terminal_control"]["human_review_required"] is True


def test_g48_report_has_exactly_six_top_level_headings() -> None:
    report = REPORT.read_text(encoding="utf-8")
    assert [line for line in report.splitlines() if line.startswith("# ")] == [
        "# 1. Implementation Summary",
        "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment",
        "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary",
        "# 6. Certification Verdict",
    ]
    required = (
        "SELECTED_CHECKOUT_HEAD",
        "HOST_GUEST_CONTEXT_VECTOR_SEMANTIC_EQUIVALENCE",
        "Reuse Impact Assessment",
        "CCWIM_MATURITY_LEVEL",
        "COGNITION_PROVENANCE",
        "DID_HV_REQUIRE_NEW_COMMON_INFRASTRUCTURE?",
        "E05_AFTER_HV = 8/18",
        "AUTO_CONTINUABLE = NO",
        "HUMAN_REVIEW_REQUIRED = YES",
    )
    assert all(token in report for token in required)


def test_auditor_and_reducer_have_no_operational_entrypoint() -> None:
    source = AUDITOR_PATH.read_text(encoding="utf-8") + REDUCER_PATH.read_text(encoding="utf-8")
    prohibited = (
        "subprocess.Popen",
        "run_qemu_once(",
        "launch_once(",
        "invoke_pre(",
        "request_authority(",
        "consume_authority(",
    )
    assert not any(token in source for token in prohibited)
