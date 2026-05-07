import json
import os
import hashlib
from datetime import datetime

ARTIFACT_ROOT = "../artifacts"


def _hash(data: dict) -> str:
    serialized = json.dumps(data, sort_keys=True)
    return hashlib.sha256(serialized.encode()).hexdigest()


def store_experiment(experiment: dict) -> str:

    experiment["timestamp"] = datetime.utcnow().isoformat()

    experiment_hash = _hash(experiment)

    path = os.path.join(ARTIFACT_ROOT, "experiments", f"{experiment_hash}.json")

    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w") as f:
        json.dump(experiment, f, indent=2)

    return experiment_hash


def store_result(result: dict) -> str:

    result["timestamp"] = datetime.utcnow().isoformat()

    result_hash = _hash(result)

    path = os.path.join(ARTIFACT_ROOT, "results", f"{result_hash}.json")

    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w") as f:
        json.dump(result, f, indent=2)

    return result_hash