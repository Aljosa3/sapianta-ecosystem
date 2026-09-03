#!/usr/bin/env python3
"""Repository-only proof of the HN expected-harness identity binding."""

from __future__ import annotations

import ast
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

import pytest


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
HN = ROOT / (
    ".github/governance/evidence/"
    "g77_256hn_wrong_input_bootstrap_harness_binding_v1"
)
HN_CLOUD_INIT = HN / "static/G77_256HN_CLOUD_INIT_USER_DATA_V1.yaml"
HN_SEED = HN / "static/SAPIANTA_WRONG_ATTEMPT_NOCLOUD_SEED_V1.img"
HK = ROOT / ".github/governance/evidence/g77_256hk_current_hg_bootstrap_binding_v1"
HK_CLOUD_INIT = HK / "static/G77_256HK_CLOUD_INIT_USER_DATA_V1.yaml"
HK_SEED = HK / "static/SAPIANTA_WRONG_ATTEMPT_NOCLOUD_SEED_V1.img"
FM = ROOT / ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1"
LAUNCHER_PATH = FM / "launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
OWNER_PATH = FM / "launcher/sapianta_fresh_operation_context_v1.py"
META_DATA = FM / "raw/G77_256FM_CLOUD_INIT_META_DATA_V1.yaml"
NETWORK_CONFIG = FM / "raw/G77_256FM_CLOUD_INIT_NETWORK_CONFIG_V1.yaml"
HA_ADAPTER = ROOT / (
    ".github/governance/evidence/g77_256ha_wrong_input_route_binding_v1/"
    "adapter/G77_256HA_WRONG_INPUT_VECTOR_ADAPTER_V1.py"
)
GY_PRODUCER = ROOT / (
    ".github/governance/evidence/g77_256gy_wrong_input_formalization_v1/"
    "producer/G77_256GY_WRONG_INPUT_REQUEST_AND_CANDIDATE_PRODUCER_V1.py"
)
GY_REDUCER = ROOT / (
    ".github/governance/evidence/g77_256gy_wrong_input_formalization_v1/"
    "reducer/G77_256GY_WRONG_INPUT_TERMINAL_ACCEPTANCE_REDUCER_V1.py"
)
HM = ROOT / ".github/governance/evidence/g77_256hm_wrong_input_operational_v1"
HM_INDEPENDENT = HM / "G77_256HM_INDEPENDENT_TERMINAL_EVIDENCE_REDUCTION_V1.json"
HM_TERMINAL = HM / "G77_256HM_SPCE_TERMINAL_REDUCTION_V1.json"
HM_HEAD = "888b3fcab74339b3201f469190e64f6c44f77508"
HM_TREE = "4427b64bc2a7768e847db8e4b97daf1a9ff132ba"
HG_HEAD = "842a0f2cccd53222d11daa698bdeab17f0aac043"
HG_TREE = "414a5f940e3b5027b6dd86c38d7a134f5c8ab0c4"
HISTORICAL_FM_WRAPPER_SHA256 = (
    "f2808a148bc9839f083ea9e59903674fe0dcd2a7587eee342fca44066ee9ad2b"
)
ACTIVE_WRONG_INPUT_ADAPTER_SHA256 = (
    "fb83002e5567c2a109bfb977270865e6fb085e39f551d1068d03537a3b1d6230"
)
HN_CLOUD_INIT_SHA256 = (
    "be30e3c5084b7464653b8560d4259d69dbdff106d5c118791df6cf87c28d718f"
)
HN_SEED_SHA256 = (
    "e9aeac9135ecbf92bffbb8798a90bd61e39e49e15fa5dff0a4c0e6974e6bf731"
)
HM_CANDIDATE = HM / (
    "live_binding/candidate/G77_256GY_WRONG_INPUT_POST_COMMIT_CANDIDATE_V1.json"
)
HN_REPORT = ROOT / (
    "docs/governance/G77_256HN_WRONG_INPUT_GUEST_BOOTSTRAP_EXPECTED_HARNESS_"
    "IDENTITY_BINDING_CORRECTION_V1.md"
)


def load_module(path: Path, identity: str):
    specification = importlib.util.spec_from_file_location(identity, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


LAUNCHER = load_module(LAUNCHER_PATH, "g77_256hn_fm_launcher")
OWNER = LAUNCHER.fresh_context


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_unique(path: Path) -> dict[str, Any]:
    def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        value: dict[str, Any] = {}
        for key, item in pairs:
            if key in value:
                raise ValueError(f"duplicate JSON key: {key}")
            value[key] = item
        return value

    raw = path.read_bytes()
    value = json.loads(raw, object_pairs_hook=unique_object)
    assert isinstance(value, dict)
    assert raw == OWNER.canonical_bytes(value)
    return value


def build_context(tmp_path: Path) -> dict[str, Any]:
    return LAUNCHER.build_operation_context(
        repository_root=ROOT,
        repository_head=HM_HEAD,
        repository_tree=HM_TREE,
        generation_identity=(
            "G77_256HN_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_INPUT_"
            "OPERATIONAL_COMMISSIONING_V1"
        ),
        operation_identity="G77_256HN_STATIC_BINDING_FIXTURE_001",
        identity_namespace_prefix="G77_256HN",
        operation_evidence_root=tmp_path / "operation_state",
        transient_root=tmp_path / "transient",
        candidate_source_path=HM_CANDIDATE.relative_to(ROOT),
    )


def reseal(context: dict[str, Any]) -> dict[str, Any]:
    value = deepcopy(context)
    value.pop("context_sha256", None)
    return OWNER.seal_context(value)


def project_adapter(context: dict[str, Any], payload: bytes | None = None) -> None:
    binding = context["guest_adapter_binding"]
    projection_root = Path(binding["projection_root"])
    projection_root.mkdir(mode=0o700, parents=True)
    source_bytes = (ROOT / binding["source_path"]).read_bytes()
    projected_bytes = source_bytes if payload is None else payload
    Path(binding["projected_path"]).write_bytes(projected_bytes)
    Path(binding["bootstrap_projected_path"]).write_bytes(projected_bytes)


def build_seed(asset_root: Path, cloud_text: str) -> Path:
    asset_root.mkdir(mode=0o700, parents=True)
    (asset_root / "user-data").write_text(cloud_text, encoding="utf-8")
    (asset_root / "meta-data").write_bytes(META_DATA.read_bytes())
    (asset_root / "network-config").write_bytes(NETWORK_CONFIG.read_bytes())
    seed = asset_root / "seed.img"
    subprocess.run(
        [
            "genisoimage", "-quiet", "-output", str(seed), "-volid", "cidata",
            "-joliet", "-rock", "user-data", "meta-data", "network-config",
        ],
        cwd=asset_root,
        check=True,
    )
    return seed


def context_with_cloud(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    cloud_text: str,
) -> dict[str, Any]:
    asset_root = tmp_path / "bootstrap"
    cloud = asset_root / "user-data"
    seed = build_seed(asset_root, cloud_text)
    cloud_sha = sha256_path(cloud)
    seed_sha = sha256_path(seed)
    monkeypatch.setattr(LAUNCHER, "CLOUD_INIT", str(cloud))
    monkeypatch.setattr(LAUNCHER, "CLOUD_INIT_SHA256", cloud_sha)
    monkeypatch.setattr(LAUNCHER, "SEED", str(seed))
    monkeypatch.setitem(LAUNCHER.EXPECTED_ASSET_SHA256, str(seed), seed_sha)
    return build_context(tmp_path)


def replace_expected_hash(cloud_text: str, replacement: str) -> str:
    assert cloud_text.count(ACTIVE_WRONG_INPUT_ADAPTER_SHA256) == 1
    return cloud_text.replace(ACTIVE_WRONG_INPUT_ADAPTER_SHA256, replacement)


def assert_binding_rejected(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    cloud_text: str,
) -> None:
    context = context_with_cloud(monkeypatch, tmp_path, cloud_text)
    project_adapter(context)
    with pytest.raises((RuntimeError, OWNER.ContextError)):
        LAUNCHER.prove_guest_adapter_binding(ROOT, context)


def test_hm_terminal_failure_and_exact_identities_authenticate() -> None:
    independent = load_unique(HM_INDEPENDENT)["reduction"]
    terminal = load_unique(HM_TERMINAL)["reduction"]
    assert independent["failure"] == {
        "active_adapter_sha256": ACTIVE_WRONG_INPUT_ADAPTER_SHA256,
        "expected_harness_sha256": HISTORICAL_FM_WRAPPER_SHA256,
        "harness_exit_status": 40,
        "qemu_process_exit_status": 0,
        "reason": "EN harness hash mismatch",
        "serial_byte_count": 88742,
        "serial_sha256": (
            "a0d0f592f657c0e846088d45c3d5c9c1cb8d62e72b94e1bf674948b5ab1cb846"
        ),
        "type": "RuntimeError",
    }
    assert terminal["terminal_state"] == "FAIL_CLOSED__OPERATION_CONSUMED__NO_RETRY"
    assert terminal["reducers"]["agreement"] == (
        "VERIFIED__NOT_ACCEPTED__E05_CREDIT_0"
    )
    assert terminal["e05"] == {"after": "7/18", "before": "7/18", "credit": 0}
    assert sha256_path(HA_ADAPTER) == ACTIVE_WRONG_INPUT_ADAPTER_SHA256
    assert sha256_path(FM / "harness/G77_256FM_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py") == (
        HISTORICAL_FM_WRAPPER_SHA256
    )


def test_exact_active_projected_wrong_input_identity_is_accepted(tmp_path: Path) -> None:
    context = build_context(tmp_path)
    project_adapter(context)
    result = LAUNCHER.prove_guest_adapter_binding(ROOT, context)
    assert result["result"] == "PREAUTHORITY_GUEST_ADAPTER_BINDING_PASS"
    assert result["source_sha256"] == result["projected_sha256"] == (
        ACTIVE_WRONG_INPUT_ADAPTER_SHA256
    )
    assert result["nocloud_seed_sha256"] == HN_SEED_SHA256


@pytest.mark.parametrize(
    "replacement",
    (
        HISTORICAL_FM_WRAPPER_SHA256,
        "0" * 64,
        hashlib.sha256(b"unrelated repository object").hexdigest(),
        "malformed",
        "",
    ),
)
def test_historical_stale_unrelated_malformed_and_missing_identity_are_rejected(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    replacement: str,
) -> None:
    assert_binding_rejected(
        monkeypatch,
        tmp_path,
        replace_expected_hash(HN_CLOUD_INIT.read_text(encoding="utf-8"), replacement),
    )


def test_missing_active_adapter_is_rejected(tmp_path: Path) -> None:
    context = build_context(tmp_path)
    with pytest.raises(RuntimeError, match="projection root absent"):
        LAUNCHER.prove_guest_adapter_binding(ROOT, context)


def test_changed_active_adapter_bytes_with_old_expected_identity_are_rejected(
    tmp_path: Path,
) -> None:
    context = build_context(tmp_path)
    project_adapter(context, HA_ADAPTER.read_bytes() + b"\n# substituted\n")
    with pytest.raises(RuntimeError, match="source/projected exact bytes differ"):
        LAUNCHER.prove_guest_adapter_binding(ROOT, context)


def test_bootstrap_and_projected_adapter_disagreement_is_rejected(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    unrelated = hashlib.sha256(b"valid but unrelated adapter").hexdigest()
    assert_binding_rejected(
        monkeypatch,
        tmp_path,
        replace_expected_hash(HN_CLOUD_INIT.read_text(encoding="utf-8"), unrelated),
    )


def test_ambiguous_multiple_candidate_adapter_commands_are_rejected(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    cloud = HN_CLOUD_INIT.read_text(encoding="utf-8")
    command = next(
        line for line in cloud.splitlines()
        if line.strip().startswith("/usr/bin/python3 ")
    )
    assert_binding_rejected(monkeypatch, tmp_path, cloud.replace(command, command + "\n" + command))


def test_wrong_checkout_owner_is_rejected(tmp_path: Path) -> None:
    context = build_context(tmp_path)
    context["qemu_executable_base_seed_checkout_bindings"]["checkout"]["head"] = "1" * 40
    context = reseal(context)
    project_adapter(context)
    with pytest.raises(RuntimeError, match="argument binding mismatch"):
        LAUNCHER.prove_guest_adapter_binding(ROOT, context)


def test_wrong_projected_guest_path_is_rejected(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    cloud = HN_CLOUD_INIT.read_text(encoding="utf-8").replace(
        "/mnt/dp-harness/G77_256FM_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py",
        "/mnt/dp-harness/UNRELATED_ADAPTER.py",
    )
    assert_binding_rejected(monkeypatch, tmp_path, cloud)


def test_historical_hm_fixture_is_statically_blocked_and_corrected_binding_accepts(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    historical = load_unique(HM_INDEPENDENT)["reduction"]["failure"]
    cloud = replace_expected_hash(
        HN_CLOUD_INIT.read_text(encoding="utf-8"),
        historical["expected_harness_sha256"],
    )
    with monkeypatch.context() as historical_patch:
        assert_binding_rejected(
            historical_patch, tmp_path / "historical", cloud
        )
    context = build_context(tmp_path / "corrected")
    project_adapter(context)
    assert LAUNCHER.prove_guest_adapter_binding(ROOT, context)["result"] == (
        "PREAUTHORITY_GUEST_ADAPTER_BINDING_PASS"
    )


def test_hn_bootstrap_pair_is_exact_and_projects_only_current_sources() -> None:
    assert sha256_path(HN_CLOUD_INIT) == LAUNCHER.CLOUD_INIT_SHA256 == (
        HN_CLOUD_INIT_SHA256
    )
    assert sha256_path(HN_SEED) == LAUNCHER.EXPECTED_ASSET_SHA256[LAUNCHER.SEED] == (
        HN_SEED_SHA256
    )
    cloud = HN_CLOUD_INIT.read_text(encoding="utf-8")
    assert cloud.count(ACTIVE_WRONG_INPUT_ADAPTER_SHA256) == 1
    assert HISTORICAL_FM_WRAPPER_SHA256 not in cloud
    for member, source in {
        "/user-data": HN_CLOUD_INIT,
        "/meta-data": META_DATA,
        "/network-config": NETWORK_CONFIG,
    }.items():
        projected = subprocess.check_output(
            ["isoinfo", "-i", str(HN_SEED), "-R", "-x", member]
        )
        assert projected == source.read_bytes()


def test_context_derived_vector_selects_one_exact_bootstrap_pair() -> None:
    wrong_input = LAUNCHER.current_bootstrap_asset_bindings(OWNER.WRONG_INPUT)
    wrong_attempt = LAUNCHER.current_bootstrap_asset_bindings(OWNER.WRONG_ATTEMPT)
    assert wrong_input == {
        "cloud_init_path": LAUNCHER.CLOUD_INIT,
        "cloud_init_sha256": HN_CLOUD_INIT_SHA256,
        "seed_path": LAUNCHER.SEED,
        "seed_sha256": HN_SEED_SHA256,
    }
    assert wrong_attempt == {
        "cloud_init_path": LAUNCHER.WRONG_ATTEMPT_CLOUD_INIT,
        "cloud_init_sha256": sha256_path(HK_CLOUD_INIT),
        "seed_path": LAUNCHER.WRONG_ATTEMPT_SEED,
        "seed_sha256": sha256_path(HK_SEED),
    }
    with pytest.raises(RuntimeError, match="vector unsupported"):
        LAUNCHER.current_bootstrap_asset_bindings("UNRELATED")


def test_hg_hk_gy_ha_semantics_and_historical_assets_are_unchanged() -> None:
    assert subprocess.run(
        ["git", "diff", "--quiet", "HEAD", "--", str(HK.relative_to(ROOT))],
        cwd=ROOT,
        check=False,
    ).returncode == 0
    assert sha256_path(HK_CLOUD_INIT) == (
        "f10425de141e2f790b4b57fe00aa59c345aeb4e2c0e58e3a2b57cbaf602ff666"
    )
    assert sha256_path(HK_SEED) == (
        "6346b9f02b236d71f2698b01a0d607549ad4d9d779a72b5168658994c519913d"
    )
    assert sha256_path(OWNER_PATH) == (
        "db8257ab2e693edf842ba8224792910eb77a32116bf61cd60290d6ca535c73bf"
    )
    assert sha256_path(GY_PRODUCER) == (
        "643de4aa38264410c445107dfdd71b02334871021dd0b7d5ef8886a62e80cd22"
    )
    assert sha256_path(GY_REDUCER) == (
        "8a6e6081118a2c1d305260555ba1ad5a11d97a5d66516f9810beb87c5c39fbf7"
    )
    source = HA_ADAPTER.read_text(encoding="utf-8")
    assert 'TARGET_MUTATION = "input_identity"' in source
    assert 'DEPENDENT_RECOMPUTATION = "record_identity"' in source
    assert "SEMANTIC_MUTATION_COUNT = 1" in source
    assert 'EXPECTED_DIFFERING_FIELDS = ["input_identity", "record_identity"]' in source


def test_single_route_and_zero_authority_or_operation_expansion() -> None:
    source = LAUNCHER_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    mains = [
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "main"
    ]
    qemu_calls = [
        node for node in ast.walk(mains[0])
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "subprocess"
        and node.func.attr == "run"
    ]
    assert len(mains) == len(qemu_calls) == 1
    changed = subprocess.check_output(
        ["git", "diff", "--unified=0", "HEAD", "--", str(LAUNCHER_PATH.relative_to(ROOT))],
        cwd=ROOT,
        text=True,
    )
    additions = "\n".join(
        line[1:] for line in changed.splitlines()
        if line.startswith("+") and not line.startswith("+++")
    ).lower()
    assert "qemu-system" not in additions
    assert "human_operational_authorization" not in additions
    assert "claim_and_invoke" not in additions
    assert "request_identity" not in additions
    assert "retry" not in additions


def test_g48_report_has_exact_six_heading_structure_and_terminal_boundary() -> None:
    report = HN_REPORT.read_text(encoding="utf-8")
    assert [line for line in report.splitlines() if line.startswith("# ")] == [
        "# 1. Implementation Summary",
        "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment",
        "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary",
        "# 6. Certification Verdict",
    ]
    required = (
        "HM_TERMINAL_STATUS = VERIFIED",
        "LAST_VERIFIED_EDGE",
        "FIRST_BROKEN_EDGE",
        HISTORICAL_FM_WRAPPER_SHA256,
        ACTIVE_WRONG_INPUT_ADAPTER_SHA256,
        "HM_FAILURE_CLASS_STATIC_BLOCK_STATUS = VERIFIED",
        "GY_WRONG_INPUT_SEMANTICS = VERIFIED",
        "HA_SEMANTIC_FIREWALL = VERIFIED",
        "PRODUCTION_ROUTE_DELTA = 0",
        "EX_REUSED = 17/17",
        "EX_RECONSTRUCTED = 0",
        "WRONG_INPUT_OPERATIONAL_CAPABILITY = NOT_PROVEN",
        "POST_COMMIT_LIVE_BINDING_STATUS = NOT_PROVEN",
        "AUTO_CONTINUABLE = NO",
        "HUMAN_REVIEW_REQUIRED = YES",
    )
    assert all(token in report for token in required)
    assert report.rstrip().endswith(
        "VERIFIED__G77_256HN_WRONG_INPUT_GUEST_BOOTSTRAP_EXPECTED_HARNESS_"
        "IDENTITY_BINDING_CORRECTED__HM_FAILURE_CLASS_STATICALLY_BLOCKED__ONE_"
        "PRODUCTION_ROUTE__ZERO_OPERATION__E05_7_OF_18__POST_COMMIT_LIVE_"
        "BINDING_NOT_PROVEN__HUMAN_REVIEW_REQUIRED"
    )
