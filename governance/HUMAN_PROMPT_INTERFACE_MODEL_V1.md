# HUMAN_PROMPT_INTERFACE_MODEL_V1

## Model

The Human Prompt Interface is the operator-facing entry boundary for AiGOL.

It accepts human intent and converts it into replay-visible input evidence.

## Human Prompt Artifact

A future implementation should create a `HUMAN_PROMPT_ARTIFACT` containing:

- prompt id;
- prompt text;
- prompt text hash;
- created timestamp;
- operator context;
- requested mode or hint;
- target reference if provided;
- replay reference;
- authority status;
- artifact hash.

## Authority Status

Human Prompt has no execution authority.

It cannot:

- authorize;
- govern;
- execute;
- dispatch;
- mutate replay;
- mutate Constitutional Memory;
- directly command a worker.

## Input Boundary

The interface may accept:

- natural-language request;
- bounded command-like request;
- optional explicit target;
- optional workspace;
- optional request for explanation or replay report.

The interface must reject or fail closed on:

- hidden execution request;
- direct worker command;
- authority-bearing input;
- replay mutation request;
- ambiguous execution scope.

## Output Boundary

The interface may produce:

- prompt artifact;
- intent classification artifact;
- routing artifact;
- replay reference;
- explanation response;
- governed operation result if downstream authorization succeeds.

It must not produce:

- direct worker command;
- authorization decision;
- governance decision;
- provider command outside provider boundary.

## Current Implementation Readiness

Existing components already provide most downstream pieces:

- intent classification;
- routing model;
- provider proposal runtime;
- authorization runtime;
- worker execution path;
- replay verification;
- replay reporting;
- replay-backed explanation.

The missing component is the first prompt artifact and CLI boundary.
