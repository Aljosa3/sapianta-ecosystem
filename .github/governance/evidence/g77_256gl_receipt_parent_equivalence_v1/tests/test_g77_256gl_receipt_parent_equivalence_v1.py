#!/usr/bin/env python3
"""Positive and fail-closed GL receipt-parent equivalence proofs."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[5]
ORCHESTRATOR_PATH = REPOSITORY_ROOT / (
    ".github/governance/evidence/g77_256gl_receipt_parent_equivalence_v1/"
    "orchestration/G77_256GL_RECEIPT_PARENT_PREAUTHORIZATION_BINDING_V1.py"
)
OWNER_PATH = REPOSITORY_ROOT / (
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
PROOF_PATH = REPOSITORY_ROOT / (
    ".github/governance/evidence/g77_256gl_receipt_parent_equivalence_v1/"
    "G77_256GL_ROOT_CAUSE_EQUIVALENCE_AND_REUSE_PROOF_V1.json"
)
GK_REDUCTION_PATH = REPOSITORY_ROOT / (
    ".github/governance/evidence/g77_256gk_wrong_attempt_operational_v1/"
    "G77_256GK_SPCE_FINAL_FAIL_CLOSED_REDUCTION_V1.json"
)
GK_VERDICT = (
    "FAIL_CLOSED__G77_256GK_POST_AUTHORITY_PRE_LAUNCHER_FINAL_ADMISSION_FAILED__"
    "DURABLE_RECEIPT_PARENT_ABSENT__EXISTING_GA_OWNER_NOT_INVOKED_BEFORE_SEAL__"
    "AUTHORITY_CONSUMED_AND_NON_REUSABLE__NO_PRE__NO_QEMU__NO_P11_ENTRY__"
    "NO_RETRY_REPAIR_REPLAY__E05_REMAINS_6_OF_18__HUMAN_REVIEW_REQUIRED"
)


def load(path: Path, name: str):
    specification = importlib.util.spec_from_file_location(name, path)
    if specification is None or specification.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


GL = load(ORCHESTRATOR_PATH, "g77_256gl_orchestration")
FM = load(OWNER_PATH, "g77_256gl_existing_fm_owner")


def context_for(root: Path, prefix: str) -> dict:
    root.mkdir(parents=True, exist_ok=True)
    context = FM.build_operation_context(
        repository_root=REPOSITORY_ROOT,
        repository_head="a" * 40,
        repository_tree="b" * 40,
        generation_identity=(
            prefix
            + "_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_ATTEMPT_OPERATIONAL_COMMISSIONING_V1"
        ),
        operation_identity=prefix + "_OPERATION_001",
        identity_namespace_prefix=prefix,
        operation_evidence_root=root / "operation",
        transient_root=root / "transient",
    )
    Path(context["operation_evidence_root"]).mkdir()
    return context


def reseal_context(context: dict) -> None:
    unsealed = {key: value for key, value in context.items() if key != "context_sha256"}
    context["context_sha256"] = hashlib.sha256(FM.canonical_bytes(unsealed)).hexdigest()


def reseal_claim(claim: dict) -> None:
    claim["observation_sha256"] = hashlib.sha256(
        FM.canonical_bytes(claim["observation"])
    ).hexdigest()


def reseal_checkpoint(checkpoint: dict) -> None:
    checkpoint["checkpoint_sha256"] = hashlib.sha256(
        FM.canonical_bytes(checkpoint["checkpoint"])
    ).hexdigest()


class G77256GLPositiveProofs(unittest.TestCase):
    def prove_namespace(self, root: Path, prefix: str):
        context = context_for(root, prefix)
        claim = GL.prepare_and_observe_receipt_parent(REPOSITORY_ROOT, context)
        checkpoint = GL.reduce_preauthorization_checkpoint(
            REPOSITORY_ROOT, context, claim
        )
        result = GL.validate_preauth_final_admission_equivalence(
            REPOSITORY_ROOT, context, claim, checkpoint
        )
        self.assertTrue(checkpoint["checkpoint"]["receipt_parent_ready"])
        self.assertEqual(
            result["preauth_final_admission_equivalence"], GL.EQUIVALENCE_RESULT
        )
        self.assertEqual(result["repeated_observation"], "IDENTICAL")
        self.assertEqual(result["human_constitutional_authorization_count"], 0)
        self.assertEqual(result["operational_execution_count"], 0)
        return context, claim, checkpoint

    def test_fresh_namespace_a_and_b_generalize_without_historical_reuse(self):
        with tempfile.TemporaryDirectory(prefix="g77_256gl_positive_") as temporary:
            root = Path(temporary)
            context_a, claim_a, _ = self.prove_namespace(root / "a", "G77_256GLTESTA")
            context_b, claim_b, _ = self.prove_namespace(root / "b", "G77_256GLTESTB")
            self.assertNotEqual(context_a["operation_identity"], context_b["operation_identity"])
            self.assertNotEqual(claim_a["observation_sha256"], claim_b["observation_sha256"])

    def test_preparation_validation_checkpoint_and_fo_use_existing_owner(self):
        source = ORCHESTRATOR_PATH.read_text(encoding="utf-8")
        owner_source = OWNER_PATH.read_text(encoding="utf-8")
        self.assertIn("owner.prepare_receipt_parent(repository_root, context)", source)
        self.assertGreaterEqual(
            source.count("owner.validate_receipt_parent_ready"), 3
        )
        self.assertIn(
            "receipt_readiness = validate_receipt_parent_ready(repository_root, context)",
            owner_source,
        )
        self.assertNotIn("subprocess.run", source)
        self.assertNotIn("qemu-system", source)


class G77256GLHistoricalAndSealProofs(unittest.TestCase):
    def test_exact_gk_terminal_result_and_consumed_authority_reauthenticate(self):
        raw = GK_REDUCTION_PATH.read_bytes()
        self.assertEqual(
            hashlib.sha256(raw).hexdigest(),
            "bb17c5bd97e9453586aae7612e6d0213f6e4b20c27633d65211b5cb233011727",
        )
        envelope = json.loads(raw)
        reduction = envelope["reduction"]
        self.assertEqual(
            envelope["reduction_sha256"],
            hashlib.sha256(FM.canonical_bytes(reduction)).hexdigest(),
        )
        self.assertEqual(reduction["verdict"], GK_VERDICT)
        self.assertEqual(
            reduction["terminal_failure"]["first_broken_edge"],
            "GK_SEALED_RECEIPT_PARENT_READY_CLAIM_TO_FO_VALIDATE_RECEIPT_PARENT_READY",
        )
        self.assertTrue(reduction["preauthorization"]["sealed_receipt_parent_ready_claim"])
        self.assertFalse(
            reduction["preauthorization"]["observed_receipt_parent_exists_at_final_admission"]
        )
        authority = reduction["human_authority"]
        self.assertTrue(authority["authorization_consumed"])
        self.assertFalse(authority["authorization_reusable"])
        self.assertFalse(authority["authorization_transferable"])
        counters = reduction["operational_counters"]
        self.assertEqual(counters["human_constitutional_authorization_count"], 1)
        for field in (
            "governed_launcher_activations",
            "qemu_execution_count",
            "vm_boot_count",
            "pre_count",
            "post_count",
            "wrong_attempt_execution_count",
            "request_count",
            "p11_entry_count",
            "protected_invocation_count",
            "protected_effect_count",
            "retry_count",
            "repair_execution_count",
            "replay_execution_count",
        ):
            self.assertEqual(counters[field], 0, field)
        self.assertEqual(reduction["ex"]["reused"], "17/17")
        self.assertEqual(reduction["ex"]["reconstructed"], 0)
        self.assertEqual(reduction["e05"]["before"], "6/18")
        self.assertEqual(reduction["e05"]["after"], "6/18")

    def test_gl_proof_seal_owner_contract_and_zero_counters(self):
        envelope = json.loads(PROOF_PATH.read_bytes())
        proof = envelope["proof"]
        self.assertEqual(
            envelope["proof_sha256"],
            hashlib.sha256(FM.canonical_bytes(proof)).hexdigest(),
        )
        self.assertEqual(
            proof["equivalence"]["preauth_final_admission_equivalence"],
            GL.EQUIVALENCE_RESULT,
        )
        self.assertEqual(
            proof["same_class_review"]["classification"],
            "NO_ADDITIONAL_INSTANCE_FOUND_WITHIN_REVIEWED_BOUNDARY",
        )
        self.assertEqual(proof["reuse"]["ex_reused"], "17/17")
        self.assertEqual(proof["reuse"]["ex_reconstructed"], 0)
        self.assertTrue(
            all(value == 0 for value in proof["operational_counters"].values())
        )
        self.assertEqual(proof["architecture_counters"]["production_route_delta"], 0)
        self.assertEqual(proof["e05"]["before"], proof["e05"]["after"])


class G77256GLNegativeProofs(unittest.TestCase):
    def test_absent_symlink_non_directory_and_unexpected_content_fail_closed(self):
        for case in ("absent", "symlink", "file", "content"):
            with self.subTest(case=case), tempfile.TemporaryDirectory(
                prefix=f"g77_256gl_{case}_"
            ) as temporary, tempfile.TemporaryDirectory(
                prefix="g77_256gl_target_"
            ) as target:
                context = context_for(Path(temporary), "G77_256GLNEG01")
                parent = Path(context["receipt_parent"])
                if case == "absent":
                    with self.assertRaises(RuntimeError):
                        FM.validate_receipt_parent_ready(REPOSITORY_ROOT, context)
                    continue
                if case == "symlink":
                    parent.symlink_to(Path(target), target_is_directory=True)
                elif case == "file":
                    parent.write_text("not a directory", encoding="utf-8")
                else:
                    parent.mkdir()
                    (parent / "unexpected").write_text("occupied", encoding="utf-8")
                with self.assertRaises((RuntimeError, ValueError)):
                    GL.prepare_and_observe_receipt_parent(REPOSITORY_ROOT, context)

    def test_wrong_operation_context_path_and_other_namespace_fail_closed(self):
        with tempfile.TemporaryDirectory(prefix="g77_256gl_bindings_") as temporary:
            root = Path(temporary)
            context_a = context_for(root / "a", "G77_256GLNEGA")
            context_b = context_for(root / "b", "G77_256GLNEGB")
            claim_a = GL.prepare_and_observe_receipt_parent(REPOSITORY_ROOT, context_a)
            GL.prepare_and_observe_receipt_parent(REPOSITORY_ROOT, context_b)
            for field, value in (
                ("operation_identity", context_b["operation_identity"]),
                ("context_sha256", context_b["context_sha256"]),
                ("receipt_parent", context_b["receipt_parent"]),
            ):
                with self.subTest(field=field):
                    forged = copy.deepcopy(claim_a)
                    forged["observation"][field] = value
                    reseal_claim(forged)
                    with self.assertRaisesRegex(RuntimeError, "binding mismatch"):
                        GL.validate_bound_observation(
                            REPOSITORY_ROOT, context_a, forged
                        )
            with self.assertRaisesRegex(RuntimeError, "binding mismatch"):
                GL.validate_bound_observation(REPOSITORY_ROOT, context_b, claim_a)

    def test_stale_historical_namespace_is_rejected_by_existing_context_owner(self):
        with tempfile.TemporaryDirectory(prefix="g77_256gl_stale_") as temporary:
            context = context_for(Path(temporary), "G77_256GLFRESH")
            context["identity_namespace_prefix"] = "G77_256FM"
            context["generation_identity"] = "G77_256FM_REUSED"
            context["operation_identity"] = "G77_256FM_OPERATION_001"
            reseal_context(context)
            with self.assertRaises((RuntimeError, ValueError)):
                GL.prepare_and_observe_receipt_parent(REPOSITORY_ROOT, context)

    def test_checkpoint_ready_cannot_survive_absence_validation_failure_or_forgery(self):
        with tempfile.TemporaryDirectory(prefix="g77_256gl_checkpoint_") as temporary:
            context = context_for(Path(temporary), "G77_256GLNEG02")
            claim = GL.prepare_and_observe_receipt_parent(REPOSITORY_ROOT, context)
            checkpoint = GL.reduce_preauthorization_checkpoint(
                REPOSITORY_ROOT, context, claim
            )
            Path(context["receipt_parent"]).rmdir()
            with self.assertRaises(RuntimeError):
                GL.validate_preauth_final_admission_equivalence(
                    REPOSITORY_ROOT, context, claim, checkpoint
                )

        with tempfile.TemporaryDirectory(prefix="g77_256gl_forged_") as temporary:
            context = context_for(Path(temporary), "G77_256GLNEG03")
            claim = GL.prepare_and_observe_receipt_parent(REPOSITORY_ROOT, context)
            forged = copy.deepcopy(claim)
            forged["observation"]["receipt_parent_ready"] = False
            reseal_claim(forged)
            with self.assertRaisesRegex(RuntimeError, "did not establish"):
                GL.reduce_preauthorization_checkpoint(REPOSITORY_ROOT, context, forged)

    def test_validation_against_another_path_and_state_change_fail_closed(self):
        with tempfile.TemporaryDirectory(prefix="g77_256gl_drift_") as temporary:
            context = context_for(Path(temporary), "G77_256GLNEG04")
            claim = GL.prepare_and_observe_receipt_parent(REPOSITORY_ROOT, context)
            checkpoint = GL.reduce_preauthorization_checkpoint(
                REPOSITORY_ROOT, context, claim
            )
            parent = Path(context["receipt_parent"])
            marker = parent / "state-change"
            marker.write_text("changed", encoding="utf-8")
            marker.unlink()
            with self.assertRaisesRegex(RuntimeError, "state changed"):
                GL.validate_preauth_final_admission_equivalence(
                    REPOSITORY_ROOT, context, claim, checkpoint
                )

    def test_checkpoint_forged_ready_and_observation_hash_mismatch_fail_closed(self):
        with tempfile.TemporaryDirectory(prefix="g77_256gl_forged_checkpoint_") as temporary:
            context = context_for(Path(temporary), "G77_256GLNEG05")
            claim = GL.prepare_and_observe_receipt_parent(REPOSITORY_ROOT, context)
            checkpoint = GL.reduce_preauthorization_checkpoint(
                REPOSITORY_ROOT, context, claim
            )
            forged = copy.deepcopy(checkpoint)
            forged["checkpoint"]["receipt_parent_observation_sha256"] = "0" * 64
            reseal_checkpoint(forged)
            with self.assertRaisesRegex(RuntimeError, "binding mismatch"):
                GL.validate_preauth_final_admission_equivalence(
                    REPOSITORY_ROOT, context, claim, forged
                )

            unknown = copy.deepcopy(checkpoint)
            unknown["checkpoint"]["free_standing_ready"] = True
            reseal_checkpoint(unknown)
            with self.assertRaisesRegex(RuntimeError, "checkpoint malformed"):
                GL.validate_preauth_final_admission_equivalence(
                    REPOSITORY_ROOT, context, claim, unknown
                )

            unsealed = copy.deepcopy(claim)
            unsealed["observation"]["operation_identity"] = "G77_256GLNEG05_OTHER"
            with self.assertRaisesRegex(RuntimeError, "seal mismatch"):
                GL.validate_bound_observation(REPOSITORY_ROOT, context, unsealed)


if __name__ == "__main__":
    unittest.main()
