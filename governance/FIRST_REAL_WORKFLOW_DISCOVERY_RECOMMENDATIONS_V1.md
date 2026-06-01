# FIRST_REAL_WORKFLOW_DISCOVERY_RECOMMENDATIONS_V1

## Recommendation Summary

AiGOL should be adopted first for workflows where it can already provide high execution value and high explanation readiness.

## Immediate Adoption Candidates

Use AiGOL today for:

1. Governed milestone marker files.
2. New governance artifact skeleton files.
3. New ADR skeleton files.
4. Operational usage log files.
5. Acceptance evidence JSON stubs.
6. Replay certification JSON stubs.
7. Replay verification by operation id.
8. Governed operation status explanation.

These workflows are bounded, replayable, and explainable with current evidence.

## Do Not Prioritize Yet

Do not prioritize these until more evidence exists:

- provider expansion;
- orchestration;
- planning;
- reflection;
- multi-worker execution;
- broad GitHub automation.

## Strongest Future Workflow

The highest-value future workflow is:

```text
Operation replay ledger and usage summary
```

Reason:

- weekly usage already required manual counting;
- replay evidence is already rich;
- explanation quality would improve significantly with an operation-level ledger;
- this directly supports trust explanations.

## Recommended Next Development Priority

Build the smallest replay/operator reporting improvement that can answer:

```text
How many operations happened?
Which succeeded?
Which failed closed?
Which have reconstructable replay?
Which worker ran?
Which authorization scope was used?
```

This should remain a replay/operator UX improvement, not an execution expansion.

## Later Worker Candidates

After replay/operator reporting improves, the most evidence-aligned worker candidates are:

1. Repository inspection worker.
2. Structured JSON update worker.
3. Test runner evidence worker.
4. Append/update filesystem worker.
5. GitHub issue worker.

## Adoption Rule

AiGOL should be used when it can answer:

```text
What happened?
Why did it happen?
Why was it authorized?
Why should the result be trusted?
```

from replay-visible evidence.
