const lifecycleEntries = [];
const replaySessionEntries = [];
const REPLAY_SESSION_ID = "PERSISTENT_REPLAY_SESSION_V1";
const REQUIRED_SEMANTIC_PROPOSAL_FIELDS = [
  "human_request",
  "semantic_intent",
  "proposed_mode",
  "risk_class",
  "authority_boundary_statement",
  "semantic_boundary_statement",
  "requested_action_type"
];
const ALLOWED_SEMANTIC_PROPOSAL_MODES = ["READ_ONLY", "REVIEW_ONLY", "DEMO_ONLY"];
const REJECTED_SEMANTIC_PROPOSAL_MODES = [
  "EXECUTE",
  "AUTO_EXECUTE",
  "AUTONOMOUS",
  "PROVIDER_RUNTIME",
  "ORCHESTRATION"
];

const COCKPIT_IDS = {
  executiveOperationalSummary: "executive-operational-summary",
  operationalNarrative: "operational-narrative",
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
  continuityFindings: "continuity-findings",
  envelopeValidationArtifact: "inspection-envelope-validation-artifact",
  validatorCompositionArtifact: "inspection-validator-composition-artifact",
  continuityReportArtifact: "inspection-continuity-report-artifact",
  replaySummaryArtifact: "inspection-replay-summary-artifact",
  lifecycleSummaryArtifact: "inspection-lifecycle-summary-artifact",
  lineageSummaryArtifact: "inspection-lineage-summary-artifact",
  authorityBoundaryArtifact: "inspection-authority-boundary-artifact",
  semanticBoundaryArtifact: "inspection-semantic-boundary-artifact",
  currentReplaySession: "current-replay-session",
  replayEntryInspection: "replay-entry-inspection",
  semanticProposalValidationStatus: "semantic-proposal-validation-status",
  semanticProposalArtifact: "semantic-proposal-artifact"
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
  const proposal = entry.semantic_proposal || {};
  return [
    "label: Semantic direction proposal - not execution authority",
    "semantic replay: model-native and non-deterministic",
    "continuity: In-memory sidepanel continuity - non-durable",
    `semantic_intent: ${compactValue(proposal.semantic_intent)}`,
    `proposed_mode: ${compactValue(proposal.proposed_mode)}`,
    `risk_class: ${compactValue(proposal.risk_class)}`,
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
  const proposal = entry.semantic_proposal || {};
  return [
    "label: Human Request - explicit local input only",
    "authority: request context does not approve, dispatch, or execute",
    `request_text: ${compactValue(proposal.human_request || request.request_text)}`,
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

function riskLevel(entry) {
  const report = continuityReport(entry);
  const proposal = entry.semantic_proposal || {};
  if (statusValue(entry) === "BLOCKED" || report.aggregate_governance_status === "CONTINUITY_BOUNDARY_VIOLATION") {
    return "BOUNDARY_REVIEW";
  }
  if (proposal.risk_class) {
    return String(proposal.risk_class).toUpperCase();
  }
  return "LOW";
}

function currentMode(entry) {
  const proposal = entry.semantic_proposal || {};
  if (proposal.proposed_mode) {
    return proposal.proposed_mode;
  }
  return "READ_ONLY";
}

function executiveOperationalSummary(entry) {
  const report = continuityReport(entry);
  const continuityStatus = report.aggregate_governance_status === "CONTINUITY_BOUNDARY_VIOLATION"
    ? "BOUNDARY_REVIEW"
    : report.aggregate_governance_status ? "VALID" : "UNKNOWN";
  return [
    "SYSTEM STATUS: STABLE",
    `CONTINUITY STATUS: ${continuityStatus}`,
    "REPLAY STATUS: PRESERVED",
    "LIFECYCLE STATUS: READ_ONLY",
    "BOUNDARY STATUS: PRESERVED",
    `RISK LEVEL: ${riskLevel(entry)}`,
    `CURRENT MODE: ${currentMode(entry)}`,
    "AUTHORITY: VISIBILITY_ONLY_NOT_APPROVAL_DISPATCH_EXECUTION_OR_CONTINUATION"
  ].join("\n");
}

function operationalNarrative(entry) {
  const report = continuityReport(entry);
  const hasReport = Boolean(report.aggregate_governance_status);
  const violations = ((report.authority_boundary_summary || {}).violations || []).length;
  const replayVisible = (report.replay_visibility_summary || {}).visible === true;
  const lifecycleVisible = (report.lifecycle_visibility_summary || {}).visible === true;
  return [
    hasReport ? "Governance continuity is stable." : "Governance continuity has not been rendered yet.",
    replayVisible ? "Replay visibility is preserved." : "Replay visibility is awaiting an explicit local entry.",
    violations ? "Authority findings require review." : "No authority violations detected.",
    lifecycleVisible ? "Lifecycle visibility remains read-only." : "Lifecycle visibility remains read-only and awaits rendered evidence.",
    "This summary is non-authoritative and never implies execution readiness."
  ].join("\n");
}

function artifactJson(value) {
  return JSON.stringify(canonicalize(value || {}), null, 2);
}

function replaySummaryArtifact(entry) {
  const report = continuityReport(entry);
  const envelope = (entry.artifacts && entry.artifacts.envelope) || {};
  return {
    label: "Replay Summary Artifact - read-only inspection",
    authority: "inspection creates no dispatch, approval, execution, or replay mutation",
    replay_refs: envelope.replay_refs || [],
    replay_visibility_summary: report.replay_visibility_summary || {},
    replay_lifecycle_visibility: sidepanelContinuityRendering(entry).replay_lifecycle_visibility || {}
  };
}

function lifecycleSummaryArtifact(entry) {
  const report = continuityReport(entry);
  const envelope = (entry.artifacts && entry.artifacts.envelope) || {};
  return {
    label: "Lifecycle Summary Artifact - read-only inspection",
    authority: "inspection creates no lifecycle transition",
    lifecycle_refs: envelope.lifecycle_refs || [],
    lifecycle_visibility_summary: report.lifecycle_visibility_summary || {}
  };
}

function lineageSummaryArtifact(entry) {
  const envelope = (entry.artifacts && entry.artifacts.envelope) || {};
  const report = continuityReport(entry);
  const rendering = sidepanelContinuityRendering(entry);
  return {
    label: "Lineage Summary Artifact - read-only inspection",
    mutation: false,
    lineage_id: envelope.lineage_id || "unknown",
    lineage_summary: rendering.lineage_summary || report.lineage_summary || {}
  };
}

function authorityBoundaryArtifact(entry) {
  const envelope = (entry.artifacts && entry.artifacts.envelope) || {};
  const report = continuityReport(entry);
  const rendering = sidepanelContinuityRendering(entry);
  return {
    label: "Authority Boundary Artifact - read-only inspection",
    authority_boundary_statement: envelope.authority_boundary_statement || "No authority boundary statement rendered.",
    authority_boundary_summary: rendering.authority_boundary_visibility || report.authority_boundary_summary || {},
    guarantees: entry.authority_guarantees || {}
  };
}

function semanticBoundaryArtifact(entry) {
  const envelope = (entry.artifacts && entry.artifacts.envelope) || {};
  const report = continuityReport(entry);
  const rendering = sidepanelContinuityRendering(entry);
  return {
    label: "Semantic Boundary Artifact - read-only inspection",
    semantic_interpretation_boundary: envelope.semantic_interpretation_boundary || {},
    semantic_boundary_summary: rendering.semantic_boundary_visibility || report.semantic_boundary_summary || {}
  };
}

function semanticProposalArtifact(entry) {
  return {
    label: "Semantic Proposal Artifact - read-only import",
    proposal: entry.semantic_proposal || {},
    validation: entry.semantic_proposal_validation || {},
    authority: "proposal import creates no provider call, approval, dispatch, execution, or continuation authority",
    persistence: "in-memory sidepanel-local only"
  };
}

function semanticProposalValidationSummary(entry) {
  const validation = entry.semantic_proposal_validation || {};
  return [
    "label: Semantic Proposal Validation Status - deterministic local validation",
    "authority: accepted proposal is not approval, dispatch, execution, or continuation",
    `status: ${compactValue(validation.status)}`,
    `proposal_id: ${compactValue(validation.proposal_id)}`,
    `errors: ${compactValue(validation.errors)}`,
    `proposed_mode: ${compactValue(validation.proposed_mode)}`
  ].join("\n");
}

function validateSemanticProposalShape(proposal) {
  const errors = [];
  if (!proposal || typeof proposal !== "object" || Array.isArray(proposal)) {
    return ["proposal must be a JSON object"];
  }
  REQUIRED_SEMANTIC_PROPOSAL_FIELDS.forEach((field) => {
    if (typeof proposal[field] !== "string" || proposal[field].trim() === "") {
      errors.push(`missing required field: ${field}`);
    }
  });
  return errors;
}

function containsClaim(text, token, denialTokens) {
  return text.includes(token) && !denialTokens.some((denial) => text.includes(denial));
}

function validateSemanticProposalAuthority(proposal) {
  const mode = String(proposal.proposed_mode || "").trim();
  const claimText = [
    proposal.requested_action_type,
    proposal.authority_boundary_statement,
    proposal.semantic_boundary_statement,
    proposal.semantic_intent
  ].join(" ").toLowerCase();
  const errors = [];
  if (!ALLOWED_SEMANTIC_PROPOSAL_MODES.includes(mode)) {
    errors.push(`unsupported proposed_mode: ${mode || "unknown"}`);
  }
  if (REJECTED_SEMANTIC_PROPOSAL_MODES.includes(mode)) {
    errors.push(`rejected proposed_mode: ${mode}`);
  }
  if (
    containsClaim(claimText, "execute", ["no execute", "not execute", "without execution"]) ||
    containsClaim(claimText, "execution authority", ["no execution authority", "not execution authority"])
  ) {
    errors.push("implicit execution authority claim rejected");
  }
  if (containsClaim(claimText, "provider", ["no provider", "without provider"]) || claimText.includes("codex dispatch")) {
    errors.push("provider execution claim rejected");
  }
  if (containsClaim(claimText, "orchestration", ["no orchestration", "without orchestration"])) {
    errors.push("orchestration claim rejected");
  }
  if (
    containsClaim(claimText, "autonomous", ["no autonomous", "not autonomous", "without autonomous"]) ||
    containsClaim(claimText, "continuation authority", ["no continuation authority", "not continuation authority"])
  ) {
    errors.push("continuation authority claim rejected");
  }
  return errors;
}

function parseSemanticProposal(rawText) {
  try {
    return { proposal: JSON.parse(rawText) };
  } catch (error) {
    return { errors: ["invalid JSON"] };
  }
}

function validateSemanticProposal(rawText) {
  const parsed = parseSemanticProposal(rawText);
  if (parsed.errors) {
    return { status: "REJECTED", errors: parsed.errors, proposal: {} };
  }
  const proposal = canonicalize(parsed.proposal);
  const errors = validateSemanticProposalShape(proposal).concat(validateSemanticProposalAuthority(proposal));
  const proposalId = deterministicId("SEMANTIC-PROPOSAL", proposal);
  return {
    status: errors.length ? "REJECTED" : "ACCEPTED",
    proposal_id: proposalId,
    proposed_mode: proposal.proposed_mode || "unknown",
    errors,
    proposal
  };
}

function semanticProposalBlockedResult(validation) {
  return {
    demo_id: "CHATGPT_SEMANTIC_PROPOSAL_IMPORT_V1",
    status: "BLOCKED",
    semantic_proposal_validation: canonicalize(validation),
    semantic_proposal: validation.proposal || {},
    boundary_guarantees: {
      automatic_dispatch: false,
      hidden_execution: false,
      hidden_persistence: false
    },
    continuity_report: {
      aggregate_governance_status: "CONTINUITY_BOUNDARY_VIOLATION",
      continuity_findings: validation.errors || [],
      continuity_risks: ["Semantic proposal rejected before continuity flow generation."],
      continuity_recommendations: ["Revise proposal fields and keep mode READ_ONLY, REVIEW_ONLY, or DEMO_ONLY."]
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

function runSemanticProposalContinuityFlow(validation) {
  const proposal = validation.proposal;
  const result = runMinimalGovernedOperationalLoopDemo(proposal.human_request);
  const envelope = result.artifacts.envelope;
  envelope.semantic_proposal_ref = validation.proposal_id;
  envelope.semantic_interpretation_boundary.statement = proposal.semantic_boundary_statement;
  envelope.authority_boundary_statement = proposal.authority_boundary_statement;
  result.demo_id = "CHATGPT_SEMANTIC_PROPOSAL_IMPORT_V1";
  result.semantic_proposal_validation = {
    status: validation.status,
    proposal_id: validation.proposal_id,
    proposed_mode: validation.proposed_mode,
    errors: []
  };
  result.semantic_proposal = proposal;
  result.continuity_report.continuity_findings = [
    `Semantic proposal accepted in ${proposal.proposed_mode} mode.`
  ];
  result.continuity_report.continuity_risks = [
    "Semantic cognition remains non-deterministic and non-authoritative."
  ];
  result.continuity_report.continuity_recommendations = [
    "Review continuity evidence before any separate governed action."
  ];
  return canonicalize(result);
}

function importSemanticProposalFromSidepanel() {
  const proposalInput = document.getElementById("chatgpt-semantic-proposal");
  const validation = validateSemanticProposal(proposalInput ? proposalInput.value : "");
  const result = validation.status === "ACCEPTED"
    ? runSemanticProposalContinuityFlow(validation)
    : semanticProposalBlockedResult(validation);
  window.sidepanelRenderResult(result);
}

function replaySessionEntry(summary, index) {
  const entry = canonicalize(summary);
  const report = continuityReport(entry);
  const lineage = lineageSummaryArtifact(entry);
  return canonicalize({
    replay_entry_id: deterministicId("REPLAY-ENTRY", {
      sequence: index + 1,
      continuity_report_id: report.continuity_report_id || "unknown",
      lineage_id: lineage.lineage_id
    }),
    sequence: index + 1,
    status: statusValue(entry),
    continuity_report: report,
    replay_summary: replaySummaryArtifact(entry),
    lifecycle_summary: lifecycleSummaryArtifact(entry),
    lineage_summary: lineage,
    authority_boundary_summary: authorityBoundaryArtifact(entry),
    semantic_boundary_summary: semanticBoundaryArtifact(entry)
  });
}

function replaySessionSummary() {
  return artifactJson({
    replay_session_id: REPLAY_SESSION_ID,
    persistence_scope: "bounded in-memory session visibility",
    durable_storage: false,
    entry_count: replaySessionEntries.length,
    serialization: "canonical JSON through canonicalize",
    append_only: true,
    rewrite: false,
    repair: false,
    explicit_load_required: true,
    authority: "replay visibility creates no provider call, dispatch, approval, execution, or continuation"
  });
}

function loadedReplayInspection() {
  return artifactJson({
    replay_session_id: REPLAY_SESSION_ID,
    label: "Loaded Replay Entry Inspection - read-only",
    entries: replaySessionEntries,
    mutation: false,
    rewrite: false,
    repair: false,
    durable_storage: false
  });
}

function renderReplaySessionVisibility() {
  setCockpitText(COCKPIT_IDS.currentReplaySession, replaySessionSummary());
}

function loadReplaySession() {
  renderReplaySessionVisibility();
  setCockpitText(COCKPIT_IDS.replayEntryInspection, loadedReplayInspection());
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
  setCockpitText(COCKPIT_IDS.executiveOperationalSummary, executiveOperationalSummary(latest));
  setCockpitText(COCKPIT_IDS.operationalNarrative, operationalNarrative(latest));
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
  setCockpitText(COCKPIT_IDS.envelopeValidationArtifact, artifactJson(latest.envelope_validation_report));
  setCockpitText(COCKPIT_IDS.validatorCompositionArtifact, artifactJson(latest.validator_composition_report));
  setCockpitText(COCKPIT_IDS.continuityReportArtifact, artifactJson(continuityReport(latest)));
  setCockpitText(COCKPIT_IDS.replaySummaryArtifact, artifactJson(replaySummaryArtifact(latest)));
  setCockpitText(COCKPIT_IDS.lifecycleSummaryArtifact, artifactJson(lifecycleSummaryArtifact(latest)));
  setCockpitText(COCKPIT_IDS.lineageSummaryArtifact, artifactJson(lineageSummaryArtifact(latest)));
  setCockpitText(COCKPIT_IDS.authorityBoundaryArtifact, artifactJson(authorityBoundaryArtifact(latest)));
  setCockpitText(COCKPIT_IDS.semanticBoundaryArtifact, artifactJson(semanticBoundaryArtifact(latest)));
  setCockpitText(COCKPIT_IDS.semanticProposalValidationStatus, semanticProposalValidationSummary(latest));
  setCockpitText(COCKPIT_IDS.semanticProposalArtifact, artifactJson(semanticProposalArtifact(latest)));
  renderReplaySessionVisibility();
}

window.sidepanelRenderResult = function renderLifecycleResult(summary) {
  const canonicalSummary = canonicalize(summary);
  lifecycleEntries.push(canonicalize(summary));
  replaySessionEntries.push(replaySessionEntry(canonicalSummary, replaySessionEntries.length));

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

const loadReplayButton = document.getElementById("load-replay-session");
if (loadReplayButton) {
  loadReplayButton.onclick = loadReplaySession;
}

const importSemanticProposalButton = document.getElementById("import-semantic-proposal");
if (importSemanticProposalButton) {
  importSemanticProposalButton.onclick = importSemanticProposalFromSidepanel;
}
