# Platform Wide Semantic Responsibility Audit V1

Status: governance audit artifact.

Scope: Platform Core semantic responsibility alignment after UBTR/HIRR boundary freeze.

This artifact does not implement runtime code, modify tests, change routing behavior, retire compatibility layers, or alter governance authority.

## 1. Purpose

Platform Core Generation 1 is certified.

UBTR is beta ready.

UBTR/HIRR final boundaries are frozen:

- UBTR owns meaning.
- HIRR owns clarification lifecycle.
- Compatibility layers remain active until consumer-specific parity and retirement certification are complete.

Consumer Migration Batch 01 certified a CSA-primary ACLI routing subset.

Consumer Migration Batch 02 certified a CSA-primary HIRR ambiguous-intent clarification intake subset.

This audit verifies whether any remaining Platform Core subsystem still owns semantic interpretation that should belong to UBTR.

## 2. Audit Method

The audit reviewed:

- certified UBTR consumer migration artifacts;
- the UBTR Consumer Migration Master Plan;
- the HIRR post-UBTR responsibility audit;
- the frozen UBTR/HIRR boundary specification;
- runtime subsystem entrypoints and classifiers;
- replay, explanation, approval, lifecycle, worker, provider, PPP, OCS, and translation surfaces.

The audit distinguishes:

- natural-language interpretation;
- semantic intent classification;
- CSA consumption;
- structured lifecycle or command authority;
- replay or rendering surfaces that must remain non-authoritative;
- compatibility-only semantic paths retained for rollback.

No runtime code or tests were changed.

## 3. Platform Finding

Platform semantic responsibilities are not yet fully aligned.

UBTR is the canonical semantic authority by architecture and by certified migration pattern, but Platform Core still contains compatibility-era semantic interpretation in several consumers.

The remaining semantic responsibility gaps are bounded and replay-safe, not governance bypasses.

They do not change the Generation 1 certification result because:

- compatibility layers are intentionally active;
- approval, provider, worker, execution, OCS, PPP, governance, and replay authority boundaries remain separate;
- Batch 01 and Batch 02 explicitly certified CSA primary only for parity-proven subsets;
- non-parity prompt families continue to use compatibility fallback.

The platform cannot yet claim that every runtime semantic decision consumes CSA as the primary semantic source.

## 4. Responsibility Classification

| Classification | Meaning |
| --- | --- |
| `UBTR responsibility` | Semantic meaning should be produced by UBTR and represented by CSA. |
| `Permanent subsystem responsibility` | The subsystem owns lifecycle, authority, validation, rendering, replay, or execution boundaries rather than semantic meaning. |
| `Shared during migration only` | Local compatibility interpretation remains active until CSA parity is certified. |
| `Compatibility-only` | The path should remain observable as rollback or legacy support, not as final semantic authority. |
| `Candidate for retirement` | The local semantic path can be retired only after parity, replay, rollback, and regression certification. |

## 5. Platform Semantic Responsibility Matrix

| Subsystem | Interprets Natural Language? | Classifies Semantic Intent? | Consumes CSA? | Should Semantic Responsibility Remain? | Should Migrate To UBTR? | Transitional Or Permanent? | Audit Finding |
| --- | --- | --- | --- | --- | --- | --- | --- |
| UBTR Human -> Governance translation | Yes | Yes | Produces CSA source lineage | Yes, as UBTR | Already UBTR | Permanent UBTR responsibility | Aligned. |
| Canonical Semantic Artifact runtime | No prompt interpretation; structures canonical semantics | Yes, from UBTR translation input | Produces CSA | Yes, as canonical artifact authority | Already UBTR | Permanent UBTR responsibility | Aligned. |
| UBTR semantic cognition orchestration | Yes, when deterministic translation is insufficient | Yes | Produces and updates CSA lineage | Yes, as UBTR/OCS semantic bridge | Already UBTR | Permanent UBTR responsibility with OCS handoff boundary | Aligned if OCS remains cognition authority. |
| UBTR OCS cognition result integration | No independent prompt interpretation | Integrates OCS cognition result into CSA | Produces integrated CSA | Yes, as CSA integration | Already UBTR | Permanent UBTR responsibility | Aligned. |
| UBTR Governance -> Human translation | Yes, for operator-facing projection | Yes, for explanation semantics | Consumes governance artifacts and translation lineage | Yes, as UBTR projection | Already UBTR | Permanent UBTR responsibility | Aligned. |
| ACLI conversational routing | Yes | Yes | Partially, for Batch 01 and Batch 02 subsets | No, except compatibility fallback | Yes | Shared during migration only | Gap remains beyond certified subsets. |
| ACLI `_classify_workflow()` compatibility classifier | Yes | Yes | No direct CSA authority | No | Yes | Compatibility-only, candidate for retirement | Duplicate semantic owner. |
| ACLI proposal-only OCS escalation | Yes | Yes | Not primary | No | Yes | Shared during migration only | Gap remains; high certification priority. |
| ACLI routing visibility | No independent authority intended | May render selected semantic route | Consumes routing artifacts | No semantic authority should remain | Render from CSA/routing evidence | Permanent renderer after source cleanup | Must not duplicate classification. |
| HIRR ambiguous clarification intake | Yes | Yes | Yes for certified Batch 02 subset | No semantic ownership; lifecycle only | Already migrated for narrow subset | Shared during migration only | Partially aligned. |
| HIRR remaining intake families | Yes | Yes | Not primary | No | Yes | Shared during migration only | Gap remains. |
| HIRR governed-development intake | Yes | Yes | Indirect through ACLI Batch 01 metadata for subset | No | Yes | Shared during migration only | Gap remains outside certified route subset. |
| HIRR clarification continuity and reply refinement | Yes, for replies | Yes | Not primary | No semantic ownership; lifecycle remains | Yes | Shared during migration only | Gap remains. |
| HIRR clarification lifecycle state | No, except when coupled to reply text | No final semantic authority | Should consume linked CSA after migration | Yes, lifecycle only | Semantic reply meaning should migrate | Permanent HIRR lifecycle responsibility | HIRR must keep lifecycle and binding. |
| OCS LLM cognition prompt routing | Yes, for cognition/proposal cues | Yes | Not yet consistently primary | OCS owns cognition process, not initial NL meaning | Yes for input semantics | Shared during migration only | Gap remains in entry routing. |
| OCS semantic resolution | Consumes OCS source artifacts, not raw operator prompts in the same role | Yes, as cognition-result semantics | CSA lineage should be upstream evidence | Yes, for OCS cognition result semantics | CSA lineage should feed it; OCS authority remains | Permanent OCS cognition responsibility | Not a UBTR replacement target, but lineage alignment is needed. |
| PPP routing and resource selection | Mostly no; consumes structured context and replay | Mostly structured selection | CSA annotation only in target state | Yes, structured PPP authority remains | Only semantic annotation should migrate | Permanent PPP validation responsibility | No direct semantic authority should remain except compatibility annotations. |
| Approval runtime | Exact command parsing and approval state | No broad semantic intent authority | No CSA needed for exact commands | Yes, structured approval authority remains | No for exact commands; yes for ambiguous prose before command boundary | Permanent approval responsibility | Aligned if command parser remains structured. |
| Resume and lifecycle runtimes | Exact lifecycle command parsing | No broad semantic authority | No CSA needed for exact commands | Yes, lifecycle authority remains | No for exact commands | Permanent lifecycle responsibility | Aligned. |
| Recommendation approval/follow-up | Yes for local prompt checks | Yes for approval/rejection/follow-up cues | Not primary | Structured command authority remains; prose semantics should not remain | Yes for ambiguous prose only | Shared during migration only | Narrow gap remains. |
| Replay persistence and reconstruction | No | No | Records CSA and route evidence | Yes, replay read-only authority remains | No | Permanent replay responsibility | Aligned. |
| Replay-derived improvement and gap classifiers | Yes, over replay evidence text | Yes | Indirect | No final semantic authority | Yes, for new-session structured CSA/replay provenance | Shared during migration only | Gap remains for token-scan classification. |
| Worker handoff entry detectors | Yes | Yes | Not primary | No, except structured lifecycle state | Yes | Shared during migration only | Gap remains across worker request, assignment, dispatch, invocation, execution, result capture, validation, and replay review detectors. |
| Worker runtime, invocation, dispatch, execution | No broad NL interpretation when entered through structured artifacts | No semantic source authority | Should consume structured handoff artifacts | Yes, worker boundary remains | No | Permanent worker responsibility | Aligned when detectors are separated from worker authority. |
| Explanation compatibility rendering | No final authority intended | May preserve compatibility language | Partial Governance -> Human UBTR integration | Rendering remains; semantic wording source should migrate | Yes for primary explanation semantics | Shared during migration only | Gap remains where compatibility renderer is primary. |
| LLM-assisted explanation | No authority; provider wording only | Advisory wording only | Indirect through authoritative state | Yes, renderer/advisory role remains | No semantic authority should be granted | Permanent non-authoritative renderer | Aligned if advisory flags remain. |
| Translation runtimes | Yes | Yes | Produce or consume translation artifacts | Yes, as UBTR | Already UBTR | Permanent UBTR responsibility | Aligned. |
| Provider orchestration | No final semantic authority should be owned | Provider suggestions may classify after deterministic failure | Not primary | Provider ownership remains advisory/non-authoritative | CSA should precede provider-assisted classification | Shared during migration only | Gap remains in provider-assisted intent classification. |
| Execution authorization | Some entry detectors interpret prompts | Authorization itself is structured | Not primary | Authorization authority remains; entry semantics should not | Yes for detector semantics | Mixed: detector transitional, authorization permanent | Gap remains in prompt detectors only. |
| Native development routing | Yes | Yes | Not primary | No | Yes | Shared during migration only | Gap remains. |
| Native development context intake | Yes | Yes | Not primary | Structured context authority remains; prompt semantics should migrate | Yes | Shared during migration only | Gap remains for prompt qualification. |
| Product 1 decision validation routing | Yes in specialized route checks | Yes | Not primary | Product 1 governance framing remains; semantic classification should not | Yes | Shared during migration only | Gap remains; must preserve AI Decision Validator framing. |
| Domain proposal and unknown-domain clarification | Yes | Yes | Not primary | Governance approval remains; semantic domain candidate should not | Yes | Shared during migration only | Gap remains. |
| Provider onboarding routing | Yes | Yes | Not primary | Provider governance remains; provider semantic extraction should not | Yes | Shared during migration only | Gap remains. |
| Semantic similarity/domain reference adaptation | Yes | Yes | Not primary | No | Yes | Shared during migration only | Gap remains. |
| Governance/replay/source-of-truth question resolvers | Yes, for governance-oriented prompts | Yes | Not primary | Structured source-of-truth and governance constraints remain | Yes for prompt semantics | Shared during migration only | Gap remains where prompt-oriented resolvers infer meaning. |
| Hardening runtime | Yes, over interaction text/evidence | Yes | Indirect | No semantic ownership | Yes, through structured CSA/replay fields for new sessions | Shared during migration only | Gap remains for token-scan scenario classification. |
| Legacy `intent_classifier.py` and older conversation runtime | Yes | Yes | No | No | Yes or retire | Compatibility-only | Retirement candidate after entrypoint audit. |

## 6. Remaining Migration Inventory

The remaining semantic migration inventory is:

1. Replay comparison substrate for every still-active natural-language consumer.
2. Proposal-only OCS routing from CSA no-execution/advisory/provider-needed semantics.
3. Remaining HIRR intake families beyond the Batch 02 ambiguous-intent subset.
4. HIRR clarification continuity and clarification reply refinement through linked original CSA and reply-turn CSA.
5. Human execution intent detection and execution authorization entry detectors.
6. Worker and domain lifecycle entry detectors that classify human prompts before structured lifecycle state exists.
7. Native development intent routing and native development context intake.
8. Specialized Product 1, domain proposal, unknown-domain, provider onboarding, and semantic similarity routing.
9. Provider-assisted intent classification, with CSA failure evidence required before provider advisory classification.
10. PPP/resource-selection CSA annotation, preserving structured PPP authority.
11. Explanation compatibility rendering, where Governance -> Human UBTR output should become primary only after section parity.
12. Replay-derived improvement, replay gap, hardening, and scenario classifiers that scan text instead of structured replay/CSA fields.
13. Legacy deterministic intent classifiers and older conversation entrypoints.

## 7. Duplicate Semantic Responsibility Report

Duplicate semantic responsibility remains in these areas:

| Duplicate Responsibility | UBTR Target | Current Duplicate Owner | Retirement Condition |
| --- | --- | --- | --- |
| Workflow identity from operator prompt | CSA `workflow_identity` and `semantic_identity` | ACLI `_classify_workflow()` | Route-by-route parity, replay lineage, fallback proof, full regression. |
| Governed-development route meaning | CSA development domain/action/entity fields | ACLI compatibility route and HIRR development classifier | Certified parity for all governed-development prompt families. |
| Ambiguous HIRR intake families | CSA ambiguity and clarification state | HIRR local intake markers | Family-by-family parity beyond Batch 02. |
| Clarification reply refinement | Linked original CSA and reply-turn CSA | HIRR continuity markers | Target preservation, ambiguity reduction, and unsafe escalation parity. |
| Proposal-only cognition meaning | CSA no-execution/advisory/cognition-needed fields | ACLI proposal-only marker classifier and HIRR post-clarification markers | OCS ownership preserved and proposal-only parity certified. |
| Generic execution and artifact-creation meaning | CSA execution intent and requested actions | `human_execution_intent_detection.py` and entry detectors | Fail-closed parity and approval boundary certification. |
| Worker/domain lifecycle entry meaning | CSA requested action plus structured lifecycle target | `detect_domain_*_entry_intent()` functions | Structured lifecycle entry or CSA parity for each detector. |
| Native development semantic target | CSA development action/domain/resource fields | Native development intent and context classifiers | Native catalog and context boundary parity. |
| Product/domain/provider specialized meaning | CSA domain, provider, Product 1, and entity fields | Specialized route markers | Route-family parity preserving Product 1 and provider/governance authority. |
| Provider-assisted intent suggestion | CSA deterministic failure and advisory escalation state | Provider-assisted intent classifier | CSA-first failure proof and provider advisory-only certification. |
| Explanation section semantics | Governance -> Human UBTR output | Compatibility explanation renderers | Operator section parity and source transparency. |
| Replay/hardening scenario classification | Structured CSA and replay provenance | Token scans over replay/interactions | New-session structured fields sufficient for classification; legacy scans retained. |
| Legacy broad intent classification | CSA workflow and semantic identity | `intent_classifier.py` and old conversation runtime | Entry point retirement or CSA parity certification. |

## 8. Retirement Candidates

The following are candidates for retirement after parity certification:

1. ACLI local workflow semantic marker cascades.
2. ACLI proposal-only OCS marker detection.
3. HIRR local semantic marker families not permanently tied to lifecycle state.
4. HIRR clarification reply semantic marker groups.
5. Human execution intent prompt-marker detection.
6. Worker and domain lifecycle prompt entry detectors.
7. Native development prompt and catalog semantic markers.
8. Product 1, provider onboarding, domain proposal, unknown-domain, and semantic similarity prompt markers.
9. Provider-assisted intent classification as a primary semantic fallback before CSA failure evidence exists.
10. Compatibility explanation wording as primary semantic projection.
11. Hardening and replay-derived token scans for new replay sessions.
12. Legacy deterministic intent classifier entrypoints.

The following are not retirement candidates:

- UBTR translation and CSA generation.
- HIRR clarification lifecycle orchestration.
- HIRR one-active-clarification invariant.
- HIRR reply binding and clarification chain continuity.
- OCS cognition ownership and provider selection boundaries.
- PPP structured validation and resource-selection authority.
- Approval exact command parsing and approval state.
- Resume and lifecycle exact command parsing.
- Replay read-only persistence and reconstruction.
- Worker execution, dispatch, invocation, result capture, and validation boundaries.
- Provider governance and credential boundaries.
- Execution authorization and fail-closed enforcement.
- Human authority and governance authority.

## 9. Implementation Priority

Recommended implementation order:

1. Platform-wide replay comparison substrate for remaining consumers.
2. Proposal-only OCS CSA migration.
3. Remaining HIRR intake-family CSA migration.
4. HIRR clarification reply and continuity CSA lineage.
5. Execution-intent and execution-authorization entry detector migration.
6. Worker/domain lifecycle entry detector migration.
7. Native development routing and context-intake migration.
8. Specialized Product 1, domain, provider, and semantic similarity route migration.
9. Provider-assisted intent classification CSA-first guard.
10. PPP/resource-selection CSA annotation.
11. Explanation rendering migration to Governance -> Human UBTR output where parity is proven.
12. Replay/hardening/replay-derived classifier replacement for new sessions.
13. Legacy classifier retirement audit.

This order preserves:

- governance authority;
- replay lineage;
- approval boundaries;
- PPP authority;
- worker boundaries;
- provider ownership;
- OCS cognition authority;
- Product 1 AI Decision Validator positioning.

## 10. Certification Impact

This audit does not identify:

- a governance bypass;
- an approval bypass;
- a replay mutation path;
- an OCS authority violation;
- a provider ownership violation;
- a worker boundary violation;
- a PPP authority violation;
- an execution authorization violation.

It does identify remaining semantic-responsibility gaps.

Certification language should therefore remain:

```text
UBTR is the canonical semantic architecture and is primary only for certified parity-proven consumer subsets.
Compatibility semantic consumers remain active, observable, rollback-capable, and subject to migration.
```

Certification language must not yet claim:

```text
UBTR is the exclusive runtime semantic source for every Platform Core consumer.
```

Future certification checkpoints must prove, for each migrated consumer:

- CSA or UBTR semantic field coverage;
- compatibility parity;
- previous compatibility source visibility;
- CSA hash/reference visibility;
- migration batch identifier;
- rollback behavior;
- replay reconstruction;
- no authority expansion into approval, PPP, workers, providers, OCS, governance, or execution.

## 11. Audit Conclusion

Platform Core semantic responsibility is architecturally aligned but not fully operationally aligned.

UBTR owns the final semantic boundary.

Several Platform Core subsystems still perform local natural-language interpretation or semantic intent classification for compatibility-era routing, clarification, lifecycle entry, explanation, hardening, or replay-derived decisions.

Those paths should migrate through parity-gated consumer batches rather than broad retirement.

Final verdict:

PLATFORM_SEMANTIC_RESPONSIBILITY_GAPS_REMAIN
