# Generation 31-02 Product 1 Decision Validation Packet Certified Operational Onboarding

Status: implemented and validated.

Date: 2026-07-15

Implementation verdict:

`PRODUCT1_DECISION_VALIDATION_PACKET_CERTIFIED_OPERATIONALLY_ONBOARDED`

## Constitutional scope

This milestone extends the immutable Generation 30 certified baseline with
exactly one existing Product 1 capability:

`PRODUCT1_DECISION_VALIDATION_PACKET_GENERATION`

It does not reopen Platform Core, G28, G29, Generation 30, Replay,
Governance, Project Objective, Platform Knowledge, Platform Query Router,
Canonical Platform Presentation, or Human Interface authority. It adds no
router, selection algorithm, lifecycle stage, clarification subsystem,
artifact discovery, Worker path, Provider path, or mutation authority.

The capability reuses the existing deterministic implementation and
certification evidence in
`aigol.runtime.product1_decision_validation_packet_certification_v1`.
No second packet-generation algorithm was created.

## Capability and certification binding

The static onboarding contract is:

| Contract element | G31-02 binding |
|---|---|
| Capability identity | `PRODUCT1_DECISION_VALIDATION_PACKET_GENERATION` |
| Capability owner | `PRODUCT1_AI_DECISION_VALIDATOR` |
| Certification status | `CERTIFIED` / `RUNTIME` |
| G28 adapter | `G31_02_PRODUCT1_DECISION_VALIDATION_PACKET_ADAPTER_V1` |
| Canonical input family | `PRODUCT1_DECISION_VALIDATION_REQUEST_ARTIFACT_V1` |
| Canonical output family | `PRODUCT1_DECISION_VALIDATION_PACKET_ARTIFACT_V1` |
| Invocation mode | deterministic, read-only, static allowlist |
| Current-run Provider / Worker | prohibited |
| Repository mutation | prohibited |

The certification registry record binds the existing Product 1 Decision
Validation Packet certification report to this operational capability. The
G28 adapter delegates to the existing packet generator and reconstructor.

## Canonical immutable input contract

The Product 1 decision-validation request is an immutable, hash-addressed
artifact created from caller-supplied exact evidence roots. It records:

- one request identity and capability identity;
- exact Product 1 end-to-end certification root;
- exact multi-provider readiness certification root;
- the exact certified scenario Replay root;
- 19 source references with their canonical content hashes;
- one deterministic source-manifest hash;
- explicit read-only and non-authority boundary flags.

The request validator performs no discovery. It reconstructs the pinned
Product 1 certification, reconstructs the pinned provider-governance Replay,
checks the provider-readiness verdict, verifies all source content hashes,
and verifies the ordered nine-step scenario Replay and its nested artifact
hashes.

Malformed requests, unsupported identities, changed source artifacts,
substituted references, invalid source hashes, non-certified lineage, and
boundary changes fail closed before G28 invocation.

## G28 and G29 onboarding lifecycle

The capability uses the existing extension points:

1. the certification registry returns the static certified record;
2. the G29 semantic descriptor recognizes Product 1 packet validation,
   review, explanation, and audit objectives;
3. without a compatible canonical artifact, G29 asks one owner-specific
   `input_artifact_family` clarification and does not invoke G28;
4. G29-08 resolves only an explicit opaque Replay-wrapper reference and
   dispatches to the Product 1 request validator;
5. G29-06 deterministically projects the validated request artifact,
   request identity, and artifact hash into the existing G28 input contract;
6. Platform Knowledge verifies the exact capability certification record;
7. unchanged G29-04 invokes unchanged G28 through the static adapter;
8. the existing packet generator produces the existing canonical output;
9. native reconstruction revalidates every pinned source and regenerates the
   packet deterministically before accepting the recorded output;
10. Canonical Platform Presentation projects the enterprise-readable packet;
11. the existing nested route reconstructor verifies selection, knowledge,
    lifecycle, invocation, packet, and presentation lineage.

Selection remains distinct from authorization. Natural language is never
treated as canonical decision evidence.

## Clarification continuation integration

Focused real-session testing exposed one bounded continuation defect before
capability invocation. The original Project Objective was correctly
preserved, but the attachment turn recomputed optional generic candidate
discovery from a workspace that now contained the active objective. That
changed a confidence value, and G29 correctly rejected the non-originating
candidate evidence as a lineage mismatch.

The bounded repair does not change G29 selection or scoring. Owner-specific
continuation now supplies the mandatory, replay-validated originating Project
Objective without supplying newly recomputed optional discovery evidence.
This uses the existing G29 contract, under which candidate-discovery evidence
is optional while Project Objective identity is mandatory. Clarification
owner, semantic slot, originating route, objective, explicit ingress, and
attachment-attempt lineage remain fail-closed and reconstructable.

## Canonical Product 1 presentation

The presentation exposes the existing enterprise packet sections:

- packet metadata and decision summary;
- historical Provider and Worker participation summaries;
- approval and authorization summaries;
- verification and audit conclusions;
- boundary guarantees and reviewer next actions.

The presentation explicitly distinguishes historical evidence from the
current invocation. The certified source packet describes bounded historical
Provider participation and Worker execution. The G31-02 packet-generation
request itself invokes no Provider or Worker, authorizes no execution, and
mutates no repository.

## Replay and tamper evidence

Successful reconstruction covers:

```text
operational turn
  -> Project Objective
  -> owner-specific clarification
  -> attachment attempt(s)
  -> G29-08 explicit ingress
  -> G29-02 selection
  -> Platform Knowledge
  -> G29-04 lifecycle
  -> G28 invocation
  -> native Product 1 packet Replay
  -> Canonical Platform Presentation
```

The native packet reconstructor validates the request, all 19 pinned sources,
both certification lineages, the scenario Replay, the packet artifact, the
current-run authority flags, and exact deterministic regeneration of the
packet. Recomputed wrapper hashes cannot conceal packet substitution.

Ingress and operational reconstruction fail closed on invalid wrapper hashes,
source substitution, out-of-root references, clarification owner or slot
substitution, route or objective tampering, removed or reordered retries,
packet substitution, and presentation substitution.

## Real terminal validation

A real PTY-backed `./aicli` session used this request:

```text
Validate a Product 1 Decision Validation Packet from certified Replay evidence.
Audit only.
Do not implement anything.
Do not mutate the repository.
```

Observed sequence:

1. Platform Core returned an owner-specific `input_artifact_family`
   clarification and recommended `/attach <reference>`;
2. an out-of-root wrapper reference failed closed before semantic
   continuation, leaving the original clarification active;
3. a compatible immutable wrapper under the allowed runtime root was attached;
4. G29 selected `PRODUCT1_DECISION_VALIDATION_PACKET_GENERATION`;
5. Platform Knowledge, G29-04, unchanged G28, packet reconstruction, and
   canonical presentation completed;
6. Replay reconstructed two ordered attachment attempts with final status
   `ATTACHMENT_RETRY_COMPLETED`;
7. the final route reported `provider_invoked: false`,
   `worker_invoked: false`, and `repository_mutated: false`;
8. AiCLI closed with `aicli_authorizes: false`, `aicli_executes: false`, and
   `aicli_owns_replay: false`.

## Authority confirmation

| Responsibility | Preserved owner |
|---|---|
| Project Objective, semantic intent, and clarification | Platform Core |
| Canonical artifact resolution and validation | G29-08 / Platform Core |
| Semantic capability selection | G29-02 |
| Selection-to-invocation lifecycle | G29-04 |
| Certified invocation | G28 |
| Packet generation and native validation | existing Product 1 runtime |
| Presentation | Canonical Platform Presentation |
| Replay recording and reconstruction | Replay |
| Opaque input transport and rendering | AiCLI |
| Provider and Worker operation | separate Provider and Worker platforms |

The current invocation is deterministic and read-only. It performs no
artifact discovery, Provider invocation, Worker invocation, execution
authorization, deployment, repository mutation, or external integration.

## Validation evidence

Validation completed on 2026-07-15:

- focused G31-02 onboarding tests: **6 passed, 0 skipped, 0 failed**;
- affected Product 1, G28, G29, and Generation 30 tests:
  **121 passed, 0 skipped, 0 failed**;
- Product 1 packet plus focused G31-02 tests:
  **10 passed, 0 skipped, 0 failed**;
- G28 regressions: **14 passed, 0 skipped, 0 failed**;
- G29 regressions: **59 passed, 0 skipped, 0 failed**;
- all Generation 30 tests: **38 passed, 0 skipped, 0 failed**;
- Project Services, Platform Knowledge, Platform Query Router, Human
  Interface, and AiCLI tests: **61 passed, 0 skipped, 0 failed**;
- Replay-named tests: **245 passed, 0 skipped, 0 failed**;
- governance-named tests: **187 passed, 0 skipped, 0 failed**;
- governance conformance tests: **5 passed, 0 skipped, 0 failed**;
- full repository suite, final run:
  **6,174 passed, 1 skipped, 0 failed**;
- targeted `py_compile`: passed;
- `git diff --check`: passed;
- real PTY-backed invalid-then-valid attachment lifecycle: passed;
- real operational Replay reconstruction: passed.

The first full-suite attempt recorded **6,173 passed, 1 skipped, 1 failed**
because one ACLI hardening test transiently observed a successful turn where
its fail-closed fixture was expected. The failing test passed immediately in
isolation, its complete six-test file passed, and the exact first 54-test
collection prefix passed. The unmodified second full-suite run passed all
6,174 executed tests. This is recorded as a non-blocking suite observation,
not hidden as a capability failure. Focused counts overlap broader suites and
must not be added together.

The deterministic governance conformance engine reported:

- status: `PARTIALLY_CONFORMANT`;
- checks passed: 18;
- checks failed: 2;
- critical violations: 0;
- deterministic: true;
- fail-closed: true;
- read-only: true.

The two failures are the known pre-existing root and system pre-commit hook
drift findings. G31-02 did not alter or conceal them.

## Reusable Product 1 onboarding pattern

Future Product 1 read-only capabilities should reuse this bounded sequence:

```text
existing deterministic Product 1 implementation
  + existing certification evidence
  + exact immutable source-manifest artifact
  + fail-closed native validator
  + static registry and G28 adapter binding
  + one G29 descriptor and input projection
  + existing G29-08 ingress
  + native deterministic reconstruction
  + bounded enterprise presentation
  + nested operational Replay
```

Each future capability must remain independently justified. This pattern does
not authorize a new registry subsystem, product algorithm, domain catalog,
artifact discovery service, Worker or Provider expansion, dashboard, release
pipeline, or mutation path.

## Remaining bounded observations

- Request-artifact construction is currently a deterministic programmatic
  fixture operation; AiCLI transports the resulting opaque wrapper but does
  not discover or construct it. That is intentional under the certified
  Human Interface and artifact-ingress boundaries.
- The packet is generated from checked-in certified historical evidence. It
  does not claim live external validation, production readiness, general
  availability, or regulatory compliance.
- Repository governance remains `PARTIALLY_CONFORMANT` with the two known
  pre-existing hook-drift findings unless the final governance run records a
  different deterministic result.

## Recommendation for G31-03

Proceed with a bounded Product 1 enterprise acceptance audit for the newly
operational packet. Validate enterprise reviewer comprehension, the canonical
demo script, evidence navigation, and release-readiness gaps using existing
Product 1 lifecycle artifacts. Do not add runtime authority, dashboards,
external execution, artifact discovery, or deployment automation unless that
audit identifies one deterministic bounded product gap.
