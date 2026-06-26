import json
from pathlib import Path


def log_execution(entry):

    workflow_id = entry["workflow_id"]

    log_file = (

        Path("results")

        / workflow_id

        / "execution_log.json"
    )

    logs = []

    log_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    if log_file.exists():

        with open(
            log_file,
            "r"
        ) as f:

            logs = json.load(f)

    logs.append(entry)

    with open(
        log_file,
        "w"
    ) as f:

        json.dump(
            logs,
            f,
            indent=4
        )