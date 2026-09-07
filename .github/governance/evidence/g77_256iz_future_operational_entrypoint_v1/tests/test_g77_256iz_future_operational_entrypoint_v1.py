#!/usr/bin/env python3
"""Repository-only static validation for the IZ FUTURE entrypoint."""

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
IZ = ROOT / ".github/governance/evidence/g77_256iz_future_operational_entrypoint_v1"
ADAPTER = IZ / "adapter/G77_256IZ_FUTURE_VECTOR_ADAPTER_V1.py"
FORMAL = IZ / "G77_256IZ_ENTRYPOINT_FORMAL_ANALYSIS_V1.md"
REPORT = IZ / "G77_256IZ_G48_IMPLEMENTATION_REPORT_V1.md"
REDUCTION = IZ / "G77_256IZ_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
FM_CONTEXT = ROOT / (
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "sapianta_fresh_operation_context_v1.py"
)
FM_LAUNCHER = ROOT / (
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
IY_TERMINAL = ROOT / (
    ".github/governance/evidence/g77_256iy_future_operational_v1/"
    "G77_256IY_SPCE_TERMINAL_REDUCTION_V1.json"
)
EX = ROOT / (
    ".github/governance/evidence/g77_256ex_common_substrate_certification_v1/"
    "G77_256EX_P11_SPCE_COMMON_SUBSTRATE_CERTIFICATION_V1.json"
)
CLOUD = IZ / "static/G77_256IZ_CLOUD_INIT_USER_DATA_V1.yaml"
SEED = IZ / "static/SAPIANTA_FUTURE_NOCLOUD_SEED_V2.img"


def load_module(path: Path, name: str):
    specification = importlib.util.spec_from_file_location(name, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


def unique(pairs):
    value = {}
    for key, item in pairs:
        assert key not in value
        value[key] = item
    return value


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique)


A = load_module(ADAPTER, "g77_256iz_static_adapter")
FM = load_module(FM_CONTEXT, "g77_256iz_static_fm_context")
L = load_module(FM_LAUNCHER, "g77_256iz_static_fm_launcher")


def test_exact_i_y_entry_and_immutable_terminal() -> None:
    assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip() == (
        "fb9756f5b5042df1b601cbcbbee1eda50c443245"
    )
    assert subprocess.check_output(["git", "rev-parse", "HEAD^{tree}"], cwd=ROOT, text=True).strip() == (
        "c6d9e28597b92e3d74c4abb33b808095668e748e"
    )
    reduction = load_json(IY_TERMINAL)["reduction"]
    assert reduction["terminal"] == "E__AUTHORIZED_OPERATION_FAILED_BEFORE_REQUEST"
    assert reduction["first_broken_edge"] == "FUTURE_GUEST_ADAPTER_OPERATIONAL_CLI_ENTRYPOINT_ABSENT"
    assert reduction["operational_counters"]["authority_consumption"] == 1
    assert reduction["operational_counters"]["operation_attempt"] == 1
    assert reduction["operational_counters"]["request"] == 0
    assert reduction["operational_counters"]["p11_entry"] == 0
    assert reduction["e05"] == {"before": "10/18", "credit": 0, "after": "10/18"}
    assert hashlib.sha256(IY_TERMINAL.read_bytes()).hexdigest() == (
        "847260552f707ea824820d452ce980c6a66cb8eba163515f1dbb229c9827d274"
    )


def test_formalization_resolves_a_through_o_before_implementation() -> None:
    text = FORMAL.read_text(encoding="utf-8")
    for letter in "ABCDEFGHIJKLMNO":
        assert f"{letter}. " in text
    assert "UNIQUE_MINIMUM_GOVERNED_REALIZATION = VERIFIED__" in text
    assert "P11BoundedConsumerV1.submit_human_act(now_unix_ns=500)" in text
    assert "second harness route would create a\nparallel production path" in text


def test_exact_ie_future_semantics_and_no_wall_clock_fixture() -> None:
    packet = A.authenticate_future_semantics(ROOT)
    assert packet["evaluation_time_unix_ns"] == 500
    assert packet["baseline_payload"]["valid_from_unix_ns"] == 100
    assert packet["future_payload"]["valid_from_unix_ns"] == 600
    assert packet["future_payload"]["valid_until_unix_ns"] == 1000
    assert packet["differing_payload_fields"] == ["valid_from_unix_ns"]
    assert packet["future_payload_digest"] == A.EXPECTED_FUTURE_PAYLOAD_DIGEST
    assert packet["fixture_uses_wall_clock"] is False


def test_fc_er_specializations_are_closed_count_checked_and_compilable() -> None:
    specialized = A.specialize_fc_runtime_source(
        repository_root=ROOT, identity_namespace_prefix="G77_256ZZ"
    )
    assert specialized.count("now_unix_ns=EVALUATION_TIME_UNIX_NS") == 1
    assert specialized.count('"valid_from_unix_ns": FUTURE_VALID_FROM_UNIX_NS') == 1
    assert specialized.count('"valid_until_unix_ns": VALID_UNTIL_UNIX_NS') == 1
    assert "P11-E05/NEGATIVE_AUTHORITY/FUTURE" in specialized
    assert "G77_256FC" not in specialized
    ast.parse(specialized)
    er = A.load_future_er(ROOT)
    assert er.create_input_and_authority.__code__.co_consts.count(500) >= 1
    assert er.create_input_and_authority.__code__.co_consts.count(100) >= 1
    assert er.create_input_and_authority.__code__.co_consts.count(1000) >= 1


def test_future_reducer_accepts_only_exact_pre_owner_state_denial() -> None:
    counters = {
        "human_operational_act_creation_count": 1,
        "human_operational_act_submitted_count": 0,
        "p11_entry_count": 0,
        "p11_operational_invocation_count": 0,
        "e05_case_execution_count": 1,
    }
    checkpoint = {
        "owner_state_initialization_count": 0,
        "denial_error_type": A.EXPECTED_DENIAL_TYPE,
        "denial_error": A.EXPECTED_DENIAL,
    }
    seal = {
        "operational_result": "PASS__FUTURE_DENIED_AT_D2_SUBMISSION_BEFORE_OWNER_STATE_AND_ENTRY",
        "first_failure": None,
    }
    accepted = A.future_terminal_reduction(
        phase="PHASE_C_EXECUTION_COMPLETE_PENDING_GUEST_TEARDOWN",
        counters=counters,
        first_failure_or_current_result="PASS__FUTURE_SUBMISSION_DENIED_BEFORE_OWNER_STATE_AND_ENTRY",
        first_failure=None,
        authority_checkpoint=checkpoint,
        execution_seal=seal,
    )
    assert accepted["success_evidence_complete"] is True
    assert accepted["e05_credit"] == 1
    rejected = A.future_terminal_reduction(
        phase="PHASE_C_EXECUTION_COMPLETE_PENDING_GUEST_TEARDOWN",
        counters=counters,
        first_failure_or_current_result="PASS__FUTURE_SUBMISSION_DENIED_BEFORE_OWNER_STATE_AND_ENTRY",
        first_failure=None,
        authority_checkpoint=checkpoint | {"owner_state_initialization_count": 1},
        execution_seal=seal,
    )
    assert rejected["success_evidence_complete"] is False
    assert rejected["e05_credit"] == 0


def test_fm_selects_one_iz_adapter_and_successor_nocloud_pair() -> None:
    generation = "G77_256ZZ_ONE_FRESH_HUMAN_AUTHORIZED_FUTURE_OPERATIONAL_COMMISSIONING_V1"
    assert FM.operation_vector(generation) == "FUTURE"
    assert FM.adapter_source_relative_path(generation) == (
        ".github/governance/evidence/g77_256iz_future_operational_entrypoint_v1/"
        "adapter/G77_256IZ_FUTURE_VECTOR_ADAPTER_V1.py"
    )
    assert hashlib.sha256(ADAPTER.read_bytes()).hexdigest() == (
        "e7babafc2a85ebcb59ef3b7aaa70cf220a5a6fb6833dc2f85f8377be5c3c8533"
    )
    bootstrap = L.current_bootstrap_asset_bindings("FUTURE")
    assert bootstrap["cloud_init_path"].endswith("G77_256IZ_CLOUD_INIT_USER_DATA_V1.yaml")
    assert bootstrap["seed_path"].endswith("SAPIANTA_FUTURE_NOCLOUD_SEED_V2.img")
    assert hashlib.sha256(CLOUD.read_bytes()).hexdigest() == bootstrap["cloud_init_sha256"]
    assert hashlib.sha256(SEED.read_bytes()).hexdigest() == bootstrap["seed_sha256"]
    cloud = CLOUD.read_text(encoding="utf-8")
    assert cloud.count("export PYTHONPATH=/mnt/aigol") == 1
    assert cloud.count("/mnt/dp-harness/G77_256FM_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py") == 1
    assert cloud.count("-nic") == 0  # no-network is inherited from FM QEMU argv, not guest input.


def test_seed_projects_exact_sources_and_ex_is_reused_not_rebuilt() -> None:
    expected = {
        "/user-data": CLOUD,
        "/meta-data": ROOT / (
            ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/raw/"
            "G77_256FM_CLOUD_INIT_META_DATA_V1.yaml"
        ),
        "/network-config": ROOT / (
            ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/raw/"
            "G77_256FM_CLOUD_INIT_NETWORK_CONFIG_V1.yaml"
        ),
    }
    for member, source in expected.items():
        projected = subprocess.check_output(["isoinfo", "-i", str(SEED), "-R", "-x", member])
        assert projected == source.read_bytes()
    ex = load_json(EX)["certificate"]
    assert ex["component_counts"]["CERTIFIED"] == 17
    assert ex["certificate_is_credit_authority"] is False


def test_no_p11_or_historical_evidence_mutation_and_index_empty() -> None:
    changed = set(
        subprocess.check_output(["git", "diff", "--name-only"], cwd=ROOT, text=True).splitlines()
    )
    assert not any(path.startswith("tests/p11_") or "g77_256i" in path and not path.startswith(
        ".github/governance/evidence/g77_256iz_"
    ) for path in changed)
    assert changed == {
        ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py",
        ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/sapianta_fresh_operation_context_v1.py",
    }
    assert subprocess.check_output(["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True).strip() == ""


def test_canonical_reduction_inner_seal_ast_and_g48_structure() -> None:
    envelope = load_json(REDUCTION)
    canonical = json.dumps(
        envelope["reduction"], sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")
    assert envelope["reduction_sha256"] == hashlib.sha256(canonical).hexdigest()
    for path in IZ.rglob("*.py"):
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    headings = [
        line for line in REPORT.read_text(encoding="utf-8").splitlines()
        if line.startswith("# ")
    ]
    assert headings == [
        "# 1. Implementation Summary", "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment", "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary", "# 6. Certification Verdict",
    ]


def test_exact_existing_cli_context_request_and_p11_contract_is_reused() -> None:
    """Prove the executable shape without calling the adapter or ER main."""

    adapter_tree = ast.parse(ADAPTER.read_text(encoding="utf-8"))
    mains = [
        node for node in adapter_tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "main"
    ]
    assert len(mains) == 1
    assert A.GUEST_REPOSITORY_ROOT == Path("/mnt/aigol")
    assert A.GUEST_CONTEXT_PATH == Path(
        "/mnt/g77-evidence/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
    )

    specialized_fc = A.specialize_fc_runtime_source(
        repository_root=ROOT, identity_namespace_prefix="G77_256ZZ"
    )
    specialized_er = (ROOT / A.ER_HARNESS).read_text(encoding="utf-8")
    assert specialized_er.count("if len(sys.argv) != 6:") == 1
    assert specialized_er.count(
        "expected_harness, schema_sha, expected_head, expected_tree, dn_harness_sha = sys.argv[1:]"
    ) == 1
    assert specialized_fc.count("CustodyRequest(") == 1
    assert specialized_fc.count("consumer.submit_human_act(") == 1
    assert specialized_fc.count("now_unix_ns=EVALUATION_TIME_UNIX_NS") == 1
    assert specialized_fc.count("bind_record_identity(") >= 2
    assert specialized_fc.count("canonical_human_authority_payload_digest_v1(") >= 1
    assert specialized_fc.count("rebind_canonical_correlation(") >= 1
    assert "initialize_available(" not in specialized_fc
    assert "valid_from <=" not in ADAPTER.read_text(encoding="utf-8")


def test_malformed_guest_context_fails_before_runtime_entry(tmp_path: Path) -> None:
    malformed = tmp_path / "context.json"
    malformed.write_text('{"schema_id":"NOT_THE_CONTEXT"}\n', encoding="utf-8")
    with pytest.raises(Exception):
        A.load_guest_runtime_namespace(repository_root=ROOT, context_path=malformed)


def test_two_owner_mutations_are_only_closed_future_successor_rebindings() -> None:
    launcher_relative = FM_LAUNCHER.relative_to(ROOT).as_posix()
    context_relative = FM_CONTEXT.relative_to(ROOT).as_posix()
    changed = subprocess.check_output(
        ["git", "diff", "--name-only"], cwd=ROOT, text=True
    ).splitlines()
    assert changed == [launcher_relative, context_relative]

    baseline_context = subprocess.check_output(
        ["git", "show", f"HEAD:{context_relative}"], cwd=ROOT, text=True
    )
    current_context = FM_CONTEXT.read_text(encoding="utf-8")
    assert baseline_context.count(
        "g77_256if_future_post_commit_readiness_v1/"
    ) == 1
    assert current_context.count(
        "g77_256iz_future_operational_entrypoint_v1/"
    ) == 1
    for vector in ("WRONG_ATTEMPT", "WRONG_INPUT", "WRONG_CONTRACT", "WRONG_PROVENANCE"):
        assert baseline_context.count(f'{vector}_ADAPTER_SOURCE_RELATIVE_PATH') == current_context.count(
            f'{vector}_ADAPTER_SOURCE_RELATIVE_PATH'
        )

    baseline_launcher = subprocess.check_output(
        ["git", "show", f"HEAD:{launcher_relative}"], cwd=ROOT, text=True
    )
    current_launcher = FM_LAUNCHER.read_text(encoding="utf-8")
    assert baseline_launcher.count(
        "g77_256iw_future_guest_import_root_binding_v1/"
    ) == 2
    assert current_launcher.count(
        "g77_256iz_future_operational_entrypoint_v1/"
    ) == 2
    assert baseline_launcher.count("def main() -> int:") == 1
    assert current_launcher.count("def main() -> int:") == 1
    assert baseline_launcher.count("def current_bootstrap_asset_bindings(") == 1
    assert current_launcher.count("def current_bootstrap_asset_bindings(") == 1


def test_g48_v1_required_contents_and_result_vocabulary() -> None:
    text = REPORT.read_text(encoding="utf-8")
    for required in (
        "Generation: G77-256IZ",
        "Report identity: G77_256IZ_G48_IMPLEMENTATION_REPORT_V1",
        "Reporting date: 2026-09-07",
        "Constitutional baseline:",
        "Implementation contracts:",
        "## Public API",
        "## Orchestration Entry Point",
        "## Semantic Reductions",
        "## Public Validators",
        "## Canonical Data Models",
        "## Deterministic Algorithms",
        "## Responsibility Boundaries",
        "## Verified",
        "## Not Verified",
        "| Requirement | Evidence | Validation | Result |",
        "PRODUCTION_OWNER_MUTATION_SET = VERIFIED__FM_LAUNCHER_AND_FM_OPERATION_CONTEXT_OWNER",
        "COGNITION_ASSISTED_HANDOFF = VERIFIED__REPOSITORY_DERIVED_CROSS_WORKER_SAME_GENERATION_IZ_RECOVERY",
        "COGNITION_PROVENANCE = VERIFIED__RATIFIED_IY_CHECKPOINT_AND_AUTHENTICATED_UNCOMMITTED_IZ_DELTA_PRIMARY",
        "PROJECT_PROGRESS = NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR",
    ):
        assert required in text
    assert text.rstrip().endswith(
        "A__FUTURE_GOVERNED_OPERATIONAL_ADAPTER_ENTRYPOINT_REPOSITORY_ONLY_STATIC_READINESS_VERIFIED"
    )
