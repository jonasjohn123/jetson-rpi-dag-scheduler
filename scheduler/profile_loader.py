import yaml
from pathlib import Path


WORKERS_FILE = Path(
    "configs/workers.yaml"
)

EXECUTION_FILE = Path(
    "configs/execution_profiles.yaml"
)

NETWORK_FILE = Path(
    "configs/network_profiles.yaml"
)


def load_profiles():
    """
    Load HEFT cost tables.

    Returns:
        tuple:
            workers,
            exec_cost,
            comm_cost
    """

    with open(WORKERS_FILE, "r") as f:

        workers_data = yaml.safe_load(f)

    with open(EXECUTION_FILE, "r") as f:

        execution_data = yaml.safe_load(f)

    with open(NETWORK_FILE, "r") as f:

        network_data = yaml.safe_load(f)

    workers = [
        worker["id"]
        for worker in workers_data["workers"]
    ]

    exec_cost = {}

    for task_type, task_data in (
        execution_data["task_types"].items()
    ):

        exec_cost[task_type] = {}

        for worker_id, profile in (
            task_data.items()
        ):

            exec_cost[
                task_type
            ][worker_id] = profile[
                "mean_ms"
            ]

    comm_cost = {}

    for src, links in (
        network_data["links"].items()
    ):

        comm_cost[src] = {}

        for dst, profile in (
            links.items()
        ):

            comm_cost[src][dst] = (
                profile["latency_ms"]
            )

    return (
        workers,
        exec_cost,
        comm_cost
    )