#!/usr/bin/env python3
"""Static positive and fail-closed tests for the existing FM/FO owner chain."""

from __future__ import annotations

import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[5]
LAUNCHER_PATH = REPOSITORY_ROOT / (
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
SPEC = importlib.util.spec_from_file_location("g77_256fm_launcher_v1", LAUNCHER_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("FM launcher import failed")
LAUNCHER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(LAUNCHER)

HEAD = "a" * 40
TREE = "b" * 40
HUMAN_SOURCE = "e" * 64


def sealed_authority() -> dict:
    authorization = {
        "schema_id": LAUNCHER.AUTHORIZATION_SCHEMA,
        "authorization_present": True,
        "authorization_kind": "FRESH_HUMAN_OPERATIONAL_AUTHORIZATION",
        "authorization_source_sha256": HUMAN_SOURCE,
        "authorized_generation_identity": LAUNCHER.GENERATION_IDENTITY,
        "authorized_vector": "WRONG_ATTEMPT",
        "authorized_repository_head": HEAD,
        "authorized_repository_tree": TREE,
        "authorized_constitutional_anchor_head": LAUNCHER.CONSTITUTIONAL_ANCHOR_HEAD,
        "authorized_candidate_sha256": LAUNCHER.CANDIDATE_SHA256,
        "authorized_materialization_sha256": LAUNCHER.MATERIALIZATION_SHA256,
        "authorized_canonical_argv_sha256": LAUNCHER.CANONICAL_ARGV_SHA256,
        "authorized_wrapper_sha256": LAUNCHER.ADAPTER_SHA256,
        "authorized_fk_adapter_sha256": LAUNCHER.FK_ADAPTER_SHA256,
        "vm_boot_limit": 1,
        "qemu_system_execution_limit": 1,
        "wrong_attempt_operational_attempt_limit": 1,
        "retry_limit": 0,
        "repair_limit": 0,
        "replay_limit": 0,
        "receipt_namespace_must_be_unconsumed": True,
        "network_authorized": False,
        "provider_authorized": False,
        "trusted_access_authorized": False,
        "authorization_reusable": False,
        "auto_continuable": False,
    }
    return {
        "schema_id": LAUNCHER.AUTHORITY_SCHEMA,
        "authorization": authorization,
        "authorization_sha256": LAUNCHER.authority_sha256(authorization),
    }


def authority_file_sha(authority: dict) -> str:
    return hashlib.sha256(LAUNCHER.canonical_bytes(authority)).hexdigest()


def vector() -> list[str]:
    return json.loads((REPOSITORY_ROOT / LAUNCHER.VECTOR).read_text(encoding="utf-8"))


def final_admission(argv: list[str], digest: str):
    authority = sealed_authority()
    file_sha = authority_file_sha(authority)
    return LAUNCHER.validate_final_admission(
        repository_root=REPOSITORY_ROOT,
        authority=authority,
        authority_file_sha256=file_sha,
        supplied_authority_sha256=file_sha,
        observed_head=HEAD,
        observed_tree=TREE,
        anchor_is_ancestor=True,
        repository_clean=True,
        observed_asset_sha256=LAUNCHER.asset_observations(REPOSITORY_ROOT),
        argv=argv,
        canonical_argv_sha256=digest,
        receipt_namespace_consumed=False,
    )


class G77256FYPrebootVisibilityTests(unittest.TestCase):
    def test_exact_host_to_guest_composition_passes(self):
        argv = vector()
        result = LAUNCHER.validate_preboot_visibility(
            REPOSITORY_ROOT,
            argv,
            LAUNCHER.CANONICAL_ARGV_SHA256,
        )
        self.assertEqual(result["result"], "PREBOOT_VISIBILITY_COMPOSITION_PASS")
        self.assertEqual(result["host_export_root"], LAUNCHER.HOST_EXPORT_ROOT)
        self.assertEqual(result["guest_required_path"], LAUNCHER.GUEST_REQUIRED_PATH)
        self.assertEqual(result["mapped_host_path"], LAUNCHER.MAPPED_HOST_PATH)
        self.assertEqual(result["manifest_sha256"], LAUNCHER.CANDIDATE_SHA256)

    def test_final_admission_consumes_same_composition(self):
        result = final_admission(vector(), LAUNCHER.CANONICAL_ARGV_SHA256)
        self.assertEqual(result["result"], "ADMIT_TO_BOOT_BOUNDARY_ONLY")
        self.assertEqual(
            result["preboot_visibility_composition"],
            "PREBOOT_VISIBILITY_COMPOSITION_PASS",
        )
        self.assertEqual(result["runtime_export_root"], LAUNCHER.HOST_EXPORT_ROOT)

    def test_mismatched_actual_qemu_export_root_is_denied(self):
        argv = vector()
        argv[-1] = argv[-1].replace(
            LAUNCHER.HOST_EXPORT_ROOT,
            "/tmp/g77_256fy_intentionally_mismatched_export",
        )
        canonicalizer = LAUNCHER.load_canonicalizer(REPOSITORY_ROOT)
        with self.assertRaisesRegex(RuntimeError, "canonical QEMU argv identity mismatch"):
            final_admission(argv, canonicalizer.argv_sha256(argv))

    def test_absent_manifest_is_denied_by_existing_preboot_owner(self):
        envelope = json.loads((REPOSITORY_ROOT / LAUNCHER.MATERIALIZATION).read_text())
        checkpoint = copy.deepcopy(envelope["checkpoint"])
        with tempfile.TemporaryDirectory(prefix="g77_256fy_absent_") as temporary:
            export_root = Path(temporary)
            relative = LAUNCHER.HARNESS_RELATIVE_FILENAME
            qemu_argument = (
                f"local,path={export_root},mount_tag={LAUNCHER.MOUNT_TAG},"
                "security_model=none"
            )
            checkpoint["visibility_composition"].update({
                "host_export_root": str(export_root),
                "mapped_host_path": str(export_root / relative),
                "qemu_virtfs_argument": qemu_argument,
            })
            checkpoint["canonical_manifest"]["runtime_export_path"] = str(
                export_root / relative
            )
            argv = vector()
            argv[-1] = qemu_argument
            canonicalizer = LAUNCHER.load_canonicalizer(REPOSITORY_ROOT)
            digest = canonicalizer.argv_sha256(argv)
            checkpoint["qemu_binding"]["canonical_argv_sha256"] = digest
            with self.assertRaisesRegex(RuntimeError, "host projection absent"):
                LAUNCHER.prove_visibility_composition(
                    repository_root=REPOSITORY_ROOT,
                    checkpoint=checkpoint,
                    argv=argv,
                    canonical_argv_sha256=digest,
                )

    def test_wrong_manifest_bytes_are_denied_before_final_admission(self):
        envelope = json.loads((REPOSITORY_ROOT / LAUNCHER.MATERIALIZATION).read_text())
        checkpoint = copy.deepcopy(envelope["checkpoint"])
        with tempfile.TemporaryDirectory(prefix="g77_256fy_wrong_bytes_") as temporary:
            export_root = Path(temporary)
            runtime_path = export_root / LAUNCHER.HARNESS_RELATIVE_FILENAME
            runtime_path.write_bytes(b"{}\n")
            qemu_argument = (
                f"local,path={export_root},mount_tag={LAUNCHER.MOUNT_TAG},"
                "security_model=none"
            )
            checkpoint["visibility_composition"].update({
                "host_export_root": str(export_root),
                "mapped_host_path": str(runtime_path),
                "qemu_virtfs_argument": qemu_argument,
            })
            checkpoint["canonical_manifest"]["runtime_export_path"] = str(runtime_path)
            argv = vector()
            argv[-1] = qemu_argument
            canonicalizer = LAUNCHER.load_canonicalizer(REPOSITORY_ROOT)
            digest = canonicalizer.argv_sha256(argv)
            checkpoint["qemu_binding"]["canonical_argv_sha256"] = digest
            with self.assertRaisesRegex(RuntimeError, "identity mismatch"):
                LAUNCHER.prove_visibility_composition(
                    repository_root=REPOSITORY_ROOT,
                    checkpoint=checkpoint,
                    argv=argv,
                    canonical_argv_sha256=digest,
                )

    def test_all_visibility_gates_precede_the_sole_qemu_call(self):
        tree = ast.parse(LAUNCHER_PATH.read_text(encoding="utf-8"))
        final_gate_lines = [
            node.lineno
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "validate_final_admission"
        ]
        qemu_call_lines = [
            node.lineno
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "subprocess"
            and node.func.attr == "run"
            and node.args
            and isinstance(node.args[0], ast.Name)
            and node.args[0].id == "argv"
        ]
        self.assertEqual(len(final_gate_lines), 1)
        self.assertEqual(len(qemu_call_lines), 1)
        self.assertLess(final_gate_lines[0], qemu_call_lines[0])


if __name__ == "__main__":
    unittest.main()
