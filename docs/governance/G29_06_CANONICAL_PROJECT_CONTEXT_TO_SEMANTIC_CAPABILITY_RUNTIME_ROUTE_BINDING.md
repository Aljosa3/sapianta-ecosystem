# G29-06 Canonical Project Context to Semantic Capability Runtime Route Binding

Status: implemented Platform Core integration.

## Purpose

G29-06 composes the already certified Project Objective, G29-02 selection,
Platform Knowledge, G29-04 lifecycle, unchanged G28 invocation, and Canonical
Platform Presentation responsibilities. It creates no new semantic,
certification, invocation, execution, or presentation authority.

## Runtime ownership

The binding is owned entirely by Platform Core. A Human Interface may submit
text and explicit canonical artifacts and may render the returned Platform Core
result. It does not determine route eligibility, rank candidates, choose an
artifact, invoke a capability, or authorize execution.

## End-to-end runtime transition

```text
Natural-language request
        |
        v
Platform Core Project Services
        |
        +--> validated Project Objective outside bounded G29 scope
        |          |
        |          v
        |     existing Platform Query Router
        |          |
        |          v
        |     Canonical Platform Presentation
        |
        +--> validated, non-mutating Project Objective in bounded G29 scope
                   |
                   v
             G29-02 semantic selection
                   |
          +--------+---------+
          |                  |
          v                  v
     clarification      unique selection
          |                  |
          |                  v
          |          exact explicit artifact binding
          |                  |
          |        +---------+----------+
          |        |                    |
          |        v                    v
          |   clarification      Platform Knowledge
          |                             |
          |                             v
          |                      G29-04 lifecycle
          |                             |
          |                             v
          |                      unchanged G28 binding
          |                             |
          |                             v
          |                  Canonical Platform Presentation
          |                             |
          +--------------+--------------+
                         v
             existing Human Interface projection
```

## Routing decision

The route requires a sufficient Project Objective, a non-mutating governed work
type, and objective evidence within the immutable semantic descriptor scope of
the three G28 adapters. Objectives outside that scope continue through the
existing Query Router unchanged. Eligibility is not capability selection;
G29-02 remains the only semantic scoring and ranking authority.

## Clarification flow

G29 clarification is preserved without modification and projected through the
existing Platform Core Human Interface clarification contract. Artifact
binding asks exactly one deterministic question when zero or multiple explicit
compatible artifacts remain. Neither condition may continue to G29-04.

## Explicit artifact binding

Only caller-supplied canonical artifact objects participate. The binding uses
the selected G29 input artifact types to require exactly one compatible object.
It copies the artifact's existing identifier and hashes into the exact G28
input fields. It never constructs artifact contents, identifiers, references,
or hashes from natural-language text, Project Objective prose, or semantic
descriptors.

## Platform Knowledge and lifecycle invocation

After unique selection and unique artifact binding, the binding queries the
existing Platform Knowledge runtime using the selected identifier. The full
response, response hash, immutable Replay reference, selection artifact,
concrete inputs, actor, timestamp, session, invocation identifier, and Replay
destination are passed to unchanged G29-04. G29-04 alone delegates to G28; the
G29-06 route contains no direct G28 invocation.

## Presentation and Replay continuity

Successful invocation uses the Canonical Platform Presentation produced by
G29-04 and projects it into the existing governed read-only result. Selection
and artifact clarification use the existing Human Interface clarification
projection. Fail-closed lifecycle results remain visible in that same
read-only Platform Core response contract.

The top-level route artifact binds:

- Project Objective reference and hash;
- G29 selection reference, hash, and Replay location;
- bound canonical artifact type and hash;
- Platform Knowledge response reference and hash;
- G29-04 lifecycle result hash and Replay location;
- G28-derived canonical presentation hash.

Reconstruction validates the top-level artifact, reconstructs G29 selection,
and, for a completed route, reconstructs G29-04, unchanged G28, and canonical
presentation lineage.

## Authority boundaries

- Semantic selection is not authorization.
- The Human Interface has no semantic or invocation authority.
- G28 remains the sole certified capability invocation authority.
- Worker execution authorization remains separate and is never reached.
- No Provider or Worker is invoked.
- No repository mutation is performed.
- Replay is mandatory and append-only.
- Existing Governance, Certification, Platform Knowledge, and Presentation
  semantics are unchanged.

## Known limitation

Natural-language text cannot substitute for a canonical input artifact. A
successful route therefore requires an explicit compatible artifact supplied
through the Platform Core call contract. Requests without one deterministically
clarify and remain non-invoking.
