#!/usr/bin/env python3
"""Context-aware regression for reused FY visibility semantics."""

from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[5]
LAUNCHER_PATH = REPOSITORY_ROOT / (
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
SPEC = importlib.util.spec_from_file_location("g77_256fy_context_owner", LAUNCHER_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("FM launcher import failed")
LAUNCHER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(LAUNCHER)
PREFIX = "G77_256FYTEST01"


def context_for(root: Path) -> tuple[dict, Path]:
    context = LAUNCHER.build_operation_context(
        repository_root=REPOSITORY_ROOT,
        repository_head="a" * 40,
        repository_tree="b" * 40,
        generation_identity=PREFIX + "_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_ATTEMPT_OPERATIONAL_COMMISSIONING_V1",
        operation_identity=PREFIX + "_OPERATION_001",
        identity_namespace_prefix=PREFIX,
        operation_evidence_root=root / "operation",
        transient_root=root / "transient",
    )
    path = root / "context.json"
    path.write_bytes(LAUNCHER.canonical_bytes(context))
    LAUNCHER.materialize_operation_state(
        repository_root=REPOSITORY_ROOT,
        context=context,
        context_source_path=path,
    )
    return context, path


class G77256FYPrebootVisibilityTests(unittest.TestCase):
    def test_exact_context_host_to_guest_composition_passes(self):
        with tempfile.TemporaryDirectory(prefix="sapianta_visibility_context_") as temporary:
            context, _ = context_for(Path(temporary))
            result = LAUNCHER.validate_preboot_visibility(
                REPOSITORY_ROOT,
                context,
                context["canonical_argv"],
                context["canonical_argv_sha256"],
            )
            self.assertEqual(result["result"], "PREBOOT_VISIBILITY_COMPOSITION_PASS")
            self.assertEqual(result["host_export_root"], context["runtime_export_root"])
            self.assertEqual(result["guest_required_path"], context["guest_context_path"])

    def test_virtfs_manifest_and_guest_context_mismatches_are_denied(self):
        for case in ("virtfs", "manifest", "guest_context"):
            with self.subTest(case=case), tempfile.TemporaryDirectory(prefix=f"sapianta_visibility_{case}_") as temporary:
                context, _ = context_for(Path(temporary))
                if case == "virtfs":
                    argv = list(context["canonical_argv"])
                    argv[-1] = argv[-1].replace(context["runtime_export_root"], "/tmp/mismatch")
                    with self.assertRaisesRegex(RuntimeError, "argv instance"):
                        LAUNCHER.validate_preboot_visibility(
                            REPOSITORY_ROOT, context, argv,
                            LAUNCHER.fresh_context.argv_sha256(argv),
                        )
                elif case == "manifest":
                    Path(context["runtime_manifest_path"]).write_text("{}\n", encoding="utf-8")
                    with self.assertRaisesRegex(RuntimeError, "manifest projection bytes"):
                        LAUNCHER.validate_preboot_visibility(
                            REPOSITORY_ROOT, context, context["canonical_argv"],
                            context["canonical_argv_sha256"],
                        )
                else:
                    projection = Path(context["runtime_export_root"]) / LAUNCHER.fresh_context.GUEST_CONTEXT_FILENAME
                    value = copy.deepcopy(context)
                    value["context_sha256"] = "0" * 64
                    projection.write_bytes(LAUNCHER.canonical_bytes(value))
                    with self.assertRaisesRegex(ValueError, "context seal"):
                        LAUNCHER.validate_preboot_visibility(
                            REPOSITORY_ROOT, context, context["canonical_argv"],
                            context["canonical_argv_sha256"],
                        )

    def test_historical_fy_composition_is_not_execution_fallback(self):
        source = LAUNCHER_PATH.read_text(encoding="utf-8")
        main_source = source[source.index("def main()") :]
        self.assertIn("--operation-context", source)
        self.assertNotIn("_validate_historical_fy_preboot_visibility", main_source)
        self.assertNotIn("FY_ROOT", main_source)


if __name__ == "__main__":
    unittest.main()
