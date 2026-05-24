# NATIVE_HOST_REGISTRATION_FIX_V1

## Purpose

This milestone stabilizes the Chrome Native Messaging registration boundary for the existing AiGOL governed execution path:

Human operator -> Browser Companion sidepanel -> service worker -> registered Native Messaging host -> Python runtime bridge -> bounded provider path.

It does not add architecture, orchestration, retries, alternate providers, autonomous continuation, or governance bypasses.

## Root Cause

The service worker reached `chrome.runtime.sendNativeMessage(...)`, but Chrome returned:

`Specified native messaging host not found.`

This means the browser extension attempted the Native Messaging launch and failed before the Python host process was located. The failing layer is Chrome Native Messaging host registration, not provider execution.

## Manifest Structure

The required host manifest remains:

```json
{
  "name": "com.sapianta.aigol_bridge",
  "description": "SAPIANTA AiGOL local native messaging bridge",
  "path": "/absolute/path/to/sapianta/agol_bridge/native/native_messaging_host.py",
  "type": "stdio",
  "allowed_origins": [
    "chrome-extension://<EXTENSION_ID>/"
  ]
}
```

`allowed_origins` must contain the exact installed Chrome extension ID. The helper rejects malformed extension IDs and generates the expected origin deterministically.

## Linux Registration Path Model

The deterministic Linux registration directory for Google Chrome is:

`~/.config/google-chrome/NativeMessagingHosts`

The deterministic manifest path is:

`~/.config/google-chrome/NativeMessagingHosts/com.sapianta.aigol_bridge.json`

Chromium can be inspected separately with the `chromium` variant:

`~/.config/chromium/NativeMessagingHosts/com.sapianta.aigol_bridge.json`

The helper reports paths and generated manifest previews. It does not silently install the manifest or mutate user system directories.

## Extension ID Continuity

Chrome resolves the host only when the manifest contains:

`chrome-extension://<EXTENSION_ID>/`

where `<EXTENSION_ID>` is the actual Browser Companion extension ID shown by Chrome. The repository does not hardcode an extension key, so operator registration must bind the currently installed extension ID into the local manifest.

## Executable Continuity

The manifest `path` must point to:

`agol_bridge/native/native_messaging_host.py`

The executable must exist and be executable by the local operator. The validator exposes:

- `native_host_executable_found`
- `native_host_executable_executable`
- `native_host_launch_ready`

## Diagnostics Model

Registration validation produces deterministic diagnostics:

- `native_host_manifest_found`
- `native_host_manifest_path`
- `native_host_executable_found`
- `native_host_executable_executable`
- `native_host_allowed_origin_match`
- `native_host_registration_valid`
- `native_host_launch_ready`

The service worker also preserves host-not-found registration diagnostics when Chrome returns the Native Messaging registration failure.

## Operational Registration Steps

1. Obtain the Browser Companion extension ID from `chrome://extensions`.
2. Generate or inspect the manifest with `agol_bridge.native.native_host_registration`.
3. Place the manifest at the Chrome Native Messaging host registration path.
4. Ensure `agol_bridge/native/native_messaging_host.py` is executable.
5. Re-run the Browser Companion controlled handoff flow.

## Boundary Confirmation

This fix does not:

- dispatch a provider directly;
- add orchestration;
- add retries;
- add autonomous continuation;
- bypass governance;
- create an alternate execution path;
- silently mutate Chrome registration directories.

Registration readiness only makes Chrome able to launch the existing governed Native Messaging host.
