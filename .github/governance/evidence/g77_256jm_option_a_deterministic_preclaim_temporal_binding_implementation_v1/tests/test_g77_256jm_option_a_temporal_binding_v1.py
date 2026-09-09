"""Repository-only verification of the G77-256JM Option A binding.

The suite never calls submit_human_act, claim_and_invoke_once, PRE, FM main,
QEMU, or a VM.  It exercises only pure construction, authentication, and
reduction surfaces.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
import importlib.util
import inspect
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tarfile

import pytest


ROOT = Path(__file__).resolve().parents[5]
NAMESPACE = ROOT / (
    ".github/governance/evidence/"
    "g77_256jm_option_a_deterministic_preclaim_temporal_binding_implementation_v1"
)
FM_OWNER = ROOT / (
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "sapianta_fresh_operation_context_v1.py"
)
LAUNCHER_PATH = FM_OWNER.parent / "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
JL_REDUCTION = ROOT / (
    ".github/governance/evidence/"
    "g77_256jl_p11_custody_owned_deterministic_preclaim_temporal_owner_contract_v1/"
    "G77_256JL_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
)
REPORT = NAMESPACE / "G77_256JM_G48_IMPLEMENTATION_REPORT_V1.md"
REDUCTION = NAMESPACE / "G77_256JM_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"

sys.path.insert(0, str(ROOT / "tests"))
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash
from p11_da_custody_process_v1 import FixedPrincipalBindings
from p11_da_operational_consumer_v1 import (
    CH_PASS_CONJUNCTION,
    P11BoundedConsumerV1,
    ProtectedOwnerStateStoreV1,
    authenticate_preclaim_temporal_binding,
    create_commissioning_gate_v1,
    fixed_endpoint_identity,
    fixed_principal_bindings_identity,
    fixture_root_identity,
    materialization_identity,
    preclaim_temporal_binding_identity,
    preclaim_temporal_decision,
)


def load_module(path: Path, name: str):
    specification = importlib.util.spec_from_file_location(name, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


FM = load_module(FM_OWNER, "g77_256jm_fm_context_owner")
LAUNCHER = load_module(LAUNCHER_PATH, "g77_256jm_fm_launcher")


def context_for(root: Path) -> dict:
    prefix = "G77_256JMTEST"
    return LAUNCHER.build_operation_context(
        repository_root=ROOT,
        repository_head="a" * 40,
        repository_tree="b" * 40,
        generation_identity=(
            prefix
            + "_ONE_FRESH_HUMAN_AUTHORIZED_FUTURE_OPERATIONAL_COMMISSIONING_V1"
        ),
        operation_identity=prefix + "_OPERATION_001",
        identity_namespace_prefix=prefix,
        operation_evidence_root=root / "operation_state",
        transient_root=root / "transient",
    )


def reseal(context: dict) -> dict:
    value = {key: item for key, item in context.items() if key != "context_sha256"}
    context["context_sha256"] = hashlib.sha256(FM.canonical_bytes(value)).hexdigest()
    return context


def gate_for(context: dict, store: ProtectedOwnerStateStoreV1, bindings):
    fixture = fixture_root_identity(store.fixture_root, bindings.custody_uid)
    principal = fixed_principal_bindings_identity(bindings)
    endpoint = fixed_endpoint_identity(store.fixture_root, bindings.custody_uid)
    materialization = materialization_identity(
        fixture_identity=fixture,
        principal_identity=principal,
        endpoint_identity=endpoint,
        owner_state_identity=store.root_identity,
    )
    return create_commissioning_gate_v1(
        dh_checkpoint="9f5fd37212547cf06b664c94152ae0ec50a55b79",
        ch_decision_package_identity=(
            "G77_256CH_P11_E01_E12_OPERATIONAL_EVIDENCE_GENERATION_"
            "HUMAN_AUTHORIZATION_DECISION_PACKAGE_V1"
        ),
        ch_artifact_sha256=(
            "d07f6eae99abd6f95b37553c84eb226298e40e5c61f42f5597980d784a16e2ce"
        ),
        cg_checkpoint="authenticated-cg-checkpoint",
        cg_report_identity="authenticated-cg-report",
        cd_plan_identity="authenticated-cd-plan",
        cd_plan_sha256="1" * 64,
        cf_source_tree_identity="bb5382994b266e53358acb286ef06f41ce2936e6",
        cf_source_sha256=(
            "a1b58fa8ddedb5058393aa23d815262c92c8b185c0b193764f77420313af0bab"
        ),
        materialization_identity=materialization,
        fixture_root_identity=fixture,
        principal_bindings_identity=principal,
        endpoint_identity=endpoint,
        owner_state_root_identity=store.root_identity,
        operation_context_sha256=context["context_sha256"],
        preclaim_temporal_binding_identity=preclaim_temporal_binding_identity(
            context["preclaim_temporal_binding"]
        ),
        condition_results=CH_PASS_CONJUNCTION,
        condition_evidence_identities=tuple(
            (f"P{number:02d}", f"evidence-{number:02d}")
            for number in range(1, 13)
        ),
    )


def store_for(root: Path) -> ProtectedOwnerStateStoreV1:
    fixture = root / "fixture"
    fixture.mkdir(mode=0o700)
    return ProtectedOwnerStateStoreV1(fixture, os.getuid())


def test_jl_contract_is_reconstructed_exactly() -> None:
    value = json.loads(JL_REDUCTION.read_bytes())["reduction"]
    assert value["terminal"] == (
        "A__P11_CUSTODY_OWNED_DETERMINISTIC_PRECLAIM_TEMPORAL_OWNER_CONTRACT_VERIFIED"
    )
    assert value["selected_temporal_owner_contract"] == (
        "OPTION_A__P11_CUSTODY_POLICY_OWNED_COORDINATE_SEALED_IN_EXISTING_"
        "SAPIANTA_FRESH_OPERATION_CONTEXT_V1"
    )
    assert value["temporal_coordinate_owner"] == (
        "P11_DA_AUTHORITY_CUSTODY_PROCESS_PRINCIPAL_TEMPORAL_POLICY_V1"
    )


def test_materializer_derives_specification_owned_coordinate_and_seals_it(
    tmp_path: Path,
) -> None:
    context = context_for(tmp_path)
    binding = context["preclaim_temporal_binding"]
    assert binding["coordinate_unix_ns"] == 1000
    assert binding == FM.materialize_preclaim_temporal_binding(
        repository_root=ROOT,
        generation_identity=context["generation_identity"],
        operation_identity=context["operation_identity"],
    )
    assert "preclaim_temporal_binding" in (
        context["authorization_binding_policy"]["authorization_must_bind"]
    )
    assert FM.validate_context(context, repository_root=ROOT) == context


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda value: value.pop("preclaim_temporal_binding"), "fields"),
        (
            lambda value: value["preclaim_temporal_binding"].update(
                {"coordinate_unix_ns": "1000"}
            ),
            "policy output",
        ),
        (
            lambda value: value["preclaim_temporal_binding"].update(
                {"coordinate_unix_ns": -1}
            ),
            "policy output",
        ),
        (
            lambda value: value["preclaim_temporal_binding"].update(
                {"coordinate_unix_ns": 999}
            ),
            "policy output",
        ),
        (
            lambda value: value["preclaim_temporal_binding"].update(
                {"wall_clock_coordinate_unix_ns": 1001}
            ),
            "fields",
        ),
        (
            lambda value: value["preclaim_temporal_binding"].update(
                {"producer_identity": "CALLER"}
            ),
            "policy output",
        ),
        (
            lambda value: value["preclaim_temporal_binding"].update(
                {"producer_identity": "PROVIDER"}
            ),
            "policy output",
        ),
        (
            lambda value: value["preclaim_temporal_binding"].update(
                {"operation_identity": "G77_256JM_OTHER_OPERATION_001"}
            ),
            "policy output",
        ),
    ],
)
def test_missing_malformed_conflicting_substituted_and_mismatched_fail_closed(
    tmp_path: Path, mutation, message: str
) -> None:
    context = context_for(tmp_path)
    mutation(context)
    reseal(context)
    with pytest.raises(FM.ContextError, match=message):
        FM.validate_context(context, repository_root=ROOT)


def test_unresealed_coordinate_mutation_invalidates_context_seal(tmp_path: Path) -> None:
    context = context_for(tmp_path)
    context["preclaim_temporal_binding"]["coordinate_unix_ns"] = 999
    with pytest.raises(FM.ContextError, match="context seal mismatch"):
        FM.validate_context(context, repository_root=ROOT)


def test_duplicate_temporal_coordinate_fails_unique_json_loading(tmp_path: Path) -> None:
    context = context_for(tmp_path)
    raw = FM.canonical_bytes(context)
    raw = raw.replace(b'"coordinate_unix_ns":1000', b'"coordinate_unix_ns":1000,"coordinate_unix_ns":1000', 1)
    path = tmp_path / "duplicate.json"
    path.write_bytes(raw)
    with pytest.raises(FM.ContextError, match="duplicate keys"):
        FM.load_context(path, repository_root=ROOT)


def test_commissioning_gate_and_p11_custody_reauthenticate_same_context(
    tmp_path: Path,
) -> None:
    context = context_for(tmp_path)
    store = store_for(tmp_path)
    bindings = FixedPrincipalBindings(os.getuid() + 1, os.getuid() + 2, os.getuid())
    gate = gate_for(context, store, bindings)
    consumer = P11BoundedConsumerV1(
        store=store,
        principal_bindings=bindings,
        commissioning_gate=gate,
        fresh_operation_context=context,
    )
    assert gate.operation_context_sha256 == context["context_sha256"]
    assert gate.preclaim_temporal_binding_identity == (
        preclaim_temporal_binding_identity(context["preclaim_temporal_binding"])
    )
    assert consumer.production_route_count == 0


def test_mutation_after_gate_or_human_correlation_fails_closed(tmp_path: Path) -> None:
    context = context_for(tmp_path)
    human_fixture = LAUNCHER.preauthority_serialization_fixture(context)
    store = store_for(tmp_path)
    bindings = FixedPrincipalBindings(os.getuid() + 1, os.getuid() + 2, os.getuid())
    gate = gate_for(context, store, bindings)
    context["preclaim_temporal_binding"]["coordinate_unix_ns"] = 999
    reseal(context)
    assert human_fixture["authorized_context_sha256"] != context["context_sha256"]
    with pytest.raises(
        FailClosedRuntimeError, match="temporal binding|commissioning gate"
    ):
        P11BoundedConsumerV1(
            store=store,
            principal_bindings=bindings,
            commissioning_gate=gate,
            fresh_operation_context=context,
        )


def test_context_candidate_and_preflight_correlations_cover_coordinate(
    tmp_path: Path,
) -> None:
    context = context_for(tmp_path)
    human_fixture = LAUNCHER.preauthority_serialization_fixture(context)
    assert human_fixture["authorized_context_sha256"] == context["context_sha256"]
    assert "coordinate_unix_ns" not in human_fixture
    assert "preclaim_time_unix_ns" not in human_fixture
    store = store_for(tmp_path)
    bindings = FixedPrincipalBindings(os.getuid() + 1, os.getuid() + 2, os.getuid())
    gate = gate_for(context, store, bindings)
    assert gate.gate_identity == replay_hash(gate.identity_preimage())
    changed = deepcopy(context)
    changed["candidate_manifest_sha256"] = "f" * 64
    reseal(changed)
    assert changed["context_sha256"] != gate.operation_context_sha256


def test_temporal_boundaries_and_deterministic_read_only_replay(tmp_path: Path) -> None:
    binding, _ = authenticate_preclaim_temporal_binding(context_for(tmp_path))
    decisions = []
    for coordinate in (999, 1000, 1001):
        value = dict(binding, coordinate_unix_ns=coordinate)
        decisions.append(
            preclaim_temporal_decision(
                value, valid_from_unix_ns=100, valid_until_unix_ns=1000
            )
        )
    assert decisions == ["CURRENT", "EXPIRED", "EXPIRED"]
    assert preclaim_temporal_decision(
        dict(binding, coordinate_unix_ns=99),
        valid_from_unix_ns=100,
        valid_until_unix_ns=1000,
    ) == "FUTURE"
    assert preclaim_temporal_decision(
        binding, valid_from_unix_ns=100, valid_until_unix_ns=1000
    ) == preclaim_temporal_decision(
        binding, valid_from_unix_ns=100, valid_until_unix_ns=1000
    )


def test_no_clock_or_coordinate_selection_surface_and_single_route() -> None:
    signature = inspect.signature(P11BoundedConsumerV1.claim_and_invoke_once)
    assert not ({"now", "time", "clock", "provider", "preclaim_time"} & set(signature.parameters))
    source = inspect.getsource(P11BoundedConsumerV1.claim_and_invoke_once)
    assert "time.time_ns" not in source
    assert 'temporal_binding["coordinate_unix_ns"]' in source
    launcher_source = LAUNCHER_PATH.read_text(encoding="utf-8")
    assert len(re.findall(
        r"^\s*result = subprocess\.run\(argv, check=False\)$",
        launcher_source,
        re.MULTILINE,
    )) == 1
    assert launcher_source.count("def build_operation_context(") == 1


def test_ex_is_reused_17_of_17_without_reconstruction(tmp_path: Path) -> None:
    certificate_path = ROOT / (
        ".github/governance/evidence/g77_256ex_common_substrate_certification_v1/"
        "G77_256EX_P11_SPCE_COMMON_SUBSTRATE_CERTIFICATION_V1.json"
    )
    certificate = json.loads(certificate_path.read_bytes())["certificate"]
    assert certificate["component_counts"]["CERTIFIED"] == 17
    assert certificate["reusable_p11_spce_execution_substrate"].startswith(
        "CONSTITUTIONALLY_CERTIFIED"
    )
    archive = subprocess.check_output(
        ["git", "archive", "651168072f39d6cd0323efc23ed830445a05062b"],
        cwd=ROOT,
    )
    with tarfile.open(fileobj=io.BytesIO(archive)) as bundle:
        bundle.extractall(tmp_path, filter="data")
    validator_path = tmp_path / (
        ".github/governance/evidence/g77_256ex_common_substrate_certification_v1/"
        "validator/G77_256EX_COMMON_SUBSTRATE_CERTIFICATION_VALIDATOR_V1.py"
    )
    validator = load_module(validator_path, "g77_256jm_ex_entry_validator")
    result = validator.validate(tmp_path / certificate_path.relative_to(ROOT))
    assert result["regression_total"] == result["regression_pass"] == 12
    assert result["regression_fail"] == 0

    ew_manifest = json.loads((ROOT / (
        ".github/governance/evidence/g77_256ew_reusable_p11_spce_substrate_v1/"
        "G77_256EW_P11_SPCE_REUSABLE_SUBSTRATE_MANIFEST_V1.json"
    )).read_bytes())["manifest"]
    changed_paths = set(subprocess.check_output(
        ["git", "diff", "--name-only"], cwd=ROOT, text=True
    ).splitlines())
    changed_bindings = {
        item["path"]: item["classification"]
        for item in ew_manifest["component_bindings"]
        if item["path"] in changed_paths
    }
    assert changed_bindings == {
        "tests/p11_da_operational_consumer_v1.py": "REQUIRES_HARDENING"
    }


def test_preclaim_authentication_and_decision_precede_ledger_append() -> None:
    source = inspect.getsource(P11BoundedConsumerV1.claim_and_invoke_once)
    authentication = source.index("authenticate_preclaim_temporal_binding")
    decision = source.index("preclaim_temporal_decision")
    authority_validation = source.index("self._validate_authority_sources")
    preclaim_append = source.index('"P11_DA_OPERATIONAL_PRECLAIM"')
    assert authentication < decision < authority_validation < preclaim_append
    authority_source = inspect.getsource(P11BoundedConsumerV1._validate_authority_sources)
    assert "preflight_binding_identity" in authority_source


def test_repository_only_suite_contains_no_operational_calls() -> None:
    source = Path(__file__).read_text(encoding="utf-8")
    forbidden = tuple("." + name + "(" for name in (
        "submit_human_act",
        "claim_and_invoke_once",
        "main",
    ))
    assert all(token not in source for token in forbidden)


def test_g48_exactly_six_h1_and_required_compact_sections() -> None:
    headings = re.findall(r"^# (.+)$", REPORT.read_text(encoding="utf-8"), re.MULTILINE)
    assert headings == [
        "1. Implementation Summary",
        "2. Code Evidence",
        "3. Constitutional Self-Assessment",
        "4. Validation Matrix",
        "5. Repository Mutation Summary",
        "6. Certification Verdict",
    ]
    text = REPORT.read_text(encoding="utf-8")
    assert "## Reuse Impact Assessment" in text
    assert "## Constitutional Continuity & Worker Independence Metrics — CCWIM" in text
    assert "INTRA_GENERATION_CROSS_WORKER_CONTINUATION" in text
    assert "UNCOMMITTED_DELTA_RECOVERY" in text
    assert "Unrelated pre-existing changes:" in text
    assert text.split("# 6. Certification Verdict", 1)[1].strip() == (
        "A__OPTION_A_DETERMINISTIC_PRECLAIM_TEMPORAL_BINDING_"
        "IMPLEMENTED_AND_REPOSITORY_VERIFIED"
    )
    for question in (
        "Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?",
        "Katere nove zmogljivosti (če sploh) nastanejo?",
        "Ali katera obstoječa zmogljivost postane nedosegljiva?",
        "Ali implementacija ustvarja vzporedni tok?",
        "Ali zmanjšuje ali povečuje število produkcijskih poti?",
    ):
        assert question in text


def test_reduction_is_unique_key_inner_sealed_and_complete() -> None:
    def unique(pairs):
        value = {}
        for key, item in pairs:
            assert key not in value
            value[key] = item
        return value

    envelope = json.loads(REDUCTION.read_bytes(), object_pairs_hook=unique)
    reduction = envelope["reduction"]
    canonical = (
        json.dumps(reduction, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode()
    assert envelope["reduction_sha256"] == hashlib.sha256(canonical).hexdigest()
    assert reduction["terminal"] == (
        "A__OPTION_A_DETERMINISTIC_PRECLAIM_TEMPORAL_BINDING_"
        "IMPLEMENTED_AND_REPOSITORY_VERIFIED"
    )
    assert reduction["ccwim"]["intra_generation_cross_worker_continuation"].startswith(
        "VERIFIED"
    )
    assert reduction["ccwim"]["uncommitted_delta_recovery"].startswith("VERIFIED")
    assert reduction["reuse"]["ex_reused"] == "VERIFIED__17_OF_17"
    assert reduction["reuse"]["ex_reconstructed"] == "VERIFIED__0"
