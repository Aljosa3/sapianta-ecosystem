# Worker Replay Mapping V1

Status: model-only worker replay definition.

## Purpose

Worker replay mapping makes worker activity replay-visible without making the worker authoritative.

Replay remains the source of truth.

## Required Replay Stages

A real worker attachment should record append-only stages:

1. governed execution request
2. AiGOL authorization evidence
3. worker identity envelope
4. capability binding evidence
5. worker execution request
6. worker result evidence
7. worker termination evidence
8. governed return linkage

## Replay Requirements

Worker replay evidence must be:

- deterministic
- append-only
- lineage-linked
- hash-verifiable where applicable
- scoped to one authorized execution request
- preserved on failure

## Worker Result Evidence

Worker result evidence should record:

- worker id
- invocation id
- authorized request id
- capability binding id
- execution status
- output summary
- failure reason when failed
- termination state
- replay reference

## Replay Prohibitions

The worker must not:

- mutate existing replay artifacts
- reorder replay stages
- hide execution evidence
- emit unverifiable result lineage
- replace governed result evidence
- use logs as replay substitutes

## Replay Corruption Handling

Replay corruption, missing replay stages, hash mismatch, lineage mismatch, or ambiguous ordering must fail closed and produce deterministic failure evidence.
