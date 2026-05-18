const LOCAL_ENDPOINT = "http://127.0.0.1:8110/governed-invoke";
const LOCAL_INTERPRET_ENDPOINT = "http://127.0.0.1:8110/governed-interpret";
const LOCAL_CODEX_SYNTHESIS_ENDPOINT = "http://127.0.0.1:8110/governed-codex-synthesize";
const LOCAL_CODEX_HANDOFF_ENDPOINT = "http://127.0.0.1:8110/governed-codex-handoff";
const LOCAL_EXECUTION_AUTHORIZE_ENDPOINT = "http://127.0.0.1:8110/governed-execution-authorize";
const LOCAL_EXECUTION_CONSUME_ENDPOINT = "http://127.0.0.1:8110/governed-execution-consume";
const LOCAL_CODEX_EXECUTE_ENDPOINT = "http://127.0.0.1:8110/governed-codex-execute";
const LOCAL_EXECUTION_OBSERVE_ENDPOINT = "http://127.0.0.1:8110/governed-execution-observe";
const LOCAL_CHATGPT_BRIDGE_ENDPOINT = "http://127.0.0.1:8110/governed-chatgpt-bridge";
const LOCAL_INTENT_TRANSFER_ENDPOINT = "http://127.0.0.1:8110/governed-intent-transfer";
const ARTIFACT_PATTERN = /^[A-Z0-9_-]{1,96}$/;
let confirmedArtifact = null;
let pendingArtifact = null;
let pendingCodexSynthesis = null;
let confirmedCodexSynthesis = null;
let confirmedHandoffPackage = null;
let currentAuthorityToken = null;
let latestConsumerResponse = null;
let latestAdapterResponse = null;
let pendingConversationBridge = null;

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

function validateCodexSynthesis(response) {
  return response
    && response.status === "SYNTHESIZED"
    && response.requires_confirmation === true
    && response.allowed_to_execute_automatically === false
    && response.replay_visible === true
    && typeof response.codex_prompt_preview === "string";
}

function validateConversationBridge(response) {
  return response
    && response.status === "NORMALIZED"
    && response.requires_confirmation === true
    && response.allowed_to_execute_automatically === false
    && response.replay_visible === true
    && response.bridge_boundary_state
    && response.bridge_boundary_state.chatgpt_authority === false
    && response.bridge_boundary_state.execution_authority === false;
}

async function previewIntent() {
  const mode = document.getElementById("mode").value;
  const text = document.getElementById("artifact").value.trim();
  try {
    if (mode === "conversation") {
      const response = await fetch(LOCAL_CHATGPT_BRIDGE_ENDPOINT, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ conversational_input: text })
      });
      const payload = await response.json();
      if (!validateConversationBridge(payload)) {
        throw new Error("Conversational bridge failed governed validation.");
      }
      pendingConversationBridge = payload;
      renderResult({
        status: payload.status,
        original_conversational_request: text,
        normalized_governed_request: payload.normalized_request,
        replay_identity: payload.replay_identity,
        governance_mode: payload.governance_mode,
        bridge_boundary_guarantees: payload.bridge_boundary_state,
        requires_confirmation: payload.requires_confirmation,
        explicit_statement: "ChatGPT reasoning is non-authoritative and cannot directly trigger execution."
      });
      return;
    }
    const endpoint = mode === "codex" ? LOCAL_CODEX_SYNTHESIS_ENDPOINT : LOCAL_INTERPRET_ENDPOINT;
    const response = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ natural_language: text })
    });
    const payload = await response.json();
    if (mode === "codex") {
      if (!validateCodexSynthesis(payload)) {
        throw new Error("Codex synthesis failed governed validation.");
      }
      pendingArtifact = null;
      confirmedArtifact = null;
      pendingCodexSynthesis = payload;
      confirmedCodexSynthesis = null;
      confirmedHandoffPackage = null;
      currentAuthorityToken = null;
      latestConsumerResponse = null;
      latestAdapterResponse = null;
      pendingConversationBridge = null;
      renderResult({
        status: payload.status,
        task_class: payload.task_class,
        governance_mode: payload.governance_mode,
        replay_identity: payload.replay_identity,
        codex_prompt_preview: payload.codex_prompt_preview,
        blocked_capability_checks: payload.blocked_capability_checks,
        requires_confirmation: payload.requires_confirmation,
        allowed_to_execute_automatically: payload.allowed_to_execute_automatically
      });
      return;
    }
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
    pendingCodexSynthesis = null;
    confirmedCodexSynthesis = null;
    confirmedHandoffPackage = null;
    currentAuthorityToken = null;
    latestConsumerResponse = null;
    latestAdapterResponse = null;
    pendingConversationBridge = null;
    renderResult({ status: "BLOCKED", error: error.message });
  }
}

function confirmIntentPreview() {
  if (document.getElementById("mode").value === "conversation") {
    if (!pendingConversationBridge) {
      renderResult({ status: "BLOCKED", error: "No conversational bridge preview is available to confirm." });
      return;
    }
    renderResult({
      status: "CONFIRMED",
      normalized_governed_request: pendingConversationBridge.normalized_request,
      downstream_governance_request: pendingConversationBridge.downstream_governance_request,
      requires_confirmation: false,
      allowed_to_execute_automatically: false,
      explicit_statement: "ChatGPT reasoning is non-authoritative and cannot directly trigger execution."
    });
    return;
  }
  if (document.getElementById("mode").value === "codex") {
    if (!pendingCodexSynthesis) {
      renderResult({ status: "BLOCKED", error: "No governed Codex preview is available to confirm." });
      return;
    }
    confirmedCodexSynthesis = pendingCodexSynthesis;
    renderResult({
      status: "CONFIRMED",
      requires_confirmation: false,
      allowed_to_execute_automatically: false,
      downstream_handoff_prepared: true
    });
    return;
  }
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

function validateHandoffPackage(response) {
  return response
    && response.status === "HANDOFF_READY"
    && response.requires_confirmation === true
    && response.allowed_to_execute_automatically === false
    && response.downstream_execution_authority === false
    && typeof response.replay_identity === "string";
}

function validateIntentTransferPackage(response) {
  return response
    && response.status === "TRANSFER_READY"
    && response.requires_preview === true
    && response.requires_confirmation === true
    && response.execution_authority === false
    && response.chatgpt_authority === false
    && response.package
    && response.package.transfer_boundary_statement === "This transfer package is non-executing and requires explicit governance preview and confirmation.";
}

function exportJsonFile(filename, value) {
  const blob = new Blob([JSON.stringify(canonicalize(value), null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}

async function exportGovernedHandoffPackage() {
  if (document.getElementById("mode").value !== "codex" || !confirmedCodexSynthesis) {
    renderResult({ status: "BLOCKED", error: "Explicit Codex preview confirmation is required before export." });
    return;
  }
  const originalHumanRequest = document.getElementById("artifact").value.trim();
  try {
    const response = await fetch(LOCAL_CODEX_HANDOFF_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        synthesis_response: confirmedCodexSynthesis,
        original_human_request: originalHumanRequest
      })
    });
    const payload = await response.json();
    if (!validateHandoffPackage(payload)) {
      throw new Error("Handoff package failed governed validation.");
    }
    confirmedHandoffPackage = payload;
    exportJsonFile(`governed_codex_handoff_${payload.replay_identity}.json`, payload);
    renderResult({
      status: payload.status,
      replay_identity: payload.replay_identity,
      blocked_capabilities: payload.blocked_capabilities,
      downstream_execution_authority: payload.downstream_execution_authority,
      export_confirmed: true
    });
  } catch (error) {
    renderResult({ status: "BLOCKED", error: error.message });
  }
}

async function exportGovernedIntentTransferPackage() {
  if (document.getElementById("mode").value !== "conversation" || !pendingConversationBridge) {
    renderResult({ status: "BLOCKED", error: "Conversational bridge preview is required before transfer export." });
    return;
  }
  const conversationalInput = document.getElementById("artifact").value.trim();
  try {
    const response = await fetch(LOCAL_INTENT_TRANSFER_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        conversational_input: conversationalInput,
        normalized_governed_request: pendingConversationBridge.normalized_request,
        governance_mode: pendingConversationBridge.governance_mode,
        replay_identity: pendingConversationBridge.replay_identity
      })
    });
    const payload = await response.json();
    if (!validateIntentTransferPackage(payload)) {
      throw new Error("Intent transfer package failed governed validation.");
    }
    exportJsonFile(`governed_intent_transfer_${payload.transfer_identity}.json`, payload.package);
    renderResult({
      status: payload.status,
      conversational_input: conversationalInput,
      normalized_governed_request: payload.package.normalized_governed_request,
      transfer_identity: payload.transfer_identity,
      replay_identity: payload.replay_identity,
      boundary_guarantees: payload.boundary_state,
      transfer_boundary_statement: payload.package.transfer_boundary_statement,
      export_confirmed: true
    });
  } catch (error) {
    renderResult({ status: "BLOCKED", error: error.message });
  }
}

function validateExecutionAuthorization(response) {
  return response
    && response.status === "AUTHORIZED"
    && response.downstream_execution_authority === true
    && response.revocation_supported === true
    && typeof response.token_id === "string"
    && typeof response.authorization_expiration === "string";
}

async function requestExecutionAuthorization() {
  if (document.getElementById("mode").value !== "codex" || !confirmedHandoffPackage) {
    renderResult({ status: "BLOCKED", error: "Exported handoff package is required before authorization." });
    return;
  }
  try {
    const response = await fetch(LOCAL_EXECUTION_AUTHORIZE_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        handoff_package: confirmedHandoffPackage,
        approved_by: "human",
        approval_timestamp: new Date().toISOString()
      })
    });
    const payload = await response.json();
    if (!validateExecutionAuthorization(payload)) {
      throw new Error("Execution authorization failed governed validation.");
    }
    currentAuthorityToken = payload;
    latestConsumerResponse = null;
    latestAdapterResponse = null;
    renderResult({
      status: payload.status,
      token_id: payload.token_id,
      replay_identity: payload.replay_identity,
      authorization_expiration: payload.authorization_expiration,
      execution_window_seconds: payload.execution_window_seconds,
      blocked_capabilities: payload.blocked_capabilities,
      revocation_supported: payload.revocation_supported,
      execution_disclaimer: "Execution authorization does not execute Codex."
    });
  } catch (error) {
    renderResult({ status: "BLOCKED", error: error.message });
  }
}

function validateMockExecution(response) {
  return response
    && response.status === "MOCK_EXECUTION_ACCEPTED"
    && response.execution_performed === false
    && response.receipt
    && response.receipt.execution_performed === false
    && typeof response.receipt.receipt_id === "string";
}

async function runMockGovernedExecution() {
  if (document.getElementById("mode").value !== "codex" || !confirmedHandoffPackage || !currentAuthorityToken) {
    renderResult({ status: "BLOCKED", error: "Authorization is required before mock execution consumption." });
    return;
  }
  try {
    const response = await fetch(LOCAL_EXECUTION_CONSUME_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        handoff_package: confirmedHandoffPackage,
        authority_token: currentAuthorityToken,
        now: new Date().toISOString(),
        revoked_token_ids: []
      })
    });
    const payload = await response.json();
    if (!validateMockExecution(payload)) {
      throw new Error("Mock execution consumer failed governed validation.");
    }
    latestConsumerResponse = payload;
    renderResult({
      status: payload.status,
      replay_identity: payload.replay_identity,
      receipt_id: payload.receipt.receipt_id,
      authority_token_id: payload.receipt.authority_token_id,
      expiration_validation: payload.validation.valid,
      execution_performed: payload.execution_performed,
      constitutional_statement: payload.receipt.constitutional_statement
    });
  } catch (error) {
    renderResult({ status: "BLOCKED", error: error.message });
  }
}

function validateCodexExecution(response) {
  return response
    && ["EXECUTION_ACCEPTED", "EXECUTION_FAILURE", "EXECUTION_TIMEOUT"].includes(response.status)
    && response.receipt
    && typeof response.receipt.receipt_id === "string"
    && typeof response.receipt.stdout_hash === "string"
    && typeof response.receipt.stderr_hash === "string";
}

async function runGovernedCodexExecution() {
  if (document.getElementById("mode").value !== "codex" || !confirmedHandoffPackage || !currentAuthorityToken) {
    renderResult({ status: "BLOCKED", error: "Authorization is required before governed Codex execution." });
    return;
  }
  try {
    const response = await fetch(LOCAL_CODEX_EXECUTE_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        handoff_package: confirmedHandoffPackage,
        authority_token: currentAuthorityToken,
        now: new Date().toISOString(),
        revoked_token_ids: [],
        codex_executable: "codex",
        timeout_seconds: 30
      })
    });
    const payload = await response.json();
    if (!validateCodexExecution(payload)) {
      throw new Error("Codex execution adapter failed governed validation.");
    }
    latestAdapterResponse = payload;
    renderResult({
      status: payload.status,
      replay_identity: payload.replay_identity,
      receipt_id: payload.receipt.receipt_id,
      authority_token_id: payload.receipt.authority_token_id,
      expiration_validation: payload.validation.consumer_validation.valid,
      bounded_execution_status: payload.dispatch.execution_status,
      stdout_hash: payload.receipt.stdout_hash,
      stderr_hash: payload.receipt.stderr_hash
    });
  } catch (error) {
    renderResult({ status: "BLOCKED", error: error.message });
  }
}

function validateExecutionObservability(response) {
  return response
    && response.status === "OBSERVED"
    && response.read_only === true
    && response.execution_triggered === false
    && response.trace
    && typeof response.trace.execution_trace_id === "string"
    && typeof response.trace.stdout_hash === "string"
    && typeof response.trace.stderr_hash === "string"
    && Array.isArray(response.timeline);
}

async function inspectGovernedExecution() {
  if (
    document.getElementById("mode").value !== "codex"
    || !confirmedHandoffPackage
    || !currentAuthorityToken
    || !latestConsumerResponse
    || !latestAdapterResponse
  ) {
    renderResult({ status: "BLOCKED", error: "Completed governed execution receipts are required before inspection." });
    return;
  }
  try {
    const response = await fetch(LOCAL_EXECUTION_OBSERVE_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        handoff_package: confirmedHandoffPackage,
        authority_token: currentAuthorityToken,
        consumer_response: latestConsumerResponse,
        adapter_response: latestAdapterResponse,
        now: new Date().toISOString(),
        revoked_token_ids: []
      })
    });
    const payload = await response.json();
    if (!validateExecutionObservability(payload)) {
      throw new Error("Execution observability failed governed validation.");
    }
    renderResult({
      status: payload.status,
      replay_identity: payload.trace.replay_identity,
      timeline: payload.timeline,
      authority_status: payload.trace.authorization_status,
      receipt_status: {
        consumer: payload.trace.consumer_receipt_status,
        adapter: payload.trace.adapter_receipt_status
      },
      stdout_hash: payload.trace.stdout_hash,
      stderr_hash: payload.trace.stderr_hash,
      blocked_capabilities: payload.trace.blocked_capabilities,
      execution_triggered: payload.execution_triggered
    });
  } catch (error) {
    renderResult({ status: "BLOCKED", error: error.message });
  }
}

async function invokeGovernedRuntime() {
  const mode = document.getElementById("mode").value;
  if (mode === "codex") {
    renderResult({
      status: "BLOCKED",
      error: "Governed Codex Task mode is preview-only and does not execute Codex."
    });
    return;
  }
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
document.getElementById("transfer-export").addEventListener("click", exportGovernedIntentTransferPackage);
document.getElementById("export").addEventListener("click", exportGovernedHandoffPackage);
document.getElementById("authorize").addEventListener("click", requestExecutionAuthorization);
document.getElementById("consume").addEventListener("click", runMockGovernedExecution);
document.getElementById("codex-execute").addEventListener("click", runGovernedCodexExecution);
document.getElementById("observe").addEventListener("click", inspectGovernedExecution);
document.getElementById("invoke").addEventListener("click", invokeGovernedRuntime);
