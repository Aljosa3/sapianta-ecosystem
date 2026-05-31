# AUTHORIZED_WORKER_REQUEST_REPLAY_MODEL_V1

## Status

Certified replay model.

## Replay Purpose

Replay records the transformation from authorization artifact to authorized
worker request.

Replay does not execute the request.

Replay does not dispatch the request.

Replay does not invoke the worker.

## Required Reconstruction

Replay must reconstruct:

- proposal
- authorization
- authorized request
- worker target
- scope
- request lineage

## Required Replay Fields

- proposal_reference
- authorization_id
- authorization_hash
- request_id
- worker_id
- authorized_scope
- capability_binding
- request_timestamp
- request_hash
- replay_reference

## Replay Failure Requirements

Replay must preserve failure evidence for:

- missing authorization
- scope mismatch
- worker mismatch
- invalid request lineage
- invalid request metadata
- authorization not found

## Replay Non-Authority Rule

Replay evidence proves what happened.

Replay evidence does not authorize execution.
