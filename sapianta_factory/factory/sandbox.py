import importlib.util
import traceback
import uuid

from factory.registry import store_experiment, store_result
from factory.architecture_guardian import validate_candidate


def load_module(path: str):

    spec = importlib.util.spec_from_file_location("candidate_module", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


def run_experiment(module_path: str, input_data: dict):

    validate_candidate(module_path)

    experiment = {
        "id": str(uuid.uuid4()),
        "module": module_path,
        "input": input_data,
    }

    experiment_hash = store_experiment(experiment)

    try:

        module = load_module(module_path)

        if not hasattr(module, "run"):
            raise Exception("Module must implement run(input_data)")

        output = module.run(input_data)

        result = {
            "experiment_hash": experiment_hash,
            "status": "success",
            "output": output,
        }

    except Exception as e:

        result = {
            "experiment_hash": experiment_hash,
            "status": "error",
            "error": str(e),
            "trace": traceback.format_exc(),
        }

    result_hash = store_result(result)

    return result_hash