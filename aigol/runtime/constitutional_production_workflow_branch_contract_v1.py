"""Canonical Constitutional Production Workflow Branch contract for B6.

This module defines and validates the complete constitutional branch graph,
owner-produced predicate facts, and branch-local provenance bindings.  It does
not route a request, invoke Canonical Human Entry, select an owner, execute a
workflow, mutate state, persist Replay, observe through CRO, or certify a
production cutover.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from hashlib import sha256
import json
from types import MappingProxyType
from typing import Any, Mapping

from aigol.runtime.models import FailClosedRuntimeError


CANONICAL_PRODUCTION_WORKFLOW_BRANCH_CONTRACT_VERSION = (
    "G69_15_CONSTITUTIONAL_PRODUCTION_WORKFLOW_BRANCH_MODEL_V1"
)
CANONICAL_PRODUCTION_WORKFLOW_BRANCH_MODEL_IDENTITY_PREFIX = (
    "CONSTITUTIONAL-PRODUCTION-WORKFLOW-BRANCH-MODEL-"
)
CANONICAL_WORKFLOW_BRANCH_PROVENANCE_IDENTITY_PREFIX = (
    "CONSTITUTIONAL-WORKFLOW-BRANCH-PROVENANCE-"
)

READ_ONLY = "READ_ONLY"
GOVERNED_ACTION = "GOVERNED_ACTION"
CERTIFIED_REUSE = "CERTIFIED_REUSE"
GOVERNED_DEVELOPMENT = "GOVERNED_DEVELOPMENT"
NON_MUTATING_CAPABILITY = "NON_MUTATING_CAPABILITY"
CONTENT_OR_REPOSITORY_MUTATION = "CONTENT_OR_REPOSITORY_MUTATION"
HUMAN_RETURN = "HUMAN_RETURN"
CONSTITUTIONAL_COMPLETION = "CONSTITUTIONAL_COMPLETION"

CANONICAL_WORKFLOW_BRANCH_ORDER = (
    READ_ONLY,
    GOVERNED_ACTION,
    CERTIFIED_REUSE,
    GOVERNED_DEVELOPMENT,
    NON_MUTATING_CAPABILITY,
    CONTENT_OR_REPOSITORY_MUTATION,
    HUMAN_RETURN,
    CONSTITUTIONAL_COMPLETION,
)

TRANSPORT_ONLY = "TRANSPORT_ONLY"
NO_SEMANTIC_CAPABILITY = "NO_SEMANTIC_CAPABILITY"
NO_WORKFLOW_EXECUTION = "NO_WORKFLOW_EXECUTION"
NO_PRODUCTION_ROUTE_CREATION = "NO_PRODUCTION_ROUTE_CREATION"


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )


def _identity(prefix: str, value: Any) -> str:
    return prefix + sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _require_text(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise FailClosedRuntimeError(
            f"workflow branch {field_name} is absent or malformed"
        )
    return value


def _require_positive_integer(value: Any, field_name: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise FailClosedRuntimeError(
            f"workflow branch {field_name} is absent or malformed"
        )
    return value


def _require_sha256(value: Any, field_name: str) -> str:
    text = _require_text(value, field_name)
    if not text.startswith("sha256:") or len(text) != 71:
        raise FailClosedRuntimeError(
            f"workflow branch {field_name} is not a SHA-256 reference"
        )
    try:
        int(text[7:], 16)
    except ValueError as exc:
        raise FailClosedRuntimeError(
            f"workflow branch {field_name} is not a SHA-256 reference"
        ) from exc
    return text


@dataclass(frozen=True, slots=True)
class CanonicalWorkflowBranchPredicateV1:
    """One exact owner-produced fact required to identify a branch."""

    fact_name: str
    expected_value: str
    producing_owner: str
    evidence_role: str

    def __post_init__(self) -> None:
        for field_name in (
            "fact_name",
            "expected_value",
            "producing_owner",
            "evidence_role",
        ):
            object.__setattr__(
                self,
                field_name,
                _require_text(getattr(self, field_name), field_name),
            )

    def to_dict(self) -> dict[str, str]:
        return {
            "fact_name": self.fact_name,
            "expected_value": self.expected_value,
            "producing_owner": self.producing_owner,
            "evidence_role": self.evidence_role,
        }

    @classmethod
    def from_dict(
        cls, value: Mapping[str, Any]
    ) -> "CanonicalWorkflowBranchPredicateV1":
        if not isinstance(value, Mapping) or set(value) != {
            "fact_name",
            "expected_value",
            "producing_owner",
            "evidence_role",
        }:
            raise FailClosedRuntimeError("workflow branch predicate is malformed")
        return cls(**dict(value))


@dataclass(frozen=True, slots=True)
class CanonicalWorkflowEvidenceRequirementV1:
    """One exact provenance role and its constitutional producing owner."""

    evidence_role: str
    producing_owner: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "evidence_role",
            _require_text(self.evidence_role, "evidence_role"),
        )
        object.__setattr__(
            self,
            "producing_owner",
            _require_text(self.producing_owner, "producing_owner"),
        )

    def to_dict(self) -> dict[str, str]:
        return {
            "evidence_role": self.evidence_role,
            "producing_owner": self.producing_owner,
        }

    @classmethod
    def from_dict(
        cls, value: Mapping[str, Any]
    ) -> "CanonicalWorkflowEvidenceRequirementV1":
        if not isinstance(value, Mapping) or set(value) != {
            "evidence_role",
            "producing_owner",
        }:
            raise FailClosedRuntimeError(
                "workflow evidence requirement is malformed"
            )
        return cls(**dict(value))


@dataclass(frozen=True, slots=True)
class CanonicalWorkflowBranchDefinitionV1:
    """One closed branch definition inside the constitutional graph."""

    branch_kind: str
    decision_owner: str
    predicate: CanonicalWorkflowBranchPredicateV1
    allowed_predecessor_branches: tuple[str, ...]
    allowed_successor_branches: tuple[str, ...]
    required_evidence: tuple[CanonicalWorkflowEvidenceRequirementV1, ...]
    terminal_branch: bool

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "branch_kind",
            _require_text(self.branch_kind, "branch_kind"),
        )
        object.__setattr__(
            self,
            "decision_owner",
            _require_text(self.decision_owner, "decision_owner"),
        )
        if not isinstance(self.predicate, CanonicalWorkflowBranchPredicateV1):
            raise FailClosedRuntimeError("workflow branch predicate is malformed")
        for field_name in (
            "allowed_predecessor_branches",
            "allowed_successor_branches",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, tuple) or any(
                item not in CANONICAL_WORKFLOW_BRANCH_ORDER for item in value
            ) or len(value) != len(set(value)):
                raise FailClosedRuntimeError(
                    f"workflow branch {field_name} is malformed"
                )
        if not isinstance(self.required_evidence, tuple) or not self.required_evidence:
            raise FailClosedRuntimeError(
                "workflow branch required evidence is absent"
            )
        if any(
            not isinstance(item, CanonicalWorkflowEvidenceRequirementV1)
            for item in self.required_evidence
        ):
            raise FailClosedRuntimeError(
                "workflow branch required evidence is malformed"
            )
        roles = tuple(item.evidence_role for item in self.required_evidence)
        if len(roles) != len(set(roles)):
            raise FailClosedRuntimeError(
                "workflow branch evidence roles are duplicated"
            )
        if self.predicate.evidence_role not in roles:
            raise FailClosedRuntimeError(
                "workflow branch predicate evidence role is absent"
            )
        if not isinstance(self.terminal_branch, bool):
            raise FailClosedRuntimeError(
                "workflow branch terminal classification is malformed"
            )
        if self.terminal_branch and self.allowed_successor_branches:
            raise FailClosedRuntimeError(
                "terminal workflow branch cannot have a successor"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "branch_kind": self.branch_kind,
            "decision_owner": self.decision_owner,
            "predicate": self.predicate.to_dict(),
            "allowed_predecessor_branches": list(
                self.allowed_predecessor_branches
            ),
            "allowed_successor_branches": list(self.allowed_successor_branches),
            "required_evidence": [
                item.to_dict() for item in self.required_evidence
            ],
            "terminal_branch": self.terminal_branch,
        }

    @classmethod
    def from_dict(
        cls, value: Mapping[str, Any]
    ) -> "CanonicalWorkflowBranchDefinitionV1":
        if not isinstance(value, Mapping) or set(value) != {
            "branch_kind",
            "decision_owner",
            "predicate",
            "allowed_predecessor_branches",
            "allowed_successor_branches",
            "required_evidence",
            "terminal_branch",
        }:
            raise FailClosedRuntimeError("workflow branch definition is malformed")
        return cls(
            branch_kind=value["branch_kind"],
            decision_owner=value["decision_owner"],
            predicate=CanonicalWorkflowBranchPredicateV1.from_dict(
                value["predicate"]
            ),
            allowed_predecessor_branches=tuple(
                value["allowed_predecessor_branches"]
            ),
            allowed_successor_branches=tuple(value["allowed_successor_branches"]),
            required_evidence=tuple(
                CanonicalWorkflowEvidenceRequirementV1.from_dict(item)
                for item in value["required_evidence"]
            ),
            terminal_branch=value["terminal_branch"],
        )


def _predicate(
    fact_name: str,
    expected_value: str,
    producing_owner: str,
    evidence_role: str,
) -> CanonicalWorkflowBranchPredicateV1:
    return CanonicalWorkflowBranchPredicateV1(
        fact_name=fact_name,
        expected_value=expected_value,
        producing_owner=producing_owner,
        evidence_role=evidence_role,
    )


def _requirement(
    evidence_role: str,
    producing_owner: str,
) -> CanonicalWorkflowEvidenceRequirementV1:
    return CanonicalWorkflowEvidenceRequirementV1(
        evidence_role=evidence_role,
        producing_owner=producing_owner,
    )


CANONICAL_WORKFLOW_BRANCH_DEFINITIONS = (
    CanonicalWorkflowBranchDefinitionV1(
        branch_kind=READ_ONLY,
        decision_owner="G66_CONVERSATION_ROUTE_OWNER",
        predicate=_predicate(
            "route_class",
            READ_ONLY,
            "G66_CONVERSATION_ROUTE_OWNER",
            "PRODUCTION_FLOW_BINDING",
        ),
        allowed_predecessor_branches=(),
        allowed_successor_branches=(HUMAN_RETURN,),
        required_evidence=(
            _requirement(
                "PRODUCTION_FLOW_BINDING",
                "G66_CONVERSATION_ROUTE_OWNER",
            ),
            _requirement(
                "READ_ONLY_OWNER_RESULT",
                "SELF_OR_PLATFORM_KNOWLEDGE_OWNER",
            ),
        ),
        terminal_branch=False,
    ),
    CanonicalWorkflowBranchDefinitionV1(
        branch_kind=GOVERNED_ACTION,
        decision_owner="G66_CONVERSATION_ROUTE_OWNER",
        predicate=_predicate(
            "route_class",
            GOVERNED_ACTION,
            "G66_CONVERSATION_ROUTE_OWNER",
            "PRODUCTION_FLOW_BINDING",
        ),
        allowed_predecessor_branches=(),
        allowed_successor_branches=(CERTIFIED_REUSE, GOVERNED_DEVELOPMENT),
        required_evidence=(
            _requirement(
                "PRODUCTION_FLOW_BINDING",
                "G66_CONVERSATION_ROUTE_OWNER",
            ),
            _requirement(
                "SEMANTIC_STATE_PROPOSAL",
                "G59_CONVERSATION_OWNER",
            ),
            _requirement(
                "PROPOSAL_VALIDATION",
                "G59_INTERPRETER_VALIDATOR",
            ),
            _requirement(
                "PROPOSAL_COMMIT",
                "G59_CONVERSATION_OWNER",
            ),
            _requirement(
                "CANDIDATE_REVIEW",
                "HUMAN_AUTHORITY_PLUS_G59_CONVERSATION",
            ),
            _requirement(
                "OBJECTIVE_READINESS",
                "G59_CONVERSATION_OWNER",
            ),
            _requirement(
                "OBJECTIVE_COMMITMENT",
                "HUMAN_AUTHORITY_PLUS_G59_CONVERSATION",
            ),
            _requirement(
                "COMMITTED_OBJECTIVE_HANDOFF",
                "G60_ORCHESTRATION_OWNER",
            ),
            _requirement(
                "PLATFORM_ADMISSION",
                "PLATFORM_CORE_PROJECT_SERVICES",
            ),
        ),
        terminal_branch=False,
    ),
    CanonicalWorkflowBranchDefinitionV1(
        branch_kind=CERTIFIED_REUSE,
        decision_owner="G64_PRODUCTION_REUSE_PROOF_OWNER",
        predicate=_predicate(
            "reuse_disposition",
            "CERTIFIED_CAPABILITY_REUSE",
            "G64_PRODUCTION_REUSE_PROOF_OWNER",
            "PRODUCTION_REUSE_PROOF",
        ),
        allowed_predecessor_branches=(GOVERNED_ACTION,),
        allowed_successor_branches=(
            NON_MUTATING_CAPABILITY,
            CONTENT_OR_REPOSITORY_MUTATION,
        ),
        required_evidence=(
            _requirement(
                "PRODUCTION_REUSE_PROOF",
                "G64_PRODUCTION_REUSE_PROOF_OWNER",
            ),
            _requirement(
                "CERTIFIED_CAPABILITY_COVERAGE",
                "PLATFORM_CAPABILITY_OWNER",
            ),
        ),
        terminal_branch=False,
    ),
    CanonicalWorkflowBranchDefinitionV1(
        branch_kind=GOVERNED_DEVELOPMENT,
        decision_owner="G47_DEVELOPMENT_GOVERNANCE_OWNER",
        predicate=_predicate(
            "reuse_disposition",
            "FRESH_GOVERNED_DEVELOPMENT_REQUIRED",
            "G64_PRODUCTION_REUSE_PROOF_OWNER",
            "PRODUCTION_REUSE_PROOF",
        ),
        allowed_predecessor_branches=(GOVERNED_ACTION,),
        allowed_successor_branches=(
            NON_MUTATING_CAPABILITY,
            CONTENT_OR_REPOSITORY_MUTATION,
        ),
        required_evidence=(
            _requirement(
                "PRODUCTION_REUSE_PROOF",
                "G64_PRODUCTION_REUSE_PROOF_OWNER",
            ),
            _requirement(
                "G47_PLANNING_ELIGIBILITY",
                "G47_DEVELOPMENT_GOVERNANCE_OWNER",
            ),
            _requirement(
                "PLAN_DURABLE_WORK_APPROVAL",
                "PLANNER_DURABLE_WORK_APPROVAL_OWNERS",
            ),
        ),
        terminal_branch=False,
    ),
    CanonicalWorkflowBranchDefinitionV1(
        branch_kind=NON_MUTATING_CAPABILITY,
        decision_owner="RESULT_VALIDATION_OWNER",
        predicate=_predicate(
            "validated_effect_class",
            NON_MUTATING_CAPABILITY,
            "RESULT_VALIDATION_OWNER",
            "VALIDATED_RESULT",
        ),
        allowed_predecessor_branches=(CERTIFIED_REUSE, GOVERNED_DEVELOPMENT),
        allowed_successor_branches=(HUMAN_RETURN,),
        required_evidence=(
            _requirement(
                "CAPABILITY_ROUTE_EXECUTION_PREPARATION",
                "PLATFORM_CAPABILITY_AND_PREPARATION_OWNERS",
            ),
            _requirement(
                "EXECUTION_SUMMARY_HUMAN_DECISION",
                "SUMMARY_OWNER_PLUS_HUMAN_AUTHORITY",
            ),
            _requirement(
                "EXECUTION_AUTHORIZATION",
                "EXECUTION_AUTHORIZATION_OWNER",
            ),
            _requirement(
                "WORKER_SELECTION_INVOCATION_REQUEST",
                "SELECTION_AND_WORKER_REQUEST_OWNERS",
            ),
            _requirement(
                "WORKER_ASSIGNMENT",
                "WORKER_LIFECYCLE_OWNER",
            ),
            _requirement(
                "WORKER_DISPATCH_INVOCATION",
                "WORKER_LIFECYCLE_OWNER",
            ),
            _requirement(
                "EXECUTION_CANDIDATE_ACTIVATION",
                "EXECUTION_WORKER_PROVIDER_OWNERS",
            ),
            _requirement("RESULT_CAPTURE", "RESULT_OWNER"),
            _requirement("VALIDATED_RESULT", "RESULT_VALIDATION_OWNER"),
            _requirement(
                "CAPABILITY_COMPLETION",
                "CAPABILITY_COMPLETION_OWNER",
            ),
            _requirement(
                "POST_EXECUTION_REPLAY_REVIEW",
                "REPLAY_REVIEW_OWNER",
            ),
            _requirement(
                "GOVERNED_TERMINATION",
                "TERMINATION_OWNER",
            ),
            _requirement(
                "FINAL_EXECUTION_CERTIFICATION",
                "FINAL_EXECUTION_CERTIFICATION_OWNER",
            ),
        ),
        terminal_branch=False,
    ),
    CanonicalWorkflowBranchDefinitionV1(
        branch_kind=CONTENT_OR_REPOSITORY_MUTATION,
        decision_owner="HUMAN_AUTHORITY_PLUS_MUTATION_AUTHORIZATION",
        predicate=_predicate(
            "validated_effect_class",
            CONTENT_OR_REPOSITORY_MUTATION,
            "RESULT_VALIDATION_OWNER",
            "VALIDATED_RESULT",
        ),
        allowed_predecessor_branches=(CERTIFIED_REUSE, GOVERNED_DEVELOPMENT),
        allowed_successor_branches=(HUMAN_RETURN, CONSTITUTIONAL_COMPLETION),
        required_evidence=(
            _requirement(
                "CAPABILITY_ROUTE_EXECUTION_PREPARATION",
                "PLATFORM_CAPABILITY_AND_PREPARATION_OWNERS",
            ),
            _requirement(
                "EXECUTION_SUMMARY_HUMAN_DECISION",
                "SUMMARY_OWNER_PLUS_HUMAN_AUTHORITY",
            ),
            _requirement(
                "EXECUTION_AUTHORIZATION",
                "EXECUTION_AUTHORIZATION_OWNER",
            ),
            _requirement(
                "WORKER_SELECTION_INVOCATION_REQUEST",
                "SELECTION_AND_WORKER_REQUEST_OWNERS",
            ),
            _requirement(
                "WORKER_ASSIGNMENT",
                "WORKER_LIFECYCLE_OWNER",
            ),
            _requirement(
                "WORKER_DISPATCH_INVOCATION",
                "WORKER_LIFECYCLE_OWNER",
            ),
            _requirement(
                "EXECUTION_CANDIDATE_ACTIVATION",
                "EXECUTION_WORKER_PROVIDER_OWNERS",
            ),
            _requirement("RESULT_CAPTURE", "RESULT_OWNER"),
            _requirement("VALIDATED_RESULT", "RESULT_VALIDATION_OWNER"),
            _requirement(
                "OUTCOME_ACCEPTANCE_PREPARATION",
                "HUMAN_RESULT_AND_ACCEPTANCE_OWNERS",
            ),
            _requirement(
                "CONTENT_ACCEPTANCE_DECISION",
                "HUMAN_AUTHORITY_PLUS_ACCEPTANCE_OWNER",
            ),
            _requirement(
                "MUTATION_AUTHORIZATION",
                "MUTATION_AUTHORIZATION_OWNER",
            ),
            _requirement(
                "REPLACEMENT_WORKER_RESULT",
                "FILESYSTEM_WORKER_AND_RESULT_OWNERS",
            ),
            _requirement(
                "POST_EXECUTION_REPLAY_REVIEW",
                "REPLAY_REVIEW_OWNER",
            ),
            _requirement(
                "GOVERNED_TERMINATION",
                "TERMINATION_OWNER",
            ),
            _requirement(
                "FINAL_EXECUTION_CERTIFICATION",
                "FINAL_EXECUTION_CERTIFICATION_OWNER",
            ),
        ),
        terminal_branch=False,
    ),
    CanonicalWorkflowBranchDefinitionV1(
        branch_kind=HUMAN_RETURN,
        decision_owner="CANONICAL_HIR_PRESENTATION_OWNER",
        predicate=_predicate(
            "human_return_eligibility",
            "BRANCH_TERMINAL_EVIDENCE_COMPLETE",
            "BRANCH_TERMINAL_OWNER",
            "BRANCH_TERMINAL_EVIDENCE",
        ),
        allowed_predecessor_branches=(
            READ_ONLY,
            NON_MUTATING_CAPABILITY,
            CONTENT_OR_REPOSITORY_MUTATION,
            CONSTITUTIONAL_COMPLETION,
        ),
        allowed_successor_branches=(),
        required_evidence=(
            _requirement(
                "BRANCH_TERMINAL_EVIDENCE",
                "BRANCH_TERMINAL_OWNER",
            ),
            _requirement(
                "CANONICAL_PRESENTATION",
                "CANONICAL_HIR_PRESENTATION_OWNER",
            ),
        ),
        terminal_branch=True,
    ),
    CanonicalWorkflowBranchDefinitionV1(
        branch_kind=CONSTITUTIONAL_COMPLETION,
        decision_owner="G64_CONSTITUTIONAL_COMPLETION_OWNER",
        predicate=_predicate(
            "constitutional_completion_applicability",
            "GOVERNED_DEVELOPMENT_CHANGE_VALIDATED",
            "G64_CONSTITUTIONAL_COMPLETION_OWNER",
            "GOVERNED_DEVELOPMENT_PENDING_COMPLETION",
        ),
        allowed_predecessor_branches=(CONTENT_OR_REPOSITORY_MUTATION,),
        allowed_successor_branches=(HUMAN_RETURN,),
        required_evidence=(
            _requirement(
                "GOVERNED_DEVELOPMENT_PENDING_COMPLETION",
                "G64_CONSTITUTIONAL_COMPLETION_OWNER",
            ),
            _requirement("EXTERNAL_G48_REPORT", "G48_REPORTING_OWNER"),
            _requirement(
                "GOVERNANCE_ASSESSMENT",
                "DEVELOPMENT_GOVERNANCE_OWNER",
            ),
            _requirement(
                "CONSTITUTIONAL_CERTIFICATION",
                "CONSTITUTIONAL_CERTIFICATION_OWNER",
            ),
            _requirement("PROMOTION_DECISION", "PROMOTION_OWNER"),
        ),
        terminal_branch=False,
    ),
)


@dataclass(frozen=True, slots=True)
class CanonicalProductionWorkflowBranchModelV1:
    """Immutable complete branch graph with fixed production invariants."""

    contract_version: str
    model_identity: str
    canonical_entry_identity: str
    branch_definitions: tuple[CanonicalWorkflowBranchDefinitionV1, ...]
    che_definition_count: int
    production_hic_family_count: int
    production_owner_chain_count: int
    production_path_count: int
    parallel_production_path_count: int
    hic_responsibility: str
    hic_semantic_capability: str
    workflow_execution_capability: str
    production_route_creation_capability: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "contract_version",
            _require_text(self.contract_version, "contract_version"),
        )
        object.__setattr__(
            self,
            "model_identity",
            _require_text(self.model_identity, "model_identity"),
        )
        object.__setattr__(
            self,
            "canonical_entry_identity",
            _require_text(self.canonical_entry_identity, "canonical_entry_identity"),
        )
        if not isinstance(self.branch_definitions, tuple) or any(
            not isinstance(item, CanonicalWorkflowBranchDefinitionV1)
            for item in self.branch_definitions
        ):
            raise FailClosedRuntimeError(
                "workflow branch definitions are malformed"
            )
        for field_name in (
            "che_definition_count",
            "production_hic_family_count",
            "production_owner_chain_count",
            "production_path_count",
        ):
            _require_positive_integer(getattr(self, field_name), field_name)
        if (
            not isinstance(self.parallel_production_path_count, int)
            or isinstance(self.parallel_production_path_count, bool)
            or self.parallel_production_path_count < 0
        ):
            raise FailClosedRuntimeError(
                "workflow branch parallel path count is malformed"
            )
        for field_name in (
            "hic_responsibility",
            "hic_semantic_capability",
            "workflow_execution_capability",
            "production_route_creation_capability",
        ):
            object.__setattr__(
                self,
                field_name,
                _require_text(getattr(self, field_name), field_name),
            )

    def identity_payload(self) -> dict[str, Any]:
        return {
            "contract_version": self.contract_version,
            "canonical_entry_identity": self.canonical_entry_identity,
            "branch_definitions": [
                item.to_dict() for item in self.branch_definitions
            ],
            "che_definition_count": self.che_definition_count,
            "production_hic_family_count": self.production_hic_family_count,
            "production_owner_chain_count": self.production_owner_chain_count,
            "production_path_count": self.production_path_count,
            "parallel_production_path_count": self.parallel_production_path_count,
            "hic_responsibility": self.hic_responsibility,
            "hic_semantic_capability": self.hic_semantic_capability,
            "workflow_execution_capability": self.workflow_execution_capability,
            "production_route_creation_capability": (
                self.production_route_creation_capability
            ),
        }

    def to_dict(self) -> dict[str, Any]:
        return {"model_identity": self.model_identity, **self.identity_payload()}

    @classmethod
    def from_dict(
        cls, value: Mapping[str, Any]
    ) -> "CanonicalProductionWorkflowBranchModelV1":
        if not isinstance(value, Mapping) or set(value) != {
            "contract_version",
            "model_identity",
            "canonical_entry_identity",
            "branch_definitions",
            "che_definition_count",
            "production_hic_family_count",
            "production_owner_chain_count",
            "production_path_count",
            "parallel_production_path_count",
            "hic_responsibility",
            "hic_semantic_capability",
            "workflow_execution_capability",
            "production_route_creation_capability",
        }:
            raise FailClosedRuntimeError("workflow branch model is malformed")
        return cls(
            contract_version=value["contract_version"],
            model_identity=value["model_identity"],
            canonical_entry_identity=value["canonical_entry_identity"],
            branch_definitions=tuple(
                CanonicalWorkflowBranchDefinitionV1.from_dict(item)
                for item in value["branch_definitions"]
            ),
            che_definition_count=value["che_definition_count"],
            production_hic_family_count=value["production_hic_family_count"],
            production_owner_chain_count=value["production_owner_chain_count"],
            production_path_count=value["production_path_count"],
            parallel_production_path_count=value["parallel_production_path_count"],
            hic_responsibility=value["hic_responsibility"],
            hic_semantic_capability=value["hic_semantic_capability"],
            workflow_execution_capability=value["workflow_execution_capability"],
            production_route_creation_capability=value[
                "production_route_creation_capability"
            ],
        )


def create_canonical_production_workflow_branch_model_v1(
) -> CanonicalProductionWorkflowBranchModelV1:
    provisional = CanonicalProductionWorkflowBranchModelV1(
        contract_version=CANONICAL_PRODUCTION_WORKFLOW_BRANCH_CONTRACT_VERSION,
        model_identity="PENDING-CANONICAL-IDENTITY",
        canonical_entry_identity="CANONICAL_HUMAN_ENTRY",
        branch_definitions=CANONICAL_WORKFLOW_BRANCH_DEFINITIONS,
        che_definition_count=1,
        production_hic_family_count=1,
        production_owner_chain_count=1,
        production_path_count=1,
        parallel_production_path_count=0,
        hic_responsibility=TRANSPORT_ONLY,
        hic_semantic_capability=NO_SEMANTIC_CAPABILITY,
        workflow_execution_capability=NO_WORKFLOW_EXECUTION,
        production_route_creation_capability=NO_PRODUCTION_ROUTE_CREATION,
    )
    return replace(
        provisional,
        model_identity=_identity(
            CANONICAL_PRODUCTION_WORKFLOW_BRANCH_MODEL_IDENTITY_PREFIX,
            provisional.identity_payload(),
        ),
    )


def validate_canonical_production_workflow_branch_model_v1(
    value: CanonicalProductionWorkflowBranchModelV1 | Mapping[str, Any],
) -> CanonicalProductionWorkflowBranchModelV1:
    model = (
        value
        if isinstance(value, CanonicalProductionWorkflowBranchModelV1)
        else CanonicalProductionWorkflowBranchModelV1.from_dict(value)
    )
    if model.contract_version != CANONICAL_PRODUCTION_WORKFLOW_BRANCH_CONTRACT_VERSION:
        raise FailClosedRuntimeError("workflow branch contract version is invalid")
    if model.canonical_entry_identity != "CANONICAL_HUMAN_ENTRY":
        raise FailClosedRuntimeError("workflow branch canonical entry is invalid")
    if model.branch_definitions != CANONICAL_WORKFLOW_BRANCH_DEFINITIONS:
        raise FailClosedRuntimeError("workflow branch graph is not canonical")
    for definition in model.branch_definitions:
        for successor in definition.allowed_successor_branches:
            successor_definition = _branch_definition(model, successor)
            if definition.branch_kind not in (
                successor_definition.allowed_predecessor_branches
            ):
                raise FailClosedRuntimeError(
                    "workflow branch graph is not reciprocal"
                )
    expected_invariants = (
        model.che_definition_count,
        model.production_hic_family_count,
        model.production_owner_chain_count,
        model.production_path_count,
        model.parallel_production_path_count,
        model.hic_responsibility,
        model.hic_semantic_capability,
        model.workflow_execution_capability,
        model.production_route_creation_capability,
    )
    if expected_invariants != (
        1,
        1,
        1,
        1,
        0,
        TRANSPORT_ONLY,
        NO_SEMANTIC_CAPABILITY,
        NO_WORKFLOW_EXECUTION,
        NO_PRODUCTION_ROUTE_CREATION,
    ):
        raise FailClosedRuntimeError(
            "workflow branch production invariants are invalid"
        )
    expected_identity = _identity(
        CANONICAL_PRODUCTION_WORKFLOW_BRANCH_MODEL_IDENTITY_PREFIX,
        model.identity_payload(),
    )
    if model.model_identity != expected_identity:
        raise FailClosedRuntimeError("workflow branch model identity is invalid")
    return model


@dataclass(frozen=True, slots=True)
class CanonicalWorkflowEvidenceReferenceV1:
    """Reference-only owner evidence used to validate one branch fact."""

    evidence_role: str
    producing_owner: str
    artifact_identity: str
    artifact_digest: str

    def __post_init__(self) -> None:
        for field_name in (
            "evidence_role",
            "producing_owner",
            "artifact_identity",
        ):
            object.__setattr__(
                self,
                field_name,
                _require_text(getattr(self, field_name), field_name),
            )
        object.__setattr__(
            self,
            "artifact_digest",
            _require_sha256(self.artifact_digest, "artifact_digest"),
        )

    def to_dict(self) -> dict[str, str]:
        return {
            "evidence_role": self.evidence_role,
            "producing_owner": self.producing_owner,
            "artifact_identity": self.artifact_identity,
            "artifact_digest": self.artifact_digest,
        }

    @classmethod
    def from_dict(
        cls, value: Mapping[str, Any]
    ) -> "CanonicalWorkflowEvidenceReferenceV1":
        if not isinstance(value, Mapping) or set(value) != {
            "evidence_role",
            "producing_owner",
            "artifact_identity",
            "artifact_digest",
        }:
            raise FailClosedRuntimeError(
                "workflow branch evidence reference is malformed"
            )
        return cls(**dict(value))


@dataclass(frozen=True, slots=True)
class CanonicalWorkflowBranchProvenanceV1:
    """Immutable owner-evidence binding for one caller-selected branch."""

    contract_version: str
    provenance_identity: str
    model_identity: str
    source_request_identity: str
    source_interaction_identity: str
    branch_sequence: int
    branch_kind: str
    predecessor_branch_kind: str | None
    previous_provenance_identity: str | None
    predicate_facts: Mapping[str, str]
    evidence_references: tuple[CanonicalWorkflowEvidenceReferenceV1, ...]
    observed_at: str

    def __post_init__(self) -> None:
        for field_name in (
            "contract_version",
            "provenance_identity",
            "model_identity",
            "source_request_identity",
            "source_interaction_identity",
            "branch_kind",
            "observed_at",
        ):
            object.__setattr__(
                self,
                field_name,
                _require_text(getattr(self, field_name), field_name),
            )
        object.__setattr__(
            self,
            "branch_sequence",
            _require_positive_integer(self.branch_sequence, "branch_sequence"),
        )
        for field_name in (
            "predecessor_branch_kind",
            "previous_provenance_identity",
        ):
            value = getattr(self, field_name)
            if value is not None:
                object.__setattr__(
                    self,
                    field_name,
                    _require_text(value, field_name),
                )
        if not isinstance(self.predicate_facts, Mapping):
            raise FailClosedRuntimeError(
                "workflow branch predicate facts are malformed"
            )
        facts = dict(self.predicate_facts)
        if any(
            not isinstance(key, str)
            or not isinstance(item, str)
            or not key.strip()
            or not item.strip()
            for key, item in facts.items()
        ):
            raise FailClosedRuntimeError(
                "workflow branch predicate facts are malformed"
            )
        object.__setattr__(self, "predicate_facts", MappingProxyType(facts))
        if not isinstance(self.evidence_references, tuple) or any(
            not isinstance(item, CanonicalWorkflowEvidenceReferenceV1)
            for item in self.evidence_references
        ):
            raise FailClosedRuntimeError(
                "workflow branch evidence references are malformed"
            )

    def identity_payload(self) -> dict[str, Any]:
        return {
            "contract_version": self.contract_version,
            "model_identity": self.model_identity,
            "source_request_identity": self.source_request_identity,
            "source_interaction_identity": self.source_interaction_identity,
            "branch_sequence": self.branch_sequence,
            "branch_kind": self.branch_kind,
            "predecessor_branch_kind": self.predecessor_branch_kind,
            "previous_provenance_identity": self.previous_provenance_identity,
            "predicate_facts": dict(self.predicate_facts),
            "evidence_references": [
                item.to_dict() for item in self.evidence_references
            ],
            "observed_at": self.observed_at,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "provenance_identity": self.provenance_identity,
            **self.identity_payload(),
        }

    @classmethod
    def from_dict(
        cls, value: Mapping[str, Any]
    ) -> "CanonicalWorkflowBranchProvenanceV1":
        if not isinstance(value, Mapping) or set(value) != {
            "contract_version",
            "provenance_identity",
            "model_identity",
            "source_request_identity",
            "source_interaction_identity",
            "branch_sequence",
            "branch_kind",
            "predecessor_branch_kind",
            "previous_provenance_identity",
            "predicate_facts",
            "evidence_references",
            "observed_at",
        }:
            raise FailClosedRuntimeError(
                "workflow branch provenance is malformed"
            )
        return cls(
            contract_version=value["contract_version"],
            provenance_identity=value["provenance_identity"],
            model_identity=value["model_identity"],
            source_request_identity=value["source_request_identity"],
            source_interaction_identity=value["source_interaction_identity"],
            branch_sequence=value["branch_sequence"],
            branch_kind=value["branch_kind"],
            predecessor_branch_kind=value["predecessor_branch_kind"],
            previous_provenance_identity=value["previous_provenance_identity"],
            predicate_facts=value["predicate_facts"],
            evidence_references=tuple(
                CanonicalWorkflowEvidenceReferenceV1.from_dict(item)
                for item in value["evidence_references"]
            ),
            observed_at=value["observed_at"],
        )


def _branch_definition(
    model: CanonicalProductionWorkflowBranchModelV1,
    branch_kind: str,
) -> CanonicalWorkflowBranchDefinitionV1:
    for definition in model.branch_definitions:
        if definition.branch_kind == branch_kind:
            return definition
    raise FailClosedRuntimeError("workflow branch kind is not canonical")


def _validate_branch_evidence(
    definition: CanonicalWorkflowBranchDefinitionV1,
    evidence_references: tuple[CanonicalWorkflowEvidenceReferenceV1, ...],
) -> None:
    actual = tuple(
        (item.evidence_role, item.producing_owner)
        for item in evidence_references
    )
    if len({item[0] for item in actual}) != len(evidence_references):
        raise FailClosedRuntimeError(
            "workflow branch evidence roles are duplicated"
        )
    expected = tuple(
        (item.evidence_role, item.producing_owner)
        for item in definition.required_evidence
    )
    if actual != expected:
        raise FailClosedRuntimeError(
            "workflow branch owner evidence or sequence does not match the contract"
        )


def bind_canonical_workflow_branch_provenance_v1(
    *,
    model: CanonicalProductionWorkflowBranchModelV1 | Mapping[str, Any],
    source_request_identity: str,
    source_interaction_identity: str,
    branch_sequence: int,
    branch_kind: str,
    predecessor_branch_kind: str | None,
    previous_provenance_identity: str | None,
    predicate_facts: Mapping[str, str],
    evidence_references: tuple[CanonicalWorkflowEvidenceReferenceV1, ...],
    observed_at: str,
) -> CanonicalWorkflowBranchProvenanceV1:
    """Bind already-produced owner facts without selecting or executing a branch."""

    canonical_model = validate_canonical_production_workflow_branch_model_v1(
        model
    )
    definition = _branch_definition(canonical_model, branch_kind)
    facts = dict(predicate_facts)
    if facts != {
        definition.predicate.fact_name: definition.predicate.expected_value
    }:
        raise FailClosedRuntimeError(
            "workflow branch predicate facts do not match the contract"
        )
    if definition.allowed_predecessor_branches:
        if predecessor_branch_kind not in definition.allowed_predecessor_branches:
            raise FailClosedRuntimeError(
                "workflow branch predecessor is not permitted"
            )
        _require_text(
            previous_provenance_identity,
            "previous_provenance_identity",
        )
    elif predecessor_branch_kind is not None or previous_provenance_identity is not None:
        raise FailClosedRuntimeError(
            "initial workflow branch cannot claim a predecessor"
        )
    _validate_branch_evidence(definition, evidence_references)
    provisional = CanonicalWorkflowBranchProvenanceV1(
        contract_version=CANONICAL_PRODUCTION_WORKFLOW_BRANCH_CONTRACT_VERSION,
        provenance_identity="PENDING-CANONICAL-IDENTITY",
        model_identity=canonical_model.model_identity,
        source_request_identity=source_request_identity,
        source_interaction_identity=source_interaction_identity,
        branch_sequence=branch_sequence,
        branch_kind=branch_kind,
        predecessor_branch_kind=predecessor_branch_kind,
        previous_provenance_identity=previous_provenance_identity,
        predicate_facts=facts,
        evidence_references=evidence_references,
        observed_at=observed_at,
    )
    return replace(
        provisional,
        provenance_identity=_identity(
            CANONICAL_WORKFLOW_BRANCH_PROVENANCE_IDENTITY_PREFIX,
            provisional.identity_payload(),
        ),
    )


def validate_canonical_workflow_branch_provenance_v1(
    *,
    model: CanonicalProductionWorkflowBranchModelV1 | Mapping[str, Any],
    value: CanonicalWorkflowBranchProvenanceV1 | Mapping[str, Any],
) -> CanonicalWorkflowBranchProvenanceV1:
    canonical_model = validate_canonical_production_workflow_branch_model_v1(
        model
    )
    provenance = (
        value
        if isinstance(value, CanonicalWorkflowBranchProvenanceV1)
        else CanonicalWorkflowBranchProvenanceV1.from_dict(value)
    )
    if provenance.contract_version != CANONICAL_PRODUCTION_WORKFLOW_BRANCH_CONTRACT_VERSION:
        raise FailClosedRuntimeError(
            "workflow branch provenance contract version is invalid"
        )
    if provenance.model_identity != canonical_model.model_identity:
        raise FailClosedRuntimeError(
            "workflow branch provenance model binding is invalid"
        )
    definition = _branch_definition(canonical_model, provenance.branch_kind)
    if dict(provenance.predicate_facts) != {
        definition.predicate.fact_name: definition.predicate.expected_value
    }:
        raise FailClosedRuntimeError(
            "workflow branch predicate facts do not match the contract"
        )
    if definition.allowed_predecessor_branches:
        if provenance.predecessor_branch_kind not in (
            definition.allowed_predecessor_branches
        ) or provenance.previous_provenance_identity is None:
            raise FailClosedRuntimeError(
                "workflow branch predecessor is not permitted"
            )
    elif (
        provenance.predecessor_branch_kind is not None
        or provenance.previous_provenance_identity is not None
    ):
        raise FailClosedRuntimeError(
            "initial workflow branch cannot claim a predecessor"
        )
    _validate_branch_evidence(definition, provenance.evidence_references)
    expected_identity = _identity(
        CANONICAL_WORKFLOW_BRANCH_PROVENANCE_IDENTITY_PREFIX,
        provenance.identity_payload(),
    )
    if provenance.provenance_identity != expected_identity:
        raise FailClosedRuntimeError(
            "workflow branch provenance identity is invalid"
        )
    return provenance


def validate_canonical_workflow_branch_journey_v1(
    *,
    model: CanonicalProductionWorkflowBranchModelV1 | Mapping[str, Any],
    provenances: tuple[CanonicalWorkflowBranchProvenanceV1, ...],
) -> tuple[CanonicalWorkflowBranchProvenanceV1, ...]:
    """Validate one immutable branch journey without routing or persistence."""

    canonical_model = validate_canonical_production_workflow_branch_model_v1(
        model
    )
    if not isinstance(provenances, tuple) or not provenances:
        raise FailClosedRuntimeError("workflow branch journey is absent")
    validated = tuple(
        validate_canonical_workflow_branch_provenance_v1(
            model=canonical_model,
            value=item,
        )
        for item in provenances
    )
    request_identity = validated[0].source_request_identity
    interaction_identity = validated[0].source_interaction_identity
    for index, current in enumerate(validated, start=1):
        if current.branch_sequence != index:
            raise FailClosedRuntimeError(
                "workflow branch journey sequence is invalid"
            )
        if (
            current.source_request_identity != request_identity
            or current.source_interaction_identity != interaction_identity
        ):
            raise FailClosedRuntimeError(
                "workflow branch journey source binding is invalid"
            )
        if index == 1:
            if current.predecessor_branch_kind is not None:
                raise FailClosedRuntimeError(
                    "workflow branch journey initial branch is invalid"
                )
            continue
        previous = validated[index - 2]
        if (
            current.predecessor_branch_kind != previous.branch_kind
            or current.previous_provenance_identity
            != previous.provenance_identity
        ):
            raise FailClosedRuntimeError(
                "workflow branch journey predecessor binding is invalid"
            )
        if (
            current.branch_kind == CONSTITUTIONAL_COMPLETION
            and GOVERNED_DEVELOPMENT
            not in tuple(item.branch_kind for item in validated[: index - 1])
        ):
            raise FailClosedRuntimeError(
                "constitutional completion lacks governed-development lineage"
            )
    final_definition = _branch_definition(
        canonical_model,
        validated[-1].branch_kind,
    )
    if not final_definition.terminal_branch:
        raise FailClosedRuntimeError(
            "workflow branch journey does not terminate at Human return"
        )
    return validated
