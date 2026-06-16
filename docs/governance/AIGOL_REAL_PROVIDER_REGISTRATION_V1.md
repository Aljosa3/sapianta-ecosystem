# AIGOL Real Provider Registration V1

Status: implemented registration milestone.

Purpose: register the first real cognition providers inside ERR as passive resource metadata.

This milestone proves:

```text
OCS
-> required capability
-> ERR
-> real provider metadata
```

No provider execution, provider transport, authentication, API key handling, session management, provider comparison, routing engine, ranking, marketplace behavior, ELL, or lifecycle engine is introduced.

## Architecture Summary

ERR remains passive shared infrastructure.

The real provider registration path is:

```text
registry = create_err_v0_registry()
-> register_real_cognition_providers(registry)
-> find_resources_by_capability(registry, "reasoning", resource_type=COGNITION_PROVIDER)
-> real provider metadata returned
```

OCS does not require architecture changes because the existing OCS ERR integration already accepts:

```text
use_err_resource_lookup
err_required_capability
err_registry
```

OCS can therefore consume a real-provider ERR registry through the same capability lookup path used by the mock provider integration.

## Provider Registry Entries

The following provider resources are registered:

| resource_id | resource_type | capabilities | status |
| --- | --- | --- | --- |
| `openai` | `COGNITION_PROVIDER` | `reasoning`, `planning`, `summarization`, `analysis`, `generation` | `ACTIVE` |
| `claude` | `COGNITION_PROVIDER` | `reasoning`, `planning`, `summarization`, `analysis`, `generation` | `ACTIVE` |
| `gemini` | `COGNITION_PROVIDER` | `reasoning`, `planning`, `summarization`, `analysis`, `generation` | `ACTIVE` |
| `mistral` | `COGNITION_PROVIDER` | `reasoning`, `planning`, `summarization`, `analysis`, `generation` | `ACTIVE` |

No additional metadata fields are added.

The existing ERR resource model remains:

```text
resource_id
resource_type
capabilities
status
```

## Demonstration

### OpenAI

Standard ERR selection:

```text
required_capability = reasoning
resource_type = COGNITION_PROVIDER
registry = real_provider_err_v1_registry()
-> selected_resource_id = openai
```

Replay evidence records:

```text
selection_status = RESOURCE_SELECTED
selected_resource_id = openai
selected_resource_type = COGNITION_PROVIDER
active_resource_ids = [openai, claude, gemini, mistral]
provider_invoked = false
worker_invoked = false
orchestration_performed = false
governance_modified = false
replay_visible = true
```

### Claude

Standard ERR selection with OpenAI inactive:

```text
required_capability = reasoning
resource_type = COGNITION_PROVIDER
registry = real_provider_err_v1_registry(openai inactive for filtering test)
-> selected_resource_id = claude
```

Replay evidence records:

```text
selection_status = RESOURCE_SELECTED
selected_resource_id = claude
selected_resource_type = COGNITION_PROVIDER
active_resource_ids = [claude, gemini, mistral]
provider_invoked = false
worker_invoked = false
orchestration_performed = false
governance_modified = false
replay_visible = true
```

This demonstrates both real provider metadata discovery and `ACTIVE` filtering.

## Governance Validation

This milestone preserves the ERR scope lock.

ERR still does not:

- invoke providers;
- invoke workers;
- dispatch;
- authorize;
- govern;
- rank providers;
- optimize provider selection;
- compare providers;
- manage provider lifecycle;
- authenticate;
- handle API keys;
- create sessions;
- become ELL;
- mutate replay history.

Provider registration is metadata registration only.

Selection evidence is not approval, authorization, dispatch, invocation, or execution.

## Tests Executed

Focused validation:

```text
python -m pytest \
  tests/test_real_provider_registration_v1.py \
  tests/test_external_resource_registry_runtime_v0.py \
  tests/test_ocs_llm_cognition_end_to_end_runtime_v1.py

36 passed
```

Coverage:

- real provider registration succeeds;
- provider lookup by id succeeds;
- capability search returns real providers;
- inactive provider filtering excludes inactive providers;
- OpenAI selection creates replay-visible evidence;
- Claude selection creates replay-visible evidence after OpenAI is inactive;
- OCS ERR path accepts an ERR registry without architecture changes;
- ERR passive boundary remains protected;
- existing ERR_V0 and OCS ERR tests remain passing.

## Files Added

- `tests/test_real_provider_registration_v1.py`
- `docs/governance/AIGOL_REAL_PROVIDER_REGISTRATION_V1.md`

## Files Modified

- `aigol/runtime/external_resource_registry_runtime.py`

## Remaining Gaps

Remaining gaps are intentional non-goals:

1. OpenAI is not invoked.
2. Claude is not invoked.
3. Gemini is not invoked.
4. Mistral is not invoked.
5. No provider API keys or authentication are modeled.
6. No provider transport layer is implemented.
7. No provider comparison, ranking, routing, or optimization is implemented.
8. No lifecycle or ELL runtime is implemented.

Future provider-runtime milestones must pass governance review and must preserve the ERR passive boundary.

## Final Recommendation

ERR remains a passive shared infrastructure layer when populated with real provider metadata.

Supporting evidence:

- the resource schema did not expand beyond existing ERR fields;
- real providers are registered as metadata only;
- capability lookup returns metadata, not execution handles;
- replay selection evidence explicitly records `provider_invoked = false`;
- OCS can use the existing ERR registry input without architecture changes;
- passive-boundary tests reject provider invocation, dispatch, authorization, ranking, optimization, lifecycle, transport, and HTTP client surfaces.

Recommendation:

```text
KEEP_ERR_PASSIVE_SHARED_INFRASTRUCTURE = YES
REAL_PROVIDER_REGISTRATION_APPROVED_AS_METADATA_ONLY = YES
PROVIDER_RUNTIME_IMPLEMENTATION_REQUIRED_FOR_API_CALLS = FUTURE_GOVERNED_MILESTONE
```
