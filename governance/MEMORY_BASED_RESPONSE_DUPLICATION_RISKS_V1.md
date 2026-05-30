# Memory Based Response Duplication Risks V1

Status: duplication risk analysis.

## Consultation Duplication

Risk: response generation could duplicate Constitutional Memory Consultation if it performs retrieval again.

Constraint: response must consume an existing consultation record and citation bundle.

## Retrieval Duplication

Risk: response generation could become a second retrieval model.

Constraint: response must not search, select, or replace artifacts.

## Governance Duplication

Risk: response language could drift into governance recommendation.

Constraint: response must remain explanation over evidence, not decision.

## Replay Duplication

Risk: response replay could replace consultation replay.

Constraint: response replay must link to consultation replay and preserve its separate role.

## Intent Routing Duplication

Risk: response generation could choose destinations after producing text.

Constraint: routing remains upstream and separate.
