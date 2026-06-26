# PLATFORM_CORE_GENERATION1_RELEASE_CANDIDATE_VALIDATION_V1

Status: COMPLETE

Target verdict:

```text
PLATFORM_CORE_GENERATION1_RELEASE_CANDIDATE_VALIDATION_COMPLETE
```

Release-candidate recommendation:

```text
RELEASE_CANDIDATE_NOT_READY_FOR_FORMAL_CERTIFICATION
```

## 1. Validation Purpose

This artifact records the full release-candidate validation run for Platform Core Generation 1.

This is a validation artifact only. It does not modify runtime code, tests, governance, replay, routing, lifecycle, PPP, provider pipeline, or Platform Core architecture.

## 2. Validation Commands

Executed:

```text
git diff --check
python -m pytest -q
```

Additional classification spot checks:

```text
python -m pytest tests/test_governed_provider_activation_v1.py -q
python -m pytest tests/test_multiline_prompt_support_runtime_v1.py tests/test_native_development_task_intake_and_session_resume_v1.py tests/test_persistent_replay_session.py -q
python -m pytest tests/test_conversation_chain_continuity_runtime_v1.py tests/test_interactive_conversation_cli_v1.py tests/test_lifecycle_gap_detection_runtime_v1.py -q
```

## 3. Validation Results

Whitespace validation:

```text
PASS
```

Full pytest result:

```text
85 failed
5503 passed
2 skipped
duration: 122.88s
```

Conclusion:

```text
The full release-candidate suite does not pass.
Platform Core Generation 1 cannot move directly from READY_WITH_LIMITATIONS to formal certification until release-candidate blockers are resolved or explicitly reclassified by governance review.
```

## 4. Failure Classification Summary

| Category | Count / Scope | Certification Impact |
| --- | --- | --- |
| Core blocker | Small but material set | Blocks release-candidate certification until resolved or formally reclassified. |
| Non-core limitation | Several operator/UX/reporting failures | Does not invalidate architecture, but blocks clean RC evidence if in full suite. |
| Stale test / lexical guard | Multiple tests | Requires test review, not architecture repair. |
| External dependency / sandbox | Provider vault and local socket failures | Not a Platform Core logic defect, but must be handled in certification environment. |
| Unrelated domain coverage | Large `sapianta-domain-trading` cluster | Outside Platform Core path; should be excluded or separately certified. |

## 5. Core Blockers

The following failures affect Platform Core release-candidate confidence because they touch interactive operator flow, replay/session continuity, lifecycle gap evidence, or prompt handling.

### 5.1 Conversation Chain Continuity

Failure:

```text
tests/test_conversation_chain_continuity_runtime_v1.py::test_interactive_conversation_preserves_current_chain_across_turns
```

Observed:

```text
KeyError: 'suggested_inspection_commands'
```

Classification:

```text
Core blocker
```

Reason:

The canonical chain id is preserved, but the second turn lacks expected inspection command evidence. This affects operator replay inspection continuity and release-candidate evidence quality.

### 5.2 Multiline Prompt Support

Failures:

```text
tests/test_multiline_prompt_support_runtime_v1.py::test_case_b_multiline_paste_creates_one_turn_without_fragmentation
tests/test_multiline_prompt_support_runtime_v1.py::test_multiline_reentry_does_not_consume_sentinel_as_second_turn
tests/test_multiline_prompt_support_runtime_v1.py::test_single_line_prompt_still_creates_one_turn
```

Observed:

- Expected deterministic monkeypatched response is not rendered.
- Prompt state shows `WAITING_FOR_OPERATOR: CLARIFICATION` instead of completed state.
- Single-line prompt routes to clarification instead of the monkeypatched conversation path.

Classification:

```text
Core blocker / possible stale test interaction
```

Reason:

Multiline capture itself still appears to preserve one-turn boundaries, but the operator-visible completion assertions no longer match current routing behavior. This must be resolved or reclassified before formal RC certification.

### 5.3 Session Resume Native Context Replay

Failure:

```text
tests/test_native_development_task_intake_and_session_resume_v1.py::test_session_resume_allocates_next_unused_turn_without_router_collision
```

Observed:

```text
TURN-000002/native_development_task_intake/000_native_development_task_intake_recorded.json missing
```

Classification:

```text
Core blocker
```

Reason:

Session resume allocation works, but expected native-development replay location is missing. This may be a routing change or replay-path movement, but release-candidate evidence cannot assume it is benign without audit.

### 5.4 Interactive Fail-Closed Output Ordering

Failure:

```text
tests/test_interactive_conversation_cli_v1.py::test_interactive_conversation_fails_closed_on_runtime_error
```

Observed:

The expected `FAILED_CLOSED: synthetic runtime failure` location changed; current output includes a `TURN COMPLETED` block where the test expected the fail-closed line.

Classification:

```text
Core UX / stale assertion candidate
```

Reason:

Fail-closed behavior appears present, but operator output ordering changed. This affects formal operator evidence expectations and should be reviewed.

### 5.5 Lifecycle Gap Classification

Failure:

```text
tests/test_lifecycle_gap_detection_runtime_v1.py::test_lifecycle_gap_detection_generates_gap_artifacts_for_failed_lifecycle_run
```

Observed:

```text
FAIL_CLOSED_INTERRUPTION missing from gap_categories
```

Classification:

```text
Core blocker
```

Reason:

Gap detection did produce lifecycle gaps, but no longer classifies the fail-closed interruption category expected by the hardening evidence model.

## 6. Non-Core Limitations And Operator Coverage Failures

### 6.1 Provider Onboarding Domain Acceptance

Failures:

```text
tests/test_conversation_native_development_intent_routing_v1.py::test_interactive_conversation_routes_acceptance_prompts_without_provider_entry_failure
tests/test_conversation_to_ppp_handoff_execution_v1.py::test_interactive_conversation_routes_acceptance_scenarios_to_terminal_states
```

Observed:

```text
unsupported conversational workflow selection: PROVIDER_ONBOARDING_DOMAIN
```

Classification:

```text
Unrelated domain coverage / non-core limitation
```

Reason:

This affects provider-onboarding acceptance prompts, not the certified Platform Core hardening path. It should be tracked separately before claiming broad provider-onboarding readiness.

### 6.2 Freeform Human Prompt Acceptance

Failures:

```text
tests/test_freeform_human_prompt_acceptance_v1.py::test_freeform_acceptance_report_matches_current_acli_behavior
tests/test_freeform_human_prompt_acceptance_v1.py::test_freeform_failures_preserve_governance_safety_boundaries
```

Observed:

- Acceptance report expected count differs from current behavior.
- Some records now contain `INTAKE_NOT_APPLICABLE`.

Classification:

```text
Non-core limitation / stale evidence report candidate
```

Reason:

Safety boundaries remain under test, but the recorded acceptance report no longer matches current routing behavior. Requires report regeneration or routing audit.

## 7. Stale Test Or Lexical Guard Failures

Several failures are caused by broad string bans that now match diagnostic labels, command names, or preview labels rather than actual forbidden behavior.

Examples:

```text
tests/test_aigol_cli_foundation_v1.py::test_no_orchestration_introduced
tests/test_cli_controlled_execution_runtime_v1.py::test_no_retries_introduced
tests/test_governed_browser_companion_runtime.py::test_no_retry_fallback_or_hidden_automation_surface_exists
tests/test_canonical_bridge_result_artifact_export_import.py::test_sidepanel_import_is_operator_selected_only_without_endpoint_or_listener
tests/test_chat_first_operator_flow.py::test_no_durable_persistence_or_endpoint_is_added
tests/test_chatgpt_ingress_native_import_preview_v1.py::test_no_native_messaging_call_is_wired_to_preview_button
tests/test_chatgpt_ingress_to_semantic_contract_preview_v1.py::test_preview_path_never_invokes_codex_provider
tests/test_local_governed_transport_runtime_attachment.py::test_no_endpoint_provider_execution_or_orchestration_behavior_is_added
tests/test_persistent_replay_session.py::test_replay_session_is_bounded_in_memory_and_append_only
```

Observed examples:

```text
"retry" matched lifecycle command vocabulary.
"fallback" matched diagnostic vocabulary.
"serviceworker" matched a diagnostics variable name.
"codex_cli_provider" matched preview boundary text.
".pop(" matched non-mutating string parsing usage.
```

Classification:

```text
Stale test / overbroad lexical guard
```

Certification impact:

These failures block a clean full-suite release-candidate run, but do not by themselves prove Platform Core architecture drift. They require test review and likely more precise assertions.

## 8. External Dependency And Sandbox Failures

### 8.1 Provider Credential Vault Path

Failures:

```text
tests/test_governed_provider_activation_v1.py::* 8 failures
```

Observed:

```text
OSError: [Errno 30] Read-only file system:
/home/pisarna/.config/aigol/provider-credentials.json
```

Classification:

```text
External dependency / sandbox configuration
```

Reason:

Tests attempt to write provider credentials outside the writable workspace. This is not a Platform Core logic failure, but formal certification must run in an environment with a writable configured credential vault or a test-local vault override.

### 8.2 Local Preview HTTP Server

Failures:

```text
tests/test_governed_intent_transfer_ingestion.py::test_local_runtime_ingestion_route_returns_preview_ready_response
tests/test_governed_local_preview_runtime.py::test_real_localhost_post_invocation
```

Observed:

```text
PermissionError: [Errno 1] Operation not permitted
```

Classification:

```text
External dependency / sandbox networking
```

Reason:

The environment blocks local socket creation. This is not evidence of a Platform Core logic defect.

## 9. System Readiness And Provider Connectivity Audits

Failures:

```text
tests/test_provider_acli_connectivity_audit_v1.py::test_provider_acli_connectivity_audit_finds_expected_gaps
tests/test_provider_credential_vault_onboarding_certification_v1.py::test_provider_credential_vault_onboarding_certification_detects_fallback_dependency
tests/test_system_readiness_certification_v1.py::test_system_readiness_certification_produces_expected_packages
tests/test_system_readiness_certification_v1.py::test_system_readiness_certifies_major_architectural_chains
```

Classification:

```text
Operational / evidence drift
```

Reason:

These tests assert readiness report content or package outputs that may have drifted after recent hardening. They should be audited before formal certification.

## 10. Domain-Trading Failures

The largest failure cluster is under:

```text
sapianta-domain-trading/tests/
```

Examples:

```text
test_architecture_evolution_constitution.py
test_architecture_freeze_manifest.py
test_architecture_promotion_gates.py
test_architecture_review_checkpoint.py
test_domain_lock_policy.py
test_execution_envelope_model.py
test_finalize_domain_governance_foundation.py
test_finalize_governed_execution_semantics.py
test_governance_adversarial_suite.py
test_governance_capability_review.py
test_governed_execution_proposal_pipeline.py
test_runtime_foundation_freeze.py
```

Observed:

- missing `sapianta-domain-trading/FINALIZE_GOVERNED_EXECUTION_SEMANTICS_FOUNDATION.json`;
- missing finalization artifacts;
- manifest hash mismatches;
- domain governance documents not matching generated manifests.

Classification:

```text
Unrelated domain coverage / separate domain certification
```

Certification impact:

These failures block a repository-wide full-suite pass, but should not automatically block Platform Core Generation 1 certification unless domain-trading is included in the Platform Core certification scope. They must be excluded by scope or repaired in a domain-specific release track.

## 11. Core Certification Gate Review

| Gate | RC Status | Notes |
| --- | --- | --- |
| Deterministic routing | OPEN_WITH_FAILURES | Provider-onboarding and freeform acceptance failures require classification. |
| Deterministic replay | OPEN_WITH_FAILURES | Session resume replay path and domain-trading manifest failures require resolution or scoping. |
| Workflow identity | MOSTLY_CLOSED | Recent PPP/lifecycle tests pass; chain inspection evidence has a missing field. |
| Lifecycle continuation | CLOSED | Recent repaired lifecycle/PPP continuation surfaces pass focused validation. |
| Fail-closed behavior | OPEN_WITH_FAILURES | Fail-closed exists, but lifecycle gap classification and output ordering assertions fail. |
| Governance preservation | CLOSED_WITH_SCOPE_LIMITS | No governance defect shown in Platform Core path; domain-trading governance manifests fail separately. |
| Approval preservation | NOT_IMPLICATED_BY_RC_FAILURES | No direct approval-boundary failure identified in the summary. |
| Replay preservation | OPEN_WITH_FAILURES | Core replay is strong, but full-suite replay/domain artifacts are not clean. |
| Hardening evidence | OPEN_WITH_FAILURES | Lifecycle gap detection classification failure is material. |
| Operator usability | OPEN_WITH_FAILURES | Multiline prompt and fail-closed output tests fail. |
| Auditability | OPEN_WITH_FAILURES | Several audit/report tests have evidence drift. |

## 12. Can Platform Core Proceed Toward Formal Certification?

Answer:

```text
NOT YET AS A RELEASE CANDIDATE
```

Platform Core remains architecturally ready with limitations, but the full release-candidate validation is not clean enough to enter formal certification without remediation or governed scope exclusion.

The release-candidate path should proceed as:

```text
READY_WITH_LIMITATIONS
-> RC failure triage
-> resolve core blockers
-> reclassify or scope-exclude stale/domain/external failures
-> rerun full release-candidate validation
-> formal certification review
```

## 13. Required Remediation Before Formal Certification

P0 release-candidate blockers:

1. Restore or reclassify conversation chain inspection command evidence.

2. Audit multiline prompt support against current routing and operator output behavior.

3. Audit session-resume native replay path expectations.

4. Restore or reclassify lifecycle gap detection category `FAIL_CLOSED_INTERRUPTION`.

5. Decide whether provider-onboarding domain prompts are in Platform Core scope.

P1 cleanup:

1. Replace broad lexical guard tests with behavior-specific assertions.

2. Regenerate or reclassify freeform prompt acceptance reports.

3. Add test-local credential vault configuration for provider activation tests.

4. Mark local socket tests with environment requirements or use a sandbox-compatible path.

5. Separate domain-trading certification suite from Platform Core release-candidate suite unless it is explicitly in scope.

## 14. Final Recommendation

Recommendation:

```text
HOLD_FORMAL_CERTIFICATION_PENDING_RC_TRIAGE
```

Rationale:

- The full suite does not pass.
- Several failures are not Platform Core defects, but they still prevent a clean release-candidate evidence package.
- A smaller set of failures touches core operator continuity, prompt handling, session replay, and hardening gap classification.
- Formal certification should be evidence-based and should not proceed with unresolved full-suite failures unless they are formally scoped out.

## 15. Final Verdict

```text
PLATFORM_CORE_GENERATION1_RELEASE_CANDIDATE_VALIDATION_COMPLETE
```
