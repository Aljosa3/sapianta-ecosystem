# COGNITION_RUNTIME_COVERAGE_RECOMMENDATIONS_V1

## Status

Review-only recommendations.

## Primary Recommendation

Continue Trading Domain development while prioritizing cognition hardening in parallel.

Recommended choice:

```text
Continue Trading
```

## Justification

The coverage sweep showed:

- 100% representative prompt class coverage;
- 75% successful governed response coverage;
- 25% healthy fail-closed coverage;
- no worker invocation;
- no execution request creation;
- provider use remained proposal-only.

The remaining gaps affect cognition completeness and operator ergonomics, not the safety of explicit-input, evidence-only Trading Worker foundations.

## Recommended Cognition Hardening Order

1. `CONTEXT_ASSEMBLY_ARTIFACT_MODEL_V1`;
2. `DOMAIN_SELECTION_REGISTRY_V1`;
3. `PROVIDER_NECESSITY_POLICY_V1`;
4. `EVIDENCE_BOUND_CONVERSATION_RESPONSE_V1`;
5. `COGNITION_REPLAY_VISIBILITY_ROLLUP_V1`;
6. `COGNITION_RUNTIME_END_TO_END_CERTIFICATION_V1`.

## Recommended Trading Path

Proceed to:

```text
TRADING_DECISION_VALIDATION_TEST_FIXTURES_V1
```

Only create fixtures and evidence-only worker foundations that use explicit trading artifacts.

Do not rely on:

- inferred domain context;
- hidden context assembly;
- automatic provider necessity;
- implicit portfolio state;
- implicit market state.

## Recommended Coverage Improvements

Future coverage should include:

- real provider availability rerun;
- dashboard/current-status prompt cases;
- domain selection prompt cases;
- evidence-bound conversation prompt cases;
- unsafe prompt rejection cases;
- replay visibility rollup for every case;
- provider proposal-only verification for every provider-assisted case.

## Final Recommendation

Do not pause Trading Domain work.

Do harden cognition in parallel, because full cognition certification still depends on context assembly, domain selection, provider necessity policy, and replay visibility rollup.
