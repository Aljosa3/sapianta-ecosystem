#!/usr/bin/env python3
"""Repository-only adversarial tests for the corrected FM admission boundary."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
from pathlib import Path
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


HEAD_A = "a" * 40
TREE_A = "b" * 40
HEAD_B = "c" * 40
TREE_B = "d" * 40
FRESH_HUMAN_SOURCE = "e" * 64
ARGV = ["/usr/bin/qemu-system-x86_64", "-nic", "none"]


def sealed_authority(*, head: str = HEAD_A, tree: str = TREE_A) -> dict:
    authorization = {
        "schema_id": LAUNCHER.AUTHORIZATION_SCHEMA,
        "authorization_present": True,
        "authorization_kind": "FRESH_HUMAN_OPERATIONAL_AUTHORIZATION",
        "authorization_source_sha256": FRESH_HUMAN_SOURCE,
        "authorized_generation_identity": LAUNCHER.GENERATION_IDENTITY,
        "authorized_vector": "WRONG_ATTEMPT",
        "authorized_repository_head": head,
        "authorized_repository_tree": tree,
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


def file_sha(authority: dict) -> str:
    return hashlib.sha256(LAUNCHER.canonical_bytes(authority)).hexdigest()


def reseal(authority: dict) -> dict:
    authority["authorization_sha256"] = LAUNCHER.authority_sha256(authority["authorization"])
    return authority


def admit(authority: dict, **changes):
    arguments = {
        "authority": authority,
        "authority_file_sha256": file_sha(authority),
        "supplied_authority_sha256": file_sha(authority),
        "observed_head": HEAD_A,
        "observed_tree": TREE_A,
        "anchor_is_ancestor": True,
        "repository_clean": True,
        "observed_asset_sha256": dict(LAUNCHER.EXPECTED_ASSET_SHA256),
        "argv": list(ARGV),
        "canonical_argv_sha256": LAUNCHER.CANONICAL_ARGV_SHA256,
        "receipt_namespace_consumed": False,
    }
    arguments.update(changes)
    return LAUNCHER.validate_execution_admission(**arguments)


class G77256FOExecutionAdmissionTests(unittest.TestCase):
    def assert_denied(self, authority: dict, **changes) -> None:
        with self.assertRaises(RuntimeError):
            admit(authority, **changes)

    def test_case_01_wrong_committed_constitutional_authority_denied(self):
        self.assert_denied(sealed_authority(), observed_head="f" * 40)

    def test_case_02_wrong_candidate_identity_denied(self):
        authority = sealed_authority()
        authority["authorization"]["authorized_candidate_sha256"] = "0" * 64
        self.assert_denied(reseal(authority))

    def test_case_03_wrong_materialization_or_asset_identity_denied(self):
        authority = sealed_authority()
        authority["authorization"]["authorized_materialization_sha256"] = "0" * 64
        self.assert_denied(reseal(authority))
        assets = dict(LAUNCHER.EXPECTED_ASSET_SHA256)
        assets[LAUNCHER.OVERLAY] = "0" * 64
        self.assert_denied(sealed_authority(), observed_asset_sha256=assets)

    def test_case_04_modified_canonical_argv_denied(self):
        self.assert_denied(sealed_authority(), canonical_argv_sha256="0" * 64)

    def test_case_05_network_enabled_argv_denied(self):
        self.assert_denied(
            sealed_authority(),
            argv=["/usr/bin/qemu-system-x86_64", "-nic", "user"],
        )

    def test_case_06_wrong_wrapper_or_adapter_binding_denied(self):
        authority = sealed_authority()
        authority["authorization"]["authorized_wrapper_sha256"] = "0" * 64
        self.assert_denied(reseal(authority))
        authority = sealed_authority()
        authority["authorization"]["authorized_fk_adapter_sha256"] = "0" * 64
        self.assert_denied(reseal(authority))

    def test_case_07_consumed_one_shot_receipt_state_denied(self):
        self.assert_denied(sealed_authority(), receipt_namespace_consumed=True)

    def test_case_08_missing_human_operational_authority_denied(self):
        authority = sealed_authority()
        authority["authorization"]["authorization_present"] = False
        self.assert_denied(reseal(authority))
        authority = sealed_authority()
        authority["authorization"]["authorization_source_sha256"] = (
            LAUNCHER.FO_REPOSITORY_ONLY_AUTHORIZATION_SHA256
        )
        self.assert_denied(reseal(authority))

    def test_case_09_malformed_or_unknown_required_field_denied(self):
        authority = sealed_authority()
        del authority["authorization"]["authorized_vector"]
        self.assert_denied(reseal(authority))
        authority = sealed_authority()
        authority["authorization"]["unknown_authority_field"] = "UNKNOWN"
        self.assert_denied(reseal(authority))
        authority = sealed_authority()
        authority["authorization"]["authorization_kind"] = "UNKNOWN"
        self.assert_denied(reseal(authority))

    def test_case_10_exact_valid_state_admits_to_boot_boundary_only(self):
        result = admit(sealed_authority())
        self.assertEqual(result["result"], "ADMIT_TO_BOOT_BOUNDARY_ONLY")

    def test_post_commit_authority_binding_stability(self):
        before = admit(sealed_authority(head=HEAD_A, tree=TREE_A))
        after_authority = sealed_authority(head=HEAD_B, tree=TREE_B)
        after = admit(
            after_authority,
            observed_head=HEAD_B,
            observed_tree=TREE_B,
        )
        self.assertEqual(before["result"], "ADMIT_TO_BOOT_BOUNDARY_ONLY")
        self.assertEqual(after["result"], "ADMIT_TO_BOOT_BOUNDARY_ONLY")
        self.assertEqual(
            before["constitutional_anchor_head"],
            after["constitutional_anchor_head"],
        )
        self.assertNotEqual(
            before["authorized_repository_head"],
            after["authorized_repository_head"],
        )
        self.assert_denied(
            copy.deepcopy(after_authority),
            observed_head="f" * 40,
            observed_tree=TREE_B,
        )


if __name__ == "__main__":
    unittest.main()
