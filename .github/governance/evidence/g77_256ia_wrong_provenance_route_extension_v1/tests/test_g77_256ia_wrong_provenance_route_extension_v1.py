#!/usr/bin/env python3
"""Repository-only regression firewall for the IA existing-route extension."""

from __future__ import annotations

import ast
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
FM_ROOT = ROOT / ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1"
OWNER_PATH = FM_ROOT / "launcher/sapianta_fresh_operation_context_v1.py"
LAUNCHER_PATH = FM_ROOT / "launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
GN_PATH = ROOT / (
    ".github/governance/evidence/g77_256gn_human_authorization_presentation_binding_v1/"
    "presentation/G77_256GN_SEALED_REQUEST_HUMAN_AUTHORIZATION_PRESENTATION_V1.py"
)
IA_ROOT = ROOT / ".github/governance/evidence/g77_256ia_wrong_provenance_route_extension_v1"
ADAPTER_PATH = IA_ROOT / "adapter/G77_256IA_WRONG_PROVENANCE_VECTOR_ADAPTER_V1.py"
MATERIALIZER_PATH = IA_ROOT / (
    "orchestration/G77_256IA_WRONG_PROVENANCE_PREAUTHORIZATION_MATERIALIZER_V1.py"
)
TERMINAL_PATH = IA_ROOT / "G77_256IA_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
REPORT_PATH = IA_ROOT / "G77_256IA_G48_IMPLEMENTATION_REPORT_V1.md"
HZ_ROOT = ROOT / ".github/governance/evidence/g77_256hz_wrong_provenance_formalization_v1"
HZ_SPEC = HZ_ROOT / "G77_256HZ_WRONG_PROVENANCE_FORMAL_SPECIFICATION_V1.json"
HZ_PRODUCER = HZ_ROOT / "producer/G77_256HZ_WRONG_PROVENANCE_VECTOR_PRODUCER_V1.py"
HZ_REDUCER = HZ_ROOT / (
    "reducer/G77_256HZ_WRONG_PROVENANCE_REPOSITORY_CAPABILITY_REDUCER_V1.py"
)
HP_REQUEST = ROOT / (
    ".github/governance/evidence/g77_256hp_wrong_input_operational_v1/"
    "G77_256HP_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
)
META_DATA = FM_ROOT / "raw/G77_256FM_CLOUD_INIT_META_DATA_V1.yaml"
NETWORK_CONFIG = FM_ROOT / "raw/G77_256FM_CLOUD_INIT_NETWORK_CONFIG_V1.yaml"
HZ_HEAD = "9db84476f263b9676d2ff7407152388afad04618"
HZ_TREE = "8753786eede58f453a40af71825c19bc3efaff0a"
HT_HEAD = "af44f0afd02be7e21a24e962309e28f6edd17ae0"
HT_TREE = "fc949a2bbaa0a507edbc25811563dc5e13d18315"
GENERATION = (
    "G77_256IATEST_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_PROVENANCE_"
    "OPERATIONAL_COMMISSIONING_V1"
)


def load_module(path: Path, identity: str):
    specification = importlib.util.spec_from_file_location(identity, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


OWNER = load_module(OWNER_PATH, "g77_256ia_test_context_owner")
LAUNCHER = load_module(LAUNCHER_PATH, "g77_256ia_test_launcher")
GN = load_module(GN_PATH, "g77_256ia_test_gn")
ADAPTER = load_module(ADAPTER_PATH, "g77_256ia_test_adapter")
MATERIALIZER = load_module(MATERIALIZER_PATH, "g77_256ia_test_materializer")


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_unique_json(raw: bytes) -> dict:
    def unique(pairs):
        value = {}
        for key, item in pairs:
            assert key not in value
            value[key] = item
        return value

    return json.loads(raw, object_pairs_hook=unique)


def build_context(tmp_path: Path, vector: str = "WRONG_PROVENANCE") -> dict:
    generation = (
        f"G77_256IATEST_ONE_FRESH_HUMAN_AUTHORIZED_{vector}_"
        "OPERATIONAL_COMMISSIONING_V1"
    )
    return LAUNCHER.build_operation_context(
        repository_root=ROOT,
        repository_head=HZ_HEAD,
        repository_tree=HZ_TREE,
        generation_identity=generation,
        operation_identity=f"G77_256IATEST_{vector}_STATIC_FIXTURE_001",
        identity_namespace_prefix="G77_256IATEST",
        operation_evidence_root=tmp_path / vector.lower() / "operation_state",
        transient_root=tmp_path / vector.lower() / "transient",
        candidate_source_path=HZ_SPEC.relative_to(ROOT),
    )


def project_adapter(context: dict) -> None:
    binding = context["guest_adapter_binding"]
    projection_root = Path(binding["projection_root"])
    projection_root.mkdir(mode=0o700, parents=True)
    source = (ROOT / binding["source_path"]).read_bytes()
    Path(binding["projected_path"]).write_bytes(source)
    Path(binding["bootstrap_projected_path"]).write_bytes(source)


def reseal_request(envelope: dict) -> None:
    envelope["request_sha256"] = hashlib.sha256(
        GN._canonical_bytes(envelope["request"])
    ).hexdigest()


@pytest.mark.parametrize(
    "vector",
    ("WRONG_ATTEMPT", "WRONG_INPUT", "WRONG_CONTRACT", "WRONG_PROVENANCE"),
)
def test_closed_vector_set_accepts_exact_four_canonical_vectors(vector: str) -> None:
    generation = (
        f"G77_256IATEST_ONE_FRESH_HUMAN_AUTHORIZED_{vector}_"
        "OPERATIONAL_COMMISSIONING_V1"
    )
    assert OWNER.operation_vector(generation) == vector
    assert vector in OWNER.SUPPORTED_OPERATION_VECTORS
    assert vector in GN.SUPPORTED_VECTORS


@pytest.mark.parametrize(
    "generation",
    (
        "G77_256IATEST_ONE_FRESH_HUMAN_AUTHORIZED_UNKNOWN_OPERATIONAL_COMMISSIONING_V1",
        "G77_256IATEST_WRONG_PROVENANCE",
        "G77_256IATEST_ONE_FRESH_HUMAN_AUTHORIZED_wrong_provenance_OPERATIONAL_COMMISSIONING_V1",
        "G77_256IATEST_ONE_FRESH_HUMAN_AUTHORIZED_WRONG-PROVENANCE_OPERATIONAL_COMMISSIONING_V1",
        "",
    ),
)
def test_unknown_malformed_empty_and_alias_vectors_fail_closed(generation: str) -> None:
    with pytest.raises(OWNER.ContextError, match="no exact supported operation vector"):
        OWNER.operation_vector(generation)


@pytest.mark.parametrize(
    ("vector", "source_suffix", "attempt_field", "bootstrap_marker"),
    (
        (
            "WRONG_ATTEMPT",
            "G77_256FM_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py",
            "wrong_attempt_operational_attempt_limit",
            "G77_256HK_CLOUD_INIT_USER_DATA_V1.yaml",
        ),
        (
            "WRONG_INPUT",
            "G77_256HA_WRONG_INPUT_VECTOR_ADAPTER_V1.py",
            "wrong_input_operational_attempt_limit",
            "G77_256HN_CLOUD_INIT_USER_DATA_V1.yaml",
        ),
        (
            "WRONG_CONTRACT",
            "G77_256HT_WRONG_CONTRACT_VECTOR_ADAPTER_V1.py",
            "wrong_contract_operational_attempt_limit",
            "G77_256HT_CLOUD_INIT_USER_DATA_TEMPLATE_V1.yaml",
        ),
        (
            "WRONG_PROVENANCE",
            "G77_256IA_WRONG_PROVENANCE_VECTOR_ADAPTER_V1.py",
            "wrong_provenance_operational_attempt_limit",
            "G77_256IA_CLOUD_INIT_USER_DATA_TEMPLATE_V1.yaml",
        ),
    ),
)
def test_existing_route_selectors_are_deterministic_and_non_regressing(
    tmp_path: Path,
    vector: str,
    source_suffix: str,
    attempt_field: str,
    bootstrap_marker: str,
) -> None:
    context = build_context(tmp_path, vector)
    assert context["guest_adapter_binding"]["source_path"].endswith(source_suffix)
    bootstrap = LAUNCHER.current_bootstrap_asset_bindings(vector)
    assert bootstrap["cloud_init_path"].endswith(bootstrap_marker)
    fields = LAUNCHER.authorization_fields({"authorized_vector": vector})
    assert attempt_field in fields
    assert LAUNCHER.operation_attempt_limit_field(vector) == attempt_field
    assert sum(field.endswith("operational_attempt_limit") for field in fields) == 1


@pytest.mark.parametrize("vector", ("UNKNOWN", "wrong_provenance", "", None))
def test_all_string_dispatch_boundaries_reject_noncanonical_vectors(vector) -> None:
    with pytest.raises(RuntimeError, match="unsupported"):
        LAUNCHER.current_bootstrap_asset_bindings(vector)
    with pytest.raises(RuntimeError, match="unsupported"):
        LAUNCHER.authorization_fields({"authorized_vector": vector})
    with pytest.raises(RuntimeError, match="unsupported"):
        LAUNCHER.operation_attempt_limit_field(vector)


def test_wrong_provenance_context_adapter_bootstrap_and_guest_binding(
    tmp_path: Path,
) -> None:
    context = build_context(tmp_path)
    binding = context["guest_adapter_binding"]
    assert OWNER.operation_vector(context["generation_identity"]) == "WRONG_PROVENANCE"
    assert binding["source_path"] == ADAPTER_PATH.relative_to(ROOT).as_posix()
    assert binding["source_sha256"] == sha256_path(ADAPTER_PATH)
    assert binding["adapter_identity"].endswith(
        "_WRONG_PROVENANCE_VECTOR_ADAPTER_V1.py"
    )
    project_adapter(context)
    proof = LAUNCHER.prove_guest_adapter_binding(ROOT, context)
    assert proof["result"] == "PREAUTHORITY_GUEST_ADAPTER_BINDING_PASS"
    assert proof["source_sha256"] == sha256_path(ADAPTER_PATH)


def test_wrong_provenance_seed_is_exact_static_template_projection() -> None:
    bootstrap = LAUNCHER.current_bootstrap_asset_bindings("WRONG_PROVENANCE")
    seed = Path(bootstrap["seed_path"])
    assert subprocess.check_output(
        ["isoinfo", "-i", str(seed), "-R", "-x", "/user-data"],
        stderr=subprocess.DEVNULL,
    ) == (ROOT / bootstrap["cloud_init_path"]).read_bytes()
    assert sha256_path(seed) == bootstrap["seed_sha256"]
    assert subprocess.check_output(
        ["isoinfo", "-i", str(seed), "-R", "-x", "/meta-data"],
        stderr=subprocess.DEVNULL,
    ) == META_DATA.read_bytes()
    assert subprocess.check_output(
        ["isoinfo", "-i", str(seed), "-R", "-x", "/network-config"],
        stderr=subprocess.DEVNULL,
    ) == NETWORK_CONFIG.read_bytes()


def test_adapter_reuses_exact_hz_producer_and_reducer_semantics() -> None:
    assert sha256_path(HZ_PRODUCER) == ADAPTER.HZ_PRODUCER_SHA256
    assert sha256_path(HZ_REDUCER) == ADAPTER.HZ_REDUCER_SHA256
    projection = ADAPTER.construct_wrong_provenance_payload(
        repository_root=ROOT,
        wrong_provenance_identity="G77_256IA_DISTINCT_WRONG_PROVENANCE_001",
        request_identity="G77_256IA_REPOSITORY_ONLY_REQUEST_FIXTURE_001",
    )
    binding = projection["semantic_binding"]
    assert binding["independent_mutated_coordinate"] == "provenance_identity"
    assert binding["independent_mutation_count"] == 1
    assert binding["dependent_recomputed_coordinate"] == "record_identity"
    assert binding["dependent_recomputation_count"] == 1
    assert binding["differing_input_fields"] == [
        "provenance_identity", "record_identity"
    ]
    assert binding["provenance_specific_comparison_reached"] is False
    assert projection["authoritative_provenance_resolution"] == (
        "VERIFIED__UNIQUE_EXISTING_PROTECTED_OWNER"
    )
    assert projection["request_is_authority"] is False
    assert projection["adapter_invoked_p11"] is False
    assert projection["operational_execution_count"] == 0


def test_fc_specialization_changes_only_provenance_semantic_coordinate() -> None:
    source = ADAPTER.specialize_fc_runtime_source(
        repository_root=ROOT, identity_namespace_prefix="G77_256IATEST"
    )
    assert source.count(
        'wrong_value["provenance_identity"] = WRONG_PROVENANCE_ID'
    ) == 1
    assert 'wrong_value["input_identity"] = WRONG_PROVENANCE_ID' not in source
    assert 'wrong_value["attempt_identity"] = WRONG_PROVENANCE_ID' not in source
    assert 'wrong_value["contract_identity"] = WRONG_PROVENANCE_ID' not in source
    assert '"supplied_attempt_identity": WRONG_PROVENANCE_ID' not in source
    assert source.count(
        '"supplied_provenance_identity": WRONG_PROVENANCE_ID'
    ) == 2


def test_gn_supports_truthful_provenance_and_rejects_cross_vector_substitution(
    tmp_path: Path,
) -> None:
    base = json.loads(HP_REQUEST.read_bytes())
    valid = deepcopy(base)
    valid["request"]["authorized_vector_requested"] = "WRONG_PROVENANCE"
    valid["request"]["generation_identity"] = GENERATION
    reseal_request(valid)
    valid_path = tmp_path / "valid.json"
    valid_path.write_bytes(GN._canonical_bytes(valid))
    presentation = GN.render_human_authorization_presentation(valid_path)
    assert b'AUTHORIZED_VECTOR_REQUESTED "WRONG_PROVENANCE"' in presentation
    assert GN.validate_human_authorization_presentation(
        valid_path, presentation
    )["human_constitutional_authorization_count"] == 0

    for vector, generation in (
        ("WRONG_INPUT", GENERATION),
        (
            "WRONG_PROVENANCE",
            "G77_256IATEST_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_INPUT_"
            "OPERATIONAL_COMMISSIONING_V1",
        ),
    ):
        substituted = deepcopy(base)
        substituted["request"]["authorized_vector_requested"] = vector
        substituted["request"]["generation_identity"] = generation
        reseal_request(substituted)
        path = tmp_path / f"{vector}.json"
        path.write_bytes(GN._canonical_bytes(substituted))
        with pytest.raises(
            GN.PresentationBindingError,
            match="SEALED_REQUEST_VECTOR_GENERATION_BINDING_INVALID",
        ):
            GN.render_human_authorization_presentation(path)


def test_thin_materializer_binds_one_non_authority_future_chain(
    tmp_path: Path,
) -> None:
    context = build_context(tmp_path)
    candidate_bytes = HZ_SPEC.read_bytes()
    candidate_sha = hashlib.sha256(candidate_bytes).hexdigest()
    request = {
        "authorized_vector_requested": "WRONG_PROVENANCE",
        "generation_identity": GENERATION,
        "candidate_sha256": candidate_sha,
        "context_sha256": context["context_sha256"],
        "canonical_argv_sha256": context["canonical_argv_sha256"],
        "request_is_authority": False,
    }
    presentation = {
        "AUTHORIZED_VECTOR_REQUESTED": "WRONG_PROVENANCE",
        "GENERATION_ID": GENERATION,
        "CANDIDATE_SHA256": candidate_sha,
        "CONTEXT_SHA256": context["context_sha256"],
        "CANONICAL_ARGV_SHA256": context["canonical_argv_sha256"],
    }
    semantics = {
        "selected_vector": "P11-E05/NEGATIVE_AUTHORITY/WRONG_PROVENANCE",
        "target_mutation": "provenance_identity",
        "dependent_recomputation": "record_identity",
        "semantic_mutation_count": 1,
        "unrelated_mutation_count": 0,
        "authoritative_provenance_resolution": (
            "VERIFIED__UNIQUE_EXISTING_PROTECTED_OWNER"
        ),
        "provenance_specific_comparison_reached": False,
    }
    result = MATERIALIZER.validate_future_materialization_chain(
        repository_root=ROOT,
        candidate_bytes=candidate_bytes,
        candidate_semantics=semantics,
        context=context,
        request_binding=request,
        presentation_binding=presentation,
    )
    assert result["candidate_context_argv_presentation_chain"] == "VERIFIED"
    assert result["request_created"] is False
    assert result["presentation_created"] is False
    assert result["post_commit_rebind_required"] is True
    assert result["preoperational_readiness"] == "NOT_PROVEN"

    wrong = deepcopy(presentation)
    wrong["AUTHORIZED_VECTOR_REQUESTED"] = "WRONG_CONTRACT"
    with pytest.raises(
        MATERIALIZER.WrongProvenanceMaterializationError,
        match="PRESENTATION_REQUEST_CHAIN_INVALID",
    ):
        MATERIALIZER.validate_future_materialization_chain(
            repository_root=ROOT,
            candidate_bytes=candidate_bytes,
            candidate_semantics=semantics,
            context=context,
            request_binding=request,
            presentation_binding=wrong,
        )


def test_single_production_route_and_static_checkout_boundary() -> None:
    assert list(IA_ROOT.rglob("*LAUNCHER*.py")) == []
    tree = ast.parse(LAUNCHER_PATH.read_text(encoding="utf-8"))
    main_functions = [
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == "main"
    ]
    assert len(main_functions) == 1
    assert LAUNCHER.CHECKOUT_HEAD == HT_HEAD
    assert LAUNCHER.CHECKOUT_TREE == HT_TREE
    assert LAUNCHER.CHECKOUT_HEAD != HZ_HEAD
    assert "subprocess" not in MATERIALIZER_PATH.read_text(encoding="utf-8")


def test_owner_hash_is_current_and_operational_counters_are_absent() -> None:
    assert sha256_path(OWNER_PATH) == LAUNCHER.FRESH_OPERATION_CONTEXT_OWNER_SHA256
    source = MATERIALIZER_PATH.read_text(encoding="utf-8")
    assert "def main(" not in source
    assert "qemu-system" not in source
    assert "CLAIM_AND_INVOKE_ONCE" not in source


def test_terminal_reduction_is_canonical_sealed_and_g48_exact() -> None:
    raw = TERMINAL_PATH.read_bytes()
    envelope = load_unique_json(raw)
    assert raw == (
        json.dumps(
            envelope, sort_keys=True, separators=(",", ":"), allow_nan=False
        ) + "\n"
    ).encode("utf-8")
    inner = (
        json.dumps(
            envelope["reduction"],
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ) + "\n"
    ).encode("utf-8")
    assert hashlib.sha256(inner).hexdigest() == envelope["reduction_sha256"]
    assert set(envelope["reduction"]["operational_counters"].values()) == {0}
    assert envelope["reduction"]["e05"] == {
        "after": "9/18",
        "before": "9/18",
        "credit": 0,
        "remaining": 9,
        "required": 18,
        "satisfied": 9,
    }
    allowed_statuses = {
        "VERIFIED", "ESTIMATED", "NOT_MEASURED", "NOT_PROVEN", "NOT_APPLICABLE"
    }
    for section in ("ccwim", "required_metrics"):
        for metric in envelope["reduction"][section].values():
            assert metric["status"] in allowed_statuses
    headings = [
        line
        for line in REPORT_PATH.read_text(encoding="utf-8").splitlines()
        if line.startswith("# ")
    ]
    assert headings == [
        "# 1. Implementation Summary",
        "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment",
        "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary",
        "# 6. Certification Verdict",
    ]
