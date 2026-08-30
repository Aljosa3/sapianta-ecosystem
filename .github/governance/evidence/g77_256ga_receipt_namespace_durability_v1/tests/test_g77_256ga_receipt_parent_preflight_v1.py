#!/usr/bin/env python3
"""Repository-only GA proof for receipt-parent preparation and admission."""

from __future__ import annotations

import ast
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest import mock


REPOSITORY_ROOT = Path(__file__).resolve().parents[5]
LAUNCHER_PATH = REPOSITORY_ROOT / (
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
SPEC = importlib.util.spec_from_file_location("g77_256ga_launcher_v1", LAUNCHER_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("FM launcher import failed")
LAUNCHER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(LAUNCHER)


def isolated_root() -> tempfile.TemporaryDirectory[str]:
    return tempfile.TemporaryDirectory(prefix="g77_256ga_receipt_parent_")


def create_evidence_root(root: Path) -> Path:
    evidence_root = root / LAUNCHER.FY_ROOT
    evidence_root.mkdir(parents=True)
    return evidence_root


def final_admission_arguments(root: Path) -> dict:
    return {
        "repository_root": root,
        "authority": {},
        "authority_file_sha256": "a" * 64,
        "supplied_authority_sha256": "a" * 64,
        "observed_head": "b" * 40,
        "observed_tree": "c" * 40,
        "anchor_is_ancestor": True,
        "repository_clean": True,
        "observed_asset_sha256": {},
        "argv": ["/usr/bin/qemu-system-x86_64", "-nic", "none"],
        "canonical_argv_sha256": "d" * 64,
        "receipt_namespace_consumed": False,
    }


def visibility_result() -> dict[str, str]:
    return {
        "result": "PREBOOT_VISIBILITY_COMPOSITION_PASS",
        "host_export_root": "/static/test/export",
        "guest_required_path": "/mnt/g77-evidence/manifest.json",
        "manifest_sha256": "e" * 64,
        "composition_file_sha256": "f" * 64,
    }


def authority_admission_result() -> dict[str, str]:
    return {
        "result": "ADMIT_TO_BOOT_BOUNDARY_ONLY",
        "authorized_repository_head": "b" * 40,
        "authorized_repository_tree": "c" * 40,
        "constitutional_anchor_head": LAUNCHER.CONSTITUTIONAL_ANCHOR_HEAD,
        "execution_authority_file_sha256": "a" * 64,
        "human_authorization_source_sha256": "1" * 64,
    }


class G77256GAReceiptParentPreflightTests(unittest.TestCase):
    def test_positive_preparation_and_read_only_reauthentication(self):
        with isolated_root() as temporary:
            root = Path(temporary)
            create_evidence_root(root)
            prepared = LAUNCHER.prepare_receipt_parent(root)
            verified = LAUNCHER.validate_receipt_parent_ready(root)
            self.assertEqual(prepared, verified)
            self.assertTrue(verified["receipt_parent_ready"])
            self.assertTrue(verified["receipt_files_absent"])
            self.assertTrue(verified["receipt_namespace_unused"])
            self.assertEqual(list(Path(verified["receipt_parent"]).iterdir()), [])

    def test_positive_final_admission_composes_receipt_readiness(self):
        with isolated_root() as temporary:
            root = Path(temporary)
            create_evidence_root(root)
            LAUNCHER.prepare_receipt_parent(root)
            with mock.patch.object(
                LAUNCHER, "validate_preboot_visibility", return_value=visibility_result()
            ), mock.patch.object(
                LAUNCHER, "validate_execution_admission", return_value=authority_admission_result()
            ):
                result = LAUNCHER.validate_final_admission(
                    **final_admission_arguments(root)
                )
            self.assertEqual(result["result"], "ADMIT_TO_BOOT_BOUNDARY_ONLY")
            self.assertEqual(result["receipt_parent_ready"], "PASS")
            self.assertEqual(result["receipt_files_absent"], "PASS")
            self.assertEqual(result["receipt_namespace_unused"], "PASS")

    def test_fz_absent_parent_fails_before_other_final_admission_gates(self):
        with isolated_root() as temporary:
            root = Path(temporary)
            create_evidence_root(root)
            with mock.patch.object(
                LAUNCHER, "validate_preboot_visibility"
            ) as visibility, mock.patch.object(
                LAUNCHER, "validate_execution_admission"
            ) as authority:
                with self.assertRaisesRegex(RuntimeError, "receipt parent absent"):
                    LAUNCHER.validate_final_admission(**final_admission_arguments(root))
            visibility.assert_not_called()
            authority.assert_not_called()

    def test_parent_file_is_denied(self):
        with isolated_root() as temporary:
            root = Path(temporary)
            evidence_root = create_evidence_root(root)
            (evidence_root / "receipts").write_text("not a directory", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "non-directory"):
                LAUNCHER.validate_receipt_parent_ready(root)

    def test_parent_symlink_is_denied(self):
        with isolated_root() as temporary, isolated_root() as target:
            root = Path(temporary)
            evidence_root = create_evidence_root(root)
            (evidence_root / "receipts").symlink_to(Path(target), target_is_directory=True)
            with self.assertRaisesRegex(RuntimeError, "symlinked"):
                LAUNCHER.validate_receipt_parent_ready(root)

    def test_evidence_root_symlink_substitution_is_denied(self):
        with isolated_root() as temporary, isolated_root() as target:
            root = Path(temporary)
            evidence_parent = root / Path(LAUNCHER.FY_ROOT).parent
            evidence_parent.mkdir(parents=True)
            (root / LAUNCHER.FY_ROOT).symlink_to(Path(target), target_is_directory=True)
            with self.assertRaisesRegex(RuntimeError, "symlink substitution"):
                LAUNCHER.receipt_namespace_paths(root)

    def test_receipt_collision_is_denied(self):
        with isolated_root() as temporary:
            root = Path(temporary)
            create_evidence_root(root)
            LAUNCHER.prepare_receipt_parent(root)
            pre_receipt = root / LAUNCHER.PRE_RECEIPT
            pre_receipt.write_text("{}\n", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "receipt file collision"):
                LAUNCHER.validate_receipt_parent_ready(root)

    def test_unexpected_parent_content_is_denied(self):
        with isolated_root() as temporary:
            root = Path(temporary)
            create_evidence_root(root)
            readiness = LAUNCHER.prepare_receipt_parent(root)
            (Path(readiness["receipt_parent"]) / "unexpected").write_text("x")
            with self.assertRaisesRegex(RuntimeError, "unexpected.*content"):
                LAUNCHER.validate_receipt_parent_ready(root)

    def test_guest_evidence_collision_prevents_preparation(self):
        with isolated_root() as temporary:
            root = Path(temporary)
            evidence_root = create_evidence_root(root)
            runtime_export = evidence_root / "runtime_export"
            runtime_export.mkdir()
            (root / LAUNCHER.RAW_EXECUTION).write_text("{}\n", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "consumed receipt or guest evidence"):
                LAUNCHER.prepare_receipt_parent(root)

    def test_path_traversal_binding_is_denied(self):
        with isolated_root() as temporary:
            root = Path(temporary)
            create_evidence_root(root)
            with mock.patch.object(LAUNCHER, "PRE_RECEIPT", "../escape/pre.json"), mock.patch.object(
                LAUNCHER, "POST_RECEIPT", "../escape/post.json"
            ):
                with self.assertRaisesRegex(RuntimeError, "traverses"):
                    LAUNCHER.receipt_namespace_paths(root)

    def test_gate_order_precedes_receipt_write_and_sole_qemu_call(self):
        tree = ast.parse(LAUNCHER_PATH.read_text(encoding="utf-8"))
        functions = {
            node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)
        }
        final_calls = [
            (node.func.id, node.lineno)
            for node in ast.walk(functions["validate_final_admission"])
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        ]
        final_lines = {name: line for name, line in final_calls}
        self.assertLess(
            final_lines["validate_receipt_parent_ready"],
            final_lines["validate_preboot_visibility"],
        )
        main_calls = [
            (node.func.id, node.lineno)
            for node in ast.walk(functions["main"])
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        ]
        final_admission_lines = [
            line for name, line in main_calls if name == "validate_final_admission"
        ]
        receipt_write_lines = sorted(
            line for name, line in main_calls if name == "write_atomic"
        )
        qemu_lines = [
            node.lineno
            for node in ast.walk(functions["main"])
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "subprocess"
            and node.func.attr == "run"
        ]
        self.assertEqual(len(final_admission_lines), 1)
        self.assertEqual(len(receipt_write_lines), 2)
        self.assertEqual(len(qemu_lines), 1)
        self.assertLess(final_admission_lines[0], receipt_write_lines[0])
        self.assertLess(receipt_write_lines[0], qemu_lines[0])
        self.assertLess(qemu_lines[0], receipt_write_lines[1])
        self.assertNotIn("prepare_receipt_parent", [name for name, _ in main_calls])


if __name__ == "__main__":
    unittest.main()
