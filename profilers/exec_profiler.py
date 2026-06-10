import grpc
import yaml
from pathlib import Path

import messages_pb2
import messages_pb2_grpc


WORKERS_FILE = Path("configs/workers.yaml")
TASKS_FILE = Path("configs/tasks.yaml")
OUTPUT_FILE = Path("configs/execution_profiles.yaml")


def load_workers():

    with open(WORKERS_FILE, "r") as f:
        return yaml.safe_load(f)["workers"]


def load_tasks():

    with open(TASKS_FILE, "r") as f:
        return yaml.safe_load(f)["tasks"]


def profile_task(worker, command, runs=5):

    channel = grpc.insecure_channel(
        f"{worker['ip']}:{worker['grpc_port']}"
    )

    stub = messages_pb2_grpc.WorkerServiceStub(
        channel
    )

    response = stub.ProfileTask(
        messages_pb2.TaskProfileRequest(
            command=command,
            runs=runs
        )
    )

    return {
        "mean_ms": round(
            response.mean_ms,
            2
        ),
        "min_ms": round(
            response.min_ms,
            2
        ),
        "max_ms": round(
            response.max_ms,
            2
        )
    }


def save_profiles(profile_data):

    with open(OUTPUT_FILE, "w") as f:

        yaml.dump(
            profile_data,
            f,
            default_flow_style=False,
            sort_keys=False
        )


def build_execution_matrix():

    workers = load_workers()

    tasks = load_tasks()

    profile_data = {
        "task_types": {}
    }

    for task_name, task_info in tasks.items():

        command = task_info["command"]

        profile_data["task_types"][
            task_name
        ] = {}

        for worker in workers:

            worker_id = worker["id"]

            result = profile_task(
                worker,
                command
            )

            profile_data["task_types"][
                task_name
            ][worker_id] = result

    save_profiles(profile_data)

    return profile_data


if __name__ == "__main__":

    build_execution_matrix()