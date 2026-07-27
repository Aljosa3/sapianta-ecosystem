# Generation 32-10D: Constitutional Replay to Governance Integration

Status: IMPLEMENTED — REPLAY-DRIVEN, READ-ONLY GOVERNANCE EVALUATION  
Date: 2026-07-27  
Scope: First constitutional Governance consumption of Automatic Constitutional Validator Replay

## 1. Architecture

```text
ECC + Evidence Manifest + evidence
        |
        v
Automatic Constitutional Validator
        |
        v
Immutable Platform Replay record
        |
        v
Constitutional Replay Governance reader and assessment
```

Governance consumes only the replay reconstruction interface. It does not
invoke the Validator, access Validator inputs, write or repair Replay, modify
Evidence, or alter Replay history. Platform Replay remains the sole recorder
and the constitutional source of execution evidence.

## 2. Governance Replay Reader

`read_constitutional_validator_replay()` delegates reconstruction and integrity
verification to the Replay-owned interface. Governance requires a reconstructed
single-event Platform Replay stream with valid Replay identity, wrapper hash,
Validator result hash, ECC contract hash, Evidence Manifest hash, and summary.

Invalid, substituted, reordered, or otherwise corrupt Replay fails closed
before a governance assessment is produced.

## 3. Constitutional Governance Assessment Model

`ConstitutionalGovernanceAssessment` is an immutable, deterministic,
non-authorizing model. It contains:

- deterministic `assessment_id` and `assessment_hash`;
- Replay identity and hash;
- Validator execution and result identities;
- ECC and Evidence Manifest hash bindings;
- Validator PASS or FAIL outcome;
- constitutional interpretation and failure codes;
- explicit read-only and non-authority boundary flags.

The separate assessment records `governance_assessed = true`; the historical
Validator Replay remains unchanged with `governance_assessed = false` because
it correctly represents the state at the time of recording.

Governance maps a verified Validator `PASS` to
`CONSTITUTIONALLY_COMPLIANT` and a verified `FAIL` to
`CONSTITUTIONALLY_NON_COMPLIANT`. This is interpretation of an immutable
outcome; it neither replaces nor changes the Validator's PASS/FAIL result.

## 4. Deterministic Lifecycle

1. Validator completes an immutable result.
2. Platform Replay records the immutable result.
3. Governance reads and reconstructs the Replay record.
4. Replay integrity and lineage are verified.
5. Governance derives and returns an in-memory assessment.

The assessment is not appended to the Validator Replay stream. This preserves
Replay ownership and makes evaluation repeatable: the same verified Replay
record produces the same assessment identity and hash.

## 5. Authority and Compatibility Boundaries

The assessment has no Certification, authorization, Worker, Provider, or
execution effect. Its model explicitly retains all of the following as false:

- `replay_modified`
- `validator_invoked`
- `evidence_modified`
- `certification_performed`
- `authorization_created`
- `worker_assigned`
- `provider_invoked`
- `execution_requested`

The original Validator Replay remains unchanged and continues to state that no
Governance assessment existed at the time it was recorded. The separate
in-memory assessment does not retroactively alter that historical fact.

This adds a new Governance reader only. Existing Replay formats, Validator
interfaces, Certification paths, authorization paths, Worker behavior, and
Provider behavior remain compatible and unchanged.

## 6. Validation and Repository Impact

Focused tests cover PASS and FAIL interpretation, deterministic repeated
assessment, tampered Replay rejection, no Validator dependency in the
Governance module, and the certified Filesystem ECC → Validator → Replay →
Governance path.

```text
python -m py_compile aigol/runtime/constitutional_replay_governance.py
python -m pytest tests/test_constitutional_validator_replay_v1.py \
  tests/test_automatic_constitutional_validator_kernel_v1.py -q
# 24 passed
git diff --check
```

The change adds one read-only Governance module and tests. It does not modify
constitutional artifacts, Replay ownership, Validator semantics, Certification,
policy, authorization, Worker, Provider, or execution behavior.
