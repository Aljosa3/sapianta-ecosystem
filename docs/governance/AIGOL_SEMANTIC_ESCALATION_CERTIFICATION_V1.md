# AIGOL_SEMANTIC_ESCALATION_CERTIFICATION_V1

Status: executable certification artifact.

## Goal

Certify that ACLI can safely use external cognition providers to resolve ambiguous natural-language intent while preserving governance boundaries.

## Certification Scope

The certification covers:

- ambiguous requests;
- incomplete requests;
- overloaded terminology;
- multiple plausible interpretations;
- domain ambiguity;
- Slovenian natural-language prompts;
- mixed-language prompts.

## Required Behavior

For each scenario:

1. ACLI attempts deterministic resolution first.
2. Low-confidence deterministic resolution escalates to `OCS_LLM_COGNITION`.
3. A cognition provider returns a proposal-only semantic interpretation.
4. The human confirms the interpretation.
5. Workflow selection occurs only after confirmation.
6. No execution occurs before confirmation.
7. Provider usage metrics and cognition participation are replay-visible.
8. The provider never receives authority.

## Replay Artifacts

The runtime writes:

- `SEMANTIC_ESCALATION_DETERMINISTIC_ATTEMPT_ARTIFACT_V1`
- `SEMANTIC_ESCALATION_PROVIDER_PROPOSAL_ARTIFACT_V1`
- `SEMANTIC_ESCALATION_HUMAN_CONFIRMATION_ARTIFACT_V1`
- `SEMANTIC_ESCALATION_WORKFLOW_SELECTION_ARTIFACT_V1`
- `SEMANTIC_ESCALATION_AUTHORITY_BOUNDARY_ARTIFACT_V1`
- provider usage metric artifacts;
- cognition participation artifacts.

## Output

Artifacts are written under:

```text
runtime/semantic_escalation_certification_v1/
  CERT-XXXXXX/
    coverage_report/
    evidence_package/
    replay_package/
    certification_report/
```

## Success Criteria

The final verdict is `SEMANTIC_ESCALATION_CERTIFIED` only when deterministic low-confidence routing, provider escalation, semantic proposal capture, human confirmation, post-confirmation workflow selection, provider metrics, participation metrics, no-authority-transfer evidence, replay reconstruction, and secret-free evidence all pass.

## Final Verdict

Executable runtime determines:

- `SEMANTIC_ESCALATION_CERTIFIED`
- `SEMANTIC_ESCALATION_GAPS_FOUND`
