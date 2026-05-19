const lifecycleEntries = [];

const COCKPIT_IDS = {
  replayTimeline: "replay-timeline",
  lifecycleView: "lifecycle-view",
  approvalVisibility: "approval-visibility",
  governanceBoundary: "governance-boundary",
  semanticDirection: "semantic-direction",
  continuityHumanRequest: "continuity-human-request",
  envelopeValidationStatus: "envelope-validation-status",
  validatorCompositionStatus: "validator-composition-status",
  continuityStatus: "continuity-status",
  lineageSummary: "lineage-summary",
  continuityFindings: "continuity-findings"
};

function deterministicId(prefix, value) {
  const text = JSON.stringify(canonicalize(value));
  let hash = 2166136261;
  for (let index = 0; index < text.length; index += 1) {
    hash ^= text.charCodeAt(index);
    hash = Math.imul(hash, 16777619);
  }
  return `${prefix}-${(hash >>> 0).toString(16).padStart(8, "0")}`;
}

function lifecycleStatus(summary) {
  if (summary.status === "BLOCKED") {
    return "blocked";
  }
  if (summary.status === "RETURNED" || summary.status === "OBSERVED") {
    return "returned";
  }
  return "";
}

function statusValue(summary) {
  return summary.status || summary.ingestion_status || "UNKNOWN";
}

function setCockpitText(id, value) {
  const node = document.getElementById(id);
  if (node) {
    node.textContent = value;
  }
}

function compactValue(value) {
  if (value === undefined || value === null || value === "") {
    return "unknown";
  }
  if (typeof value === "object") {
    return JSON.stringify(canonicalize(value));
  }
  return String(value);
}

function replaySummary(entry, index) {
  return [
    `entry: ${index + 1}`,
    "label: Transport replay - deterministic package movement evidence",
    `status: ${statusValue(entry)}`,
    `replay_identity: ${compactValue(entry.replay_identity)}`,
    `request_id: ${compactValue(entry.request_id)}`,
    `response_id: ${compactValue(entry.response_id)}`
  ].join("\n");
}

function lifecycleSummary(entry) {
  return [
    "label: Lifecycle state - governed transport state",
    "mutation: visualization creates no lifecycle transition",
    `status: ${statusValue(entry)}`,
    `timeline: ${compactValue(entry.timeline || entry.timeline_state)}`,
    `deterministic_closure: ${compactValue(entry.deterministic_closure || entry.closure)}`
  ].join("\n");
}

function approvalSummary(entry) {
  return [
    "label: Approval state - visibility only",
    "authority: visualization grants no execution authority",
    `requires_confirmation: ${compactValue(entry.requires_confirmation)}`,
    `approval_required: ${compactValue(entry.approval_required)}`,
    `authority_granted: ${compactValue(entry.authority_granted)}`,
    `execution_authority: ${compactValue(entry.execution_authority || entry.downstream_execution_authority)}`
  ].join("\n");
}

function boundarySummary(entry) {
  const evidence = entry.evidence || {};
  const boundary = entry.boundary_guarantees || entry.boundary_state || entry.ingestion_boundary_guarantees || {};
  return [
    "label: Boundary evidence view",
    "observability: read-only, no dispatch, no runtime write",
    `localhost_only: ${compactValue(evidence.localhost_only)}`,
    `hidden_execution: ${compactValue(evidence.hidden_execution_present || boundary.hidden_execution)}`,
    `automatic_dispatch: ${compactValue(boundary.automatic_dispatch)}`,
    `hidden_persistence: false`,
    `hidden_networking: false`
  ].join("\n");
}

function semanticDirectionSummary(entry) {
  return [
    "label: Semantic direction proposal - not execution authority",
    "semantic replay: model-native and non-deterministic",
    "continuity: In-memory sidepanel continuity - non-durable",
    `normalized_request: ${compactValue(entry.normalized_governed_request)}`,
    `governance_mode: ${compactValue(entry.governance_mode)}`,
    `codex_prompt_preview: ${compactValue(entry.codex_prompt_preview)}`
  ].join("\n");
}

function continuityReport(entry) {
  return entry.continuity_report || {};
}

function sidepanelContinuityRendering(entry) {
  return entry.sidepanel_rendering || {};
}

function continuityHumanRequestSummary(entry) {
  const envelope = (entry.artifacts && entry.artifacts.envelope) || {};
  const request = envelope.originating_human_request_ref || {};
  return [
    "label: Human Request - explicit local input only",
    "authority: request context does not approve, dispatch, or execute",
    `request_text: ${compactValue(request.request_text)}`,
    `authority: ${compactValue(request.authority)}`
  ].join("\n");
}

function envelopeValidationStatusSummary(entry) {
  const report = entry.envelope_validation_report || {};
  return [
    "label: Envelope Validation Status - read-only report",
    "authority: validation success is not approval",
    `validation_id: ${compactValue(report.validation_id)}`,
    `status: ${compactValue(report.status)}`
  ].join("\n");
}

function validatorCompositionStatusSummary(entry) {
  const report = entry.validator_composition_report || {};
  return [
    "label: Validator Composition Status - deterministic aggregation only",
    "authority: aggregate valid is not dispatch",
    `composition_id: ${compactValue(report.composition_id)}`,
    `aggregate_status: ${compactValue(report.aggregate_status)}`,
    `validator_order: ${compactValue(report.validator_order)}`
  ].join("\n");
}

function continuityStatusSummary(entry) {
  const report = continuityReport(entry);
  return [
    "label: Continuity Status - report validity only",
    "authority: CONTINUITY_VALID is not approval, dispatch, execution, or continuation",
    `continuity_report_id: ${compactValue(report.continuity_report_id)}`,
    `aggregate_governance_status: ${compactValue(report.aggregate_governance_status)}`,
    `recommendations: ${compactValue(report.continuity_recommendations)}`
  ].join("\n");
}

function lineageSummary(entry) {
  const rendering = sidepanelContinuityRendering(entry);
  const report = continuityReport(entry);
  return [
    "label: Lineage Summary - visibility without mutation",
    `lineage_summary: ${compactValue(rendering.lineage_summary || report.lineage_summary)}`,
    "mutation: false"
  ].join("\n");
}

function continuityFindingsSummary(entry) {
  const report = continuityReport(entry);
  return [
    "label: Findings / Risks / Recommendations - report-only",
    "continuation: no autonomous continuation",
    `findings: ${compactValue(report.continuity_findings)}`,
    `risks: ${compactValue(report.continuity_risks)}`,
    `recommendations: ${compactValue(report.continuity_recommendations)}`
  ].join("\n");
}

function demoReplayReferences() {
  return [
    { replay_id: "DEMO-REPLAY-ENVELOPE", reference_status: "REFERENCED_NOT_MUTATED" },
    { replay_id: "DEMO-REPLAY-COMPOSITION", reference_status: "REFERENCED_NOT_MUTATED" },
    { replay_id: "DEMO-REPLAY-CONTINUITY", reference_status: "REFERENCED_NOT_MUTATED" }
  ];
}

function demoLifecycleReferences() {
  return [
    { previous_state: "CREATED", next_state: "NORMALIZED", reference_status: "VISIBLE_APPEND_ONLY_REFERENCE" },
    { previous_state: "NORMALIZED", next_state: "RETURNED", reference_status: "VISIBLE_APPEND_ONLY_REFERENCE" }
  ];
}

function runMinimalGovernedOperationalLoopDemo(userRequest) {
  const requestText = String(userRequest || "Show governed continuity without execution");
  const lineageId = deterministicId("DEMO-LINEAGE", { request: requestText });
  const continuityReportId = deterministicId("CONTINUITY", { request: requestText, lineage_id: lineageId });
  const envelopeValidationId = deterministicId("VALIDATION", { request: requestText });
  const compositionId = deterministicId("COMPOSITION", { request: requestText, validator_order: ["envelope_validation"] });

  const replayRefs = demoReplayReferences();
  const lifecycleRefs = demoLifecycleReferences();
  const envelope = {
    loop_id: "DEMO-LOOP-1",
    originating_human_request_ref: { request_text: requestText, authority: "context_only" },
    semantic_interpretation_boundary: {
      statement: "Semantic direction is context only and remains non-authoritative.",
      interpretation_status: "NON_AUTHORITATIVE",
      semantic_replay_determinism: false,
      semantic_authority: false
    },
    replay_refs: replayRefs,
    lifecycle_refs: lifecycleRefs,
    lineage_id: lineageId,
    authority_boundary_statement: "VALID and CONTINUITY_VALID are not approval, dispatch, execution, or continuation authority."
  };
  const continuityReport = {
    continuity_report_id: continuityReportId,
    aggregate_governance_status: "CONTINUITY_VALID",
    replay_visibility_summary: { visible: true, reference_count: replayRefs.length, gaps: [], mutated: false },
    lifecycle_visibility_summary: { visible: true, reference_count: lifecycleRefs.length, gaps: [], mutated: false },
    authority_boundary_summary: { visible: true, statement_count: 1, violations: [], authority_created: false },
    semantic_boundary_summary: { visible: true, statement_count: 1, overclaims: [], semantic_authority_created: false },
    determinism_summary: {
      deterministic_report_generation: true,
      stable_status_precedence: true,
      unknown_statuses_fail_closed: true
    },
    continuity_findings: [],
    continuity_risks: [],
    continuity_recommendations: ["Continuity evidence is valid for read-only operational review."],
    lineage_summary: { visible: true, reference_count: 1, mutated: false }
  };

  return {
    demo_id: "MINIMAL_GOVERNED_OPERATIONAL_LOOP_RUNTIME_V1",
    status: "RETURNED",
    artifacts: { envelope },
    envelope_validation_report: { validation_id: envelopeValidationId, status: "VALID" },
    validator_composition_report: {
      composition_id: compositionId,
      aggregate_status: "VALID",
      validator_order: ["envelope_validation"]
    },
    continuity_report: continuityReport,
    sidepanel_rendering: {
      continuity_findings: [],
      replay_lifecycle_visibility: {
        replay: continuityReport.replay_visibility_summary,
        lifecycle: continuityReport.lifecycle_visibility_summary
      },
      authority_boundary_visibility: continuityReport.authority_boundary_summary,
      semantic_boundary_visibility: continuityReport.semantic_boundary_summary,
      lineage_summary: continuityReport.lineage_summary,
      observability_label: "Read-only sidepanel observability; no provider calls, approval, execution, or continuation."
    },
    authority_guarantees: {
      provider_calls: false,
      dispatch: false,
      approval: false,
      execution: false,
      lifecycle_mutation: false,
      replay_mutation: false,
      persistence: false,
      orchestration: false,
      autonomous_continuation: false,
      hidden_authority: false
    }
  };
}

function runGovernedDemoFromSidepanel() {
  const request = document.getElementById("governed-demo-request");
  const artifactInput = document.getElementById("artifact");
  const value = request && request.value ? request.value : artifactInput.value;
  window.sidepanelRenderResult(runMinimalGovernedOperationalLoopDemo(value));
}

function renderReadOnlyCockpit() {
  const latest = lifecycleEntries[lifecycleEntries.length - 1] || {};
  setCockpitText(
    COCKPIT_IDS.replayTimeline,
    lifecycleEntries.map(replaySummary).join("\n\n") || "No replay entries rendered."
  );
  setCockpitText(COCKPIT_IDS.lifecycleView, lifecycleSummary(latest));
  setCockpitText(COCKPIT_IDS.approvalVisibility, approvalSummary(latest));
  setCockpitText(COCKPIT_IDS.governanceBoundary, boundarySummary(latest));
  setCockpitText(COCKPIT_IDS.semanticDirection, semanticDirectionSummary(latest));
  setCockpitText(COCKPIT_IDS.continuityHumanRequest, continuityHumanRequestSummary(latest));
  setCockpitText(COCKPIT_IDS.envelopeValidationStatus, envelopeValidationStatusSummary(latest));
  setCockpitText(COCKPIT_IDS.validatorCompositionStatus, validatorCompositionStatusSummary(latest));
  setCockpitText(COCKPIT_IDS.continuityStatus, continuityStatusSummary(latest));
  setCockpitText(COCKPIT_IDS.lineageSummary, lineageSummary(latest));
  setCockpitText(COCKPIT_IDS.continuityFindings, continuityFindingsSummary(latest));
}

window.sidepanelRenderResult = function renderLifecycleResult(summary) {
  lifecycleEntries.push(canonicalize(summary));

  const result = document.getElementById("result");
  const entry = document.createElement("article");
  const heading = document.createElement("h3");
  const payload = document.createElement("pre");
  const statusClass = lifecycleStatus(summary);

  entry.className = `lifecycle-entry${statusClass ? ` ${statusClass}` : ""}`;
  heading.textContent = `Lifecycle entry ${lifecycleEntries.length}: ${summary.status || "RESULT"}`;
  payload.textContent = JSON.stringify(canonicalize(summary), null, 2);

  entry.append(heading, payload);
  result.append(entry);
  result.scrollTop = result.scrollHeight;
  renderReadOnlyCockpit();
};

const governedDemoButton = document.getElementById("run-governed-demo");
if (governedDemoButton) {
  governedDemoButton.onclick = runGovernedDemoFromSidepanel;
}
