from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[5]
FM_PATH = ROOT / (
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
ADAPTER_PATH = ROOT / (
    ".github/governance/evidence/"
    "g77_256jr_expired_human_authority_materialization_and_presentation_binding_v1/"
    "adapter/G77_256JR_EXPIRED_VECTOR_ADAPTER_V1.py"
)
ER_PATH = ROOT / (
    ".github/governance/evidence/g77_256er_p11_operational_v1/harness/"
    "G77_256ER_P11_OPERATIONAL_HARNESS_V1.py"
)
CLOUD_PATH = ROOT / (
    ".github/governance/evidence/"
    "g77_256jx_er_admission_runtime_checkout_role_separation_repair_v1/"
    "static/G77_256JX_CLOUD_INIT_USER_DATA_V1.yaml"
)
SEED_PATH = CLOUD_PATH.with_name("SAPIANTA_EXPIRED_NOCLOUD_SEED_V3.img")
META_PATH = ROOT / (
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/raw/"
    "G77_256FM_CLOUD_INIT_META_DATA_V1.yaml"
)
NETWORK_PATH = META_PATH.with_name("G77_256FM_CLOUD_INIT_NETWORK_CONFIG_V1.yaml")
P11_PATH = ROOT / "tests/p11_da_operational_consumer_v1.py"
JX_ROOT = CLOUD_PATH.parents[1]
REPORT_PATH = JX_ROOT / "G77_256JX_G48_IMPLEMENTATION_REPORT_V1.md"
REDUCTION_PATH = JX_ROOT / "G77_256JX_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
FORMALIZER_PATH = JX_ROOT / "analysis/G77_256JX_ER_ROLE_SEPARATION_FORMALIZER_V1.py"

ENTRY_HEAD = "e8346d2700fa459de546dde961e108706749581b"
ENTRY_TREE = "4bb2d25086390f49d3577500c650891e9ca4a652"
JR_HEAD = "304b342e26e92f226afa01db4b4203acfa51f532"
JR_TREE = "fc0c50e4dd79e900d85d48c5c0aeb53fe9d0c937"
ER_SHA256 = "c6539d1cc60940b1999956965bff43923a270598a982cd19f976eadec0a93152"
ADAPTER_SHA256 = "f24d696ee3ab1f1b5d5feef2fa29e155e971f1aa1b8d890c98734011fb40e1d7"
P11_SHA256 = "38399ab9d1eb74dc2a231eb3a363064ba8b90077d6cdbf1d3494ca937b2127f5"


def load_module(path: Path, name: str):
    specification = importlib.util.spec_from_file_location(name, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture()
def fm():
    return load_module(FM_PATH, "g77_256jx_test_fm")


@pytest.fixture()
def adapter():
    return load_module(ADAPTER_PATH, "g77_256jx_test_expired_adapter")


def build_context(fm, tmp_path: Path) -> dict:
    return fm.build_operation_context(
        repository_root=ROOT,
        repository_head=ENTRY_HEAD,
        repository_tree=ENTRY_TREE,
        generation_identity=(
            "G77_256JX_ONE_FRESH_HUMAN_AUTHORIZED_EXPIRED_"
            "OPERATIONAL_COMMISSIONING_V1"
        ),
        operation_identity="G77_256JX_E05_EXPIRED_DENIAL_BEFORE_ENTRY_001",
        identity_namespace_prefix="G77_256JX",
        operation_evidence_root=tmp_path / "operation_state",
        transient_root=tmp_path / "transient",
    )


def test_authenticated_owners_produce_distinct_sealed_roles(fm, tmp_path: Path) -> None:
    context = build_context(fm, tmp_path)
    checkout = context["qemu_executable_base_seed_checkout_bindings"]["checkout"]
    fm.authenticate_current_committed_jm_route(ROOT, ENTRY_HEAD, ENTRY_TREE)
    assert (context["repository_head"], context["repository_tree"]) == (
        ENTRY_HEAD,
        ENTRY_TREE,
    )
    assert (checkout["head"], checkout["tree"]) == (JR_HEAD, JR_TREE)
    assert context["context_sha256"] == fm.fresh_context.sha256_bytes(
        fm.fresh_context.canonical_bytes(
            {key: value for key, value in context.items() if key != "context_sha256"}
        )
    )
    fm.validate_immutable_context_bindings(ROOT, context)


def _exercise_specialized_loader(
    er,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    *,
    admission_head: str = ENTRY_HEAD,
    admission_tree: str = ENTRY_TREE,
    runtime_head: str = JR_HEAD,
    runtime_tree: str = JR_TREE,
) -> dict:
    context = {
        "repository_head": admission_head,
        "repository_tree": admission_tree,
        "qemu_executable_base_seed_checkout_bindings": {
            "checkout": {"head": runtime_head, "tree": runtime_tree}
        },
        "wrapper_fc_er_che_schema_hashes": {"er_harness": ER_SHA256},
    }
    context_path = tmp_path / "context.json"
    context_path.write_text(json.dumps(context), encoding="utf-8")
    owner_path = tmp_path / "owner.py"
    owner_path.write_text(
        "import json\n"
        "def load_context(path, *, repository_root):\n"
        "    return json.loads(path.read_text(encoding='utf-8'))\n",
        encoding="utf-8",
    )
    p11_path = tmp_path / "p11.py"
    p11_path.write_text("# bound P11\n", encoding="utf-8")
    monkeypatch.setattr(er, "FRESH_OPERATION_CONTEXT_OWNER_PATH", owner_path)
    monkeypatch.setattr(er, "FRESH_OPERATION_CONTEXT_PATH", context_path)
    monkeypatch.setattr(er, "P11_CONSUMER_PATH", p11_path)
    monkeypatch.setattr(er, "COMMITTED_JM_P11_SHA256", P11_SHA256)
    monkeypatch.setattr(er, "_AUTHENTICATED_FRESH_OPERATION_CONTEXT", None)
    monkeypatch.setattr(
        er,
        "run_git",
        lambda *args: JR_TREE if args == ("rev-parse", "HEAD^{tree}") else JR_HEAD,
    )
    monkeypatch.setattr(
        er,
        "sha256_path",
        lambda path: P11_SHA256 if Path(path) == p11_path else ER_SHA256,
    )
    return er.load_authenticated_fresh_operation_context()


def test_specialized_er_accepts_distinct_and_historical_equal_roles(
    adapter, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    er = adapter.specialize_er_harness(ROOT)
    distinct = _exercise_specialized_loader(er, tmp_path, monkeypatch)
    assert distinct["repository_head"] == ENTRY_HEAD
    assert distinct["qemu_executable_base_seed_checkout_bindings"]["checkout"][
        "head"
    ] == JR_HEAD
    equal = _exercise_specialized_loader(
        er,
        tmp_path,
        monkeypatch,
        admission_head=JR_HEAD,
        admission_tree=JR_TREE,
    )
    assert equal["repository_head"] == JR_HEAD


def test_existing_guest_namespace_delivers_specialized_er(
    fm, adapter, tmp_path: Path
) -> None:
    context = build_context(fm, tmp_path)
    context_path = tmp_path / "SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
    context_path.write_bytes(fm.fresh_context.canonical_bytes(context))
    namespace = adapter.load_guest_runtime_namespace(ROOT, context_path)
    er = namespace["load_er"]()
    constants = er.load_authenticated_fresh_operation_context.__code__.co_consts
    assert namespace["GENERATION_ID"] == context["generation_identity"]
    assert "repository_head" not in constants
    assert "repository_tree" not in constants
    assert {"head", "tree"}.issubset(set(constants))


@pytest.mark.parametrize(
    ("runtime_head", "runtime_tree"),
    [
        ("f" * 40, JR_TREE),
        (JR_HEAD, "f" * 40),
        (ENTRY_HEAD, ENTRY_TREE),
    ],
)
def test_specialized_er_rejects_runtime_corruption_and_role_swap(
    adapter,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    runtime_head: str,
    runtime_tree: str,
) -> None:
    er = adapter.specialize_er_harness(ROOT)
    with pytest.raises(RuntimeError, match="checkout binding mismatch"):
        _exercise_specialized_loader(
            er,
            tmp_path,
            monkeypatch,
            runtime_head=runtime_head,
            runtime_tree=runtime_tree,
        )


@pytest.mark.parametrize(
    "mutation",
    [
        {"repository_head": "f" * 40},
        {"repository_tree": "f" * 40},
    ],
)
def test_host_admission_owner_rejects_caller_or_provider_substitution(
    fm, tmp_path: Path, mutation: dict[str, str]
) -> None:
    context = build_context(fm, tmp_path)
    context.update(mutation)
    with pytest.raises(RuntimeError, match="repository binding differs"):
        fm.validate_execution_admission(
            context=context,
            authority={},
            authority_file_sha256="",
            supplied_authority_sha256="",
            observed_head=ENTRY_HEAD,
            observed_tree=ENTRY_TREE,
            anchor_is_ancestor=True,
            repository_clean=True,
            observed_asset_sha256={},
            argv=[],
            canonical_argv_sha256="",
            receipt_namespace_consumed=False,
        )


def test_runtime_binding_rejects_unsealed_substitution_missing_binding_and_swap(
    fm, tmp_path: Path
) -> None:
    context = build_context(fm, tmp_path)
    checkout = context["qemu_executable_base_seed_checkout_bindings"]["checkout"]

    unsealed = json.loads(json.dumps(context))
    unsealed["qemu_executable_base_seed_checkout_bindings"]["checkout"]["head"] = (
        ENTRY_HEAD
    )
    with pytest.raises(fm.fresh_context.ContextError, match="context seal mismatch"):
        fm.validate_immutable_context_bindings(ROOT, unsealed)

    missing = json.loads(json.dumps(context))
    del missing["qemu_executable_base_seed_checkout_bindings"]["checkout"]
    missing = fm.fresh_context.seal_context(
        {key: value for key, value in missing.items() if key != "context_sha256"}
    )
    with pytest.raises(fm.fresh_context.ContextError, match="bindings incomplete"):
        fm.validate_immutable_context_bindings(ROOT, missing)

    swapped = json.loads(json.dumps(context))
    swapped["repository_head"], checkout_head = checkout["head"], swapped[
        "repository_head"
    ]
    swapped["repository_tree"], checkout_tree = checkout["tree"], swapped[
        "repository_tree"
    ]
    swapped["qemu_executable_base_seed_checkout_bindings"]["checkout"].update(
        {"head": checkout_head, "tree": checkout_tree}
    )
    swapped = fm.fresh_context.seal_context(
        {key: value for key, value in swapped.items() if key != "context_sha256"}
    )
    with pytest.raises(RuntimeError, match="binding"):
        fm.validate_immutable_context_bindings(ROOT, swapped)


def test_exact_family_local_delivery_and_jr_runtime_are_preserved(fm) -> None:
    assert sha256(ADAPTER_PATH) == ADAPTER_SHA256
    assert sha256(ER_PATH) == ER_SHA256
    assert sha256(P11_PATH) == P11_SHA256
    assert fm.governed_checkout_identity(ROOT, "EXPIRED", ENTRY_HEAD, ENTRY_TREE) == (
        JR_HEAD,
        JR_TREE,
    )
    assert fm.governed_checkout_identity(
        ROOT,
        "EXPIRED",
        "98206cab55fb4201c3b60de48eb032cca196de7c",
        "ab1a39d41553fc0296e65287782a36b1f20fb22b",
    ) == (JR_HEAD, JR_TREE)
    command = fm.bootstrap_guest_command_arguments(
        CLOUD_PATH.read_text(encoding="utf-8"),
        "/mnt/dp-harness/G77_256FM_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py",
    )
    assert command == (
        ADAPTER_SHA256,
        "95ca9b753b2e4256b6530652d5a6e2a8220fed68c52f774928e1e39721f4ca67",
        JR_HEAD,
        JR_TREE,
        "4e5d01699796d4bb451818408f7cd6a080b6d55fde518df8a9dd2acd3f1a73bb",
    )
    for member, source in (
        ("/user-data", CLOUD_PATH),
        ("/meta-data", META_PATH),
        ("/network-config", NETWORK_PATH),
    ):
        assert subprocess.check_output(
            ["isoinfo", "-i", str(SEED_PATH), "-R", "-x", member],
            stderr=subprocess.DEVNULL,
        ) == source.read_bytes()


def test_temporal_contract_and_single_route_remain_exact(adapter) -> None:
    er = adapter.specialize_er_harness(ROOT)
    assert {500, 100, 1000}.issubset(set(er.create_input_and_authority.__code__.co_consts))
    assert adapter.VALID_FROM_UNIX_NS == 100
    assert adapter.VALID_UNTIL_UNIX_NS == 1000
    assert adapter.PRECLAIM_TIME_UNIX_NS == 1000
    tree = ast.parse(FM_PATH.read_text(encoding="utf-8"))
    assert sum(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == "main"
        for node in tree.body
    ) == 1


def test_terminal_reduction_is_canonical_unique_key_sealed_and_replayable() -> None:
    def unique_object(pairs):
        value = {}
        for key, item in pairs:
            assert key not in value
            value[key] = item
        return value

    raw = REDUCTION_PATH.read_bytes()
    envelope = json.loads(raw, object_pairs_hook=unique_object)
    canonical = (
        json.dumps(envelope, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")
    assert raw == canonical
    reduction = envelope["reduction"]
    assert envelope["reduction_sha256"] == hashlib.sha256(
        (
            json.dumps(reduction, sort_keys=True, separators=(",", ":"), allow_nan=False)
            + "\n"
        ).encode("utf-8")
    ).hexdigest()
    formalizer = load_module(FORMALIZER_PATH, "g77_256jx_test_formalizer")
    assert reduction == formalizer.build_reduction()
    assert reduction["continuation"]["recovery_type"] == (
        "SAME_GENERATION_SAME_ACCOUNT_PROVIDER_LIMIT_CONTINUATION"
    )
    assert reduction["continuation"]["new_generation_created"] == "VERIFIED__NO"
    assert reduction["continuation"]["recovery_existing_delta_authenticated"] == (
        "VERIFIED__YES"
    )


def test_g48_has_six_h1_and_five_exact_reuse_questions() -> None:
    text = REPORT_PATH.read_text(encoding="utf-8")
    assert [line for line in text.splitlines() if line.startswith("# ")] == [
        "# 1. Implementation Summary",
        "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment",
        "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary",
        "# 6. Certification Verdict",
    ]
    questions = (
        "1. Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?",
        "2. Katere nove zmogljivosti (če sploh) nastanejo?",
        "3. Ali katera obstoječa zmogljivost postane nedosegljiva?",
        "4. Ali implementacija ustvarja vzporedni tok?",
        "5. Ali zmanjšuje ali povečuje število produkcijskih poti?",
    )
    assert all(text.count(question) == 1 for question in questions)


def test_bounded_mutation_scope_layer_zero_and_index() -> None:
    changed = set(
        subprocess.check_output(
            ["git", "diff", "--name-only"], cwd=ROOT, text=True
        ).splitlines()
    )
    assert changed == {
        str(FM_PATH.relative_to(ROOT)),
        str(ADAPTER_PATH.relative_to(ROOT)),
    }
    status = subprocess.check_output(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=ROOT,
        text=True,
    ).splitlines()
    assert status
    assert all(
        line[3:].startswith(str(JX_ROOT.relative_to(ROOT)) + "/")
        or line[3:] in changed
        for line in status
    )
    assert not any(line[3:].startswith("docs/governance/") for line in status)
    assert subprocess.check_output(
        ["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True
    ).strip() == ""
