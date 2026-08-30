#!/usr/bin/env python3
"""Context-bound FO pure-admission regression tests."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[5]
LAUNCHER_PATH = REPOSITORY_ROOT / (
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
SPEC = importlib.util.spec_from_file_location("g77_256fo_context_owner", LAUNCHER_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("FM launcher import failed")
LAUNCHER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(LAUNCHER)
PREFIX = "G77_256FOTEST01"


def context_for(root: Path, head: str = "a" * 40, tree: str = "b" * 40) -> dict:
    return LAUNCHER.build_operation_context(
        repository_root=REPOSITORY_ROOT,
        repository_head=head,
        repository_tree=tree,
        generation_identity=PREFIX + "_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_ATTEMPT_OPERATIONAL_COMMISSIONING_V1",
        operation_identity=PREFIX + "_OPERATION_001",
        identity_namespace_prefix=PREFIX,
        operation_evidence_root=root / "operation",
        transient_root=root / "transient",
    )


def sealed_authority(context: dict) -> dict:
    authorization = {
        "schema_id": LAUNCHER.AUTHORIZATION_SCHEMA,
        "authorization_present": True,
        "authorization_kind": "FRESH_HUMAN_OPERATIONAL_AUTHORIZATION",
        "authorization_source_sha256": "e" * 64,
        "authorized_context_sha256": context["context_sha256"],
        "authorized_operation_identity": context["operation_identity"],
        "authorized_generation_identity": context["generation_identity"],
        "authorized_vector": "WRONG_ATTEMPT",
        "authorized_repository_head": context["repository_head"],
        "authorized_repository_tree": context["repository_tree"],
        "authorized_constitutional_anchor_head": LAUNCHER.CONSTITUTIONAL_ANCHOR_HEAD,
        "authorized_candidate_sha256": context["candidate_manifest_sha256"],
        "authorized_canonical_argv_sha256": context["canonical_argv_sha256"],
        "authorized_wrapper_sha256": context["wrapper_fc_er_che_schema_hashes"]["wrapper"],
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


def reseal(authority: dict) -> dict:
    authority["authorization_sha256"] = LAUNCHER.authority_sha256(authority["authorization"])
    return authority


def admit(context: dict, authority: dict, **changes):
    file_sha = hashlib.sha256(LAUNCHER.canonical_bytes(authority)).hexdigest()
    arguments = {
        "context": context,
        "authority": authority,
        "authority_file_sha256": file_sha,
        "supplied_authority_sha256": file_sha,
        "observed_head": context["repository_head"],
        "observed_tree": context["repository_tree"],
        "anchor_is_ancestor": True,
        "repository_clean": True,
        "observed_asset_sha256": LAUNCHER.context_asset_expectations(context),
        "argv": context["canonical_argv"],
        "canonical_argv_sha256": context["canonical_argv_sha256"],
        "receipt_namespace_consumed": False,
    }
    arguments.update(changes)
    return LAUNCHER.validate_execution_admission(**arguments)


class G77256FOExecutionAdmissionTests(unittest.TestCase):
    def test_exact_test_only_non_authority_fixture_admits_to_boundary_only(self):
        with tempfile.TemporaryDirectory(prefix="g77_256fo_positive_") as temporary:
            context = context_for(Path(temporary))
            result = admit(context, sealed_authority(context))
            self.assertEqual(result["result"], "ADMIT_TO_BOOT_BOUNDARY_ONLY")

    def test_context_head_tree_candidate_wrapper_and_argv_mismatches_denied(self):
        fields = (
            "authorized_context_sha256",
            "authorized_repository_head",
            "authorized_repository_tree",
            "authorized_candidate_sha256",
            "authorized_wrapper_sha256",
            "authorized_canonical_argv_sha256",
        )
        for field in fields:
            with self.subTest(field=field), tempfile.TemporaryDirectory(prefix="g77_256fo_binding_") as temporary:
                context = context_for(Path(temporary))
                authority = sealed_authority(context)
                authority["authorization"][field] = ("0" * 40 if field.endswith(("head", "tree")) else "0" * 64)
                with self.assertRaises(RuntimeError):
                    admit(context, reseal(authority))

    def test_no_network_one_shot_and_unconsumed_namespace_enforced(self):
        with tempfile.TemporaryDirectory(prefix="g77_256fo_policy_") as temporary:
            context = context_for(Path(temporary))
            authority = sealed_authority(context)
            for field, value in (
                ("network_authorized", True),
                ("retry_limit", 1),
                ("repair_limit", 1),
                ("replay_limit", 1),
                ("authorization_reusable", True),
            ):
                with self.subTest(field=field):
                    mutated = copy.deepcopy(authority)
                    mutated["authorization"][field] = value
                    with self.assertRaises(RuntimeError):
                        admit(context, reseal(mutated))
            with self.assertRaises(RuntimeError):
                admit(context, authority, receipt_namespace_consumed=True)
            network_argv = list(context["canonical_argv"])
            network_argv[network_argv.index("-nic") + 1] = "user"
            with self.assertRaises(RuntimeError):
                admit(context, authority, argv=network_argv)

    def test_missing_unknown_old_fy_and_spent_authorities_denied(self):
        with tempfile.TemporaryDirectory(prefix="g77_256fo_schema_") as temporary:
            context = context_for(Path(temporary))
            baseline = sealed_authority(context)
            mutations = []
            missing = copy.deepcopy(baseline)
            del missing["authorization"]["authorized_context_sha256"]
            mutations.append(reseal(missing))
            unknown = copy.deepcopy(baseline)
            unknown["authorization"]["unknown"] = True
            mutations.append(reseal(unknown))
            old_fy = copy.deepcopy(baseline)
            old_fy["schema_id"] = "G77_256FY_EXECUTION_TIME_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1"
            mutations.append(old_fy)
            spent = copy.deepcopy(baseline)
            spent["authorization"]["authorization_source_sha256"] = LAUNCHER.FN_SPENT_AUTHORIZATION_SHA256
            mutations.append(reseal(spent))
            for authority in mutations:
                with self.assertRaises(RuntimeError):
                    admit(context, authority)

    def test_post_commit_context_binding_stability(self):
        with tempfile.TemporaryDirectory(prefix="g77_256fo_commit_") as temporary:
            root = Path(temporary)
            before = context_for(root / "before", "a" * 40, "b" * 40)
            after = context_for(root / "after", "c" * 40, "d" * 40)
            self.assertEqual(admit(before, sealed_authority(before))["result"], "ADMIT_TO_BOOT_BOUNDARY_ONLY")
            self.assertEqual(admit(after, sealed_authority(after))["result"], "ADMIT_TO_BOOT_BOUNDARY_ONLY")
            with self.assertRaises(RuntimeError):
                admit(after, sealed_authority(after), observed_head="f" * 40)


if __name__ == "__main__":
    unittest.main()
