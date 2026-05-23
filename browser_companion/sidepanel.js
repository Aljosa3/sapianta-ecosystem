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
const CANONICAL_BRIDGE_RESULT_ARTIFACT_TYPE = "MINIMAL_END_TO_END_BRIDGE_RESULT";
const CANONICAL_BRIDGE_RESULT_SCHEMA_VERSION = 1;
const CANONICAL_BRIDGE_RESULT_AUTHORITY = "NON_EXECUTING_NON_AUTHORITATIVE";
const SERVICE_WORKER_NATIVE_BRIDGE_ACTION = "RUN_NATIVE_BRIDGE";

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
  endToEndBridgeLifecycle: "end-to-end-bridge-lifecycle",
  canonicalBridgeResultArtifactStatus: "canonical-bridge-result-artifact-status",
  observatoryTopology: "observatory-topology",
  observatoryClassificationLegend: "observatory-classification-legend",
  observatoryHumanRequest: "observatory-human-request",
  observatorySemanticReasoning: "observatory-semantic-reasoning",
  observatorySemanticContract: "observatory-semantic-contract",
  observatorySemanticContractJson: "observatory-semantic-contract-json",
  observatoryAigolGovernance: "observatory-aigol-governance",
  observatoryTaskPackage: "observatory-task-package",
  observatoryTaskPackageJson: "observatory-task-package-json",
  observatoryCodexExecution: "observatory-codex-execution",
  observatoryPostVerification: "observatory-post-verification",
  observatoryGovernedReturn: "observatory-governed-return",
  chatgptIngressArtifactPreview: "chatgpt-ingress-artifact-preview-card",
  chatgptIngressImportValidation: "chatgpt-ingress-import-validation-card",
  chatgptIngressProposalCandidate: "chatgpt-ingress-proposal-candidate-card",
  chatgptIngressContractCandidate: "chatgpt-ingress-contract-candidate-card",
  chatgptIngressGovernanceReport: "chatgpt-ingress-governance-report-card",
  chatgptIngressAcceptanceGate: "chatgpt-ingress-acceptance-gate-card",
  governedTaskPackagePreview: "governed-task-package-preview-card",
  humanApprovalGate: "human-approval-gate-card",
  governedHandoffPackagePreview: "governed-handoff-package-preview-card",
  explicitDispatchAuthorization: "explicit-dispatch-authorization-card",
  controlledExecutionContinuityPreview: "controlled-execution-continuity-preview-card",
  chatgptIngressStop: "chatgpt-ingress-stop-card",
  chatgptIngressNativeImportStatus: "chatgpt-ingress-native-import-status"
};

let latestChatgptIngressTaskPackagePreview = null;
let latestGovernedHandoffPackagePreview = null;

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

function previewHash(prefix, value) {
  return deterministicId(prefix, canonicalize(value));
}

function chatgptIngressPreviewArtifact() {
  const humanRequest = "Preview ChatGPT ingress continuity without execution authority.";
  const semanticOutput = "Model-produced semantic input proposes import-only structural continuity.";
  const humanRequestHash = previewHash("PREVIEW-HUMAN-REQUEST-HASH", humanRequest);
  const semanticOutputHash = previewHash("PREVIEW-SEMANTIC-OUTPUT-HASH", semanticOutput);
  const replayIdentity = deterministicId("CHATGPT-INGRESS-PREVIEW-REPLAY", {
    session_id: "CHATGPT-INGRESS-PREVIEW-SESSION",
    human_request_hash: humanRequestHash,
    semantic_output_hash: semanticOutputHash,
    schema_version: "1.0"
  });
  const artifact = {
    artifact_type: "CHATGPT_INGRESS_ARTIFACT_V1",
    schema_version: "1.0",
    source: "chatgpt",
    created_at: "1970-01-01T00:00:00Z",
    session_id: "CHATGPT-INGRESS-PREVIEW-SESSION",
    human_request: humanRequest,
    chatgpt_semantic_output: semanticOutput,
    normalized_intent: "PREVIEW_SEMANTIC_INGRESS_CONTINUITY",
    expected_artifacts: ["semantic proposal candidate", "semantic contract candidate", "governance acceptance report"],
    constraints: ["preview only", "import visibility only", "no execution", "no Codex dispatch"],
    forbidden_operations: ["execution authorization", "provider dispatch", "governance approval", "autonomous continuation"],
    authority_boundary: {
      chatgpt_authority: false,
      execution_authority: false,
      governance_authority: false,
      approval_authority: false,
      provider_dispatch_authority: false,
      autonomous_continuation_authority: false,
      boundary_statement: "ChatGPT output is semantic input only and cannot authorize execution."
    },
    provenance: {
      preview_only: true,
      live_chatgpt_invoked: false,
      aigol_governance_required: true
    },
    replay_identity: replayIdentity,
    hashes: {
      human_request_hash: humanRequestHash,
      semantic_output_hash: semanticOutputHash
    },
    validation_status: "ACCEPTED_AS_SEMANTIC_INPUT"
  };
  artifact.hashes.artifact_hash = previewHash("CHATGPT-INGRESS-ARTIFACT-HASH", artifact);
  return canonicalize(artifact);
}

const CHATGPT_INGRESS_REQUIRED_FIELDS = [
  "artifact_type",
  "schema_version",
  "source",
  "created_at",
  "session_id",
  "human_request",
  "chatgpt_semantic_output",
  "normalized_intent",
  "expected_artifacts",
  "constraints",
  "forbidden_operations",
  "authority_boundary",
  "provenance",
  "replay_identity",
  "hashes",
  "validation_status"
];

const CHATGPT_INGRESS_AUTHORITY_FLAGS = [
  "chatgpt_authority",
  "execution_authority",
  "governance_authority",
  "approval_authority",
  "provider_dispatch_authority",
  "autonomous_continuation_authority"
];

function chatgptIngressHashLooksValid(value) {
  return typeof value === "string" && /^sha256:[0-9a-f]{64}$/.test(value);
}

function chatgptIngressImportedClaimText(artifact) {
  return [
    artifact.human_request,
    artifact.chatgpt_semantic_output,
    artifact.normalized_intent,
    compactValue(artifact.expected_artifacts || []),
    compactValue(artifact.constraints || []),
    compactValue(artifact.provenance || {})
  ].join(" ").toLowerCase();
}

function chatgptIngressForbiddenImportFields(value, path = "") {
  const findings = [];
  if (value && typeof value === "object" && !Array.isArray(value)) {
    Object.keys(value).forEach((key) => {
      const childPath = path ? `${path}.${key}` : key;
      if ([
        "provider_dispatch",
        "execution_authorization",
        "execution_authorized",
        "autonomous_continuation",
        "governance_approval",
        "governance_approved"
      ].includes(key)) {
        findings.push(childPath);
      }
      findings.push(...chatgptIngressForbiddenImportFields(value[key], childPath));
    });
  } else if (Array.isArray(value)) {
    value.forEach((child, index) => {
      findings.push(...chatgptIngressForbiddenImportFields(child, `${path}[${index}]`));
    });
  }
  return findings;
}

function validateImportedChatgptIngressArtifact(artifact) {
  const errors = [];
  if (!artifact || typeof artifact !== "object" || Array.isArray(artifact)) {
    return { valid: false, status: "REJECTED", errors: ["artifact must be a JSON object"] };
  }
  CHATGPT_INGRESS_REQUIRED_FIELDS.forEach((field) => {
    if (!(field in artifact)) {
      errors.push(`missing required field: ${field}`);
    }
  });
  if (errors.length) {
    return { valid: false, status: "REJECTED", errors };
  }
  if (artifact.artifact_type !== "CHATGPT_INGRESS_ARTIFACT_V1") {
    errors.push("artifact_type invalid");
  }
  if (artifact.schema_version !== "1.0") {
    errors.push("schema_version unsupported");
  }
  if (artifact.source !== "chatgpt") {
    errors.push("source must be chatgpt");
  }
  if (artifact.validation_status !== "ACCEPTED_AS_SEMANTIC_INPUT") {
    errors.push("validation_status must be ACCEPTED_AS_SEMANTIC_INPUT for preview import");
  }
  const boundary = artifact.authority_boundary || {};
  CHATGPT_INGRESS_AUTHORITY_FLAGS.forEach((flag) => {
    if (boundary[flag] !== false) {
      errors.push(`${flag} must be false`);
    }
  });
  if (boundary.boundary_statement !== "ChatGPT output is semantic input only and cannot authorize execution.") {
    errors.push("required boundary statement missing");
  }
  const hashes = artifact.hashes || {};
  ["human_request_hash", "semantic_output_hash", "artifact_hash"].forEach((field) => {
    if (!chatgptIngressHashLooksValid(hashes[field])) {
      errors.push(`${field} missing or invalid`);
    }
  });
  if (typeof artifact.replay_identity !== "string" || artifact.replay_identity.trim() === "") {
    errors.push("replay identity invalid");
  }
  if (!artifact.provenance || typeof artifact.provenance !== "object" || Array.isArray(artifact.provenance)) {
    errors.push("provenance invalid");
  }
  chatgptIngressForbiddenImportFields(artifact).forEach((field) => {
    errors.push(`forbidden field present: ${field}`);
  });
  const claimText = chatgptIngressImportedClaimText(artifact);
  [
    "approved for execution",
    "approval granted",
    "governance approved",
    "authorize execution",
    "execution authorized",
    "dispatch to codex",
    "semantic correctness verified",
    "semantically correct",
    "bypass aigol",
    "bypass governance",
    "continue autonomously"
  ].forEach((phrase) => {
    if (claimText.includes(phrase)) {
      errors.push(`forbidden claim present: ${phrase}`);
    }
  });
  return {
    valid: errors.length === 0,
    status: errors.length === 0 ? "ACCEPTED_AS_SEMANTIC_INPUT" : "REJECTED",
    errors,
    replay_identity: artifact.replay_identity || "UNKNOWN",
    artifact_hash: hashes.artifact_hash || "UNKNOWN"
  };
}

function rejectedChatgptIngressPreview({ reason, artifact = {} }) {
  const hashes = artifact.hashes || {};
  const ingressArtifactHash = hashes.artifact_hash || "UNKNOWN";
  const semanticOutputHash = hashes.semantic_output_hash || "UNKNOWN";
  const replayIdentity = artifact.replay_identity || "UNKNOWN";
  const governanceReport = {
    report_type: "CHATGPT_INGRESS_IMPORT_VALIDATION_REPORT_V1",
    status: "REJECTED",
    classification: "STRUCTURAL_ONLY",
    import_only: true,
    rejection_reason: reason,
    replay_identity: replayIdentity,
    ingress_artifact_hash: ingressArtifactHash,
    semantic_output_hash: semanticOutputHash,
    proposal_candidate_hash: "NONE",
    contract_candidate_hash: "NONE",
    provenance_lineage: artifact.provenance || {},
    execution_performed: false,
    codex_dispatch_performed: false,
    governance_approved: false,
    semantic_correctness_verified: false,
    autonomous_continuation_performed: false
  };
  governanceReport.governance_report_hash = previewHash("CHATGPT-INGRESS-GOVERNANCE-REPORT-HASH", governanceReport);
  return canonicalize({
    artifact,
    import_validation: {
      status: "REJECTED",
      classification: "STRUCTURAL_ONLY",
      import_only: true,
      errors: [reason],
      replay_identity: replayIdentity,
      artifact_hash: ingressArtifactHash,
      execution_performed: false,
      codex_dispatch_performed: false
    },
    proposal_candidate: {},
    contract_candidate: {},
    governance_report: governanceReport
  });
}

function chatgptIngressPreviewImport(artifactInput = null) {
  const artifact = artifactInput ? canonicalize(artifactInput) : chatgptIngressPreviewArtifact();
  const validation = artifactInput
    ? validateImportedChatgptIngressArtifact(artifact)
    : {
      valid: true,
      status: "ACCEPTED_AS_SEMANTIC_INPUT",
      errors: [],
      replay_identity: artifact.replay_identity,
      artifact_hash: artifact.hashes.artifact_hash
    };
  if (!validation.valid) {
    return rejectedChatgptIngressPreview({ reason: validation.errors.join("; "), artifact });
  }
  const proposalCandidate = {
    candidate_type: "CHATGPT_INGRESS_SEMANTIC_PROPOSAL_CANDIDATE_V1",
    proposal_candidate_only: true,
    classification: "ADVISORY_ONLY",
    normalized_intent: artifact.normalized_intent,
    expected_artifacts: artifact.expected_artifacts,
    constraints: artifact.constraints,
    forbidden_operations: artifact.forbidden_operations,
    replay_identity: artifact.replay_identity,
    hashes: {
      ingress_artifact_hash: artifact.hashes.artifact_hash,
      human_request_hash: artifact.hashes.human_request_hash,
      semantic_output_hash: artifact.hashes.semantic_output_hash
    },
    provenance_lineage: artifact.provenance,
    execution_authority: false,
    governance_authority: false,
    codex_dispatch_allowed: false,
    autonomous_continuation_allowed: false
  };
  proposalCandidate.proposal_candidate_hash = previewHash("CHATGPT-INGRESS-PROPOSAL-CANDIDATE-HASH", proposalCandidate);

  const contractCandidate = {
    candidate_type: "CHATGPT_INGRESS_SEMANTIC_CONTRACT_CANDIDATE_V1",
    contract_candidate_only: true,
    classification: "STRUCTURAL_ONLY",
    source_proposal_candidate_hash: proposalCandidate.proposal_candidate_hash,
    normalized_intent: proposalCandidate.normalized_intent,
    replay_identity: artifact.replay_identity,
    hashes: proposalCandidate.hashes,
    provenance_lineage: artifact.provenance,
    semantic_correctness_verified: false,
    governance_approved: false,
    execution_authorized: false,
    provider_dispatch_authorized: false
  };
  contractCandidate.contract_candidate_hash = previewHash("CHATGPT-INGRESS-CONTRACT-CANDIDATE-HASH", contractCandidate);

  const governanceReport = {
    report_type: "CHATGPT_INGRESS_IMPORT_VALIDATION_REPORT_V1",
    status: "ACCEPTED_FOR_STRUCTURAL_IMPORT",
    classification: "STRUCTURAL_ONLY",
    import_only: true,
    replay_identity: artifact.replay_identity,
    ingress_artifact_hash: artifact.hashes.artifact_hash,
    proposal_candidate_hash: proposalCandidate.proposal_candidate_hash,
    contract_candidate_hash: contractCandidate.contract_candidate_hash,
    provenance_lineage: artifact.provenance,
    execution_performed: false,
    codex_dispatch_performed: false,
    governance_approved: false,
    semantic_correctness_verified: false,
    autonomous_continuation_performed: false
  };
  governanceReport.governance_report_hash = previewHash("CHATGPT-INGRESS-GOVERNANCE-REPORT-HASH", governanceReport);

  return canonicalize({
    artifact,
    import_validation: {
      status: validation.status,
      classification: "STRUCTURAL_ONLY",
      import_only: true,
      errors: validation.errors,
      replay_identity: validation.replay_identity,
      artifact_hash: validation.artifact_hash,
      execution_performed: false,
      codex_dispatch_performed: false
    },
    proposal_candidate: proposalCandidate,
    contract_candidate: contractCandidate,
    governance_report: governanceReport
  });
}

function chatgptIngressPreviewCard(name, classification, fields) {
  return [
    `${name}`,
    `CLASSIFICATION: ${classification}`,
    "PREVIEW_ONLY: true",
    "IMPORT_ONLY: true",
    ...fields,
    "execution_performed: false",
    "codex_dispatch_performed: false",
    "governance_approved: false",
    "semantic_correctness_verified: false",
    "autonomous_continuation_performed: false"
  ].join("\n");
}

function chatgptIngressAcceptanceGate(preview) {
  const report = preview.governance_report || {};
  const proposal = preview.proposal_candidate || {};
  const contract = preview.contract_candidate || {};
  const accepted = report.status === "ACCEPTED_FOR_STRUCTURAL_IMPORT"
    && proposal.proposal_candidate_hash
    && contract.contract_candidate_hash
    && report.replay_identity
    && report.replay_identity !== "UNKNOWN"
    && report.ingress_artifact_hash
    && report.ingress_artifact_hash !== "UNKNOWN"
    && report.semantic_correctness_verified === false
    && report.execution_performed === false
    && report.codex_dispatch_performed === false
    && report.governance_approved === false
    && report.autonomous_continuation_performed === false;
  const checks = {
    authority_boundary_check: {
      passed: accepted,
      detail: "No execution, dispatch, approval, governance execution, or autonomous continuation authority is present."
    },
    replay_continuity_check: {
      passed: accepted,
      detail: "Replay identity is visible and preserved for preview continuity."
    },
    provenance_check: {
      passed: accepted && Boolean(report.provenance_lineage),
      detail: "Provenance lineage is visible for imported semantic input."
    },
    hash_integrity_check: {
      passed: accepted,
      detail: "Ingress, proposal candidate, and contract candidate hashes are visible."
    },
    semantic_correctness_check: {
      passed: report.semantic_correctness_verified === false,
      detail: "Semantic correctness is not verified."
    },
    execution_boundary_check: {
      passed: report.execution_performed === false,
      detail: "Execution is not performed or authorized."
    },
    provider_dispatch_check: {
      passed: report.codex_dispatch_performed === false,
      detail: "Codex/provider dispatch is not performed or authorized."
    },
    autonomous_continuation_check: {
      passed: report.autonomous_continuation_performed === false,
      detail: "Autonomous continuation is not performed or authorized."
    }
  };
  const rejectionReasons = accepted ? [] : [
    report.rejection_reason || "import validation did not satisfy governed preview admissibility"
  ];
  const evidence = {
    gate_type: "CHATGPT_INGRESS_ACCEPTANCE_GATE_V1",
    gate_status: accepted ? "ACCEPTED_FOR_GOVERNED_PREVIEW" : "REJECTED_BY_GOVERNANCE_GATE",
    admissibility_reasons: Object.values(checks).filter((check) => check.passed).map((check) => check.detail),
    rejection_reasons: rejectionReasons,
    ...checks,
    ingress_artifact_hash: report.ingress_artifact_hash || "UNKNOWN",
    proposal_candidate_hash: report.proposal_candidate_hash || "NONE",
    contract_candidate_hash: report.contract_candidate_hash || "NONE",
    replay_identity: report.replay_identity || "UNKNOWN",
    execution_authorized: false,
    codex_dispatch_authorized: false,
    provider_dispatch_authorized: false,
    semantic_correctness_verified: false,
    governance_execution_approval: false,
    autonomous_continuation_authorized: false
  };
  evidence.decision_hash = previewHash("CHATGPT-INGRESS-ACCEPTANCE-GATE-DECISION-HASH", evidence);
  return canonicalize(evidence);
}

function governedTaskPackagePreview(preview, acceptanceGate) {
  const report = preview.governance_report || {};
  const contract = preview.contract_candidate || {};
  const proposal = preview.proposal_candidate || {};
  const ready = acceptanceGate.gate_status === "ACCEPTED_FOR_GOVERNED_PREVIEW";
  const taskPreview = {
    artifact_type: "GOVERNED_TASK_PACKAGE_PREVIEW_V1",
    schema_version: "1.0",
    replay_identity: acceptanceGate.replay_identity || report.replay_identity || "UNKNOWN",
    provenance: {
      source: "CHATGPT_INGRESS_ACCEPTANCE_GATE_V1",
      provenance_lineage: report.provenance_lineage || {},
      source_candidate_references: proposal.provenance_lineage || {}
    },
    source_ingress_artifact_hash: acceptanceGate.ingress_artifact_hash || report.ingress_artifact_hash || "UNKNOWN",
    semantic_proposal_candidate_hash: acceptanceGate.proposal_candidate_hash || report.proposal_candidate_hash || "NONE",
    semantic_contract_candidate_hash: acceptanceGate.contract_candidate_hash || report.contract_candidate_hash || "NONE",
    admissibility_gate_hash: acceptanceGate.decision_hash || "NONE",
    normalized_intent: contract.normalized_intent || proposal.normalized_intent || "",
    expected_artifacts: contract.expected_artifacts || proposal.expected_artifacts || [],
    constraints: contract.constraints || proposal.constraints || [],
    forbidden_operations: [
      "codex_dispatch",
      "native_messaging_execution",
      "provider_dispatch",
      "governance_execution_approval",
      "automatic_execution",
      "autonomous_continuation",
      "orchestration",
      "retries",
      "fallback_routing"
    ],
    execution_boundary_state: ready ? "READY_FOR_HUMAN_APPROVAL" : "PREVIEW_REJECTED",
    human_approval_required: true,
    governance_status: ready ? "READY_FOR_HUMAN_APPROVAL" : "PREVIEW_REJECTED",
    preview_only: true,
    executable: false,
    dispatchable: false,
    governance_finalized: false,
    execution_authorized: false,
    codex_dispatch_authorized: false,
    provider_dispatch_authorized: false,
    governance_execution_approved: false,
    autonomous_continuation_authorized: false,
    classification: ["STRUCTURAL_ONLY", "ADVISORY_ONLY"],
    boundary_statement: "Execution boundary reached but not crossed; explicit future human approval is required."
  };
  taskPreview.preview_hash = previewHash("GOVERNED-TASK-PACKAGE-PREVIEW-HASH", {
    source_ingress_artifact_hash: taskPreview.source_ingress_artifact_hash,
    semantic_proposal_candidate_hash: taskPreview.semantic_proposal_candidate_hash,
    semantic_contract_candidate_hash: taskPreview.semantic_contract_candidate_hash,
    admissibility_gate_hash: taskPreview.admissibility_gate_hash,
    replay_identity: taskPreview.replay_identity,
    governance_status: taskPreview.governance_status,
    execution_boundary_state: taskPreview.execution_boundary_state
  });
  return canonicalize(taskPreview);
}

function humanApprovalGate(taskPackagePreview, humanDecision) {
  const approved = humanDecision === "APPROVE";
  const sourceReady = taskPackagePreview.execution_boundary_state === "READY_FOR_HUMAN_APPROVAL"
    && taskPackagePreview.governance_status === "READY_FOR_HUMAN_APPROVAL"
    && taskPackagePreview.preview_hash
    && taskPackagePreview.replay_identity
    && taskPackagePreview.provenance
    && taskPackagePreview.execution_authorized === false
    && taskPackagePreview.codex_dispatch_authorized === false
    && taskPackagePreview.provider_dispatch_authorized === false
    && taskPackagePreview.governance_execution_approved === false
    && taskPackagePreview.autonomous_continuation_authorized === false;
  const approval = {
    artifact_type: "HUMAN_APPROVAL_GATE_V1",
    schema_version: "1.0",
    replay_identity: taskPackagePreview.replay_identity || "UNKNOWN",
    source_task_package_preview_hash: taskPackagePreview.preview_hash || "UNKNOWN",
    human_decision: humanDecision,
    approval_status: approved && sourceReady ? "APPROVED_FOR_GOVERNED_HANDOFF" : "REJECTED_BY_HUMAN",
    approval_reason: approved && sourceReady
      ? "Human explicitly approved preview for future governed handoff evidence."
      : "Human explicitly rejected preview or source preview was not approval-ready.",
    operator_label: "LOCAL_BROWSER_OPERATOR",
    created_at: "1970-01-01T00:00:00Z",
    provenance: {
      source: "GOVERNED_TASK_PACKAGE_PREVIEW_V1",
      source_state: taskPackagePreview.execution_boundary_state || "UNKNOWN",
      source_governance_status: taskPackagePreview.governance_status || "UNKNOWN"
    },
    authority_boundary: {
      human_authority: true,
      execution_authority: false,
      codex_dispatch_authority: false,
      provider_dispatch_authority: false,
      governance_execution_authority: false,
      autonomous_continuation_authority: false,
      semantic_correctness_authority: false
    },
    human_approved: approved && sourceReady,
    execution_performed: false,
    codex_dispatch_performed: false,
    provider_dispatch_performed: false,
    autonomous_continuation_performed: false,
    semantic_correctness_verified: false,
    approval_evidence_only: true
  };
  approval.approval_hash = previewHash("HUMAN-APPROVAL-GATE-HASH", {
    replay_identity: approval.replay_identity,
    source_task_package_preview_hash: approval.source_task_package_preview_hash,
    human_decision: approval.human_decision,
    approval_status: approval.approval_status,
    approval_reason: approval.approval_reason,
    authority_boundary: approval.authority_boundary,
    provenance: approval.provenance
  });
  return canonicalize(approval);
}

function governedHandoffPackagePreview(taskPackagePreview, approval) {
  const approvalReady = approval.approval_status === "APPROVED_FOR_GOVERNED_HANDOFF"
    && approval.human_approved === true
    && approval.replay_identity === taskPackagePreview.replay_identity
    && approval.source_task_package_preview_hash === taskPackagePreview.preview_hash
    && taskPackagePreview.execution_boundary_state === "READY_FOR_HUMAN_APPROVAL"
    && taskPackagePreview.governance_status === "READY_FOR_HUMAN_APPROVAL"
    && taskPackagePreview.execution_authorized === false
    && taskPackagePreview.codex_dispatch_authorized === false
    && taskPackagePreview.provider_dispatch_authorized === false
    && taskPackagePreview.governance_execution_approved === false
    && taskPackagePreview.autonomous_continuation_authorized === false;
  const handoffPreview = {
    artifact_type: "GOVERNED_HANDOFF_PACKAGE_PREVIEW_V1",
    schema_version: "1.0",
    replay_identity: taskPackagePreview.replay_identity || approval.replay_identity || "UNKNOWN",
    provenance: {
      source: "HUMAN_APPROVAL_GATE_V1",
      task_package_preview_provenance: taskPackagePreview.provenance || {},
      human_approval_provenance: approval.provenance || {}
    },
    source_ingress_artifact_hash: taskPackagePreview.source_ingress_artifact_hash || "UNKNOWN",
    semantic_contract_candidate_hash: taskPackagePreview.semantic_contract_candidate_hash || "NONE",
    admissibility_gate_hash: taskPackagePreview.admissibility_gate_hash || "NONE",
    governed_task_package_preview_hash: taskPackagePreview.preview_hash || "UNKNOWN",
    human_approval_hash: approval.approval_hash || "UNKNOWN",
    handoff_boundary_state: approvalReady ? "READY_FOR_EXPLICIT_DISPATCH_AUTHORIZATION" : "HANDOFF_PREVIEW_REJECTED",
    target_provider_boundary: "BOUNDED_PROVIDER_DISPATCH_BOUNDARY_PREVIEW",
    allowed_provider_kind: "CODEX_CLI_PROVIDER_BOUNDARY_PREVIEW",
    workspace_scope_preview: "CURRENT_GOVERNED_WORKSPACE_ONLY_PREVIEW",
    timeout_policy_preview: "BOUNDED_TIMEOUT_REQUIRED_BEFORE_DISPATCH_AUTHORIZATION",
    constraints: taskPackagePreview.constraints || [],
    forbidden_operations: [
      "codex_dispatch",
      "native_messaging_execution",
      "provider_dispatch",
      "runtime_execution",
      "automatic_handoff",
      "automatic_execution",
      "autonomous_continuation",
      "orchestration",
      "retries",
      "background_workers"
    ],
    authority_boundary: {
      human_approval_present: approvalReady,
      execution_authorized: false,
      dispatch_authorized: false,
      codex_dispatch_authorized: false,
      provider_dispatch_authorized: false,
      governance_execution_approved: false,
      autonomous_continuation_authorized: false,
      boundary_statement: "Human approval is present, but it is not dispatch authorization."
    },
    handoff_preview_status: approvalReady ? "READY_FOR_EXPLICIT_DISPATCH_AUTHORIZATION" : "HANDOFF_PREVIEW_REJECTED",
    preview_only: true,
    executable: false,
    dispatchable: false,
    execution_performed: false,
    codex_dispatch_performed: false,
    provider_dispatch_performed: false,
    autonomous_continuation_performed: false,
    explicit_dispatch_authorization_required: true,
    classification: ["STRUCTURAL_ONLY", "ADVISORY_ONLY"]
  };
  handoffPreview.handoff_preview_hash = previewHash("GOVERNED-HANDOFF-PACKAGE-PREVIEW-HASH", {
    replay_identity: handoffPreview.replay_identity,
    source_ingress_artifact_hash: handoffPreview.source_ingress_artifact_hash,
    semantic_contract_candidate_hash: handoffPreview.semantic_contract_candidate_hash,
    admissibility_gate_hash: handoffPreview.admissibility_gate_hash,
    governed_task_package_preview_hash: handoffPreview.governed_task_package_preview_hash,
    human_approval_hash: handoffPreview.human_approval_hash,
    target_provider_boundary: handoffPreview.target_provider_boundary,
    allowed_provider_kind: handoffPreview.allowed_provider_kind,
    workspace_scope_preview: handoffPreview.workspace_scope_preview,
    timeout_policy_preview: handoffPreview.timeout_policy_preview,
    handoff_boundary_state: handoffPreview.handoff_boundary_state,
    authority_boundary: handoffPreview.authority_boundary,
    handoff_preview_status: handoffPreview.handoff_preview_status
  });
  return canonicalize(handoffPreview);
}

function renderGovernedHandoffPackagePreview(handoffPreview) {
  latestGovernedHandoffPackagePreview = handoffPreview;
  setCockpitText(COCKPIT_IDS.governedHandoffPackagePreview, [
    "Governed Handoff Package Preview",
    "ARTIFACT_TYPE: GOVERNED_HANDOFF_PACKAGE_PREVIEW_V1",
    "CLASSIFICATION: STRUCTURAL_ONLY / ADVISORY_ONLY",
    "HANDOFF PREVIEW ONLY",
    "NO EXECUTION",
    "NO CODEX DISPATCH",
    "NO PROVIDER DISPATCH",
    "EXPLICIT DISPATCH AUTHORIZATION REQUIRED",
    `handoff_preview_status: ${handoffPreview.handoff_preview_status}`,
    `handoff_boundary_state: ${handoffPreview.handoff_boundary_state}`,
    `replay_identity: ${handoffPreview.replay_identity}`,
    `handoff_preview_hash: ${handoffPreview.handoff_preview_hash}`,
    `human_approval_hash: ${handoffPreview.human_approval_hash}`,
    `governed_task_package_preview_hash: ${handoffPreview.governed_task_package_preview_hash}`,
    `target_provider_boundary: ${handoffPreview.target_provider_boundary}`,
    `allowed_provider_kind: ${handoffPreview.allowed_provider_kind}`,
    `workspace_scope_preview: ${handoffPreview.workspace_scope_preview}`,
    `timeout_policy_preview: ${handoffPreview.timeout_policy_preview}`,
    "human_approval_present: true",
    "execution_authorized: false",
    "dispatch_authorized: false",
    "codex_dispatch_authorized: false",
    "provider_dispatch_authorized: false",
    "preview_only: true",
    "executable: false",
    "dispatchable: false",
    "execution_performed: false",
    "codex_dispatch_performed: false",
    "provider_dispatch_performed: false",
    "autonomous_continuation_performed: false",
    "STOP: provider boundary preview reached but not crossed"
  ].join("\n"));
}

function explicitDispatchAuthorization(handoffPreview, dispatchDecision) {
  const authorized = dispatchDecision === "AUTHORIZE";
  const handoffReady = handoffPreview.handoff_boundary_state === "READY_FOR_EXPLICIT_DISPATCH_AUTHORIZATION"
    && handoffPreview.handoff_preview_status === "READY_FOR_EXPLICIT_DISPATCH_AUTHORIZATION"
    && handoffPreview.handoff_preview_hash
    && handoffPreview.replay_identity
    && handoffPreview.provenance
    && (handoffPreview.authority_boundary || {}).execution_authorized === false
    && (handoffPreview.authority_boundary || {}).dispatch_authorized === false
    && (handoffPreview.authority_boundary || {}).codex_dispatch_authorized === false
    && (handoffPreview.authority_boundary || {}).provider_dispatch_authorized === false
    && (handoffPreview.authority_boundary || {}).autonomous_continuation_authorized === false
    && handoffPreview.execution_performed === false
    && handoffPreview.codex_dispatch_performed === false
    && handoffPreview.provider_dispatch_performed === false
    && handoffPreview.executable === false
    && handoffPreview.dispatchable === false;
  const dispatchAuthorized = authorized && handoffReady;
  const authorization = {
    artifact_type: "EXPLICIT_DISPATCH_AUTHORIZATION_V1",
    schema_version: "1.0",
    replay_identity: handoffPreview.replay_identity || "UNKNOWN",
    provenance: {
      source: "GOVERNED_HANDOFF_PACKAGE_PREVIEW_V1",
      source_ingress_artifact_hash: handoffPreview.source_ingress_artifact_hash || "UNKNOWN",
      semantic_contract_candidate_hash: handoffPreview.semantic_contract_candidate_hash || "NONE",
      governed_task_package_preview_hash: handoffPreview.governed_task_package_preview_hash || "UNKNOWN",
      handoff_preview_provenance: handoffPreview.provenance || {}
    },
    source_handoff_preview_hash: handoffPreview.handoff_preview_hash || "UNKNOWN",
    human_approval_hash: handoffPreview.human_approval_hash || "UNKNOWN",
    admissibility_gate_hash: handoffPreview.admissibility_gate_hash || "NONE",
    dispatch_authorization_status: dispatchAuthorized ? "DISPATCH_AUTHORIZED" : "DISPATCH_REJECTED",
    dispatch_authorization_reason: dispatchAuthorized
      ? "Explicit dispatch authorization evidence created; execution remains stopped."
      : "Dispatch preview rejected or handoff preview was not authorization-ready.",
    dispatch_authority_boundary: {
      dispatch_authorized: dispatchAuthorized,
      execution_authorized: false,
      execution_performed: false,
      codex_dispatch_performed: false,
      provider_dispatch_performed: false,
      native_messaging_called: false,
      autonomous_continuation_authorized: false
    },
    allowed_provider_kind: handoffPreview.allowed_provider_kind || "UNKNOWN",
    provider_boundary_state: dispatchAuthorized ? "READY_FOR_CONTROLLED_EXECUTION_CONTINUITY" : "DISPATCH_REJECTED",
    workspace_scope_preview: handoffPreview.workspace_scope_preview || "UNKNOWN",
    timeout_policy_preview: handoffPreview.timeout_policy_preview || "UNKNOWN",
    constraints: handoffPreview.constraints || [],
    forbidden_operations: handoffPreview.forbidden_operations || [],
    dispatch_authorized: dispatchAuthorized,
    execution_performed: false,
    codex_dispatch_performed: false,
    provider_dispatch_performed: false,
    native_messaging_called: false,
    executable: false,
    dispatched: false,
    autonomous_continuation_performed: false,
    classification: ["STRUCTURAL_ONLY", "ADVISORY_ONLY"]
  };
  authorization.dispatch_authorization_hash = previewHash("EXPLICIT-DISPATCH-AUTHORIZATION-HASH", {
    replay_identity: authorization.replay_identity,
    source_ingress_artifact_hash: authorization.provenance.source_ingress_artifact_hash,
    semantic_contract_candidate_hash: authorization.provenance.semantic_contract_candidate_hash,
    admissibility_gate_hash: authorization.admissibility_gate_hash,
    governed_task_package_preview_hash: authorization.provenance.governed_task_package_preview_hash,
    human_approval_hash: authorization.human_approval_hash,
    governed_handoff_preview_hash: authorization.source_handoff_preview_hash,
    dispatch_authorization_status: authorization.dispatch_authorization_status,
    provider_boundary_state: authorization.provider_boundary_state,
    dispatch_authority_boundary: authorization.dispatch_authority_boundary
  });
  return canonicalize(authorization);
}

function renderExplicitDispatchAuthorization(authorization) {
  const continuityPreview = controlledExecutionContinuityPreview(authorization);
  setCockpitText(COCKPIT_IDS.explicitDispatchAuthorization, [
    "Explicit Dispatch Authorization",
    "ARTIFACT_TYPE: EXPLICIT_DISPATCH_AUTHORIZATION_V1",
    "CLASSIFICATION: STRUCTURAL_ONLY / ADVISORY_ONLY",
    "DISPATCH AUTHORIZATION ONLY",
    "NO EXECUTION",
    "NO CODEX DISPATCH",
    "NO PROVIDER EXECUTION",
    "NATIVE MESSAGING NOT CALLED",
    `dispatch_authorization_status: ${authorization.dispatch_authorization_status}`,
    `provider_boundary_state: ${authorization.provider_boundary_state}`,
    `dispatch_authorization_hash: ${authorization.dispatch_authorization_hash}`,
    `allowed_provider_kind: ${authorization.allowed_provider_kind}`,
    `workspace_scope_preview: ${authorization.workspace_scope_preview}`,
    `timeout_policy_preview: ${authorization.timeout_policy_preview}`,
    `authority_boundary_summary: ${compactValue(authorization.dispatch_authority_boundary)}`,
    `dispatch_authorized: ${authorization.dispatch_authorized}`,
    "execution_performed: false",
    "codex_dispatch_performed: false",
    "provider_dispatch_performed: false",
    "native_messaging_called: false",
    "executable: false",
    "dispatched: false",
    "autonomous_continuation_performed: false",
    "STOP: dispatch authorization continuity reached without execution continuity"
  ].join("\n"));
  renderControlledExecutionContinuityPreview(continuityPreview);
  setCockpitText(COCKPIT_IDS.chatgptIngressStop, [
    "STOP (No Execution)",
    "CLASSIFICATION: UI_ONLY",
    "DISPATCH_AUTHORIZATION_ONLY: true",
    "STOP boundary after EXPLICIT DISPATCH AUTHORIZATION",
    "STOP boundary after CONTROLLED EXECUTION CONTINUITY PREVIEW",
    `dispatch_authorization_status: ${authorization.dispatch_authorization_status}`,
    `dispatch_authorization_hash: ${authorization.dispatch_authorization_hash}`,
    `execution_continuity_status: ${continuityPreview.execution_continuity_status}`,
    `continuity_preview_hash: ${continuityPreview.continuity_preview_hash}`,
    `provider_boundary_state: ${authorization.provider_boundary_state}`,
    "runtime_boundary: no Native Messaging, no service worker execution path, no Python runtime execution, no Codex provider",
    "execution_performed: false",
    "codex_dispatch_performed: false",
    "provider_dispatch_performed: false",
    "native_messaging_called: false",
    "dispatched: false"
  ].join("\n"));
}

function controlledExecutionContinuityPreview(authorization) {
  const ready = authorization.dispatch_authorization_status === "DISPATCH_AUTHORIZED"
    && authorization.dispatch_authorized === true
    && authorization.replay_identity
    && authorization.dispatch_authorization_hash
    && authorization.provenance
    && authorization.execution_performed === false
    && authorization.codex_dispatch_performed === false
    && authorization.provider_dispatch_performed === false
    && authorization.native_messaging_called === false
    && authorization.executable === false
    && authorization.dispatched === false
    && authorization.autonomous_continuation_performed === false;
  const executionPathCandidate = {
    path_type: "CONTROLLED_EXECUTION_CONTINUITY_PATH_CANDIDATE",
    stages: [
      { stage: "sidepanel", status: "PREVIEW_ONLY", called: false },
      { stage: "service_worker", status: "NOT_CALLED", called: false },
      { stage: "Native Messaging host", status: "NOT_CALLED", called: false },
      { stage: "Python runtime bridge", status: "NOT_CALLED", called: false },
      { stage: "bounded Codex CLI provider", status: "NOT_CALLED", called: false }
    ]
  };
  const preview = {
    artifact_type: "CONTROLLED_EXECUTION_CONTINUITY_PREVIEW_V1",
    schema_version: "1.0",
    replay_identity: authorization.replay_identity || "UNKNOWN",
    provenance: {
      source: "EXPLICIT_DISPATCH_AUTHORIZATION_V1",
      dispatch_authorization_provenance: authorization.provenance || {},
      dispatch_authorization_status: authorization.dispatch_authorization_status || "UNKNOWN"
    },
    source_dispatch_authorization_hash: authorization.dispatch_authorization_hash || "UNKNOWN",
    source_handoff_preview_hash: authorization.source_handoff_preview_hash || "UNKNOWN",
    human_approval_hash: authorization.human_approval_hash || "UNKNOWN",
    governed_task_package_preview_hash: (authorization.provenance || {}).governed_task_package_preview_hash || "UNKNOWN",
    semantic_contract_candidate_hash: (authorization.provenance || {}).semantic_contract_candidate_hash || "NONE",
    admissibility_gate_hash: authorization.admissibility_gate_hash || "NONE",
    execution_continuity_status: ready ? "READY_FOR_CONTROLLED_EXECUTION_HANDOFF" : "EXECUTION_CONTINUITY_PREVIEW_REJECTED",
    execution_path_candidate: executionPathCandidate,
    native_messaging_path_candidate: { stage: "Native Messaging host", status: "NOT_CALLED", called: false },
    service_worker_path_candidate: { stage: "service_worker", status: "NOT_CALLED", called: false },
    python_runtime_bridge_candidate: { stage: "Python runtime bridge", status: "NOT_CALLED", called: false },
    codex_provider_candidate: { stage: "bounded Codex CLI provider", status: "NOT_CALLED", called: false },
    workspace_scope_candidate: authorization.workspace_scope_preview || "UNKNOWN",
    timeout_policy_candidate: authorization.timeout_policy_preview || "UNKNOWN",
    authority_boundary: {
      dispatch_authorized: ready,
      execution_authorized: false,
      execution_performed: false,
      codex_dispatch_performed: false,
      native_messaging_called: false,
      provider_invoked: false,
      autonomous_continuation_authorized: false
    },
    preview_only: true,
    execution_performed: false,
    codex_dispatch_performed: false,
    native_messaging_called: false,
    provider_invoked: false,
    provider_dispatch_performed: false,
    service_worker_called: false,
    executable: false,
    dispatched: false,
    autonomous_continuation_performed: false,
    classification: ["STRUCTURAL_ONLY", "ADVISORY_ONLY"]
  };
  preview.continuity_preview_hash = previewHash("CONTROLLED-EXECUTION-CONTINUITY-PREVIEW-HASH", {
    replay_identity: preview.replay_identity,
    source_dispatch_authorization_hash: preview.source_dispatch_authorization_hash,
    source_handoff_preview_hash: preview.source_handoff_preview_hash,
    human_approval_hash: preview.human_approval_hash,
    governed_task_package_preview_hash: preview.governed_task_package_preview_hash,
    semantic_contract_candidate_hash: preview.semantic_contract_candidate_hash,
    admissibility_gate_hash: preview.admissibility_gate_hash,
    execution_path_candidate: preview.execution_path_candidate,
    authority_boundary: preview.authority_boundary,
    execution_continuity_status: preview.execution_continuity_status
  });
  return canonicalize(preview);
}

function renderControlledExecutionContinuityPreview(preview) {
  setCockpitText(COCKPIT_IDS.controlledExecutionContinuityPreview, [
    "Controlled Execution Continuity Preview",
    "ARTIFACT_TYPE: CONTROLLED_EXECUTION_CONTINUITY_PREVIEW_V1",
    "CLASSIFICATION: STRUCTURAL_ONLY / ADVISORY_ONLY",
    "EXECUTION CONTINUITY PREVIEW ONLY",
    "NO EXECUTION",
    "NO CODEX DISPATCH",
    "NATIVE MESSAGING NOT CALLED",
    "PROVIDER NOT INVOKED",
    `execution_continuity_status: ${preview.execution_continuity_status}`,
    `continuity_preview_hash: ${preview.continuity_preview_hash}`,
    `execution_path_candidate: ${compactValue(preview.execution_path_candidate)}`,
    `native_messaging_path_candidate: ${compactValue(preview.native_messaging_path_candidate)}`,
    `service_worker_path_candidate: ${compactValue(preview.service_worker_path_candidate)}`,
    `python_runtime_bridge_candidate: ${compactValue(preview.python_runtime_bridge_candidate)}`,
    `codex_provider_candidate: ${compactValue(preview.codex_provider_candidate)}`,
    `workspace_scope_candidate: ${preview.workspace_scope_candidate}`,
    `timeout_policy_candidate: ${preview.timeout_policy_candidate}`,
    "all_stages: PREVIEW_ONLY / NOT_CALLED",
    "execution_performed: false",
    "codex_dispatch_performed: false",
    "native_messaging_called: false",
    "provider_invoked: false",
    "provider_dispatch_performed: false",
    "service_worker_called: false",
    "executable: false",
    "dispatched: false",
    "STOP: execution path candidate visible but not used"
  ].join("\n"));
}

function renderHumanApprovalGate(approval) {
  const handoffPreview = governedHandoffPackagePreview(latestChatgptIngressTaskPackagePreview || {}, approval);
  setCockpitText(COCKPIT_IDS.humanApprovalGate, [
    "Human Approval Gate",
    "ARTIFACT_TYPE: HUMAN_APPROVAL_GATE_V1",
    "CLASSIFICATION: STRUCTURAL_ONLY / ADVISORY_ONLY",
    "HUMAN APPROVAL ONLY",
    "NO EXECUTION",
    "NO CODEX DISPATCH",
    "APPROVAL EVIDENCE ONLY",
    `source_state: ${(approval.provenance || {}).source_state || "UNKNOWN"}`,
    `approval_status: ${approval.approval_status}`,
    `human_decision: ${approval.human_decision}`,
    `human_approved: ${approval.human_approved}`,
    `approval_reason: ${approval.approval_reason}`,
    `operator_label: ${approval.operator_label}`,
    `replay_identity: ${approval.replay_identity}`,
    `source_task_package_preview_hash: ${approval.source_task_package_preview_hash}`,
    `approval_hash: ${approval.approval_hash}`,
    "execution_performed: false",
    "codex_dispatch_performed: false",
    "provider_dispatch_performed: false",
    "autonomous_continuation_performed: false",
    "semantic_correctness_verified: false",
    "STOP: Approval evidence created; execution boundary remains uncrossed"
  ].join("\n"));
  renderGovernedHandoffPackagePreview(handoffPreview);
  setCockpitText(COCKPIT_IDS.chatgptIngressStop, [
    "STOP (No Execution)",
    "CLASSIFICATION: UI_ONLY",
    "PREVIEW_ONLY: true",
    "APPROVAL_EVIDENCE_ONLY: true",
    "STOP boundary after READY_FOR_HUMAN_APPROVAL",
    "STOP boundary after HUMAN APPROVAL GATE",
    "STOP boundary after GOVERNED HANDOFF PACKAGE PREVIEW",
    "STOP boundary after EXPLICIT DISPATCH AUTHORIZATION",
    `approval_status: ${approval.approval_status}`,
    `approval_hash: ${approval.approval_hash}`,
    `handoff_preview_status: ${handoffPreview.handoff_preview_status}`,
    `handoff_preview_hash: ${handoffPreview.handoff_preview_hash}`,
    "runtime_boundary: no Native Messaging, no service worker execution path, no Python runtime execution, no Codex provider",
    "execution_performed: false",
    "codex_dispatch_performed: false",
    "provider_dispatch_performed: false",
    "autonomous_continuation_performed: false"
  ].join("\n"));
}

function renderChatgptIngressPreview(preview = chatgptIngressPreviewImport()) {
  const acceptanceGate = chatgptIngressAcceptanceGate(preview);
  const taskPackagePreview = governedTaskPackagePreview(preview, acceptanceGate);
  latestChatgptIngressTaskPackagePreview = taskPackagePreview;
  const accepted = preview.governance_report.status === "ACCEPTED_FOR_STRUCTURAL_IMPORT";
  const rejected = preview.governance_report.status === "REJECTED";
  setCockpitText(COCKPIT_IDS.chatgptIngressNativeImportStatus, [
    "CHATGPT_INGRESS_NATIVE_IMPORT_PREVIEW_V1",
    "IMPORT ONLY",
    "PREVIEW ONLY",
    "NON-EXECUTING",
    `import_status: ${preview.governance_report.status}`,
    `rejection_reason: ${rejected ? compactValue(preview.governance_report.rejection_reason) : "none"}`,
    `accepted_visible: ${accepted}`,
    `rejected_visible: ${rejected}`,
    `replay_identity: ${preview.governance_report.replay_identity}`,
    `ingress_artifact_hash: ${preview.governance_report.ingress_artifact_hash}`,
    `semantic_output_hash: ${preview.governance_report.semantic_output_hash || (preview.artifact.hashes || {}).semantic_output_hash || "UNKNOWN"}`,
    `proposal_candidate_hash: ${preview.governance_report.proposal_candidate_hash}`,
    `contract_candidate_hash: ${preview.governance_report.contract_candidate_hash}`,
    `governance_report_hash: ${preview.governance_report.governance_report_hash}`,
    `gate_status: ${acceptanceGate.gate_status}`,
    `decision_hash: ${acceptanceGate.decision_hash}`,
    "execution performed: false",
    "Codex dispatch: false",
    "governance approved: false",
    "semantic correctness verified: false",
    "autonomous continuation: false"
  ].join("\n"));
  setCockpitText(COCKPIT_IDS.chatgptIngressArtifactPreview, chatgptIngressPreviewCard(
    "CHATGPT_INGRESS_ARTIFACT_V1",
    "STRUCTURAL_ONLY",
    [
      `replay_identity: ${preview.artifact.replay_identity}`,
      `ingress_artifact_hash: ${(preview.artifact.hashes || {}).artifact_hash || "UNKNOWN"}`,
      `semantic_output_hash: ${(preview.artifact.hashes || {}).semantic_output_hash || "UNKNOWN"}`,
      "live_chatgpt_invoked: false",
      "source: chatgpt artifact preview only"
    ]
  ));
  setCockpitText(COCKPIT_IDS.chatgptIngressImportValidation, chatgptIngressPreviewCard(
    "Import Validation",
    "STRUCTURAL_ONLY",
    [
      `status: ${preview.import_validation.status}`,
      `rejection_reason: ${compactValue((preview.import_validation.errors || []).join("; "))}`,
      `replay_identity: ${preview.import_validation.replay_identity}`,
      `ingress_artifact_hash: ${preview.import_validation.artifact_hash}`,
      "validation_scope: structural import validation only"
    ]
  ));
  setCockpitText(COCKPIT_IDS.chatgptIngressProposalCandidate, chatgptIngressPreviewCard(
    "Semantic Proposal Candidate",
    "ADVISORY_ONLY",
    [
      "proposal_candidate_only: true",
      `proposal_candidate_hash: ${preview.proposal_candidate.proposal_candidate_hash || "NONE"}`,
      `replay_identity: ${preview.proposal_candidate.replay_identity || "UNKNOWN"}`,
      `provenance_lineage: ${compactValue(preview.proposal_candidate.provenance_lineage)}`,
      "execution_authority: false",
      "codex_dispatch_allowed: false"
    ]
  ));
  setCockpitText(COCKPIT_IDS.chatgptIngressContractCandidate, chatgptIngressPreviewCard(
    "Semantic Contract Candidate",
    "STRUCTURAL_ONLY",
    [
      "contract_candidate_only: true",
      `contract_candidate_hash: ${preview.contract_candidate.contract_candidate_hash || "NONE"}`,
      `source_proposal_candidate_hash: ${preview.contract_candidate.source_proposal_candidate_hash || "NONE"}`,
      `replay_identity: ${preview.contract_candidate.replay_identity || "UNKNOWN"}`,
      "provider_dispatch_authorized: false"
    ]
  ));
  setCockpitText(COCKPIT_IDS.chatgptIngressGovernanceReport, chatgptIngressPreviewCard(
    "Governance Acceptance Report",
    "STRUCTURAL_ONLY",
    [
      `status: ${preview.governance_report.status}`,
      `governance_report_hash: ${preview.governance_report.governance_report_hash}`,
      `proposal_candidate_hash: ${preview.governance_report.proposal_candidate_hash}`,
      `contract_candidate_hash: ${preview.governance_report.contract_candidate_hash}`,
      `provenance_lineage: ${compactValue(preview.governance_report.provenance_lineage)}`
    ]
  ));
  setCockpitText(COCKPIT_IDS.chatgptIngressAcceptanceGate, chatgptIngressPreviewCard(
    "Acceptance Gate",
    "STRUCTURAL_ONLY",
    [
      "GATE ONLY",
      "NO EXECUTION",
      "NO CODEX DISPATCH",
      `gate_status: ${acceptanceGate.gate_status}`,
      `decision_hash: ${acceptanceGate.decision_hash}`,
      `admissibility_reasons: ${compactValue(acceptanceGate.admissibility_reasons)}`,
      `rejection_reasons: ${compactValue(acceptanceGate.rejection_reasons)}`,
      `authority_boundary_check: ${compactValue(acceptanceGate.authority_boundary_check)}`,
      `replay_continuity_check: ${compactValue(acceptanceGate.replay_continuity_check)}`,
      `provenance_check: ${compactValue(acceptanceGate.provenance_check)}`,
      `hash_integrity_check: ${compactValue(acceptanceGate.hash_integrity_check)}`,
      `semantic_correctness_check: ${compactValue(acceptanceGate.semantic_correctness_check)}`,
      `execution_boundary_check: ${compactValue(acceptanceGate.execution_boundary_check)}`,
      `provider_dispatch_check: ${compactValue(acceptanceGate.provider_dispatch_check)}`,
      `autonomous_continuation_check: ${compactValue(acceptanceGate.autonomous_continuation_check)}`,
      "execution_authorized: false",
      "codex_dispatch_authorized: false",
      "provider_dispatch_authorized: false",
      "governance_execution_approval: false",
      "autonomous_continuation_authorized: false"
    ]
  ));
  setCockpitText(COCKPIT_IDS.governedTaskPackagePreview, [
    "Governed Task Package Preview",
    "ARTIFACT_TYPE: GOVERNED_TASK_PACKAGE_PREVIEW_V1",
    "CLASSIFICATION: STRUCTURAL_ONLY / ADVISORY_ONLY",
    "PREVIEW ONLY",
    "NO EXECUTION",
    "NO CODEX DISPATCH",
    "HUMAN APPROVAL REQUIRED",
    `governance_status: ${taskPackagePreview.governance_status}`,
    `execution_boundary_state: ${taskPackagePreview.execution_boundary_state}`,
    `human_approval_required: ${taskPackagePreview.human_approval_required}`,
    `replay_identity: ${taskPackagePreview.replay_identity}`,
    `preview_hash: ${taskPackagePreview.preview_hash}`,
    `source_ingress_artifact_hash: ${taskPackagePreview.source_ingress_artifact_hash}`,
    `semantic_proposal_candidate_hash: ${taskPackagePreview.semantic_proposal_candidate_hash}`,
    `semantic_contract_candidate_hash: ${taskPackagePreview.semantic_contract_candidate_hash}`,
    `admissibility_gate_hash: ${taskPackagePreview.admissibility_gate_hash}`,
    `provenance_lineage: ${compactValue(taskPackagePreview.provenance)}`,
    "admissibility_continuity: visible",
    "preview_only: true",
    "executable: false",
    "dispatchable: false",
    "governance_finalized: false",
    "execution_authorized: false",
    "codex_dispatch_authorized: false",
    "provider_dispatch_authorized: false",
    "governance_execution_approved: false",
    "autonomous_continuation_authorized: false",
    "boundary: execution boundary reached but not crossed"
  ].join("\n"));
  setCockpitText(COCKPIT_IDS.humanApprovalGate, [
    "Human Approval Gate",
    "ARTIFACT_TYPE: HUMAN_APPROVAL_GATE_V1",
    "CLASSIFICATION: STRUCTURAL_ONLY / ADVISORY_ONLY",
    "HUMAN APPROVAL ONLY",
    "NO EXECUTION",
    "NO CODEX DISPATCH",
    "APPROVAL EVIDENCE ONLY",
    `source_state: ${taskPackagePreview.execution_boundary_state}`,
    "approval_status: not decided",
    "human_decision: none",
    "approval_hash: not generated",
    "execution_performed: false",
    "codex_dispatch_performed: false",
    "provider_dispatch_performed: false",
    "autonomous_continuation_performed: false"
  ].join("\n"));
  setCockpitText(COCKPIT_IDS.governedHandoffPackagePreview, [
    "Governed Handoff Package Preview",
    "ARTIFACT_TYPE: GOVERNED_HANDOFF_PACKAGE_PREVIEW_V1",
    "CLASSIFICATION: STRUCTURAL_ONLY / ADVISORY_ONLY",
    "HANDOFF PREVIEW ONLY",
    "NO EXECUTION",
    "NO CODEX DISPATCH",
    "NO PROVIDER DISPATCH",
    "EXPLICIT DISPATCH AUTHORIZATION REQUIRED",
    "handoff_preview_status: not generated",
    "handoff_boundary_state: READY_FOR_EXPLICIT_DISPATCH_AUTHORIZATION",
    "handoff_preview_hash: not generated",
    "human_approval_hash: not generated",
    "target_provider_boundary: BOUNDED_PROVIDER_DISPATCH_BOUNDARY_PREVIEW",
    "workspace_scope_preview: CURRENT_GOVERNED_WORKSPACE_ONLY_PREVIEW",
    "timeout_policy_preview: BOUNDED_TIMEOUT_REQUIRED_BEFORE_DISPATCH_AUTHORIZATION",
    "preview_only: true",
    "executable: false",
    "dispatchable: false",
    "execution_performed: false",
    "codex_dispatch_performed: false",
    "provider_dispatch_performed: false",
    "explicit_dispatch_authorization_required: true"
  ].join("\n"));
  setCockpitText(COCKPIT_IDS.explicitDispatchAuthorization, [
    "Explicit Dispatch Authorization",
    "ARTIFACT_TYPE: EXPLICIT_DISPATCH_AUTHORIZATION_V1",
    "CLASSIFICATION: STRUCTURAL_ONLY / ADVISORY_ONLY",
    "DISPATCH AUTHORIZATION ONLY",
    "NO EXECUTION",
    "NO CODEX DISPATCH",
    "NO PROVIDER EXECUTION",
    "NATIVE MESSAGING NOT CALLED",
    "dispatch_authorization_status: DISPATCH_REJECTED",
    "provider_boundary_state: not authorized",
    "dispatch_authorization_hash: not generated",
    "dispatch_authorized: false",
    "execution_performed: false",
    "codex_dispatch_performed: false",
    "provider_dispatch_performed: false",
    "native_messaging_called: false",
    "executable: false",
    "dispatched: false"
  ].join("\n"));
  setCockpitText(COCKPIT_IDS.controlledExecutionContinuityPreview, [
    "Controlled Execution Continuity Preview",
    "ARTIFACT_TYPE: CONTROLLED_EXECUTION_CONTINUITY_PREVIEW_V1",
    "CLASSIFICATION: STRUCTURAL_ONLY / ADVISORY_ONLY",
    "EXECUTION CONTINUITY PREVIEW ONLY",
    "NO EXECUTION",
    "NO CODEX DISPATCH",
    "NATIVE MESSAGING NOT CALLED",
    "PROVIDER NOT INVOKED",
    "execution_continuity_status: not generated",
    "continuity_preview_hash: not generated",
    "execution_path_candidate: sidepanel -> service_worker -> Native Messaging host -> Python runtime bridge -> bounded Codex CLI provider",
    "all_stages: PREVIEW_ONLY / NOT_CALLED",
    "execution_performed: false",
    "codex_dispatch_performed: false",
    "native_messaging_called: false",
    "provider_invoked: false",
    "service_worker_called: false"
  ].join("\n"));
  setCockpitText(COCKPIT_IDS.chatgptIngressStop, [
    "STOP (No Execution)",
    "CLASSIFICATION: UI_ONLY",
    "PREVIEW_ONLY: true",
    "IMPORT_ONLY: true",
    "STOP boundary after READY_FOR_HUMAN_APPROVAL",
    "STOP boundary after HUMAN APPROVAL GATE",
    "STOP boundary after GOVERNED HANDOFF PACKAGE PREVIEW",
    "STOP boundary after EXPLICIT DISPATCH AUTHORIZATION",
    "STOP boundary after CONTROLLED EXECUTION CONTINUITY PREVIEW",
    "runtime_boundary: no Native Messaging, no service worker execution path, no Python runtime execution, no Codex provider",
    `replay_identity: ${preview.artifact.replay_identity}`,
    `task_package_preview_hash: ${taskPackagePreview.preview_hash}`,
    `execution_boundary_state: ${taskPackagePreview.execution_boundary_state}`,
    `ingress_artifact_hash: ${(preview.artifact.hashes || {}).artifact_hash || "UNKNOWN"}`,
    `proposal_candidate_hash: ${preview.proposal_candidate.proposal_candidate_hash || "NONE"}`,
    `contract_candidate_hash: ${preview.contract_candidate.contract_candidate_hash || "NONE"}`,
    `governance_report_hash: ${preview.governance_report.governance_report_hash}`,
    `gate_status: ${acceptanceGate.gate_status}`,
    `decision_hash: ${acceptanceGate.decision_hash}`,
    "execution_performed: false",
    "codex_dispatch_performed: false",
    "governance_approved: false",
    "semantic_correctness_verified: false",
    "autonomous_continuation_performed: false"
  ].join("\n"));
}

function renderChatgptIngressInvalidJsonPreview(message) {
  renderChatgptIngressPreview(rejectedChatgptIngressPreview({
    reason: `INVALID_JSON: ${message}`,
    artifact: {}
  }));
}

function previewImportedChatgptIngressArtifactFromSidepanel() {
  const input = document.getElementById("chatgpt-ingress-artifact-json");
  const rawText = input && input.value ? input.value.trim() : "";
  if (!rawText) {
    renderChatgptIngressInvalidJsonPreview("empty CHATGPT_INGRESS_ARTIFACT_V1 JSON");
    return;
  }
  try {
    const artifact = JSON.parse(rawText);
    renderChatgptIngressPreview(chatgptIngressPreviewImport(artifact));
  } catch (error) {
    renderChatgptIngressInvalidJsonPreview(error.message || "invalid JSON");
  }
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
  if (
    entry.governed_chat_return
    && (
      entry.demo_id === "MINIMAL_END_TO_END_BRIDGE_SIDEPANEL_ATTACHMENT_V1"
      || entry.demo_id === "CANONICAL_BRIDGE_RESULT_ARTIFACT_EXPORT_IMPORT_V1"
    )
  ) {
    const bridgeReturn = entry.governed_chat_return;
    return [
      `Governed bridge ${String(bridgeReturn.status || "UNKNOWN").toLowerCase()}`,
      "",
      `Reason: ${compactValue(bridgeReturn.reason)}`,
      `Replay: ${compactValue(bridgeReturn.replay_visibility)}`,
      `Next: ${compactValue(bridgeReturn.next_recommended_step)}`,
      "",
      "Authority: ChatGPT = advisory cognition only; AiGOL = governance authority; Codex = bounded CLI provider only.",
      "REAL CODEX EXECUTION / BOUNDED CODEX CLI ONLY",
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
  const artifact = entry.bridge_result_artifact || {};
  const taskPackage = entry.task_package || {};
  const codexResult = entry.codex_cli_result || entry.mock_codex_result || {};
  const resultValidation = entry.result_validation || {};
  const governedReturn = entry.governed_chat_return || {};
  const replayIds = (entry.replay_events || []).map((event) => event.replay_event_id).join(", ") || "none";
  const proposal = latestProposal(entry);
  return [
    artifact.imported ? "SOURCE: CANONICAL PYTHON RESULT ARTIFACT" : "SOURCE: sidepanel runtime visibility",
    `STATUS: ${compactValue(bridge.status || entry.status)}`,
    `HUMAN REQUEST: ${compactValue(proposal.human_request || bridge.human_request)}`,
    `SEMANTIC PROPOSAL: ${compactValue(entry.proposal_id || proposal.proposal_id)}`,
    `GOVERNED TRANSPORT STATUS: ${compactValue(entry.transport_status || latestTransportReport(entry).status)}`,
    `GOVERNED TASK PACKAGE: ${compactValue(taskPackage.task_id)}`,
    `CODEX CLI RESULT: ${compactValue(codexResult.bounded_execution_status || codexResult.status)}`,
    `RESULT VALIDATION: ${compactValue(resultValidation.status)}`,
    `GOVERNED CHAT RETURN: ${compactValue(governedReturn.status)} - ${compactValue(governedReturn.reason)}`,
    `RECOMMENDED NEXT STEP: ${compactValue(governedReturn.next_recommended_step)}`,
    `SESSION: ${compactValue(entry.session_id || bridge.session_id)}`,
    `REPLAY EVENT IDS: ${replayIds}`,
    `REJECTION REASON: ${compactValue(governedReturn.status === "REJECTED" ? governedReturn.reason : "")}`,
    "AUTHORITY: ChatGPT advisory cognition only; AiGOL governance authority; Codex bounded CLI provider only.",
    "REAL_CODEX_EXECUTION",
    "BOUNDED_CODEX_CLI_PROVIDER",
    "NO AUTONOMOUS CONTINUATION"
  ].join("\n");
}

function canonicalBridgeResultArtifactStatusSummary(entry) {
  const artifact = entry.bridge_result_artifact || {};
  const verification = artifact.hash_verification || {};
  return [
    `CANONICAL PYTHON RESULT ARTIFACT: ${artifact.imported ? "imported" : entry.demo_id === "CANONICAL_BRIDGE_RESULT_ARTIFACT_EXPORT_IMPORT_V1" ? "rejected" : "not imported"}`,
    `ARTIFACT TYPE: ${compactValue(artifact.artifact_type || CANONICAL_BRIDGE_RESULT_ARTIFACT_TYPE)}`,
    `SCHEMA VERSION: ${compactValue(artifact.schema_version || CANONICAL_BRIDGE_RESULT_SCHEMA_VERSION)}`,
    `HASH STATUS: ${compactValue(verification.status || "not verified")}`,
    `ARTIFACT HASH: ${compactValue(artifact.artifact_hash || verification.artifact_hash)}`,
    `AUTHORITY: ${compactValue(artifact.authority || CANONICAL_BRIDGE_RESULT_AUTHORITY)}`,
    "HASH VERIFIED IS INTEGRITY ONLY",
    "CANONICAL IMPORT DOES NOT APPROVE, DISPATCH, EXECUTE, OR PERSIST",
    "REAL CODEX EXECUTION / BOUNDED CODEX CLI ONLY"
  ].join("\n");
}

function observatoryClassificationLegendSummary() {
  return [
    "ENFORCED: runtime gate or provider boundary",
    "STRUCTURAL_ONLY: schema, lineage, hash, or flag verification",
    "ADVISORY_ONLY: semantic/return context without authority",
    "UI_ONLY: descriptive sidepanel narration",
    "REAL governance markers identify runtime checks; DESCRIPTIVE markers identify labels and operator narration."
  ].join("\n");
}

function isCanonicalPythonRuntimeEntry(entry) {
  const artifact = entry.bridge_result_artifact || {};
  const native = entry.native_bridge || {};
  return artifact.imported === true || native.canonical_python_runtime === true || entry.demo_id === "NATIVE_MESSAGING_LOCAL_BRIDGE_V1";
}

function isJsOnlyBridgeEntry(entry) {
  return entry.demo_id === "MINIMAL_END_TO_END_BRIDGE_SIDEPANEL_ATTACHMENT_V1" || Boolean(entry.mock_codex_result);
}

function observatoryRuntimeMarker(entry) {
  if (isCanonicalPythonRuntimeEntry(entry)) {
    return "CANONICAL_NATIVE_PYTHON_RUNTIME_PATH";
  }
  if (isJsOnlyBridgeEntry(entry)) {
    return "JS_ONLY_DEMO_OR_MOCK_PATH";
  }
  if (entry.demo_id === "CHATGPT_SEMANTIC_PROPOSAL_IMPORT_V1") {
    return "LOCAL_SEMANTIC_PROPOSAL_IMPORT_PATH";
  }
  if (entry.demo_id) {
    return "SIDEPANEL_VISIBILITY_PATH";
  }
  return "NO_RUNTIME_PATH_RENDERED";
}

function observatoryProposal(entry) {
  return entry.semantic_proposal || {};
}

function observatoryTransportReport(entry) {
  const flow = entry.chat_first_flow || {};
  return entry.local_governed_transport_report || flow.transport_report || {};
}

function observatoryTaskPackage(entry) {
  return entry.task_package || {};
}

function observatorySemanticContract(entry) {
  const task = observatoryTaskPackage(entry);
  return task.semantic_contract || entry.semantic_contract || {};
}

function observatoryCodexResult(entry) {
  return entry.codex_cli_result || entry.mock_codex_result || {};
}

function observatoryHumanRequestValue(entry) {
  const proposal = observatoryProposal(entry);
  const bridge = entry.end_to_end_bridge || {};
  const task = observatoryTaskPackage(entry);
  const metadata = task.metadata || {};
  return proposal.human_request || metadata.human_request || bridge.human_request || "";
}

function observatoryHumanRequestSummary(entry) {
  const requestText = observatoryHumanRequestValue(entry);
  const sessionId = entry.session_id || (entry.end_to_end_bridge || {}).session_id || "unknown";
  const status = entry.status === "BLOCKED" ? "BLOCKED" : requestText ? "RECEIVED" : "NOT_STARTED";
  const requestId = requestText
    ? deterministicId("OBSERVATORY-REQUEST", { human_request: requestText, session_id: sessionId })
    : "unknown";
  return [
    `INPUT: ${compactValue(requestText)}`,
    `OUTPUT: ${requestText ? "request context captured for governed flow" : "no request rendered"}`,
    "AUTHORITY: UI_ONLY",
    "BOUNDARY: human text alone grants no approval, dispatch, execution, orchestration, or continuation",
    `STATUS: ${status}`,
    `REQUEST_ID: ${requestId}`,
    `SESSION_ID: ${compactValue(sessionId)}`,
    `RUNTIME_PATH: ${observatoryRuntimeMarker(entry)}`
  ].join("\n");
}

function observatorySemanticReasoningSummary(entry) {
  const proposal = observatoryProposal(entry);
  const requestText = observatoryHumanRequestValue(entry);
  const hasProposal = Boolean(proposal.proposal_id || proposal.semantic_intent);
  const constraints = [
    "no approval",
    "no dispatch",
    "no autonomous continuation",
    "semantic only"
  ];
  const ambiguities = hasProposal ? [] : ["semantic proposal not present in rendered artifact"];
  return [
    `INPUT: ${compactValue(requestText)}`,
    `OUTPUT: ${compactValue(proposal.semantic_intent)}`,
    "AUTHORITY: ADVISORY_ONLY",
    "BOUNDARY: LOCAL DETERMINISTIC NORMALIZATION; NON-AUTHORITATIVE; SEMANTIC ONLY",
    `STATUS: ${hasProposal ? "NORMALIZED" : "NOT_STARTED"}`,
    `NORMALIZATION_SOURCE: ${compactValue(proposal.proposal_id ? "LOCAL DETERMINISTIC NORMALIZATION" : "not rendered")}`,
    `inferred_intent: ${compactValue(proposal.semantic_intent)}`,
    `detected_domain: ${requestText ? "software_governance_runtime" : "unknown"}`,
    `constraints: ${compactValue(constraints)}`,
    `semantic_ambiguities: ${compactValue(ambiguities)}`,
    "REAL_OR_DESCRIPTIVE: ADVISORY_ONLY; not live ChatGPT cognition"
  ].join("\n");
}

function observatoryAigolGovernanceSummary(entry) {
  const transport = observatoryTransportReport(entry);
  const task = observatoryTaskPackage(entry);
  const proposal = observatoryProposal(entry);
  const metadata = task.metadata || {};
  const transportStatus = transport.status || entry.transport_status || "not invoked";
  const blocked = String(transportStatus).includes("REJECTED") || entry.status === "BLOCKED";
  const status = blocked ? "BLOCKED" : transportStatus === "TRANSPORT_ACCEPTED" ? "PASS" : "NOT_STARTED";
  return [
    `INPUT: ${compactValue(transport.transport_id || entry.transport_status || "transport envelope not rendered")}`,
    `OUTPUT: ${compactValue(transportStatus)}`,
    "AUTHORITY: ENFORCED",
    "BOUNDARY: REAL ENFORCEMENT for shape, session, hash, authority text, replay/lifecycle policy, and task package gate",
    `STATUS: ${status}`,
    `allowed_mutation_zones: ${compactValue(metadata.allowed_workspace_root || metadata.allowed_workspace_roots || "workspace boundary not rendered")}`,
    `replay_policy: ${compactValue((transport.transport_event || {}).visibility_scope || "session-local visibility")}`,
    `lifecycle_policy: ${compactValue(metadata.lifecycle_state || "visibility only")}`,
    `execution_scope: ${compactValue(metadata.authority || "bounded provider only after gateway")}`,
    `risk_class: ${compactValue(task.risk_class || proposal.risk_class)}`,
    `authority_boundary: ${compactValue(transport.authority_label || "SEMANTIC_TRANSPORT_ONLY")}`,
    `approval_state: ${compactValue(task.approval_required === true ? "NEEDS_APPROVAL" : task.approval_required === false ? "NO_APPROVAL_TOKEN_PRESENT" : "unknown")}`,
    `transport_validation_result: ${compactValue(transport.validation || transportStatus)}`,
    "REAL_OR_DESCRIPTIVE: REAL ENFORCEMENT where transport report/task validation exists; UI labels are descriptive only"
  ].join("\n");
}

function observatorySemanticContractSummary(entry) {
  const proposal = observatoryProposal(entry);
  const contract = observatorySemanticContract(entry);
  const status = contract.contract_id ? "CONTRACT_READY_FOR_GOVERNANCE" : "NOT_STARTED";
  return [
    `INPUT: ${compactValue(proposal.proposal_id || proposal.semantic_intent)}`,
    `OUTPUT: ${compactValue(contract.contract_id)}`,
    "AUTHORITY: STRUCTURAL_ONLY",
    "BOUNDARY: STRUCTURED_SEMANTIC_CONTRACT; NON_EXECUTION_AUTHORITY; input to governance, not execution authorization",
    `STATUS: ${status}`,
    "labels: STRUCTURED_SEMANTIC_CONTRACT, NON_EXECUTION_AUTHORITY, GOVERNANCE_MEDIATED, REPLAYABLE_SEMANTIC_CONTRACT",
    `human_request: ${compactValue(contract.human_request)}`,
    `semantic_intent: ${compactValue(contract.semantic_intent)}`,
    `requested_operation: ${compactValue(contract.requested_operation)}`,
    `allowed_scope: ${compactValue(contract.allowed_scope)}`,
    `expected_artifacts: ${compactValue(contract.expected_artifacts)}`,
    `expected_tests: ${compactValue(contract.expected_tests)}`,
    `forbidden_operations: ${compactValue(contract.forbidden_operations)}`,
    `completion_requirements: ${compactValue(contract.completion_requirements)}`,
    `ambiguities: ${compactValue(contract.ambiguities)}`,
    `authority_boundary: ${compactValue(contract.authority_boundary)}`,
    `semantic_source: ${compactValue(contract.semantic_source)}`,
    `contract_version: ${compactValue(contract.contract_version)}`,
    `artifact_hash: ${compactValue(contract.artifact_hash)}`,
    `provenance: ${compactValue(contract.provenance)}`
  ].join("\n");
}

function observatoryTaskPackageHash(taskPackage) {
  if (!taskPackage || !Object.keys(taskPackage).length) {
    return "unknown";
  }
  return deterministicId("TASK-PACKAGE-CANONICAL-HASH", taskPackage);
}

function observatoryTaskPackageSummary(entry) {
  const task = observatoryTaskPackage(entry);
  const metadata = task.metadata || {};
  const constraints = task.constraints || [];
  const forbidden = constraints.filter((constraint) => String(constraint).toLowerCase().includes("no "));
  const status = task.task_id ? "PACKAGED" : "NOT_STARTED";
  return [
    `INPUT: ${compactValue(entry.transport_status || observatoryTransportReport(entry).status || "validated transport not rendered")}`,
    `OUTPUT: ${compactValue(task.task_id)}`,
    "AUTHORITY: STRUCTURAL_ONLY",
    "BOUNDARY: WHAT CODEX ACTUALLY RECEIVES; bounded package is not semantic correctness proof",
    `STATUS: ${status}`,
    `codex_prompt: ${compactValue(task.codex_prompt)}`,
    `task_id: ${compactValue(task.task_id)}`,
    `proposal_id: ${compactValue(metadata.proposal_id || entry.proposal_id)}`,
    `allowed_paths: ${compactValue(metadata.allowed_workspace_root || metadata.allowed_workspace_roots)}`,
    `forbidden_operations: ${compactValue(forbidden)}`,
    `deterministic_constraints: ${compactValue(constraints)}`,
    `execution_scope: ${compactValue(metadata.execution_provider || metadata.authority)}`,
    `requested_mode: ${compactValue((observatoryProposal(entry) || {}).proposed_mode || task.requested_mode || "not rendered")}`,
    `canonical_artifact_hash: ${observatoryTaskPackageHash(task)}`,
    `provenance: ${isCanonicalPythonRuntimeEntry(entry) ? "CANONICAL_PYTHON_RUNTIME" : isJsOnlyBridgeEntry(entry) ? "JS_ONLY_DEMO_OR_MOCK_PATH" : "not rendered"}`
  ].join("\n");
}

function observatoryExecutionMode(entry, codexResult) {
  if (codexResult.provider_result || (codexResult.tests || []).some((test) => test.execution === "REAL_CODEX_CLI_BOUNDED")) {
    return "REAL_CODEX_EXECUTION";
  }
  if (entry.mock_codex_result || codexResult.result_id && String(codexResult.result_id).includes("MOCK")) {
    return "MOCK_EXECUTION";
  }
  if ((entry.native_bridge || {}).real_codex_execution === true || (entry.bridge_result_artifact || {}).real_codex_execution === true) {
    return "REAL_CODEX_EXECUTION";
  }
  return "NOT_STARTED";
}

function observatoryCodexExecutionSummary(entry) {
  const codexResult = observatoryCodexResult(entry);
  const providerResult = codexResult.provider_result || {};
  const executionMode = observatoryExecutionMode(entry, codexResult);
  const status = providerResult.status || codexResult.bounded_execution_status || codexResult.status || "NOT_STARTED";
  return [
    `INPUT: ${compactValue((observatoryTaskPackage(entry) || {}).task_id)}`,
    `OUTPUT: ${compactValue(codexResult.result_id || providerResult.task_package_id)}`,
    `AUTHORITY: ${executionMode === "NOT_STARTED" ? "UI_ONLY" : "ENFORCED"}`,
    "BOUNDARY: bounded provider invocation only; no autonomous continuation, retries, approval, or orchestration",
    `STATUS: ${compactValue(status)}`,
    `EXECUTION_KIND: ${executionMode}`,
    `commands_executed: ${compactValue(providerResult.command || [])}`,
    `files_touched: ${compactValue(codexResult.files_changed || [])}`,
    `tests_executed: ${compactValue(codexResult.tests || [])}`,
    `execution_duration: ${compactValue(providerResult.execution_duration || "not captured")}`,
    `provider_status: ${compactValue(providerResult.status || "not captured")}`,
    `timeout_state: ${status === "TIMEOUT" ? "TIMEOUT" : "not timed out"}`,
    `stdout_summary: ${compactValue(providerResult.stdout || codexResult.summary)}`,
    `stderr_summary: ${compactValue(providerResult.stderr)}`
  ].join("\n");
}

function observatoryPostExecutionVerificationSummary(entry) {
  const validation = entry.result_validation || {};
  const checks = validation.checks || {};
  const valid = validation.valid === true;
  const hasValidation = Boolean(validation.status || Object.keys(checks).length);
  const status = !hasValidation ? "NOT_STARTED" : valid ? "VERIFIED" : "REJECTED";
  return [
    `INPUT: ${compactValue((observatoryCodexResult(entry) || {}).result_id || (observatoryTaskPackage(entry) || {}).task_id)}`,
    `OUTPUT: ${compactValue(validation.status)}`,
    "AUTHORITY: STRUCTURAL_ONLY",
    "BOUNDARY: STRUCTURAL VERIFICATION ONLY; semantic correctness is not verified",
    `STATUS: ${status}`,
    `lineage_verification: ${compactValue(checks.result_lineage)}`,
    `replay_integrity: ${compactValue(checks.replay_visibility || "visible only")}`,
    `result_schema_validation: ${compactValue(checks.schema_valid || validation.valid)}`,
    `forbidden_authority_flag_detection: ${compactValue(checks.non_authority_semantics)}`,
    `lifecycle_verification: ${compactValue(checks.bounded_lifecycle)}`,
    `audit_verification: ${compactValue(validation.errors && validation.errors.length ? validation.errors : "no structural errors rendered")}`,
    "REAL_OR_DESCRIPTIVE: REAL structural validation where result_validation is present"
  ].join("\n");
}

function observatoryGovernedReturnSummary(entry) {
  const governedReturn = entry.governed_chat_return || {};
  const status = governedReturn.status || "NOT_STARTED";
  return [
    `INPUT: ${compactValue((entry.result_validation || {}).status)}`,
    `OUTPUT: ${compactValue(governedReturn.status)}`,
    "AUTHORITY: ADVISORY_ONLY",
    "BOUNDARY: GOVERNED OPERATOR RETURN; NOT LIVE CHATGPT INTERPRETATION",
    `STATUS: ${compactValue(status)}`,
    `governed_summary: ${compactValue(governedReturn.reason)}`,
    `detected_risks: ${compactValue((continuityReport(entry) || {}).continuity_risks || [])}`,
    `recommended_next_step: ${compactValue(governedReturn.next_recommended_step)}`,
    `authority_disclaimer: ${compactValue(governedReturn.non_authority_reminder || "No approval, dispatch, orchestration, repeated execution, or autonomous continuation authority was created.")}`,
    "REAL_OR_DESCRIPTIVE: advisory return summary only; no live ChatGPT interpretation"
  ].join("\n");
}

function observatoryTopologySummary(entry) {
  return [
    "TOPOLOGY: Human -> local deterministic normalization -> AiGOL governance gateway -> governed task package -> Codex execution layer -> AiGOL post-execution structural verification -> governed operator return",
    `CANONICAL_NATIVE_RUNTIME_PATH: ${isCanonicalPythonRuntimeEntry(entry)}`,
    `DEMO_OR_MOCK_PATH: ${isJsOnlyBridgeEntry(entry)}`,
    `JS_ONLY_PATH: ${isJsOnlyBridgeEntry(entry) || observatoryRuntimeMarker(entry) === "SIDEPANEL_VISIBILITY_PATH"}`,
    `CURRENT_PATH: ${observatoryRuntimeMarker(entry)}`,
    "REAL_ENFORCEMENT: service worker, native host, Python runtime, local transport handler, task package validation, Codex CLI provider boundary, result lineage validation",
    "DESCRIPTIVE_GOVERNANCE: sidepanel labels, operator narration, imported proposal headings, continuity summaries without canonical Python artifact",
    "CHATGPT_STATUS: no live ChatGPT invocation in this runtime path",
    "SEMANTIC_CORRECTNESS_STATUS: not verified"
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

function canonicalBridgeResultArtifactHashInput(artifact) {
  const canonicalArtifact = canonicalize(artifact || {});
  const { artifact_hash: artifactHash, ...hashInput } = canonicalArtifact;
  return hashInput;
}

async function canonicalBridgeResultArtifactHash(artifact) {
  const bytes = new TextEncoder().encode(JSON.stringify(canonicalBridgeResultArtifactHashInput(artifact)));
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  return `sha256:${Array.from(new Uint8Array(digest))
    .map((byte) => byte.toString(16).padStart(2, "0"))
    .join("")}`;
}

function validateCanonicalBridgeResultArtifactSchema(artifact) {
  const required = [
    "artifact_type",
    "schema_version",
    "authority",
    "session_id",
    "proposal_id",
    "replay_events",
    "task_package",
    "codex_cli_result",
    "result_validation",
    "governed_chat_return",
    "artifact_hash"
  ];
  const errors = [];
  if (!artifact || typeof artifact !== "object" || Array.isArray(artifact)) {
    return ["canonical bridge result artifact must be a JSON object"];
  }
  required.forEach((field) => {
    if (!(field in artifact)) {
      errors.push(`missing required field: ${field}`);
    }
  });
  if (artifact.artifact_type !== CANONICAL_BRIDGE_RESULT_ARTIFACT_TYPE) {
    errors.push("artifact_type must be MINIMAL_END_TO_END_BRIDGE_RESULT");
  }
  if (artifact.schema_version !== CANONICAL_BRIDGE_RESULT_SCHEMA_VERSION) {
    errors.push("schema_version must be 1");
  }
  if (artifact.authority !== CANONICAL_BRIDGE_RESULT_AUTHORITY) {
    errors.push("authority must be NON_EXECUTING_NON_AUTHORITATIVE");
  }
  if (!Array.isArray(artifact.replay_events)) {
    errors.push("replay_events must be an array");
  }
  return errors;
}

async function verifyCanonicalBridgeResultArtifactHash(artifact) {
  if (!artifact || typeof artifact !== "object" || Array.isArray(artifact)) {
    return canonicalize({
      status: "HASH_INVALID",
      errors: ["malformed canonical bridge result artifact"],
      artifact_hash: "unknown",
      computed_hash: "not_computed",
      artifact_identity: "unknown",
      replay_safe_integrity: false
    });
  }
  const artifactHash = artifact.artifact_hash;
  const artifactIdentity = artifact.proposal_id || artifact.session_id || "unknown";
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
  const computedHash = await canonicalBridgeResultArtifactHash(artifact);
  if (computedHash !== artifactHash) {
    return canonicalize({
      status: "HASH_MISMATCH",
      errors: ["canonical bridge result artifact_hash mismatch"],
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

function canonicalBridgeResultBlockedResult({ validationErrors, hashVerification }) {
  const errors = validationErrors.concat((hashVerification && hashVerification.errors) || []);
  return canonicalize({
    demo_id: "CANONICAL_BRIDGE_RESULT_ARTIFACT_EXPORT_IMPORT_V1",
    status: "BLOCKED",
    bridge_result_artifact: {
      source: "CANONICAL PYTHON RESULT ARTIFACT",
      imported: false,
      validation_status: "REJECTED",
      validation_errors: errors,
      hash_verification: hashVerification || {},
      authority: CANONICAL_BRIDGE_RESULT_AUTHORITY,
      real_codex_execution: true,
      bounded_codex_cli_only: true
    },
    governed_chat_return: {
      status: "REJECTED",
      reason: errors.join("; ") || "canonical bridge result artifact rejected",
      replay_visibility: "SESSION_LOCAL_REPLAY_VISIBLE",
      next_recommended_step: "Export a fresh canonical Python bridge result artifact and import it explicitly.",
      non_authority_reminder: "No execution occurred. No provider was invoked. No approval, dispatch, or continuation authority was created."
    },
    result_validation: {
      status: "RESULT_REJECTED",
      valid: false,
      errors
    },
    replay_events: [],
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

function canonicalBridgeResultFromArtifact(artifact, hashVerification) {
  const accepted = artifact.status === "BRIDGE_ACCEPTED" && artifact.result_validation && artifact.result_validation.valid === true;
  return canonicalize({
    demo_id: "CANONICAL_BRIDGE_RESULT_ARTIFACT_EXPORT_IMPORT_V1",
    status: accepted ? "RETURNED" : "BLOCKED",
    session_id: artifact.session_id,
    proposal_id: artifact.proposal_id,
    transport_status: artifact.transport_status,
    task_package: artifact.task_package || {},
    codex_cli_result: artifact.codex_cli_result || artifact.mock_codex_result || {},
    result_validation: artifact.result_validation || {},
    governed_chat_return: artifact.governed_chat_return || {},
    replay_events: artifact.replay_events || [],
    operator_visibility: artifact.operator_visibility || {},
    non_authority_guarantees: artifact.non_authority_guarantees || [],
    bridge_result_artifact: {
      source: "CANONICAL PYTHON RESULT ARTIFACT",
      imported: true,
      artifact_type: artifact.artifact_type,
      schema_version: artifact.schema_version,
      artifact_hash: artifact.artifact_hash,
      hash_verification: hashVerification,
      authority: artifact.authority,
      real_codex_execution: true,
      bounded_codex_cli_only: true
    },
    native_bridge: {
      label: "NATIVE_BRIDGE_LOCAL_ONLY",
      operator_triggered: true,
      canonical_python_runtime: true,
      real_codex_execution: true,
      provider: "CODEX_CLI",
      autonomous_continuation: false
    },
    end_to_end_bridge: {
      status: artifact.status,
      human_request: ((artifact.codex_cli_result || artifact.mock_codex_result || {}).summary) || "",
      session_id: artifact.session_id,
      canonical_python_result_artifact: true,
      compact_runtime_narration: true
    },
    continuity_report: {
      aggregate_governance_status: accepted ? "CONTINUITY_VALID" : "CONTINUITY_BOUNDARY_VIOLATION",
      replay_visibility_summary: { visible: true, reference_count: (artifact.replay_events || []).length, gaps: [], mutated: false },
      lifecycle_visibility_summary: { visible: true, reference_count: 5, gaps: [], mutated: false },
      authority_boundary_summary: { visible: true, statement_count: 1, violations: [], authority_created: false },
      semantic_boundary_summary: { visible: true, statement_count: 1, overclaims: [], semantic_authority_created: false },
      continuity_findings: ["Canonical Python bridge result artifact imported and rendered read-only."],
      continuity_risks: ["Artifact import verifies integrity only; it does not prove semantic correctness or grant authority."],
      continuity_recommendations: ["Use the canonical artifact as the sidepanel runtime truth for review-only lifecycle visibility."],
      lineage_summary: { visible: true, reference_count: 1, mutated: false }
    },
    authority_guarantees: {
      provider_calls: "CODEX_CLI_ONLY",
      dispatch: false,
      approval: false,
      execution: "BOUNDED_CODEX_CLI_ONLY",
      lifecycle_mutation: false,
      replay_mutation: false,
      persistence: false,
      orchestration: false,
      autonomous_continuation: false,
      hidden_authority: false
    }
  });
}

function nativeBridgeMessageFromSidepanel() {
  const requestInput = document.getElementById("chat-first-human-request");
  const artifactInput = document.getElementById("artifact");
  const sessionInput = document.getElementById("local-transport-session-id");
  const humanRequest = requestInput && requestInput.value
    ? requestInput.value
    : artifactInput && artifactInput.value ? artifactInput.value : "";
  const sessionId = sessionInput && sessionInput.value ? sessionInput.value : LOCAL_GOVERNED_TRANSPORT_SESSION_ID;
  return canonicalize({
    action: "RUN_MINIMAL_END_TO_END_BRIDGE",
    request_id: deterministicId("NATIVE-BRIDGE-REQUEST", {
      human_request: humanRequest,
      session_id: sessionId
    }),
    human_request: humanRequest,
    session_id: sessionId,
    operator_triggered: true,
    authority_boundary: "SEMANTIC_TRANSPORT_ONLY",
    labels: [
      "NATIVE_BRIDGE_LOCAL_ONLY",
      "OPERATOR_TRIGGERED",
      "CANONICAL_PYTHON_RUNTIME",
      "REAL_CODEX_EXECUTION",
      "BOUNDED_CODEX_CLI_PROVIDER",
      "NO_AUTONOMOUS_CONTINUATION"
    ]
  });
}

function nativeBridgeRejectedResult(reason) {
  return canonicalize({
    demo_id: "NATIVE_MESSAGING_LOCAL_BRIDGE_V1",
    status: "BLOCKED",
    bridge_result_artifact: {
      source: "NATIVE_BRIDGE_LOCAL_ONLY",
      imported: false,
      validation_status: "REJECTED",
      validation_errors: [reason],
      authority: CANONICAL_BRIDGE_RESULT_AUTHORITY,
      real_codex_execution: false,
      bounded_codex_cli_only: true
    },
    native_bridge: {
      label: "NATIVE_BRIDGE_LOCAL_ONLY",
      operator_triggered: true,
      canonical_python_runtime: true,
      real_codex_execution: false,
      provider: "CODEX_CLI",
      autonomous_continuation: false,
      rejection_reason: reason
    },
    governed_chat_return: {
      status: "REJECTED",
      reason,
      replay_visibility: "SESSION_LOCAL_REPLAY_VISIBLE",
      next_recommended_step: "Check the Native Messaging host installation and rerun explicitly.",
      non_authority_reminder: "No approval, dispatch, orchestration, repeated execution, or autonomous continuation authority was created."
    },
    result_validation: {
      status: "RESULT_REJECTED",
      valid: false,
      errors: [reason]
    },
    replay_events: [],
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

function nativeBridgeLoadingResult() {
  return canonicalize({
    demo_id: "NATIVE_MESSAGING_SERVICE_WORKER_RUNTIME_FIX_V1",
    status: "RUNNING",
    bridge_result_artifact: {
      source: "MV3_SERVICE_WORKER_NATIVE_BRIDGE",
      imported: false,
      validation_status: "PENDING",
      validation_errors: [],
      authority: CANONICAL_BRIDGE_RESULT_AUTHORITY,
      real_codex_execution: false,
      bounded_codex_cli_only: true
    },
    native_bridge: {
      label: "NATIVE_BRIDGE_LOCAL_ONLY",
      runtime_controller: "SERVICE_WORKER_RUNTIME_CONTROLLER",
      operator_triggered: true,
      loading: true,
      autonomous_continuation: false
    },
    governed_chat_return: {
      status: "RUNNING",
      reason: "Native bridge request sent to MV3 service worker.",
      replay_visibility: "SESSION_LOCAL_REPLAY_VISIBLE",
      next_recommended_step: "Wait for the service worker to return the canonical Python runtime result.",
      non_authority_reminder: "Operator-triggered only. No approval, dispatch, orchestration, or autonomous continuation authority is created."
    },
    result_validation: {
      status: "PENDING",
      valid: false,
      errors: []
    },
    replay_events: [],
    authority_guarantees: {
      provider_calls: "CODEX_CLI_ONLY",
      dispatch: false,
      approval: false,
      execution: "BOUNDED_CODEX_CLI_ONLY",
      lifecycle_mutation: false,
      replay_mutation: false,
      persistence: false,
      orchestration: false,
      autonomous_continuation: false,
      hidden_authority: false
    }
  });
}

function nativeBridgeRuntimeFailureResult(response) {
  const error = response && response.error ? response.error : {};
  const code = error.code || "SERVICE_WORKER_NATIVE_BRIDGE_ERROR";
  const message = error.message || "Native bridge service worker failed.";
  const result = nativeBridgeRejectedResult(`${code}: ${message}`);
  result.demo_id = "NATIVE_MESSAGING_SERVICE_WORKER_RUNTIME_FIX_V1";
  result.native_bridge = canonicalize({
    ...(result.native_bridge || {}),
    runtime_controller: "SERVICE_WORKER_RUNTIME_CONTROLLER",
    runtime_failure_state: true,
    error_code: code,
    error_message: message
  });
  result.governed_chat_return.reason = `${code}: ${message}`;
  return canonicalize(result);
}

async function renderNativeBridgeResponse(response) {
  if (!response || response.status !== "NATIVE_BRIDGE_ACCEPTED" || !response.result_artifact) {
    window.sidepanelRenderResult(nativeBridgeRejectedResult(
      response && response.rejection_reason ? response.rejection_reason : "native bridge response rejected"
    ));
    return;
  }
  const artifact = canonicalize(response.result_artifact);
  const schemaErrors = validateCanonicalBridgeResultArtifactSchema(artifact);
  const hashVerification = await verifyCanonicalBridgeResultArtifactHash(artifact);
  if (schemaErrors.length || hashVerification.status !== "HASH_VERIFIED") {
    window.sidepanelRenderResult(canonicalBridgeResultBlockedResult({
      validationErrors: schemaErrors.concat(hashVerification.errors || []),
      hashVerification
    }));
    return;
  }
  const result = canonicalBridgeResultFromArtifact(artifact, hashVerification);
  result.demo_id = "NATIVE_MESSAGING_LOCAL_BRIDGE_V1";
  result.native_bridge = canonicalize({
    ...(result.native_bridge || {}),
    response_status: response.status,
    request_id: response.request_id || "UNKNOWN",
    labels: response.labels || []
  });
  window.sidepanelRenderResult(canonicalize(result));
}

function runNativeBridgeFromSidepanel() {
  window.sidepanelRenderResult(nativeBridgeLoadingResult());
  if (typeof chrome === "undefined" || !chrome.runtime || !chrome.runtime.sendMessage) {
    window.sidepanelRenderResult(nativeBridgeRuntimeFailureResult({
      error: {
        code: "NATIVE_BRIDGE_UNAVAILABLE",
        message: "Chrome runtime messaging is unavailable in this context."
      }
    }));
    return;
  }
  const message = nativeBridgeMessageFromSidepanel();
  chrome.runtime.sendMessage({
    action: SERVICE_WORKER_NATIVE_BRIDGE_ACTION,
    operator_triggered: true,
    native_message: message
  }, (response) => {
    const runtimeError = chrome.runtime.lastError;
    if (runtimeError) {
      window.sidepanelRenderResult(nativeBridgeRuntimeFailureResult({
        error: {
          code: "SERVICE_WORKER_UNAVAILABLE",
          message: runtimeError.message || "service worker native bridge invocation failed"
        }
      }));
      return;
    }
    if (!response || response.status !== "SERVICE_WORKER_NATIVE_BRIDGE_RETURNED") {
      window.sidepanelRenderResult(nativeBridgeRuntimeFailureResult(response || {
        error: {
          code: "INVALID_RESPONSE",
          message: "Service worker returned an invalid native bridge response."
        }
      }));
      return;
    }
    renderNativeBridgeResponse(response.native_response);
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

async function importCanonicalBridgeResultFromSidepanel() {
  const fileInput = document.getElementById("bridge-result-artifact-file");
  const file = fileInput && fileInput.files ? fileInput.files[0] : null;
  if (!file) {
    window.sidepanelRenderResult(canonicalBridgeResultBlockedResult({
      validationErrors: ["missing bridge_result_artifact.json file selection"],
      hashVerification: {
        status: "HASH_MISSING",
        errors: ["missing bridge_result_artifact.json file selection"],
        artifact_hash: "missing",
        computed_hash: "not_computed",
        artifact_identity: "unknown",
        replay_safe_integrity: false
      }
    }));
    return;
  }
  let parsedArtifact = {};
  let validationErrors = [];
  let hashVerification = {};
  try {
    parsedArtifact = canonicalize(JSON.parse(await file.text()));
    validationErrors = validateCanonicalBridgeResultArtifactSchema(parsedArtifact);
    hashVerification = await verifyCanonicalBridgeResultArtifactHash(parsedArtifact);
    if (hashVerification.status !== "HASH_VERIFIED") {
      validationErrors = validationErrors.concat(hashVerification.errors);
    }
  } catch (error) {
    validationErrors = ["invalid canonical bridge result artifact JSON"];
    hashVerification = {
      status: "HASH_INVALID",
      errors: ["invalid canonical bridge result artifact JSON"],
      artifact_hash: "unknown",
      computed_hash: "not_computed",
      artifact_identity: "unknown",
      replay_safe_integrity: false
    };
  }
  const result = validationErrors.length
    ? canonicalBridgeResultBlockedResult({ validationErrors, hashVerification })
    : canonicalBridgeResultFromArtifact(parsedArtifact, hashVerification);
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
  setCockpitText(COCKPIT_IDS.canonicalBridgeResultArtifactStatus, canonicalBridgeResultArtifactStatusSummary(latest));
  setCockpitText(COCKPIT_IDS.observatoryTopology, observatoryTopologySummary(latest));
  setCockpitText(COCKPIT_IDS.observatoryClassificationLegend, observatoryClassificationLegendSummary());
  setCockpitText(COCKPIT_IDS.observatoryHumanRequest, observatoryHumanRequestSummary(latest));
  setCockpitText(COCKPIT_IDS.observatorySemanticReasoning, observatorySemanticReasoningSummary(latest));
  setCockpitText(COCKPIT_IDS.observatorySemanticContract, observatorySemanticContractSummary(latest));
  setCockpitText(COCKPIT_IDS.observatorySemanticContractJson, artifactJson(observatorySemanticContract(latest)));
  setCockpitText(COCKPIT_IDS.observatoryAigolGovernance, observatoryAigolGovernanceSummary(latest));
  setCockpitText(COCKPIT_IDS.observatoryTaskPackage, observatoryTaskPackageSummary(latest));
  setCockpitText(COCKPIT_IDS.observatoryTaskPackageJson, artifactJson(observatoryTaskPackage(latest)));
  setCockpitText(COCKPIT_IDS.observatoryCodexExecution, observatoryCodexExecutionSummary(latest));
  setCockpitText(COCKPIT_IDS.observatoryPostVerification, observatoryPostExecutionVerificationSummary(latest));
  setCockpitText(COCKPIT_IDS.observatoryGovernedReturn, observatoryGovernedReturnSummary(latest));
  renderChatgptIngressPreview();
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

const importCanonicalBridgeResultButton = document.getElementById("import-canonical-bridge-result");
if (importCanonicalBridgeResultButton) {
  importCanonicalBridgeResultButton.onclick = importCanonicalBridgeResultFromSidepanel;
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

const runNativeBridgeButton = document.getElementById("run-native-bridge");
if (runNativeBridgeButton) {
  runNativeBridgeButton.onclick = runNativeBridgeFromSidepanel;
}

const previewChatgptIngressImportOnlyButton = document.getElementById("preview-chatgpt-ingress-import-only");
if (previewChatgptIngressImportOnlyButton) {
  previewChatgptIngressImportOnlyButton.onclick = previewImportedChatgptIngressArtifactFromSidepanel;
}

const approveTaskPackagePreviewButton = document.getElementById("approve-task-package-preview");
if (approveTaskPackagePreviewButton) {
  approveTaskPackagePreviewButton.onclick = function approveTaskPackagePreviewEvidenceOnly() {
    renderHumanApprovalGate(humanApprovalGate(latestChatgptIngressTaskPackagePreview || {}, "APPROVE"));
  };
}

const rejectTaskPackagePreviewButton = document.getElementById("reject-task-package-preview");
if (rejectTaskPackagePreviewButton) {
  rejectTaskPackagePreviewButton.onclick = function rejectTaskPackagePreviewEvidenceOnly() {
    renderHumanApprovalGate(humanApprovalGate(latestChatgptIngressTaskPackagePreview || {}, "REJECT"));
  };
}

const authorizeDispatchPreviewButton = document.getElementById("authorize-dispatch-preview");
if (authorizeDispatchPreviewButton) {
  authorizeDispatchPreviewButton.onclick = function authorizeDispatchPreviewEvidenceOnly() {
    renderExplicitDispatchAuthorization(explicitDispatchAuthorization(latestGovernedHandoffPackagePreview || {}, "AUTHORIZE"));
  };
}

const rejectDispatchPreviewButton = document.getElementById("reject-dispatch-preview");
if (rejectDispatchPreviewButton) {
  rejectDispatchPreviewButton.onclick = function rejectDispatchPreviewEvidenceOnly() {
    renderExplicitDispatchAuthorization(explicitDispatchAuthorization(latestGovernedHandoffPackagePreview || {}, "REJECT"));
  };
}

renderChatgptIngressPreview();
