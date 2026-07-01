# G8-00A Platform Runtime Adoption Readiness Review V1

Status: platform runtime adoption readiness reviewed.

Final verdict: PLATFORM_RUNTIME_READY_FOR_ACLI_NEXT

## 1. Executive Summary

This review evaluates whether AiGOL can begin replacing the current manual ChatGPT -> Codex -> Terminal -> Git copy/paste workflow with a Platform Core driven development workflow.

Certified baselines:

```text
GENERATION_6_ARCHITECTURE_CERTIFIED_AND_COMPLETE
GENERATION_7_CANONICALIZATION_CERTIFIED
GENERATION_8_RUNTIME_ADOPTION_PROGRAM_APPROVED
```

Conclusion:

AiGOL is ready to begin building ACLI Next as the canonical human entrypoint for Platform Core driven development.

This does not mean the current manual workflow can be fully eliminated immediately. It means the certified Platform Core is now sufficient to support a new primary runtime entrypoint that routes natural-language development through PGSP, UBTR, CSA, OCS, Governance, Replay, canonical evidence, and eventually Worker execution without redefining architecture.

The remaining work is implementation and integration, not architectural redesign.

## 2. Current Workflow Analysis

Current manual workflow:

```text
Human
-> ChatGPT
-> copy / paste
-> Codex
-> copy / paste
-> Terminal
-> Git
-> manual evidence collection
```

Target Platform Core workflow:

```text
Human
-> ACLI Next
-> PGSP
-> UBTR
-> CSA
-> OCS
-> Governance
-> Provider / Worker Services where authorized
-> Replay
-> UHCL review
-> Human confirmation
```

The certified Platform Core already contains the required ownership model, session protocol, translation path, canonicalization model, replay model, governance model, execution pipeline architecture, and canonical evidence schemas.

The gap is that the current operator experience still depends on external conversational composition, copy/paste, terminal command execution, and manual evidence collection.

## 3. Platform Core Readiness Matrix

| Component | Readiness | Basis | Runtime Adoption Gap |
| --- | --- | --- | --- |
| PGSP | Mostly Ready | Certified public API and adapter contract; G8 adoption program prioritizes projection lookup contract. | Needs ACLI Next invocation model and projection lookup contract. |
| UBTR | Mostly Ready | Canonical semantic translation authority is certified. | Needs canonical capability alias consumption from G7 records. |
| CSA | Mostly Ready | Canonical semantic representation is certified as UBTR-to-OCS handoff. | Needs development workflow intent records for ACLI Next sessions. |
| OCS | Mostly Ready | Orchestration and proposal ownership are certified. | Needs direct use of canonical evidence in live development proposals. |
| Governance | Ready | Certification and admissibility authority preserved through G6 and G7. | Needs runtime adoption review surfaces for ACLI Next evidence. |
| Replay | Ready | Replay remains reconstruction authority; G7 preserves replay fields and missing replay policy. | Needs ACLI Next runtime events to be replay-visible. |
| Worker Platform | Mostly Ready | G5 certified Worker handoff and PGSP Worker orchestration; G7 mapping model exists. | Needs bounded development Worker command classes and authorization linkage. |
| External Provider Platform | Mostly Ready | EPP architecture, provider identity, and read-only cognition path are certified. | Needs ACLI Next provider selection/usage contract through PGSP. |
| Canonical Platform Knowledge | Mostly Ready | G7 schemas and mappings certified. | Needs PGSP lookup contract and optional machine-readable pilot. |
| Canonical mappings | Ready as schema | G7-03 mapping and lineage canonicalization certified. | Needs populated records for key runtime surfaces. |
| Runtime registries | Partially Ready | Existing registries are reusable and must not be replaced. | Need canonical references and drift policy. |
| ACLI | Partially Ready | Existing ACLI proved live entrypoint and adapter boundary. | Historical CLI is not sufficient as primary Platform runtime interface. |
| CLI | Partially Ready | Useful for tooling and commands. | Should remain compatibility/tooling surface, not primary governed session UX. |
| Developer tooling | Partially Ready | Validation and conformance tooling exist. | Needs canonical evidence inspection and optional record validation. |

Overall readiness: ready to begin ACLI Next implementation.

## 4. Manual Workflow Elimination Assessment

| Manual Activity | Can Platform Core Eliminate Now? | Assessment |
| --- | --- | --- |
| Writing prompts | Partially | PGSP/UBTR can accept natural language, but ACLI Next needs conversation flow and context capture. |
| Copying prompts | Yes, with ACLI Next | A primary ACLI Next interface can route requests directly into PGSP. |
| Selecting providers | Partially | EPP and provider identity are certified; live selection policy and UX need integration. |
| Selecting Workers | Partially | Worker platform is certified; development Worker capability selection needs ACLI Next/PGSP wiring. |
| Invoking Codex | Not directly | Current Codex remains outside Platform Core; replacing this requires provider/Worker integration through certified services. |
| Executing terminal commands | Partially | Worker execution architecture exists; bounded command Worker classes and authorization flow need implementation. |
| Collecting evidence | Mostly | Replay and canonical evidence schemas exist; ACLI Next must capture runtime evidence automatically. |
| Creating commits | Not yet | Repository mutation and commit creation require authorized Worker execution and policy. |
| Replay recording | Mostly | Replay is certified; ACLI Next events and lookup results need replay integration. |

The copy/paste prompt loop can be targeted first. Terminal and Git elimination require later Worker and authorization implementation.

## 5. Remaining Manual Dependency Inventory

| Manual Dependency | Why It Still Exists | Missing Capability | Gap Type | Priority |
| --- | --- | --- | --- | --- |
| External prompt composition | No primary Platform-native conversation entrypoint yet. | ACLI Next conversation/session runtime over PGSP. | Implementation only | P0 |
| Copy/paste into Codex | Codex is currently used as external reasoning/execution helper. | Provider/Worker-backed development loop through PGSP. | Implementation only | P1 |
| Manual capability lookup | Canonical schemas exist but lookup contract is not implemented. | PGSP projection lookup contract and optional records. | Implementation only | P0 |
| Manual provider choice | EPP exists but operator-facing selection is not wired into ACLI Next. | PGSP/EPP provider selection and review contract. | Implementation only | P2 |
| Manual command execution | Worker platform exists but command classes are not exposed through ACLI Next. | Authorized bounded Worker command execution. | Implementation only | P2 |
| Manual evidence gathering | Replay exists but current workflow evidence is outside Platform runtime. | ACLI Next replay event capture. | Implementation only | P0 |
| Manual commit creation | Repository mutation and Git commit are not yet governed Worker capabilities. | Commit Worker class, authorization, replay, rollback policy. | Implementation only with policy certification | P3 |
| Manual validation selection | Tests are chosen by developer/Codex context. | OCS/Governance validation recommendation using canonical mappings. | Implementation only | P2 |
| Manual status reporting | Current summaries are composed externally. | UHCL rendering of PGSP session evidence. | Implementation only | P1 |

No listed dependency requires Platform Core redesign.

## 6. ACLI Evolution Analysis

Existing ACLI should not be treated as the long-term primary human interface.

Existing ACLI proved valuable because it established:

- live input capture;
- adapter boundary;
- terminal rendering;
- response capture;
- routing into PGSP lineage;
- replay-visible session evidence.

However, historical ACLI should remain a compatibility surface because it was introduced as an entrypoint over earlier advisory sessions, not as the full Platform Core operational development shell.

ACLI must never own:

- semantic interpretation;
- governance;
- replay;
- provider logic;
- Worker logic;
- approval;
- authorization;
- reusable communication.

Those boundaries remain correct for ACLI Next.

## 7. ACLI Next Feasibility Assessment

ACLI Next is feasible and should become the canonical human entrypoint for Platform Core driven development.

ACLI Next should be:

- a governed session interface over PGSP;
- a renderer for UHCL outputs;
- a capture surface for human requests, confirmations, and review decisions;
- a replay-visible source of session interaction events;
- a consumer of PGSP projection lookup results;
- compatible with existing ACLI command patterns where useful.

ACLI Next should not be:

- a translator;
- an orchestrator;
- a governance engine;
- a replay engine;
- a Worker runtime;
- a provider selector with authority;
- a Git automation layer outside Worker authorization;
- a replacement for CLI tooling.

Feasibility result: ready to begin ACLI Next implementation.

## 8. Migration Strategy

Migration should proceed incrementally:

1. Preserve existing ACLI commands as compatibility entrypoints.
2. Define ACLI Next command namespace and session contract.
3. Route ACLI Next requests through PGSP only.
4. Add PGSP projection lookup contract consumption.
5. Capture ACLI Next session events into Replay.
6. Render UHCL outputs without generating reusable explanations in ACLI Next.
7. Add provider cognition review only through certified EPP/PGSP paths.
8. Add bounded Worker execution only after authorization and replay requirements are satisfied.
9. Keep Git mutation and commit creation out of scope until Worker mutation policy is certified.

Compatibility requirements:

- existing `aigol` commands remain usable;
- existing replay artifacts remain reconstructable;
- existing PGSP public API remains canonical;
- existing ACLI behavior is not silently reinterpreted as ACLI Next.

## 9. Implementation Priorities

| Priority | Implementation Item | Purpose |
| --- | --- | --- |
| P0 | ACLI Next entrypoint contract | Define primary human session interface over PGSP. |
| P0 | PGSP projection lookup contract | Replace routine manual capability lookup with canonical evidence lookup. |
| P0 | ACLI Next replay event model | Ensure every interaction is replay-visible. |
| P1 | UHCL rendering contract for ACLI Next | Preserve reusable communication ownership. |
| P1 | OCS proposal display and confirmation loop | Move proposal review out of copy/paste workflow. |
| P2 | EPP provider cognition integration | Replace external model selection and prompt copy/paste with governed provider usage. |
| P2 | Bounded Worker command execution review | Begin terminal-command replacement through authorized Workers. |
| P3 | Git mutation and commit Worker certification | Replace manual Git only after mutation policy, authorization, replay, and rollback are certified. |
| P4 | Developer tooling canonical evidence inspection | Improve operator visibility without creating authority. |

## 10. Risks

| Risk | Mitigation |
| --- | --- |
| ACLI Next accidentally becomes semantic owner | Route all interpretation through UBTR. |
| ACLI Next becomes governance shortcut | Require Governance checkpoints and replay evidence. |
| Projection lookup becomes authority | Treat lookup as evidence only; Governance decides admissibility. |
| Worker execution bypasses authorization | Keep Worker execution out of ACLI Next until authorization handoff is certified. |
| Replay gaps appear in live sessions | Require ACLI Next event replay model before runtime execution expansion. |
| Historical CLI compatibility breaks | Preserve existing commands and make ACLI Next a new namespace or mode. |
| Manual discovery returns through habit | Use G7-04 fallback only for missing, stale, conflicting, partial, or uncertified records. |

## 11. Recommended Transition Roadmap

Recommended next milestones:

1. `G8_01_ACLI_NEXT_CANONICAL_HUMAN_ENTRYPOINT_CONTRACT_V1`
2. `G8_02_PGSP_PROJECTION_LOOKUP_CONTRACT_FOR_ACLI_NEXT_V1`
3. `G8_03_ACLI_NEXT_REPLAY_EVENT_MODEL_V1`
4. `G8_04_ACLI_NEXT_UHCL_RENDERING_AND_CONFIRMATION_CONTRACT_V1`
5. `G8_05_ACLI_NEXT_FIRST_NON_MUTATING_PLATFORM_DEVELOPMENT_SESSION_V1`
6. `G8_06_PROVIDER_COGNITION_ADOPTION_IN_ACLI_NEXT_REVIEW_V1`
7. `G8_07_BOUNDED_WORKER_COMMAND_ADOPTION_READINESS_REVIEW_V1`
8. `G8_08_GENERATION_8_RUNTIME_ADOPTION_CERTIFICATION_REVIEW_V1`

This roadmap starts with non-mutating, replay-visible Platform sessions before expanding toward provider and Worker execution.

## 12. Readiness Assessment

| Readiness Area | Assessment |
| --- | --- |
| Platform Core architecture | Ready |
| Canonical evidence model | Ready |
| PGSP session protocol | Ready for ACLI Next contract |
| Replay evidence model | Ready, with ACLI Next event model needed |
| Governance authority | Ready |
| Worker execution replacement of terminal | Not immediately ready; requires bounded Worker adoption |
| Git workflow replacement | Not ready; requires mutation and commit Worker certification |
| Copy/paste prompt replacement | Ready to begin through ACLI Next |
| Full copy/paste workflow elimination | Not yet complete |

The correct next phase is ACLI Next, not additional architecture review.

## 13. Final Determination

AiGOL is ready to begin replacing the current manual copy/paste development workflow with a Platform Core driven runtime centered around ACLI Next.

The certified Platform Core should be reused as the execution engine. ACLI Next should become the canonical human entrypoint, while preserving existing ACLI compatibility and all certified ownership boundaries.

## 14. Validation Evidence

Validation performed:

```text
git diff --check
```

Validation result: clean.

Final verdict: PLATFORM_RUNTIME_READY_FOR_ACLI_NEXT
