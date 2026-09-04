#!/usr/bin/env python3
"""Repository-only regression firewall for the HT existing-route extension."""

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
HT_ROOT = ROOT / ".github/governance/evidence/g77_256ht_wrong_contract_route_extension_v1"
ADAPTER_PATH = HT_ROOT / "adapter/G77_256HT_WRONG_CONTRACT_VECTOR_ADAPTER_V1.py"
MATERIALIZER_PATH = HT_ROOT / (
    "orchestration/G77_256HT_WRONG_CONTRACT_PREAUTHORIZATION_MATERIALIZER_V1.py"
)
HP_REQUEST = ROOT / (
    ".github/governance/evidence/g77_256hp_wrong_input_operational_v1/"
    "G77_256HP_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
)
HR_SPEC = ROOT / (
    ".github/governance/evidence/g77_256hr_wrong_contract_formalization_v1/"
    "G77_256HR_WRONG_CONTRACT_FORMAL_SPECIFICATION_V1.json"
)
META_DATA = FM_ROOT / "raw/G77_256FM_CLOUD_INIT_META_DATA_V1.yaml"
NETWORK_CONFIG = FM_ROOT / "raw/G77_256FM_CLOUD_INIT_NETWORK_CONFIG_V1.yaml"
HS_HEAD = "247d6b089b91c20364b5d0ce43017c07bae803b7"
HS_TREE = "100e28651dbc5d24e533bb6f73b0a5c72a3fbe7c"
GENERATION = (
    "G77_256HTTEST_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_CONTRACT_"
    "OPERATIONAL_COMMISSIONING_V1"
)


def load_module(path: Path, identity: str):
    specification = importlib.util.spec_from_file_location(identity, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


OWNER = load_module(OWNER_PATH, "g77_256ht_test_context_owner")
LAUNCHER = load_module(LAUNCHER_PATH, "g77_256ht_test_launcher")
GN = load_module(GN_PATH, "g77_256ht_test_gn")
ADAPTER = load_module(ADAPTER_PATH, "g77_256ht_test_adapter")
MATERIALIZER = load_module(MATERIALIZER_PATH, "g77_256ht_test_materializer")


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_context(tmp_path: Path) -> dict:
    return LAUNCHER.build_operation_context(
        repository_root=ROOT,
        repository_head=HS_HEAD,
        repository_tree=HS_TREE,
        generation_identity=GENERATION,
        operation_identity="G77_256HTTEST_WRONG_CONTRACT_STATIC_FIXTURE_001",
        identity_namespace_prefix="G77_256HTTEST",
        operation_evidence_root=tmp_path / "operation_state",
        transient_root=tmp_path / "transient",
        candidate_source_path=HR_SPEC.relative_to(ROOT),
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


def write_request(tmp_path: Path, envelope: dict, name: str) -> Path:
    path = tmp_path / name
    path.write_bytes(GN._canonical_bytes(envelope))
    return path


@pytest.mark.parametrize(
    ("vector", "suffix"),
    (
        ("WRONG_ATTEMPT", "WRONG_ATTEMPT"),
        ("WRONG_INPUT", "WRONG_INPUT"),
        ("WRONG_CONTRACT", "WRONG_CONTRACT"),
    ),
)
def test_existing_closed_vector_set_accepts_exact_three_vectors(
    vector: str, suffix: str
) -> None:
    generation = (
        f"G77_256HTTEST_ONE_FRESH_HUMAN_AUTHORIZED_{suffix}_"
        "OPERATIONAL_COMMISSIONING_V1"
    )
    assert OWNER.operation_vector(generation) == vector


@pytest.mark.parametrize(
    ("vector", "expected_source_suffix", "attempt_field"),
    (
        (
            "WRONG_ATTEMPT",
            "G77_256FM_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py",
            "wrong_attempt_operational_attempt_limit",
        ),
        (
            "WRONG_INPUT",
            "G77_256HA_WRONG_INPUT_VECTOR_ADAPTER_V1.py",
            "wrong_input_operational_attempt_limit",
        ),
        (
            "WRONG_CONTRACT",
            "G77_256HT_WRONG_CONTRACT_VECTOR_ADAPTER_V1.py",
            "wrong_contract_operational_attempt_limit",
        ),
    ),
)
def test_fm_context_bootstrap_and_authorization_behavior_for_all_vectors(
    tmp_path: Path,
    vector: str,
    expected_source_suffix: str,
    attempt_field: str,
) -> None:
    generation = (
        f"G77_256HTREG_{'ONE_FRESH_HUMAN_AUTHORIZED_' + vector}_"
        "OPERATIONAL_COMMISSIONING_V1"
    )
    context = LAUNCHER.build_operation_context(
        repository_root=ROOT,
        repository_head=HS_HEAD,
        repository_tree=HS_TREE,
        generation_identity=generation,
        operation_identity=f"G77_256HTREG_{vector}_STATIC_FIXTURE_001",
        identity_namespace_prefix="G77_256HTREG",
        operation_evidence_root=tmp_path / vector.lower() / "operation_state",
        transient_root=tmp_path / vector.lower() / "transient",
        candidate_source_path=HR_SPEC.relative_to(ROOT),
    )
    assert context["guest_adapter_binding"]["source_path"].endswith(
        expected_source_suffix
    )
    assert LAUNCHER.current_bootstrap_asset_bindings(vector)
    fields = LAUNCHER.authorization_fields({"authorized_vector": vector})
    assert attempt_field in fields
    assert sum(field.endswith("operational_attempt_limit") for field in fields) == 1


@pytest.mark.parametrize(
    "generation",
    (
        "G77_256HTTEST_ONE_FRESH_HUMAN_AUTHORIZED_UNKNOWN_OPERATIONAL_COMMISSIONING_V1",
        "G77_256HTTEST_WRONG_CONTRACT",
        "",
    ),
)
def test_unknown_and_malformed_vectors_remain_fail_closed(generation: str) -> None:
    with pytest.raises(OWNER.ContextError, match="no exact supported operation vector"):
        OWNER.operation_vector(generation)


def test_wrong_contract_context_adapter_bootstrap_and_authorization_selectors(
    tmp_path: Path,
) -> None:
    context = build_context(tmp_path)
    binding = context["guest_adapter_binding"]
    assert OWNER.operation_vector(context["generation_identity"]) == "WRONG_CONTRACT"
    assert binding["source_path"] == ADAPTER_PATH.relative_to(ROOT).as_posix()
    assert binding["source_sha256"] == sha256_path(ADAPTER_PATH)
    assert binding["adapter_identity"].endswith(
        "_WRONG_CONTRACT_VECTOR_ADAPTER_V1.py"
    )
    bootstrap = LAUNCHER.current_bootstrap_asset_bindings("WRONG_CONTRACT")
    assert bootstrap["cloud_init_path"].endswith(
        "G77_256HT_CLOUD_INIT_USER_DATA_TEMPLATE_V1.yaml"
    )
    assert bootstrap["seed_path"].endswith(
        "SAPIANTA_WRONG_CONTRACT_NOCLOUD_SEED_TEMPLATE_V1.img"
    )
    fields = LAUNCHER.authorization_fields({"authorized_vector": "WRONG_CONTRACT"})
    assert "wrong_contract_operational_attempt_limit" in fields
    assert "wrong_input_operational_attempt_limit" not in fields
    assert "wrong_attempt_operational_attempt_limit" not in fields
    project_adapter(context)
    proof = LAUNCHER.prove_guest_adapter_binding(ROOT, context)
    assert proof["result"] == "PREAUTHORITY_GUEST_ADAPTER_BINDING_PASS"
    assert proof["source_sha256"] == sha256_path(ADAPTER_PATH)


def test_wrong_contract_seed_is_exact_template_projection() -> None:
    bootstrap = LAUNCHER.current_bootstrap_asset_bindings("WRONG_CONTRACT")
    seed = Path(bootstrap["seed_path"])
    projected = subprocess.check_output(
        ["isoinfo", "-i", str(seed), "-R", "-x", "/user-data"],
        stderr=subprocess.DEVNULL,
    )
    assert projected == (ROOT / bootstrap["cloud_init_path"]).read_bytes()
    assert sha256_path(seed) == bootstrap["seed_sha256"]
    assert subprocess.check_output(
        ["isoinfo", "-i", str(seed), "-R", "-x", "/meta-data"],
        stderr=subprocess.DEVNULL,
    ) == META_DATA.read_bytes()
    assert subprocess.check_output(
        ["isoinfo", "-i", str(seed), "-R", "-x", "/network-config"],
        stderr=subprocess.DEVNULL,
    ) == NETWORK_CONFIG.read_bytes()


def test_wrong_contract_adapter_implements_exact_hr_semantics() -> None:
    projection = ADAPTER.construct_wrong_contract_payload(
        repository_root=ROOT,
        wrong_contract_identity="G77_256HT_DISTINCT_WRONG_CONTRACT_001",
        request_identity="G77_256HT_REPOSITORY_ONLY_REQUEST_FIXTURE_001",
    )
    binding = projection["semantic_binding"]
    assert binding["target_mutated_coordinate"] == "contract_identity"
    assert binding["dependent_recomputation_fields"] == ["record_identity"]
    assert binding["semantic_mutation_count"] == 1
    assert binding["differing_input_fields"] == [
        "contract_identity", "record_identity"
    ]
    assert binding["contract_specific_comparison_reached"] is False
    assert projection["request_is_authority"] is False
    assert projection["adapter_invoked_p11"] is False
    source = ADAPTER.specialize_fc_runtime_source(
        repository_root=ROOT, identity_namespace_prefix="G77_256HTTEST"
    )
    assert source.count('wrong_value["contract_identity"] = WRONG_CONTRACT_ID') == 1
    assert 'wrong_value["input_identity"] = WRONG_CONTRACT_ID' not in source
    assert 'wrong_value["attempt_identity"] = WRONG_CONTRACT_ID' not in source
    assert '"supplied_attempt_identity": WRONG_CONTRACT_ID' not in source
    assert source.count('"supplied_contract_identity": WRONG_CONTRACT_ID') == 2


def test_gn_supports_truthful_wrong_contract_and_rejects_cross_vector_substitution(
    tmp_path: Path,
) -> None:
    base = json.loads(HP_REQUEST.read_bytes())
    valid = deepcopy(base)
    valid["request"]["authorized_vector_requested"] = "WRONG_CONTRACT"
    valid["request"]["generation_identity"] = GENERATION
    reseal_request(valid)
    valid_path = write_request(tmp_path, valid, "valid.json")
    presentation = GN.render_human_authorization_presentation(valid_path)
    assert b'AUTHORIZED_VECTOR_REQUESTED "WRONG_CONTRACT"' in presentation
    assert GN.validate_human_authorization_presentation(
        valid_path, presentation
    )["human_constitutional_authorization_count"] == 0

    for vector, generation in (
        ("WRONG_INPUT", GENERATION),
        (
            "WRONG_CONTRACT",
            "G77_256HTTEST_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_INPUT_"
            "OPERATIONAL_COMMISSIONING_V1",
        ),
    ):
        substituted = deepcopy(base)
        substituted["request"]["authorized_vector_requested"] = vector
        substituted["request"]["generation_identity"] = generation
        reseal_request(substituted)
        path = write_request(tmp_path, substituted, f"{vector}.json")
        with pytest.raises(
            GN.PresentationBindingError,
            match="SEALED_REQUEST_VECTOR_GENERATION_BINDING_INVALID",
        ):
            GN.render_human_authorization_presentation(path)


def test_thin_materializer_binds_one_coherent_non_authority_chain(
    tmp_path: Path,
) -> None:
    context = build_context(tmp_path)
    candidate_bytes = HR_SPEC.read_bytes()
    candidate_sha = hashlib.sha256(candidate_bytes).hexdigest()
    request = {
        "authorized_vector_requested": "WRONG_CONTRACT",
        "generation_identity": GENERATION,
        "candidate_sha256": candidate_sha,
        "context_sha256": context["context_sha256"],
        "canonical_argv_sha256": context["canonical_argv_sha256"],
        "request_is_authority": False,
    }
    presentation = {
        "AUTHORIZED_VECTOR_REQUESTED": "WRONG_CONTRACT",
        "GENERATION_ID": GENERATION,
        "CANDIDATE_SHA256": candidate_sha,
        "CONTEXT_SHA256": context["context_sha256"],
        "CANONICAL_ARGV_SHA256": context["canonical_argv_sha256"],
    }
    result = MATERIALIZER.validate_future_materialization_chain(
        repository_root=ROOT,
        candidate_bytes=candidate_bytes,
        candidate_semantics={
            "selected_vector": "P11-E05/NEGATIVE_AUTHORITY/WRONG_CONTRACT",
            "target_mutation": "contract_identity",
            "dependent_recomputation": "record_identity",
            "semantic_mutation_count": 1,
            "unrelated_mutation_count": 0,
        },
        context=context,
        request_binding=request,
        presentation_binding=presentation,
    )
    assert result["candidate_context_argv_presentation_chain"] == "VERIFIED"
    assert result["request_created"] is False
    assert result["post_commit_rebind_required"] is True
    assert result["preoperational_readiness"] == "NOT_PROVEN"

    wrong = deepcopy(presentation)
    wrong["AUTHORIZED_VECTOR_REQUESTED"] = "WRONG_INPUT"
    with pytest.raises(
        MATERIALIZER.WrongContractMaterializationError,
        match="PRESENTATION_REQUEST_CHAIN_INVALID",
    ):
        MATERIALIZER.validate_future_materialization_chain(
            repository_root=ROOT,
            candidate_bytes=candidate_bytes,
            candidate_semantics={
                "selected_vector": "P11-E05/NEGATIVE_AUTHORITY/WRONG_CONTRACT",
                "target_mutation": "contract_identity",
                "dependent_recomputation": "record_identity",
                "semantic_mutation_count": 1,
                "unrelated_mutation_count": 0,
            },
            context=context,
            request_binding=request,
            presentation_binding=wrong,
        )


def test_single_production_route_and_no_new_operational_owner() -> None:
    launchers = list(HT_ROOT.rglob("*LAUNCHER*.py"))
    assert launchers == []
    tree = ast.parse(LAUNCHER_PATH.read_text(encoding="utf-8"))
    main_functions = [
        node for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == "main"
    ]
    assert len(main_functions) == 1
    assert "subprocess" not in MATERIALIZER_PATH.read_text(encoding="utf-8")
