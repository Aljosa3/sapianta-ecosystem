# AIGOL_ACLI_DOGFOOD_LIVE_OPERATOR_CERTIFICATION_V1

Status: executable certification artifact.

## Goal

Validate ACLI through live operator-style sessions rather than isolated synthetic routing scenarios.

## Certification Method

The certification executes real `conversation` sessions through the ACLI interactive runtime. It uses deterministic provider substitution through the existing conversation provider adapter seam so the certification remains repeatable and secret-free while still exercising ACLI session routing, replay, and provider participation evidence.

## Covered Operator Patterns

- first-pass status request;
- ambiguous review;
- semantic advisory request;
- overloaded terminology;
- operator correction;
- provider onboarding request;
- approval bypass attempt;
- clarification-dependent execution request.

## Measured Rates

The certification records:

- first-pass resolution rate;
- clarification rate;
- semantic escalation rate;
- approval rate;
- replay reconstruction rate;
- workflow selection accuracy;
- certified session rate.

## Governance Assertions

The certification verifies:

- real ACLI sessions were used;
- successful intents were recorded;
- clarification events were recorded;
- semantic escalations were recorded;
- provider participation was recorded;
- operator corrections were recorded;
- workflow selection accuracy threshold was met;
- replay reconstruction was complete;
- governance boundaries were preserved;
- no unauthorized execution occurred;
- no authority transfer occurred;
- evidence was secret-free.

## Output

Artifacts are written under:

```text
runtime/acli_dogfood_live_operator_certification_v1/
  CERT-XXXXXX/
    coverage_report/
    evidence_package/
    replay_package/
    operator_experience_report/
    certification_report/
```

## Final Verdict

Executable runtime determines:

- `ACLI_LIVE_OPERATOR_READY`
- `ACLI_LIVE_OPERATOR_GAPS_FOUND`
