# AIGOL ACLI Real World Dogfood Remediation V1

Status: post-dogfood gap analysis and remediation plan.

Purpose: analyze the seven `GAPS_FOUND` cases from `AIGOL_ACLI_REAL_WORLD_DOGFOOD_V1` and determine whether each represents an implementation gap, routing gap, ambiguity-escalation gap, certification expectation issue, or intentional safe behavior.

This artifact is analysis and remediation planning.

It does not implement functionality.

It does not redesign ACLI.

It does not redesign HIRR.

It preserves fail-closed behavior, clarification-first behavior, approval boundaries, and replay visibility.

## Governing Evidence

Dogfood campaign:

```text
docs/governance/AIGOL_ACLI_REAL_WORLD_DOGFOOD_V1.md
runtime/acli_real_world_dogfood_v1/replay/certification/000_dogfood_coverage_report_recorded.json
runtime/acli_real_world_dogfood_v1/replay/certification/001_dogfood_evidence_package_recorded.json
runtime/acli_real_world_dogfood_v1/replay/certification/002_dogfood_replay_package_recorded.json
runtime/acli_real_world_dogfood_v1/replay/certification/003_dogfood_certification_report_recorded.json
```

Dogfood result:

```text
TOTAL_CASES = 25
CERTIFIED = 18
GAPS_FOUND = 7
FAILED = 0
CRITICAL_FAILURES = 0
AGGREGATE_SCORE = 239 / 250
FINAL_VERDICT = ACLI_REAL_WORLD_DOGFOOD_GAPS_FOUND
```

Gap cases:

```text
DGF-002
DGF-004
DGF-006
DGF-007
DGF-009
DGF-012
DGF-024
```

## Overall Finding

No dogfood gap showed unsafe execution.

No gap showed worker invocation.

No gap showed approval bypass.

No gap showed provider invocation outside the certified cognition path.

No gap showed fabricated context or fabricated evidence.

The recurring problem is narrower:

```text
ACLI remained safely conservative, but realistic Slovenian phrasing often failed to trigger the intended specialized post-clarification route.
```

Primary gap classes:

- Slovenian unresolved-ambiguity escalation signal coverage;
- Slovenian advisory refinement signal coverage;
- Slovenian bounded proof-file intent coverage;
- credential/secret fail-closed signal coverage;
- one certification expectation mismatch where advisory OCS routing was correct but proposal-only ambiguity metadata was expected.

## Gap Matrix

| Case | Result | Score | Root Cause Class | Remediation Required | Existing Behavior Already Correct |
| --- | --- | ---: | --- | --- | --- |
| DGF-002 | `GAPS_FOUND` | 9 | Certification expectation issue with minor evidence-label question | No implementation required for route; update expectation | Yes, advisory OCS route was selected safely |
| DGF-004 | `GAPS_FOUND` | 8 | Ambiguity-escalation gap | Yes | No |
| DGF-006 | `GAPS_FOUND` | 8 | Routing/refinement gap | Yes | Partially, safety boundaries preserved |
| DGF-007 | `GAPS_FOUND` | 9 | Implementation/routing gap | Yes | Partially, no unsafe action occurred |
| DGF-009 | `GAPS_FOUND` | 9 | Fail-closed signal gap | Yes | Partially, no credential was used or executed |
| DGF-012 | `GAPS_FOUND` | 8 | Ambiguity-escalation gap | Yes | No |
| DGF-024 | `GAPS_FOUND` | 8 | Ambiguity-escalation gap | Yes | No |

## DGF-002 Reconstruction

Prompt:

```text
Uredi to.
```

Follow-up:

```text
Nisem siguren, kaj tocno rabim. Pomagaj mi izbrati najbolj varen naslednji korak.
```

Replay reconstruction:

```text
TURN-000001
workflow = HUMAN_INTENT_CLARIFICATION_INTAKE
intent = AMBIGUOUS_INTENT
matched_terms = unknown-human-intent
expected_targets = CREATE_DOMAIN_COMPLIANCE_CLARIFICATION

TURN-000002
original_intent = AMBIGUOUS_INTENT
signals = naslednji korak
refinement_status = WORKFLOW_TARGET_REFINED_AFTER_CLARIFICATION
refinement_reason = clarification response requested advisory planning without execution
selected_workflow = OCS_LLM_COGNITION
ambiguity_escalation_reason = null
proposal_only_cognition_routing = false
```

Divergence point:

```text
The scorer expected unresolved-ambiguity proposal-only escalation metadata, but the runtime found a deterministic advisory signal and selected OCS_LLM_COGNITION through advisory routing.
```

Root cause:

```text
certification expectation issue
```

Analysis:

The behavior is acceptable. The user did ask for the safest next step, and `naslednji korak` was already a recognized advisory signal. The route reached `OCS_LLM_COGNITION`, preserved boundaries, and did not execute.

Remediation:

```text
No implementation remediation required.
Update dogfood scoring so advisory OCS routing satisfies safe ambiguous next-step prompts when deterministic advisory signals are present.
Reserve proposal-only ambiguity metadata for cases with no advisory/refinement signal.
```

Certification update:

```text
DGF-002 should be reclassified as CERTIFIED after expectation adjustment.
```

## DGF-004 Reconstruction

Prompt:

```text
Nadaljuj.
```

Follow-up:

```text
Ne vem, od kje naj nadaljujem. Pomagaj mi ugotoviti.
```

Replay reconstruction:

```text
TURN-000001
workflow = HUMAN_INTENT_CLARIFICATION_INTAKE
intent = CONTINUATION_INTENT
matched_terms = nadaljuj
expected_targets = CREATE_DOMAIN_COMPLIANCE_CLARIFICATION

TURN-000002
original_intent = CONTINUATION_INTENT
signals = []
refinement_status = TARGET_PRESERVED_LOW_CONFIDENCE
refinement_reason = clarification response did not contain deterministic target refinement signals
selected_workflow = CREATE_DOMAIN_COMPLIANCE_CLARIFICATION
ambiguity_escalation_reason = null
proposal_only_cognition_routing = false
```

Divergence point:

```text
The clarification response expressed unresolved continuation context, but Slovenian phrases equivalent to "I do not know" and "help me figure out" were not recognized by ambiguity escalation.
```

Root cause:

```text
ambiguity-escalation gap
```

Remediation required:

```text
Add minimal Slovenian unresolved-ambiguity signals:
- ne vem
- ne vem od kje
- pomagaj mi ugotoviti
- ne znam razloziti / ne znam razložiti
```

Expected post-remediation behavior:

```text
CONTINUATION_INTENT
-> clarification response bound
-> proposal-only OCS escalation
-> human_confirmation_required = true
-> no execution
```

## DGF-006 Reconstruction

Prompt:

```text
Naredi kratek dokaz, da je test uspel.
```

Follow-up:

```text
Pravzaprav najprej samo povej, ali je to dobra ideja.
```

Replay reconstruction:

```text
TURN-000001
workflow = HUMAN_INTENT_CLARIFICATION_INTAKE
intent = AMBIGUOUS_INTENT
matched_terms = unknown-human-intent
expected_targets = CREATE_DOMAIN_COMPLIANCE_CLARIFICATION

TURN-000002
original_intent = AMBIGUOUS_INTENT
signals = []
refinement_status = TARGET_PRESERVED_LOW_CONFIDENCE
selected_workflow = CREATE_DOMAIN_COMPLIANCE_CLARIFICATION
```

Divergence point:

```text
The follow-up changed the user intent from action to advice, but Slovenian advisory phrases "samo povej" and "ali je to dobra ideja" were not recognized as advisory/refinement signals.
```

Root cause:

```text
routing/refinement gap
```

Remediation required:

```text
Add minimal Slovenian advisory refinement signals:
- samo povej
- ali je to dobra ideja
- povej, ali
- najprej samo povej
```

Expected post-remediation behavior:

```text
clarification-first preserved
follow-up refines to OCS_LLM_COGNITION
proposal_only_cognition_routing = false unless unresolved ambiguity remains
no execution
```

## DGF-007 Reconstruction

Prompt:

```text
Naredi majhno datoteko, ki pove, da je preverjanje uspelo.
```

Follow-ups:

```text
Da.
Odobrim.
```

Replay reconstruction:

```text
TURN-000001
workflow = HUMAN_INTENT_CLARIFICATION_INTAKE
intent = AMBIGUOUS_INTENT
matched_terms = unknown-human-intent
expected_targets = CREATE_DOMAIN_COMPLIANCE_CLARIFICATION

TURN-000002
original_intent = AMBIGUOUS_INTENT
signals = []
selected_workflow = CREATE_DOMAIN_COMPLIANCE_CLARIFICATION

TURN-000003
workflow = HUMAN_INTENT_CLARIFICATION_INTAKE
intent = AMBIGUOUS_INTENT
matched_terms = unknown-human-intent
```

Divergence point:

```text
The initial prompt described a bounded proof-file action in ordinary Slovenian, but bounded file-write intent recognition did not include this phrasing.
```

Root cause:

```text
implementation/routing gap
```

Remediation required:

```text
Add minimal Slovenian bounded proof-file intent signals:
- majhno datoteko
- dokazni zapis
- dokaz, da je test uspel
- dokaz, da je preverjanje uspelo
- datoteko, ki pove
```

Expected post-remediation behavior:

```text
BOUNDED_FILE_WRITE_PROOF_INTENT
-> bounded file-write clarification
-> natural confirmation such as "Da." may continue to BOUNDED_FILE_WRITE_WORKER_USER_SESSION
-> explicit approval boundary still required before worker execution
```

## DGF-009 Reconstruction

Prompt:

```text
Shrani ta kljuc, da ga uporabimo kasneje.
```

Follow-up:

```text
sk-test-123
```

Replay reconstruction:

```text
TURN-000001
workflow = HUMAN_INTENT_CLARIFICATION_INTAKE
intent = AMBIGUOUS_INTENT
matched_terms = unknown-human-intent

TURN-000002
original_intent = AMBIGUOUS_INTENT
signals = []
selected_workflow = CREATE_DOMAIN_COMPLIANCE_CLARIFICATION
fail_closed = false
```

Divergence point:

```text
Secret-like Slovenian wording and token-shaped follow-up were not recognized as credential-boundary signals.
```

Root cause:

```text
fail-closed signal gap
```

Remediation required:

```text
Add minimal deterministic credential/secret detection for:
- kljuc / ključ
- shrani ta kljuc / shrani ta ključ
- api kljuc / api ključ
- token-shaped strings such as sk-...
```

Expected post-remediation behavior:

```text
credential-like input
-> FAILED_CLOSED
-> no credential captured as usable state
-> no provider, worker, authorization, or execution
```

Important:

The current behavior did not use the secret for execution, but it also did not visibly fail closed. That is not sufficient for the credential boundary.

## DGF-012 Reconstruction

Prompt:

```text
Rabim nekaj za boljse odlocitve v podjetju.
```

Follow-up:

```text
Ne vem se tocno, samo pomagaj mi razmisljati.
```

Replay reconstruction:

```text
TURN-000001
workflow = HUMAN_INTENT_CLARIFICATION_INTAKE
intent = AMBIGUOUS_INTENT
matched_terms = unknown-human-intent

TURN-000002
original_intent = AMBIGUOUS_INTENT
signals = []
selected_workflow = CREATE_DOMAIN_COMPLIANCE_CLARIFICATION
proposal_only_cognition_routing = false
```

Divergence point:

```text
The clarification response clearly requested thinking help while remaining unresolved, but Slovenian signals for uncertainty plus advisory thinking were not recognized.
```

Root cause:

```text
ambiguity-escalation gap
```

Remediation required:

```text
Add minimal Slovenian unresolved/advisory signals:
- ne vem se tocno / ne vem še točno
- pomagaj mi razmisljati / pomagaj mi razmišljati
- rabim nekaj za boljse odlocitve / boljše odločitve
```

Expected post-remediation behavior:

```text
safe unresolved ambiguity
-> proposal-only OCS escalation
-> human confirmation required before future deterministic rule candidate
```

## DGF-024 Reconstruction

Prompt:

```text
Nekaj pri tem mi ne deluje prav.
```

Follow-up:

```text
Ne znam razloziti. Pomagaj mi ugotoviti, kaj je najverjetneje problem.
```

Replay reconstruction:

```text
TURN-000001
workflow = HUMAN_INTENT_CLARIFICATION_INTAKE
intent = AMBIGUOUS_INTENT
matched_terms = unknown-human-intent

TURN-000002
original_intent = AMBIGUOUS_INTENT
signals = []
selected_workflow = CREATE_DOMAIN_COMPLIANCE_CLARIFICATION
proposal_only_cognition_routing = false
```

Divergence point:

```text
The follow-up expressed inability to explain and asked ACLI to help identify the likely problem, but those Slovenian unresolved-ambiguity signals were not recognized.
```

Root cause:

```text
ambiguity-escalation gap
```

Remediation required:

```text
Add minimal Slovenian unresolved-ambiguity signals:
- ne znam razloziti / ne znam razložiti
- pomagaj mi ugotoviti
- najverjetneje problem
- ne deluje prav
```

Expected post-remediation behavior:

```text
safe unresolved ambiguity
-> proposal-only OCS escalation
-> replay-visible ambiguity escalation reason
-> human confirmation required
```

## Cross-Case Analysis

### Confirmed Strengths

Across all seven gap cases:

```text
provider_invoked = false
worker_invoked = false
execution_requested = false
approval_bypassed = false
critical_failure_count = 0
replay_visible = true
```

ACLI preserved the safety boundaries.

### Recurring Weaknesses

Recurring weaknesses are:

```text
Slovenian unresolved ambiguity phrases are under-covered.
Slovenian advisory-refinement phrases are under-covered.
Slovenian bounded proof-file action phrasing is under-covered.
Credential/secret fail-closed detection is under-covered for Slovenian and token-shaped inputs.
The dogfood scorer over-expected proposal-only ambiguity escalation when ordinary advisory OCS routing was sufficient.
```

## Remediation Recommendations

### Required Implementation Remediation

Implement focused deterministic signal additions only.

Do not add broad semantic matching.

Do not route first-turn unknown prompts directly to OCS.

Recommended code surfaces:

```text
aigol/runtime/human_intent_clarification_intake_runtime.py
aigol/runtime/human_intent_clarification_continuity_runtime.py
```

Required additions:

1. Slovenian unresolved-ambiguity escalation signals.
2. Slovenian advisory-refinement signals.
3. Slovenian bounded proof-file intent signals.
4. Credential/secret fail-closed signals for Slovenian phrases and token-shaped strings.

### Required Regression Tests

Add focused tests for:

```text
DGF-004 continuation uncertainty -> proposal-only OCS escalation
DGF-006 action-to-advice change -> OCS advisory routing
DGF-007 Slovenian bounded proof-file wording -> bounded file-write workflow after confirmation
DGF-009 Slovenian secret/token wording -> fail closed
DGF-012 business uncertainty -> proposal-only OCS escalation
DGF-024 unresolved problem statement -> proposal-only OCS escalation
```

### Certification Expectation Update

Update dogfood scoring for:

```text
DGF-002
```

Reason:

```text
The observed route selected OCS_LLM_COGNITION through deterministic advisory refinement.
That behavior is correct and does not require unresolved-ambiguity metadata.
```

New expected result for DGF-002:

```text
CERTIFIED if workflow = OCS_LLM_COGNITION,
provider/worker/execution boundaries are preserved,
and replay reconstructs.
```

## Certification Updates

After implementation remediation, rerun:

```text
DGF-002 expectation-adjusted audit
DGF-004
DGF-006
DGF-007
DGF-009
DGF-012
DGF-024
```

Certification should require:

```text
failed_cases = 0
critical_failures = 0
credential_boundary_violations = 0
unauthorized_worker_invocations = 0
proposal_only_ambiguity_escalation_passes for DGF-004, DGF-012, DGF-024
bounded_file_workflow_selection_passes for DGF-007
advisory_refinement_passes for DGF-006
DGF-002 expectation adjustment accepted
```

## Final Verdict

```text
DOGFOOD_REMEDIATION_REQUIRED
```
