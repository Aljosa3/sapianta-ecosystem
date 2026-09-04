#!/usr/bin/env python3
"""Authority-free tests for the G77-256HU committed-route audit."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import importlib.util
from pathlib import Path
import subprocess
import sys

import pytest


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
HU = ROOT / ".github/governance/evidence/g77_256hu_post_ht_live_binding_readiness_v1"
AUDITOR_PATH = HU / "audit/G77_256HU_POST_HT_COMMITTED_IDENTITY_AUDITOR_V1.py"
TERMINAL = HU / "G77_256HU_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
REPORT = ROOT / "docs/governance/G77_256HU_POST_HT_WRONG_CONTRACT_COMMITTED_IDENTITY_LIVE_BINDING_AND_PREOPERATIONAL_READINESS_CERTIFICATION_V1.md"


def load_module(path: Path, identity: str):
    specification = importlib.util.spec_from_file_location(identity, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


AUDITOR = load_module(AUDITOR_PATH, "g77_256hu_auditor")


def rejects(call) -> bool:
    try:
        call()
    except Exception:
        return True
    return False


def test_exact_ht_entry_ancestry_remote_tracking_and_nested_authority() -> None:
    observed = AUDITOR.authenticate_entry(ROOT)
    assert observed["head"] == AUDITOR.EXPECTED_HEAD
    assert observed["tree"] == AUDITOR.EXPECTED_TREE
    assert observed["subject"] == AUDITOR.EXPECTED_SUBJECT
    assert observed["parent"] == AUDITOR.EXPECTED_PARENT
    assert observed["remote_tracking_head"] == AUDITOR.EXPECTED_HEAD
    assert observed["nested"]["head"] == AUDITOR.NESTED_HEAD
    assert observed["nested"]["branch"] == ""
    assert observed["nested"]["status"] == ""
    assert subprocess.check_output(
        ["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True
    ).strip() == ""


def test_committed_identity_map_uses_exact_ht_git_objects() -> None:
    identities = AUDITOR.committed_identity_map(ROOT)
    assert set(identities) == set(AUDITOR.IDENTITY_PATHS)
    assert all(item["committed_identity_status"] == "VERIFIED" for item in identities.values())
    for item in identities.values():
        committed = subprocess.check_output(
            ["git", "show", f"{AUDITOR.EXPECTED_HEAD}:{item['path']}"], cwd=ROOT
        )
        assert hashlib.sha256(committed).hexdigest() == item["sha256"]
        assert subprocess.check_output(
            ["git", "rev-parse", f"{AUDITOR.EXPECTED_HEAD}:{item['path']}"],
            cwd=ROOT,
            text=True,
        ).strip() == item["git_blob_id"]


def test_ht_hr_and_ex_reconstruct_from_committed_bytes() -> None:
    reconstructed = AUDITOR.authenticate_ht_and_hr(ROOT)
    assert reconstructed["ht"]["readiness_reduction"]["post_commit_rebind_required"] == "VERIFIED"
    assert reconstructed["ht"]["e05"] == {"before": "8/18", "credit": 0, "after": "8/18"}
    assert reconstructed["hr"]["mutation_rule"] == reconstructed["hr"]["mutation_rule"] | {
        "target_field": "contract_identity",
        "dependent_recomputation": "record_identity",
        "semantic_mutation_count": 1,
    }
    assert AUDITOR.authenticate_ex_reuse(ROOT) == {
        "ex_reused": "17/17",
        "ex_reconstructed": 0,
    }


def test_committed_expected_harness_relation_is_exact() -> None:
    result = AUDITOR.audit_committed_route(ROOT)
    assert result["expected_harness_binding_status"] == "VERIFIED"
    assert result["wrong_contract_expected_harness_sha256"] == result[
        "committed_wrong_contract_adapter_sha256"
    ]


def test_current_host_selector_and_bootstrap_reach_stale_hg_guest_context() -> None:
    result = AUDITOR.audit_committed_route(ROOT)
    assert result["host_wrong_contract_selector_status"] == "VERIFIED"
    assert (result["checkout_head"], result["checkout_tree"]) == (
        AUDITOR.HG_HEAD,
        AUDITOR.HG_TREE,
    )
    assert result["checkout_contains_committed_ht"] is False
    assert result["guest_checkout_context_wrong_contract_support"] == "NOT_PROVEN"
    assert result["first_broken_edge"] == (
        "GUEST_ADAPTER_LOADS_FM_CONTEXT_OWNER_FROM_HG_PINNED_CHECKOUT_"
        "WHERE_WRONG_CONTRACT_IS_UNSUPPORTED"
    )


def test_hg_checkout_context_owner_rejects_wrong_contract() -> None:
    source = subprocess.check_output(
        ["git", "show", f"{AUDITOR.HG_HEAD}:{AUDITOR.FM_CONTEXT.as_posix()}"], cwd=ROOT
    )
    namespace = {"__name__": "g77_256hu_hg_context", "__file__": str(AUDITOR.FM_CONTEXT)}
    exec(compile(source, str(AUDITOR.FM_CONTEXT), "exec"), namespace)
    with pytest.raises(namespace["ContextError"], match="no exact supported operation vector"):
        namespace["operation_vector"](AUDITOR.GENERATION)


def test_current_ht_context_owner_accepts_wrong_contract_but_does_not_repair_guest_checkout() -> None:
    namespace = {"__name__": "g77_256hu_ht_context", "__file__": str(AUDITOR.FM_CONTEXT)}
    source = subprocess.check_output(
        ["git", "show", f"{AUDITOR.EXPECTED_HEAD}:{AUDITOR.FM_CONTEXT.as_posix()}"], cwd=ROOT
    )
    exec(compile(source, str(AUDITOR.FM_CONTEXT), "exec"), namespace)
    assert namespace["operation_vector"](AUDITOR.GENERATION) == AUDITOR.VECTOR
    assert namespace["adapter_source_relative_path"](AUDITOR.GENERATION) == AUDITOR.ADAPTER.as_posix()


@pytest.mark.parametrize(
    "field",
    (
        "ht_head",
        "ht_tree",
        "hr_spec",
        "hr_producer",
        "hr_reducer",
        "fm_context_owner",
        "fm_launcher",
        "gn_owner",
        "adapter",
        "materializer",
        "cloud_init",
        "nocloud_seed",
        "candidate",
        "runtime",
        "context_candidate",
        "context",
        "checkout_head",
        "checkout_tree",
        "projection",
        "expected_harness",
        "vector",
        "presentation_vector",
        "du",
        "eb",
        "ee",
    ),
)
def test_negative_matrix_rejects_each_stale_or_incoherent_binding(field: str) -> None:
    chain = deepcopy(AUDITOR.coherent_future_chain_fixture(ROOT))
    chain[field] = "MALFORMED_OR_STALE"
    assert rejects(lambda: AUDITOR.validate_coherent_future_chain(ROOT, chain))


@pytest.mark.parametrize(
    ("vector", "presentation"),
    (
        ("UNKNOWN", "UNKNOWN"),
        ("MALFORMED", "WRONG_CONTRACT"),
        ("WRONG_INPUT", "WRONG_CONTRACT"),
        ("WRONG_CONTRACT", "WRONG_INPUT"),
    ),
)
def test_unknown_malformed_and_cross_vector_substitution_reject(
    vector: str, presentation: str
) -> None:
    chain = deepcopy(AUDITOR.coherent_future_chain_fixture(ROOT))
    chain["vector"] = vector
    chain["presentation_vector"] = presentation
    assert rejects(lambda: AUDITOR.validate_coherent_future_chain(ROOT, chain))


def test_current_committed_chain_cannot_be_misreported_as_coherent() -> None:
    chain = AUDITOR.coherent_future_chain_fixture(ROOT)
    chain["checkout_head"] = AUDITOR.HG_HEAD
    chain["checkout_tree"] = AUDITOR.HG_TREE
    chain["du"] = chain["eb"] = chain["ee"] = "NOT_PROVEN"
    assert rejects(lambda: AUDITOR.validate_coherent_future_chain(ROOT, chain))


def test_hard_no_operation_firewall_and_single_route() -> None:
    source = AUDITOR_PATH.read_text(encoding="utf-8")
    prohibited_tokens = (
        "subprocess.Popen",
        "run_qemu_once(",
        "launch_once(",
        "invoke_pre(",
        "request_authority(",
        "consume_authority(",
    )
    assert not any(token in source for token in prohibited_tokens)
    assert sum(
        path.name == "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
        for path in ROOT.rglob("G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py")
    ) == 1


def test_terminal_reduction_and_g48_shape_report_truthful_failure_branch() -> None:
    terminal = AUDITOR._committed_json if False else None  # keep operational imports absent
    raw = TERMINAL.read_bytes()
    value = __import__("json").loads(raw, object_pairs_hook=AUDITOR._unique_object)
    assert raw == AUDITOR.canonical_bytes(value)
    assert value["reduction_sha256"] == AUDITOR.sha256_bytes(
        AUDITOR.canonical_bytes(value["reduction"])
    )
    reduction = value["reduction"]
    assert reduction["readiness"]["preoperational_readiness_status"] == "NOT_PROVEN"
    assert reduction["du_eb_ee"] == {
        "current_du_status": "NOT_PROVEN",
        "current_eb_status": "NOT_PROVEN",
        "current_ee_status": "NOT_PROVEN",
    }
    assert set(reduction["operational_counters"].values()) == {0}
    headings = [line for line in REPORT.read_text(encoding="utf-8").splitlines() if line.startswith("# ")]
    assert headings == [
        "# 1. Implementation Summary",
        "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment",
        "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary",
        "# 6. Certification Verdict",
    ]
