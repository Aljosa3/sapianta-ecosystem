"""Native local bridge helpers for Browser Companion integration."""

from agol_bridge.native.native_messaging_host import (
    NATIVE_BRIDGE_ACCEPTED,
    NATIVE_BRIDGE_REJECTED,
    handle_native_message,
)
from agol_bridge.native.native_host_registration import (
    NATIVE_HOST_NAME,
    generate_native_host_manifest,
    native_host_executable_path,
    native_host_manifest_path,
    validate_native_host_registration,
)

__all__ = [
    "NATIVE_BRIDGE_ACCEPTED",
    "NATIVE_BRIDGE_REJECTED",
    "NATIVE_HOST_NAME",
    "generate_native_host_manifest",
    "handle_native_message",
    "native_host_executable_path",
    "native_host_manifest_path",
    "validate_native_host_registration",
]
