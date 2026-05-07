# SAPIANTA Trading Domain Future Roadmap

## Active Work

No Trading activation work is active.

Trading architectural memory finalization is appropriate as documentation-only state reconstruction.

## Near-Term Documentation Work

- preserve Trading state in architectural memory
- mark Trading as dormant and validation-oriented
- document partial implementations and stale areas
- document activation requirements
- document boundary preservation

## Future Work

- reconcile standalone `sapianta-domain-trading` package with `sapianta_system/runtime` trading surfaces
- make replay side-effect-free
- validate or retire stale scripts
- implement or explicitly defer empty data source/indicator/pipeline modules
- formalize paper-trading dry-run boundary
- formalize broker adapter boundary
- integrate audit viewer for trading envelopes
- define Trading activation ADR if future activation is desired

## Future Experimental Ideas

- paper-only trading replay UI
- deterministic strategy artifact viewer
- governance-bound ranking visualization
- simulation result lineage explorer
- policy-difference review for trading constraints

## Runtime Activation Delay

Runtime activation remains intentionally delayed because the repository shows useful deterministic foundations but not a complete operational safety model.

Trading should remain dormant until runtime-safe activation, broker isolation, approval semantics, and replay-clean execution boundaries exist.

## Proposed Milestone Category

Category: `research` or `governance`

Use `research` for domain investigation and state reconstruction.
Use `governance` only if the milestone updates master governance memory state or ADRs.
