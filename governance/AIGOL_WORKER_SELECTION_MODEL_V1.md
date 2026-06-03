# AIGOL_WORKER_SELECTION_MODEL_V1

## Status

Worker selection model.

## Purpose

Worker selection determines which existing Worker, if any, is eligible for a governed task.

Selection is deterministic, replay-visible, and fail-closed.

Selection does not dispatch or invoke Workers.

## Selection Inputs

Worker selection requires:

- task packet;
- domain id;
- requested capability;
- required Worker family;
- authority profile requirement;
- trust requirement;
- dependency requirements;
- replay contract requirement;
- governance authorization status;
- Worker registry hash;
- Worker capability hash.

## Selection Output

Selection should produce:

```text
WORKER_SELECTION_DECISION_V1
```

containing:

- selected Worker id;
- selected Worker version;
- selected Worker family;
- selected capability id;
- selected authority profile;
- selection reason;
- rejected Workers and reasons;
- reuse-or-create recommendation;
- policy version;
- policy hash;
- registry hash;
- replay references;
- fail-closed status.

## Selection Order

Selection should evaluate:

1. governance authorization presence;
2. domain compatibility;
3. Worker family compatibility;
4. capability compatibility;
5. authority profile compatibility;
6. trust threshold;
7. dependency satisfaction;
8. replay contract compatibility;
9. lifecycle status;
10. deterministic tie-breaker.

## Reuse Existing Worker

Select reuse when:

- at least one certified or available Worker satisfies the task;
- no authority expansion is needed;
- dependencies are available;
- replay contract matches;
- trust level satisfies policy.

## Create New Worker

Recommend new Worker creation when:

- no existing Worker satisfies capability requirements;
- all existing options fail for structural reasons;
- requested capability is valid under domain policy;
- new Worker foundation can be proposed through PPP;
- creation remains non-executing until governed implementation and certification.

The selection model may recommend creation.

It must not create the Worker.

## Worker Upgrade Recommendation

Recommend upgrade when:

- existing Worker family is appropriate;
- current version lacks a bounded capability;
- authority boundary can remain stable;
- upgrade can be proposed through PPP;
- replay and dependency changes are explicit.

## Worker Repair Recommendation

Recommend repair when:

- Worker failed validation or execution;
- failure is localized;
- capability and authority remain valid;
- repair can be proposed through PPP.

## Worker Deprecation Recommendation

Recommend deprecation when:

- Worker is unsafe;
- Worker is obsolete;
- Worker is repeatedly failing;
- replacement exists;
- dependency migration is possible;
- historical replay remains preserved.

## Deterministic Tie-Breaking

Allowed tie-breakers:

- explicit governance priority;
- highest trust level;
- most recent certified version;
- lowest dependency burden;
- strongest replay compatibility;
- lexical Worker id as final fallback.

Random selection is prohibited.

## Authority Boundaries

Worker selection must not:

- invoke Workers;
- dispatch;
- execute;
- create Workers;
- upgrade Workers;
- repair Workers;
- mutate governance;
- mutate replay except append-only selection evidence when implemented.

