"""Candidate H Stage-1 canonical bytes and frozen data models."""

from .cj1 import (
    CJ1Error,
    cj1_decode,
    cj1_digest,
    cj1_encode,
    cj1_identity,
    sha256_hex,
)
from . import models as _models
from .models import (
    AUTHENTICATION_CONTRACT_VERSION,
    G77_62_MODEL_SPECS,
    HUMAN_AUTHORITY,
    MODEL_REGISTRY,
    MODEL_OWNER_RULES,
    CanonicalModelError,
    FrozenCanonicalModel,
)

for _model_name, _model_type in MODEL_REGISTRY.items():
    globals()[_model_name] = _model_type

__all__ = [
    "AUTHENTICATION_CONTRACT_VERSION",
    "CJ1Error",
    "CanonicalModelError",
    "FrozenCanonicalModel",
    "G77_62_MODEL_SPECS",
    "HUMAN_AUTHORITY",
    "MODEL_REGISTRY",
    "MODEL_OWNER_RULES",
    "cj1_decode",
    "cj1_digest",
    "cj1_encode",
    "cj1_identity",
    "sha256_hex",
] + sorted(MODEL_REGISTRY)
