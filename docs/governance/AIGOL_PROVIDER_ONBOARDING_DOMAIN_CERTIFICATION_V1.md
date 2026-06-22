# AIGOL_PROVIDER_ONBOARDING_DOMAIN_CERTIFICATION_V1

Status: executable certification artifact.

## Goal

Certify that a normal operator can onboard and manage cognition providers through natural-language ACLI-style prompts without knowing AiGOL implementation details, vault internals, workflow identifiers, or provider lifecycle commands.

## Natural-Language Coverage

The certification covers:

- `Dodaj Claude kot cognition provider.`
- `Dodaj Gemini.`
- `Želim uporabljati Mistral.`
- `Onemogoči Claude.`

## Certified Domain Behavior

The Provider Onboarding Domain verifies:

- deterministic provider intent classification;
- provider registration visibility;
- vault onboarding;
- credential verification;
- provider management disable flow;
- certification workflow generation;
- execution summary before action;
- explicit human approval before execution;
- replay-visible evidence;
- no live provider or worker invocation during onboarding;
- secret-free evidence.

## Runtime Boundary

Provider onboarding is a governed management workflow. It may create or update credential-vault state after approval, but it does not grant the provider authority and does not invoke the provider as part of onboarding.

## Replay Output

Artifacts are written under:

```text
runtime/provider_onboarding_domain_certification_v1/
  CERT-XXXXXX/
    coverage_report/
    evidence_package/
    replay_package/
    certification_report/
```

## Success Criteria

The final verdict is `PROVIDER_ONBOARDING_DOMAIN_CERTIFIED` only when:

- natural-language requests route to provider onboarding or management workflows;
- supported providers are identified;
- vault onboarding and verification are visible;
- certification workflow generation is visible;
- execution summaries precede action;
- human approval is recorded;
- replay reconstructs all scenarios;
- evidence remains secret-free.

## Final Verdict

Executable runtime determines:

- `PROVIDER_ONBOARDING_DOMAIN_CERTIFIED`
- `PROVIDER_ONBOARDING_DOMAIN_GAPS_FOUND`
