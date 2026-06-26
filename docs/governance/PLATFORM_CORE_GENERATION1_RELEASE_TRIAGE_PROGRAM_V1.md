# PLATFORM_CORE_GENERATION1_RELEASE_TRIAGE_PROGRAM_V1

Status: COMPLETE

Verdict:

```text
PLATFORM_CORE_GENERATION1_RELEASE_TRIAGE_PROGRAM_COMPLETE
```

Release-candidate posture:

```text
READY_WITH_LIMITATIONS
```

Recommended certification posture:

```text
HOLD_FORMAL_CERTIFICATION_PENDING_TRIAGE_BATCH_EXECUTION
```

## 1. Executive Summary

Platform Core Generation 1 remains under Feature Freeze.

This triage program classifies the full Release Candidate validation failure set without changing runtime code, tests, governance, replay, routing, lifecycle, PPP, translation, provider model, or Platform Core architecture.

Validation source:

```text
python -m pytest -q --tb=no -rf
```

Observed result:

```text
85 failed
5503 passed
2 skipped
duration: 119.82s
```

The failure set does not indicate a need for new architecture. It does indicate that formal certification cannot proceed until Platform Core blockers are repaired or formally reclassified, stale tests are updated, environment-bound tests are isolated, and non-core domain suites are separated from the Platform Core release-candidate gate.

## 2. Category Statistics

| Category | Count | Blocks Formal Certification | Required Action |
| --- | ---: | --- | --- |
| `RC_CORE_BLOCKER` | 7 | Yes | Audit and repair or explicitly reclassify. |
| `RC_CORE_REGRESSION` | 0 | No current direct classification | Keep available for future triage if a certified behavior regression is proven. |
| `STALE_TEST` | 9 | Blocks clean suite, not architecture | Replace broad lexical assertions with behavior assertions. |
| `DOMAIN_OUTSIDE_CERTIFIED_CORE` | 53 | No, if formally scoped out | Move to domain-specific certification or repair separately. |
| `EXTERNAL_DEPENDENCY` | 0 | Not currently used | Current external-looking failures are environment/sandbox-bound. |
| `SANDBOX_OR_ENVIRONMENT` | 10 | No, but blocks this local RC run | Provide certification-compatible test environment or local test overrides. |
| `READINESS_REPORT_DRIFT` | 6 | Yes for report-based certification evidence | Regenerate or update readiness/audit evidence after review. |
| `TEST_INFRASTRUCTURE` | 0 | No current direct classification | None. |
| `OTHER` | 0 | No | None. |

Total classified failures:

```text
85
```

## 3. Failure Inventory

Every failing test is assigned exactly one category.

| # | Test | Subsystem | Category | Suspected Root Cause | Certification Impact | Complexity | Recommended Next Action |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 1 | `tests/test_conversation_chain_continuity_runtime_v1.py::test_interactive_conversation_preserves_current_chain_across_turns` | ACLI conversation replay continuity | `RC_CORE_BLOCKER` | Second turn lacks expected `suggested_inspection_commands` evidence. | Blocks operator replay inspection confidence. | Medium | Audit chain artifact schema and restore/reclassify inspection evidence. |
| 2 | `tests/test_interactive_conversation_cli_v1.py::test_interactive_conversation_fails_closed_on_runtime_error` | ACLI fail-closed UX | `RC_CORE_BLOCKER` | Fail-closed output ordering changed; test sees `TURN COMPLETED` where fail-closed line was expected. | Blocks clean fail-closed operator evidence. | Low | Audit output contract; either restore ordering or update certified expectation. |
| 3 | `tests/test_lifecycle_gap_detection_runtime_v1.py::test_lifecycle_gap_detection_generates_gap_artifacts_for_failed_lifecycle_run` | Hardening lifecycle gap evidence | `RC_CORE_BLOCKER` | `FAIL_CLOSED_INTERRUPTION` category no longer emitted. | Blocks hardening evidence completeness. | Medium | Restore gap category or formally replace it with current equivalent. |
| 4 | `tests/test_multiline_prompt_support_runtime_v1.py::test_case_b_multiline_paste_creates_one_turn_without_fragmentation` | ACLI prompt intake | `RC_CORE_BLOCKER` | Current routing does not render expected deterministic completion output. | Blocks operator prompt-handling certification. | Medium | Audit multiline prompt output contract against current routing. |
| 5 | `tests/test_multiline_prompt_support_runtime_v1.py::test_multiline_reentry_does_not_consume_sentinel_as_second_turn` | ACLI prompt intake | `RC_CORE_BLOCKER` | Prompt state remains `WAITING_FOR_OPERATOR: CLARIFICATION` instead of completed state. | Blocks prompt lifecycle confidence. | Medium | Determine whether clarification is correct or stale expectation. |
| 6 | `tests/test_multiline_prompt_support_runtime_v1.py::test_single_line_prompt_still_creates_one_turn` | ACLI prompt intake | `RC_CORE_BLOCKER` | Single-line prompt routes into current HIRR path instead of monkeypatched response. | Blocks intake regression evidence. | Medium | Audit test seam and current intake contract. |
| 7 | `tests/test_native_development_task_intake_and_session_resume_v1.py::test_session_resume_allocates_next_unused_turn_without_router_collision` | Native development replay resume | `RC_CORE_BLOCKER` | Expected native-development replay artifact path is missing on resume. | Blocks resume/replay certification confidence. | Medium | Audit replay path movement versus missing persistence. |
| 8 | `tests/test_aigol_cli_foundation_v1.py::test_no_orchestration_introduced` | CLI lexical guard | `STALE_TEST` | Broad ban matches lifecycle command vocabulary such as `retry`. | Blocks suite only. | Low | Replace lexical ban with behavior-level orchestration assertion. |
| 9 | `tests/test_canonical_bridge_result_artifact_export_import.py::test_sidepanel_import_is_operator_selected_only_without_endpoint_or_listener` | Browser sidepanel lexical guard | `STALE_TEST` | Broad ban matches diagnostic `serviceworker` label. | Blocks suite only. | Low | Narrow assertion to actual endpoint/listener behavior. |
| 10 | `tests/test_chat_first_operator_flow.py::test_no_durable_persistence_or_endpoint_is_added` | Chat-first browser preview | `STALE_TEST` | Broad ban matches diagnostic `serviceworker` label. | Blocks suite only. | Low | Replace string ban with behavior-specific check. |
| 11 | `tests/test_chatgpt_ingress_native_import_preview_v1.py::test_no_native_messaging_call_is_wired_to_preview_button` | ChatGPT ingress preview | `STALE_TEST` | Preview path contains native messaging vocabulary in a prohibited context assertion. | Blocks suite only. | Low | Verify behavior; update test if no live native call occurs. |
| 12 | `tests/test_chatgpt_ingress_to_semantic_contract_preview_v1.py::test_preview_path_never_invokes_codex_provider` | ChatGPT semantic preview | `STALE_TEST` | Broad guard matches `codex_cli_provider` preview boundary text. | Blocks suite only. | Low | Assert provider invocation absence rather than vocabulary absence. |
| 13 | `tests/test_cli_controlled_execution_runtime_v1.py::test_no_retries_introduced` | CLI lexical guard | `STALE_TEST` | Broad ban matches lifecycle command `retry`. | Blocks suite only. | Low | Replace no-retry vocabulary assertion with no autonomous retry behavior assertion. |
| 14 | `tests/test_governed_browser_companion_runtime.py::test_no_retry_fallback_or_hidden_automation_surface_exists` | Browser companion lexical guard | `STALE_TEST` | Broad ban matches diagnostic `fallback` vocabulary. | Blocks suite only. | Low | Distinguish diagnostic fallback text from hidden automation behavior. |
| 15 | `tests/test_local_governed_transport_runtime_attachment.py::test_no_endpoint_provider_execution_or_orchestration_behavior_is_added` | Local governed transport lexical guard | `STALE_TEST` | Broad vocabulary guard catches non-executing attachment/runtime labels. | Blocks suite only. | Low | Replace lexical guard with actual transport/execution boundary checks. |
| 16 | `tests/test_persistent_replay_session.py::test_replay_session_is_bounded_in_memory_and_append_only` | Replay session JS assertion | `STALE_TEST` | Broad `.pop(` ban matches non-mutating string parsing usage. | Blocks suite only. | Low | Assert replay array append-only behavior directly. |
| 17 | `tests/test_conversation_native_development_intent_routing_v1.py::test_interactive_conversation_routes_acceptance_prompts_without_provider_entry_failure` | Provider onboarding workflow | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | `PROVIDER_ONBOARDING_DOMAIN` is unsupported by current conversational lifecycle. | Does not block Platform Core if provider onboarding is scoped out. | Medium | Move to provider-onboarding certification or implement in later domain track. |
| 18 | `tests/test_conversation_to_ppp_handoff_execution_v1.py::test_interactive_conversation_routes_acceptance_scenarios_to_terminal_states` | Provider onboarding / PPP acceptance | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | Acceptance scenarios include unsupported provider-onboarding domain. | Does not block Platform Core if scoped out. | Medium | Separate provider-onboarding acceptance from Platform Core RC gate. |
| 19 | `tests/test_governed_intent_transfer_ingestion.py::test_local_runtime_ingestion_route_returns_preview_ready_response` | Local preview transport | `SANDBOX_OR_ENVIRONMENT` | Local socket/server creation is blocked by execution environment. | Does not prove runtime defect. | Low | Run in environment permitting localhost or mark with environment requirement. |
| 20 | `tests/test_governed_local_preview_runtime.py::test_real_localhost_post_invocation` | Local preview transport | `SANDBOX_OR_ENVIRONMENT` | Localhost POST server cannot start under current sandbox. | Does not prove runtime defect. | Low | Run in certification environment with local socket permission. |
| 21 | `tests/test_governed_provider_activation_v1.py::test_provider_activation_success` | Provider credential vault | `SANDBOX_OR_ENVIRONMENT` | Credential vault write targets read-only home config path. | Does not prove provider authority defect. | Low | Use test-local credential vault path in certification environment. |
| 22 | `tests/test_governed_provider_activation_v1.py::test_missing_api_key_blocked` | Provider credential vault | `SANDBOX_OR_ENVIRONMENT` | Credential vault setup fails before missing-key behavior can be asserted. | Does not prove governance defect. | Low | Provide writable vault fixture or environment override. |
| 23 | `tests/test_governed_provider_activation_v1.py::test_replay_visible_invocation_persistence` | Provider replay | `SANDBOX_OR_ENVIRONMENT` | Read-only vault prevents provider invocation setup. | Blocks local evidence, not architecture. | Low | Rerun with writable test vault. |
| 24 | `tests/test_governed_provider_activation_v1.py::test_deterministic_replay_hashing` | Provider replay hashing | `SANDBOX_OR_ENVIRONMENT` | Read-only vault prevents setup. | Blocks local evidence, not architecture. | Low | Rerun with writable test vault. |
| 25 | `tests/test_governed_provider_activation_v1.py::test_provider_response_persistence` | Provider response persistence | `SANDBOX_OR_ENVIRONMENT` | Read-only vault prevents setup. | Blocks local evidence, not architecture. | Low | Rerun with writable test vault. |
| 26 | `tests/test_governed_provider_activation_v1.py::test_provider_cannot_bypass_runtime_authority` | Provider authority boundary | `SANDBOX_OR_ENVIRONMENT` | Read-only vault prevents setup. | Needs environment rerun to certify provider boundary. | Low | Rerun with writable test vault. |
| 27 | `tests/test_governed_provider_activation_v1.py::test_provider_cannot_trigger_execution` | Provider execution boundary | `SANDBOX_OR_ENVIRONMENT` | Read-only vault prevents setup. | Needs environment rerun to certify provider boundary. | Low | Rerun with writable test vault. |
| 28 | `tests/test_governed_provider_activation_v1.py::test_provider_invocation_replay_reconstruction` | Provider replay reconstruction | `SANDBOX_OR_ENVIRONMENT` | Read-only vault prevents setup. | Needs environment rerun to certify provider replay. | Low | Rerun with writable test vault. |
| 29 | `tests/test_freeform_human_prompt_acceptance_v1.py::test_freeform_acceptance_report_matches_current_acli_behavior` | Freeform acceptance report | `READINESS_REPORT_DRIFT` | Recorded acceptance report counts no longer match current ACLI behavior. | Blocks report-based certification evidence. | Low | Regenerate report after routing review. |
| 30 | `tests/test_freeform_human_prompt_acceptance_v1.py::test_freeform_failures_preserve_governance_safety_boundaries` | Freeform acceptance safety report | `READINESS_REPORT_DRIFT` | Current report includes `INTAKE_NOT_APPLICABLE` where previous expectations differed. | Blocks acceptance-report evidence. | Low | Audit report semantics and update expected evidence if correct. |
| 31 | `tests/test_provider_acli_connectivity_audit_v1.py::test_provider_acli_connectivity_audit_finds_expected_gaps` | Provider ACLI connectivity audit | `READINESS_REPORT_DRIFT` | Audit expected gaps no longer match implementation/evidence. | Blocks provider readiness reporting, not core architecture. | Low | Regenerate audit after provider path classification. |
| 32 | `tests/test_provider_credential_vault_onboarding_certification_v1.py::test_provider_credential_vault_onboarding_certification_detects_fallback_dependency` | Provider credential certification report | `READINESS_REPORT_DRIFT` | Certification report expectation drift after provider/vault changes. | Blocks provider onboarding evidence. | Low | Update report after environment-correct provider run. |
| 33 | `tests/test_system_readiness_certification_v1.py::test_system_readiness_certification_produces_expected_packages` | System readiness report | `READINESS_REPORT_DRIFT` | Generated readiness package content no longer matches expected package set. | Blocks formal readiness evidence. | Medium | Regenerate package or repair missing output after audit. |
| 34 | `tests/test_system_readiness_certification_v1.py::test_system_readiness_certifies_major_architectural_chains` | System readiness report | `READINESS_REPORT_DRIFT` | Major-chain certification assertions drifted from current implementation/evidence. | Blocks formal readiness evidence. | Medium | Audit readiness chain list and update evidence. |
| 35 | `sapianta-domain-trading/tests/test_architecture_evolution_constitution.py::test_constitutional_engine_is_read_only` | Trading domain governance | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | Domain-specific artifact/freeze expectations outside Platform Core scope. | Does not block Platform Core if scoped out. | High | Move to trading-domain certification track. |
| 36 | `sapianta-domain-trading/tests/test_architecture_evolution_constitution.py::test_constitution_manifest_and_artifacts_exist` | Trading domain governance | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | Missing or mismatched trading-domain manifest/artifacts. | Does not block Platform Core if scoped out. | High | Repair trading-domain manifests separately. |
| 37 | `sapianta-domain-trading/tests/test_architecture_freeze_manifest.py::test_frozen_semantics_are_explicit` | Trading domain freeze manifest | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | Trading freeze document/manifest mismatch. | Does not block Platform Core if scoped out. | High | Domain-specific freeze remediation. |
| 38 | `sapianta-domain-trading/tests/test_architecture_freeze_manifest.py::test_replay_topology_remains_immutable` | Trading domain freeze manifest | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | Trading replay topology evidence mismatch. | Does not block Platform Core if scoped out. | High | Domain-specific replay topology review. |
| 39 | `sapianta-domain-trading/tests/test_architecture_freeze_manifest.py::test_invariant_topology_is_traceable` | Trading domain freeze manifest | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | Trading invariant traceability evidence mismatch. | Does not block Platform Core if scoped out. | High | Domain-specific manifest repair. |
| 40 | `sapianta-domain-trading/tests/test_architecture_freeze_manifest.py::test_mutation_boundaries_remain_enforced` | Trading domain freeze manifest | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | Trading mutation-boundary evidence mismatch. | Does not block Platform Core if scoped out. | High | Domain-specific boundary review. |
| 41 | `sapianta-domain-trading/tests/test_architecture_freeze_manifest.py::test_governance_freeze_manifest_is_deterministic` | Trading domain freeze manifest | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | Trading deterministic manifest mismatch. | Does not block Platform Core if scoped out. | High | Regenerate or repair trading manifest. |
| 42 | `sapianta-domain-trading/tests/test_architecture_freeze_manifest.py::test_semantic_kernel_remains_protected` | Trading domain freeze manifest | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | Trading semantic-kernel protection assertion outside core scope. | Does not block Platform Core if scoped out. | High | Domain-specific certification. |
| 43 | `sapianta-domain-trading/tests/test_architecture_freeze_manifest.py::test_codex_alignment_terminology_remains_explicit` | Trading domain freeze manifest | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | Trading Codex terminology evidence mismatch. | Does not block Platform Core if scoped out. | Medium | Domain-specific doc/evidence update. |
| 44 | `sapianta-domain-trading/tests/test_architecture_freeze_manifest.py::test_no_experimental_zone_leaks_into_frozen_governance` | Trading domain freeze manifest | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | Trading experimental-zone assertion outside core scope. | Does not block Platform Core if scoped out. | High | Domain-specific audit. |
| 45 | `sapianta-domain-trading/tests/test_architecture_freeze_manifest.py::test_required_architecture_artifacts_exist` | Trading domain freeze manifest | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | Missing trading architecture artifacts. | Does not block Platform Core if scoped out. | High | Create/repair domain artifacts in separate track. |
| 46 | `sapianta-domain-trading/tests/test_architecture_freeze_manifest.py::test_system_identity_and_expansion_boundaries_are_explicit` | Trading domain freeze manifest | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | Trading identity/boundary evidence mismatch. | Does not block Platform Core if scoped out. | Medium | Domain-specific evidence update. |
| 47 | `sapianta-domain-trading/tests/test_architecture_promotion_gates.py::test_promotion_gates_remain_read_only_and_manifest_stable` | Trading promotion gates | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | Trading promotion manifest stability failure. | Does not block Platform Core if scoped out. | High | Domain-specific promotion-gate repair. |
| 48 | `sapianta-domain-trading/tests/test_architecture_promotion_gates.py::test_promotion_manifest_and_artifacts_exist` | Trading promotion gates | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | Missing trading promotion manifest/artifacts. | Does not block Platform Core if scoped out. | High | Domain-specific artifact repair. |
| 49 | `sapianta-domain-trading/tests/test_architecture_review_checkpoint.py::test_semantic_consistency_review_passes` | Trading review checkpoint | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | Trading semantic consistency checkpoint fails. | Does not block Platform Core if scoped out. | High | Domain-specific checkpoint remediation. |
| 50 | `sapianta-domain-trading/tests/test_architecture_review_checkpoint.py::test_replay_topology_audit_passes_and_is_side_effect_free` | Trading review checkpoint | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | Trading replay topology checkpoint fails. | Does not block Platform Core if scoped out. | High | Domain-specific replay audit. |
| 51 | `sapianta-domain-trading/tests/test_architecture_review_checkpoint.py::test_invariant_topology_review_has_no_contradictions` | Trading review checkpoint | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | Trading invariant topology checkpoint fails. | Does not block Platform Core if scoped out. | High | Domain-specific invariant audit. |
| 52 | `sapianta-domain-trading/tests/test_architecture_review_checkpoint.py::test_trust_boundaries_and_mutation_boundaries_remain_isolated` | Trading review checkpoint | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | Trading boundary checkpoint fails. | Does not block Platform Core if scoped out. | High | Domain-specific boundary audit. |
| 53 | `sapianta-domain-trading/tests/test_architecture_review_checkpoint.py::test_governance_dependencies_are_acyclic` | Trading review checkpoint | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | Trading dependency checkpoint fails. | Does not block Platform Core if scoped out. | High | Domain-specific dependency audit. |
| 54 | `sapianta-domain-trading/tests/test_architecture_review_checkpoint.py::test_codex_vocabulary_remains_deterministic` | Trading review checkpoint | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | Trading vocabulary checkpoint fails. | Does not block Platform Core if scoped out. | Medium | Domain-specific terminology repair. |
| 55 | `sapianta-domain-trading/tests/test_architecture_review_checkpoint.py::test_no_experimental_leakage_exists` | Trading review checkpoint | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | Trading experimental leakage checkpoint fails. | Does not block Platform Core if scoped out. | High | Domain-specific audit. |
| 56 | `sapianta-domain-trading/tests/test_architecture_review_checkpoint.py::test_architectural_drift_detection_catches_trust_boundary_leakage` | Trading review checkpoint | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | Trading drift-detection checkpoint fails. | Does not block Platform Core if scoped out. | Medium | Domain-specific drift test review. |
| 57 | `sapianta-domain-trading/tests/test_architecture_review_checkpoint.py::test_review_process_remains_read_only_and_deterministic` | Trading review checkpoint | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | Trading review-process checkpoint fails. | Does not block Platform Core if scoped out. | High | Domain-specific review repair. |
| 58 | `sapianta-domain-trading/tests/test_architecture_review_checkpoint.py::test_required_review_outputs_exist` | Trading review checkpoint | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | Missing trading review outputs. | Does not block Platform Core if scoped out. | High | Domain-specific output generation. |
| 59 | `sapianta-domain-trading/tests/test_architecture_review_checkpoint.py::test_checkpoint_json_matches_pass_statuses` | Trading review checkpoint | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | Trading checkpoint JSON status mismatch. | Does not block Platform Core if scoped out. | Medium | Domain-specific checkpoint regeneration. |
| 60 | `sapianta-domain-trading/tests/test_domain_lock_policy.py::test_codex_visible_classifications_remain_stable` | Trading domain lock | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | Trading domain classification evidence mismatch. | Does not block Platform Core if scoped out. | Medium | Domain-specific lock policy update. |
| 61 | `sapianta-domain-trading/tests/test_domain_lock_policy.py::test_domain_lock_policy_artifacts_exist` | Trading domain lock | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | Missing trading domain-lock artifacts. | Does not block Platform Core if scoped out. | High | Domain-specific artifact repair. |
| 62 | `sapianta-domain-trading/tests/test_execution_envelope_model.py::test_manifest_matches_live_document_and_artifacts_exist` | Trading execution envelope | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | Trading execution-envelope manifest mismatch. | Does not block Platform Core if scoped out. | High | Domain-specific manifest regeneration. |
| 63 | `sapianta-domain-trading/tests/test_finalize_domain_governance_foundation.py::test_final_manifest_exists_and_is_deterministic_json` | Trading governance finalization | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | Missing deterministic trading final manifest. | Does not block Platform Core if scoped out. | High | Domain-specific finalization repair. |
| 64 | `sapianta-domain-trading/tests/test_finalize_domain_governance_foundation.py::test_semantic_freeze_consistency` | Trading governance finalization | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | Trading semantic-freeze consistency mismatch. | Does not block Platform Core if scoped out. | High | Domain-specific freeze review. |
| 65 | `sapianta-domain-trading/tests/test_finalize_domain_governance_foundation.py::test_trusted_scope_finalization_is_deterministic` | Trading governance finalization | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | Trading trusted-scope finalization mismatch. | Does not block Platform Core if scoped out. | High | Domain-specific finalization repair. |
| 66 | `sapianta-domain-trading/tests/test_finalize_domain_governance_foundation.py::test_escalation_semantics_are_finalized_and_deterministic` | Trading governance finalization | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | Trading escalation-semantics finalization mismatch. | Does not block Platform Core if scoped out. | High | Domain-specific finalization repair. |
| 67 | `sapianta-domain-trading/tests/test_finalize_domain_governance_foundation.py::test_codex_semantic_continuity_is_stable` | Trading governance finalization | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | Trading Codex semantic-continuity evidence mismatch. | Does not block Platform Core if scoped out. | Medium | Domain-specific evidence update. |
| 68 | `sapianta-domain-trading/tests/test_finalize_domain_governance_foundation.py::test_finalization_artifacts_exist` | Trading governance finalization | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | Missing trading finalization artifacts. | Does not block Platform Core if scoped out. | High | Domain-specific artifact generation. |
| 69 | `sapianta-domain-trading/tests/test_finalize_domain_governance_foundation.py::test_no_capability_expansion_was_introduced_by_finalization` | Trading governance finalization | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | Trading finalization capability assertion fails. | Does not block Platform Core if scoped out. | High | Domain-specific governance audit. |
| 70 | `sapianta-domain-trading/tests/test_finalize_governed_execution_semantics.py::test_semantic_freeze_is_explicit` | Trading governed execution finalization | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | Trading governed-execution semantic freeze mismatch. | Does not block Platform Core if scoped out. | High | Domain-specific finalization repair. |
| 71 | `sapianta-domain-trading/tests/test_finalize_governed_execution_semantics.py::test_governance_topology_is_locked` | Trading governed execution finalization | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | Trading governance topology lock mismatch. | Does not block Platform Core if scoped out. | High | Domain-specific topology repair. |
| 72 | `sapianta-domain-trading/tests/test_finalize_governed_execution_semantics.py::test_replay_semantics_are_finalized` | Trading governed execution finalization | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | Trading replay finalization mismatch. | Does not block Platform Core if scoped out. | High | Domain-specific replay repair. |
| 73 | `sapianta-domain-trading/tests/test_finalize_governed_execution_semantics.py::test_invariant_topology_is_finalized` | Trading governed execution finalization | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | Trading invariant topology finalization mismatch. | Does not block Platform Core if scoped out. | High | Domain-specific invariant repair. |
| 74 | `sapianta-domain-trading/tests/test_finalize_governed_execution_semantics.py::test_trust_boundaries_are_finalized` | Trading governed execution finalization | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | Trading trust boundary finalization mismatch. | Does not block Platform Core if scoped out. | High | Domain-specific boundary repair. |
| 75 | `sapianta-domain-trading/tests/test_finalize_governed_execution_semantics.py::test_residual_risks_are_consolidated_and_visible` | Trading governed execution finalization | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | Trading residual-risk finalization mismatch. | Does not block Platform Core if scoped out. | Medium | Domain-specific risk evidence update. |
| 76 | `sapianta-domain-trading/tests/test_finalize_governed_execution_semantics.py::test_expansion_readiness_is_classified` | Trading governed execution finalization | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | Trading expansion-readiness classification mismatch. | Does not block Platform Core if scoped out. | Medium | Domain-specific readiness update. |
| 77 | `sapianta-domain-trading/tests/test_finalize_governed_execution_semantics.py::test_governance_stabilization_review_passes` | Trading governed execution finalization | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | Trading stabilization review fails. | Does not block Platform Core if scoped out. | High | Domain-specific stabilization repair. |
| 78 | `sapianta-domain-trading/tests/test_finalize_governed_execution_semantics.py::test_codex_semantic_stabilization_exists` | Trading governed execution finalization | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | Trading Codex semantic-stabilization artifact missing/mismatched. | Does not block Platform Core if scoped out. | Medium | Domain-specific artifact repair. |
| 79 | `sapianta-domain-trading/tests/test_finalize_governed_execution_semantics.py::test_no_capability_expansion_or_production_execution_exists` | Trading governed execution finalization | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | Trading capability/production execution assertion fails. | Does not block Platform Core if scoped out. | High | Domain-specific governance audit. |
| 80 | `sapianta-domain-trading/tests/test_finalize_governed_execution_semantics.py::test_finalization_artifacts_exist` | Trading governed execution finalization | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | Missing trading governed-execution finalization artifacts. | Does not block Platform Core if scoped out. | High | Domain-specific artifact generation. |
| 81 | `sapianta-domain-trading/tests/test_finalize_governed_execution_semantics.py::test_final_manifest_is_deterministic` | Trading governed execution finalization | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | Trading final manifest mismatch or missing deterministic manifest. | Does not block Platform Core if scoped out. | High | Domain-specific manifest repair. |
| 82 | `sapianta-domain-trading/tests/test_governance_adversarial_suite.py::test_manifest_matches_live_document_and_artifacts_exist` | Trading adversarial governance | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | Trading adversarial suite manifest mismatch. | Does not block Platform Core if scoped out. | High | Domain-specific manifest repair. |
| 83 | `sapianta-domain-trading/tests/test_governance_capability_review.py::test_manifest_matches_live_document_and_artifacts_exist` | Trading capability review | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | Trading capability review manifest mismatch. | Does not block Platform Core if scoped out. | High | Domain-specific manifest repair. |
| 84 | `sapianta-domain-trading/tests/test_governed_execution_proposal_pipeline.py::test_manifest_matches_live_document_and_artifacts_exist` | Trading governed execution proposal pipeline | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | Trading proposal pipeline manifest mismatch. | Does not block Platform Core if scoped out. | High | Domain-specific manifest repair. |
| 85 | `sapianta-domain-trading/tests/test_runtime_foundation_freeze.py::test_manifest_matches_live_document_and_artifacts_exist` | Trading runtime foundation freeze | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | Trading runtime foundation manifest mismatch. | Does not block Platform Core if scoped out. | High | Domain-specific manifest repair. |

## 4. Representative Failures By Category

### RC_CORE_BLOCKER

Representative failures:

- Conversation chain continuity missing expected inspection evidence.
- Multiline prompt tests no longer match current operator-visible lifecycle.
- Native development session resume misses expected replay artifact path.
- Lifecycle gap detection no longer emits `FAIL_CLOSED_INTERRUPTION`.

Certification impact:

```text
BLOCKS_FORMAL_CERTIFICATION
```

Required action:

```text
REQUIRES_AUDIT_BEFORE_REPAIR
REQUIRES_IMPLEMENTATION_REPAIR_OR_FORMAL_RECLASSIFICATION
```

### STALE_TEST

Representative failures:

- Lexical tests reject `retry`, `fallback`, `serviceworker`, `codex_cli_provider`, or `.pop(` even when the matched usage is diagnostic, operator-facing, or behaviorally safe.

Certification impact:

```text
DOES_NOT_BLOCK_ARCHITECTURE
BLOCKS_CLEAN_RELEASE_CANDIDATE_SUITE
```

Required action:

```text
REQUIRES_TEST_UPDATE
```

### DOMAIN_OUTSIDE_CERTIFIED_CORE

Representative failures:

- `PROVIDER_ONBOARDING_DOMAIN` conversational selection is unsupported.
- `sapianta-domain-trading` governance, freeze, checkpoint, finalization, and manifest suites fail.

Certification impact:

```text
DOES_NOT_BLOCK_PLATFORM_CORE_IF_FORMALLY_SCOPED_OUT
```

Required action:

```text
REQUIRES_SCOPE_DECISION
REQUIRES_DOMAIN_SPECIFIC_CERTIFICATION_TRACK
```

### SANDBOX_OR_ENVIRONMENT

Representative failures:

- Localhost preview tests cannot bind or post under the current environment.
- Provider activation tests cannot write the credential vault under `/home/pisarna/.config/aigol`.

Certification impact:

```text
DOES_NOT_PROVE_PLATFORM_CORE_DEFECT
BLOCKS_THIS_LOCAL_RC_RUN
```

Required action:

```text
REQUIRES_ENVIRONMENT_CORRECTION
```

### READINESS_REPORT_DRIFT

Representative failures:

- Freeform acceptance report no longer matches current ACLI behavior.
- Provider connectivity and system readiness reports no longer match generated evidence.

Certification impact:

```text
BLOCKS_FORMAL_CERTIFICATION_EVIDENCE
```

Required action:

```text
REQUIRES_AUDIT_BEFORE_REPORT_UPDATE
```

## 5. Certification Impact Assessment

Platform Core Generation 1 should not proceed to formal certification directly from this RC run.

Blocking reasons:

1. The `RC_CORE_BLOCKER` set contains prompt intake, replay continuity, fail-closed evidence, and hardening gap classification failures.

2. The `READINESS_REPORT_DRIFT` set prevents certification from relying on the current readiness/audit packages as final evidence.

3. The repository-wide suite includes domain-trading certification failures outside Platform Core scope; formal certification requires either domain repair or governed scope exclusion.

4. Environment-bound provider and local transport failures must be rerun under a certification-compatible environment before provider/transport evidence is accepted.

Non-blocking with formal scope decision:

1. `STALE_TEST` lexical guard failures do not prove runtime defects.

2. `DOMAIN_OUTSIDE_CERTIFIED_CORE` failures do not block Platform Core if excluded from Platform Core Generation 1 certification scope.

3. `SANDBOX_OR_ENVIRONMENT` failures do not prove defects but require a clean certification environment.

## 6. Recommended Repair Order

1. `RC_BATCH_01_CORE_BLOCKERS`

   Repair or formally reclassify the seven Platform Core blockers.

2. `RC_BATCH_02_READINESS_REPORT_DRIFT`

   Regenerate readiness and freeform acceptance evidence after blocker triage.

3. `RC_BATCH_03_STALE_TESTS`

   Convert lexical guard tests into behavior assertions.

4. `RC_BATCH_04_ENVIRONMENT`

   Provide writable provider credential fixtures and socket-capable certification environment.

5. `RC_BATCH_05_SCOPE_AND_DOMAIN`

   Formally exclude or separately certify provider-onboarding and trading-domain suites.

## 7. Recommended Work Packages

### RC_BATCH_01_CORE_BLOCKERS

Included failures:

- Tests 1 through 7 in the failure inventory.

Rationale:

These failures touch certified Platform Core operator continuity, prompt intake, session replay, fail-closed evidence, and hardening gap classification.

Estimated implementation scope:

```text
MEDIUM
```

Regression requirements:

- Conversation chain continuity.
- Multiline prompt single-turn handling.
- Session resume replay location.
- Fail-closed CLI output contract.
- Lifecycle gap evidence categories.

### RC_BATCH_02_READINESS_REPORT_DRIFT

Included failures:

- Tests 29 through 34 in the failure inventory.

Rationale:

Formal certification requires readiness reports and audit packages to match current implementation evidence.

Estimated implementation scope:

```text
LOW_TO_MEDIUM
```

Regression requirements:

- Freeform acceptance report regeneration.
- Provider ACLI connectivity audit package.
- Provider credential onboarding certification package.
- System readiness package generation.

### RC_BATCH_03_STALE_TESTS

Included failures:

- Tests 8 through 16 in the failure inventory.

Rationale:

Broad lexical guards now catch safe diagnostic or operator-visible language. The tests should verify forbidden behavior rather than forbidden words.

Estimated implementation scope:

```text
LOW
```

Regression requirements:

- No autonomous orchestration behavior.
- No hidden browser endpoints/listeners.
- No provider invocation from preview paths.
- Replay remains append-only.

### RC_BATCH_04_ENVIRONMENT

Included failures:

- Tests 19 through 28 in the failure inventory.

Rationale:

The current sandbox blocks localhost socket tests and provider credential vault writes. These must be rerun in a certification-compatible environment or adjusted to use test-local fixtures.

Estimated implementation scope:

```text
LOW
```

Regression requirements:

- Provider credential vault uses writable test fixture.
- Local preview transport tests declare and verify environment capability.
- Provider authority and replay boundary tests rerun successfully.

### RC_BATCH_05_SCOPE_AND_DOMAIN

Included failures:

- Tests 17 and 18.
- Tests 35 through 85.

Rationale:

Provider onboarding and trading-domain governance failures are outside the current certified Platform Core path unless governance explicitly expands the certification scope.

Estimated implementation scope:

```text
MEDIUM_TO_HIGH
```

Regression requirements:

- Formal Platform Core scope manifest.
- Provider onboarding track, if included.
- Trading-domain certification track, if included.
- Repository-wide suite grouping that distinguishes Platform Core from domain-specific certification.

## 8. Certification Review By Category

| Category | Blocks Formal Certification | Requires Audit Before Repair | Requires Implementation Repair | Requires Documentation Update | Requires Environment Correction |
| --- | --- | --- | --- | --- | --- |
| `RC_CORE_BLOCKER` | Yes | Yes | Likely | Possibly | No |
| `RC_CORE_REGRESSION` | Not currently present | N/A | N/A | N/A | N/A |
| `STALE_TEST` | Blocks clean suite only | Yes | No runtime repair | Test update only | No |
| `DOMAIN_OUTSIDE_CERTIFIED_CORE` | No if scoped out | Yes | Only in domain track | Scope documentation | No |
| `EXTERNAL_DEPENDENCY` | Not currently present | N/A | N/A | N/A | N/A |
| `SANDBOX_OR_ENVIRONMENT` | No | No | No runtime repair | Possibly test notes | Yes |
| `READINESS_REPORT_DRIFT` | Yes for evidence | Yes | Possibly | Yes | No |
| `TEST_INFRASTRUCTURE` | Not currently present | N/A | N/A | N/A | N/A |
| `OTHER` | Not currently present | N/A | N/A | N/A | N/A |

## 9. Release Candidate Implementation Sequence

Recommended sequence:

```text
RC_BATCH_01_CORE_BLOCKERS
-> RC_BATCH_02_READINESS_REPORT_DRIFT
-> RC_BATCH_03_STALE_TESTS
-> RC_BATCH_04_ENVIRONMENT
-> RC_BATCH_05_SCOPE_AND_DOMAIN
-> rerun Platform Core RC suite
-> rerun repository-wide suite with formal scope labels
-> formal certification review
```

This sequence preserves Feature Freeze because it starts with existing behavior and evidence defects, then resolves stale assertions and environment setup, and only then addresses out-of-scope domain work.

## 10. Final Determination

The Release Candidate failure set is completely classified, prioritized, and grouped into deterministic repair batches.

Platform Core Generation 1 remains:

```text
READY_WITH_LIMITATIONS
```

It should not yet be promoted to formal certification until `RC_BATCH_01_CORE_BLOCKERS` and `RC_BATCH_02_READINESS_REPORT_DRIFT` are closed or formally reclassified, and the environment/domain scope questions are resolved.

Final verdict:

```text
PLATFORM_CORE_GENERATION1_RELEASE_TRIAGE_PROGRAM_COMPLETE
```
