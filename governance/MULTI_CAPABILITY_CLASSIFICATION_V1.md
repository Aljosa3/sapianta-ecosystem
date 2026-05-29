# Multi-Capability Classification V1

Status: first capability taxonomy milestone.

This artifact establishes constitutional capability classification above the execution runtime prototype. It is taxonomy-only and does not introduce new execution powers, filesystem write, network execution, shell execution, orchestration runtime, or agent runtime.

## Purpose

Capabilities must be classified before additional capabilities are attached.

The purpose is to prevent capability sprawl and preserve constitutional simplicity.

## Capability Classes

The canonical capability classes are:

- `READ_ONLY`
- `INSPECTION`
- `QUERY`
- `MUTATION`
- `DESTRUCTIVE`
- `PRIVILEGED`

## Risk Levels

The canonical risk levels are:

- `LOW`
- `MEDIUM`
- `HIGH`
- `CRITICAL`

## Classification Summary

| Capability Class | Risk Level | Default Boundary |
| --- | --- | --- |
| `READ_ONLY` | `LOW` | `RESTRICTED` until explicitly attached |
| `INSPECTION` | `LOW` | `RESTRICTED` until explicitly attached |
| `QUERY` | `MEDIUM` | `RESTRICTED` |
| `MUTATION` | `HIGH` | `DENIED` |
| `DESTRUCTIVE` | `CRITICAL` | `DENIED` |
| `PRIVILEGED` | `CRITICAL` | `DENIED` |

## Classification Guarantees

Capability classification must preserve:

- replay centrality
- boundedness
- authority separation
- constitutional freeze

Capability classification must not introduce:

- execution power
- orchestration
- hidden authority
- capability escalation

## Architectural Status

This milestone defines taxonomy only.

It does not activate:

- new capabilities
- filesystem write
- network execution
- shell execution
- orchestration runtime
- agent runtime

