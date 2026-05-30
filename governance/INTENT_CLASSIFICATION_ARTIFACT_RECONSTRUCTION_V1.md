# Intent Classification Artifact Reconstruction V1

Status: reconstruction requirements for Intent Classification Artifact.

## Reconstruction Requirement

Replay observers must be able to reconstruct:

- why classification occurred
- which destination was selected
- which artifact version was used
- which input was classified
- whether ambiguity existed
- whether failure occurred
- which replay parent and lineage references bind the artifact

Classification: `REQUIRED`

## Reconstruction Inputs

Required reconstruction inputs:

- Human Prompt evidence
- Intent Classification Artifact
- artifact hash
- replay parent
- lineage references
- classification version

Optional reconstruction inputs:

- normalized request evidence
- cited Constitutional Memory references

## Reconstruction Failure

Reconstruction must fail closed on:

- missing artifact id
- missing human request reference
- missing destination
- invalid destination
- missing replay reference
- corrupted artifact hash
- missing classification version
- ambiguous classification reason

## Reconstruction Boundary

Reconstruction explains classification.

It does not authorize, govern, route, execute, or invoke providers/workers.

