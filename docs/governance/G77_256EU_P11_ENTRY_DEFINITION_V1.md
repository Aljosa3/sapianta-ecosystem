# G77-256EU P11 Entry Definition V1

Status: Human-authorized constitutional semantic definition.

Version: `1.0.0`

Identity: `P11_ENTRY_DEFINITION_V1`

Effective scope: prospective P11 semantic classification and counter evidence from the first commit containing this artifact onward.

Authority origin: the explicit Human G77-256EU constitutional authorization, authenticated against repository baseline commit `34a6343e229042ab1d435444687fe5d665b90724` and tree `6c042e3fe1ccbab3389d4cab401e4598f6479adf`.

This artifact formalizes the Human decision. It does not originate independent authority, authorize operational execution, modify historical evidence, award E05 credit, enter P12, create a production route, or certify the reusable P11/SPCE substrate.

## 1. Canonical definition

A P11 entry occurs only when all of the following are true for one exact request:

1. the request reaches the governed P11 constitutional boundary;
2. all constitutionally required pre-attempt controls applicable to the request pass;
3. the request is constitutionally admitted to begin a P11 attempt; and
4. the P11 attempt actually begins.

The conjunction is exact:

```text
P11_ENTRY =
BOUNDARY_REQUEST
AND PRE_ATTEMPT_GATES_PASS
AND P11_ATTEMPT_AUTHORIZED
AND P11_ATTEMPT_START
```

A request rejected before P11 attempt start does not increment `P11_ENTRY_COUNT`. The rejected request remains evidence-visible as a boundary request and, when its pre-attempt denial is classifiable, as a pre-attempt denial.

```text
BOUNDARY_REQUEST != P11_ENTRY
PRE_ATTEMPT_DENIAL != P11_ENTRY
DENIAL_EVIDENCE != ABSENCE_OF_REQUEST
```

## 2. Canonical event vocabulary

The prospective evidence model distinguishes these event classes:

| Event | Meaning | Counter effect |
|---|---|---|
| `BOUNDARY_REQUEST` | One request reached the governed P11 boundary. | `BOUNDARY_REQUEST_COUNT += 1` |
| `PRE_ATTEMPT_GATE_EVALUATION` | All controls applicable before attempt start were evaluated. | No entry increment by itself. |
| `PRE_ATTEMPT_DENIAL` | A boundary request was denied before attempt authorization and start. | `PRE_ATTEMPT_DENIAL_COUNT += 1`; `P11_ENTRY_COUNT += 0` |
| `P11_ATTEMPT_AUTHORIZED` | The exact request passed all pre-attempt gates and was admitted to start. | No entry increment without actual start. |
| `P11_ATTEMPT_START` | The authorized admitted attempt actually began. | Causes exactly one `P11_ENTRY` for that attempt. |
| `P11_ENTRY` | The conjunction in section 1 became true. | `P11_ENTRY_COUNT += 1` exactly once. |
| `P11_OPERATIONAL_INVOCATION` | The existing governed operational invocation event. | `P11_OPERATIONAL_INVOCATION_COUNT += 1` under its existing meaning. |
| `PROTECTED_EFFECT` | The existing protected effect event. | `PROTECTED_EFFECT_COUNT += 1` under its existing meaning. |

This definition does not silently redefine invocation or protected-effect semantics.

## 3. Required invariants

### 3.1 Negative invariant

```text
PRE_ATTEMPT_DENIAL
=> P11_ATTEMPT_AUTHORIZED = FALSE
=> P11_ATTEMPT_START = FALSE
=> P11_ENTRY_INCREMENT = 0
```

### 3.2 Positive invariant

```text
P11_ATTEMPT_START = TRUE
=> PRE_ATTEMPT_GATES_PASS = TRUE
AND P11_ATTEMPT_AUTHORIZED = TRUE
AND P11_ENTRY_INCREMENT = EXACTLY_ONE
```

### 3.3 Cardinality and visibility invariants

- A single admitted attempt increments `P11_ENTRY_COUNT` no more than once.
- A denied boundary request remains evidence-visible.
- A classifiable pre-attempt denial without denial evidence is invalid evidence.
- A boundary request alone never proves a P11 entry.
- An unknown or unclassifiable semantic state fails closed and never increments `P11_ENTRY_COUNT` by inference.
- `BOUNDARY_REQUEST_COUNT` is not a substitute for `P11_ENTRY_COUNT`.
- `P11_ENTRY_COUNT` is not a substitute for `P11_OPERATIONAL_INVOCATION_COUNT`.
- `P11_OPERATIONAL_INVOCATION_COUNT` is not a substitute for `PROTECTED_EFFECT_COUNT`.
- A protected effect cannot be inferred from request, denial, entry, or invocation counters.
- These semantics create no P12 or production authority.

## 4. Canonical counter model

The prospective counter model is:

| Counter | Increment condition |
|---|---|
| `BOUNDARY_REQUEST_COUNT` | Exactly once when a request reaches the governed P11 boundary. |
| `PRE_ATTEMPT_DENIAL_COUNT` | Exactly once when that request is classifiably denied before attempt start. |
| `P11_ENTRY_COUNT` | Exactly once when an admitted P11 attempt actually begins. |
| `P11_OPERATIONAL_INVOCATION_COUNT` | Under the unchanged existing invocation semantics. |
| `PROTECTED_EFFECT_COUNT` | Under the unchanged existing protected-effect semantics. |
| `SECOND_PROTECTED_EFFECT_COUNT` | Counts a protected effect after the first protected effect within the bounded one-use lifecycle; the required one-use value is zero. |

For the canonical one-use `CONSUMED` lifecycle containing one admitted request followed by one denied reuse request, the normative expected model is:

```text
BOUNDARY_REQUEST_COUNT = 2
PRE_ATTEMPT_DENIAL_COUNT = 1
P11_ENTRY_COUNT = 1
P11_OPERATIONAL_INVOCATION_COUNT = 1
PROTECTED_EFFECT_COUNT = 1
SECOND_PROTECTED_EFFECT_COUNT = 0
```

## 5. Canonical lifecycle example

```text
REQUEST_1
  -> BOUNDARY_REQUEST
  -> PRE_ATTEMPT_GATE_EVALUATION = PASS
  -> P11_ATTEMPT_AUTHORIZED
  -> P11_ATTEMPT_START
  -> P11_ENTRY_COUNT += 1
  -> permitted invocation and effect under existing authority
  -> authority becomes CONSUMED

REQUEST_2
  -> BOUNDARY_REQUEST
  -> PRE_ATTEMPT_GATE_EVALUATION = DENY_CONSUMED
  -> PRE_ATTEMPT_DENIAL_COUNT += 1
  -> P11_ATTEMPT_AUTHORIZED = FALSE
  -> P11_ATTEMPT_START = FALSE
  -> P11_ENTRY_COUNT += 0
  -> PROTECTED_EFFECT_COUNT += 0
```

A denied reuse request after one-use authority becomes `CONSUMED` is not a second P11 entry when denial occurs before attempt start.

## 6. Prospective evidence requirements

Future operational evidence claiming conformance to this definition must preserve, for every boundary request:

- a stable request identity;
- evidence that the request reached the governed boundary;
- the pre-attempt gate disposition;
- explicit attempt-authorization state;
- explicit attempt-start state or a separately certified deterministic mapping to an existing durable event;
- the independently counted entry, invocation, and effect events;
- denial evidence for every classifiable pre-attempt denial; and
- fail-closed treatment of unknown semantic state.

An evidence producer must not derive `P11_ENTRY_COUNT` from API call count, boundary-request count, invocation count, or effect count.

This repository-only generation does not alter the historical ER harness or operational consumer. Prospective operational instrumentation remains a separate bounded implementation and authorization concern.

## 7. Historical immutability and credit boundary

This definition is prospective and normative. It does not silently rewrite, replace, erase, normalize, or reinterpret ER, ES, or ET evidence. Historical counters remain the exact historical observations that were committed.

A historical compatibility assessment may compare persisted facts with this definition, but it must disclose missing direct mappings and must not mutate credit.

```text
E05_BEFORE = 5/18
E05_AFTER = 5/18
E05_REMAINING = 13
CONSUMED_CONSTITUTIONAL_CREDIT_STATE = UNSATISFIED
RETROACTIVE_E05_CREDIT_AUTHORIZED = NO
```

## 8. Non-authority boundary

This definition does not authorize:

- a VM, overlay, NoCloud seed, QEMU invocation, boot, or materialization;
- commissioning, P11 execution, CONSUMED execution, or another E05 case;
- creation or invocation of a Human operational act;
- automatic retry or repair-and-continue;
- P12 entry or production routing;
- a parallel P11 implementation, counter dialect, validator path, or SPCE executor;
- certification of `REUSABLE_P11_SPCE_EXECUTION_SUBSTRATE`; or
- automatic continuation.

The constitutional optimization remains:

```text
FORMALIZE -> REUSE -> BIND -> VERIFY
```

Common semantics may be reused only with per-generation identity and applicability reauthentication and fresh vector-specific evidence.
