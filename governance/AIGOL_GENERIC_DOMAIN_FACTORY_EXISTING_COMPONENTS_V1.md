# AIGOL_GENERIC_DOMAIN_FACTORY_EXISTING_COMPONENTS_V1

## Status

Review-only existing components inventory.

## Reusable Components

The following components are reusable for a future generic governed domain
factory:

| Component | Reuse value | Current limitation |
| --- | --- | --- |
| `conversation_native_development_intent_routing.py` | Deterministically recognizes native development intent and some domain creation prompts. | Classification does not produce an executable bundle definition. |
| `domain_and_worker_resolution_registry.py` | Contains domain registry concepts for Trading, Marketing, Healthcare, Public Services, and Server Management. | Registry is not consumed by executable bundle creation. |
| `worker_result_capture_runtime.py` | Captures allowed output lists deterministically. | Output content remains generic capture metadata, not domain bundle content. |
| `worker_result_validation_runtime.py` | Validates produced output lists and preserves lineage. | Validation is only as generic as the upstream allowed output list. |
| `executable_domain_bundle_runtime.py` | Provides create-only authorization, target preflight, artifact creation, hash verification, replay, and failure consistency. | Hardcoded to one Marketing executable bundle. |
| `post_execution_replay_review_runtime.py` | Reconstructs executable bundle lineage after verified bundle creation. | Consumes executable bundle replay but does not select or validate a domain bundle registry entry. |
| `governed_termination_runtime.py` | Terminates reviewed lifecycle deterministically. | Depends on successful post-execution replay review; not a factory selector. |

## Existing Marketing Bundle Components

The certified executable bundle currently creates exactly:

- `governance/MARKETING_DOMAIN_FOUNDATION_V1.md`;
- `governance/MARKETING_DOMAIN_MODEL_V1.md`;
- `governance/MARKETING_DOMAIN_CERTIFICATION.json`;
- `aigol/runtime/marketing_domain_runtime.py`;
- `tests/test_marketing_domain_runtime_v1.py`.

## Reusable Governance Semantics

These semantics should be preserved in any generic factory milestone:

- `CREATE_ONLY` permission;
- no overwrite, delete, rename, move, recursive creation, or implicit creation;
- exact target preflight before first write;
- exact path and content hash authorization;
- deterministic replay;
- terminal fail-closed behavior;
- post-execution replay review before termination;
- human/governance authority separation.

## Non-Reusable As-Is

The following cannot be reused unchanged for a generic domain factory:

- Marketing constants as factory identity;
- fixed Marketing content templates;
- fixed Marketing runtime module and test module;
- `_require_bundle_id` accepting only `MARKETING_EXECUTABLE_DOMAIN_BUNDLE_V1`;
- CLI binding that checks only `governance/MARKETING_DOMAIN_FOUNDATION_V1.md`;
- executable bundle validation that compares outputs only against
  `EXECUTABLE_BUNDLE_PATHS`.
