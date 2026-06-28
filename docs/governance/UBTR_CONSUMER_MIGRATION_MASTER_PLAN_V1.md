# UBTR Consumer Migration Master Plan V1

Status: governance planning artifact.

Scope: Platform Core Generation 2 UBTR consumer migration roadmap after certified Batch 01.

This artifact does not implement runtime behavior, modify tests, change routing, change governance authority, change replay semantics, retire compatibility layers, or introduce new architecture.

## 1. Purpose

Platform Core Generation 1 is certified.

UBTR is:

- architecture complete;
- beta ready;
- replay-visible across the Human -> UBTR -> OCS -> UBTR -> Human path;
- certified for Consumer Migration Batch 01 ACLI routing.

Batch 01 established the governing migration model:

```text
CSA primary only where compatibility parity is proven
-> compatibility fallback remains active
-> replay records semantic source, previous compatibility route, migration evidence, and routing lineage
```

This master plan defines the roadmap for every remaining Platform Core consumer that still directly performs semantic interpretation or consumes compatibility-layer semantics.

## 2. Migration Rule

Every remaining migration must preserve the Batch 01 parity model.

CSA or UBTR may become the primary semantic source only when:

- the target consumer's current compatibility behavior is known;
- the CSA or UBTR field set represents the same semantic meaning;
- parity is proven against a certified prompt or replay corpus;
- replay records both the new semantic source and previous compatibility source;
- rollback to compatibility behavior is possible without replay reinterpretation;
- approval, PPP, workers, provider selection, OCS authority, and governance authority remain unchanged.

If parity is not proven, the consumer must remain on compatibility fallback while recording CSA/UBTR comparison evidence.

## 3. Consumer Inventory

| Consumer | Current Semantic Source | Target Semantic Source | Difficulty | Certification Risk | Replay Impact | Regression Requirements | Rollback Strategy | Parity Evidence Required |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Batch 01 ACLI governed-development route subset | CSA gated by compatibility route parity | CSA | Complete | Low | Records `semantic_routing_source`, previous compatibility route, CSA hash, UBTR lineage | Existing Batch 01 regression and full suite | Disable CSA branch; retain `_classify_workflow()` | Certified |
| Broad ACLI workflow classifier | `_classify_workflow(human_prompt)` marker cascade | CSA `workflow_identity`, `semantic_identity`, ambiguity and confidence | High | High | Must record selected source, fallback reason, divergence status, previous local route | Full conversational CLI corpus, Product 1, governance artifact, provider onboarding, domain, OCS, native development, unrestricted autonomy fail-closed | Keep local classifier as authoritative fallback | Route-by-route equality with certified local classifier |
| Proposal-only OCS escalation | `_proposal_only_ocs_escalation(normalized)` local markers | CSA/UBTR execution intent, provider relevance, requested actions, no-execution semantics | Medium | High | Must record proposal-only source, provider relevance source, no-execution evidence, previous marker result | English and Slovenian proposal-only prompts, governance-document prompts, execution-like negative prompts, no worker invocation | Return to local marker escalation | CSA proves proposal-only, no-execution, provider-required semantics match local markers |
| HIRR intake | `classify_human_intent_for_clarification()` marker families | CSA/UBTR intent family, ambiguity flags, clarification state | High | High | Must bind HIRR artifact to CSA hash and previous marker family | All HIRR family tests, ambiguity tests, clarification question tests, unknown-intent behavior | Keep HIRR local classifier authoritative | CSA can produce HIRR-compatible artifact for certified HIRR corpus |
| HIRR governed-development intake | `classify_development_intent_for_governed_routing()` | CSA development domain/action/entity fields | Medium | High | Must record CSA-derived HIRR-compatible intake and previous local signals | Governed-development routing tests, freeform development boundary tests, non-parity fallback tests | Keep development classifier fallback | CSA and local classifier select the same governed workflow |
| HIRR continuity and clarification refinement | Local clarification state/refinement rules | Linked original CSA plus clarification-turn CSA | High | High | Must link original and clarification CSA hashes, ambiguity reduction evidence, preserved target | Clarification promotion, target preservation, multilingual clarification, proposal-only after clarification | Keep local continuity refinement | CSA proves clarification reduces ambiguity without changing target incorrectly |
| Human execution intent detection | `detect_human_execution_intent()` creation/execution/governance markers | CSA execution intent, approval required, requested actions, entities | Medium | High | Must record execution-intent source and fail-closed reason source | Domain creation, artifact creation, generic execution fail-closed, no authorization from UBTR | Keep local detector fallback | CSA matches local `GENERIC_*` classes and `NO_EXECUTION_INTENT` |
| Native development intent routing | `conversation_native_development_intent_routing.py` catalog markers | CSA development action/domain/resource fields | Medium | Medium | Must record catalog parity, CSA source, previous catalog match terms | Native development catalog tests, provider add unsupported behavior, worker/domain resource tests | Keep native catalog fallback | CSA identifies same domain/resource/provider/worker family as catalog |
| Native development context intake | `native_development_task_intake_runtime.is_*prompt()` and context markers | CSA development task semantics plus structured context artifacts | Medium | Medium | Must record CSA annotation without replacing structured context authority | Freeform development tests, PPP handoff, replay-safe context restoration | Keep native context detection fallback | CSA distinguishes context-intake prompts from governed-development workflow prompts |
| Product 1 decision validation routing | Product-specific local route/decision validators and structured packet tests | CSA Product 1 domain, decision-validation intent, evidence entities | Medium | High | Must record Product 1 semantic source and previous product route | Product 1 packet certification, decision validation fixtures, enterprise demo flows | Keep product route fallback | CSA identifies AI Decision Validator intent without generic chatbot or AGI drift |
| Provider onboarding routing | ACLI provider onboarding markers and unsupported workflow handling | CSA provider entity/action fields | Medium | Medium | Must record provider target, previous provider route, unsupported fallback | Provider onboarding/domain certification tests, unsupported route fail-closed tests | Keep provider marker fallback | CSA extracts provider identity and action with same route outcome |
| Domain proposal and unknown-domain clarification | Domain prompt markers and domain proposal governance runtime | CSA domain candidate, entities, ambiguity, approval requirement | Medium | High | Must record domain semantic source and proposal/clarification fallback reason | Domain proposal tests, unknown-domain clarification tests, no candidate activation before approval | Keep domain prompt markers fallback | CSA domain candidate and approval requirement match local behavior |
| Semantic similarity/domain reference adaptation | `is_domain_reference_adaptation_prompt()` and similarity runtime | CSA source/target domain references and adaptation action | Medium | Medium | Must record domain reference source and previous adaptation marker | Domain reference adaptation tests, semantic similarity tests | Keep local adaptation marker fallback | CSA identifies reference and target domain pair with route parity |
| OCS LLM cognition prompt routing | `is_ocs_llm_cognition_prompt()` and broad cognition route markers | CSA cognition/advisory/proposal semantics plus OCS handoff policy | Medium | High | Must record OCS routing source, CSA hash, OCS handoff linkage | OCS cognition binding, clarification, approval-required, provider necessity tests | Keep explicit OCS route markers | CSA selects OCS only for same advisory/cognition cases |
| OCS semantic resolution | OCS semantic artifacts built from OCS context/cognition outputs | CSA as upstream semantic lineage, OCS artifacts remain OCS-owned | Medium | Medium | Must link CSA lineage to OCS semantic resolution without giving UBTR provider authority | OCS semantic resolution, OCS end-to-end, provider necessity | Keep OCS semantic resolution unchanged | CSA lineage is present; OCS still owns cognition/result semantics |
| PPP routing and resource selection | Structured context, replay-derived intent, resource selection artifacts | CSA annotation only; structured artifacts remain authority | Medium | High | Must record CSA reference beside PPP source artifact | PPP routing, resource selection, continuation, restored context tests | Keep structured PPP path | CSA agrees with structured context but does not replace it |
| Approval and resume commands | Deterministic command parsing and replay-restored approval state | No CSA for exact commands; Governance -> Human UBTR for presentation | Low | High | Must record when UBTR is renderer-only and command parser remains authority | Same-session approval, restart approval, reject, modification, resume/cancel/retry | Keep command parser unchanged | Exact commands remain out of UBTR semantic migration |
| Recommendation approval/follow-up | Local recommendation prompt checks | CSA ambiguous prose only; exact recommendation commands remain structured | Low | Medium | Must record command vs prose source | Recommendation approval/rejection/ignore/follow-up tests | Keep local recommendation checks | CSA used only when no exact command matches |
| Clarification lifecycle resolution | Structured clarification lifecycle state plus prompt checks | Linked CSA for natural-language replies; lifecycle state remains authority | Medium | High | Must link clarification reply CSA to lifecycle state | Clarification lifecycle, reply binding, resume tests | Keep lifecycle resolver fallback | CSA reply semantics match current resolution result |
| Provider-unavailable clarification fallback | `_classify_ambiguity(prompt)` narrow fallback eligibility | CSA ambiguity/clarification required fields | Medium | Medium | Must record fallback eligibility source and provider failure lineage | Provider-unavailable fallback tests and broad cognition negative cases | Keep narrow fallback eligibility | CSA marks same fallback-eligible prompts only |
| Universal intake layer | Workflow-id classification, not broad NL interpretation | CSA workflow identity for migrated workflows | Low | Medium | Must record CSA workflow identity when present | Universal intake tests | Keep workflow-id classifier | CSA workflow identity maps to same intake classification |
| Provider-assisted intent classification | Provider advisory semantic suggestion after deterministic failure | CSA first; provider remains advisory and non-authoritative | High | Medium | Must record deterministic CSA failure before provider suggestion | Provider-assisted classification, provider unavailable, advisory-only tests | Keep provider-assisted path as fallback after deterministic failure | CSA cannot classify or explicitly requests advisory escalation |
| Explanation compatibility rendering | Human-friendly explanation sections and compatibility renderers | Governance -> Human UBTR output as primary renderer with compatibility sections as fallback | Medium | Medium | Must record primary renderer, compatibility sections, source transparency | Explanation section parity, operator-visible cognition, no authority flags | Restore compatibility renderer as primary | UBTR output contains all certified operator guidance sections |
| LLM-assisted explanation | Authoritative state plus optional provider wording | Governance -> Human UBTR plus advisory provider wording | Low | Low | Must retain advisory-only/provider non-authority flags | LLM-assisted explanation tests, provider failure tests | Disable provider advisory wording | UBTR deterministic output present; provider only enriches prose |
| Conversational routing visibility | Routing decision artifacts and visibility renderers | Authoritative CSA/routing decision source fields | Low | Medium | Must stop duplicating independent visibility classifications | Routing visibility and dispatch authority tests | Render from compatibility routing fields | Visibility exactly matches authoritative route selection |
| Hardening runtime | Local token scans over interaction evidence | Structured replay fields plus CSA/UBTR source fields | Medium | Medium | Must record scenario classification source: UBTR, structured replay, or legacy scan | Hardening progress, failure events, legacy replay tests | Use token scan fallback for legacy sessions | New sessions expose structured fields sufficient for classification |
| Replay-derived improvement/gap classifiers | Replay gap and improvement-intent local classification | Structured replay plus CSA/UBTR provenance fields | Medium | Medium | Must include semantic-source provenance in gap/improvement evidence | Replay gap, replay-derived improvement, PPP integration tests | Keep local replay-derived classifiers | CSA/replay fields identify the same gap class |
| Legacy `intent_classifier.py` and older conversation runtime | Deterministic local classifiers | CSA comparison first; legacy fallback for old entrypoints | Medium | Medium | Must mark legacy source and unsupported fallback | Prompt-to-conversation, provider-assisted conversation tests | Keep legacy runtime fallback | CSA route parity for entrypoints still in use |
| Worker/domain lifecycle entry detectors | `detect_domain_*_entry_intent()` functions on human prompts | Prefer structured lifecycle state; CSA only for natural-language entry requests | Medium | High | Must record lifecycle detector source and no execution authority | Worker request/assignment/dispatch/invocation/result lifecycle tests | Keep detector functions | CSA requested action and lifecycle stage match local detector |

## 4. Migration Dependency Graph

```text
Certified Batch 01 parity gate
  -> Batch 02 replay comparison substrate
      -> Batch 03 proposal-only OCS routing
      -> Batch 04 HIRR intake
          -> Batch 05 HIRR continuity and clarification refinement
              -> Batch 06 execution-intent detection
                  -> Batch 07 native development and context routing
                      -> Batch 08 domain/Product 1/provider specialized routes
                          -> Batch 09 PPP/resource-selection semantic annotation
                              -> Batch 10 approval/resume/recommendation command boundary certification
                                  -> Batch 11 explanation rendering migration
                                      -> Batch 12 replay, hardening, and replay-derived classifiers
                                          -> Batch 13 legacy classifier retirement audit
```

Parallel lanes:

- Explanation rendering parity can start after Batch 02, but cannot become primary until Governance -> Human UBTR output proves section parity.
- Replay and hardening field work can start after Batch 02, but certification must wait until upstream consumers emit stable provenance fields.
- Approval/resume exact command parsing is not blocked by CSA migration because exact lifecycle commands remain structured command authority.

## 5. Recommended Migration Batches

### Batch 02: Replay Comparison Substrate

Objective:

Record CSA/UBTR comparison evidence for every remaining ACLI semantic consumer without changing selected workflow.

Consumers:

- broad ACLI classifier;
- proposal-only OCS escalation;
- HIRR intake;
- execution-intent detection;
- native development/context detectors;
- specialized domain/Product 1/provider routes.

Certification checkpoint:

- every natural-language ACLI turn records local source, CSA source when available, agreement/divergence, fallback reason, and authority flags.

### Batch 03: Proposal-Only OCS Routing

Objective:

Migrate proposal-only OCS escalation when CSA proves proposal-only, no-execution, and provider-required semantics.

Certification checkpoint:

- English and Slovenian proposal-only prompts route identically;
- execution-like prompts do not become proposal-only;
- provider selection remains OCS-owned;
- no worker invocation occurs.

### Batch 04: HIRR Intake

Objective:

Generate HIRR-compatible intake artifacts from CSA/UBTR fields for certified HIRR prompt families.

Certification checkpoint:

- HIRR artifact shape is unchanged;
- clarification questions remain stable;
- CSA source and previous marker family are replay-visible.

### Batch 05: HIRR Continuity

Objective:

Use linked original and clarification-turn CSA artifacts to prove ambiguity reduction while preserving local continuity state.

Certification checkpoint:

- clarification promotion, target preservation, and multilingual clarification remain green.

### Batch 06: Execution Intent Detection

Objective:

Migrate generic governed domain creation, artifact creation, and generic execution fail-closed detection to CSA when parity is proven.

Certification checkpoint:

- CSA never grants execution authority;
- generic execution requests still fail closed without certified mapping.

### Batch 07: Native Development And Context Routing

Objective:

Migrate native development catalog decisions and context-intake boundaries without collapsing them into governed development workflow.

Certification checkpoint:

- native resource catalog parity is proven;
- freeform context prompts keep current behavior;
- PPP handoff behavior is unchanged.

### Batch 08: Specialized Routes

Objective:

Migrate Product 1, provider onboarding, domain proposal, unknown-domain clarification, semantic similarity, and OCS cognition route subsets.

Certification checkpoint:

- each specialized route has its own parity corpus;
- enterprise Product 1 framing remains AI Decision Validator, not chatbot or AGI;
- provider/OCS ownership remains unchanged.

### Batch 09: PPP And Resource Selection Annotation

Objective:

Attach CSA lineage to PPP/resource-selection flows without replacing structured context authority.

Certification checkpoint:

- PPP consumes the same structured artifacts;
- CSA is annotation/provenance only unless a later certification explicitly proves equivalent structured input.

### Batch 10: Command Boundary Certification

Objective:

Certify that approval, resume, lifecycle, and recommendation exact commands remain structured command authority and are not migrated to UBTR semantic authority.

Certification checkpoint:

- exact commands bypass CSA routing by design;
- ambiguous prose can use CSA/UBTR as evidence only after command parser non-match.

### Batch 11: Explanation Rendering

Objective:

Make Governance -> Human UBTR output the primary operator renderer where section parity is proven.

Certification checkpoint:

- compatibility explanation sections remain visible as fallback;
- source transparency records UBTR primary versus compatibility fallback;
- renderers remain non-authoritative.

### Batch 12: Replay, Hardening, And Replay-Derived Classifiers

Objective:

Move new-session hardening and replay-derived classifications from token scans to structured replay and CSA provenance fields.

Certification checkpoint:

- legacy replay remains classifiable;
- new replay classification uses structured fields;
- no historical replay is reinterpreted.

### Batch 13: Compatibility Retirement Audit

Objective:

Audit which compatibility layers can be retired, diagnostic-only, or must remain active.

Certification checkpoint:

- no retirement occurs without consumer-specific parity evidence, rollback proof, and full regression success.

## 6. Estimated Implementation Order

1. Batch 02: comparison substrate.
2. Batch 03: proposal-only OCS routing.
3. Batch 04: HIRR intake.
4. Batch 05: HIRR continuity.
5. Batch 06: execution-intent detection.
6. Batch 07: native development and context routing.
7. Batch 08A: domain proposal and unknown-domain clarification.
8. Batch 08B: provider onboarding and specialized provider routes.
9. Batch 08C: Product 1 decision validation routing.
10. Batch 08D: semantic similarity/domain reference and broad OCS cognition route subsets.
11. Batch 09: PPP/resource-selection annotation.
12. Batch 10: command boundary certification.
13. Batch 11: explanation rendering.
14. Batch 12: replay/hardening/replay-derived classifiers.
15. Batch 13: retirement audit.

Implementation should stop after any batch that reveals CSA/compatibility divergence until the divergence is classified as:

- UBTR field gap;
- compatibility marker bug;
- intentional behavior difference requiring governance approval;
- unsupported prompt outside migration scope.

## 7. Certification Checkpoints

Every batch must produce:

- governance artifact describing scope and non-goals;
- runtime evidence only when runtime changes are intentionally part of that batch;
- regression tests covering migrated and fallback paths;
- replay evidence fields for semantic source and previous compatibility source;
- rollback statement;
- provider/worker/approval/PPP/OCS authority preservation statement;
- `git diff --check`;
- targeted tests;
- full `python -m pytest -q` before certification.

Batch-specific checkpoints:

| Batch | Checkpoint |
| --- | --- |
| 02 | Comparison evidence exists without behavior change |
| 03 | Proposal-only CSA parity and OCS ownership proven |
| 04 | HIRR-compatible CSA intake artifact proven |
| 05 | Clarification CSA lineage and ambiguity reduction proven |
| 06 | Execution-intent fail-closed parity proven |
| 07 | Native development/context boundary preserved |
| 08 | Specialized route parity proven by route family |
| 09 | PPP structured authority preserved with CSA lineage |
| 10 | Exact command authority preserved outside UBTR |
| 11 | UBTR output section parity proven |
| 12 | Structured replay classification replaces token scans for new sessions |
| 13 | Retirement eligibility proven or compatibility retained |

## 8. Rollback Model

Rollback for every migrated consumer must:

- preserve the previous compatibility route or classifier;
- preserve CSA/UBTR replay artifacts as evidence;
- mark fallback reason in replay;
- keep historical replay read-only;
- avoid reinterpretation of prior route decisions;
- preserve output shapes expected by downstream consumers.

Rollback must never:

- erase CSA lineage;
- grant execution, approval, worker, provider, or governance authority;
- convert provider/advisory output into semantic authority;
- bypass OCS provider ownership;
- bypass PPP validation;
- remove known limitation visibility.

## 9. Retirement Rules

Compatibility may be retired only when:

- CSA/UBTR fields cover the full certified behavior;
- parity evidence covers positive, negative, ambiguous, multilingual, and fail-closed cases;
- replay reconstruction proves semantic source lineage;
- fallback has been exercised and remains reversible before retirement;
- certification explicitly authorizes retirement.

Compatibility must remain active when:

- any prompt family lacks CSA representation;
- local multilingual behavior remains more complete;
- exact command parsing is safer as structured command authority;
- structured PPP/replay state is more authoritative than natural-language interpretation;
- provider output is advisory only;
- retirement would hide partial conformance.

## 10. Non-Goals

This master plan does not:

- implement runtime;
- modify tests;
- redesign UBTR;
- redesign ACLI, HIRR, OCS, PPP, approval, replay, providers, or workers;
- introduce provider authority;
- introduce worker authority;
- introduce autonomous constitutional mutation;
- convert exact approval/resume commands into semantic translation requests;
- retire compatibility layers automatically;
- claim full UBTR exclusivity before all batches are certified.

## 11. Certification Statement

After Batch 01, Platform Core can claim:

- UBTR is canonical semantic infrastructure;
- CSA can be primary for certified parity-gated ACLI route subsets;
- compatibility layers remain active and observable;
- partial conformance remains visible.

After this master plan is executed and certified batch by batch, Platform Core may claim:

- natural-language semantic consumers derive meaning from CSA/UBTR artifacts or structured replay artifacts;
- compatibility layers are limited to documented rollback, legacy, unsupported, or exact-command surfaces;
- semantic provenance is replay-visible across ACLI, HIRR, OCS, PPP, explanation, hardening, and replay-derived consumers.

Platform Core must not claim UBTR-exclusive semantic authority until Batch 13 confirms every compatibility layer is either retired, diagnostic-only, or explicitly retained with governance justification.

## Final Verdict

UBTR_CONSUMER_MIGRATION_MASTER_PLAN_READY
