# RC_CERTIFICATION_BLOCKER_IDENTIFICATION_V1

Status: COMPLETE

Final verdict:

```text
RC_CERTIFICATION_BLOCKER_IDENTIFICATION_COMPLETE
```

## 1. Executive Summary

This artifact answers the certification question:

```text
How many of the current 85 failing tests actually prevent formal Platform Core Generation 1 certification?
```

Answer:

```text
13 certification blockers
72 non-blocking failures
```

The 13 blockers are:

- 7 `RC_CORE_BLOCKER` failures affecting Platform Core runtime behavior or evidence;
- 6 `READINESS_REPORT_DRIFT` failures affecting formal certification evidence packages.

The remaining 72 failures do not block Platform Core Generation 1 certification under the current certification scope because they are stale lexical tests, environment/sandbox limitations, or domain/provider-onboarding/trading-domain failures outside the certified core.

This is a certification analysis artifact only. It does not implement repairs, modify runtime code, modify tests, modify governance, modify replay, modify routing, modify lifecycle, modify PPP, or modify the provider pipeline.

## 2. Certification Scope

Platform Core Generation 1 certification scope includes:

- Universal ACLI operator lifecycle;
- HIRR-facing prompt intake and clarification behavior;
- workflow identity preservation;
- replay lineage and replay-visible evidence;
- fail-closed operator behavior;
- lifecycle and hardening evidence;
- readiness/certification evidence packages required to support formal certification.

Platform Core Generation 1 certification scope excludes:

- trading-domain certification suites;
- provider-onboarding domain completion unless separately included;
- browser companion lexical guard refinements that do not prove runtime behavior defects;
- local socket availability in this sandbox;
- provider credential vault writes to an unavailable local home directory;
- broad repository-wide domain artifacts outside Platform Core Generation 1.

## 3. Summary Statistics

| Metric | Count |
| --- | ---: |
| Total RC failures | 85 |
| Certification blockers | 13 |
| Non-blocking failures | 72 |

Category breakdown:

| Category | Total | Blockers | Non-Blockers |
| --- | ---: | ---: | ---: |
| `RC_CORE_BLOCKER` | 7 | 7 | 0 |
| `RC_CORE_REGRESSION` | 0 | 0 | 0 |
| `STALE_TEST` | 9 | 0 | 9 |
| `DOMAIN_OUTSIDE_CERTIFIED_CORE` | 53 | 0 | 53 |
| `EXTERNAL_DEPENDENCY` | 0 | 0 | 0 |
| `SANDBOX_OR_ENVIRONMENT` | 10 | 0 | 10 |
| `READINESS_REPORT_DRIFT` | 6 | 6 | 0 |
| `TEST_INFRASTRUCTURE` | 0 | 0 | 0 |
| `OTHER` | 0 | 0 | 0 |

Blockers by subsystem:

| Subsystem | Blockers |
| --- | ---: |
| ACLI conversation replay continuity | 1 |
| ACLI fail-closed operator UX | 1 |
| Hardening / lifecycle gap evidence | 1 |
| ACLI prompt intake / multiline prompt support | 3 |
| Native development replay resume | 1 |
| Readiness and certification reports | 6 |
| HIRR | 0 |
| PPP | 0 |
| Provider pipeline runtime | 0 |
| Translation | 0 |
| Outside scope | 0 |
| Environment | 0 |
| Stale tests | 0 |

## 4. Blocker Inventory

| # | Test | Subsystem | Category | Blocker | Why It Blocks Certification | RC Batch | Complexity | Regression Scope |
| ---: | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `tests/test_conversation_chain_continuity_runtime_v1.py::test_interactive_conversation_preserves_current_chain_across_turns` | ACLI conversation replay continuity | `RC_CORE_BLOCKER` | YES | Platform Core certification requires replay-visible chain continuity and operator inspection evidence. | `RC_BATCH_01` | Medium | Conversation chain continuity and replay inspection commands. |
| 2 | `tests/test_interactive_conversation_cli_v1.py::test_interactive_conversation_fails_closed_on_runtime_error` | ACLI fail-closed UX | `RC_CORE_BLOCKER` | YES | Certification requires clear fail-closed operator evidence when runtime errors occur. | `RC_BATCH_01` | Low | Interactive fail-closed output and workflow status rendering. |
| 3 | `tests/test_lifecycle_gap_detection_runtime_v1.py::test_lifecycle_gap_detection_generates_gap_artifacts_for_failed_lifecycle_run` | Hardening lifecycle gap evidence | `RC_CORE_BLOCKER` | YES | Hardening evidence must classify fail-closed lifecycle interruption deterministically. | `RC_BATCH_01` | Medium | Lifecycle gap detection and replay reconstruction. |
| 4 | `tests/test_multiline_prompt_support_runtime_v1.py::test_case_b_multiline_paste_creates_one_turn_without_fragmentation` | ACLI prompt intake | `RC_CORE_BLOCKER` | YES | Operator prompt intake must preserve one governed turn for multiline input. | `RC_BATCH_01` | Medium | Multiline prompt capture, turn completion, routing compatibility. |
| 5 | `tests/test_multiline_prompt_support_runtime_v1.py::test_multiline_reentry_does_not_consume_sentinel_as_second_turn` | ACLI prompt intake | `RC_CORE_BLOCKER` | YES | Sentinel handling must not create fragmented or misleading operator turns. | `RC_BATCH_01` | Medium | Multiline reentry, prompt state rendering, turn boundaries. |
| 6 | `tests/test_multiline_prompt_support_runtime_v1.py::test_single_line_prompt_still_creates_one_turn` | ACLI prompt intake | `RC_CORE_BLOCKER` | YES | Single-line prompt behavior must remain stable while multiline support exists. | `RC_BATCH_01` | Medium | Single-line prompt capture and response rendering. |
| 7 | `tests/test_native_development_task_intake_and_session_resume_v1.py::test_session_resume_allocates_next_unused_turn_without_router_collision` | Native development replay resume | `RC_CORE_BLOCKER` | YES | Certification requires replay-safe session resume and deterministic native-development artifact placement. | `RC_BATCH_01` | Medium | Session resume, native-development intake, replay path preservation. |
| 29 | `tests/test_freeform_human_prompt_acceptance_v1.py::test_freeform_acceptance_report_matches_current_acli_behavior` | Freeform acceptance report | `READINESS_REPORT_DRIFT` | YES | Formal certification cannot rely on an acceptance report that no longer matches current behavior. | `RC_BATCH_02` | Low | Freeform acceptance report regeneration and routing evidence review. |
| 30 | `tests/test_freeform_human_prompt_acceptance_v1.py::test_freeform_failures_preserve_governance_safety_boundaries` | Freeform acceptance safety report | `READINESS_REPORT_DRIFT` | YES | Safety-boundary evidence must be current before it can support certification. | `RC_BATCH_02` | Low | Freeform failure report semantics and safety-boundary evidence. |
| 31 | `tests/test_provider_acli_connectivity_audit_v1.py::test_provider_acli_connectivity_audit_finds_expected_gaps` | Provider ACLI connectivity audit | `READINESS_REPORT_DRIFT` | YES | Provider connectivity audit is part of certification evidence and must match current gaps. | `RC_BATCH_02` | Low | Provider connectivity audit package. |
| 32 | `tests/test_provider_credential_vault_onboarding_certification_v1.py::test_provider_credential_vault_onboarding_certification_detects_fallback_dependency` | Provider credential certification report | `READINESS_REPORT_DRIFT` | YES | Provider credential certification evidence must not be stale. | `RC_BATCH_02` | Low | Provider credential readiness report. |
| 33 | `tests/test_system_readiness_certification_v1.py::test_system_readiness_certification_produces_expected_packages` | System readiness report | `READINESS_REPORT_DRIFT` | YES | Formal certification depends on readiness packages being produced accurately. | `RC_BATCH_02` | Medium | System readiness package generation. |
| 34 | `tests/test_system_readiness_certification_v1.py::test_system_readiness_certifies_major_architectural_chains` | System readiness report | `READINESS_REPORT_DRIFT` | YES | Major architectural chain certification evidence must match the current Platform Core. | `RC_BATCH_02` | Medium | System readiness chain evidence and report assertions. |

## 5. Non-Blocker Inventory

Every non-blocking failure remains useful for repository quality, but it does not prevent formal Platform Core Generation 1 certification under the current certification scope.

| # | Test | Subsystem | Category | Blocker | Why Certification Can Proceed Without It | Future Batch |
| ---: | --- | --- | --- | --- | --- | --- |
| 8 | `tests/test_aigol_cli_foundation_v1.py::test_no_orchestration_introduced` | CLI lexical guard | `STALE_TEST` | NO | Broad lexical matching does not prove forbidden orchestration behavior. | `RC_BATCH_03` |
| 9 | `tests/test_canonical_bridge_result_artifact_export_import.py::test_sidepanel_import_is_operator_selected_only_without_endpoint_or_listener` | Browser sidepanel lexical guard | `STALE_TEST` | NO | Diagnostic vocabulary does not prove a hidden endpoint or listener. | `RC_BATCH_03` |
| 10 | `tests/test_chat_first_operator_flow.py::test_no_durable_persistence_or_endpoint_is_added` | Chat-first browser preview | `STALE_TEST` | NO | The failure is vocabulary-based, not behavioral Platform Core evidence. | `RC_BATCH_03` |
| 11 | `tests/test_chatgpt_ingress_native_import_preview_v1.py::test_no_native_messaging_call_is_wired_to_preview_button` | ChatGPT ingress preview | `STALE_TEST` | NO | Requires behavior-specific assertion; not a core certification blocker. | `RC_BATCH_03` |
| 12 | `tests/test_chatgpt_ingress_to_semantic_contract_preview_v1.py::test_preview_path_never_invokes_codex_provider` | ChatGPT semantic preview | `STALE_TEST` | NO | Preview vocabulary does not prove provider invocation. | `RC_BATCH_03` |
| 13 | `tests/test_cli_controlled_execution_runtime_v1.py::test_no_retries_introduced` | CLI lexical guard | `STALE_TEST` | NO | Lifecycle command vocabulary does not equal autonomous retry behavior. | `RC_BATCH_03` |
| 14 | `tests/test_governed_browser_companion_runtime.py::test_no_retry_fallback_or_hidden_automation_surface_exists` | Browser companion lexical guard | `STALE_TEST` | NO | Diagnostic fallback language is not hidden automation. | `RC_BATCH_03` |
| 15 | `tests/test_local_governed_transport_runtime_attachment.py::test_no_endpoint_provider_execution_or_orchestration_behavior_is_added` | Local governed transport lexical guard | `STALE_TEST` | NO | Needs behavior-specific transport assertion. | `RC_BATCH_03` |
| 16 | `tests/test_persistent_replay_session.py::test_replay_session_is_bounded_in_memory_and_append_only` | Replay session JS assertion | `STALE_TEST` | NO | Non-mutating string parsing does not prove replay mutation. | `RC_BATCH_03` |
| 17 | `tests/test_conversation_native_development_intent_routing_v1.py::test_interactive_conversation_routes_acceptance_prompts_without_provider_entry_failure` | Provider onboarding workflow | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | NO | Provider onboarding domain is not in current Platform Core certification scope. | `RC_BATCH_05` |
| 18 | `tests/test_conversation_to_ppp_handoff_execution_v1.py::test_interactive_conversation_routes_acceptance_scenarios_to_terminal_states` | Provider onboarding / PPP acceptance | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | NO | Acceptance scenario belongs to provider-onboarding/domain track. | `RC_BATCH_05` |
| 19 | `tests/test_governed_intent_transfer_ingestion.py::test_local_runtime_ingestion_route_returns_preview_ready_response` | Local preview transport | `SANDBOX_OR_ENVIRONMENT` | NO | Local socket restriction is an environment condition, not a core defect. | `RC_BATCH_04` |
| 20 | `tests/test_governed_local_preview_runtime.py::test_real_localhost_post_invocation` | Local preview transport | `SANDBOX_OR_ENVIRONMENT` | NO | Certification can use an environment with permitted localhost transport. | `RC_BATCH_04` |
| 21 | `tests/test_governed_provider_activation_v1.py::test_provider_activation_success` | Provider credential vault | `SANDBOX_OR_ENVIRONMENT` | NO | Read-only local vault path blocks setup but does not prove runtime defect. | `RC_BATCH_04` |
| 22 | `tests/test_governed_provider_activation_v1.py::test_missing_api_key_blocked` | Provider credential vault | `SANDBOX_OR_ENVIRONMENT` | NO | Environment setup fails before behavior is tested. | `RC_BATCH_04` |
| 23 | `tests/test_governed_provider_activation_v1.py::test_replay_visible_invocation_persistence` | Provider replay | `SANDBOX_OR_ENVIRONMENT` | NO | Requires writable certification vault fixture. | `RC_BATCH_04` |
| 24 | `tests/test_governed_provider_activation_v1.py::test_deterministic_replay_hashing` | Provider replay hashing | `SANDBOX_OR_ENVIRONMENT` | NO | Requires writable certification vault fixture. | `RC_BATCH_04` |
| 25 | `tests/test_governed_provider_activation_v1.py::test_provider_response_persistence` | Provider response persistence | `SANDBOX_OR_ENVIRONMENT` | NO | Requires writable certification vault fixture. | `RC_BATCH_04` |
| 26 | `tests/test_governed_provider_activation_v1.py::test_provider_cannot_bypass_runtime_authority` | Provider authority boundary | `SANDBOX_OR_ENVIRONMENT` | NO | Environment rerun required; not counted as a current implementation blocker. | `RC_BATCH_04` |
| 27 | `tests/test_governed_provider_activation_v1.py::test_provider_cannot_trigger_execution` | Provider execution boundary | `SANDBOX_OR_ENVIRONMENT` | NO | Environment rerun required; not counted as a current implementation blocker. | `RC_BATCH_04` |
| 28 | `tests/test_governed_provider_activation_v1.py::test_provider_invocation_replay_reconstruction` | Provider replay reconstruction | `SANDBOX_OR_ENVIRONMENT` | NO | Environment rerun required; not counted as a current implementation blocker. | `RC_BATCH_04` |
| 35 | `sapianta-domain-trading/tests/test_architecture_evolution_constitution.py::test_constitutional_engine_is_read_only` | Trading domain governance | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | NO | Trading domain is outside Platform Core Generation 1 certification. | `RC_BATCH_05` |
| 36 | `sapianta-domain-trading/tests/test_architecture_evolution_constitution.py::test_constitution_manifest_and_artifacts_exist` | Trading domain governance | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | NO | Domain-specific artifact coverage. | `RC_BATCH_05` |
| 37 | `sapianta-domain-trading/tests/test_architecture_freeze_manifest.py::test_frozen_semantics_are_explicit` | Trading domain freeze manifest | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | NO | Domain-specific freeze evidence. | `RC_BATCH_05` |
| 38 | `sapianta-domain-trading/tests/test_architecture_freeze_manifest.py::test_replay_topology_remains_immutable` | Trading domain freeze manifest | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | NO | Domain-specific replay topology evidence. | `RC_BATCH_05` |
| 39 | `sapianta-domain-trading/tests/test_architecture_freeze_manifest.py::test_invariant_topology_is_traceable` | Trading domain freeze manifest | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | NO | Domain-specific invariant evidence. | `RC_BATCH_05` |
| 40 | `sapianta-domain-trading/tests/test_architecture_freeze_manifest.py::test_mutation_boundaries_remain_enforced` | Trading domain freeze manifest | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | NO | Domain-specific mutation-boundary evidence. | `RC_BATCH_05` |
| 41 | `sapianta-domain-trading/tests/test_architecture_freeze_manifest.py::test_governance_freeze_manifest_is_deterministic` | Trading domain freeze manifest | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | NO | Domain-specific manifest evidence. | `RC_BATCH_05` |
| 42 | `sapianta-domain-trading/tests/test_architecture_freeze_manifest.py::test_semantic_kernel_remains_protected` | Trading domain freeze manifest | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | NO | Domain-specific semantic-kernel evidence. | `RC_BATCH_05` |
| 43 | `sapianta-domain-trading/tests/test_architecture_freeze_manifest.py::test_codex_alignment_terminology_remains_explicit` | Trading domain freeze manifest | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | NO | Domain-specific terminology evidence. | `RC_BATCH_05` |
| 44 | `sapianta-domain-trading/tests/test_architecture_freeze_manifest.py::test_no_experimental_zone_leaks_into_frozen_governance` | Trading domain freeze manifest | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | NO | Domain-specific experimental-boundary evidence. | `RC_BATCH_05` |
| 45 | `sapianta-domain-trading/tests/test_architecture_freeze_manifest.py::test_required_architecture_artifacts_exist` | Trading domain freeze manifest | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | NO | Domain-specific required artifacts. | `RC_BATCH_05` |
| 46 | `sapianta-domain-trading/tests/test_architecture_freeze_manifest.py::test_system_identity_and_expansion_boundaries_are_explicit` | Trading domain freeze manifest | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | NO | Domain-specific identity/boundary evidence. | `RC_BATCH_05` |
| 47 | `sapianta-domain-trading/tests/test_architecture_promotion_gates.py::test_promotion_gates_remain_read_only_and_manifest_stable` | Trading promotion gates | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | NO | Domain-specific promotion evidence. | `RC_BATCH_05` |
| 48 | `sapianta-domain-trading/tests/test_architecture_promotion_gates.py::test_promotion_manifest_and_artifacts_exist` | Trading promotion gates | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | NO | Domain-specific promotion artifacts. | `RC_BATCH_05` |
| 49 | `sapianta-domain-trading/tests/test_architecture_review_checkpoint.py::test_semantic_consistency_review_passes` | Trading review checkpoint | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | NO | Domain-specific review checkpoint. | `RC_BATCH_05` |
| 50 | `sapianta-domain-trading/tests/test_architecture_review_checkpoint.py::test_replay_topology_audit_passes_and_is_side_effect_free` | Trading review checkpoint | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | NO | Domain-specific replay audit. | `RC_BATCH_05` |
| 51 | `sapianta-domain-trading/tests/test_architecture_review_checkpoint.py::test_invariant_topology_review_has_no_contradictions` | Trading review checkpoint | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | NO | Domain-specific invariant checkpoint. | `RC_BATCH_05` |
| 52 | `sapianta-domain-trading/tests/test_architecture_review_checkpoint.py::test_trust_boundaries_and_mutation_boundaries_remain_isolated` | Trading review checkpoint | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | NO | Domain-specific boundary checkpoint. | `RC_BATCH_05` |
| 53 | `sapianta-domain-trading/tests/test_architecture_review_checkpoint.py::test_governance_dependencies_are_acyclic` | Trading review checkpoint | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | NO | Domain-specific dependency checkpoint. | `RC_BATCH_05` |
| 54 | `sapianta-domain-trading/tests/test_architecture_review_checkpoint.py::test_codex_vocabulary_remains_deterministic` | Trading review checkpoint | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | NO | Domain-specific vocabulary checkpoint. | `RC_BATCH_05` |
| 55 | `sapianta-domain-trading/tests/test_architecture_review_checkpoint.py::test_no_experimental_leakage_exists` | Trading review checkpoint | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | NO | Domain-specific experimental-zone checkpoint. | `RC_BATCH_05` |
| 56 | `sapianta-domain-trading/tests/test_architecture_review_checkpoint.py::test_architectural_drift_detection_catches_trust_boundary_leakage` | Trading review checkpoint | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | NO | Domain-specific drift detection. | `RC_BATCH_05` |
| 57 | `sapianta-domain-trading/tests/test_architecture_review_checkpoint.py::test_review_process_remains_read_only_and_deterministic` | Trading review checkpoint | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | NO | Domain-specific review process. | `RC_BATCH_05` |
| 58 | `sapianta-domain-trading/tests/test_architecture_review_checkpoint.py::test_required_review_outputs_exist` | Trading review checkpoint | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | NO | Domain-specific review outputs. | `RC_BATCH_05` |
| 59 | `sapianta-domain-trading/tests/test_architecture_review_checkpoint.py::test_checkpoint_json_matches_pass_statuses` | Trading review checkpoint | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | NO | Domain-specific checkpoint JSON. | `RC_BATCH_05` |
| 60 | `sapianta-domain-trading/tests/test_domain_lock_policy.py::test_codex_visible_classifications_remain_stable` | Trading domain lock | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | NO | Domain-specific lock-policy evidence. | `RC_BATCH_05` |
| 61 | `sapianta-domain-trading/tests/test_domain_lock_policy.py::test_domain_lock_policy_artifacts_exist` | Trading domain lock | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | NO | Domain-specific lock-policy artifacts. | `RC_BATCH_05` |
| 62 | `sapianta-domain-trading/tests/test_execution_envelope_model.py::test_manifest_matches_live_document_and_artifacts_exist` | Trading execution envelope | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | NO | Domain-specific execution-envelope manifest. | `RC_BATCH_05` |
| 63 | `sapianta-domain-trading/tests/test_finalize_domain_governance_foundation.py::test_final_manifest_exists_and_is_deterministic_json` | Trading governance finalization | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | NO | Domain-specific final manifest. | `RC_BATCH_05` |
| 64 | `sapianta-domain-trading/tests/test_finalize_domain_governance_foundation.py::test_semantic_freeze_consistency` | Trading governance finalization | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | NO | Domain-specific semantic freeze. | `RC_BATCH_05` |
| 65 | `sapianta-domain-trading/tests/test_finalize_domain_governance_foundation.py::test_trusted_scope_finalization_is_deterministic` | Trading governance finalization | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | NO | Domain-specific trusted-scope finalization. | `RC_BATCH_05` |
| 66 | `sapianta-domain-trading/tests/test_finalize_domain_governance_foundation.py::test_escalation_semantics_are_finalized_and_deterministic` | Trading governance finalization | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | NO | Domain-specific escalation semantics. | `RC_BATCH_05` |
| 67 | `sapianta-domain-trading/tests/test_finalize_domain_governance_foundation.py::test_codex_semantic_continuity_is_stable` | Trading governance finalization | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | NO | Domain-specific semantic continuity. | `RC_BATCH_05` |
| 68 | `sapianta-domain-trading/tests/test_finalize_domain_governance_foundation.py::test_finalization_artifacts_exist` | Trading governance finalization | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | NO | Domain-specific finalization artifacts. | `RC_BATCH_05` |
| 69 | `sapianta-domain-trading/tests/test_finalize_domain_governance_foundation.py::test_no_capability_expansion_was_introduced_by_finalization` | Trading governance finalization | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | NO | Domain-specific capability assertion. | `RC_BATCH_05` |
| 70 | `sapianta-domain-trading/tests/test_finalize_governed_execution_semantics.py::test_semantic_freeze_is_explicit` | Trading governed execution finalization | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | NO | Domain-specific governed-execution freeze. | `RC_BATCH_05` |
| 71 | `sapianta-domain-trading/tests/test_finalize_governed_execution_semantics.py::test_governance_topology_is_locked` | Trading governed execution finalization | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | NO | Domain-specific governance topology. | `RC_BATCH_05` |
| 72 | `sapianta-domain-trading/tests/test_finalize_governed_execution_semantics.py::test_replay_semantics_are_finalized` | Trading governed execution finalization | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | NO | Domain-specific replay semantics. | `RC_BATCH_05` |
| 73 | `sapianta-domain-trading/tests/test_finalize_governed_execution_semantics.py::test_invariant_topology_is_finalized` | Trading governed execution finalization | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | NO | Domain-specific invariant topology. | `RC_BATCH_05` |
| 74 | `sapianta-domain-trading/tests/test_finalize_governed_execution_semantics.py::test_trust_boundaries_are_finalized` | Trading governed execution finalization | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | NO | Domain-specific trust boundaries. | `RC_BATCH_05` |
| 75 | `sapianta-domain-trading/tests/test_finalize_governed_execution_semantics.py::test_residual_risks_are_consolidated_and_visible` | Trading governed execution finalization | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | NO | Domain-specific residual risk evidence. | `RC_BATCH_05` |
| 76 | `sapianta-domain-trading/tests/test_finalize_governed_execution_semantics.py::test_expansion_readiness_is_classified` | Trading governed execution finalization | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | NO | Domain-specific expansion readiness. | `RC_BATCH_05` |
| 77 | `sapianta-domain-trading/tests/test_finalize_governed_execution_semantics.py::test_governance_stabilization_review_passes` | Trading governed execution finalization | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | NO | Domain-specific stabilization review. | `RC_BATCH_05` |
| 78 | `sapianta-domain-trading/tests/test_finalize_governed_execution_semantics.py::test_codex_semantic_stabilization_exists` | Trading governed execution finalization | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | NO | Domain-specific semantic stabilization. | `RC_BATCH_05` |
| 79 | `sapianta-domain-trading/tests/test_finalize_governed_execution_semantics.py::test_no_capability_expansion_or_production_execution_exists` | Trading governed execution finalization | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | NO | Domain-specific production/capability assertion. | `RC_BATCH_05` |
| 80 | `sapianta-domain-trading/tests/test_finalize_governed_execution_semantics.py::test_finalization_artifacts_exist` | Trading governed execution finalization | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | NO | Domain-specific finalization artifacts. | `RC_BATCH_05` |
| 81 | `sapianta-domain-trading/tests/test_finalize_governed_execution_semantics.py::test_final_manifest_is_deterministic` | Trading governed execution finalization | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | NO | Domain-specific final manifest. | `RC_BATCH_05` |
| 82 | `sapianta-domain-trading/tests/test_governance_adversarial_suite.py::test_manifest_matches_live_document_and_artifacts_exist` | Trading adversarial governance | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | NO | Domain-specific adversarial suite manifest. | `RC_BATCH_05` |
| 83 | `sapianta-domain-trading/tests/test_governance_capability_review.py::test_manifest_matches_live_document_and_artifacts_exist` | Trading capability review | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | NO | Domain-specific capability review manifest. | `RC_BATCH_05` |
| 84 | `sapianta-domain-trading/tests/test_governed_execution_proposal_pipeline.py::test_manifest_matches_live_document_and_artifacts_exist` | Trading governed execution proposal pipeline | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | NO | Domain-specific proposal-pipeline manifest. | `RC_BATCH_05` |
| 85 | `sapianta-domain-trading/tests/test_runtime_foundation_freeze.py::test_manifest_matches_live_document_and_artifacts_exist` | Trading runtime foundation freeze | `DOMAIN_OUTSIDE_CERTIFIED_CORE` | NO | Domain-specific runtime-foundation manifest. | `RC_BATCH_05` |

## 6. Implementation Estimate

Certification-blocking implementation scope:

| Work | Included Failures | Estimated Scope | Required Before Certification |
| --- | --- | --- | --- |
| `RC_BATCH_01_CORE_BLOCKERS` | 1-7 | Medium | Yes |
| `RC_BATCH_02_READINESS_REPORT_DRIFT` | 29-34 | Low to medium | Yes |

Non-blocking implementation scope:

| Work | Included Failures | Estimated Scope | Required Before Certification |
| --- | --- | --- | --- |
| `RC_BATCH_03_STALE_TESTS` | 8-16 | Low | No |
| `RC_BATCH_04_ENVIRONMENT` | 19-28 | Low | No, but required for a clean local full-suite run. |
| `RC_BATCH_05_SCOPE_AND_DOMAIN` | 17-18, 35-85 | Medium to high | No, if formally scoped out. |

## 7. Certification Readiness Projection

### Scenario A: Repair Only Certification Blockers

Repair set:

```text
13 failures
```

Includes:

- `RC_BATCH_01_CORE_BLOCKERS`
- `RC_BATCH_02_READINESS_REPORT_DRIFT`

Would Platform Core Generation 1 become `CERTIFIED_READY`?

```text
YES, assuming environment-bound evidence is rerun or formally accepted as environment-limited and outside the blocker count.
```

Reason:

The certification blockers are the failures that directly affect current Platform Core behavior and formal certification evidence. Once those are repaired, the remaining failures are outside certified scope, stale tests, or environment constraints.

### Scenario B: Repair All 85 Failures

Would certification meaningfully improve?

```text
YES, but mostly as repository-wide quality improvement rather than Platform Core certification necessity.
```

Reason:

Repairing all 85 failures would produce a cleaner repository-wide pytest result and reduce future ambiguity. However, 72 of the failures are not required to certify Platform Core Generation 1 under current scope. Repairing all failures would mix certification work with stale-test cleanup, environment setup, provider-onboarding/domain work, and trading-domain certification.

Difference:

```text
Scenario A certifies Platform Core Generation 1.
Scenario B cleans the broader repository and adjacent domain tracks.
```

## 8. Recommended Implementation Order

Recommended scope for achieving formal Platform Core Generation 1 certification:

1. `RC_BATCH_01_CORE_BLOCKERS`

   Close the seven Platform Core behavior/evidence blockers.

2. `RC_BATCH_02_READINESS_REPORT_DRIFT`

   Regenerate or repair the six certification evidence/report failures.

3. Formal certification review.

Recommended post-certification cleanup:

1. `RC_BATCH_03_STALE_TESTS`

   Replace broad lexical guards with behavior-specific assertions.

2. `RC_BATCH_04_ENVIRONMENT`

   Provide sandbox-compatible or certification-environment test paths.

3. `RC_BATCH_05_SCOPE_AND_DOMAIN`

   Separate provider-onboarding and trading-domain certification tracks.

## 9. Final Determination

Total failures:

```text
85
```

Certification blockers:

```text
13
```

Non-blocking failures:

```text
72
```

Recommended implementation scope for formal Platform Core Generation 1 certification:

```text
RC_BATCH_01_CORE_BLOCKERS
RC_BATCH_02_READINESS_REPORT_DRIFT
```

Final verdict:

```text
RC_CERTIFICATION_BLOCKER_IDENTIFICATION_COMPLETE
```
