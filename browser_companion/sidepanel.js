const lifecycleEntries = [];

const COCKPIT_IDS = {
  replayTimeline: "replay-timeline",
  lifecycleView: "lifecycle-view",
  approvalVisibility: "approval-visibility",
  governanceBoundary: "governance-boundary",
  semanticDirection: "semantic-direction"
};

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
