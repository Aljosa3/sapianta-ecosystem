"""Native local bridge helpers for Browser Companion integration."""

from agol_bridge.native.native_messaging_host import (
    NATIVE_BRIDGE_ACCEPTED,
    NATIVE_BRIDGE_REJECTED,
    handle_native_message,
)

__all__ = [
    "NATIVE_BRIDGE_ACCEPTED",
    "NATIVE_BRIDGE_REJECTED",
    "handle_native_message",
]
