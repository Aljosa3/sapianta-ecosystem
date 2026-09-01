#!/usr/bin/env python3
"""Repository-only regression proof for the GT checkout lifecycle binding."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[5]
LAUNCHER_PATH = REPOSITORY_ROOT / (
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
GS_CONTEXT_PATH = REPOSITORY_ROOT / (
    ".github/governance/evidence/g77_256gs_wrong_attempt_operational_v1/"
    "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
)
GS_CANDIDATE_PATH = REPOSITORY_ROOT / (
    ".github/governance/evidence/g77_256gs_wrong_attempt_operational_v1/"
    "live_binding/candidate/G77_256GS_CONTINUATION_MANIFEST_V1.json"
)
PREFIX = "G77_256GTTEST01"


def load_launcher():
    spec = importlib.util.spec_from_file_location("g77_256gt_fm_owner", LAUNCHER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("FM checkout lifecycle owner import unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


LAUNCHER = load_launcher()


def build_context(root: Path) -> dict:
    permanent = root / "permanent"
    permanent.mkdir()
    return LAUNCHER.build_operation_context(
        repository_root=REPOSITORY_ROOT,
        repository_head="a" * 40,
        repository_tree="b" * 40,
        generation_identity=(
            PREFIX
            + "_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_ATTEMPT_"
            "OPERATIONAL_COMMISSIONING_V1"
        ),
        operation_identity=PREFIX + "_OPERATION_001",
        identity_namespace_prefix=PREFIX,
        operation_evidence_root=permanent / "operation_state",
        transient_root=root / "transient",
    )


def reseal(context: dict) -> dict:
    unsealed = {key: value for key, value in context.items() if key != "context_sha256"}
    context["context_sha256"] = hashlib.sha256(
        LAUNCHER.canonical_bytes(unsealed)
    ).hexdigest()
    return context


class CheckoutLifecycleCorrectionTests(unittest.TestCase):
    def test_sealed_historical_v1_context_retains_fixed_path_collision_semantics(self):
        context = LAUNCHER.fresh_context.load_context(
            GS_CONTEXT_PATH, repository_root=REPOSITORY_ROOT
        )
        self.assertEqual(context["context_schema_version"], "1.0.0")
        self.assertEqual(
            LAUNCHER.fresh_context.checkout_lifecycle_binding(context),
            LAUNCHER.fresh_context.LEGACY_FIXED_CHECKOUT_LIFECYCLE,
        )
        with self.assertRaisesRegex(RuntimeError, "fresh checkout destination collision"):
            LAUNCHER.materialize_operation_state(
                repository_root=REPOSITORY_ROOT,
                context=context,
                context_source_path=GS_CONTEXT_PATH,
                candidate_source_path=GS_CANDIDATE_PATH,
            )

    def test_current_context_binds_checkout_to_exact_transient_root_child(self):
        with tempfile.TemporaryDirectory(prefix="g77_256gt_context_") as temporary:
            context = build_context(Path(temporary))
            checkout = Path(
                context["qemu_executable_base_seed_checkout_bindings"]["checkout"]["path"]
            )
            transient_root = Path(context["transient_root"])
            self.assertEqual(checkout, transient_root / "checkout")
            self.assertEqual(
                LAUNCHER.fresh_context.checkout_lifecycle_binding(context),
                LAUNCHER.fresh_context.OPERATION_SCOPED_CHECKOUT_LIFECYCLE,
            )
            readiness = LAUNCHER.preauth_fresh_checkout_destination_readiness(
                REPOSITORY_ROOT, context
            )
            self.assertEqual(
                readiness["result"],
                "PREAUTH_FRESH_CHECKOUT_DESTINATION_READINESS_PASS",
            )
            self.assertEqual(Path(readiness["checkout_path"]), checkout)
            self.assertFalse(readiness["destination_absence_alone_sufficient"])

    def test_nested_checkout_materializes_and_existing_gp_owner_accepts_it(self):
        with tempfile.TemporaryDirectory(prefix="g77_256gt_materialize_") as temporary:
            root = Path(temporary)
            transient_root = root / "transient"
            checkout = transient_root / "checkout"
            permanent_evidence = root / "permanent" / "evidence.json"
            permanent_evidence.parent.mkdir()
            permanent_evidence.write_text("permanent-evidence\n", encoding="utf-8")

            observation = LAUNCHER.materialize_guest_self_contained_checkout(
                source_repository=REPOSITORY_ROOT,
                checkout_path=checkout,
                expected_head=LAUNCHER.CHECKOUT_HEAD,
                expected_tree=LAUNCHER.CHECKOUT_TREE,
            )
            context = {
                "canonical_argv": [
                    "qemu-system-x86_64",
                    "-virtfs",
                    (
                        f"local,path={checkout},mount_tag=aigol_checkout,"
                        "security_model=none,readonly=on"
                    ),
                ],
                "qemu_executable_base_seed_checkout_bindings": {
                    "checkout": {
                        "path": str(checkout),
                        "head": LAUNCHER.CHECKOUT_HEAD,
                        "tree": LAUNCHER.CHECKOUT_TREE,
                        "detached": True,
                        "clean": True,
                        "read_only_mount": True,
                    }
                },
            }
            gp = LAUNCHER.validate_checkout_preboot_readiness(context)
            self.assertEqual(
                observation["result"],
                "GUEST_SELF_CONTAINED_CHECKOUT_MATERIALIZATION_PASS",
            )
            self.assertEqual(
                gp["preauth_guest_checkout_tree_authentication"]["result"],
                "PREAUTH_GUEST_CHECKOUT_TREE_AUTHENTICATION_PASS",
            )
            self.assertTrue(checkout.is_relative_to(transient_root))

            shutil.rmtree(transient_root)
            self.assertFalse(transient_root.exists())
            self.assertEqual(
                permanent_evidence.read_text(encoding="utf-8"),
                "permanent-evidence\n",
            )

    def test_active_incomplete_authority_and_legacy_states_fail_closed(self):
        for unsafe_state in ("transient", "operation", "authority"):
            with self.subTest(unsafe_state=unsafe_state), tempfile.TemporaryDirectory(
                prefix="g77_256gt_unsafe_"
            ) as temporary:
                root = Path(temporary)
                context = build_context(root)
                if unsafe_state == "transient":
                    Path(context["transient_root"]).mkdir()
                    pattern = "active or incomplete transient"
                elif unsafe_state == "operation":
                    Path(context["operation_evidence_root"]).mkdir()
                    pattern = "active or incomplete operation"
                else:
                    authority = (
                        Path(context["operation_evidence_root"]).parent
                        / f"{PREFIX}_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt"
                    )
                    authority.write_text("test-only-not-authority\n", encoding="utf-8")
                    pattern = "live authority dependency"
                with self.assertRaisesRegex(RuntimeError, pattern):
                    LAUNCHER.preauth_fresh_checkout_destination_readiness(
                        REPOSITORY_ROOT, context
                    )

        historical = LAUNCHER.fresh_context.load_context(
            GS_CONTEXT_PATH, repository_root=REPOSITORY_ROOT
        )
        with self.assertRaisesRegex(RuntimeError, "legacy checkout destination"):
            LAUNCHER.preauth_fresh_checkout_destination_readiness(
                REPOSITORY_ROOT, historical
            )

    def test_non_owned_checkout_and_failed_staging_do_not_create_lifecycle_root(self):
        with tempfile.TemporaryDirectory(prefix="g77_256gt_nonowned_") as temporary:
            root = Path(temporary)
            context = build_context(root)
            checkout = context["qemu_executable_base_seed_checkout_bindings"]["checkout"]
            old_path = checkout["path"]
            checkout["path"] = str(root / "outside" / "checkout")
            context["canonical_argv"] = [
                item.replace(old_path, checkout["path"])
                for item in context["canonical_argv"]
            ]
            context["canonical_argv_sha256"] = LAUNCHER.fresh_context.argv_sha256(
                context["canonical_argv"]
            )
            reseal(context)
            with self.assertRaisesRegex(ValueError, "no authenticated lifecycle owner"):
                LAUNCHER.fresh_context.validate_context(
                    context, repository_root=REPOSITORY_ROOT
                )

        with tempfile.TemporaryDirectory(prefix="g77_256gt_staging_") as temporary:
            lifecycle_root = Path(temporary) / "transient"
            with self.assertRaisesRegex(RuntimeError, "exact expected HEAD/TREE"):
                LAUNCHER.materialize_guest_self_contained_checkout(
                    source_repository=REPOSITORY_ROOT,
                    checkout_path=lifecycle_root / "checkout",
                    expected_head=LAUNCHER.CHECKOUT_HEAD,
                    expected_tree="0" * 40,
                )
            self.assertFalse(lifecycle_root.exists())


if __name__ == "__main__":
    unittest.main()
