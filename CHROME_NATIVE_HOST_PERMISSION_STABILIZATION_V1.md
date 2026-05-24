# CHROME_NATIVE_HOST_PERMISSION_STABILIZATION_V1

## Purpose

This milestone stabilizes diagnostics for the real Chrome Native Messaging host launch boundary:

sidepanel -> service worker -> Chrome Native Messaging host launch -> Python runtime bridge -> bounded provider path.

It does not add architecture, orchestration, retries, fallback execution, autonomous continuation, provider redesign, governance bypasses, or alternate execution topology.

## Current Failure

Chrome reports:

`Access to the specified native messaging host is forbidden.`

This means `chrome.runtime.sendNativeMessage(...)` is reached, but Chrome blocks launch before the Python host reaches provider invocation.

## Stabilized Diagnostics

The registration validator now reports deterministic launch-continuity evidence:

- `native_host_manifest_exists`
- `native_host_manifest_readable`
- `native_host_manifest_json_valid`
- `native_host_manifest_permissions`
- `native_host_executable_exists`
- `native_host_executable_readable`
- `native_host_executable_executable`
- `native_host_shebang_valid`
- `native_host_python_runtime_found`
- `native_host_allowed_origins`
- `native_host_allowed_origin_match`
- `native_host_extension_id`
- `native_host_profile_path`
- `chrome_profile_detected`
- `chrome_runtime_launch_allowed`
- `chrome_runtime_launch_attempted`
- `chrome_runtime_launch_blocked`
- `chrome_runtime_launch_failure_reason`

## Permission Continuity Model

Chrome launch is considered allowed only when all local registration evidence is valid:

- the manifest exists and is readable;
- manifest JSON parses as an object;
- `name` matches `com.sapianta.aigol_bridge`;
- `type` is `stdio`;
- `allowed_origins` contains the exact extension origin;
- the executable exists, is readable, and is executable;
- the executable shebang points to Python;
- the referenced Python runtime is available.

Anything else remains fail-closed.

## Extension ID Continuity

The native host manifest must contain:

`chrome-extension://<EXTENSION_ID>/`

where `<EXTENSION_ID>` is the installed Browser Companion extension ID from `chrome://extensions`. A different ID makes Chrome block launch even when the manifest is present.

## Chrome Profile Continuity

For Google Chrome on Linux, the deterministic registration location is:

`~/.config/google-chrome/NativeMessagingHosts/com.sapianta.aigol_bridge.json`

For Chromium, the equivalent profile root is:

`~/.config/chromium/NativeMessagingHosts/com.sapianta.aigol_bridge.json`

The helper reports the profile path and whether it is detected. It does not install files or mutate profile directories.

## Cockpit Visibility

The controlled execution handoff display now surfaces the Chrome launch boundary fields directly, including manifest, executable, shebang, allowed-origin, profile, and launch-blocked diagnostics.

## Boundary Confirmation

This milestone does not:

- invoke Codex directly;
- bypass Native Messaging;
- add retries;
- add orchestration;
- add fallback providers;
- create background workers;
- expand execution authority.

It only makes the remaining Chrome launch permission boundary deterministic and visible.
