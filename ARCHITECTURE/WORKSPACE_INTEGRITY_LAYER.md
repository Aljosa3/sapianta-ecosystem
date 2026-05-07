# SAPIANTA Workspace Integrity Layer

## Document Role

This document records the workspace integrity problem discovered during architectural memory work and defines future verification requirements.

It is documentation-only. It does not implement automation, activation, enforcement, runtime integration, or autonomous mutation.

## Discovered Problem

SAPIANTA evolved into a multi-root workspace with separate responsibilities:
- meta-root memory
- governed runtime execution
- factory proposal generation
- domain capability roots

During long-horizon AI-assisted development, two risks became visible:
- AI tooling may generate conversational patches that are not physically persisted.
- AI tooling may mutate or reason from the wrong workspace root.

A related naming confusion also emerged:
`runtime/governance/master/` sounds like runtime governance, but its current architectural role is meta-root memory, governance lineage, orchestration memory, and cross-domain architectural memory.

## Integrity Requirements

Future workspace integrity support should verify:
- active workspace root
- canonical root mapping
- repository authority for each target file
- persisted filesystem state after writes
- documentation-only versus runtime-affecting scope
- lineage-aware mutation rules
- ADR and milestone append-only constraints
- runtime activation boundaries

## Persisted Filesystem Verification

After documentation changes, future AI sessions should verify:
- intended files exist
- intended content is present
- target root matches repository authority
- changes are physically present in the local workspace
- runtime files were not modified unintentionally

## Lineage-Aware Mutation Validation

Canonical state documents may be rewritten for clarity and current authority.

Lineage documents remain append-only:
- milestone summaries
- ADRs
- historical domain investigations
- governance milestone lineage

Canonicalization must not delete lineage, collapse milestone history, or rewrite ADR semantic history.

## Repository Authority Verification

Before modifying files, tooling should determine whether the target belongs to:
- meta-root memory
- governed runtime
- factory proposal generation
- domain capability logic

No root may silently claim authority over another root.

## Future Status

The workspace integrity layer is a documented future requirement only.

It is not currently:
- runtime enforcement
- governance activation
- policy engine integration
- Decision Spine integration
- autonomous mutation control
- automatic git execution
