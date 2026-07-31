# 1. Implementation Summary

Generation: G58-01

Report identity: G58_01_CONVERSATION_INTERPRETER_ARCHITECTURE_REPORT_V1

Reporting date: 2026-07-31

Constitutional baseline:
CONVERSATION_STATE_MACHINE_AND_OBJECTIVE_COMMITMENT_PROTOCOL_CHARACTERIZED

Authenticated repository anchor:

- Commit: `9af7541047aca836f9091fb0c1915a221f9335cb`
- Direct parent: `477b49e3d76e0e01d3b49668ff574a08622cf533`
- Tree: `9d67488ff2945d3d5d48dcfc03fbef4ac108abf5`
- Subject: `G57-04: define Conversation State Machine and Objective Commitment protocol`

Implementation contracts:

- G48 Constitutional Evidence Reporting Standard V1
- G55-03 Conversation Working Memory Runtime Implementation Report V1
- G57-02 Typed Semantic Slot Taxonomy Validation Report V1
- G57-03 Conversation Envelope Architecture Report V1
- G57-04 Conversation State Machine and Objective Commitment Protocol Report V1
- PCBV31 Baseline Identity Record V1

Objective:

Define the constitutional Conversation Interpreter Layer that converts bounded
human communication into non-authoritative, versioned semantic proposals for
deterministic validation by the Conversation Layer. The architecture must
support interchangeable deterministic parsers and external LLM interpreters
without granting any interpreter Semantic CWM mutation, Objective, Platform
Core, Replay, Development Governance, Authorization, Worker, or execution
authority.

Implementation scope:

- Defined a closed interpreter abstraction, descriptor registry, capability
  contract, activation lifecycle, invocation lifecycle, and side-effect limits.
- Defined a canonical request capsule containing only the current bounded turn,
  exact Conversation Envelope/CWM bindings, necessary existing semantic state,
  current clarification, and closed proposal vocabulary.
- Defined a canonical semantic proposal format with exact source anchoring,
  advisory operation/confidence fields, alternatives, unresolved items,
  boundary flags, and a deterministic local digest.
- Defined separate integration profiles for pure deterministic parsers and
  externally hosted LLM interpreters.
- Defined order-independent multi-interpreter validation, comparison,
  compatible union, material-conflict handling, and clarification behavior.
- Defined the sole deterministic Conversation Layer validation/reduction path
  allowed to produce an atomic Semantic CWM update.
- Defined compatibility with the G57-03 Envelope, G57-02 Semantic CWM,
  G57-04 conversation protocol, and future Objective Commitment.
- Performed architecture validation only. No interpreter or runtime integration
  was implemented or invoked.

Modified modules:

- `docs/governance/G58_01_CONVERSATION_INTERPRETER_ARCHITECTURE_REPORT_V1.md`:
  this architecture-only G48 evidence report.

Intentionally unchanged modules:

- Platform Core, AiCLI, Human Interface Runtime, and Conversation Layer
  runtime, including the implemented G55-03 CWM runtime.
- Objective, Development Governance, Capability, Replay, Authorization,
  Worker, Completion, G31, and G35.
- Existing deterministic Objective inference and provider-assisted runtime
  modules; they are evidence surfaces, not dependencies authorized for reuse.
- PCBV31 and every constitutional specification, manifest, and baseline.

Architectural boundaries preserved:

- Interpreters receive immutable request data and return proposal data. They
  receive no state handle, repository mutation handle, pipeline service,
  credential, Replay writer, or tool-execution interface.
- Interpreter output is untrusted proposal material even when produced by a
  deterministic parser or when multiple interpreters agree.
- Only a deterministic Conversation Layer validator/reducer may translate
  accepted proposal elements into one expected-revision Semantic CWM update.
- Interpreters cannot confirm semantic meaning, accept Objective readiness,
  interpret Objective Commitment, create an Objective, select a capability,
  invoke Platform Core, or interact with downstream constitutional owners.
- Interpreter confidence and interpreter majority are advisory diagnostics;
  neither can overcome invalid schema, missing source evidence, semantic
  conflict, or required human clarification.
- Interpreter proposals, raw provider output, confidence, comparison, and
  validation dispositions remain local working data and never become Replay.

## Executive Summary

The Conversation Interpreter Layer is an **untrusted proposal boundary**. It
does not own conversation meaning. Conversation Layer owns the allowed
vocabulary, proposal validation, conflict determination, and the sole atomic
Semantic CWM reducer.

```text
Human turn
  -> Conversation Layer request builder
  -> one or more interchangeable interpreters
  -> untrusted semantic proposals
  -> deterministic schema/source/taxonomy validation
  -> order-independent comparison
  -> deterministic accepted delta or clarification
  -> expected-revision Semantic CWM transaction
```

A deterministic parser has stronger reproducibility evidence than an external
LLM, but not stronger constitutional authority. Its proposal may be accepted
only when the Conversation Layer independently replays the closed grammar
proof. An external LLM may suggest normalized values and alternatives, but its
self-reported confidence is not comparable authority and cannot make a
candidate complete without deterministic source validation and the G57-04
human review/confirmation protocol.

No interpreter parses `CONFIRM_CANDIDATE` or `COMMIT_EXACT_CANDIDATE`. Those
are explicit deterministic control acts owned by the G57-04 protocol. Thus an
LLM response such as “confirmed,” “execute,” or “use this capability” remains
ordinary untrusted text and cannot cross the Objective Commitment boundary.

# 2. Code Evidence

No runtime code was added or changed. Evidence consists of authenticated G57
architecture artifacts, exact current runtime boundary excerpts, the canonical
models below, and deterministic compatibility analysis.

## Authenticated Evidence Inventory

| Evidence | Git blob | SHA-256 | Architectural use |
|---|---|---|---|
| G57-04 state/commitment protocol | `64e5950cd17014c9c079e236463849156671c930` | `b31d6ce31057e855ce98bed0cb60cb764948f57c1b1c87ae646e433b47060284` | Establishes human-turn reduction, clarification, correction, confirmation, readiness, and commitment exclusion. |
| G57-03 Envelope architecture | `cb13f667017c997b4f0f3e3cc52d16db08e329ff` | `28e1aaca67a1e9efd5cfdc20a2e76e3a8357d6e95cd540e42a825cc5da8878a0` | Establishes immutable request bindings, availability, interface/participant locality, and atomic revisions. |
| G57-02 semantic taxonomy | `df1c7f5941eb1293bb4dc354116e5db0b589a84e` | `f02f2963d241900c94b4771c51124805d7fb8416b7f832ce52cd07b4a1b60e16` | Establishes six closed semantic classes, roles, cardinality, status, completeness, and normalization boundaries. |
| G55-03 CWM source | `e903bf29923b91e4fa4ffbe0cc6a5463a70ae981` | `6c144a8c10f97f56fa5177bf6c691d2bbbe7c139fea66dd2e8d30cc12277ab13` | Establishes current storage isolation, validation, revision, TTL, and fixed non-authority fields. |
| Existing provider-assisted classifier | `0c4ed2669c1ebaf5157421519c907e3941f5de2b` | `3c51324a72f88b1f01f92d79ef2252c1e0dd52abf82fd157310ba47bfe5ffddb` | Demonstrates proposal-only provider wording but also Replay/classification responsibilities that cannot be imported unchanged. |
| Existing Objective inference/clause interpreter | `3bb2e1104320763a7441595ccb9f4e03584cf082` | `ea298ba1feb75b3a55fdbf74231c26286aec17aff89cff17211aa8505bd11536` | Demonstrates deterministic clause-role logic currently co-located with Objective inference and therefore not a G58 interpreter dependency. |

## Existing Boundary Evidence

The existing G55-03 runtime stores this exact non-authority boundary:

```python
_BOUNDARY_FIELDS = {
    "runtime_owner": PLATFORM_CORE_CONVERSATION_WORKING_MEMORY_OWNER,
    "constitutional_artifact": False,
    "constitutional_authority": False,
    "replay_visible": False,
    "authorization_eligible": False,
    "worker_eligible": False,
    "objective_creation_supported": False,
    "capability_routing_supported": False,
}
```

The existing provider-assisted classifier correctly states:

```python
"LLM providers are proposal-only sources; they do not govern, authorize, execute, mutate replay, or invoke workers."
```

However, the same existing module imports Replay serialization and persists
provider-assisted classification Replay. The current Objective module also
contains `interpret_request_clause_roles` beside
`infer_platform_project_objective`. Therefore neither module is a drop-in
implementation of this architecture. Reusing them unchanged would violate the
required separation from Replay, Objective, Platform Core routing, and
certified execution owners.

They may inform future isolated test vectors only. A G58 implementation must
use a new pure proposal interface and closed Conversation Layer validator.

## Constitutional Position

The Interpreter Layer is subordinate to the Conversation Layer:

```text
Human Authority
      |
      v
Conversation Layer ---------------- owns deterministic validation/reduction
      |
      +---- immutable request ----> Interpreter Layer
      |                                  |
      |<---- untrusted proposal ----------+
      |
      v
Semantic CWM (local mutable working state)
      |
      v
G57-04 human review and future Objective Commitment
      |
      v
Existing Objective owner and certified pipeline
```

Interpreter interchangeability changes proposal generation only. It cannot
change semantic taxonomy, acceptance rules, confidence policy, Objective
readiness, commitment criteria, or downstream execution behavior.

## Interpreter Abstraction Model

### Canonical interface

```text
ConversationInterpreter:
  describe() -> InterpreterDescriptor
  interpret(InterpreterRequest) -> InterpreterProposal

No other public operation is permitted.
```

`describe` is side-effect free. `interpret` consumes an immutable bounded
request and returns one complete bounded proposal or a fail-closed invocation
disposition. Streaming fragments are never proposals and cannot be consumed by
the validator.

An interpreter interface must not expose:

- CWM `create`, `load`, `update`, `recover`, or cleanup operations;
- Conversation Envelope mutation;
- Objective or Platform Core service calls;
- capability discovery, selection, or execution binding;
- Replay writers/readers or artifact identities;
- Authorization or approval requests;
- Worker dispatch, provider-as-Worker, tools, shell, filesystem, network
  browsing, or repository mutation handles; or
- credential material.

### Interpreter descriptor

```text
interpreter_descriptor:
  descriptor_schema_version
  interpreter_id: local closed registry identity
  interpreter_version: immutable version
  interpreter_kind: DETERMINISTIC_PARSER | EXTERNAL_LLM
  proposal_schema_versions[]
  supported_languages[]
  supported_slot_classes[]
  supported_slot_roles[]
  supported_candidate_operations[]
  determinism_class: EXACT_REPRODUCIBLE | PROVIDER_VARIANT
  input_limit_bytes
  output_limit_bytes
  timeout_class
  external_data_processing: true | false
  tools_available: false
  state_mutation_available: false
  pipeline_access_available: false
  replay_access_available: false
  objective_access_available: false
  descriptor_digest
```

Unknown kinds, open-ended capabilities, mutable versions, or any `true` access
flag outside declared external data processing fail registration.

`interpreter_id` identifies one role/version combination. The same LLM vendor
used elsewhere as Worker, explanation provider, or cognition provider requires
a distinct G58 interpreter identity, configuration, limits, metrics, and
credential reference. Provider reputation or another role's certification is
not inherited.

## Interpreter Lifecycle

### Registry lifecycle

| State | Entry | Permitted behavior | Exit | Fail-closed rule |
|---|---|---|---|---|
| `DECLARED` | Closed descriptor submitted | Static descriptor inspection only | Valid descriptor -> `VALIDATED`; invalid -> `REJECTED` | No invocation |
| `VALIDATED` | Schema, digest, limits, capability vocabulary, and boundary flags pass | Compatibility tests only | Explicit Conversation Layer configuration -> `ENABLED` | No automatic enablement |
| `ENABLED` | Validated descriptor is allowlisted for an exact policy version | May receive eligible immutable requests | Disable/quiesce/failure threshold -> next state | Cannot expand capabilities at runtime |
| `QUIESCING` | Disable or version replacement begins | Existing invocation may finish; no new invocation | No active invocations -> `DISABLED` | Late proposal is validated against original request or marked stale |
| `DISABLED` | Explicit disable, missing dependency, or completed quiescence | No invocation | Separate revalidation -> `ENABLED`; retirement -> `RETIRED` | Provider availability cannot self-enable |
| `RETIRED` | Version permanently withdrawn | Historical local descriptors remain identifiable until CWM TTL cleanup | None | Cannot reactivate same version identity |
| `REJECTED` | Descriptor validation fails | None | New corrected version only | Rejected descriptor is never patched in place |

Interpreters do not transition their own registry state. Conversation Layer
configuration owns lifecycle transitions.

### Invocation lifecycle

```text
CREATED
  -> INPUT_BOUND
  -> DISPATCHED
  -> PROPOSAL_RETURNED
  -> VALIDATION_PENDING
  -> VALIDATED | REJECTED | STALE | TIMED_OUT | FAILED_CLOSED
```

The Conversation Layer owns every lifecycle disposition. A provider response,
process exit, or parser return cannot mark itself `VALIDATED`.

Timeout, exception, malformed output, partial stream, cancellation, or stale
revision produces no Semantic CWM update. Availability of another interpreter
may permit an independent proposal; otherwise the G57-04 protocol clarifies or
suspends rather than guessing.

## Interpreter Capabilities and Limits

Allowed capabilities are proposal-local:

- locate exact human source spans;
- propose one of the six G57-02 slot classes and allowed roles;
- propose bounded canonical values and equivalence hints;
- propose advisory relationships such as add/refine/replace/withdraw;
- report alternatives, ambiguity, unresolved values, and advisory confidence;
- report deterministic rule evidence or external model metadata; and
- return no-proposal/failure dispositions.

Prohibited capabilities include:

- assigning final slot status, completeness, materiality, or confidence class;
- resolving current CWM conflicts by authority or majority;
- accepting external evidence disposition;
- selecting the current clarification or rendering a binding human question;
- confirming a candidate or interpreting confirmation/commitment controls;
- creating candidate readiness or Objective readiness;
- selecting capability routes or work execution;
- changing any limit, ruleset, schema, lifecycle, or boundary flag; and
- writing persistent state, constitutional evidence, or Replay.

The descriptor declares exact byte, candidate-count, alternative-count,
language, role, and timeout limits. Conversation Layer applies stricter global
limits independently. Exceeding either limit rejects the entire proposal; it
does not truncate material values silently.

## Canonical Interpreter Request

```text
interpreter_request:
  request_schema_version
  interpretation_policy_version
  proposal_schema_version
  request_id: local digest
  conversation_identity
  workspace_identity_hash
  session_identity_hash
  current_interface_identity
  expected_global_revision
  expected_semantic_revision
  envelope_availability: ACTIVE
  conversation_protocol_state
  human_turn_id
  human_turn_text: bounded current turn only
  human_turn_digest
  language_hint: advisory
  active_clarification_binding: bounded or null
  existing_semantic_capsule: minimum necessary slots/controls
  allowed_slot_classes_roles
  allowed_candidate_operations
  normalization_ruleset_version
  limits
  boundary:
    proposal_only: true
    tools_available: false
    state_mutation_available: false
    objective_access_available: false
    platform_core_access_available: false
    replay_access_available: false
    authorization_access_available: false
    worker_access_available: false
```

The request excludes:

- complete conversation transcript;
- credentials, environment variables, filesystem content, and repository
  source unless an exact bounded human-visible fragment is itself the current
  turn;
- Objective, Replay, Authorization, Worker, or constitutional identities;
- capability registries or execution-ready evidence;
- hidden active-workspace objective expansion;
- provider-specific authority statements; and
- human confirmation or commitment secrets.

The semantic capsule contains only values necessary to interpret the current
turn: current active slot summaries, exact clarification binding, and allowed
dependency/cardinality keys. It is canonically ordered and hashed. An external
interpreter cannot request more context dynamically.

## Canonical Semantic Proposal Format

```text
interpreter_proposal:
  proposal_schema_version
  proposal_id: session-local nonconstitutional identity
  request_id
  interpreter_id
  interpreter_version
  descriptor_digest
  interpretation_policy_version
  normalization_ruleset_version
  conversation_identity
  workspace_identity_hash
  session_identity_hash
  source_global_revision
  source_semantic_revision
  human_turn_digest
  semantic_capsule_digest
  proposal_candidates[]
  unresolved_items[]
  proposal_alternatives[]
  confidence_report
  provider_metadata: bounded, secret-free, or null
  boundary_flags
  proposal_digest
```

The interpreter-returned body does not choose its authoritative local identity.
Conversation Layer canonicalizes the body without `proposal_id` or
`proposal_digest`, computes `proposal_digest`, and assigns `proposal_id` from
the request/interpreter/version/digest tuple. Any interpreter-supplied identity
value is ignored or rejected by the closed transport schema. This prevents
collision, impersonation, and digest circularity.

Each proposal candidate is:

```text
proposal_candidate:
  candidate_id: proposal-local identity
  proposed_slot_class
  proposed_slot_role
  proposed_cardinality_key
  proposed_value_kind
  source_spans[]:
    start_offset
    end_offset
    exact_surface_digest
  exact_surface_value: bounded current-turn fragment
  proposed_canonical_value
  proposed_equivalence_key
  proposed_operation: ADD | REFINE | REPLACE | WITHDRAW | NO_CHANGE
  target_slot_id: optional existing local identity
  depends_on_candidate_ids[]
  alternative_group_id: optional
  interpreter_confidence_reference
  interpreter_reason_code: closed advisory code
```

The proposal's operation, equivalence key, canonical value, confidence, and
reason are advisory. The deterministic validator re-derives them against the
current Semantic CWM. A valid source span proves only that text was present; it
does not prove the proposed interpretation.

### Fixed proposal boundary flags

```text
constitutional_artifact: false
constitutional_authority: false
semantic_cwm_mutation_authority: false
human_confirmation_authority: false
objective_creation_supported: false
capability_routing_supported: false
platform_core_invocation_supported: false
replay_visible: false
replay_mutation_supported: false
development_governance_supported: false
authorization_eligible: false
worker_eligible: false
tool_execution_supported: false
```

Missing, extra, or altered boundary flags reject the proposal.

Forbidden proposal keys and content include Objective IDs, Replay identities,
authorization IDs, Worker request IDs, executable tool calls, shell commands as
instructions, credentials, provider tokens, capability selections, approval
decisions, and claims that a proposal is accepted or committed.

## Proposal Lifecycle

| State | Owner | Entry | Exit | CWM effect |
|---|---|---|---|---|
| `RETURNED_UNTRUSTED` | Conversation Layer host | Complete interpreter return captured in memory | Closed-envelope validation | None |
| `SCHEMA_VALIDATED` | Deterministic validator | Exact schema, boundaries, limits, digest, and registry bindings pass | Source/taxonomy validation | None |
| `SEMANTIC_VALIDATED` | Deterministic validator | Source spans, taxonomy, value kinds, operation relationship, and dependencies pass | Multi-proposal comparison | None |
| `COMPARED` | Deterministic comparator | All eligible proposals canonicalized in order-independent set | Reduction decision | None |
| `ACCEPTED_FOR_REDUCTION` | Conversation Layer policy | Validated non-conflicting candidate set selected by closed policy | Expected-revision reducer transaction | None until transaction |
| `CONSUMED` | Semantic CWM reducer | Atomic post-validation CWM transaction succeeds | Local proposal retention until TTL/cleanup | One deterministic CWM revision |
| `REJECTED` | Deterministic validator/comparator | Any terminal invalidity or material unresolved conflict | Clarification/failure disposition | None |
| `STALE` | Conversation Layer | Envelope/global/semantic revision changed before consumption | Cleanup or new invocation | None |
| `SUPERSEDED` | Conversation Layer | New accepted turn/proposal set replaces an unconsumed set | Cleanup | None |

Lifecycle records remain bounded local working-state controls under the
Conversation Envelope TTL. They are not Replay or constitutional evidence.

## Deterministic Parser Integration

A deterministic parser is a pure interpreter with:

- immutable grammar and ruleset version;
- exact Unicode/token/locale policy;
- closed clause-to-class/role mappings;
- exact source offsets and surface digests;
- deterministic ambiguity output;
- no dynamic vocabulary, model, provider, repository, or network dependency;
  and
- byte-identical proposal output for identical canonical input.

The Conversation Layer independently re-evaluates the parser rule proof. A rule
match is accepted only when the validator derives the same source spans,
class/role/cardinality, and canonical value under the declared version.

Deterministic parser selection has first operational precedence because it is
local, reproducible, private, and inexpensive. When it fully covers the current
turn under a closed rule, external LLM invocation is unnecessary. This is an
efficiency/privacy rule, not authority precedence: if a separately validated
LLM proposal materially conflicts with a valid parser proposal, the system
clarifies unless one candidate is deterministically invalid.

The current `interpret_request_clause_roles` function is not imported because
it lives inside the Objective inference module and includes capability-target
eligibility. A future parser may reuse its authenticated lexical cases as test
fixtures only after restating them in a Conversation-owned pure grammar.

## External LLM Integration

### Invocation boundary

```text
Conversation Layer
  -> Interpreter Host
      -> dedicated G58 provider transport
          -> external LLM service
      <- raw bounded response
  <- parsed untrusted InterpreterProposal
```

The host, not the model, owns request construction, timeout, byte limits,
response framing, and proposal capture. Credentials remain inside a separately
owned provider credential/transport boundary and are never placed in the
interpreter request or proposal.

The dedicated G58 provider transport must be proposal-only and must expose no
Worker, tool, Platform Core, Objective, Replay, Authorization, repository, or
governance operation. Existing provider-assisted classification runtimes that
write Replay or routing artifacts cannot be reused unchanged.

### Canonical external prompt capsule

The external request contains:

- fixed non-authority instructions;
- closed proposal JSON schema and allowed class/role/operation vocabulary;
- the current bounded human turn marked as untrusted data;
- the minimum semantic capsule marked as untrusted context;
- exact request/ruleset/schema versions and limits; and
- an instruction to return one data object without tools or side effects.

Human text that asks the model to ignore schema, invoke tools, select a
capability, reveal credentials, modify state, or declare commitment remains
quoted data. A response attempting any such act fails proposal validation.

### External variability

External LLM output is `PROVIDER_VARIANT`. Identical requests need not produce
identical proposals. Determinism is restored at the boundary by:

- immutable request bytes/digest;
- closed returned schema;
- deterministic canonicalization and validation;
- exact current-state binding;
- order-independent comparison;
- deterministic conflict/clarification outcomes; and
- no direct CWM mutation.

Provider unavailability, timeout, rate limit, malformed output, or refusal
cannot broaden deterministic interpretation. The system uses another eligible
proposal or enters clarification/fail-closed state.

No live external provider was contacted by this architecture generation.

## Confidence Reporting

Confidence has three independent layers:

| Layer | Producer | Meaning | Authority |
|---|---|---|---|
| `interpreter_reported_confidence` | Interpreter | Native score/category under an identified scale | Advisory only; not comparable across interpreter versions |
| `validation_evidence_class` | Conversation validator | `EXACT_RULE_REPLAYED`, `SOURCE_ANCHORED_PROPOSAL`, `UNANCHORED`, or `INVALID` | Determines evidentiary treatment, not human truth |
| `comparison_disposition` | Deterministic comparator | Agreement, compatible union, partial coverage, conflict, or all rejected | Selects reduction vs clarification only |

Canonical confidence report:

```text
confidence_report:
  scale_id
  proposal_reported_value
  candidate_reported_values[]
  calibration_version: optional
  limitations[]: closed codes
```

Conversation Layer does not average heterogeneous model scores, compare a
parser boolean with an LLM probability, or choose the highest number. Majority,
vendor reputation, model size, cost, latency, and confidence cannot resolve a
material semantic conflict.

Valid confidence uses are limited to:

- selecting whether an unresolved proposal requires clarification;
- deciding whether to request an additional interpreter under a closed policy;
- ordering human-visible alternatives after deterministic canonical ordering
  ties are already resolved; and
- reporting uncertainty locally.

Confidence cannot change slot materiality/completeness, turn a proposal into
human assertion/confirmation, or satisfy Objective readiness.

## Deterministic Proposal Validation Flow

Validation occurs in this exact order:

1. Validate Envelope is `ACTIVE`, protocol state permits semantic input, TTL is
   valid, and request expected revisions match the atomic state.
2. Validate interpreter registry state is `ENABLED` and exact descriptor,
   version, capability, schema, language, and policy bindings match.
3. Validate proposal is one complete canonical object within byte/item limits;
   reject streaming fragments and unknown fields.
4. Validate fixed false boundary flags and reject forbidden identities,
   authority claims, tool calls, executable side-effect requests, or secrets.
5. Recompute proposal digest and verify request, turn, capsule, conversation,
   workspace, session, global revision, and semantic revision bindings.
6. Validate every source offset and surface digest against the exact current
   human turn.
7. Validate class, role, cardinality, value kind, operation vocabulary,
   candidate/alternative/dependency identities, and normalization ruleset.
8. Re-derive canonical values/equivalence where a deterministic rule exists;
   otherwise retain the value as a source-anchored `PROPOSED` candidate.
9. Re-derive semantic relationship against current CWM: no change, refine,
   replace, withdraw, or conflict. Interpreter labels do not control it.
10. Reject lower-evidence overwrite, unsupported inference, missing material
    source, illegal dependency, capability selection, or commitment language.
11. Canonicalize each valid proposal into comparison keys and compare all
    eligible interpreters as an unordered set.
12. Produce exactly one reducer disposition: accepted delta, clarification
    control, no change, or fail-closed rejection.
13. Revalidate expected revision under the CWM store lock and apply at most one
    atomic deterministic Semantic CWM transaction.
14. Recompute G57-04 completeness, conflicts, clarification, candidate,
    confirmation invalidation, Envelope phase/bindings, global revision, and
    integrity; reject the transaction if post-validation fails.

An interpreter returning valid JSON demonstrates only schema validity. No
proposal influences state until all fourteen steps and the atomic transaction
succeed.

## Multi-Interpreter Selection and Comparison

### Selection policy

Conversation Layer selects interpreters by a closed versioned policy using:

- exact required language and slot/role capability coverage;
- registry state and declared limits;
- deterministic-parser coverage result;
- privacy policy permitting or forbidding external processing;
- explicit local external-provider enablement; and
- bounded cost/latency class.

Human text cannot name or activate an interpreter. An explicit human privacy
restriction can disable external processing but cannot force a particular
provider or weaken validation.

Default sequence:

1. invoke eligible deterministic parser set;
2. if exact validated coverage is complete and unambiguous, stop;
3. otherwise invoke the bounded allowlisted external set only when policy
   permits; and
4. validate every returned proposal independently before comparison.

### Canonical comparison key

Each candidate is compared by:

```text
(
  slot_class,
  slot_role,
  cardinality_key,
  value_kind,
  validator_derived_canonical_value,
  validator_derived_operation,
  target_slot_id,
  normalized_dependency_set
)
```

Interpreter identity, invocation order, response order, latency, and reported
confidence are excluded from semantic equality.

### Comparison dispositions

| Disposition | Condition | Reducer behavior |
|---|---|---|
| `CONSENSUS` | All valid proposals provide the same key/value for overlapping material candidates | Accept validated candidates under normal status rules; agreement adds no authority |
| `COMPATIBLE_UNION` | Valid proposals cover disjoint or compatible candidates without dependency/cardinality conflict | Accept canonical union ordered by taxonomy/cardinality key |
| `PARTIAL_COVERAGE` | Valid proposals omit required material meaning without contradiction | Accept only safe source-anchored deltas; G57-04 clarification addresses missing material |
| `MATERIAL_CONFLICT` | Two valid candidates differ for the same material cardinality/dependency position | Accept neither conflicting value as final; create visible conflict/clarification |
| `INVALID_ALTERNATIVE_REMOVED` | One candidate fails deterministic validation while another passes | Remove invalid candidate; do not call this semantic tie-breaking |
| `ALL_REJECTED` | No proposal passes validation | No CWM semantic update; deterministic clarification/fail-closed disposition |

No majority vote exists. Three LLMs cannot outvote one valid conflicting
proposal. A deterministic parser wins only when the validator proves the other
candidate invalid under the same closed grammar/source contract; parser
identity alone is not precedence.

### Conflict resolution

Material conflict resolution is owned by human interaction through G57-04:

1. persist bounded conflicting candidates as local proposal/control evidence,
   not active final semantics;
2. derive one highest-precedence clarification bound to current revisions;
3. display canonical alternatives with neutral interpreter-independent labels;
4. accept exact human answer/correction through the normal deterministic turn
   protocol; and
5. re-run validation and reduction.

Interpreters may be reinvoked after a new human turn, but cannot adjudicate the
old conflict by self-critique, debate, rank, or confidence escalation.

## Conversation Layer Reduction

The reducer is pure and closed:

```text
reduce_validated_proposals(
  current_envelope_snapshot,
  current_semantic_snapshot,
  human_turn_binding,
  validated_comparison,
  policy_version
) ->
  SEMANTIC_DELTA | CLARIFICATION_DELTA | NO_CHANGE | FAIL_CLOSED
```

Only this reducer may construct CWM slot/control operations. It decides:

- final operation relationship;
- target slot identity;
- status (`PROPOSED`, `ASSERTED`, `CONFIRMED`, `CONFLICTED`, `STALE`) according
  to human source evidence and current protocol state;
- completeness/materiality under G57-02 rules;
- dependency invalidation;
- bounded provenance referencing proposal/interpreter locally;
- clarification control;
- candidate/confirmation invalidation; and
- deterministic post-state.

External LLM candidates generally enter as `PROPOSED` unless exact current-turn
source and a deterministic rule prove a direct human assertion. Even then, the
validator assigns `ASSERTED`; the interpreter does not. `CONFIRMED` remains an
explicit G57-04 human control result and is never assigned from interpreter
agreement.

The CWM update uses exact compare-and-swap revision. If any state changed while
interpreters ran, all proposals become `STALE`; they are never rebased
automatically onto new semantic state.

## Trust Boundary Diagrams

### Core proposal boundary

```text
TRUSTED CONVERSATION CONTROL               UNTRUSTED PROPOSAL ZONE

Envelope/CWM snapshot --immutable request--> Interpreter A: deterministic
         |                 |                 Interpreter B: external LLM
         |                 |                 Interpreter C: external LLM
         |                 |                         |
         |                 +<----- proposals --------+
         v
Closed schema/source/taxonomy validator
         |
         v
Order-independent comparison
         |
         +-- invalid/conflict --> G57-04 clarification
         |
         v
Pure Conversation Layer reducer
         |
         v
Expected-revision atomic Semantic CWM update

No arrow exists from an interpreter to CWM or any execution owner.
```

### External provider isolation

```text
Conversation Layer
   |
   | bounded request; no secrets/state handles
   v
G58 Interpreter Host ---- credential reference ---> Provider Transport Owner
   |                                                    |
   |                                                    v
   |                                              External LLM Service
   |                                                    |
   |<-------------- bounded raw response ---------------+
   |
   v
Untrusted proposal parser -> deterministic Conversation validator

Provider Transport has no Worker tools, Platform Core, Objective, Replay,
Authorization, Development Governance, repository, or CWM mutation surface.
```

### Constitutional exclusion

```text
Interpreter Proposal
   X-- Semantic CWM direct mutation
   X-- Objective creation
   X-- Platform Core invocation
   X-- Development Governance
   X-- Capability Selection
   X-- Replay
   X-- Authorization
   X-- Worker / Completion

Validated Conversation state
  -> human candidate review
  -> exact human confirmation
  -> future Objective Commitment
  -> existing Objective owner
  -> certified downstream pipeline
```

## Interaction with Conversation Envelope

Conversation Envelope owns every invocation's immutable locality and freshness
binding:

- conversation identity;
- workspace/session hashes;
- interface and participant assertions;
- availability and TTL;
- global/Envelope/semantic revisions;
- conversation phase; and
- current semantic/candidate bindings.

Invocation is allowed only while availability is `ACTIVE` and the G57-04 state
permits semantic input (`COLLECTING` or `CLARIFYING`, and correction from review
states). Suspension, closure, expiration, pending commitment, recovery, or
handoff prevents invocation.

An interpreter cannot alter Envelope fields. If any relevant Envelope/global
revision changes before reduction, the proposal is stale. Cross-interface
restoration requires the G57-03 protocol before new interpretation; interpreter
similarity cannot prove session continuity.

External-processing permission is a closed local Envelope/policy restriction,
not a semantic slot. Human content may restrict external use, but an
interpreter cannot enable itself or widen context scope.

## Interaction with Semantic CWM

Semantic CWM supplies a read-only minimal capsule and accepts updates only from
the Conversation reducer. The six G57-02 classes remain unchanged:

- `OPERATIVE_ACTION`;
- `OPERATIVE_SUBJECT`;
- `DESIRED_OUTCOME`;
- `WORK_TYPE`;
- `GOVERNING_QUALIFIER`; and
- `SEMANTIC_REFERENCE`.

Proposal candidates cannot introduce a seventh class or arbitrary role.
Interpreter alternatives and confidence remain control/proposal data outside
active semantic slots. Only validated human-stated assumptions can become
`GOVERNING_QUALIFIER:ASSUMPTION`; model speculation cannot.

CWM provenance may retain bounded local interpreter/proposal/version/digest
references until Envelope TTL. It must not copy credentials, raw full provider
responses, hidden chain-of-thought, full transcripts, or Replay identities.

## Interaction with G57-04 Human Protocol

- `COLLECTING`: interpreters propose initial/additional semantic candidates.
- `CLARIFYING`: request contains the exact clarification; proposals are checked
  specifically against the addressed slot unless the human explicitly corrects
  another slot.
- `CANDIDATE_REVIEW`: interpretation is allowed only for explicit correction
  or withdrawal, which invalidates candidate/confirmation through G57-04.
- `OBJECTIVE_READY`: new interpreted semantic content clears confirmation and
  returns to review/clarification; it cannot be treated as commitment.
- `COMMITMENT_PENDING`, `COMMITMENT_RECOVERY`, `HANDED_OFF`, `SUSPENDED`,
  `ABANDONED`, `EXPIRED`: no interpreter invocation is permitted.

Lifecycle control acts—confirm, commit, suspend, resume, abandon, cancel
pending commitment—are validated by deterministic Conversation protocol
controls, not natural-language interpreter proposals. If transport supplies
only ambiguous prose for such an act, the protocol clarifies rather than
letting an interpreter create the transition.

## Compatibility with Objective Commitment

Interpreter participation terminates before Objective readiness:

1. accepted interpreter-derived deltas become ordinary provisional/asserted
   Semantic CWM state through the deterministic reducer;
2. G57-04 recomputes slot completion, clarification, and candidate projection;
3. candidate projection excludes interpreter confidence, majority,
   alternatives, provider metadata, and proposal lifecycle;
4. the human reviews and confirms the exact candidate through the deterministic
   G57-04 control protocol;
5. a separate exact commitment act reaches the future Objective Commitment
   gate; and
6. existing Objective owner alone creates the immutable Objective.

The commitment request contains candidate/revision/digest/human-authority
bindings, not an interpreter decision. Interpreter identity or confidence
cannot be a commitment criterion. Reinvoking an interpreter after confirmation
would change local state or produce stale output and therefore invalidates
readiness before commitment.

Existing downstream Replay may later record the committed Objective and its
normal certified pipeline evidence. It must not consume interpreter proposals,
raw provider responses, confidence, comparison, or local proposal identities.
This preserves the requirement that interpreters never influence Replay.

## Failure and Security Model

| Failure/attack | Deterministic disposition |
|---|---|
| Prompt injection requests tools, authority, commitment, or pipeline action | Treat as human text; reject matching proposal fields; no side effect |
| Model returns tool/function call | Reject entire proposal |
| Model returns prose instead of closed object | Reject; no best-effort extraction unless separately versioned deterministic parser validates it |
| Parser/LLM proposes unsupported class/role | Reject candidate; clarify if material |
| Invalid or overlapping source offsets | Reject proposal |
| Provider output contains secrets | Reject/quarantine under future provider policy; never persist to CWM/Replay |
| Proposal exceeds bounds | Reject whole proposal; no silent material truncation |
| Interpreter times out/fails | Record local failure disposition; use other validated proposal or clarify |
| State changes during invocation | Mark proposal stale; no automatic rebase |
| Multiple interpreters disagree | Material conflict and human clarification; no majority vote |
| All interpreters agree on invalid value | Deterministic rejection |
| High confidence conflicts with exact human text | Reject/conflict; confidence has no override |
| Human asks to use a named provider | Does not change registry/selection; policy decides |
| Provider attempts repeated self-correction | No autonomous loop; each invocation requires Conversation Layer policy |
| Interpreter code attempts forbidden import/call | Static/runtime boundary test fails and interpreter is rejected/disabled |

External input/output retention, redaction, regional processing, and provider
data-use policy require a future dedicated privacy/security contract. No
external invocation is permitted before that contract and explicit local
enablement exist.

## Compatibility Assessment

### G57-02 compatibility

- Closed six-class taxonomy and role/cardinality/value-kind rules remain the
  validator authority.
- Interpreter-proposed class/role and equivalence are advisory.
- Unknown roles trigger rejection/clarification rather than schema expansion.
- Model assumptions cannot become semantic assumptions without human source.

### G57-03 compatibility

- Envelope supplies immutable invocation locality, availability, TTL, and
  revisions.
- Proposals remain in the same bounded local working domain and do not create a
  second persistent authority.
- Proposal staleness is determined by exact Envelope/CWM revision binding.
- External processing cannot widen context scope.

### G57-04 compatibility

- Interpreter outputs feed only the deterministic human-turn reduction stage.
- Clarification ordering, correction, rollback, confirmation, readiness,
  commitment, recovery, abandonment, and expiration remain protocol-owned.
- Confirmation and commitment controls are explicitly non-interpretable.
- No interpreter invocation occurs during pending/recovery/handoff.

### G55-03 compatibility

- Existing working root, lock, optimistic revision, integrity, TTL, bounds,
  recovery, cleanup, and false authority fields remain required.
- Future proposal controls require the G57 versioned V2 schema and are not
  silently added to V1.
- Interpreter latency occurs outside the state lock; expected-revision CAS
  rejects stale completion.

### Certified pipeline compatibility

- No Platform Core service is imported or invoked by interpreters.
- No Objective artifact or identity appears in request/proposal state.
- No Development Governance, Capability, Authorization, Worker, Completion, or
  Replay API is available.
- Only the future committed Objective enters existing owners.
- PCBV31 remains unchanged.

## Architecture Invariants

1. Every interpreter output is a proposal, never state or authority.
2. Interpreters receive no mutable handle or execution service.
3. Only Conversation Layer validates, compares, reduces, and submits CWM
   updates.
4. Every proposal is bound to exact Envelope/CWM revisions and current-turn
   digest.
5. Unknown schema, type, role, operation, or field fails closed.
6. Source anchoring is required for every material proposal candidate.
7. Deterministic parser reproducibility is evidence, not authority.
8. External LLM confidence and multi-interpreter majority never resolve
   material conflict.
9. Comparison is order-independent and interpreter-identity-independent.
10. Any stale proposal produces no update.
11. At most one atomic CWM revision results from one accepted human turn.
12. Interpreter metadata is excluded from candidate projection and Objective
    Commitment.
13. Confirmation and commitment are deterministic human controls, never
    interpreted semantics.
14. Interpreters never call or influence Platform Core, Objective, Replay,
    Development Governance, Authorization, Worker, or Completion.
15. External provider participation is optional; its absence produces
    clarification/fail-closed behavior, not reduced safeguards.

## Future Implementation Roadmap

This roadmap does not authorize implementation:

| Sequence | Future work | Dependency | Boundary classification |
|---:|---|---|---|
| 1 | Freeze closed request/proposal/descriptor schemas and canonical encoding | G57-02/G57-03/G57-04 | Architecture-only prerequisite |
| 2 | Publish pure validation/comparison/reducer test vectors | Step 1 | No provider/runtime integration |
| 3 | Implement isolated descriptor registry and lifecycle validator | Steps 1-2 | Conversation-owned local control |
| 4 | Implement source-span, taxonomy, boundary, digest, and stale-revision validators | Steps 1-2 | Deterministic trust boundary |
| 5 | Implement pure deterministic parser with immutable grammar proof | Steps 3-4 | No Objective/Platform Core import |
| 6 | Implement order-independent comparator and conflict-to-clarification reducer | Steps 2-5 | No CWM write yet |
| 7 | Add bounded local proposal lifecycle controls to versioned CWM V2 | G57 V2 runtime plus Steps 3-6 | Local mutable storage only |
| 8 | Integrate expected-revision atomic reducer with Semantic CWM V2 | Steps 6-7 | Sole state mutation point |
| 9 | Specify privacy, retention, credential, regional-processing, and external-enable policy | Separate security/governance authorization | External prerequisite |
| 10 | Implement dedicated proposal-only external interpreter host/transport using fake provider first | Steps 3-6 and 9 | No Replay/Worker/tools |
| 11 | Certify parser/provider parity, conflict, timeout, injection, stale-state, and no-authority properties | Steps 5-10 | Required before live provider |
| 12 | Separately authorize live external provider configuration and run bounded conversation-only validation | Step 11 | No Objective Commitment |
| 13 | Validate integration with G57-04 clarification/review/confirmation scenarios | Steps 8 and 12 | Still pre-commit |
| 14 | Re-audit future Objective Commitment compatibility and certify full human conversation path | G57 commitment implementation | Existing pipeline unchanged |

## Required Future Tests

- descriptor schema, lifecycle, immutable-version, and false-access tests;
- request minimization, exact revision, byte limit, and context-leak tests;
- deterministic parser reproducibility/golden/property tests across whitespace, Unicode,
  locale, multiline, and adversarial text;
- proposal schema, forbidden-key, boundary-flag, digest, source-offset,
  taxonomy, operation, dependency, and stale-state tests;
- confidence non-authority and heterogeneous-scale tests;
- permutation tests proving comparison output is interpreter-order independent;
- consensus, compatible union, partial coverage, material conflict, invalid
  alternative, and all-rejected tests;
- tests proving majority/high-confidence/provider reputation cannot override a
  valid conflict;
- external timeout, malformed output, tool-call, prompt-injection, secret,
  oversize, and provider-unavailable tests;
- race tests proving no state lock is held during provider latency and stale
  CAS returns no update;
- static/import and runtime spy tests proving no interpreter reaches CWM writes,
  Platform Core, Objective, Replay, Development Governance, Authorization,
  Worker, Completion, filesystem mutation, or tools;
- tests proving confirmation/commitment words cannot be promoted to control
  acts by an interpreter; and
- G55/G57 regression and complete architecture-boundary test suites.

## Validation Evidence

Focused existing Conversation, admission, Objective-boundary,
provider-assistance, and external-LLM attachment regression:

```text
python -m pytest -q \
  tests/test_g55_03_conversation_working_memory_runtime.py \
  tests/test_g49_02_platform_core_conversation_boundary.py \
  tests/test_g54_09_platform_core_admission_precedence.py \
  tests/test_g21_02_platform_project_objective_inference.py \
  tests/test_g47_r01_objective_task_intake_compatibility.py \
  tests/test_provider_assisted_intent_classification_v1.py \
  tests/test_provider_assisted_conversation_runtime_v1.py \
  tests/test_live_external_llm_provider_v1.py \
  tests/test_real_external_llm_attachment_v1.py \
  tests/test_external_llm_attachment_pressure_validation_v1.py
110 passed in 2.64s
```

Governance conformance tests:

```text
python -m pytest -q tests/test_governance_conformance.py
5 passed in 0.03s
```

Read-only repository conformance engine:

```text
python -m runtime.governance.governance_conformance_engine
status: PARTIALLY_CONFORMANT
checks_passed: 18
checks_failed: 2
critical_violations: 0
deterministic: true
fail_closed: true
read_only: true
report_hash: 0790499ee53f9a82e15225e15eff1c2637b7e60523fa38be0c921281abe4cbea
```

The two pre-existing failures remain visible:

- the expected repository-root and installed pre-commit hooks are missing; and
- the system pre-commit hook lacks `promotion_gate_v02` and
  `check_layer_freeze` tokens.

The diagnostic executed successfully and reports zero critical violations,
but repository-wide status remains `PARTIALLY_CONFORMANT`.

G48 structure and repository whitespace:

```text
awk 'BEGIN { fence=0; count=0 } /^```/ { fence=!fence; next } \
  !fence && /^# / { count++; print count ":" $0 } \
  END { if (count != 6) exit 1 }' \
  docs/governance/G58_01_CONVERSATION_INTERPRETER_ARCHITECTURE_REPORT_V1.md
1:# 1. Implementation Summary
2:# 2. Code Evidence
3:# 3. Constitutional Self-Assessment
4:# 4. Validation Matrix
5:# 5. Repository Mutation Summary
6:# 6. Certification Verdict

git diff --check
<no output; exit 0>
```

## Responsibility Boundaries

- Human interaction supplies current-turn communication and explicit
  deterministic lifecycle/confirmation/commitment controls.
- Conversation Envelope supplies invocation locality, availability, privacy
  restriction, TTL, and revision bindings.
- Interpreter registry describes proposal capabilities and lifecycle only.
- Deterministic/external interpreters produce untrusted proposal objects only.
- Conversation Layer exclusively owns request minimization, interpreter
  selection, proposal validation, comparison, conflict disposition, reduction,
  and expected-revision CWM submission.
- Semantic CWM owns provisional/asserted/confirmed typed state and history only
  after the Conversation reducer's atomic transaction.
- Future Objective Commitment and existing Objective/pipeline owners retain all
  G57-04 and downstream responsibilities.

# 3. Constitutional Self-Assessment

## Verified

- The architecture defines one narrow two-method interpreter abstraction with
  no state or pipeline handle.
- Descriptor, registry, invocation, and proposal lifecycles have closed entry,
  exit, limit, and fail-closed rules.
- Deterministic parser integration is pure/reproducible locally and remains
  proposal-only.
- External LLM integration has a minimal context capsule, dedicated non-Worker
  provider boundary, no tools, no secrets, and no Replay path.
- The proposal model binds every candidate to source spans, exact state
  revisions, closed G57 taxonomy, fixed false authority flags, and a digest.
- Fourteen deterministic validation/reduction stages separate proposal return
  from the sole atomic Semantic CWM transaction.
- Multi-interpreter comparison is canonical and order-independent; material
  conflict requires human clarification without voting or confidence override.
- Confidence layers are explicit, advisory, and excluded from Objective
  readiness and commitment.
- Conversation Envelope, Semantic CWM, G57-04 human protocol, and future
  Objective Commitment interactions preserve their existing owners.
- Interpreters have no architectural route to Platform Core, Objective,
  Development Governance, Capability, Replay, Authorization, Worker, or
  Completion.
- No runtime, API, test, PCBV31 record, constitutional artifact, or existing
  governance report was modified.

## Not Verified

- No interpreter interface, registry, parser, proposal schema, validator,
  comparator, reducer, host, transport, or CWM V2 integration is implemented.
- External provider privacy, retention, credential, regional-processing,
  procurement, and live-enable contracts are not specified or certified.
- Exact request/proposal/capsule/history byte and item budgets have not been
  measured against real multi-turn sessions.
- No live or fake external LLM invocation was performed in this generation.
- Deterministic parser coverage, languages, grammar rules, normalization proof,
  and human-source-to-`ASSERTED` policy remain future implementation details.
- The current provider-assisted classifier and Objective clause-role function
  were not reused because their ownership/Replay/routing surfaces do not match
  this architecture.
- G57 Envelope V2, Semantic CWM V2, state machine, Objective Commitment, and
  human interface integration remain unimplemented.
- Repository-wide conformance retains the declared existing hook drift; this
  architecture does not claim to repair or conceal it.

# 4. Validation Matrix

| Requirement | Evidence | Validation | Result |
|---|---|---|---|
| Interpreter abstraction | Two-method canonical interface and prohibited operations | Ownership and surface-minimization review | PASS |
| Interpreter lifecycle | Registry and invocation lifecycle tables | Entry/exit/failure review | PASS |
| Capabilities and limits | Allowed/prohibited capability lists and descriptor | Checked against all requested interpreter responsibilities | PASS |
| Deterministic parser integration | Pure grammar profile and independent proof | Compared with current co-located clause interpreter boundary | PASS |
| External LLM integration | Host/transport/prompt/variability model | Trust, privacy, tool, credential, and authority review | PASS |
| Semantic proposal format | Closed proposal/candidate/boundary models | Field-by-field owner and forbidden-key review | PASS |
| Proposal lifecycle | Nine-state lifecycle table | Confirmed no CWM effect before consumed transaction | PASS |
| Confidence reporting | Three-layer confidence model | Verified no numeric/majority authority or commitment effect | PASS |
| Multi-interpreter comparison | Selection, key, and six dispositions | Order-independence and conflict-safety review | PASS |
| Conflict resolution | Human clarification-only protocol | Confirmed no interpreter adjudication or vote | PASS |
| Deterministic validation | Fourteen-stage validation/reduction flow | Static fail-closed ordering review | PASS |
| No direct CWM mutation | Interface, diagrams, reducer boundary | Confirmed only Conversation reducer constructs update | PASS |
| Conversation Envelope interaction | Exact locality/freshness and availability contract | Compared with G57-03 | PASS |
| Semantic CWM interaction | Six-class and status ownership rules | Compared with G57-02 | PASS |
| G57-04 interaction | State-by-state invocation restrictions | Compared with clarification/confirmation/commitment protocol | PASS |
| Objective Commitment compatibility | Proposal exclusion and human control sequence | Confirmed interpreter metadata is absent from commitment | PASS |
| Platform Core/Objective exclusion | Boundary flags, request/proposal exclusions, diagrams | Static ownership review | PASS |
| Replay/Governance/Authorization/Worker exclusion | Fixed flags and unavailable APIs | Static ownership and dataflow review | PASS |
| Security/failure behavior | Failure/attack matrix | Injection, timeout, secret, stale, bounds, and conflict review | PASS |
| Implementation roadmap | Fourteen ordered future steps | Dependency and constitutional-boundary review | PASS |
| Runtime interpreter behavior | Proposed future implementation | Architecture only; implementation forbidden | NOT_APPLICABLE |
| Live external LLM behavior | Proposed future provider integration | No live invocation authorized | NOT_APPLICABLE |
| Existing conversation/provider boundary regression | Focused existing test suites | Executed after report creation | PASS |
| Governance conformance tests | Existing governance conformance suite | Executed after report creation | PASS |
| Governance diagnostic and limitation visibility | Existing read-only conformance engine | Executed; known hook drift remains visible | PASS |
| G48 report structure | This report | Verified exactly six top-level sections in required order | PASS |
| Repository whitespace integrity | Current diff | `git diff --check` | PASS |
| Forbidden mutation absence | Git status and diff inventory | Confirmed only this report was added | PASS |

# 5. Repository Mutation Summary

Modified files:

- `docs/governance/G58_01_CONVERSATION_INTERPRETER_ARCHITECTURE_REPORT_V1.md`:
  added the architecture-only interpreter abstraction, lifecycle, proposal
  model, deterministic/external integration, validation, comparison, trust
  boundaries, compatibility, roadmap, evidence, and verdict.

Unchanged subsystems:

- Platform Core, AiCLI, Human Interface Runtime, and Conversation Layer
  runtime.
- G55-03 CWM runtime and G57 architecture artifacts.
- Objective and Development Governance.
- Capability selection/execution binding, G31, and G35.
- Replay and Authorization.
- Worker lifecycle, provider Workers, dispatch, execution, Completion, and
  presentation.
- PCBV31 and every constitutional specification, manifest, and baseline.

API compatibility:

- No runtime API, registry, provider, or persisted schema changed.
- The proposed interface is future versioned architecture and does not
  reinterpret existing Objective inference or provider-assisted APIs.

Boundary preservation:

- Interpreters are proposal-only and cannot mutate Semantic CWM directly.
- Conversation Layer retains exclusive deterministic validation/reduction.
- Objective Commitment and every certified downstream owner remain outside the
  interpreter layer.

Unrelated pre-existing changes:

- None observed before this report was created.

# 6. Certification Verdict

CONVERSATION_INTERPRETER_ARCHITECTURE_CHARACTERIZED
