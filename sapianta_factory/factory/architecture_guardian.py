import os

FORBIDDEN_PATHS = [
    "sapianta_system",
    "sapianta-domain-credit",
    "sapianta-domain-trading"
]


def validate_candidate(path: str):

    abs_path = os.path.abspath(path)

    for forbidden in FORBIDDEN_PATHS:

        if forbidden in abs_path:
            raise Exception(
                f"Candidate cannot access protected path: {forbidden}"
            )

    return True