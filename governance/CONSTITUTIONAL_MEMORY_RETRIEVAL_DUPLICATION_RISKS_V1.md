# Constitutional Memory Retrieval Duplication Risks V1

Status: retrieval duplication risk analysis.

## Replay Duplication

Risk: retrieval creates a parallel replay log.

Mitigation: retrieval emits replay-visible consultation records as derived evidence only. Replay remains the evidence spine.

## Governance Duplication

Risk: retrieval output is treated as a governance decision.

Mitigation: retrieval returns `REFERENCE_RESULT`, not governance authority.

## Certification Duplication

Risk: retrieval output is treated as certification.

Mitigation: retrieval may cite certification artifacts but cannot certify.

## Lineage Duplication

Risk: retrieval creates competing lineage.

Mitigation: retrieval must cite existing lineage and dependency artifacts.

## Index Model Duplication

Risk: retrieval embeds a private index inconsistent with the canonical memory index.

Mitigation: retrieval must remain subordinate to `CONSTITUTIONAL_MEMORY_INDEX_MODEL_V1` and canonical source classifications.

## Highest Risk

The highest risk is confusing citation-backed reference with authority.

This must fail closed.

