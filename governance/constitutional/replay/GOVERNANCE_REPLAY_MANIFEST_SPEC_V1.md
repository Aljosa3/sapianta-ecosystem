# GOVERNANCE_REPLAY_MANIFEST_SPEC_V1

Status: CANONICAL GOVERNANCE REPLAY MANIFEST SPECIFICATION

## Purpose

This artifact defines canonical replay manifest structure for governance
evidence.

It does not implement replay execution.

## Manifest Determinism

Manifest structure MUST remain deterministic.

Fields MUST be serialized in canonical order.

Validation outcomes MUST be reproducible from manifest content and
referenced evidence.

## Required Manifest Sections

### replay_metadata

Records replay identity, schema version, evidence class, deterministic
hash, and timestamp reference.

### governance_references

Records governance domain, constitutional scope, protected-layer
classification, and governing freeze references.

### proposal_references

Records proposal identity, proposal hash, proposal lineage reference,
and proposal evidence bundle hash.

### certification_references

Records certification status, certification identity, certification
evidence hash, and certification lineage.

### rollback_references

Records rollback requirement, rollback identity where present, rollback
evidence hash, and rollback lineage reference.

### replay_validation_status

Records whether replay validation passed, failed, was blocked, or was
quarantined.

### evidence_integrity_status

Records evidence hash validation, canonical serialization validation,
append-only validation, and lineage reference validation.

### deterministic_verification_status

Records deterministic verification of replay input, replay output,
hashes, manifest structure, and validation status.

## Canonical Manifest Contract

A governance replay manifest MUST be:

- deterministic;
- replay-safe;
- append-only when extended;
- immutable after certification;
- explicit about missing or blocked evidence;
- non-authoritative with respect to mutation approval.

## Non-Activation Rule

A replay manifest is evidence. It is not activation, approval,
execution, mutation authority, or promotion authority.
