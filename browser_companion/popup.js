const LOCAL_ENDPOINT = "http://127.0.0.1:8110/governed-invoke";
const LOCAL_INTERPRET_ENDPOINT = "http://127.0.0.1:8110/governed-interpret";
const ARTIFACT_PATTERN = /^[A-Z0-9_-]{1,96}$/;
let confirmedArtifact = null;
let pendingArtifact = null;

function canonicalize(value) {
  if (Array.isArray(value)) {
    return value.map(canonicalize);
  }
  if (value && typeof value === "object") {
    return Object.keys(value)
      .sort()
      .reduce((result, key) => {
        result[key] = canonicalize(value[key]);
        return result;
      }, {});
  }
  return value;
}

async function sha256(value) {
  const bytes = new TextEncoder().encode(JSON.stringify(canonicalize(value)));
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  return Array.from(new Uint8Array(digest))
    .map((byte) => byte.toString(16).padStart(2, "0"))
    .join("");
}

function validateArtifact(artifact) {
  return typeof artifact === "string" && ARTIFACT_PATTERN.test(artifact);
}

async function buildGovernedRequest(artifact) {
  if (!validateArtifact(artifact)) {
    throw new Error("Artifact must use only A-Z, 0-9, underscore, or dash.");
  }
  const requestPayload = {
    interaction_identity: `OPERATOR-INTERACTION-${artifact}`,
    interaction_payload: {
      interaction_intent: `invoke artifact ${artifact}`,
      connector_name: "local_execution",
      request_payload: {
        operation_intent: `invoke artifact ${artifact}`,
        authorized_execution: true
      },
      hidden_continuation_present: false,
      orchestration_present: false,
      hidden_routing_present: false,
      hidden_execution_present: false,
      hidden_mutable_state_present: false
    }
  };
  const lineage = {
    governed_session_id: "OPERATOR-GOVERNED-SESSION",
    runtime_activation_gate_id: "GATE-1",
    runtime_operation_envelope_id: "ENV-1",
    runtime_execution_surface_id: "SURFACE-1"
  };
  const replayIdentity = await sha256({ request_payload: requestPayload, lineage });
  return {
    preview_runtime_request_id: `PREVIEW-RUNTIME-REQUEST-${replayIdentity.slice(0, 24)}`,
    request_payload: requestPayload,
    lineage,
    replay_identity: replayIdentity,
    bounded: true
  };
}

function validateRuntimeResponse(response) {
  if (!response || typeof response !== "object") return false;
  const evidence = response.evidence;
  return response.status === "RETURNED"
    && response.closure === "PASS"
    && typeof response.preview_runtime_request_id === "string"
    && typeof response.preview_runtime_response_id === "string"
    && typeof response.invocation_replay_identity === "string"
    && evidence
    && evidence.localhost_only === true
    && evidence.replay_safe === true
    && evidence.response_returned === true
    && evidence.hidden_execution_present === false;
}

function summarizeRuntimeResponse(response) {
  return {
    status: response.status,
    closure: response.closure,
    request_id: response.preview_runtime_request_id,
    response_id: response.preview_runtime_response_id,
    replay_identity: response.invocation_replay_identity,
    evidence: {
      localhost_only: response.evidence.localhost_only,
      replay_safe: response.evidence.replay_safe,
      response_returned: response.evidence.response_returned
    }
  };
}

function renderResult(summary) {
  const result = document.getElementById("result");
  result.className = summary.status === "RETURNED" ? "returned" : "blocked";
  result.textContent = JSON.stringify(summary, null, 2);
}

function validateInterpretation(response) {
  return response
    && response.status === "INTERPRETED"
    && response.requires_confirmation === true
    && response.allowed_to_execute_automatically === false
    && response.replay_visible === true
    && validateArtifact(response.artifact_candidate);
}

async function previewIntent() {
  const text = document.getElementById("artifact").value.trim();
  try {
    const response = await fetch(LOCAL_INTERPRET_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ natural_language: text })
    });
    const payload = await response.json();
    if (!validateInterpretation(payload)) {
      throw new Error("Intent interpretation failed governed validation.");
    }
    pendingArtifact = payload.artifact_candidate;
    confirmedArtifact = null;
    renderResult({
      status: payload.status,
      intent_class: payload.intent_class,
      governance_mode: payload.governance_mode,
      artifact_candidate: payload.artifact_candidate,
      replay_identity: payload.replay_identity,
      requires_confirmation: payload.requires_confirmation,
      allowed_to_execute_automatically: payload.allowed_to_execute_automatically
    });
  } catch (error) {
    pendingArtifact = null;
    confirmedArtifact = null;
    renderResult({ status: "BLOCKED", error: error.message });
  }
}

function confirmIntentPreview() {
  if (!pendingArtifact) {
    renderResult({ status: "BLOCKED", error: "No governed preview is available to confirm." });
    return;
  }
  confirmedArtifact = pendingArtifact;
  renderResult({
    status: "CONFIRMED",
    artifact_candidate: confirmedArtifact,
    requires_confirmation: false,
    allowed_to_execute_automatically: false
  });
}

async function invokeGovernedRuntime() {
  const mode = document.getElementById("mode").value;
  const artifact = mode === "intent" ? confirmedArtifact : document.getElementById("artifact").value.trim();
  try {
    if (mode === "intent" && !artifact) {
      throw new Error("Explicit confirmation is required before invoke.");
    }
    const request = await buildGovernedRequest(artifact);
    const response = await fetch(LOCAL_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request)
    });
    const payload = await response.json();
    if (!validateRuntimeResponse(payload)) {
      throw new Error("Runtime response failed governed validation.");
    }
    renderResult(summarizeRuntimeResponse(payload));
  } catch (error) {
    renderResult({ status: "BLOCKED", error: error.message });
  }
}

document.getElementById("preview").addEventListener("click", previewIntent);
document.getElementById("confirm").addEventListener("click", confirmIntentPreview);
document.getElementById("invoke").addEventListener("click", invokeGovernedRuntime);
