# G35-09 Canonical Condensation Exact G31 Input-Binding Dataflow Closure Audit

Status: CONSTITUTIONAL CONTRACT-CLOSURE AUDIT
Version: 1.0.0
Date: 2026-07-28
Authority: Platform Core constitutional development audit
Mutation authority: NONE

## 1. Executive Summary

This audit closes the exact-dataflow ambiguity between an approved
condensation and the unchanged G31 synthesis preflight.

None of Candidate Models A, B, or C is exact. The selected normative model is
**Model D — Stored Body Argument / Approved Full Projection**:

```text
P := exact versioned prefix "runtime validation: "
B := exact stored approved_synthesis_body
F := exact stored approved_projection

F == P + B
g31_preflight_argument == B
g31_preflight_final_request == F
authorized_task == B
```

The distinction between `g31_preflight_argument` and
`g31_preflight_final_request` is mandatory. The unchanged function
`preflight_codex_worker_synthesis(...)` accepts the unprefixed body as its
argument and constructs the prefixed, measured request internally. Passing
`F` as that function argument would produce `P + F` and double the prefix.

The human approves the source-bound review envelope, including `P`, `B`, and
`F` as separately displayed immutable values and their exact commitments.
No task byte used as G31 input or as the CODEX `authorized_task` may be absent
from that envelope. Existing third activation approval continues to bind the
complete generated CODEX prompt.

The accepted nine-owner scope remains sufficient. Generic synthesis, handoff,
execution-authorization, execution-gate, Worker, Provider, and task-outcome
schemas remain unchanged.

## 2. Certified Baseline

This audit treats G0 through G30 as certified, closed, and immutable and
accepts these Generation 35 determinations:

- G35-04: the existing 240-code-point preflight correctly fails closed;
- G35-05: condensation requires immutable source, deterministic validation,
  exact human approval, full projection, Replay, and unchanged downstream G31;
- G35-06: only the G31 input-binding contract requires constitutional revision;
- G35-07: the capability lifecycle, compatibility modes, and certification
  ordering are established; and
- G35-08: condensation-specific propagation into generic downstream contracts
  is unnecessary and prohibited.

The current G31 preflight remains unchanged:

```text
CODEX_SYNTHESIS_PREFIX = "runtime validation: "
CODEX_SYNTHESIS_MAXIMUM_CHARACTER_COUNT = 240
raw = required_string(function_argument)
final = CODEX_SYNTHESIS_PREFIX + raw
within_bound = len(final) <= 240
```

The existing `required_string` operation rejects empty values and returns
`value.strip()`. This audit does not authorize changing that behavior.

### 2.1 Static repository evidence

| Evidence | Architectural fact |
| --- | --- |
| `aigol/runtime/codex_worker_activation_binding_runtime.py:84-85,112-127` | G31 owns the exact prefix and 240-code-point bound; preflight receives an unprefixed string and constructs the final request. |
| `aigol/runtime/codex_worker_activation_binding_runtime.py:220-260` | Preflight reconstruction proves prefix, counts, final string, handoff, prompt, and hash continuity. |
| `aigol/runtime/codex_worker_activation_binding_runtime.py:264-317,814-870` | Activation currently uses one reconstructed original string for both preflight and `authorized_task`; this is the single required distinction point. |
| `aigol/runtime/codex_worker_activation_binding_runtime.py:1044-1047` | The unchanged required-string helper applies `strip()`, requiring the fixed-point admissibility rule for approved bodies. |
| `aigol/runtime/platform_implementation_turn_durable_work_binding.py:168-177` | Existing source lineage already preserves the original request and its hash. |
| `sapianta_system/runtime/codex_synthesis/governed_codex_task_request.py:20-53` | The generic Worker contract already accepts and hashes any exact `authorized_task`. |
| `sapianta_system/runtime/codex_synthesis/governed_codex_task_response.py:19-50` | Existing synthesis validation already proves that its natural-language request ends with the exact authorized task. |
| `sapianta_system/runtime/codex_handoff/governed_codex_handoff_response.py:22-47` | Existing handoff identity already binds prompt and Worker contract generically. |
| `aigol/runtime/codex_task_outcome_human_review_runtime.py:565-590` | Existing outcome review already separates original context, grounded project goal, authorized Worker task, and final prompt. |

## 3. Constitutional Invariants

1. The immutable original source request remains primary intent authority.
2. The completed objective remains the primary operational interpretation
   traceably bound to the original source and clarification.
3. Condensation is a representation proposal, not a new source of intent.
4. Condensation validation is deterministic, read-only, and non-authoritative.
5. Human approval binds the exact source, proposal, validation, prefix, body,
   full projection, and their hashes.
6. `P`, `B`, and `F` are distinct named values even where one is constructed
   from the others.
7. `F == P + B` is an exact code-point and UTF-8-byte equality.
8. The unchanged G31 function argument is `B`; the request constructed,
   measured, and hashed by G31 is `F`.
9. The CODEX Worker contract's `authorized_task` is exactly `B`.
10. No normalization, trimming, line-ending conversion, truncation,
    re-encoding substitution, or rewriting may occur after approval.
11. Existing execution Authorization remains independent and unchanged.
12. Existing downstream generic schemas receive ordinary exact task and
    contract values, not condensation-specific fields.
13. Direct V1 downstream artifacts remain byte-for-byte unchanged.
14. Any ambiguity, missing evidence, or equality failure terminates fail closed
    before Worker activation.

## 4. Exact Terminology

| Term | Normative meaning |
| --- | --- |
| `original_source_request` (`O`) | Exact immutable human request preserved by its existing source artifact and source-content commitment. |
| `completed_objective` | Existing clarification-complete operational objective bound to `O`; it does not replace `O`. |
| `condensation_proposal` (`C`) | Immutable non-authoritative artifact containing semantic commitments, requirement map, and proposed body. |
| `projection_prefix` (`P`) | Exact string `runtime validation: ` owned by unchanged G31 preflight; 20 Unicode code points and 20 UTF-8 bytes. |
| `approved_synthesis_body` (`B`) | Exact stored `proposed_synthesis_body` approved by Human Authority after validation. |
| `approved_projection` (`F`) | Exact stored full request `P + B` approved for G31 admission. |
| `g31_preflight_argument` | Exact Python `str` supplied as the first argument to unchanged `preflight_codex_worker_synthesis(...)`; normatively `B`. |
| `g31_preflight_final_request` | Exact `final_synthesized_request` constructed, counted, and hashed inside preflight; normatively `F`. |
| `authorized_task` | Exact task data placed in the existing generic CODEX Worker execution contract; normatively `B`. |
| input-binding artifact | Non-authoritative artifact selecting one compatibility mode and proving exact source/body/projection/preflight continuity. |
| content hash | Lowercase hexadecimal SHA-256 of the exact UTF-8 bytes of one string. |
| artifact hash | Existing canonical JSON Replay hash over an artifact, separate from raw string content hashes. |

The term `g31_preflight_input` is too ambiguous for a constitutional contract.
Where retained in presentation text, it MUST be qualified as either
`g31_preflight_argument` (`B`) or `g31_preflight_final_request` (`F`).

## 5. Candidate Dataflow Models

### 5.1 Candidate Model A — rejected

```text
approved_projection == g31_preflight_input == authorized_task
```

This model collapses prefix and task. If the projection is `P + B`, CODEX would
receive the routing prefix as part of its authorized semantic task. If the
projection is only `B`, it conflicts with the G35-05 full projection contract.

### 5.2 Candidate Model B — rejected as written

```text
approved_projection == P + B
g31_preflight_input == approved_projection
authorized_task == B
```

The separation of full projection and Worker task is correct, but the current
function does not accept an already-prefixed request. Passing `F` to the
unchanged preflight produces `P + F`, violates the 240 accounting contract,
and changes the request bytes.

### 5.3 Candidate Model C — rejected

```text
approved_projection == B
P is runtime-only
g31_preflight_input == B
authorized_task == B
```

This omits `P` from the approved projection and permits a prefix change outside
the approval boundary. It conflicts with G35-05 and does not bind every byte
of the final request measured by G31.

### 5.4 Model D — selected

```text
approved_projection == P + B
g31_preflight_argument == B
g31_preflight_final_request == approved_projection
authorized_task == B
```

Model D is the only valid interpretation. It matches the current function
signature, preserves the full approved projection, keeps routing syntax out of
the Worker task, and proves that preflight and execution refer to the same
approved task body.

## 6. Selected Normative Model

The exact immutable dataflow is:

```text
O + clarification + completed_objective
                  |
                  v
C.proposed_synthesis_body -----------------------------+
                  |                                    |
                  v                                    |
deterministic validation PASS                          |
                  |                                    |
                  v                                    |
human approves exact {source, C, validation, P, B, F} |
                  |                                    |
                  v                                    |
condensation Replay reconstructs exact B and F         |
                  |                                    |
                  v                                    |
G31 input binding returns {O, P, B, F, commitments}   |
                  |                                    |
                  +--> preflight argument = B           |
                         preflight final = P + B = F     |
                  |                                    |
                  +--> Worker authorized_task = B <-----+
```

The input binding MUST retrieve `B` from the approved condensation artifact.
It MUST NOT treat prefix removal from `F` as the authoritative source of `B`.
It recomputes `P + B` only to verify exact equality with stored `F`.

## 7. Human Approval Object

Human Authority approves one immutable review envelope. The approval binds:

- original-request artifact ID, readable exact text, content hash, and artifact
  hash;
- clarification evidence IDs/hashes and resolved answers;
- completed-objective ID/hash;
- condensation artifact ID/hash;
- semantic commitments and complete requirement map;
- deterministic validation result and hash;
- exact `P`, `B`, and `F`, displayed separately without elision;
- code-point and UTF-8 byte lengths of `P`, `B`, and `F`;
- content hashes of `P`, `B`, and `F`;
- material-difference report;
- binding mode and binding-contract version;
- decision, actor, time, and approval scope.

The human approves both the semantic representation `B` and its complete G31
projection `F`. Approval of only the source, only `B`, or only a hash is
insufficient.

No byte of `B` or `F` used by G31 may be absent from the displayed projection.
Existing static CODEX prompt scaffolding is not produced by condensation; it
remains governed by the existing synthesis contract and is bound by the
separate third activation review and approval through the complete prompt hash.

Any changed `P`, `B`, `F`, source, proposal, validation, or hash creates a new
artifact requiring a new human review. Approval is never transferable.

## 8. Projection Prefix Contract

The canonical prefix contract is:

```text
prefix_contract_id: G31_CODEX_SYNTHESIS_PREFIX_V1
projection_prefix: "runtime validation: "
unicode_code_point_count: 20
utf8_byte_count: 20
```

The identifier above names the already implemented constant for this binding
contract; it does not introduce a new G31 runtime version.

G31 preflight owns `P`. The condensation capability may copy and display it but
may not define, normalize, or replace it.

`P`:

- is versioned by exact value and contract identifier;
- is part of the reviewed and approved artifact;
- counts toward the 240-code-point limit;
- may be deterministically reconstructed only from the exact versioned G31
  constant;
- must equal the prefix stored in proposal, validation, review, approval,
  projection, input binding, and both preflight captures; and
- cannot change without invalidating the approval and requiring a new
  constitutional compatibility contract.

Reconstruction MUST be exact at both Unicode code-point and UTF-8-byte levels.

## 9. Approved Synthesis Body Contract

`B` is exactly the stored `proposed_synthesis_body` in the approved
condensation artifact. It is not a summary generated during input binding and
is not a slice derived from the full projection.

The following are mandatory:

```text
B == approved_condensation.proposed_synthesis_body
B == human_review.approved_synthesis_body
B == human_decision.approved_synthesis_body
B == input_binding.g31_preflight_argument
B == worker_execution_contract.authorized_task
SHA256(UTF8(B)) == approved_synthesis_body_sha256
```

Because the unchanged G31 helper applies `strip()`, the binding MUST prove:

```text
B is non-empty
B == B.strip()
```

This is an admissibility constraint, not permission to trim. A body containing
leading or trailing Unicode whitespace fails closed before approval can be
consumed. Internal whitespace and internal `\n`, `\r`, or `\r\n` sequences are
preserved exactly and are never normalized.

`B` MUST be validly UTF-8 encodable. Lone surrogate code points or any value
that cannot produce the committed UTF-8 byte sequence fail closed.

## 10. Exact G31 Preflight Input Contract

For the unchanged function:

```text
preflight_codex_worker_synthesis(B, ...)
```

the normative relationships are:

```text
raw_request == B
canonical_prefix == P
final_synthesized_request == F
raw_character_count == len(B)
prefix_character_count == len(P) == 20
final_character_count == len(F) == len(P) + len(B)
maximum_character_count == 240
final_character_count <= 240
0 < len(B) <= 220
final_synthesized_request_sha256 == SHA256(UTF8(F))
```

Length means Python Unicode code points, matching existing `len(str)`.
UTF-8 byte length is evidence but is not the admission limit.

No Unicode normalization form is applied. Canonically equivalent but
code-point-distinct strings are constitutionally different values. No case
folding, whitespace folding, newline conversion, trimming, ellipsis,
truncation, tokenization, or encode/decode round trip may alter `B` or `F`.

## 11. Authorized Task Identity Contract

`authorized_task == g31_preflight_final_request` is not required and would be
incorrect because the final request includes the G31 routing prefix.

The required invariants are:

```text
authorized_task == B
g31_preflight_argument == B
g31_preflight_final_request == P + authorized_task
g31_preflight_final_request == F
```

This does not permit “preflight one task, execute another task” because:

1. approval commits to `B` and `F`;
2. the input-binding artifact commits to `B`, `F`, and their content hashes;
3. both preflights report `raw_request == B` and final hash `SHA256(UTF8(F))`;
4. the existing Worker contract stores `authorized_task == B`;
5. existing synthesis validation requires the natural-language request to end
   with the exact `authorized_task`;
6. existing prompt construction quotes the exact `authorized_task`;
7. existing activation review and approval bind the Worker-contract and prompt
   hashes; and
8. existing handoff and execution identities transitively bind that contract
   and prompt.

The minimum deterministic evidence is the tuple:

```text
{
  prefix_contract_id,
  projection_prefix_sha256,
  approved_synthesis_body_sha256,
  approved_projection_sha256,
  approved_condensation_artifact_hash,
  validation_artifact_hash,
  human_decision_artifact_hash,
  input_binding_artifact_hash,
  early_preflight_final_request_sha256,
  activation_preflight_final_request_sha256,
  worker_execution_contract_hash,
  bounded_codex_prompt_sha256
}
```

Every adjacent artifact MUST also repeat the relevant exact value, not only its
hash, so reconstruction can prove content equality rather than mere reference
equality.

## 12. Original Request Preservation

`O` remains:

- primary intent authority;
- source for semantic-fidelity validation;
- source of clarification and completed-objective lineage;
- immutable context for grounded execution authorization;
- source context for task-outcome review; and
- separately reconstructable from `B` and `F`.

The existing implementation-turn durable-work binding already stores the
original request and its hash. The new condensation and input-binding Replay
refer to that source; they do not overwrite it.

The activation binding MUST retain:

```text
lineage.original_request == O
resolved_input.approved_synthesis_body == B
worker_execution_contract.authorized_task == B
```

The unchanged generic handoff request's legacy field
`original_human_request` receives `B`, because that field records the exact raw
request seen within the G31 synthesis boundary. In condensation mode it MUST
NOT be treated as primary human-intent authority. `O` remains authoritative
only through the existing implementation lineage and the upstream condensation
and input-binding references. This explicit scoping prevents the legacy field
name from silently replacing `O` and requires no generic handoff schema change.

Task-outcome review remains unchanged because its existing packet already
separates original contextual request, grounded original goal, and authorized
Worker task.

## 13. Compatibility Mode Matrix

| Property | `DIRECT_EXACT_REQUEST_V1` | `APPROVED_CONDENSATION_V1` |
| --- | --- | --- |
| Source task body supplied to preflight | Existing exact direct request `D` | Exact approved body `B` |
| Full preflight request | `P + D` | `P + B == F` |
| Worker `authorized_task` | `D` | `B` |
| Condensation proposal/validation/approval required | No | Yes |
| Condensation Replay required | No | Yes |
| G31 preflight behavior | Existing unchanged behavior | Existing unchanged behavior |
| Execution Authorization | Existing unchanged behavior | Existing unchanged behavior |
| Generic synthesis/handoff schemas | Existing V1 unchanged | Existing V1 unchanged |
| Worker/Provider/task-outcome schemas | Existing V1 unchanged | Existing V1 unchanged |
| Mode fallback | None | None |

For `DIRECT_EXACT_REQUEST_V1`, existing G31 and downstream artifacts, fields,
hash seeds, Replay ordering, approval counts, and schemas MUST remain
byte-for-byte unchanged. No `null`, empty, default, or implicit condensation
field may be inserted.

Mode-selection evidence may exist in the new upstream input-binding Replay, but
the direct path MUST branch into the historical implementation before any
downstream artifact is constructed.

`APPROVED_CONDENSATION_V1` is selected only when direct input is over the
existing bound and the complete approved condensation lineage reconstructs.
Once selected, failure is terminal for that artifact. There is no direct-mode
fallback, re-condensation, retry, or alternate-proposal selection.

## 14. Exact-Byte and Hash Commitments

Define:

```text
UTF8(X) := strict UTF-8 encoding of exact Python string X
H(X)    := lowercase_hex(SHA-256(UTF8(X)))
AH(A)   := existing canonical JSON Replay hash of artifact A
```

The contract requires at least:

```text
H(O)  original_source_request_sha256
H(P)  projection_prefix_sha256
H(B)  approved_synthesis_body_sha256
H(F)  approved_projection_sha256

AH(C) condensation_artifact_hash
AH(V) validation_artifact_hash
AH(R) human_review_artifact_hash
AH(A) human_decision_artifact_hash
AH(I) g31_input_binding_artifact_hash
```

The existing G31 field `final_synthesized_request_sha256` MUST equal `H(F)`.
The existing task-outcome criteria's `authorized_task_sha256` MUST equal
`H(B)`. Existing artifact hashes continue using existing canonical JSON
serialization; content hashes do not replace them.

The input-binding artifact MUST contain exact `P`, `B`, and `F`, their content
hashes and lengths, source/condensation/validation/decision artifact hashes,
mode, version, Replay reference, and authority flags set to false.

## 15. Early and Activation Preflight Equality

The early preflight and activation preflight MUST consume the same exact
argument `B` and reconstruct the same exact final request `F`.

The equality tuple is:

```text
(
  raw_request,
  canonical_prefix,
  final_synthesized_request,
  raw_character_count,
  prefix_character_count,
  final_character_count,
  maximum_character_count,
  character_counting_contract,
  final_synthesized_request_sha256
)
```

Both captures MUST equal:

```text
(
  B,
  P,
  F,
  len(B),
  20,
  len(F),
  240,
  "PYTHON_UNICODE_CODE_POINTS",
  H(F)
)
```

The complete preflight captures and their overall hashes are **not** required
to be equal. Early preflight has no grounded Worker contract; activation
preflight includes the grounded Worker contract and therefore legitimately
produces different synthesis, prompt, handoff, evidence, and capture hashes.

The input-binding owner MUST record a deterministic equality artifact or
equality commitment over the tuple above and both preflight artifact hashes.
Any tuple difference fails closed.

## 16. Replay and Evidence Model

The minimum causal evidence is:

1. existing original source request artifact;
2. existing clarification exchange or no-clarification resolution;
3. existing completed objective;
4. condensation proposal `C`;
5. deterministic validation `V`;
6. exact human review envelope `R`;
7. human decision `A`;
8. approved full projection `F`;
9. selected-mode/input-binding artifact `I`;
10. early preflight capture;
11. activation review referencing `I` and condensation Replay;
12. activation preflight capture;
13. existing activation approval, handoff, receipt, and downstream Replay.

Items 1 through 3 retain their existing source owners and are referenced by
hash and Replay location. Items 4 through 8 are the new upstream condensation
Replay family. Item 9 belongs to the dedicated input-binding owner and is
persisted by the existing Platform Replay mechanism. Items 10 through 13 retain
their existing owners.

Activation evidence references condensation without changing generic schemas
by adding the input-binding artifact ID/hash and its Replay reference only to
the versioned activation review's `interpreted_intent` and
`replay_references`. The existing activation approval already binds the entire
review hash. Generic synthesis, handoff, execution-gate, Worker, Provider, and
task-outcome artifacts receive no condensation-specific fields.

Replay reconstruction MUST start from `I`, reconstruct its referenced
condensation Replay, recompute all exact values and hashes, and then compare
the early and activation equality tuples. A copied hash without successful
source Replay reconstruction is insufficient.

## 17. Runtime Ownership Matrix

| Owner | Required responsibility | Prohibited responsibility |
| --- | --- | --- |
| Condensation proposal runtime | Construct immutable `C` from authenticated source and completed objective | Approve, authorize, call preflight, invoke Worker |
| Deterministic condensation validator | Verify lineage, schema, requirement fidelity, ambiguity, exact values, classifier compatibility, and bound | Rewrite `B`, repair intent, approve |
| Condensation human-decision runtime | Build exact review and bind APPROVE/REJECT to all values/hashes | Infer approval or create execution authority |
| Condensation Replay runtime | Persist and reconstruct source through approved projection | Own semantic approval or alter existing Replay |
| `canonical_governed_development_condensation_g31_input_binding_runtime.py` | Select mode; reconstruct Replay; verify validation/approval; return exact `O`, `P`, `B`, `F`; prove preflight equality; fail closed | Propose, condense, normalize, approve, authorize, mutate generic contracts, invoke Worker |
| AiCLI | Display exact review and transport explicit action | Condense, validate, approve autonomously, authorize |
| Human Interface runtime entry | Sequence pending review and retain input-binding reference across G31 transitions | Decide meaning or become Replay owner |
| CODEX Worker activation binding | Consume resolved values; retain `O`; preflight and authorize exact `B`; reference `I` in activation evidence | Re-condense, rewrite, alter generic downstream schemas |
| Capability certification registry | Register eventual independently certified capability evidence | Certify incomplete implementation or change runtime behavior |

The dedicated input-binding runtime is the sole interpreter of compatibility
mode and condensation-to-G31 value mapping. Common entry and activation call
that owner; neither duplicates its validation logic.

## 18. Activation Binding Revision

The minimum activation revision is confined to
`aigol/runtime/codex_worker_activation_binding_runtime.py`:

1. accept or retrieve one validated input-binding artifact;
2. ask the dedicated binding owner to reconstruct it;
3. preserve `_reconstruct_lineage(...).original_request` as `O`;
4. use resolved task body `B` instead of `O` for early and activation preflight;
5. construct the existing generic Worker contract with
   `authorized_task=B`;
6. derive output type and task-outcome criteria from `B`, not from `O`;
7. include the input-binding ID/hash and Replay reference in activation review
   evidence;
8. bind the existing third approval to the resulting review, contract, final
   request, and prompt hashes; and
9. repeat reconstruction during activation and activation Replay validation.

For direct V1, the activation module executes its historical branch exactly
and adds no fields or references.

No modification is required to:

- `aigol/cli/aigol_cli.py`;
- grounded execution-authorization review or decision;
- generic `runtime/codex_synthesis/*`;
- generic `runtime/codex_handoff/*`;
- execution-gate authorization chain;
- Worker or Provider contracts; or
- task-outcome review.

## 19. Fail-Closed Conditions

The input binding and activation must reject at least:

1. missing original source;
2. invalid or mismatched original-source hash;
3. missing clarification or completed objective evidence;
4. missing condensation proposal;
5. missing deterministic validation;
6. validation status other than PASS;
7. failed semantic-fidelity or requirement-map validation;
8. missing human review or human decision;
9. decision other than exact approval;
10. approval bound to another source, proposal, validation, prefix, body, or
    projection;
11. projection artifact or content-hash mismatch;
12. body artifact or content-hash mismatch;
13. `F != P + B`;
14. prefix value, contract ID, length, byte sequence, or hash mismatch;
15. unsupported or ambiguous binding version/mode;
16. direct mode containing condensation fields;
17. condensation mode missing any condensation field;
18. missing, duplicate, reordered, cross-session, or cross-workspace Replay
    event;
19. Replay reconstruction or artifact-hash mismatch;
20. `B` empty or `B != B.strip()`;
21. non-strict-UTF-8-encodable source, prefix, body, or projection;
22. attempted Unicode normalization, trimming, newline conversion, truncation,
    case conversion, or any post-approval rewriting;
23. early preflight `raw_request != B`;
24. activation preflight `raw_request != B`;
25. either preflight final request not equal to `F`;
26. early/activation equality-tuple mismatch;
27. either final request exceeding 240 Unicode code points;
28. either character-counting contract differing from
    `PYTHON_UNICODE_CODE_POINTS`;
29. `authorized_task != B`;
30. Worker-contract or task-criteria task hash not equal to `H(B)`;
31. input-binding Replay reference absent from condensation-mode activation
    evidence;
32. input-binding, preflight, activation, handoff, or prompt substitution;
33. retry, fallback, alternate proposal, or silent mode change after approval;
34. any attempt by condensation approval to act as execution authorization; or
35. any attempt to inject condensation-specific fields into prohibited generic
    downstream schemas.

Failure occurs before Worker process activation and creates no fallback or
mutation authority.

## 20. Minimal Implementation Scope Confirmation

The nine-owner scope is sufficient:

1. condensation artifact/proposal;
2. deterministic validation;
3. human review and decision;
4. condensation Replay;
5. dedicated G31 input-binding runtime;
6. AiCLI transport;
7. Human Interface transition retention;
8. CODEX Worker activation binding; and
9. eventual certification registration.

No tenth runtime owner is constitutionally required. Existing Platform Replay
persists the new artifacts; the dedicated input-binding runtime does not create
a parallel Replay authority. Existing downstream components already bind exact
task, contract, prompt, handoff, approval, and receipt identities.

## 21. Remaining Architectural Unknowns

No architectural ambiguity remains in the value identities, approval object,
prefix ownership, mode behavior, preflight argument, final measured request,
Worker task, Replay linkage, or activation boundary.

The following are implementation and certification details, not architectural
blockers:

- exact Python API names and dataclass/dictionary representation;
- physical Replay directory names;
- test fixture identifiers;
- deterministic proposal algorithm internals, provided G35-05 fidelity rules
  are satisfied;
- registry evidence identifiers assigned during later certification; and
- whether the input-binding equality commitment is stored as its own wrapper
  or within the binding artifact, provided it has one owner and one canonical
  hash.

These details cannot alter `P`, `B`, `F`, the selected mode, authority
boundaries, or the equality contract established here.

## 22. Final Verdict

`CANONICAL_CONDENSATION_EXACT_INPUT_BINDING_CONTRACT_CLOSED`

Exactly one dataflow is valid:

```text
approved_projection == projection_prefix + approved_synthesis_body
g31_preflight_argument == approved_synthesis_body
g31_preflight_final_request == approved_projection
authorized_task == approved_synthesis_body
```

Every task byte is human-reviewed and hash-bound; both preflights consume the
same exact stored body; the full measured request equals the approved
projection; the Worker receives that same body; the original request remains
independent source authority; and the generic downstream lifecycle remains
unchanged.
