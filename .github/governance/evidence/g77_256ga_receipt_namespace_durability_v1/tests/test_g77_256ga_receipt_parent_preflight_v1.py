#!/usr/bin/env python3
"""Context-aware GA receipt durability regression tests."""

from __future__ import annotations

import ast
import importlib.util
from pathlib import Path
import tempfile
import unittest


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


def context_for(root: Path, prefix: str = "G77_256GATEST01") -> dict:
    context = LAUNCHER.build_operation_context(
        repository_root=REPOSITORY_ROOT,
        repository_head="a" * 40,
        repository_tree="b" * 40,
        generation_identity=prefix + "_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_ATTEMPT_OPERATIONAL_COMMISSIONING_V1",
        operation_identity=prefix + "_OPERATION_001",
        identity_namespace_prefix=prefix,
        operation_evidence_root=root / "operation",
        transient_root=root / "transient",
    )
    Path(context["operation_evidence_root"]).mkdir()
    return context


class G77256GAReceiptParentPreflightTests(unittest.TestCase):
    def test_positive_context_preparation_and_read_only_reauthentication(self):
        with tempfile.TemporaryDirectory(prefix="sapianta_receipt_context_") as temporary:
            context = context_for(Path(temporary))
            prepared = LAUNCHER.prepare_receipt_parent(REPOSITORY_ROOT, context)
            verified = LAUNCHER.validate_receipt_parent_ready(REPOSITORY_ROOT, context)
            self.assertEqual(prepared, verified)
            self.assertTrue(verified["receipt_parent_ready"])
            self.assertTrue(verified["receipt_namespace_unused"])

    def test_parent_absent_file_symlink_and_content_are_denied(self):
        for case in ("absent", "file", "symlink", "content"):
            with self.subTest(case=case), tempfile.TemporaryDirectory(prefix=f"sapianta_receipt_{case}_") as temporary, tempfile.TemporaryDirectory(prefix="sapianta_receipt_target_") as target:
                context = context_for(Path(temporary))
                parent = Path(context["receipt_parent"])
                if case == "file":
                    parent.write_text("not-directory", encoding="utf-8")
                elif case == "symlink":
                    parent.symlink_to(Path(target), target_is_directory=True)
                elif case == "content":
                    LAUNCHER.prepare_receipt_parent(REPOSITORY_ROOT, context)
                    (parent / "unexpected").write_text("x", encoding="utf-8")
                with self.assertRaises((RuntimeError, ValueError)):
                    LAUNCHER.validate_receipt_parent_ready(REPOSITORY_ROOT, context)

    def test_every_context_declared_sink_collision_prevents_preparation(self):
        for index in range(11):
            with self.subTest(index=index), tempfile.TemporaryDirectory(prefix=f"sapianta_receipt_sink_{index}_") as temporary:
                context = context_for(Path(temporary))
                target = LAUNCHER.fresh_context.complete_mutable_sink_paths(context)[index]
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("collision\n", encoding="utf-8")
                with self.assertRaisesRegex(RuntimeError, "consumed"):
                    LAUNCHER.prepare_receipt_parent(REPOSITORY_ROOT, context)

    def test_gate_order_and_no_auto_preparation(self):
        tree = ast.parse(LAUNCHER_PATH.read_text(encoding="utf-8"))
        functions = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
        main_calls = [
            (node.func.id, node.lineno)
            for node in ast.walk(functions["main"])
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        ]
        final = [line for name, line in main_calls if name == "validate_final_admission"]
        writes = sorted(line for name, line in main_calls if name == "write_atomic")
        qemu = [
            node.lineno
            for node in ast.walk(functions["main"])
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "subprocess"
            and node.func.attr == "run"
        ]
        self.assertEqual((len(final), len(writes), len(qemu)), (1, 2, 1))
        self.assertLess(final[0], writes[0])
        self.assertLess(writes[0], qemu[0])
        self.assertLess(qemu[0], writes[1])
        self.assertNotIn("prepare_receipt_parent", [name for name, _ in main_calls])


if __name__ == "__main__":
    unittest.main()
