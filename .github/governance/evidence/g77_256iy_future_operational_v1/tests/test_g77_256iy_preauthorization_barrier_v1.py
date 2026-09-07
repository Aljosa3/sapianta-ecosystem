#!/usr/bin/env python3
"""Focused Phase A validation for the G77-256IY Human barrier."""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
IY = ROOT / ".github/governance/evidence/g77_256iy_future_operational_v1"
MATERIALIZER_PATH = IY / "orchestration/G77_256IY_PREAUTHORIZATION_MATERIALIZER_V1.py"
CONTROLLER_PATH = IY / "orchestration/G77_256IY_AUTHORITY_CONSUMPTION_CONTROLLER_V1.py"
REPORT_PATH = IY / "G77_256IY_G48_PHASE_A_HUMAN_AUTHORIZATION_BARRIER_REPORT_V1.md"


def load_module(path: Path, name: str):
    specification = importlib.util.spec_from_file_location(name, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


M = load_module(MATERIALIZER_PATH, "g77_256iy_test_materializer")
C = load_module(CONTROLLER_PATH, "g77_256iy_test_controller")


def load_unique(path: Path) -> dict:
    raw = path.read_bytes()
    value = json.loads(raw, object_pairs_hook=M.unique_object)
    assert isinstance(value, dict)
    assert raw == M.canonical_bytes(value)
    return value


def test_exact_ix_entry_lineage_nested_authority_and_frontier() -> None:
    entry = M.authenticate_entry(M.HEAD, M.NESTED_HEAD)
    assert (entry["head"], entry["tree"], entry["subject"]) == (
        M.HEAD,
        M.TREE,
        M.SUBJECT,
    )
    assert entry["local_remote_equality"] == "VERIFIED"
    assert set(entry["lineage"].values()) == {"VERIFIED"}
    assert entry["nested_authority"]["clean"] is True
    assert entry["nested_authority"]["detached"] is True
    ix = M.reconstruct_ix()
    assert ix["status"] == "VERIFIED__COMMITTED_OBJECT_RECONSTRUCTION"
    assert ix["terminal"] == "A__FUTURE_POST_COMMIT_IMPORT_ROOT_FULL_STATIC_READINESS_VERIFIED"
    assert ix["ex_reused"] == "VERIFIED__17_OF_17"
    assert ix["ex_reconstructed"] == "VERIFIED__0"


def test_fresh_identity_future_semantics_and_role_separation() -> None:
    identity = M.derive_identity()
    assert identity["operation_generation"] == M.GENERATION
    assert identity["operation_identity"] == M.OPERATION
    assert identity["committed_history_collision"] == "VERIFIED__NO"
    assert identity["previous_authority_reuse"] == "VERIFIED__NO"
    future = M.authenticate_future_semantics()
    assert (future["evaluation"], future["valid_from"], future["valid_until"]) == (500, 600, 1000)
    assert future["future_semantic_mutation_count"] == 0
    assert future["wall_clock_dependency_count"] == 0
    context = M.FM.fresh_context.load_context(
        IY / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json",
        repository_root=ROOT,
    )
    assert (context["repository_head"], context["repository_tree"]) == (M.HEAD, M.TREE)
    eb = load_unique(IY / "live_binding/v2_readiness/bindings/G77_256IY_EB_RECEIPT_V2.json")["receipt"]
    ee = load_unique(IY / "live_binding/v2_readiness/bindings/G77_256IY_EE_RECEIPT_V2.json")["receipt"]
    assert eb["certification_baseline"] == {"head": M.HEAD, "tree": M.TREE}
    assert (
        eb["runtime_target_selection_binding"]["head"],
        eb["runtime_target_selection_binding"]["tree"],
    ) == (M.IF_HEAD, M.IF_TREE)
    assert ee["certification_baseline"] == eb["certification_baseline"]
    assert ee["runtime_target_selection_binding"] == eb["runtime_target_selection_binding"]


def test_iw_import_root_fm_static_readiness_gl_gn_and_no_network() -> None:
    context = load_unique(IY / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json")
    bindings = context["qemu_executable_base_seed_checkout_bindings"]
    assert bindings["seed"]["sha256"] == "655b8b4122f89acbf0e4d3a670ee3b4fb38fb37600eeb6c8745c0a13cdc57eab"
    assert "g77_256iw_future_guest_import_root_binding_v1" in bindings["seed"]["path"]
    assert all(argument != "-net" and not argument.startswith("-netdev") for argument in context["canonical_argv"])
    static = load_unique(IY / "G77_256IY_PREAUTHORITY_STATIC_READINESS_V1.json")["proof"]
    assert static["readiness"]["result"] == "STATIC_READINESS_PASS"
    assert static["readiness"]["guest_adapter_binding"]["result"] == "PREAUTHORITY_GUEST_ADAPTER_BINDING_PASS"
    assert static["human_operational_authority"] == 0
    equivalence = load_unique(IY / "G77_256IY_GL_PREAUTH_FINAL_ADMISSION_EQUIVALENCE_V1.json")["proof"]
    assert equivalence["preauth_final_admission_equivalence"] == "VERIFIED_WITHIN_EXACT_REVIEWED_RECEIPT_PARENT_BOUNDARY"
    result = M.GN.validate_human_authorization_presentation(
        IY / "G77_256IY_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json",
        (IY / "G77_256IY_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt").read_bytes(),
    )
    assert result["human_presentation_request_equivalence"] == "VERIFIED_WITHIN_EXACT_REVIEWED_AUTHORIZATION_BINDING_BOUNDARY"
    assert result["operational_execution_count"] == 0


def test_terminal_identifiers_and_all_operational_counters() -> None:
    reduction = load_unique(IY / "G77_256IY_PREHUMAN_PHASE_A_REDUCTION_V1.json")["reduction"]
    request_path = IY / "G77_256IY_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
    request = load_unique(request_path)
    checkpoint = load_unique(IY / "G77_256IY_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json")
    presentation = IY / "G77_256IY_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt"
    assert reduction["terminal"] == "HUMAN_AUTHORIZATION_REQUIRED"
    assert reduction["authority_boundary"]["human_operational_authority"] == "VERIFIED__0"
    assert reduction["authority_boundary"]["authority_consumption"] == "VERIFIED__0"
    assert reduction["authority_boundary"]["auto_continuable"] is False
    counters = reduction["operational_counters"]
    assert counters["authorization_presentation"] == 1
    assert all(value == 0 for key, value in counters.items() if key != "authorization_presentation")
    assert reduction["e05"] == {"before": "10/18", "current": "10/18", "credit": 0, "remaining": 8}
    assert hashlib.sha256(request_path.read_bytes()).hexdigest() == "c1efbf64e20376e28c67addec55afc1e365a0bf4125f8af2997e945d207e2100"
    assert request["request_sha256"] == C.REQUEST_SHA256
    assert checkpoint["checkpoint_sha256"] == "e8dd861b67da8b61e3bdbed14a5cb5b008aa7099f2e98b50f0cc13e66f84f7e8"
    assert hashlib.sha256(presentation.read_bytes()).hexdigest() == "2b86bfc04ef66306948d6447f1b272366c14152234ad6fe7c6bea214b3fcab3b"


def test_phase_a_human_sentence_is_preserved_after_the_consumed_authority() -> None:
    expected = (
        "I explicitly authorize G77-256IY request 34ff5f440aed0d2add6dbf194fa160eaa44dafef5a75defc634c3af131dcc4b2 "
        "for operation G77_256IY_E05_FUTURE_DENIAL_BEFORE_ENTRY_001, candidate "
        "ad5d204ec6ace09f18b83fd5f868e73dac5e36dad81149f9f335c87f68cf42f7, context "
        "bf44f090cf5eb27012143187771f66c0c3d7a81518a74fbaf4e5b40a10c9a8e1, and canonical argv "
        "439ebb23c145717cae77f121067a5ecbc94923b44747e271addd11222ef32e07, starting from E05 10/18, "
        "subject to exactly one authority consumption, PRE, FM invocation, no-network QEMU, VM boot, and operation attempt, "
        "with zero retry, repair, replay, or protected effect.\n"
    )
    assert C.EXPECTED_NORMALIZED_GRANT == expected
    # The preauthorization barrier is historical evidence. Its exact Human
    # sentence is now preserved as the source of the already-consumed, strictly
    # nonreusable authority; this test must not reinterpret it as authority or
    # invoke the controller again.
    assert C.GRANT_PATH.read_text(encoding="utf-8").replace("\\_", "_") == expected
    handoff = load_unique(C.HANDOFF_PATH)["authorization"]
    consumption = load_unique(C.CONSUMPTION_PATH)["checkpoint"]
    assert handoff["authorization_reusable"] is False
    assert consumption["authority_state_after"] == "CONSUMED"
    assert consumption["authority_consumed"] == 1


def test_canonical_json_ast_single_route_p11_and_index_firewalls() -> None:
    for path in sorted(IY.rglob("*.json")):
        value = load_unique(path)
        for key, seal in (("reduction", "reduction_sha256"), ("proof", "proof_sha256"),
                          ("checkpoint", "checkpoint_sha256"), ("request", "request_sha256"),
                          ("observation", "observation_sha256")):
            if key in value and seal in value:
                assert value[seal] == hashlib.sha256(M.canonical_bytes(value[key])).hexdigest()
    for path in IY.rglob("*.py"):
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    assert "subprocess.run(argv" not in MATERIALIZER_PATH.read_text(encoding="utf-8")
    assert "subprocess.run(argv" not in CONTROLLER_PATH.read_text(encoding="utf-8")
    assert subprocess.check_output(
        ["git", "diff", "--name-only", M.HEAD, "--", "aigol/runtime", "sapianta_system",
         ".github/governance/evidence/g77_256ec_p11_operational_v1"],
        cwd=ROOT, text=True,
    ).strip() == ""
    assert subprocess.check_output(["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True).strip() == ""


def test_g48_exact_six_headings_and_required_sections() -> None:
    text = REPORT_PATH.read_text(encoding="utf-8")
    assert [line for line in text.splitlines() if line.startswith("# ")] == [
        "# 1. Implementation Summary", "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment", "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary", "# 6. Certification Verdict",
    ]
    required = {
        "Reuse Impact Assessment", "Infrastructure Amortization", "CCWIM",
        "Cognition Provenance", "Cognition-Assisted Handoff", "Prompt Context Reuse",
        "Repository-Derived Execution Context", "Constitutional Prompt Externalization",
        "Token Benchmark", "LLM Cost Reduction Ratio / LCRR", "AIGOL_CODEX_WORK_SHARE",
        "Constitutional Health Evidence", "Shadow Automation", "Historical Failure Firewall",
        "CONSTITUTIONAL_FRONTIER_DISTANCE", "CONSTITUTIONAL_FRONTIER_DISTANCe",
        "E05_FRONTIER_DISTANCE", "GOVERNANCE_EFFICIENCE",
        "ARCHITECTURAL_GOVERNANCE_EFFICIENCE", "PROOF_REUSE_EFFICIENCY",
        "OVERENGINEERING_RISK", "PROOF_PROCESS_OVERHEAD_RISK", "CANDIDATE_CAPABILITY",
        "SHADOW_DESIGN_TARGET", "CONSTITUTIONAL_CONTINUATION_PROGRESS", "EX_REUSED",
        "CHECKED_FAILURE_CLASS_COUNT", "CURRENT_APPLICABLE_ASSERTIONS",
        "HISTORICAL_OR_SUPERSEDED_SNAPSHOT_ASSERTIONS",
    }
    assert all(token in text for token in required)
