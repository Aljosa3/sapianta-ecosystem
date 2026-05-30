# Intent Classifier Fail-Closed Readiness V1

Status: fail-closed readiness review.

## Unknown Intent

Classification: `READY`

Required behavior: `FAILED_CLOSED`

## Ambiguous Intent

Classification: `READY`

Required behavior: `FAILED_CLOSED`

## Multiple Intents

Classification: `READY`

Required behavior: `FAILED_CLOSED`

## Invalid Destination

Classification: `READY`

Required behavior: `FAILED_CLOSED`

## Artifact Generation Failure

Classification: `READY_WITH_GAPS`

Required behavior: failed replay-visible artifact when possible, otherwise explicit runtime failure with no downstream action.

Gap: runtime failure artifact shape must be implemented.

## Overall Fail-Closed Readiness

`INTENT_CLASSIFIER_FAIL_CLOSED_READINESS`: `READY_WITH_GAPS`

