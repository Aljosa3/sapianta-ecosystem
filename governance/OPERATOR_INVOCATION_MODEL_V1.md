# Operator Invocation Model V1

Status: minimal invocation model.

## Invocation Inputs

The minimal operator entrypoint accepts:

- operator flow identifier
- human request
- target read-only capability
- creation timestamp
- replay directory
- optional filesystem read-only path scope
- explicit authorization flag

## Invocation Output

The entrypoint returns:

- concise operator result summary
- governed runtime flow evidence
- replay reconstruction summary
- invariant markers

## Result Summary Fields

The result summary includes:

- status: `ACCEPTED` or `REJECTED`
- capability
- human request
- replay directory
- replay verification status
- replay artifact count
- bridge final status
- result summary
- failure reason when rejected
- authority boundary reminder

## Boundary Rules

The entrypoint must not:

- infer broad capability authority
- invoke unsupported capabilities
- bypass governance
- bypass replay
- bypass authorization
- create orchestration
- create memory
- create routing

The entrypoint must preserve:

- proposal-only cognition
- AiGOL governance authority
- worker-only execution after authorization
- mandatory replay
