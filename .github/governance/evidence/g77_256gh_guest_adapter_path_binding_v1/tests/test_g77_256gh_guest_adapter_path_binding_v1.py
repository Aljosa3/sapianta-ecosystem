from __future__ import annotations

import copy
import hashlib
import importlib.util
from pathlib import Path
import tempfile
from unittest import mock

import pytest


REPOSITORY_ROOT = Path(__file__).resolve().parents[5]
LAUNCHER_PATH = REPOSITORY_ROOT / (
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)


def load_launcher():
    spec = importlib.util.spec_from_file_location("g77_256gh_launcher", LAUNCHER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


LAUNCHER = load_launcher()


def reseal(context: dict) -> dict:
    context["context_sha256"] = hashlib.sha256(
        LAUNCHER.canonical_bytes(
            {key: value for key, value in context.items() if key != "context_sha256"}
        )
    ).hexdigest()
    return context


def build_and_materialize(root: Path, prefix: str) -> dict:
    context = LAUNCHER.build_operation_context(
        repository_root=REPOSITORY_ROOT,
        repository_head="a" * 40,
        repository_tree="b" * 40,
        generation_identity=(
            f"{prefix}_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_ATTEMPT_"
            "OPERATIONAL_COMMISSIONING_V1"
        ),
        operation_identity=f"{prefix}_OPERATION_001",
        identity_namespace_prefix=prefix,
        operation_evidence_root=root / "operation",
        transient_root=root / "transient",
    )
    context_path = root / "context.json"
    context_path.write_bytes(LAUNCHER.canonical_bytes(context))
    with mock.patch.object(
        LAUNCHER,
        "materialize_guest_self_contained_checkout",
        return_value={"result": "TEST_ONLY_GQ_MATERIALIZATION_PASS"},
    ):
        materialization = LAUNCHER.materialize_operation_state(
            repository_root=REPOSITORY_ROOT,
            context=context,
            context_source_path=context_path,
        )
    assert materialization["qemu_execution_count"] == 0
    return context


@pytest.mark.parametrize("prefix", ["G77_256GHSYNTHA", "G77_256GHSYNTHB"])
def test_two_fresh_namespaces_prove_the_complete_adapter_chain(prefix: str):
    with tempfile.TemporaryDirectory(prefix="g77_256gh_positive_") as temporary:
        context = build_and_materialize(Path(temporary), prefix)
        proof = LAUNCHER.prove_guest_adapter_binding(REPOSITORY_ROOT, context)
        assert proof["result"] == "PREAUTHORITY_GUEST_ADAPTER_BINDING_PASS"
        assert proof["adapter_identity"] == (
            f"{prefix}_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py"
        )
        assert proof["guest_path"] == proof["guest_consumer_path"]
        assert proof["source_sha256"] == proof["projected_sha256"]
        assert proof["source_projected_byte_identity"] == "PASS"
        assert proof["nocloud_source_projection_identity"] == "PASS"


def test_context_derivation_rejects_wrong_name_prefix_hash_guest_path_and_escape():
    with tempfile.TemporaryDirectory(prefix="g77_256gh_context_negative_") as temporary:
        root = Path(temporary)
        baseline = build_and_materialize(root, "G77_256GHNEGATIVE")
        mutations = {
            "missing_adapter_source": (
                "source_path",
                ".github/governance/evidence/missing/ADAPTER.py",
            ),
            "wrong_adapter_filename": ("adapter_identity", "WRONG.py"),
            "wrong_dynamic_prefix": (
                "adapter_identity",
                "G77_256STALE_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py",
            ),
            "wrong_source_sha": ("source_sha256", "0" * 64),
            "wrong_guest_path": ("guest_path", "/mnt/dp-harness/WRONG.py"),
            "path_traversal": (
                "projected_path",
                str(Path(baseline["guest_adapter_binding"]["projection_root"]) / ".." / "escape.py"),
            ),
            "context_adapter_identity_mismatch": (
                "guest_path",
                "/mnt/dp-harness/G77_256OTHER_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py",
            ),
        }
        for name, (field, value) in mutations.items():
            mutated = copy.deepcopy(baseline)
            mutated["guest_adapter_binding"][field] = value
            reseal(mutated)
            with pytest.raises(ValueError, match="adapter binding|canonical safe"):
                LAUNCHER.fresh_context.validate_context(
                    mutated, repository_root=REPOSITORY_ROOT
                )

        historical = copy.deepcopy(baseline)
        historical["identity_namespace_prefix"] = "G77_256FY"
        reseal(historical)
        with pytest.raises(ValueError, match="historical"):
            LAUNCHER.fresh_context.validate_context(
                historical, repository_root=REPOSITORY_ROOT
            )


def test_materialized_projection_negative_matrix_fails_closed():
    cases = (
        "missing_adapter_source",
        "wrong_projected_filename",
        "wrong_projected_bytes",
        "stale_generation_alias",
        "duplicate_or_ambiguous_adapter",
        "projection_consumer_path_mismatch",
    )
    for case in cases:
        with tempfile.TemporaryDirectory(prefix=f"g77_256gh_{case}_") as temporary:
            context = build_and_materialize(Path(temporary), "G77_256GHMATRIX")
            binding = context["guest_adapter_binding"]
            projected = Path(binding["projected_path"])
            if case == "missing_adapter_source":
                projected.unlink()
            elif case == "wrong_projected_filename":
                projected.rename(projected.with_name("WRONG_ADAPTER.py"))
            elif case == "wrong_projected_bytes":
                projected.write_bytes(b"wrong projected bytes\n")
            elif case == "stale_generation_alias":
                projected.rename(
                    projected.with_name(
                        "G77_256GG_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py"
                    )
                )
            elif case == "duplicate_or_ambiguous_adapter":
                (projected.parent / "G77_256OTHER_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py").write_bytes(
                    projected.read_bytes()
                )

            if case == "projection_consumer_path_mismatch":
                patch = mock.patch.object(
                    LAUNCHER,
                    "fc_guest_consumer_path",
                    return_value="/mnt/dp-harness/DIFFERENT.py",
                )
            else:
                patch = mock.patch.object(
                    LAUNCHER,
                    "fc_guest_consumer_path",
                    wraps=LAUNCHER.fc_guest_consumer_path,
                )
            with patch, pytest.raises(RuntimeError):
                LAUNCHER.prove_guest_adapter_binding(REPOSITORY_ROOT, context)


def test_qemu_projection_and_nocloud_exact_bytes_fail_closed():
    with tempfile.TemporaryDirectory(prefix="g77_256gh_qemu_negative_") as temporary:
        context = build_and_materialize(Path(temporary), "G77_256GHQEMU")
        mutated = copy.deepcopy(context)
        argument_index = next(
            index + 1
            for index, value in enumerate(mutated["canonical_argv"])
            if value == "-virtfs"
            and "mount_tag=fm_harness" in mutated["canonical_argv"][index + 1]
        )
        mutated["canonical_argv"][argument_index] = mutated["canonical_argv"][
            argument_index
        ].replace("readonly=on", "readonly=off")
        mutated["canonical_argv_sha256"] = LAUNCHER.fresh_context.argv_sha256(
            mutated["canonical_argv"]
        )
        reseal(mutated)
        with pytest.raises(ValueError, match="approved operation slots"):
            LAUNCHER.fresh_context.validate_context(
                mutated, repository_root=REPOSITORY_ROOT
            )
