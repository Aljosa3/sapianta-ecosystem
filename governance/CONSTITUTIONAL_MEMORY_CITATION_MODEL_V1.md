# Constitutional Memory Citation Model V1

Status: citation model for Constitutional Memory retrieval.

## Citation Requirement

`CONSTITUTIONAL_MEMORY_CITATION_REQUIREMENT`: `MANDATORY`

Every Constitutional Memory retrieval result must include citations.

## Required Citation Fields

Each citation must include:

- artifact identity
- artifact source path or stable source identifier
- artifact classification: `CANONICAL`, `SUPPORTING`, or `DERIVED`
- memory layer or category
- retrieval timestamp or deterministic retrieval time placeholder
- replay visibility status
- authority status: `REFERENCE_ONLY`
- citation reason

## Appropriate Retrieval Outputs

Appropriate outputs:

- artifact references
- citations
- short constitutional excerpts
- lineage references
- certification references
- evidence bundles
- missing/conflict status

Inappropriate outputs:

- uncited constitutional claims
- inferred missing rules
- authorization decisions
- execution instructions
- governance mutations
- silent conflict resolution

## Excerpt Boundary

Constitutional excerpts must be short and tied to cited artifact identity.

If a longer explanation is needed, retrieval should return artifact references and a summary, not reproduce or mutate source artifacts.

## Citation Failure

If citation cannot be produced, retrieval must fail closed with:

```text
CITATION_MISSING
```

No uncited answer may be treated as Constitutional Memory retrieval.

