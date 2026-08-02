# 1. Implementation Summary

Generation: G65-05

Report identity: G65_05_SELF_KNOWLEDGE_QUERY_RUNTIME_IMPLEMENTATION_REPORT_V1

Constitutional baseline: `CONSTITUTIONAL_GOVERNANCE_CLOSED`,
`SELF_KNOWLEDGE_ARCHITECTURE_CERTIFIED`,
`SELF_KNOWLEDGE_EVIDENCE_MANIFEST_ESTABLISHED`,
`SELF_KNOWLEDGE_SNAPSHOT_RUNTIME_ESTABLISHED`, and
`SELF_KNOWLEDGE_SNAPSHOT_VALIDATION_ESTABLISHED`.

Implementation contracts: G48 Constitutional Evidence Reporting Standard V1;
G65-01 through G65-04 certified architecture, manifest, snapshot, and snapshot
validation contracts.

Reporting date: 2026-08-02.

Objective:

Implement a deterministic, read-only Self Knowledge Query Runtime that
projects only bounded, fixed views from one already validated Self Knowledge
Snapshot. It must never inspect the repository, rebuild evidence, infer facts,
generate explanations, mutate state, or initiate development or execution.

Implementation scope:

- Add closed, versioned query-request and query-response schemas.
- Admit only eight exact query subject tokens and map each to a fixed tuple of
  authenticated snapshot source classes.
- Require the exact G65-03 snapshot artifact/version/hash and a successful,
  hash-valid G65-04 validation artifact bound to that snapshot.
- Return exact snapshot evidence records, preserving source identifiers,
  paths, SHA-256 values, authority classes, section/status/limitation source
  identifiers, content, and evidence-record hashes without semantic changes.
- Add public request/response validators, deterministic response identity,
  bounded unavailable/conflict handling, and focused fail-closed regressions.

Modified modules:

- `aigol/runtime/self_knowledge_query_runtime.py` — closed request/response
  schemas, validated-snapshot admission, fixed projection, and validators.
- `tests/test_g65_05_self_knowledge_query_runtime.py` — focused coverage for
  all supported views and required negative boundaries.
- `docs/governance/G65_05_SELF_KNOWLEDGE_QUERY_RUNTIME_IMPLEMENTATION_REPORT_V1.md`
  — this G48 implementation report.

Intentionally unchanged modules:

- G65-02 manifest behavior; G65-03 snapshot behavior; G65-04 validation
  behavior; Platform Knowledge; Platform Core admission; Conversation Layer;
  Development Governance; Constitutional Reuse Proof; G48 completion;
  Authorization; Worker; Replay; providers; capability registry; and
  governance conformance behavior.

Architectural boundaries preserved:

- Query execution receives no repository root or manifest input. It uses only
  the snapshot and the successful G65-04 validation artifact bound to that
  snapshot.
- Projection is exact record filtering. It does not parse or summarize source
  content, reconcile conflicts, rank sources, choose a latest source, infer
  certification, or generate natural-language explanation.
- Request and response artifacts explicitly remain read-only and record that
  no Objective, Reuse Proof, G47 request, Authorization, Worker/provider
  request, Replay event, governance mutation, or execution was created.

# 2. Code Evidence

## Public API

`aigol/runtime/self_knowledge_query_runtime.py` exposes four operations:

```python
def create_self_knowledge_query_request(
    *,
    query_subject: str,
    snapshot: dict[str, Any],
    snapshot_validation: dict[str, Any],
) -> dict[str, Any]:

def validate_self_knowledge_query_request(
    request: dict[str, Any],
    *,
    snapshot: dict[str, Any],
    snapshot_validation: dict[str, Any],
) -> dict[str, Any]:

def execute_self_knowledge_query(
    *,
    request: dict[str, Any],
    snapshot: dict[str, Any],
    snapshot_validation: dict[str, Any],
) -> dict[str, Any]:

def validate_self_knowledge_query_response(
    response: dict[str, Any],
    *,
    request: dict[str, Any],
    snapshot: dict[str, Any],
    snapshot_validation: dict[str, Any],
) -> dict[str, Any]:
```

There is no free-form text, repository-root, manifest, Conversation, provider,
Worker, or execution parameter.

## Orchestration Entry Point

Execution validates the request, snapshot envelope/integrity, and successful
G65-04 artifact before selecting records:

```python
validated_request = validate_self_knowledge_query_request(
    request,
    snapshot=snapshot,
    snapshot_validation=snapshot_validation,
)
validated_snapshot = _validate_snapshot_envelope(snapshot)
validated_validation = _validate_snapshot_validation(
    snapshot_validation,
    snapshot=validated_snapshot,
)
```

No filesystem or runtime discovery owner is consulted.

## Query and Response Schemas

The closed `SELF_KNOWLEDGE_QUERY_REQUEST_V1` schema contains:

```text
artifact_type
request_version
query_subject
snapshot_artifact_type
snapshot_version
snapshot_hash
snapshot_validation_hash
read_only
request_hash
```

The closed `SELF_KNOWLEDGE_QUERY_RESPONSE_V1` schema contains:

```text
artifact_type
response_version
request_hash
query_subject
projection_status
unavailable_reason
snapshot_artifact_type
snapshot_version
snapshot_hash
manifest_artifact_type
manifest_version
manifest_hash
snapshot_validation_hash
projected_source_classes
fact_count
facts
boundary_flags
response_hash
```

Both identities use the existing canonical JSON SHA-256 primitive. Every fact
is an unchanged closed G65-03 evidence record rather than a new semantic fact
model.

## Closed Query Vocabulary

The exact public vocabulary is:

```python
SUPPORTED_QUERY_SUBJECTS = (
    "ARCHITECTURE",
    "RUNTIME_INVENTORY",
    "CERTIFIED_CAPABILITIES",
    "OWNERSHIP",
    "GOVERNANCE_STATE",
    "EXECUTION_BOUNDARIES",
    "CERTIFIED_HISTORY",
    "KNOWN_LIMITATIONS",
)
```

No normalization occurs. Lowercase text, sentences, combined subjects, empty
values, non-string values, and unknown tokens fail closed.

## Deterministic Projection Rules

The static, immutable mapping is:

| Query subject | Exact source classes |
|---|---|
| `ARCHITECTURE` | `CONSTITUTION`, `ENFORCEMENT_AND_LINEAGE` |
| `RUNTIME_INVENTORY` | `CAPABILITY_REGISTRY` |
| `CERTIFIED_CAPABILITIES` | `CAPABILITY_REGISTRY` |
| `OWNERSHIP` | `OWNER_AND_BOUNDARY` |
| `GOVERNANCE_STATE` | `GOVERNANCE_STATE` |
| `EXECUTION_BOUNDARIES` | `ENFORCEMENT_AND_LINEAGE`, `OWNER_AND_BOUNDARY` |
| `CERTIFIED_HISTORY` | `CERTIFIED_HISTORY` |
| `KNOWN_LIMITATIONS` | `KNOWN_LIMITATION` |

Filtering traverses the already canonical snapshot order once:

```python
facts = [
    deepcopy(record)
    for record in validated_snapshot["evidence_records"]
    if record["source_class"] in projected_classes
]
```

The runtime never scores, dynamically orders, selects latest, searches, or
reconciles records. With no matching authenticated records it returns
`UNAVAILABLE/AUTHENTICATED_EVIDENCE_UNAVAILABLE`. Conflicting bindings for one
class/source identity return
`UNAVAILABLE/AUTHENTICATED_EVIDENCE_CONFLICT` with no facts.

## Source Reference Preservation

Every returned fact is an exact deep copy of its snapshot evidence record and
therefore retains:

- `source_id`, repository-relative `path`, source `sha256`, and
  `authority_class`;
- `source_class`, `schema_or_section_identifier`, and `required` status;
- exact source content, encoding, and byte length, so explicit source status
  or limitation text remains intact where present;
- the original `evidence_record_hash`.

Focused equality coverage compares projected facts directly to the selected
snapshot records, demonstrating no field loss or synthesized status.

## Fail-Closed Validation

The request validator first rejects recursively nested authority-shaped keys,
then requires the exact closed schema, one supported token, snapshot and
G65-04 validation identities, read-only status, and request hash.

The response validator checks its exact schema, constitutional boundary flags,
and response hash, then deterministically reconstructs the complete expected
response:

```python
expected = execute_self_knowledge_query(
    request=request,
    snapshot=snapshot,
    snapshot_validation=snapshot_validation,
)
if response != expected:
    _fail("query response deterministic reconstruction mismatch")
```

Snapshot admission rechecks exact artifact/version/boundary flags, record
shape, UTF-8 byte length, source digest, evidence-record hashes, canonical
identity order, and snapshot hash. G65-04 evidence must have its exact passing
status, all verification flags, snapshot/manifest/count/class bindings, and
canonical validation hash.

## Constitutional Boundary Verification

- Platform Knowledge remains the owner of its existing capability-oriented
  knowledge service. G65-05 creates a distinct fixed snapshot projection only.
- Platform Core admission, Development Governance, Reuse Proof, G48,
  Authorization, Worker, Replay, and provider selection are neither imported
  nor invoked.
- Conversation remains non-authoritative and outside the API.
- Response boundary flags explicitly prohibit semantic interpretation,
  dynamic ranking, latest selection, natural-language generation, authority
  creation, governance mutation, and execution initiation.

# 3. Constitutional Self-Assessment

## Verified

- All eight exact query subjects produce an available response containing only
  their fixed source classes.
- Repeated identical queries produce identical response values and hashes.
- Projected facts equal the selected snapshot records exactly and preserve
  canonical snapshot order, source references, digests, authority classes,
  section/status/limitation identifiers, content, and record hashes.
- Every request/response binds the exact snapshot artifact, version, digest,
  and successful G65-04 validation digest; responses also bind the manifest
  artifact, version, and digest carried by the snapshot.
- Unsupported, lowercase, natural-language, combined/ambiguous, empty, and
  non-string subjects fail closed.
- Invalid/tampered snapshots, malformed requests, unsuccessful G65-04
  evidence, response tampering, and authority-shaped request fields fail
  closed.
- A no-record projection returns a bounded unavailable response with zero
  facts rather than inferring an answer.
- Repository byte/text access was disabled during a successful full query and
  response-validation round trip, demonstrating no repository inspection.
- Static inspection confirms no Conversation, provider, Worker,
  Authorization, Governance, Replay-runtime, or execution-owner import and no
  search/walk/glob/subprocess behavior.

## Not Verified

- No natural-language explanation, semantic fact extraction, conflict
  reconciliation, source ranking, latest-source selection, or inferred
  certification is implemented or authorized.
- No query integration with Platform Core routing, Platform Knowledge,
  Conversation, Human Interface, AiCLI, or any external transport is
  implemented.
- Query responses are returned in memory and are not persisted or written to
  Replay history.
- The complete repository test suite was not run. Validation is limited to the
  required G65-02 through G65-05, Platform Knowledge, capability-registry, and
  governance conformance suites listed below.

# 4. Validation Matrix

| Requirement | Evidence | Validation | Result |
|---|---|---|---|
| Closed versioned request schema | `_REQUEST_FIELDS`, request version/hash | Positive request validation and malformed-request regression | `PASS` |
| Closed versioned response schema | `_RESPONSE_FIELDS`, response version/hash | Deterministic response reconstruction and tamper regression | `PASS` |
| All eight supported subjects | Exact vocabulary and immutable view map | Eight parameterized subject cases | `PASS` |
| Deterministic repeated response | Fixed filtering and canonical hashing | Repeated `EXECUTION_BOUNDARIES` equality | `PASS` |
| Exact source-reference/digest preservation | Facts are unchanged snapshot records | Fact-to-snapshot equality and order assertions | `PASS` |
| Snapshot identity/digest binding | Request/response snapshot fields and hash validation | Exact snapshot/manifest/G65-04 binding assertions | `PASS` |
| Unsupported/free-form/ambiguous rejection | Exact-token validator | Six malformed subject cases | `PASS` |
| Invalid/tampered snapshot rejection | Closed snapshot envelope, source/record/snapshot hashes | Invalid artifact and changed-content cases | `PASS` |
| Malformed request and unsuccessful G65-04 rejection | Closed request and validation-artifact contracts | Missing field and changed validation status | `PASS` |
| Response tampering rejection | Response hash and deterministic reconstruction | Changed source identity case | `PASS` |
| Authority-field rejection | Recursive forbidden-key check | Eight authority-shaped field cases | `PASS` |
| Unavailable evidence handling | Bounded `UNAVAILABLE` disposition | Isolated no-matching-record projection case | `PASS` |
| No repository scan | Query API has no root/path and imports no filesystem API | Repository read methods disabled during successful round trip | `PASS` |
| Constitutional owner isolation | Import/call boundary and response flags | Focused AST/text guard | `PASS` |
| Focused G65-05 suite | Query regression module | `pytest -q tests/test_g65_05_self_knowledge_query_runtime.py` — 30 passed | `PASS` |
| Required regression compatibility | G65-02 through G65-05, Platform Knowledge, capability registry, and governance conformance | Selected required regression command — 69 passed | `PASS` |
| Python compilation | New query runtime module | `python -m py_compile aigol/runtime/self_knowledge_query_runtime.py` | `PASS` |
| Read-only governance conformance | Existing conformance engine | `python -m runtime.governance.governance_conformance_engine` — 20 passed, 0 failed, 0 warnings, `CONFORMANT` | `PASS` |
| Complete repository regression | Not run; not required for this bounded generation | Explicitly omitted and declared under `Not Verified` | `NOT_APPLICABLE` |
| Diff whitespace integrity | G65-05 changed files | `git diff --check` | `PASS` |

# 5. Repository Mutation Summary

Modified files:

- `aigol/runtime/self_knowledge_query_runtime.py` — closed query/response
  contracts, snapshot admission, fixed projections, and validators.
- `tests/test_g65_05_self_knowledge_query_runtime.py` — focused positive,
  deterministic, unavailable, tamper, malformed, and authority regressions.
- `docs/governance/G65_05_SELF_KNOWLEDGE_QUERY_RUNTIME_IMPLEMENTATION_REPORT_V1.md`
  — G48 implementation evidence.

Unchanged subsystems:

- G65-02 manifest behavior; G65-03 snapshot behavior; G65-04 snapshot
  validation behavior; Platform Knowledge; Platform Core admission;
  Conversation Layer; Development Governance; Constitutional Reuse Proof;
  G48 completion; Authorization; Worker; Replay; providers; capability
  registry; and governance conformance rules.

API compatibility:

- The only new API is the isolated query request/response runtime. No existing
  schema, route, knowledge service, provider, Worker, replay, authorization,
  certification, governance, or policy behavior changed.

Boundary preservation:

- G65-05 adds no repository discovery, semantic inference, natural-language
  generation, state mutation, Conversation interaction, Objective, Reuse
  Proof, G47 request, Authorization, Worker/provider request, Replay event,
  governance mutation, or execution path.

Unrelated pre-existing changes:

- None observed at implementation start.

# 6. Certification Verdict

SELF_KNOWLEDGE_QUERY_RUNTIME_ESTABLISHED
