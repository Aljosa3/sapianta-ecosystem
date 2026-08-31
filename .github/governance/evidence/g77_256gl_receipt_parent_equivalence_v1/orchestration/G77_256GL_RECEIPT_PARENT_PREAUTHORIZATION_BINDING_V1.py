#!/usr/bin/env python3
"""Bind preauthorization receipt readiness to the existing GA/FM owner.

This module is repository-only orchestration evidence.  It creates no Human
authority and has no launcher, QEMU, P11, receipt-writing, or production-route
capability.  Preparation and validation remain owned by the certified FM
launcher implementation introduced through GA/GD.
"""

from __future__ import annotations

import hashlib
import importlib.util
import os
from pathlib import Path
import stat
from types import ModuleType
from typing import Any


OWNER_RELATIVE_PATH = (
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
CLAIM_SCHEMA = "G77_256GL_RECEIPT_PARENT_OBSERVATION_ENVELOPE_V1"
OBSERVATION_SCHEMA = "G77_256GL_RECEIPT_PARENT_OBSERVATION_V1"
CHECKPOINT_SCHEMA = "G77_256GL_PREAUTHORIZATION_CHECKPOINT_ENVELOPE_V1"
CHECKPOINT_INNER_SCHEMA = "G77_256GL_PREAUTHORIZATION_CHECKPOINT_V1"
PREPARATION_OWNER = "EXISTING_FM_PREPARE_RECEIPT_PARENT"
VALIDATION_OWNER = "EXISTING_FM_VALIDATE_RECEIPT_PARENT_READY"
FINAL_ADMISSION_OWNER = (
    "UNCHANGED_FO_VALIDATE_FINAL_ADMISSION_TO_FM_VALIDATE_RECEIPT_PARENT_READY"
)
EQUIVALENCE_RESULT = (
    "VERIFIED_WITHIN_EXACT_REVIEWED_RECEIPT_PARENT_BOUNDARY"
)
CLAIM_DERIVATION = (
    "EXISTING_OWNER_PREPARED_STATE_AND_EXISTING_OWNER_VALIDATED_STATE_"
    "AND_OBSERVED_DURABLE_FILESYSTEM_STATE"
)
OBSERVATION_FIELDS = {
    "schema_id",
    "generation_identity",
    "operation_identity",
    "context_sha256",
    "receipt_parent",
    "receipt_parent_ready",
    "receipt_files_absent",
    "guest_outputs_absent",
    "receipt_namespace_unused",
    "directory_identity",
    "preparation_owner",
    "validation_owner",
    "authority_count",
    "operational_execution_count",
}
CHECKPOINT_FIELDS = {
    "schema_id",
    "generation_identity",
    "operation_identity",
    "context_sha256",
    "receipt_parent",
    "receipt_parent_ready",
    "receipt_parent_observation_sha256",
    "claim_derivation",
    "checkpoint_is_authority",
    "human_constitutional_authorization_count",
    "operational_execution_count",
}


def _load_existing_owner(repository_root: Path) -> ModuleType:
    owner_path = repository_root.resolve() / OWNER_RELATIVE_PATH
    if owner_path.is_symlink() or not owner_path.is_file():
        raise RuntimeError("existing GA/FM receipt-parent owner unavailable")
    specification = importlib.util.spec_from_file_location(
        "g77_256gl_existing_ga_fm_owner", owner_path
    )
    if specification is None or specification.loader is None:
        raise RuntimeError("existing GA/FM receipt-parent owner import failed")
    owner = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(owner)
    return owner


def _canonical_bytes(owner: ModuleType, value: dict[str, Any]) -> bytes:
    return owner.canonical_bytes(value)


def _sealed_hash(owner: ModuleType, value: dict[str, Any]) -> str:
    return hashlib.sha256(_canonical_bytes(owner, value)).hexdigest()


def _directory_identity(parent: Path) -> dict[str, int]:
    """Capture the same no-follow directory object for unchanged-state proof."""

    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(parent, flags)
    try:
        observed = os.fstat(descriptor)
    finally:
        os.close(descriptor)
    if not stat.S_ISDIR(observed.st_mode):
        raise RuntimeError("receipt-parent observation is not a directory")
    return {
        "device": observed.st_dev,
        "inode": observed.st_ino,
        "mode": observed.st_mode,
        "link_count": observed.st_nlink,
        "size": observed.st_size,
        "mtime_ns": observed.st_mtime_ns,
        "ctime_ns": observed.st_ctime_ns,
    }


def _observed_state(
    owner: ModuleType,
    context: dict[str, Any],
    readiness: dict[str, Any],
) -> dict[str, Any]:
    expected_keys = {
        "receipt_parent",
        "receipt_parent_ready",
        "receipt_files_absent",
        "guest_outputs_absent",
        "receipt_namespace_unused",
    }
    if set(readiness) != expected_keys:
        raise RuntimeError("existing receipt-parent owner returned an unknown result shape")
    if not all(
        readiness[field] is True
        for field in (
            "receipt_parent_ready",
            "receipt_files_absent",
            "guest_outputs_absent",
            "receipt_namespace_unused",
        )
    ):
        raise RuntimeError("existing owner did not establish receipt-parent readiness")
    if readiness["receipt_parent"] != context["receipt_parent"]:
        raise RuntimeError("existing owner observed a different receipt parent")
    return {
        "schema_id": OBSERVATION_SCHEMA,
        "generation_identity": context["generation_identity"],
        "operation_identity": context["operation_identity"],
        "context_sha256": context["context_sha256"],
        "receipt_parent": readiness["receipt_parent"],
        "receipt_parent_ready": readiness["receipt_parent_ready"],
        "receipt_files_absent": readiness["receipt_files_absent"],
        "guest_outputs_absent": readiness["guest_outputs_absent"],
        "receipt_namespace_unused": readiness["receipt_namespace_unused"],
        "directory_identity": _directory_identity(Path(readiness["receipt_parent"])),
        "preparation_owner": PREPARATION_OWNER,
        "validation_owner": VALIDATION_OWNER,
        "authority_count": 0,
        "operational_execution_count": 0,
    }


def prepare_and_observe_receipt_parent(
    repository_root: Path,
    context: dict[str, Any],
) -> dict[str, Any]:
    """Invoke the existing preparation owner, validate, then seal observation."""

    owner = _load_existing_owner(repository_root)
    prepared = owner.prepare_receipt_parent(repository_root, context)
    validated = owner.validate_receipt_parent_ready(repository_root, context)
    if prepared != validated:
        raise RuntimeError("preparation and validation observations disagree")
    observation = _observed_state(owner, context, validated)
    return {
        "schema_id": CLAIM_SCHEMA,
        "observation": observation,
        "observation_sha256": _sealed_hash(owner, observation),
    }


def validate_bound_observation(
    repository_root: Path,
    context: dict[str, Any],
    claim: dict[str, Any],
) -> dict[str, Any]:
    """Reobserve one sealed claim using the existing validation owner."""

    owner = _load_existing_owner(repository_root)
    if set(claim) != {"schema_id", "observation", "observation_sha256"}:
        raise RuntimeError("receipt-parent claim envelope fields malformed or unknown")
    if claim["schema_id"] != CLAIM_SCHEMA:
        raise RuntimeError("receipt-parent claim envelope schema mismatch")
    observation = claim["observation"]
    if (
        not isinstance(observation, dict)
        or set(observation) != OBSERVATION_FIELDS
        or observation.get("schema_id") != OBSERVATION_SCHEMA
    ):
        raise RuntimeError("receipt-parent observation malformed")
    if claim["observation_sha256"] != _sealed_hash(owner, observation):
        raise RuntimeError("receipt-parent observation seal mismatch")
    identity_fields = {
        "generation_identity": context["generation_identity"],
        "operation_identity": context["operation_identity"],
        "context_sha256": context["context_sha256"],
        "receipt_parent": context["receipt_parent"],
    }
    for field, expected in identity_fields.items():
        if observation.get(field) != expected:
            raise RuntimeError(f"receipt-parent observation binding mismatch: {field}")
    if not all(
        observation.get(field) is True
        for field in (
            "receipt_parent_ready",
            "receipt_files_absent",
            "guest_outputs_absent",
            "receipt_namespace_unused",
        )
    ):
        raise RuntimeError("bound observation did not establish receipt-parent readiness")
    if observation.get("preparation_owner") != PREPARATION_OWNER:
        raise RuntimeError("receipt-parent preparation owner mismatch")
    if observation.get("validation_owner") != VALIDATION_OWNER:
        raise RuntimeError("receipt-parent validation owner mismatch")
    if observation.get("authority_count") != 0 or observation.get("operational_execution_count") != 0:
        raise RuntimeError("repository-only receipt-parent claim contains operational authority")
    current = _observed_state(
        owner,
        context,
        owner.validate_receipt_parent_ready(repository_root, context),
    )
    if current != observation:
        raise RuntimeError("receipt-parent state changed after bound observation")
    return current


def reduce_preauthorization_checkpoint(
    repository_root: Path,
    context: dict[str, Any],
    claim: dict[str, Any],
) -> dict[str, Any]:
    """Derive readiness; callers cannot inject a free-standing ready boolean."""

    owner = _load_existing_owner(repository_root)
    observation = validate_bound_observation(repository_root, context, claim)
    checkpoint = {
        "schema_id": CHECKPOINT_INNER_SCHEMA,
        "generation_identity": observation["generation_identity"],
        "operation_identity": observation["operation_identity"],
        "context_sha256": observation["context_sha256"],
        "receipt_parent": observation["receipt_parent"],
        "receipt_parent_ready": observation["receipt_parent_ready"],
        "receipt_parent_observation_sha256": claim["observation_sha256"],
        "claim_derivation": CLAIM_DERIVATION,
        "checkpoint_is_authority": False,
        "human_constitutional_authorization_count": 0,
        "operational_execution_count": 0,
    }
    return {
        "schema_id": CHECKPOINT_SCHEMA,
        "checkpoint": checkpoint,
        "checkpoint_sha256": _sealed_hash(owner, checkpoint),
    }


def validate_preauth_final_admission_equivalence(
    repository_root: Path,
    context: dict[str, Any],
    claim: dict[str, Any],
    checkpoint_envelope: dict[str, Any],
) -> dict[str, Any]:
    """Prove the bound preauthorization and unchanged FO observation agree."""

    owner = _load_existing_owner(repository_root)
    if set(checkpoint_envelope) != {"schema_id", "checkpoint", "checkpoint_sha256"}:
        raise RuntimeError("preauthorization checkpoint envelope malformed or unknown")
    if checkpoint_envelope["schema_id"] != CHECKPOINT_SCHEMA:
        raise RuntimeError("preauthorization checkpoint envelope schema mismatch")
    checkpoint = checkpoint_envelope["checkpoint"]
    if (
        not isinstance(checkpoint, dict)
        or set(checkpoint) != CHECKPOINT_FIELDS
        or checkpoint.get("schema_id") != CHECKPOINT_INNER_SCHEMA
    ):
        raise RuntimeError("preauthorization checkpoint malformed")
    if checkpoint_envelope["checkpoint_sha256"] != _sealed_hash(owner, checkpoint):
        raise RuntimeError("preauthorization checkpoint seal mismatch")
    preauthorization = validate_bound_observation(repository_root, context, claim)
    required_checkpoint = {
        "generation_identity": preauthorization["generation_identity"],
        "operation_identity": preauthorization["operation_identity"],
        "context_sha256": preauthorization["context_sha256"],
        "receipt_parent": preauthorization["receipt_parent"],
        "receipt_parent_ready": preauthorization["receipt_parent_ready"],
        "receipt_parent_observation_sha256": claim["observation_sha256"],
    }
    for field, expected in required_checkpoint.items():
        if checkpoint.get(field) != expected:
            raise RuntimeError(f"preauthorization checkpoint binding mismatch: {field}")
    if checkpoint.get("checkpoint_is_authority") is not False:
        raise RuntimeError("preauthorization checkpoint cannot be authority")
    if checkpoint.get("claim_derivation") != CLAIM_DERIVATION:
        raise RuntimeError("preauthorization checkpoint derivation mismatch")
    if (
        checkpoint.get("human_constitutional_authorization_count") != 0
        or checkpoint.get("operational_execution_count") != 0
    ):
        raise RuntimeError("preauthorization checkpoint contains operational authority")

    # This is the exact read-only receipt-parent observation called unchanged by
    # FO validate_final_admission.  Other FO gates remain out of this exact proof.
    final_admission_readiness = owner.validate_receipt_parent_ready(
        repository_root, context
    )
    final_admission = _observed_state(owner, context, final_admission_readiness)
    if final_admission != preauthorization:
        raise RuntimeError("preauthorization and final-admission observations disagree")
    return {
        "preauth_final_admission_equivalence": EQUIVALENCE_RESULT,
        "context_sha256": context["context_sha256"],
        "operation_identity": context["operation_identity"],
        "receipt_parent": context["receipt_parent"],
        "receipt_parent_observation_sha256": claim["observation_sha256"],
        "final_admission_owner": FINAL_ADMISSION_OWNER,
        "repeated_observation": "IDENTICAL",
        "human_constitutional_authorization_count": 0,
        "operational_execution_count": 0,
    }
