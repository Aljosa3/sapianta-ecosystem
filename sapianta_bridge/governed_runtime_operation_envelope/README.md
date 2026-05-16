# Governed Runtime Operation Envelope V1

This package defines the first deterministic governed runtime operation envelope.

Activation authorization answers whether a runtime may become operationally active. The operation envelope answers what exact bounded operation may enter that runtime afterward. It defines structured operation payloads, bounded grammar, policy checks, and fail-closed validation before any command execution exists.

It does not implement shell access, subprocess execution, orchestration, or autonomous behavior.
