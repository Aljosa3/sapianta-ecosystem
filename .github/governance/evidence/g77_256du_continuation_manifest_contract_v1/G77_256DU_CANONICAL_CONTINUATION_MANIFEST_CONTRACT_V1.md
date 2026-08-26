# G77-256DU Canonical SPCE Continuation Manifest Contract V1

Status: repository-side candidate contract; not authority; no operational execution authorized.

Schema identity: `SAPIANTA_SPCE_CONTINUATION_MANIFEST_SCHEMA_V1`

Manifest identity: `SAPIANTA_SPCE_CONTINUATION_MANIFEST_V1`

Envelope identity: `SAPIANTA_SPCE_CONTINUATION_MANIFEST_ENVELOPE_V1`

Version: `1.0.0`

Required source HEAD: `813fc56ef364247675e2ef07d9c27885626766c9`

## 1. Scope and constitutional boundary

This contract closes only the producer/consumer interface frontier exposed by G77-256DT. It does not retry DT, repair or rewrite DT evidence, create or boot a VM, create a Human Operational Act, enter P11 or P12, execute E05, create a production route, replay execution, grant authority, or certify CLREC.

DT remains authenticated historical fail-closed evidence: one VM was created and booted once; the continuation-manifest envelope passed its SHA-256 check; the harness then raised `KeyError: 'completed_phase_seals'` before `execution_context` and P01. DT entered neither P11 nor P12, executed no E05 case, created no Human Operational Act, performed no retry or replay, produced no production route, and completed terminal teardown. The DT failure is not an E05 result.

V1 consolidates the proven DQ completed-seal consumer pattern, DT's useful cross-account reconstruction intent, and explicit pre-materialization schema and semantic checks into one contract. It is not a parallel continuation system.

## 2. Four independent gates

The consumer MUST evaluate the following in order and MUST NOT treat an earlier PASS as proof of a later PASS:

1. `CRYPTOGRAPHIC_AUTHENTICITY`: parse duplicate-free UTF-8 JSON, require canonical bytes, recompute `manifest_sha256`, and authenticate every bound file and completed seal.
2. `STRUCTURAL_SCHEMA_VALIDITY`: require the exact envelope, schema identity/version, required fields, field types, and closed object shapes; reject missing and unknown fields.
3. `SEMANTIC_CONTRACT_COMPATIBILITY`: verify producer, consumer, schema, lineage, seal, authority, phase, counter, frontier, and prior-manifest relationships.
4. `CONSTITUTIONAL_ADMISSIBILITY`: require explicit prohibitions, non-authority semantics, Human review, and `auto_continuable=false` before any materialization decision.

Only four PASS results constitute pre-materialization compatibility. SHA-256 validity alone never does.

## 3. Canonical serialization and envelope

The only canonical representation is UTF-8 JSON with:

- duplicate object keys forbidden;
- keys sorted lexicographically at every object level;
- separators `,` and `:` with no insignificant whitespace;
- exactly one trailing LF;
- integers expressed as JSON integers, with booleans rejected as integers;
- no NaN, Infinity, comments, or alternate encodings.

The envelope has exactly three required fields and no optional fields:

| Field | Type | Rule |
| --- | --- | --- |
| `schema_id` | string | exactly `SAPIANTA_SPCE_CONTINUATION_MANIFEST_ENVELOPE_V1` |
| `manifest` | object | exact canonical manifest defined below |
| `manifest_sha256` | lowercase SHA-256 | SHA-256 of canonical serialized `manifest`, including its trailing LF |

## 4. Canonical manifest fields

The following fields are required. Unknown fields are rejected.

| Field | Type | Lifecycle and binding semantics |
| --- | --- | --- |
| `schema_id` | string | exactly `SAPIANTA_SPCE_CONTINUATION_MANIFEST_V1` |
| `manifest_version` | string | exactly `1.0.0`; incompatible versions fail closed |
| `generation_identity` | non-empty string | immutable across a prior-manifest chain |
| `required_head` | 40-character Git object | immutable across the chain and checked against the requested checkout |
| `source_tree` | 40-character Git object | source-tree identity for reconstruction |
| `current_spce_phase` | non-empty string | current persistent phase identity |
| `phase_sequence` | non-negative integer | monotonic; regression is forbidden |
| `prior_manifest_sha256` | SHA-256 or null | null only for an initial manifest; otherwise binds the prior envelope's manifest digest |
| `completed_phase_seals` | array of seal bindings | ordered, identity-unique, append-only prefix |
| `execution_counters` | exact counter object | non-negative, semantically constrained, monotonic |
| `case_counters` | object | names match `^[a-z][a-z0-9_]*_count$`; non-negative and monotonic |
| `authority_state` | exact authority object | describes state; grants no authority |
| `lineage_bindings` | non-empty array | identity-unique committed file bindings |
| `producer_binding` | file binding | exact producer bytes |
| `consumer_binding` | file binding | exact consumer-validator bytes |
| `schema_binding` | versioned file binding | exact V1 schema bytes and identity |
| `frontier_state` | exact frontier object | present frontier and next legal action |
| `selected_case` | case object or null | null when no operational case is selected |
| `first_failure_or_current_result` | non-empty string or null | evidence state, never an authority token |
| `teardown_state` | enum | `NOT_APPLICABLE`, `PENDING`, `COMPLETE`, or `FAILED` |
| `final_execution_seal` | seal binding or null | authenticated terminal seal when one exists |
| `prohibited_actions` | unique string array | explicit constitutional negative boundary |
| `checkpoint_is_authority` | boolean | exactly false |
| `manifest_is_authority` | boolean | exactly false |
| `auto_continuable` | boolean | exactly false in V1 |

Optional V1 fields are `observations` (an array of non-empty strings) and `extension_bindings` (an array of exact file bindings). Extensions may bind evidence but may not change required semantics. A semantic change requires a new reviewed schema version; it may not be smuggled through an unknown field or extension.

## 5. Completed phase seals

Each `completed_phase_seals` item has exactly:

- `identity`: non-empty unique phase-seal identity;
- `path`: repository-relative path that cannot escape the repository;
- `inner_sha256`: lowercase SHA-256 of the seal object's canonical bytes;
- `file_sha256`: lowercase SHA-256 of the complete seal-envelope file.

The bound file MUST exist, its file digest MUST match, its envelope MUST have exactly `schema_id`, `seal`, and `seal_sha256`, and its recomputed inner seal digest MUST equal both `seal_sha256` and `inner_sha256`. Across continuation, the prior completed-seal array MUST remain an identical prefix. Missing, malformed, unauthenticated, duplicated, removed, reordered, or replaced seals fail closed.

## 6. Counters

`execution_counters` contains exactly the following non-negative integers:

`automatic_retry_count`, `commissioning_execution_count`, `commissioning_pass_count`, `execution_replay_count`, `full_history_reconstruction_count`, `human_operational_act_claimed_count`, `human_operational_act_created_count`, `human_operational_act_invoked_count`, `human_operational_act_permanently_exhausted_count`, `human_operational_act_submitted_count`, `human_operational_act_terminally_bound_count`, `p11_entry_count`, `p11_operational_invocation_count`, `p12_entry_count`, `production_route_count`, `repair_and_continue_count`, `second_vm_count`, `vm_boot_count`, and `vm_creation_count`.

Case-specific counters live only in `case_counters`, which removes the DQ/DT core-counter naming collision. A future consumer MUST compare both counter objects with the authenticated prior manifest. No counter may decrease; `vm_boot_count` may not exceed `vm_creation_count`; `commissioning_pass_count` may not exceed `commissioning_execution_count`; and `p11_operational_invocation_count` may not exceed `p11_entry_count`.

All DU counters are zero.

## 7. Authority state

`authority_state` contains exactly `lifecycle_state`, `act_identity`, `owner_revision`, `authority_survives`, `transferable`, and `reusable`.

The lifecycle enum is `NOT_CREATED`, `AUTHORIZED_NOT_CREATED`, `AVAILABLE`, `CLAIMED`, `CONSUMED`, `RECONCILIATION_REQUIRED`, `REVOKED`, `SUPERSEDED`, `EXPIRED`, or `NO_AUTHORITY_SURVIVES`. `transferable` and `reusable` are always false. No-act states require null act identity, null owner revision, and false survival. Live authority states require an act identity, non-negative owner revision, and true survival. Terminal states require an act identity and revision but false survival.

The manifest reports authority lifecycle facts but never creates, grants, transfers, revives, or consumes authority. DU uses `NOT_CREATED` with no act identity or owner revision.

## 8. Lineage, implementation, and schema bindings

Each `lineage_bindings` item contains exactly `identity`, repository-relative `path`, file `sha256`, and committed `git_blob`. The consumer MUST require the path at `required_head`, compare the committed blob, compare current bytes with the committed blob, and compare file SHA-256. The minimum lineage is identity-unique and non-empty.

`producer_binding` and `consumer_binding` each contain exactly `identity`, `path`, and `sha256`. `schema_binding` additionally contains version `1.0.0` and the exact schema identity. These bindings make silent producer, consumer, or schema drift a validation failure.

## 9. Frontier and AUTO_CONTINUABLE

`frontier_state` contains exactly `constitutional_frontier`, `exact_next_legal_action`, `continuation_mode`, and `requires_human_review`. V1 requires `requires_human_review=true`. Allowed continuation modes are `PRE_MATERIALIZATION_VALIDATION_ONLY`, `SAME_LIVE_GENERATION_ONLY`, `FINALIZATION_ONLY`, and `HUMAN_REVIEW_ONLY`.

`AUTO_CONTINUABLE=false` means that a compatible checkpoint is reconstructive evidence only. It does not authorize materialization, VM creation, execution, replay, act creation, P11/P12 entry, E05, production routing, or a new generation. V1 deliberately has no true state. A future autonomous transition would require a separately authorized constitutional contract and cannot be inferred from compatibility.

## 10. Mandatory pre-materialization ordering

Every future SPCE harness using V1 MUST invoke this validator before overlay, seed, image, or VM creation:

`PRODUCER_OUTPUT -> CANONICAL_SCHEMA -> CONSUMER_REQUIRED_FIELDS -> SEMANTIC_COMPATIBILITY -> CONSTITUTIONAL_ADMISSIBILITY`

The materialization boundary may be reached only after all five stages pass and after separate Human authorization for that generation. The validator's PASS is necessary but never sufficient authority. Rejection must occur before materialization for a missing required field, wrong type, incompatible identity/version, unauthenticated completed seal, lineage difference, invalid authority semantics, counter regression, inconsistent AUTO_CONTINUABLE, unknown field, noncanonical serialization, or digest mismatch.

## 11. Historical dialect consolidation

Minimum authenticated lineage establishes two incompatible historical dialects:

- DQ's successful producer/consumer shape included `completed_phase_seals`, `authority_lifecycle_state`, and `minimum_lineage_identities_and_hashes`.
- DT's materialized producer shape included `completed_actions`, string `authority_state`, and `minimum_lineage`, but omitted `completed_phase_seals`; DT's inherited consumer still indexed that field directly.
- DP supplied successful persistent checkpoint/seal patterns but did not define another continuation-manifest dialect.

V1 reuses the completed-seal representation proven by DQ while replacing ambiguous strings and generation-specific counter vocabularies with structured, versioned, bound fields. Future producers and consumers use V1; historical DQ and DT evidence remains immutable and is not migrated in place.

## 12. CLREC assessment

The V1 contract is suitable as a candidate primitive for `CONSTITUTIONAL_LLM_RESUMABLE_EXECUTION_CHECKPOINT` because it binds schema, producer, consumer, lineage, seals, counters, authority state, frontier, and source revision without conversation history. DU supplies repository-side compatibility evidence only. Cross-account operational use remains untested here; CLREC empirical evidence is absent for V1 and CLREC is not constitutionally certified.

## 13. Reuse impact assessment

1. Katere obstoječe certificirane zmogljivosti se ponovno uporabijo? Ponovno se uporabijo DQ-jev preverjeni vzorec `completed_phase_seals`, DP/DQ-jevi trajni SPCE checkpointi in notranji/file SHA-256 pečati, DT-jeva minimalna čezračunska rekonstrukcija, Git blob/HEAD vezava ter fail-closed in G48 poročanje.
2. Katere nove zmogljivosti, če sploh, nastanejo? Nastane kandidatna repozitorijska zmožnost enotnega verzioniranega pogodbenega preverjanja proizvajalca in porabnika pred materializacijo. Ne nastane nova operativna ali avtoritetna zmožnost.
3. Ali katera obstoječa zmogljivost postane nedosegljiva? Ne. Zgodovinski DP/DQ/DT dokazi ostanejo berljivi in nespremenjeni; prihodnja uporaba starega nepreverjenega dialekta je namenoma fail-closed.
4. Ali implementacija ustvarja vzporedni tok? Ne. V1 je konsolidacijska pogodba za prihodnji SPCE/CLREC, ne vzporedni izvajalni ali nadaljevalni tok.
5. Ali zmanjšuje ali povečuje število produkcijskih poti? Ne ustvarja produkcijske poti in ohranja `PRODUCTION_ROUTE_COUNT=0`; pogodbeno zmanjšuje prihodnje sprejemljive manifestne dialekte na enega.

## 14. DU result and next frontier

Phases A through D are repository-evidence phases only. The canonical producer fixture passes all four gates. Ten incompatible mutations are rejected before materialization. The durable DU checkpoint binds the exact evidence set and zero counters.

Exact next constitutional frontier: Human review and optional commit of DU contract evidence, followed only by separately authorized future-generation work that integrates the V1 preflight before any materialization. No such operational generation is authorized by DU.

`AUTO_CONTINUABLE=false`.
