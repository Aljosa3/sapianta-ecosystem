#!/usr/bin/env python3
"""Repository-only GP proof matrix for the FM/FY -> ER checkout boundary."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[5]
LAUNCHER_PATH = REPOSITORY_ROOT / (
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)


def load_launcher():
    spec = importlib.util.spec_from_file_location("g77_256gp_existing_fm_owner", LAUNCHER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("FM owner import unavailable")
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
    git(root, "config", "user.name", "GP Test")
    git(root, "config", "user.email", "gp@example.invalid")
    (root / "tracked.txt").write_text("guest-readable\n", encoding="utf-8")
    git(root, "add", "tracked.txt")
    git(root, "commit", "-q", "-m", "self-contained fixture")
    git(root, "checkout", "-q", "--detach")
    return git(root, "rev-parse", "HEAD"), git(root, "rev-parse", "HEAD^{tree}")


def context_for(
    checkout: Path,
    *,
    head: str,
    tree: str,
    export: Path | None = None,
    mount_tag: str = "aigol_checkout",
) -> dict:
    export_root = checkout if export is None else export
    argument = (
        f"local,path={export_root},mount_tag={mount_tag},"
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


class GuestCheckoutTreePreconditionTests(unittest.TestCase):
    def test_self_contained_checkout_is_accepted(self):
        with tempfile.TemporaryDirectory(prefix="g77_256gp_positive_") as temporary:
            checkout = Path(temporary) / "checkout"
            head, tree = create_repository(checkout)
            proof = LAUNCHER.validate_checkout_preboot_readiness(
                context_for(checkout, head=head, tree=tree)
            )["preauth_guest_checkout_tree_authentication"]
            self.assertEqual(
                proof["result"], "PREAUTH_GUEST_CHECKOUT_TREE_AUTHENTICATION_PASS"
            )
            self.assertEqual(proof["observed_head"], head)
            self.assertEqual(proof["observed_tree"], tree)
            self.assertEqual(proof["guest_destination"], "/mnt/aigol")
            self.assertEqual(proof["required_object_reachability"], "GUEST_LOCAL_ONLY")

    def test_shared_clone_external_alternate_is_rejected(self):
        with tempfile.TemporaryDirectory(prefix="g77_256gp_alternate_") as temporary:
            root = Path(temporary)
            source = root / "source"
            head, tree = create_repository(source)
            checkout = root / "checkout"
            git(root, "clone", "-q", "--shared", str(source), str(checkout))
            git(checkout, "checkout", "-q", "--detach", head)
            with self.assertRaisesRegex(RuntimeError, "alternate escapes presentation root"):
                LAUNCHER.prove_guest_checkout_tree_precondition(
                    context_for(checkout, head=head, tree=tree)
                )

    def test_missing_checkout_and_missing_git_are_rejected(self):
        with tempfile.TemporaryDirectory(prefix="g77_256gp_missing_") as temporary:
            root = Path(temporary)
            missing = root / "missing"
            with self.assertRaisesRegex(RuntimeError, "checkout missing"):
                LAUNCHER.validate_checkout_preboot_readiness(
                    context_for(missing, head="0" * 40, tree="1" * 40)
                )
            plain = root / "plain"
            plain.mkdir()
            with self.assertRaisesRegex(RuntimeError, r"\.git missing"):
                LAUNCHER.prove_guest_checkout_tree_precondition(
                    context_for(plain, head="0" * 40, tree="1" * 40)
                )

    def test_malformed_and_unreachable_gitfiles_are_rejected(self):
        with tempfile.TemporaryDirectory(prefix="g77_256gp_gitfile_") as temporary:
            root = Path(temporary)
            malformed = root / "malformed"
            malformed.mkdir()
            (malformed / ".git").write_text("not-a-gitfile\n", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "gitfile is malformed"):
                LAUNCHER.prove_guest_checkout_tree_precondition(
                    context_for(malformed, head="0" * 40, tree="1" * 40)
                )
            unreachable = root / "unreachable"
            unreachable.mkdir()
            (unreachable / ".git").write_text("gitdir: missing\n", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "gitdir is unreachable"):
                LAUNCHER.prove_guest_checkout_tree_precondition(
                    context_for(unreachable, head="0" * 40, tree="1" * 40)
                )

    def test_unreachable_common_dir_and_missing_head_are_rejected(self):
        with tempfile.TemporaryDirectory(prefix="g77_256gp_metadata_") as temporary:
            root = Path(temporary)
            common = root / "common"
            (common / ".git").mkdir(parents=True)
            (common / ".git" / "commondir").write_text("../missing\n", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "common-dir is unreachable"):
                LAUNCHER.prove_guest_checkout_tree_precondition(
                    context_for(common, head="0" * 40, tree="1" * 40)
                )
            missing_head = root / "missing-head"
            (missing_head / ".git" / "objects").mkdir(parents=True)
            with self.assertRaisesRegex(RuntimeError, "HEAD is missing"):
                LAUNCHER.prove_guest_checkout_tree_precondition(
                    context_for(missing_head, head="0" * 40, tree="1" * 40)
                )

    def test_missing_ref_and_unresolved_head_are_rejected(self):
        with tempfile.TemporaryDirectory(prefix="g77_256gp_head_") as temporary:
            root = Path(temporary)
            missing_ref = root / "missing-ref"
            head, tree = create_repository(missing_ref)
            (missing_ref / ".git" / "HEAD").write_text(
                "ref: refs/heads/absent\n", encoding="utf-8"
            )
            with self.assertRaisesRegex(RuntimeError, "ER guest Git consumer rejected"):
                LAUNCHER.prove_guest_checkout_tree_precondition(
                    context_for(missing_ref, head=head, tree=tree)
                )
            unresolved = root / "unresolved"
            _, unresolved_tree = create_repository(unresolved)
            (unresolved / ".git" / "HEAD").write_text("f" * 40 + "\n", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "ER guest Git consumer rejected"):
                LAUNCHER.prove_guest_checkout_tree_precondition(
                    context_for(unresolved, head="f" * 40, tree=unresolved_tree)
                )

    def test_missing_tree_object_and_wrong_tree_are_rejected(self):
        with tempfile.TemporaryDirectory(prefix="g77_256gp_tree_") as temporary:
            root = Path(temporary)
            missing_object = root / "missing-object"
            head, tree = create_repository(missing_object)
            tree_object = missing_object / ".git" / "objects" / tree[:2] / tree[2:]
            self.assertTrue(tree_object.is_file())
            tree_object.unlink()
            with self.assertRaisesRegex(RuntimeError, "ER guest Git consumer rejected"):
                LAUNCHER.prove_guest_checkout_tree_precondition(
                    context_for(missing_object, head=head, tree=tree)
                )
            wrong = root / "wrong"
            wrong_head, _ = create_repository(wrong)
            with self.assertRaisesRegex(RuntimeError, "resolved wrong TREE"):
                LAUNCHER.prove_guest_checkout_tree_precondition(
                    context_for(wrong, head=wrong_head, tree="0" * 40)
                )

    def test_stale_checkout_and_stale_evidence_reuse_are_rejected(self):
        with tempfile.TemporaryDirectory(prefix="g77_256gp_stale_") as temporary:
            checkout = Path(temporary) / "checkout"
            head, tree = create_repository(checkout)
            context = context_for(checkout, head=head, tree=tree)
            LAUNCHER.prove_guest_checkout_tree_precondition(context)
            (checkout / "tracked.txt").write_text("stale\n", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "stale or dirty"):
                LAUNCHER.prove_guest_checkout_tree_precondition(context)

    def test_wrong_source_presentation_and_mount_tag_are_rejected(self):
        with tempfile.TemporaryDirectory(prefix="g77_256gp_binding_") as temporary:
            root = Path(temporary)
            checkout = root / "checkout"
            head, tree = create_repository(checkout)
            alias = root / "alias"
            alias.symlink_to(checkout, target_is_directory=True)
            with self.assertRaisesRegex(RuntimeError, "presentation root is not canonical"):
                LAUNCHER.prove_guest_checkout_tree_precondition(
                    context_for(alias, head=head, tree=tree)
                )
            with self.assertRaisesRegex(RuntimeError, "presentation binding mismatch"):
                LAUNCHER.prove_guest_checkout_tree_precondition(
                    context_for(checkout, head=head, tree=tree, export=root)
                )
            with self.assertRaisesRegex(RuntimeError, "presentation binding mismatch"):
                LAUNCHER.prove_guest_checkout_tree_precondition(
                    context_for(checkout, head=head, tree=tree, mount_tag="wrong")
                )

    def test_wrong_guest_destination_and_caller_readiness_override_are_rejected(self):
        cloud = (REPOSITORY_ROOT / LAUNCHER.CLOUD_INIT).read_text(encoding="utf-8")
        er = (REPOSITORY_ROOT / LAUNCHER.ER_HARNESS_RELATIVE).read_text(encoding="utf-8")
        with self.assertRaisesRegex(RuntimeError, "guest destination mount binding mismatch"):
            LAUNCHER._validate_guest_destination_sources(
                cloud.replace("/mnt/aigol", "/mnt/wrong"), er
            )
        with tempfile.TemporaryDirectory(prefix="g77_256gp_override_") as temporary:
            checkout = Path(temporary) / "checkout"
            head, tree = create_repository(checkout)
            context = context_for(checkout, head=head, tree=tree)
            context["guest_checkout_ready"] = True
            with self.assertRaisesRegex(RuntimeError, "readiness override prohibited"):
                LAUNCHER.prove_guest_checkout_tree_precondition(context)

    def test_http_and_malformed_alternates_are_rejected(self):
        with tempfile.TemporaryDirectory(prefix="g77_256gp_alt_metadata_") as temporary:
            root = Path(temporary)
            http = root / "http"
            head, tree = create_repository(http)
            (http / ".git" / "objects" / "info" / "http-alternates").write_text(
                "https://example.invalid/objects\n", encoding="utf-8"
            )
            with self.assertRaisesRegex(RuntimeError, "HTTP object alternates"):
                LAUNCHER.prove_guest_checkout_tree_precondition(
                    context_for(http, head=head, tree=tree)
                )
            malformed = root / "malformed"
            malformed_head, malformed_tree = create_repository(malformed)
            (malformed / ".git" / "objects" / "info" / "alternates").write_text(
                "\n", encoding="utf-8"
            )
            with self.assertRaisesRegex(RuntimeError, "alternates metadata is malformed"):
                LAUNCHER.prove_guest_checkout_tree_precondition(
                    context_for(malformed, head=malformed_head, tree=malformed_tree)
                )

    def test_git_metadata_symlink_escape_is_rejected(self):
        with tempfile.TemporaryDirectory(prefix="g77_256gp_symlink_") as temporary:
            root = Path(temporary)
            checkout = root / "checkout"
            head, tree = create_repository(checkout)
            head_object = checkout / ".git" / "objects" / head[:2] / head[2:]
            external = root / "external-object"
            head_object.rename(external)
            head_object.symlink_to(external)
            with self.assertRaisesRegex(RuntimeError, "metadata symlink prohibited"):
                LAUNCHER.prove_guest_checkout_tree_precondition(
                    context_for(checkout, head=head, tree=tree)
                )


if __name__ == "__main__":
    unittest.main()
