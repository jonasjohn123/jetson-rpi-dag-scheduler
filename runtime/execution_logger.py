import json
from pathlib import Path


LOG_FILE = Path(
    "results/execution_log.json"
)


def log_execution(entry):

    logs = []

    if LOG_FILE.exists():

        with open(
            LOG_FILE,
            "r"
        ) as f:

            logs = json.load(f)

    logs.append(entry)

    with open(
        LOG_FILE,
        "w"
    ) as f:

        json.dump(
            logs,
            f,
            indent=4
        )