# Worker Identity Model V1

Status: model-only worker identity definition.

## Purpose

Worker identity makes execution participation attributable, replay-visible, bounded, and deterministic.

Worker identity does not grant authority.

## Required Identity Fields

A real worker attachment should record:

- `worker_id`: deterministic identifier for the worker boundary
- `worker_type`: bounded class such as `read_only_worker`
- `worker_instance_identity`: specific worker instance reference
- `worker_version`: version of the worker attachment boundary
- `capability_binding_id`: governed binding to an allowed capability
- `invocation_id`: replay-visible worker invocation reference
- `authorized_request_id`: reference to AiGOL authorization evidence
- `created_at`: deterministic timestamp supplied by AiGOL

## Identity Rules

Worker identity must be:

- explicit
- replay-visible
- immutable after capture
- scoped to one governed execution request
- linked to authorization evidence
- linked to worker result evidence

## Non-Authority Rule

Worker identity does not authorize execution.

Worker identity does not imply governance authority, authorization authority, replay authority, capability expansion authority, or persistence authority.

## Fail-Closed Identity Conditions

The attachment must fail closed when:

- worker identity is missing
- worker identity is ambiguous
- worker instance identity changes during invocation
- authorized request id is missing
- capability binding id is missing
- worker identity is not linked to replay evidence
- worker identity attempts to continue across invocations without explicit governance

## Identity Continuity

Worker identity continuity is invocation-scoped.

It must not become hidden session memory, persistent worker autonomy, cross-session authority, or implicit continuation.
