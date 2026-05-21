const lifecycleEntries = [];
const replaySessionEntries = [];
const REPLAY_SESSION_ID = "PERSISTENT_REPLAY_SESSION_V1";
const LOCAL_GOVERNED_TRANSPORT_SESSION_ID = "LOCAL-GOVERNED-TRANSPORT-SESSION-V1";
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
const ALLOWED_LOCAL_TRANSPORT_ACTION_TYPES = ["READ_ONLY", "REVIEW_ONLY", "DEMO_ONLY", "OBSERVE_ONLY", "OBSERVE_CONTINUITY_ONLY"];
const CHAT_FIRST_AUTHORITY_BOUNDARY_STATEMENT = "SEMANTIC_TRANSPORT_ONLY_NO_APPROVAL_NO_DISPATCH_NO_EXECUTION; Chat-first normalization creates no provider calls, no approval, no dispatch, no execution, no orchestration, and no autonomous continuation.";
const CHAT_FIRST_SEMANTIC_BOUNDARY_STATEMENT = "SEMANTIC_COGNITION_NON_AUTHORITATIVE; deterministic normalization preserves request text as bounded semantic context only and does not infer execution authority.";
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
  semanticProposalHashVerificationStatus: "semantic-proposal-hash-verification-status",
  semanticProposalArtifact: "semantic-proposal-artifact",
  localTransportRuntimeStatus: "local-transport-runtime-status",
  chatFirstResultCard: "chat-first-result-card",
  latestActionResultCard: "latest-action-result-card",
  operatorEventStream: "operator-event-stream",
  governanceChatReturn: "governance-chat-return",
  endToEndBridgeLifecycle: "end-to-end-bridge-lifecycle"
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
    if ("value" in node) {
      node.value = value;
    } else {
      node.textContent = value;
    }
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
    hash_verification: entry.semantic_proposal_hash_verification || {},
    authority: "proposal import creates no provider call, approval, dispatch, execution, or continuation authority",
    persistence: "in-memory sidepanel-local only"
  };
}

function localTransportRuntimeSummary(entry) {
  const report = entry.local_governed_transport_report || {};
  const event = report.transport_event || {};
  return [
    "label: Local Governed Transport Runtime - explicit operator-trigger only",
    "runtime: pure local handler invocation only",
    "endpoint: none",
    "server_listener: false",
    `transport_status: ${compactValue(report.status)}`,
    `replay_event_id: ${compactValue(report.replay_event_id || event.replay_event_id)}`,
    `session_id: ${compactValue(report.session_id || event.session_id)}`,
    `proposal_id: ${compactValue(report.proposal_id || event.proposal_id)}`,
    `authority_label: ${compactValue(report.authority_label || event.authority_label)}`,
    `hash_status: ${compactValue(report.hash_verification_status || event.hash_verification_status)}`,
    `rejection_reason: ${compactValue(report.rejection_reason || event.rejection_reason)}`,
    `compact_rejection: ${compactValue(report.compact_rejection)}`,
    `append_candidate: ${compactValue(event.visibility_scope)}`,
    `non_authority_guarantees: ${compactValue(report.non_authority_guarantees)}`
  ].join("\n");
}

function chatFirstResultCardSummary(entry) {
  const flow = entry.chat_first_flow || {};
  const report = entry.local_governed_transport_report || flow.transport_report || {};
  const accepted = report.status === "TRANSPORT_ACCEPTED";
  return [
    `RESULT: ${accepted ? "ACCEPTED" : flow.status || "not run"}`,
    `reason: ${compactValue(report.rejection_reason || flow.reason || "transport accepted for visibility")}`,
    `session_id: ${compactValue(report.session_id || flow.session_id)}`,
    `proposal_id: ${compactValue(report.proposal_id || flow.proposal_id)}`,
    `replay_event_id: ${compactValue(report.replay_event_id)}`,
    `integrity_status: ${compactValue(report.hash_verification_status)}`,
    "authority_scope: SEMANTIC_TRANSPORT_ONLY",
    "note: no execution, no dispatch, no approval",
    `non_authority_guarantees: ${compactValue(report.non_authority_guarantees)}`
  ].join("\n");
}

function latestTransportReport(entry) {
  const flow = entry.chat_first_flow || {};
  return entry.local_governed_transport_report || flow.transport_report || {};
}

function latestProposal(entry) {
  return entry.semantic_proposal || {};
}

function latestActionAccepted(entry) {
  return latestTransportReport(entry).status === "TRANSPORT_ACCEPTED";
}

function latestActionMode(entry) {
  const flow = entry.chat_first_flow || {};
  const proposal = latestProposal(entry);
  return compactValue(flow.requested_mode || proposal.proposed_mode || "REVIEW_ONLY");
}

function latestActionReason(entry) {
  const report = latestTransportReport(entry);
  const flow = entry.chat_first_flow || {};
  return compactValue(report.rejection_reason || flow.reason || "transport accepted for visibility");
}

function latestIntegrityStatus(entry) {
  const report = latestTransportReport(entry);
  const verification = entry.semantic_proposal_hash_verification || {};
  return compactValue(report.hash_verification_status || verification.status || "not verified");
}

function latestReplayStatus(entry) {
  const report = latestTransportReport(entry);
  if (report.status === "TRANSPORT_ACCEPTED") {
    return "SESSION_LOCAL_APPEND_CANDIDATE";
  }
  if (report.replay_event_id) {
    return "SESSION_LOCAL_REJECTED_EVENT_VISIBLE";
  }
  return "SESSION_LOCAL_VISIBILITY_ONLY";
}

function latestActionResultCardSummary(entry) {
  const report = latestTransportReport(entry);
  if (!report.status) {
    return [
      "No governed operator action has run.",
      "Authority: SEMANTIC_TRANSPORT_ONLY",
      "No execution occurred."
    ].join("\n");
  }
  if (latestActionAccepted(entry)) {
    return [
      "Governed transport accepted",
      `Mode: ${latestActionMode(entry)}`,
      `Integrity: ${latestIntegrityStatus(entry) === "HASH_VERIFIED" ? "VERIFIED" : latestIntegrityStatus(entry)}`,
      `Replay: ${latestReplayStatus(entry)}`,
      "Authority: SEMANTIC_TRANSPORT_ONLY",
      "No execution occurred.",
      "No provider invoked."
    ].join("\n");
  }
  return [
    "Governed transport rejected",
    `Reason: ${latestActionReason(entry)}`,
    `Mode: ${latestActionMode(entry)}`,
    `Integrity: ${latestIntegrityStatus(entry)}`,
    "Authority: SEMANTIC_TRANSPORT_ONLY",
    "No execution occurred.",
    "No provider invoked."
  ].join("\n");
}

function operatorEventLine(sequence, status, label, reason) {
  const suffix = reason ? ` - ${reason}` : "";
  return `${String(sequence).padStart(3, "0")} ${status} ${label}${suffix}`;
}

function operatorEventStreamSummary(entry) {
  const report = latestTransportReport(entry);
  const flow = entry.chat_first_flow || {};
  if (!report.status && !flow.status) {
    return operatorEventLine(1, "INFO", "Awaiting explicit operator action.");
  }
  const accepted = report.status === "TRANSPORT_ACCEPTED";
  const rejected = !accepted;
  const reason = rejected ? latestActionReason(entry) : "";
  const hashStatus = report.hash_verification_status || "HASH_NOT_VERIFIED";
  const hashOk = hashStatus === "HASH_VERIFIED";
  const validationOk = !rejected || !["TRANSPORT_REJECTED_SCHEMA", "TRANSPORT_REJECTED_UNSAFE_MODE", "TRANSPORT_REJECTED_AUTHORITY"].includes(report.status);
  const envelopeOk = !rejected || !["TRANSPORT_REJECTED_SCHEMA"].includes(report.status);
  const attachOk = accepted;
  const replayOk = Boolean(report.replay_event_id);
  const finalLabel = accepted ? "Governed transport accepted" : "Governed transport rejected";

  return [
    operatorEventLine(1, "INFO", "Human request received"),
    operatorEventLine(2, flow.status === "REJECTED" ? "BLOCKED" : "SUCCESS", "Semantic proposal normalized", flow.status === "REJECTED" ? reason : ""),
    operatorEventLine(3, validationOk ? "SUCCESS" : "REJECTED", "Semantic proposal validated", validationOk ? "" : reason),
    operatorEventLine(4, hashOk ? "SUCCESS" : "BLOCKED", "Hash verified", hashOk ? "" : hashStatus),
    operatorEventLine(5, envelopeOk ? "SUCCESS" : "BLOCKED", "Transport envelope prepared", envelopeOk ? "" : reason),
    operatorEventLine(6, attachOk ? "SUCCESS" : "BLOCKED", "Governed transport attached", attachOk ? "" : reason),
    operatorEventLine(7, replayOk ? "SUCCESS" : "BLOCKED", "Replay append candidate created", replayOk ? "" : "no append candidate"),
    operatorEventLine(8, accepted ? "SUCCESS" : "REJECTED", finalLabel, accepted ? "" : reason)
  ].join("\n");
}

function governanceChatReturnSummary(entry) {
  const report = latestTransportReport(entry);
  if (entry.governed_chat_return && entry.demo_id === "MINIMAL_END_TO_END_BRIDGE_SIDEPANEL_ATTACHMENT_V1") {
    const bridgeReturn = entry.governed_chat_return;
    return [
      `Governed bridge ${String(bridgeReturn.status || "UNKNOWN").toLowerCase()}`,
      "",
      `Reason: ${compactValue(bridgeReturn.reason)}`,
      `Replay: ${compactValue(bridgeReturn.replay_visibility)}`,
      `Next: ${compactValue(bridgeReturn.next_recommended_step)}`,
      "",
      bridgeReturn.non_authority_reminder || "No execution occurred. No provider invoked."
    ].join("\n");
  }
  if (!report.status) {
    return [
      "Governed transport has not run.",
      "",
      "Authority: SEMANTIC_TRANSPORT_ONLY",
      "No execution occurred.",
      "No provider invoked."
    ].join("\n");
  }
  if (latestActionAccepted(entry)) {
    return [
      "Governed transport accepted",
      "",
      `Mode: ${latestActionMode(entry)}`,
      `Integrity: ${latestIntegrityStatus(entry) === "HASH_VERIFIED" ? "VERIFIED" : latestIntegrityStatus(entry)}`,
      `Replay: ${latestReplayStatus(entry)}`,
      "Authority: SEMANTIC_TRANSPORT_ONLY",
      "",
      "No execution occurred.",
      "No provider invoked."
    ].join("\n");
  }
  return [
    "Governed transport rejected",
    "",
    `Reason: ${latestActionReason(entry)}`,
    `Mode: ${latestActionMode(entry)}`,
    `Integrity: ${latestIntegrityStatus(entry)}`,
    "Authority: SEMANTIC_TRANSPORT_ONLY",
    "",
    "No execution occurred.",
    "No provider invoked."
  ].join("\n");
}

function endToEndBridgeLifecycleSummary(entry) {
  const bridge = entry.end_to_end_bridge || {};
  const taskPackage = entry.task_package || {};
  const mockResult = entry.mock_codex_result || {};
  const resultValidation = entry.result_validation || {};
  const governedReturn = entry.governed_chat_return || {};
  const replayIds = (entry.replay_events || []).map((event) => event.replay_event_id).join(", ") || "none";
  const proposal = latestProposal(entry);
  return [
    `STATUS: ${compactValue(bridge.status || entry.status)}`,
    `HUMAN REQUEST: ${compactValue(proposal.human_request || bridge.human_request)}`,
    `SEMANTIC PROPOSAL: ${compactValue(entry.proposal_id || proposal.proposal_id)}`,
    `GOVERNED TRANSPORT STATUS: ${compactValue(entry.transport_status || latestTransportReport(entry).status)}`,
    `GOVERNED TASK PACKAGE: ${compactValue(taskPackage.task_id)}`,
    `MOCK CODEX RESULT: ${compactValue(mockResult.status)}`,
    `RESULT VALIDATION: ${compactValue(resultValidation.status)}`,
    `GOVERNED CHAT RETURN: ${compactValue(governedReturn.status)} - ${compactValue(governedReturn.reason)}`,
    `RECOMMENDED NEXT STEP: ${compactValue(governedReturn.next_recommended_step)}`,
    `SESSION: ${compactValue(entry.session_id || bridge.session_id)}`,
    `REPLAY EVENT IDS: ${replayIds}`,
    `REJECTION REASON: ${compactValue(governedReturn.status === "REJECTED" ? governedReturn.reason : "")}`,
    "AUTHORITY: ChatGPT advisory cognition only; AiGOL governance authority; Codex mocked bounded provider only.",
    "NO REAL EXECUTION",
    "NO PROVIDER CALLS",
    "NO AUTONOMOUS CONTINUATION"
  ].join("\n");
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

function semanticProposalHashVerificationSummary(entry) {
  const verification = entry.semantic_proposal_hash_verification || {};
  return [
    "label: Semantic Proposal Hash Verification - replay-safe artifact integrity",
    "authority: HASH VERIFIED is not approval, dispatch, execution, or continuation",
    `status: ${compactValue(verification.status)}`,
    `artifact_hash: ${compactValue(verification.artifact_hash)}`,
    `computed_hash: ${compactValue(verification.computed_hash)}`,
    `artifact_identity: ${compactValue(verification.artifact_identity)}`,
    `errors: ${compactValue(verification.errors)}`
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
    containsClaim(claimText, "execution authority", [
      "no execution authority",
      "not execution authority",
      "does not create governance decisions or execution authority",
      "grants no approval, dispatch, execution"
    ])
  ) {
    errors.push("implicit execution authority claim rejected");
  }
  if (
    containsClaim(claimText, "provider", ["no provider", "without provider", "providers are not invoked", "provider calls: false"]) ||
    claimText.includes("codex dispatch")
  ) {
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

function semanticProposalHashInput(proposal) {
  const canonicalProposal = canonicalize(proposal);
  const { artifact_hash: artifactHash, ...hashInput } = canonicalProposal;
  return hashInput;
}

async function semanticProposalArtifactHash(proposal) {
  const bytes = new TextEncoder().encode(JSON.stringify(semanticProposalHashInput(proposal)));
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  return `sha256:${Array.from(new Uint8Array(digest))
    .map((byte) => byte.toString(16).padStart(2, "0"))
    .join("")}`;
}

async function verifySemanticProposalArtifactHash(proposal) {
  if (!proposal || typeof proposal !== "object" || Array.isArray(proposal)) {
    return canonicalize({
      status: "HASH_INVALID",
      errors: ["malformed canonical structure"],
      artifact_hash: "unknown",
      computed_hash: "not_computed",
      artifact_identity: "unknown",
      replay_safe_integrity: false
    });
  }
  const artifactHash = proposal.artifact_hash;
  const artifactIdentity = proposal.transport_artifact_id || proposal.proposal_id || "unknown";
  if (typeof artifactHash !== "string" || artifactHash.trim() === "") {
    return canonicalize({
      status: "HASH_MISSING",
      errors: ["missing artifact_hash"],
      artifact_hash: "missing",
      computed_hash: "not_computed",
      artifact_identity: artifactIdentity,
      replay_safe_integrity: false
    });
  }
  if (!/^sha256:[0-9a-f]{64}$/.test(artifactHash)) {
    return canonicalize({
      status: "HASH_INVALID",
      errors: ["malformed artifact_hash"],
      artifact_hash: artifactHash,
      computed_hash: "not_computed",
      artifact_identity: artifactIdentity,
      replay_safe_integrity: false
    });
  }
  const computedHash = await semanticProposalArtifactHash(proposal);
  if (computedHash !== artifactHash) {
    return canonicalize({
      status: "HASH_MISMATCH",
      errors: ["artifact_hash mismatch"],
      artifact_hash: artifactHash,
      computed_hash: computedHash,
      artifact_identity: artifactIdentity,
      replay_safe_integrity: false
    });
  }
  return canonicalize({
    status: "HASH_VERIFIED",
    errors: [],
    artifact_hash: artifactHash,
    computed_hash: computedHash,
    artifact_identity: artifactIdentity,
    replay_safe_integrity: true
  });
}

function normalizeHumanRequestToSemanticProposal({ human_request, requested_mode = "REVIEW_ONLY", proposal_id = null, session_id = null }) {
  const requestText = String(human_request || "").trim();
  const mode = String(requested_mode || "").trim().toUpperCase();
  if (!requestText) {
    return { error: "human_request is required" };
  }
  if (!ALLOWED_SEMANTIC_PROPOSAL_MODES.includes(mode) || REJECTED_SEMANTIC_PROPOSAL_MODES.includes(mode)) {
    return { error: `unsafe requested_mode: ${mode || "UNKNOWN"}` };
  }
  const generatedProposalId = proposal_id || deterministicId("CHAT-FIRST-PROPOSAL", {
    human_request: requestText,
    requested_mode: mode
  });
  const proposal = canonicalize({
    human_request: requestText,
    semantic_intent: `Review bounded semantic direction for: ${requestText}`,
    proposed_mode: mode,
    risk_class: "LOW",
    authority_boundary_statement: CHAT_FIRST_AUTHORITY_BOUNDARY_STATEMENT,
    semantic_boundary_statement: CHAT_FIRST_SEMANTIC_BOUNDARY_STATEMENT,
    requested_action_type: mode,
    proposal_id: generatedProposalId,
    ...(session_id ? { session_id } : {})
  });
  return canonicalize({
    ...proposal,
    artifact_hash: deterministicChatFirstArtifactHash(proposal)
  });
}

function deterministicChatFirstArtifactHash(proposal) {
  return `sha256:${deterministicId("CHAT-FIRST-HASH", semanticProposalHashInput(proposal))
    .slice("CHAT-FIRST-HASH-".length)
    .padStart(64, "0")}`;
}

function prepareChatFirstTransportEnvelope({ human_request, session_id, requested_mode = "REVIEW_ONLY" }) {
  const sessionText = String(session_id || "").trim();
  if (!sessionText) {
    return { error: "session_id is required" };
  }
  const proposal = normalizeHumanRequestToSemanticProposal({
    human_request,
    requested_mode,
    session_id: sessionText
  });
  if (proposal.error) {
    return { error: proposal.error };
  }
  return canonicalize({
    transport_id: deterministicId("CHAT-FIRST-TRANSPORT", {
      proposal_id: proposal.proposal_id,
      session_id: sessionText
    }),
    session_id: sessionText,
    proposal_id: proposal.proposal_id,
    artifact_hash: proposal.artifact_hash,
    created_at_policy: "DETERMINISTIC_CHAT_FIRST_NORMALIZATION",
    source_label: "CHAT_FIRST_LOCAL_NORMALIZATION",
    semantic_proposal: proposal,
    authority_boundary_statement: "Semantic transport only; transport success is not approval, not dispatch, not execution, and not continuation authority.",
    replay_policy: {
      append_only: true,
      visibility_only: true,
      rewrite_allowed: false,
      repair_allowed: false,
      mutation_allowed: false,
      inference_allowed: false,
      durable_backend: false
    },
    lifecycle_policy: {
      visibility_only: true,
      execution_transition: false,
      mutation_allowed: false
    }
  });
}

function localTransportRequiredEnvelopeFields() {
  return [
    "transport_id",
    "session_id",
    "proposal_id",
    "artifact_hash",
    "created_at_policy",
    "source_label",
    "semantic_proposal",
    "authority_boundary_statement",
    "replay_policy",
    "lifecycle_policy"
  ];
}

function compactLocalTransportRejection(status) {
  const labels = {
    TRANSPORT_REJECTED_SCHEMA: "SCHEMA_REJECTED",
    TRANSPORT_REJECTED_HASH: "HASH_MISMATCH",
    TRANSPORT_REJECTED_SESSION: "UNKNOWN_SESSION",
    TRANSPORT_REJECTED_AUTHORITY: "AUTHORITY_REJECTED",
    TRANSPORT_REJECTED_UNSAFE_MODE: "UNSAFE_MODE",
    TRANSPORT_REJECTED_REPLAY_POLICY: "REPLAY_POLICY_REJECTED"
  };
  return labels[status] || "SCHEMA_REJECTED";
}

function localTransportRejectedReport(envelope, status, rejectionReason, hashStatus) {
  const safeEnvelope = canonicalize(envelope || {});
  const eventSeed = {
    artifact_hash: safeEnvelope.artifact_hash || "UNKNOWN",
    created_at_policy: safeEnvelope.created_at_policy || "UNKNOWN",
    proposal_id: safeEnvelope.proposal_id || "UNKNOWN",
    session_id: safeEnvelope.session_id || "UNKNOWN",
    source_label: safeEnvelope.source_label || "UNKNOWN",
    transport_id: safeEnvelope.transport_id || "UNKNOWN",
    transport_status: status
  };
  const event = canonicalize({
    replay_event_id: deterministicId("TRANSPORT-REPLAY", eventSeed),
    event_type: "LOCAL_GOVERNED_SEMANTIC_TRANSPORT",
    transport_status: status,
    transport_id: safeEnvelope.transport_id || "UNKNOWN",
    session_id: safeEnvelope.session_id || "UNKNOWN",
    proposal_id: safeEnvelope.proposal_id || "UNKNOWN",
    artifact_hash: safeEnvelope.artifact_hash || "UNKNOWN",
    hash_verification_status: hashStatus || "HASH_NOT_VERIFIED",
    source_label: safeEnvelope.source_label || "UNKNOWN",
    authority_label: "SEMANTIC_TRANSPORT_ONLY",
    rejection_reason: rejectionReason,
    lineage_refs: {
      transport_id: safeEnvelope.transport_id || "UNKNOWN",
      session_id: safeEnvelope.session_id || "UNKNOWN",
      proposal_id: safeEnvelope.proposal_id || "UNKNOWN",
      artifact_hash: safeEnvelope.artifact_hash || "UNKNOWN"
    },
    visibility_scope: "SESSION_LOCAL_APPEND_CANDIDATE_ONLY",
    created_at_policy: safeEnvelope.created_at_policy || "UNKNOWN"
  });
  return canonicalize({
    status,
    transport_id: event.transport_id,
    session_id: event.session_id,
    proposal_id: event.proposal_id,
    replay_event_id: event.replay_event_id,
    hash_verification_status: event.hash_verification_status,
    authority_label: "SEMANTIC_TRANSPORT_ONLY",
    rejection_reason: rejectionReason,
    compact_rejection: compactLocalTransportRejection(status),
    validation: { valid: false, errors: [rejectionReason] },
    transport_event: event,
    operator_visibility: {
      transport_event_visible: true,
      session_attachment_visible: event.session_id !== "UNKNOWN",
      replay_event_id_visible: true,
      hash_verification_visible: true,
      authority_label_visible: true,
      rejection_reason_visible: true
    },
    non_authority_guarantees: [
      "SEMANTIC_TRANSPORT_ONLY",
      "SESSION_REPLAY_ONLY",
      "HASH_VERIFIED_IS_INTEGRITY_ONLY",
      "CERTIFIED_FOR_CONTINUITY_INGESTION_IS_NOT_APPROVAL",
      "CONTINUITY_VISIBLE_IS_NOT_EXECUTION_AUTHORIZATION"
    ]
  });
}

function localTransportSessionRegistry(sessionId) {
  if (sessionId !== LOCAL_GOVERNED_TRANSPORT_SESSION_ID) {
    return {};
  }
  return {
    [LOCAL_GOVERNED_TRANSPORT_SESSION_ID]: {
      operator_visible: true,
      ambiguous: false,
      continuation_requested: false,
      cross_session_mutation: false
    }
  };
}

function buildLocalGovernedTransportEnvelope(entry, sessionId) {
  const proposal = canonicalize(entry.semantic_proposal || {});
  const validation = entry.semantic_proposal_validation || {};
  const hashVerification = entry.semantic_proposal_hash_verification || {};
  return canonicalize({
    transport_id: deterministicId("LOCAL-TRANSPORT", {
      session_id: sessionId,
      proposal_id: validation.proposal_id || proposal.proposal_id || "UNKNOWN",
      artifact_hash: hashVerification.artifact_hash || proposal.artifact_hash || "UNKNOWN"
    }),
    session_id: sessionId,
    proposal_id: validation.proposal_id || proposal.proposal_id || "UNKNOWN",
    artifact_hash: hashVerification.artifact_hash || proposal.artifact_hash || "UNKNOWN",
    created_at_policy: "EXPLICIT_SIDE_PANEL_OPERATOR_TRIGGER",
    source_label: "CHATGPT_LOCAL_ARTIFACT",
    semantic_proposal: proposal,
    authority_boundary_statement: "Semantic transport only; transport success is not approval, not dispatch, not execution, and not continuation authority.",
    replay_policy: {
      append_only: true,
      visibility_only: true,
      rewrite_allowed: false,
      repair_allowed: false,
      mutation_allowed: false,
      inference_allowed: false,
      durable_backend: false
    },
    lifecycle_policy: {
      visibility_only: true,
      execution_transition: false,
      mutation_allowed: false
    }
  });
}

function localTransportEnvelopeSchemaError(envelope) {
  const missing = localTransportRequiredEnvelopeFields().filter((field) => !(field in envelope));
  if (missing.length) {
    return `missing required fields: ${missing.join(", ")}`;
  }
  if (!envelope.semantic_proposal || typeof envelope.semantic_proposal !== "object") {
    return "semantic_proposal must be an object";
  }
  return "";
}

function localTransportSessionError(sessionId, sessionRegistry) {
  const session = sessionRegistry[sessionId];
  if (!session) {
    return "session_id is missing or unknown";
  }
  if (session.operator_visible !== true) {
    return "session attachment is not operator-visible";
  }
  if (session.ambiguous === true || Array.isArray(session)) {
    return "session_id is ambiguous";
  }
  if (session.continuation_requested === true || session.cross_session_mutation === true) {
    return "session attachment violates bounded transport";
  }
  return "";
}

function localTransportUnsafeModeError(proposal) {
  const mode = proposal.proposed_mode || "UNKNOWN";
  if (!ALLOWED_SEMANTIC_PROPOSAL_MODES.includes(mode)) {
    return `unsafe proposed_mode: ${mode}`;
  }
  return "";
}

function localTransportAuthorityError(envelope) {
  const proposal = envelope.semantic_proposal || {};
  const requestedAction = proposal.requested_action_type || "";
  const authorityStatement = envelope.authority_boundary_statement || "";
  const required = ["not approval", "not dispatch", "not execution", "not continuation"];
  if (!required.every((token) => authorityStatement.toLowerCase().includes(token))) {
    return "authority boundary statement is incomplete";
  }
  if (!ALLOWED_LOCAL_TRANSPORT_ACTION_TYPES.includes(requestedAction)) {
    return "requested action type is outside semantic transport authority";
  }
  return "";
}

function localTransportReplayPolicyError(envelope) {
  const replayPolicy = envelope.replay_policy || {};
  const lifecyclePolicy = envelope.lifecycle_policy || {};
  if (replayPolicy.append_only !== true || replayPolicy.visibility_only !== true) {
    return "replay policy must be append-only visibility only";
  }
  if (
    replayPolicy.rewrite_allowed ||
    replayPolicy.repair_allowed ||
    replayPolicy.mutation_allowed ||
    replayPolicy.inference_allowed ||
    replayPolicy.durable_backend
  ) {
    return "replay policy violates bounded transport";
  }
  if (lifecyclePolicy.visibility_only !== true || lifecyclePolicy.execution_transition || lifecyclePolicy.mutation_allowed) {
    return "lifecycle policy violates bounded transport";
  }
  return "";
}

function handle_local_governed_transport({ envelope, session_registry }) {
  const safeEnvelope = canonicalize(envelope || {});
  const safeRegistry = canonicalize(session_registry || {});
  const schemaError = localTransportEnvelopeSchemaError(safeEnvelope);
  if (schemaError) {
    return localTransportRejectedReport(safeEnvelope, "TRANSPORT_REJECTED_SCHEMA", schemaError, "HASH_NOT_VERIFIED");
  }
  const sessionError = localTransportSessionError(safeEnvelope.session_id, safeRegistry);
  if (sessionError) {
    return localTransportRejectedReport(safeEnvelope, "TRANSPORT_REJECTED_SESSION", sessionError, "HASH_PENDING");
  }
  const unsafeModeError = localTransportUnsafeModeError(safeEnvelope.semantic_proposal);
  if (unsafeModeError) {
    return localTransportRejectedReport(safeEnvelope, "TRANSPORT_REJECTED_UNSAFE_MODE", unsafeModeError, "HASH_PENDING");
  }
  if (!/^sha256:[0-9a-f]{64}$/.test(safeEnvelope.artifact_hash)) {
    return localTransportRejectedReport(safeEnvelope, "TRANSPORT_REJECTED_HASH", "artifact_hash is missing or malformed", "HASH_INVALID");
  }
  const expectedHash = safeEnvelope.source_label === "CHAT_FIRST_LOCAL_NORMALIZATION"
    ? deterministicChatFirstArtifactHash(safeEnvelope.semantic_proposal)
    : safeEnvelope.semantic_proposal.artifact_hash;
  if (safeEnvelope.artifact_hash !== expectedHash) {
    return localTransportRejectedReport(safeEnvelope, "TRANSPORT_REJECTED_HASH", "artifact_hash mismatch", "HASH_MISMATCH");
  }
  const authorityError = localTransportAuthorityError(safeEnvelope);
  if (authorityError) {
    return localTransportRejectedReport(safeEnvelope, "TRANSPORT_REJECTED_AUTHORITY", authorityError, "HASH_VERIFIED");
  }
  const replayPolicyError = localTransportReplayPolicyError(safeEnvelope);
  if (replayPolicyError) {
    return localTransportRejectedReport(safeEnvelope, "TRANSPORT_REJECTED_REPLAY_POLICY", replayPolicyError, "HASH_VERIFIED");
  }
  const eventSeed = {
    artifact_hash: safeEnvelope.artifact_hash,
    created_at_policy: safeEnvelope.created_at_policy,
    proposal_id: safeEnvelope.proposal_id,
    session_id: safeEnvelope.session_id,
    source_label: safeEnvelope.source_label,
    transport_id: safeEnvelope.transport_id,
    transport_status: "TRANSPORT_ACCEPTED"
  };
  const event = canonicalize({
    replay_event_id: deterministicId("TRANSPORT-REPLAY", eventSeed),
    event_type: "LOCAL_GOVERNED_SEMANTIC_TRANSPORT",
    transport_status: "TRANSPORT_ACCEPTED",
    transport_id: safeEnvelope.transport_id,
    session_id: safeEnvelope.session_id,
    proposal_id: safeEnvelope.proposal_id,
    artifact_hash: safeEnvelope.artifact_hash,
    hash_verification_status: "HASH_VERIFIED",
    source_label: safeEnvelope.source_label,
    authority_label: "SEMANTIC_TRANSPORT_ONLY",
    rejection_reason: "",
    lineage_refs: {
      transport_id: safeEnvelope.transport_id,
      session_id: safeEnvelope.session_id,
      proposal_id: safeEnvelope.proposal_id,
      artifact_hash: safeEnvelope.artifact_hash
    },
    visibility_scope: "SESSION_LOCAL_APPEND_CANDIDATE_ONLY",
    created_at_policy: safeEnvelope.created_at_policy
  });
  return canonicalize({
    status: "TRANSPORT_ACCEPTED",
    transport_id: safeEnvelope.transport_id,
    session_id: safeEnvelope.session_id,
    proposal_id: safeEnvelope.proposal_id,
    replay_event_id: event.replay_event_id,
    hash_verification_status: "HASH_VERIFIED",
    authority_label: "SEMANTIC_TRANSPORT_ONLY",
    rejection_reason: "",
    compact_rejection: "",
    validation: { valid: true, errors: [] },
    transport_event: event,
    operator_visibility: {
      transport_event_visible: true,
      session_attachment_visible: true,
      replay_event_id_visible: true,
      hash_verification_visible: true,
      authority_label_visible: true,
      rejection_reason_visible: false
    },
    non_authority_guarantees: [
      "SEMANTIC_TRANSPORT_ONLY",
      "SESSION_REPLAY_ONLY",
      "HASH_VERIFIED_IS_INTEGRITY_ONLY",
      "CERTIFIED_FOR_CONTINUITY_INGESTION_IS_NOT_APPROVAL",
      "CONTINUITY_VISIBLE_IS_NOT_EXECUTION_AUTHORIZATION"
    ]
  });
}

async function localSemanticProposalFileValidation(rawText, fileName) {
  const validation = validateSemanticProposal(rawText);
  const errors = [...validation.errors];
  if (fileName !== "semantic_proposal.json") {
    errors.push("semantic proposal file must be named semantic_proposal.json");
  }
  const hashVerification = await verifySemanticProposalArtifactHash(validation.proposal);
  if (hashVerification.status !== "HASH_VERIFIED") {
    errors.push(...hashVerification.errors);
  }
  return canonicalize({
    ...validation,
    status: errors.length ? "REJECTED" : validation.status,
    errors,
    hash_verification: hashVerification,
    import_source: "explicit local semantic_proposal.json file selection",
    file_name: fileName || "unknown",
    file_persisted: false,
    durable_storage: false,
    hidden_persistence: false
  });
}

function missingSemanticProposalFileValidation() {
  return canonicalize({
    status: "REJECTED",
    errors: ["missing semantic_proposal.json file selection"],
    proposal: {},
    hash_verification: {
      status: "HASH_MISSING",
      errors: ["missing semantic_proposal.json file selection"],
      artifact_hash: "missing",
      computed_hash: "not_computed",
      artifact_identity: "unknown",
      replay_safe_integrity: false
    },
    import_source: "explicit local semantic_proposal.json file selection",
    file_name: "unknown",
    file_persisted: false,
    durable_storage: false,
    hidden_persistence: false
  });
}

function semanticProposalBlockedResult(validation) {
  return {
    demo_id: "CHATGPT_SEMANTIC_PROPOSAL_IMPORT_V1",
    status: "BLOCKED",
    semantic_proposal_validation: canonicalize(validation),
    semantic_proposal_hash_verification: canonicalize(validation.hash_verification || {}),
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
    errors: [],
    import_source: validation.import_source || "explicit local semantic proposal import",
    file_name: validation.file_name || "not_applicable",
    file_persisted: false,
    durable_storage: false,
    hidden_persistence: false
  };
  result.semantic_proposal_hash_verification = canonicalize(validation.hash_verification || {});
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

async function importSemanticProposalFileFromSidepanel() {
  const fileInput = document.getElementById("semantic-proposal-file");
  const file = fileInput && fileInput.files ? fileInput.files[0] : null;
  if (!file) {
    window.sidepanelRenderResult(semanticProposalBlockedResult(missingSemanticProposalFileValidation()));
    return;
  }
  let validation;
  try {
    const rawText = await file.text();
    validation = await localSemanticProposalFileValidation(rawText, file.name);
  } catch (error) {
    validation = canonicalize({
      status: "REJECTED",
      errors: ["semantic proposal file could not be read"],
      proposal: {},
      hash_verification: {
        status: "HASH_INVALID",
        errors: ["semantic proposal file could not be read"],
        artifact_hash: "unknown",
        computed_hash: "not_computed",
        artifact_identity: "unknown",
        replay_safe_integrity: false
      },
      import_source: "explicit local semantic_proposal.json file selection",
      file_name: file.name || "unknown",
      file_persisted: false,
      durable_storage: false,
      hidden_persistence: false
    });
  }
  const result = validation.status === "ACCEPTED"
    ? runSemanticProposalContinuityFlow(validation)
    : semanticProposalBlockedResult(validation);
  window.sidepanelRenderResult(result);
}

function attachLocalGovernedTransportFromSidepanel() {
  const latest = lifecycleEntries[lifecycleEntries.length - 1] || {};
  const sessionInput = document.getElementById("local-transport-session-id");
  const sessionId = sessionInput && sessionInput.value ? sessionInput.value : "UNKNOWN";
  const envelope = buildLocalGovernedTransportEnvelope(latest, sessionId);
  const sessionRegistry = localTransportSessionRegistry(sessionId);
  const transportReport = handle_local_governed_transport({
    envelope,
    session_registry: sessionRegistry
  });
  const result = canonicalize({
    ...latest,
    status: transportReport.status === "TRANSPORT_ACCEPTED" ? "RETURNED" : "BLOCKED",
    local_governed_transport_report: transportReport,
    transport_runtime_attachment: {
      invocation: "explicit operator-triggered cockpit attach",
      automatic_ingestion: false,
      hidden_invocation: false,
      background_attach: false,
      http_endpoint: false,
      server_listener: false,
      provider_dispatch: false,
      approval: false,
      execution: false,
      orchestration: false,
      durable_persistence: false,
      autonomous_continuation: false
    },
    boundary_guarantees: {
      ...(latest.boundary_guarantees || {}),
      automatic_dispatch: false,
      hidden_execution: false,
      hidden_persistence: false
    },
    authority_guarantees: {
      ...(latest.authority_guarantees || {}),
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
  });
  window.sidepanelRenderResult(result);
}

function chatFirstBlockedResult({ reason, sessionId, mode }) {
  const transportReport = localTransportRejectedReport(
    {
      transport_id: "CHAT-FIRST-TRANSPORT-BLOCKED",
      session_id: sessionId || "UNKNOWN",
      proposal_id: "UNKNOWN",
      artifact_hash: "UNKNOWN",
      created_at_policy: "DETERMINISTIC_CHAT_FIRST_NORMALIZATION",
      source_label: "CHAT_FIRST_LOCAL_NORMALIZATION"
    },
    reason === "human_request is required" ? "TRANSPORT_REJECTED_SCHEMA" : "TRANSPORT_REJECTED_UNSAFE_MODE",
    reason,
    "HASH_NOT_VERIFIED"
  );
  return canonicalize({
    demo_id: "CHAT_FIRST_OPERATOR_FLOW_V1",
    status: "BLOCKED",
    chat_first_flow: {
      status: "REJECTED",
      reason,
      session_id: sessionId || "UNKNOWN",
      requested_mode: mode || "UNKNOWN",
      local_deterministic_normalization: true
    },
    local_governed_transport_report: transportReport,
    continuity_report: {
      aggregate_governance_status: "CONTINUITY_BOUNDARY_VIOLATION",
      continuity_findings: [reason],
      continuity_risks: ["Chat-first request rejected before governed transport acceptance."],
      continuity_recommendations: ["Use a non-empty request and REVIEW_ONLY, DEMO_ONLY, or READ_ONLY mode."]
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
  });
}

function runChatFirstGovernedFlowFromSidepanel() {
  const requestInput = document.getElementById("chat-first-human-request");
  const modeInput = document.getElementById("chat-first-requested-mode");
  const sessionInput = document.getElementById("local-transport-session-id");
  const humanRequest = requestInput ? requestInput.value : "";
  const requestedMode = modeInput && modeInput.value ? modeInput.value : "REVIEW_ONLY";
  const sessionId = sessionInput && sessionInput.value ? sessionInput.value : LOCAL_GOVERNED_TRANSPORT_SESSION_ID;
  const envelope = prepareChatFirstTransportEnvelope({
    human_request: humanRequest,
    session_id: sessionId,
    requested_mode: requestedMode
  });
  if (envelope.error) {
    window.sidepanelRenderResult(chatFirstBlockedResult({
      reason: envelope.error,
      sessionId,
      mode: requestedMode
    }));
    return;
  }
  const transportReport = handle_local_governed_transport({
    envelope,
    session_registry: localTransportSessionRegistry(sessionId)
  });
  const accepted = transportReport.status === "TRANSPORT_ACCEPTED";
  const result = canonicalize({
    demo_id: "CHAT_FIRST_OPERATOR_FLOW_V1",
    status: accepted ? "RETURNED" : "BLOCKED",
    semantic_proposal: envelope.semantic_proposal,
    semantic_proposal_validation: {
      status: accepted ? "ACCEPTED" : "REJECTED",
      proposal_id: envelope.proposal_id,
      proposed_mode: envelope.semantic_proposal.proposed_mode,
      errors: accepted ? [] : [transportReport.rejection_reason],
      import_source: "chat-first deterministic local normalization",
      file_persisted: false,
      durable_storage: false,
      hidden_persistence: false
    },
    semantic_proposal_hash_verification: {
      status: transportReport.hash_verification_status,
      artifact_hash: envelope.artifact_hash,
      computed_hash: envelope.artifact_hash,
      artifact_identity: envelope.proposal_id,
      replay_safe_integrity: accepted
    },
    local_governed_transport_report: transportReport,
    chat_first_flow: {
      status: accepted ? "ACCEPTED" : "REJECTED",
      reason: transportReport.rejection_reason || "transport accepted for visibility",
      session_id: envelope.session_id,
      proposal_id: envelope.proposal_id,
      requested_mode: requestedMode,
      local_deterministic_normalization: true,
      python_primitive_canonical: true,
      browser_mirror: true
    },
    artifacts: {
      chat_first_transport_envelope: envelope
    },
    continuity_report: {
      aggregate_governance_status: accepted ? "CONTINUITY_VALID" : "CONTINUITY_BOUNDARY_VIOLATION",
      replay_visibility_summary: { visible: accepted, reference_count: accepted ? 1 : 0, gaps: [], mutated: false },
      lifecycle_visibility_summary: { visible: true, reference_count: 0, gaps: [], mutated: false },
      authority_boundary_summary: { visible: true, statement_count: 1, violations: [], authority_created: false },
      semantic_boundary_summary: { visible: true, statement_count: 1, overclaims: [], semantic_authority_created: false },
      continuity_findings: [accepted ? "Chat-first request accepted for governed transport visibility." : transportReport.rejection_reason],
      continuity_risks: ["Deterministic normalization is not semantic understanding."],
      continuity_recommendations: ["Review transport report before any separate governed action."],
      lineage_summary: { visible: true, reference_count: 1, mutated: false }
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
  });
  window.sidepanelRenderResult(result);
}

function bridgeReplayEvent({ event_type, status, session_id, proposal_id, payload }) {
  const seed = { event_type, payload, proposal_id, session_id, status };
  return canonicalize({
    replay_event_id: deterministicId("BRIDGE-REPLAY", seed),
    event_type,
    status,
    session_id,
    proposal_id,
    payload_hash: deterministicId("BRIDGE-PAYLOAD", payload),
    visibility: "SESSION_LOCAL_REPLAY_VISIBLE",
    mutation: false,
    durable_persistence: false
  });
}

function bridgeTaskPackage({ proposal, sessionId, transportReport }) {
  const taskId = deterministicId("BRIDGE-TASK", {
    proposal_id: proposal.proposal_id,
    session_id: sessionId,
    transport_id: transportReport.transport_id
  });
  return canonicalize({
    task_id: taskId,
    governance_mode: "governed_execution_bridge_mock_only",
    risk_class: proposal.risk_class || "LOW",
    approval_required: false,
    codex_prompt: `MOCK ONLY: summarize bounded review for proposal ${proposal.proposal_id}.`,
    constraints: [
      "mock Codex result only",
      "no provider call",
      "no dispatch",
      "no approval",
      "no execution authority",
      "no orchestration",
      "no autonomous continuation",
      "session-local replay visibility only"
    ],
    expected_outputs: [
      "mock bounded result artifact",
      "result validation report",
      "ChatGPT-facing governed return summary"
    ],
    metadata: {
      session_id: sessionId,
      proposal_id: proposal.proposal_id,
      transport_status: transportReport.status,
      transport_replay_event_id: transportReport.replay_event_id,
      lifecycle_state: "TASK_PACKAGED",
      approved: false,
      execution_provider: "MOCK_CODEX_ONLY",
      authority: "NO_EXECUTION_AUTHORITY"
    }
  });
}

function mockCodexBridgeResult({ taskPackage, proposal, sessionId }) {
  const resultId = deterministicId("MOCK-CODEX-RESULT", {
    proposal_id: proposal.proposal_id,
    session_id: sessionId,
    task_id: taskPackage.task_id
  });
  return canonicalize({
    result_id: resultId,
    task_id: taskPackage.task_id,
    proposal_id: proposal.proposal_id,
    session_id: sessionId,
    status: "MOCK_CODEX_RESULT_RETURNED",
    tests: [
      {
        name: "mock_bounded_codex_lifecycle",
        status: "PASS",
        execution: "MOCK_ONLY"
      }
    ],
    files_changed: [],
    artifacts: [
      {
        artifact_id: deterministicId("MOCK-ARTIFACT", { result_id: resultId }),
        artifact_type: "bounded_mock_codex_summary",
        proposal_id: proposal.proposal_id
      }
    ],
    summary: `Mock bounded Codex result for: ${proposal.human_request}`,
    requires_human_review: true,
    provider_invoked: false,
    execution_authority_created: false,
    orchestration_created: false
  });
}

function validateBridgeResult({ mockResult, taskPackage, sessionId, proposalId }) {
  const errors = [];
  if (mockResult.task_id !== taskPackage.task_id) {
    errors.push("result task lineage mismatch");
  }
  if (mockResult.session_id !== sessionId) {
    errors.push("result session mismatch");
  }
  if (mockResult.proposal_id !== proposalId) {
    errors.push("result proposal mismatch");
  }
  if (mockResult.provider_invoked !== false) {
    errors.push("provider invocation is forbidden");
  }
  if (mockResult.execution_authority_created !== false) {
    errors.push("execution authority is forbidden");
  }
  if (mockResult.orchestration_created !== false) {
    errors.push("orchestration is forbidden");
  }
  return canonicalize({
    status: errors.length ? "RESULT_REJECTED" : "RESULT_VALIDATED",
    valid: errors.length === 0,
    errors,
    checks: {
      result_lineage: mockResult.task_id === taskPackage.task_id,
      session_match: mockResult.session_id === sessionId,
      proposal_linkage: mockResult.proposal_id === proposalId,
      bounded_lifecycle: taskPackage.metadata.lifecycle_state === "TASK_PACKAGED",
      replay_visibility: true,
      non_authority_semantics: (
        mockResult.provider_invoked === false
        && mockResult.execution_authority_created === false
        && mockResult.orchestration_created === false
      )
    }
  });
}

function governedBridgeReturn({ accepted, reason, taskPackage }) {
  return canonicalize({
    status: accepted ? "ACCEPTED" : "REJECTED",
    reason,
    replay_visibility: "SESSION_LOCAL_REPLAY_VISIBLE",
    next_recommended_step: accepted
      ? "Review the bounded task and mock result evidence before any separate governed action."
      : "Revise the request or session binding and rerun the governed bridge.",
    task_id: taskPackage && taskPackage.task_id ? taskPackage.task_id : "NONE",
    non_authority_reminder: "No execution occurred. No provider was invoked. No approval, dispatch, or continuation authority was created."
  });
}

function rejectedEndToEndBridgeResult({ sessionId, proposalId, transportStatus, reason, replayEvents }) {
  return canonicalize({
    demo_id: "MINIMAL_END_TO_END_BRIDGE_SIDEPANEL_ATTACHMENT_V1",
    status: "BLOCKED",
    session_id: sessionId || "UNKNOWN",
    proposal_id: proposalId || "UNKNOWN",
    transport_status: transportStatus,
    task_package: {},
    mock_codex_result: {},
    result_validation: { status: "RESULT_REJECTED", valid: false, errors: [reason] },
    governed_chat_return: governedBridgeReturn({ accepted: false, reason, taskPackage: null }),
    replay_events: replayEvents,
    end_to_end_bridge: {
      status: "BRIDGE_REJECTED",
      human_request: "",
      session_id: sessionId || "UNKNOWN"
    },
    operator_visibility: {
      runtime_state_visible: true,
      transport_status_visible: true,
      task_package_visible: false,
      mock_result_visible: false,
      result_validation_visible: true,
      chat_return_visible: true,
      replay_visible: true
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
    },
    non_authority_guarantees: [
      "CHATGPT_SEMANTIC_COGNITION_ADVISORY_ONLY",
      "AIGOL_VALIDATION_REQUIRED",
      "SEMANTIC_TRANSPORT_ONLY",
      "MOCK_CODEX_ONLY_NO_PROVIDER_EXECUTION",
      "NO_DISPATCH_AUTHORITY",
      "NO_APPROVAL_AUTHORITY",
      "NO_EXECUTION_AUTHORITY",
      "NO_ORCHESTRATION",
      "NO_AUTONOMOUS_CONTINUATION",
      "NO_DURABLE_PERSISTENCE"
    ]
  });
}

function runMinimalEndToEndBridgeFromSidepanel() {
  const requestInput = document.getElementById("chat-first-human-request");
  const sessionInput = document.getElementById("local-transport-session-id");
  const humanRequest = requestInput ? requestInput.value : "";
  const sessionId = sessionInput && sessionInput.value ? sessionInput.value : LOCAL_GOVERNED_TRANSPORT_SESSION_ID;
  const replayEvents = [];
  const envelope = prepareChatFirstTransportEnvelope({
    human_request: humanRequest,
    session_id: sessionId,
    requested_mode: "REVIEW_ONLY"
  });
  if (envelope.error) {
    replayEvents.push(bridgeReplayEvent({
      event_type: "SEMANTIC_PROPOSAL_REJECTED",
      status: "BRIDGE_REJECTED",
      session_id: sessionId || "UNKNOWN",
      proposal_id: "UNKNOWN",
      payload: { reason: envelope.error }
    }));
    window.sidepanelRenderResult(rejectedEndToEndBridgeResult({
      sessionId,
      proposalId: "UNKNOWN",
      transportStatus: "NOT_PREPARED",
      reason: envelope.error,
      replayEvents
    }));
    return;
  }
  const proposal = envelope.semantic_proposal;
  replayEvents.push(bridgeReplayEvent({
    event_type: "SEMANTIC_PROPOSAL_NORMALIZED",
    status: "NORMALIZED",
    session_id: sessionId,
    proposal_id: proposal.proposal_id,
    payload: proposal
  }));
  const transportReport = handle_local_governed_transport({
    envelope,
    session_registry: localTransportSessionRegistry(sessionId)
  });
  replayEvents.push(bridgeReplayEvent({
    event_type: "LOCAL_GOVERNED_TRANSPORT_VALIDATED",
    status: transportReport.status,
    session_id: sessionId || "UNKNOWN",
    proposal_id: proposal.proposal_id,
    payload: transportReport
  }));
  if (transportReport.status !== "TRANSPORT_ACCEPTED") {
    window.sidepanelRenderResult(rejectedEndToEndBridgeResult({
      sessionId,
      proposalId: proposal.proposal_id,
      transportStatus: transportReport.status,
      reason: transportReport.rejection_reason,
      replayEvents
    }));
    return;
  }
  const taskPackage = bridgeTaskPackage({ proposal, sessionId, transportReport });
  replayEvents.push(bridgeReplayEvent({
    event_type: "GOVERNED_TASK_PACKAGE_CREATED",
    status: "TASK_PACKAGE_VALID",
    session_id: sessionId,
    proposal_id: proposal.proposal_id,
    payload: taskPackage
  }));
  const mockResult = mockCodexBridgeResult({ taskPackage, proposal, sessionId });
  replayEvents.push(bridgeReplayEvent({
    event_type: "MOCK_CODEX_RESULT_CREATED",
    status: mockResult.status,
    session_id: sessionId,
    proposal_id: proposal.proposal_id,
    payload: mockResult
  }));
  const resultValidation = validateBridgeResult({
    mockResult,
    taskPackage,
    sessionId,
    proposalId: proposal.proposal_id
  });
  replayEvents.push(bridgeReplayEvent({
    event_type: "GOVERNED_RESULT_VALIDATED",
    status: resultValidation.status,
    session_id: sessionId,
    proposal_id: proposal.proposal_id,
    payload: resultValidation
  }));
  const accepted = resultValidation.valid === true;
  const result = canonicalize({
    demo_id: "MINIMAL_END_TO_END_BRIDGE_SIDEPANEL_ATTACHMENT_V1",
    status: accepted ? "RETURNED" : "BLOCKED",
    session_id: sessionId,
    proposal_id: proposal.proposal_id,
    semantic_proposal: proposal,
    semantic_proposal_validation: {
      status: "ACCEPTED",
      proposal_id: proposal.proposal_id,
      proposed_mode: proposal.proposed_mode,
      errors: [],
      import_source: "minimal end-to-end bridge sidepanel attachment",
      durable_storage: false,
      hidden_persistence: false
    },
    semantic_proposal_hash_verification: {
      status: transportReport.hash_verification_status,
      artifact_hash: envelope.artifact_hash,
      computed_hash: envelope.artifact_hash,
      artifact_identity: envelope.proposal_id,
      replay_safe_integrity: true
    },
    transport_status: transportReport.status,
    local_governed_transport_report: transportReport,
    task_package: taskPackage,
    mock_codex_result: mockResult,
    result_validation: resultValidation,
    governed_chat_return: governedBridgeReturn({
      accepted,
      reason: accepted
        ? "governed bridge lifecycle accepted with mocked bounded Codex result"
        : "result validation failed",
      taskPackage
    }),
    replay_events: replayEvents,
    end_to_end_bridge: {
      status: accepted ? "BRIDGE_ACCEPTED" : "BRIDGE_REJECTED",
      human_request: proposal.human_request,
      session_id: sessionId,
      compact_runtime_narration: true
    },
    continuity_report: {
      aggregate_governance_status: accepted ? "CONTINUITY_VALID" : "CONTINUITY_BOUNDARY_VIOLATION",
      replay_visibility_summary: { visible: true, reference_count: replayEvents.length, gaps: [], mutated: false },
      lifecycle_visibility_summary: { visible: true, reference_count: 5, gaps: [], mutated: false },
      authority_boundary_summary: { visible: true, statement_count: 1, violations: [], authority_created: false },
      semantic_boundary_summary: { visible: true, statement_count: 1, overclaims: [], semantic_authority_created: false },
      continuity_findings: [accepted ? "Minimal end-to-end bridge lifecycle rendered with mocked bounded Codex result." : "Minimal bridge lifecycle rejected."],
      continuity_risks: ["Sidepanel attachment mirrors the canonical Python runtime; no backend interop is added."],
      continuity_recommendations: ["Review governed return and replay event IDs before any separate governed action."],
      lineage_summary: { visible: true, reference_count: 1, mutated: false }
    },
    operator_visibility: {
      runtime_state_visible: true,
      transport_status_visible: true,
      task_package_visible: true,
      mock_result_visible: true,
      result_validation_visible: true,
      chat_return_visible: true,
      replay_visible: true
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
    },
    non_authority_guarantees: [
      "CHATGPT_SEMANTIC_COGNITION_ADVISORY_ONLY",
      "AIGOL_VALIDATION_REQUIRED",
      "SEMANTIC_TRANSPORT_ONLY",
      "MOCK_CODEX_ONLY_NO_PROVIDER_EXECUTION",
      "NO_DISPATCH_AUTHORITY",
      "NO_APPROVAL_AUTHORITY",
      "NO_EXECUTION_AUTHORITY",
      "NO_ORCHESTRATION",
      "NO_AUTONOMOUS_CONTINUATION",
      "NO_DURABLE_PERSISTENCE"
    ]
  });
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
  setCockpitText(COCKPIT_IDS.semanticProposalHashVerificationStatus, semanticProposalHashVerificationSummary(latest));
  setCockpitText(COCKPIT_IDS.semanticProposalArtifact, artifactJson(semanticProposalArtifact(latest)));
  setCockpitText(COCKPIT_IDS.localTransportRuntimeStatus, localTransportRuntimeSummary(latest));
  setCockpitText(COCKPIT_IDS.chatFirstResultCard, chatFirstResultCardSummary(latest));
  setCockpitText(COCKPIT_IDS.latestActionResultCard, latestActionResultCardSummary(latest));
  setCockpitText(COCKPIT_IDS.operatorEventStream, operatorEventStreamSummary(latest));
  setCockpitText(COCKPIT_IDS.governanceChatReturn, governanceChatReturnSummary(latest));
  setCockpitText(COCKPIT_IDS.endToEndBridgeLifecycle, endToEndBridgeLifecycleSummary(latest));
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

const importSemanticProposalFileButton = document.getElementById("import-semantic-proposal-file");
if (importSemanticProposalFileButton) {
  importSemanticProposalFileButton.onclick = importSemanticProposalFileFromSidepanel;
}

const attachLocalGovernedTransportButton = document.getElementById("attach-local-governed-transport");
if (attachLocalGovernedTransportButton) {
  attachLocalGovernedTransportButton.onclick = attachLocalGovernedTransportFromSidepanel;
}

const runChatFirstGovernedFlowButton = document.getElementById("run-chat-first-governed-flow");
if (runChatFirstGovernedFlowButton) {
  runChatFirstGovernedFlowButton.onclick = runChatFirstGovernedFlowFromSidepanel;
}

const runMinimalEndToEndBridgeButton = document.getElementById("run-minimal-end-to-end-bridge");
if (runMinimalEndToEndBridgeButton) {
  runMinimalEndToEndBridgeButton.onclick = runMinimalEndToEndBridgeFromSidepanel;
}
