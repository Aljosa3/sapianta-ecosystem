# ADR: GOVERNED_REAL_TIME_INTERACTION_LOOP_V1

## Status

Accepted.

## Decision

Add explicit governed conversational continuity through multi-turn lineage artifacts.

This is conversational continuity, not autonomous memory: every continuation validates prior turn and prior response IDs, replay determinism remains explicit, and provider hidden state is not trusted. The loop remains bounded governance rather than autonomous continuation authority.
