#!/usr/bin/env python3
"""Repository-only GQ proof for FM checkout materialization through GP."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock


REPOSITORY_ROOT = Path(__file__).resolve().parents[5]
LAUNCHER_PATH = REPOSITORY_ROOT / (
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)


def load_launcher():
    spec = importlib.util.spec_from_file_location("g77_256gq_existing_fm_owner", LAUNCHER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("FM materialization owner import unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


LAUNCHER = load_launcher()


def git(root: Path, *arguments: str) -> str:
    return subprocess.run(
        ["git", *arguments],
        cwd=root,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).stdout.strip()


def create_repository(root: Path) -> tuple[str, str]:
    root.mkdir()
    git(root, "init", "-q")
    git(root, "config", "user.name", "GQ Test")
    git(root, "config", "user.email", "gq@example.invalid")
    (root / "tracked.txt").write_text("guest-self-contained\n", encoding="utf-8")
    git(root, "add", "tracked.txt")
    git(root, "commit", "-q", "-m", "GQ self-contained fixture")
    return git(root, "rev-parse", "HEAD"), git(root, "rev-parse", "HEAD^{tree}")


def context_for(checkout: Path, head: str, tree: str) -> dict:
    argument = (
        f"local,path={checkout},mount_tag=aigol_checkout,"
        "security_model=none,readonly=on"
    )
    return {
        "canonical_argv": ["qemu-system-x86_64", "-virtfs", argument],
        "qemu_executable_base_seed_checkout_bindings": {
            "checkout": {
                "path": str(checkout),
                "head": head,
                "tree": tree,
                "detached": True,
                "clean": True,
                "read_only_mount": True,
            }
        },
    }


class GuestSelfContainedCheckoutMaterializationTests(unittest.TestCase):
    def test_object_localized_detached_checkout_is_accepted_by_gp_owner(self):
        with tempfile.TemporaryDirectory(prefix="g77_256gq_positive_") as temporary:
            root = Path(temporary)
            source = root / "source"
            head, tree = create_repository(source)
            checkout = root / "checkout"
            materialization = LAUNCHER.materialize_guest_self_contained_checkout(
                source_repository=source,
                checkout_path=checkout,
                expected_head=head,
                expected_tree=tree,
            )
            proof = LAUNCHER.validate_checkout_preboot_readiness(
                context_for(checkout, head, tree)
            )["preauth_guest_checkout_tree_authentication"]

            self.assertEqual(
                materialization["result"],
                "GUEST_SELF_CONTAINED_CHECKOUT_MATERIALIZATION_PASS",
            )
            self.assertEqual(materialization["observed_head"], head)
            self.assertEqual(materialization["observed_tree"], tree)
            self.assertFalse(materialization["external_git_metadata_dependency"])
            self.assertFalse(materialization["external_object_database_dependency"])
            self.assertEqual(
                proof["result"], "PREAUTH_GUEST_CHECKOUT_TREE_AUTHENTICATION_PASS"
            )
            self.assertEqual(proof["guest_destination"], "/mnt/aigol")
            self.assertFalse((checkout / ".git/objects/info/alternates").exists())
            self.assertFalse((checkout / ".git/objects/info/http-alternates").exists())

    def test_borrowed_source_is_localized_without_propagating_alternate(self):
        with tempfile.TemporaryDirectory(prefix="g77_256gq_localize_") as temporary:
            root = Path(temporary)
            origin = root / "origin"
            head, tree = create_repository(origin)
            borrowed = root / "borrowed"
            git(root, "clone", "-q", "--shared", str(origin), str(borrowed))
            self.assertTrue((borrowed / ".git/objects/info/alternates").is_file())
            checkout = root / "checkout"
            LAUNCHER.materialize_guest_self_contained_checkout(
                source_repository=borrowed,
                checkout_path=checkout,
                expected_head=head,
                expected_tree=tree,
            )
            self.assertFalse((checkout / ".git/objects/info/alternates").exists())
            self.assertEqual(git(checkout, "cat-file", "-t", head), "commit")
            self.assertEqual(git(checkout, "cat-file", "-t", tree), "tree")

    def test_collision_wrong_tree_missing_commit_and_symlink_parent_fail_closed(self):
        with tempfile.TemporaryDirectory(prefix="g77_256gq_negative_") as temporary:
            root = Path(temporary)
            source = root / "source"
            head, tree = create_repository(source)
            collision = root / "collision"
            collision.mkdir()
            with self.assertRaisesRegex(RuntimeError, "destination collision"):
                LAUNCHER.materialize_guest_self_contained_checkout(
                    source_repository=source,
                    checkout_path=collision,
                    expected_head=head,
                    expected_tree=tree,
                )
            with self.assertRaisesRegex(RuntimeError, "exact expected HEAD/TREE"):
                LAUNCHER.materialize_guest_self_contained_checkout(
                    source_repository=source,
                    checkout_path=root / "wrong-tree",
                    expected_head=head,
                    expected_tree="0" * 40,
                )
            with self.assertRaises(subprocess.CalledProcessError):
                LAUNCHER.materialize_guest_self_contained_checkout(
                    source_repository=source,
                    checkout_path=root / "missing-commit",
                    expected_head="f" * 40,
                    expected_tree=tree,
                )
            real_parent = root / "real-parent"
            real_parent.mkdir()
            alias_parent = root / "alias-parent"
            alias_parent.symlink_to(real_parent, target_is_directory=True)
            with self.assertRaisesRegex(RuntimeError, "parent is not canonical"):
                LAUNCHER.materialize_guest_self_contained_checkout(
                    source_repository=source,
                    checkout_path=alias_parent / "checkout",
                    expected_head=head,
                    expected_tree=tree,
                )

    def test_existing_fm_materialization_binds_exact_context_checkout(self):
        with tempfile.TemporaryDirectory(prefix="g77_256gq_binding_") as temporary:
            root = Path(temporary)
            context = LAUNCHER.build_operation_context(
                repository_root=REPOSITORY_ROOT,
                repository_head="a" * 40,
                repository_tree="b" * 40,
                generation_identity=(
                    "G77_256GQTEST_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_ATTEMPT_"
                    "OPERATIONAL_COMMISSIONING_V1"
                ),
                operation_identity="G77_256GQTEST_OPERATION_001",
                identity_namespace_prefix="G77_256GQTEST",
                operation_evidence_root=root / "operation",
                transient_root=root / "transient",
            )
            context_path = root / "context.json"
            context_path.write_bytes(LAUNCHER.canonical_bytes(context))
            result = {"result": "TEST_ONLY_MATERIALIZATION_BINDING_PASS"}

            def materialize_nested_checkout(**arguments):
                arguments["checkout_path"].mkdir(parents=True)
                return result

            with mock.patch.object(
                LAUNCHER,
                "materialize_guest_self_contained_checkout",
                side_effect=materialize_nested_checkout,
            ) as materialize:
                observed = LAUNCHER.materialize_operation_state(
                    repository_root=REPOSITORY_ROOT,
                    context=context,
                    context_source_path=context_path,
                )
            checkout = context["qemu_executable_base_seed_checkout_bindings"]["checkout"]
            materialize.assert_called_once_with(
                source_repository=REPOSITORY_ROOT,
                checkout_path=Path(checkout["path"]),
                expected_head=checkout["head"],
                expected_tree=checkout["tree"],
            )
            self.assertEqual(observed["checkout_materialization"], result)
            self.assertEqual(observed["qemu_execution_count"], 0)


if __name__ == "__main__":
    unittest.main()
