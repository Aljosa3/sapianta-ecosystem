const NATIVE_BRIDGE_HOST = "com.sapianta.aigol_bridge";
const SERVICE_WORKER_NATIVE_BRIDGE_ACTION = "RUN_NATIVE_BRIDGE";
const NATIVE_BRIDGE_TIMEOUT_MS = 660000;

function nativeHostRegistrationDiagnostics(code, message) {
  const hostNotFound = code === "NATIVE_HOST_NOT_FOUND";
  const hostForbidden = code === "NATIVE_HOST_FORBIDDEN";
  const launchBlocked = hostNotFound || hostForbidden;
  return {
    native_host_name: NATIVE_BRIDGE_HOST,
    native_host_manifest_exists: hostNotFound ? false : null,
    native_host_manifest_found: hostNotFound ? false : null,
    native_host_manifest_readable: hostForbidden ? null : false,
    native_host_manifest_json_valid: hostForbidden ? null : false,
    native_host_manifest_permissions: "",
    native_host_manifest_path: "",
    native_host_executable_exists: hostNotFound ? false : null,
    native_host_executable_found: hostNotFound ? false : null,
    native_host_executable_readable: hostForbidden ? null : false,
    native_host_executable_executable: hostForbidden ? null : false,
    native_host_shebang_valid: hostForbidden ? null : false,
    native_host_python_runtime_found: hostForbidden ? null : false,
    native_host_allowed_origins: [],
    native_host_allowed_origin_match: launchBlocked ? false : null,
    native_host_extension_id: "",
    native_host_profile_path: "",
    chrome_profile_detected: null,
    native_host_registration_valid: false,
    native_host_launch_ready: false,
    chrome_runtime_launch_allowed: false,
    chrome_runtime_launch_attempted: true,
    chrome_runtime_launch_blocked: launchBlocked,
    chrome_runtime_launch_failure_reason: message || code,
    native_host_registration_failure: code,
    native_host_registration_message: message || code
  };
}

function nativeBridgeRuntimeError(code, message) {
  const registrationDiagnostics = nativeHostRegistrationDiagnostics(code, message);
  return {
    status: "SERVICE_WORKER_NATIVE_BRIDGE_FAILED",
    error: {
      code,
      message: message || code
    },
    diagnostic_evidence: {
      failing_layer: "service_worker_native_bridge_response_handling",
      failing_function: "invokeNativeBridge",
      failing_condition: message || code,
      native_messaging_boundary_crossed: code !== "MISSING_PERMISSIONS",
      python_runtime_bridge_called: false,
      provider_invoked: false,
      subprocess_invoked: false,
      response_serialization_ready: false,
      native_host_registration: registrationDiagnostics,
      native_bridge: {
        failing_layer: "service_worker_native_bridge_response_handling",
        failing_function: "invokeNativeBridge",
        failing_condition: message || code,
        response_serialization_ready: false,
        native_host_registration: registrationDiagnostics
      },
      provider: {}
    },
    labels: [
      "NATIVE_BRIDGE_LOCAL_ONLY",
      "OPERATOR_TRIGGERED",
      "SERVICE_WORKER_RUNTIME_CONTROLLER",
      "CANONICAL_PYTHON_RUNTIME",
      "BOUNDED_CODEX_CLI_PROVIDER",
      "NO_AUTONOMOUS_CONTINUATION"
    ],
    authority_guarantees: {
      dispatch: false,
      approval: false,
      orchestration: false,
      autonomous_continuation: false,
      localhost_server: false,
      daemon: false,
      durable_replay_backend: false
    }
  };
}

function classifyNativeRuntimeError(message) {
  const text = String(message || "").toLowerCase();
  if (text.includes("host not found") || text.includes("specified native messaging host not found")) {
    return "NATIVE_HOST_NOT_FOUND";
  }
  if (text.includes("forbidden") || text.includes("access to the specified native messaging host is forbidden")) {
    return "NATIVE_HOST_FORBIDDEN";
  }
  if (text.includes("permission")) {
    return "MISSING_PERMISSIONS";
  }
  if (text.includes("exited") || text.includes("crash") || text.includes("disconnected")) {
    return "HOST_CRASHED";
  }
  return "HOST_CRASHED";
}

function validateNativeBridgeRequest(message) {
  if (!message || typeof message !== "object" || Array.isArray(message)) {
    return "native bridge service worker request must be an object";
  }
  if (message.action !== SERVICE_WORKER_NATIVE_BRIDGE_ACTION) {
    return "unsupported service worker action";
  }
  if (message.operator_triggered !== true) {
    return "operator_triggered must be true";
  }
  if (!message.native_message || typeof message.native_message !== "object" || Array.isArray(message.native_message)) {
    return "native_message is required";
  }
  if (message.native_message.operator_triggered !== true) {
    return "native_message.operator_triggered must be true";
  }
  return "";
}

function validateNativeBridgeResponse(response) {
  if (!response || typeof response !== "object" || Array.isArray(response)) {
    return "INVALID_RESPONSE: native bridge response must be an object";
  }
  if (!["NATIVE_BRIDGE_ACCEPTED", "NATIVE_BRIDGE_REJECTED", "NATIVE_BRIDGE_ERROR"].includes(response.status)) {
    return "native bridge response has unsupported status";
  }
  if (response.status === "NATIVE_BRIDGE_ACCEPTED" && (!response.result_artifact || typeof response.result_artifact !== "object")) {
    return "accepted native bridge response is missing result_artifact";
  }
  return "";
}

function invokeNativeBridge(nativeMessage, sendResponse) {
  if (!chrome.runtime || typeof chrome.runtime.sendNativeMessage !== "function") {
    sendResponse(nativeBridgeRuntimeError("MISSING_PERMISSIONS", "Native Messaging permission or API is unavailable."));
    return;
  }

  let settled = false;
  const timeoutId = setTimeout(() => {
    if (settled) {
      return;
    }
    settled = true;
    sendResponse(nativeBridgeRuntimeError("TIMEOUT", "Native bridge invocation timed out."));
  }, NATIVE_BRIDGE_TIMEOUT_MS);

  chrome.runtime.sendNativeMessage(NATIVE_BRIDGE_HOST, nativeMessage, (response) => {
    if (settled) {
      return;
    }
    settled = true;
    clearTimeout(timeoutId);

    const runtimeError = chrome.runtime.lastError;
    if (runtimeError) {
      sendResponse(nativeBridgeRuntimeError(classifyNativeRuntimeError(runtimeError.message), runtimeError.message));
      return;
    }

    const responseError = validateNativeBridgeResponse(response);
    if (responseError) {
      sendResponse(nativeBridgeRuntimeError("MALFORMED_RESULT", responseError));
      return;
    }

    const nativeDiagnostics = response.diagnostic_evidence || {};
    sendResponse({
      status: "SERVICE_WORKER_NATIVE_BRIDGE_RETURNED",
      native_response: response,
      diagnostic_evidence: {
        failing_layer: "",
        failing_function: "",
        failing_condition: "",
        native_messaging_boundary_crossed: true,
        python_runtime_bridge_called: Boolean(nativeDiagnostics.python_runtime_bridge_called),
        provider_invoked: Boolean(nativeDiagnostics.provider_invoked),
        subprocess_invoked: Boolean(nativeDiagnostics.subprocess_invoked),
        response_serialization_ready: true,
        native_bridge: nativeDiagnostics.native_bridge || nativeDiagnostics,
        provider: nativeDiagnostics.provider || {}
      },
      labels: [
        "NATIVE_BRIDGE_LOCAL_ONLY",
        "OPERATOR_TRIGGERED",
        "SERVICE_WORKER_RUNTIME_CONTROLLER",
        "CANONICAL_PYTHON_RUNTIME",
        "BOUNDED_CODEX_CLI_PROVIDER",
        "NO_AUTONOMOUS_CONTINUATION"
      ],
      authority_guarantees: {
        dispatch: false,
        approval: false,
        orchestration: false,
        autonomous_continuation: false,
        localhost_server: false,
        daemon: false,
        durable_replay_backend: false
      }
    });
  });
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  const validationError = validateNativeBridgeRequest(message);
  if (validationError) {
    sendResponse(nativeBridgeRuntimeError("INVALID_REQUEST", validationError));
    return false;
  }
  invokeNativeBridge(message.native_message, sendResponse);
  return true;
});
