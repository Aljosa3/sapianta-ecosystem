# Platform Semantic Gap Closure G2-08 Specialized Product Domain Provider Similarity Routes V1

Status: implementation governance artifact.

Scope: CSA-primary specialized ACLI route semantics where deterministic parity with the
compatibility implementation is proven.

This batch does not retire compatibility layers, change Product 1 framing, transfer OCS
authority, transfer PPP ownership, grant approval authority, create execution
authorization, invoke providers, invoke workers, mutate governance, or mutate replay.

## 1. Purpose

Batch G2-08 implements the selected specialized route migration in the approved sub-order:

- G2-08A: Domain proposal and unknown-domain clarification routes.
- G2-08B: Provider onboarding routes.
- G2-08C: Product 1 routes.
- G2-08D: Similarity/domain adaptation and broad OCS route subsets.

CSA becomes primary only where the CSA normalized intent and the previous compatibility
route produce deterministic family parity.

## 2. Runtime Change

The conversational CLI routing runtime now includes a G2-08 specialized-route CSA
classifier after the previously certified CSA-primary migrations.

The classifier emits:

- `specialized_route_semantic_source`;
- `specialized_route_migration_batch_id`;
- `specialized_route_family`;
- `specialized_route_semantic_comparison_artifact`;
- `specialized_route_semantic_comparison_hash`;
- `specialized_route_semantic_comparison_parity_status`;
- `specialized_route_compatibility_fallback_available`;
- `specialized_route_compatibility_fallback_authoritative`.

## 3. Specialized Routes Migrated

Migrated family set:

| Sub-batch | Route family | Migrated workflow examples |
| --- | --- | --- |
| G2-08A | `DOMAIN_UNKNOWN_DOMAIN` | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` |
| G2-08B | `PROVIDER_ONBOARDING` | `PROVIDER_ONBOARDING_DOMAIN` |
| G2-08C | `PRODUCT_1` | `AI_DECISION_VALIDATOR_DOMAIN_FOUNDATION`, `AI_DECISION_VALIDATOR_CAPABILITY_MODEL`, `AI_DECISION_VALIDATOR_CAPABILITY_LIFECYCLE` |
| G2-08D | `SIMILARITY_DOMAIN_ADAPTATION` | `DOMAIN_ADAPTATION_REFERENCE` |
| G2-08D | `BROAD_OCS_COGNITION` | selected broad OCS advisory route prompts |

Example migrated prompts:

```text
Create a compliance domain.
Create a new governed domain called PilotDomain.
Dodaj Claude.
Onemogoči Claude.
Define Product 1 AI Decision Validator domain foundation.
Create Product 1 AI Decision Validator capability model.
Define Product 1 AI Decision Validator capability lifecycle.
Create a healthcare version of the trading domain.
Should Sapianta primarily sell domains, license the platform, or offer managed services?
```

## 4. Compatibility Fallback

Compatibility remains authoritative when CSA is absent, divergent, ambiguous outside the
certified family, low confidence outside the certified family, or not inside a parity
proven route subset.

Example fallback prompt:

```text
I want to create the first real AiGOL product.
```

The compatibility route remains `OCS_LLM_COGNITION`, while G2-08 specialized-route
fields remain unset.

## 5. Replay Evidence

The specialized route comparison artifact records:

- CSA reference and hash;
- previous compatibility interpretation;
- CSA specialized route interpretation;
- CSA route decision projection;
- route family and sub-batch;
- semantic equivalence result;
- semantic differences;
- confidence comparison;
- migration batch identifier;
- replay lineage;
- parity status;
- fallback status for non-parity cases.

The artifact is hash-bound and replay-visible.

## 6. Preserved Boundaries

G2-08 preserves:

- Product 1 framing as AI Decision Validator;
- OCS cognition authority;
- provider ownership and credential governance;
- approval authority;
- PPP structured ownership;
- governance authority;
- replay authority;
- worker boundaries;
- compatibility fallback.

CSA supplies specialized routing semantics only. It does not activate domains, approve
execution, select or invoke providers, invoke workers, mutate PPP artifacts, mutate
governance, or mutate replay.

## 7. Regression Coverage

Regression coverage added:

- CSA-primary domain and unknown-domain route parity;
- CSA-primary provider onboarding route parity;
- CSA-primary Product 1 route parity;
- CSA-primary similarity/domain adaptation route parity;
- CSA-primary broad OCS route parity for certified advisory prompts;
- compatibility-authoritative fallback for non-parity broad OCS prompts;
- replay reconstruction exposure for specialized route migration evidence;
- preservation of provider, worker, approval, execution, governance, and replay
  non-mutation flags.

## 8. Rollback Impact

Rollback is bounded:

- all specialized compatibility detectors remain active;
- non-parity prompts already remain compatibility-authoritative;
- removing the G2-08 classifier restores prior compatibility route behavior;
- replay evidence is observational outside certified route families and does not mutate
  downstream authority.

## 9. Certification Impact

G2-08 certifies the largest remaining ACLI specialized route-marker cluster under the
Generation 2 parity-gated migration model.

Certification proves route-level CSA primary handling for specialized families while
preserving Product 1 framing, domain approval gates, OCS authority, provider ownership,
PPP ownership, worker boundaries, governance authority, replay authority, and rollback
visibility.

## 10. Remaining Migration Inventory

Remaining Generation 2 migration inventory after G2-08:

- OCS semantic lineage and PPP annotation;
- command boundary and recommendation prose certification;
- explanation rendering migration;
- replay, hardening, and replay-derived classifiers;
- provider-assisted and legacy classifier closure;
- compatibility retirement certification.

## 11. Final Verdict

```text
PLATFORM_SEMANTIC_GAP_CLOSURE_G2_08_READY
```
