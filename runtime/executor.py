import time
import json
import grpc
import yaml

from pathlib import Path
import json

import messages_pb2
import messages_pb2_grpc

from scheduler.dag_loader import load_dag

from runtime.queue_builder import (
    build_worker_queues
)

from statistics import median

from statistics import median

import shutil
from pathlib import Path

COMPENSATION_THRESHOLD_MS = 50
MAX_ALLOWED_OFFSET_MS = 1000

def clean_workflow_artifacts(
    workflow_id
):

    path = Path(
        "artifacts"
    ) / workflow_id

    if path.exists():

        shutil.rmtree(
            path
        )

        print(
            "[CLEANED]",
            path
        )

def load_mapping():

    with open(
        "results/mapping.json",
        "r"
    ) as f:

        return json.load(f)


def load_workers():

    with open(
        "configs/workers.yaml",
        "r"
    ) as f:

        return yaml.safe_load(f)


def load_tasks():

    with open(
        "configs/tasks.yaml",
        "r"
    ) as f:

        return yaml.safe_load(f)


def build_worker_lookup():

    workers = load_workers()

    lookup = {}

    for worker in workers["workers"]:

        lookup[
            worker["id"]
        ] = worker

    return lookup


def upload_schedule(
    worker_ip,
    workflow_id,
    tasks
):

    channel = grpc.insecure_channel(
        f"{worker_ip}:50051"
    )

    stub = (
        messages_pb2_grpc
        .WorkerServiceStub(
            channel
        )
    )

    schedule = (
        messages_pb2.WorkerSchedule(
            workflow_id=workflow_id,
            tasks=tasks
        )
    )

    return (
        stub.UploadSchedule(
            schedule
        )
    )


def start_workflow(
    worker_ip,
    workflow_id,
    start_timestamp_ms,
    worker_offset_ms
):

    channel = grpc.insecure_channel(
        f"{worker_ip}:50051"
    )

    stub = (
        messages_pb2_grpc
        .WorkerServiceStub(
            channel
        )
    )

    request = (
        messages_pb2.StartWorkflowRequest(
            workflow_id=workflow_id,
            start_timestamp_ms=
            start_timestamp_ms,
            worker_offset_ms=
            worker_offset_ms
        )
    )

    return (
        stub.StartWorkflow(
            request
        )
    )


def measure_offset(
    worker_ip,
    samples=20
):

    channel = grpc.insecure_channel(
        f"{worker_ip}:50051"
    )

    stub = (
        messages_pb2_grpc
        .WorkerServiceStub(
            channel
        )
    )

    offsets = []

    for _ in range(samples):

        t1 = int(
            time.time() * 1000
        )

        response = stub.GetTime(
            messages_pb2.TimeRequest()
        )

        t3 = int(
            time.time() * 1000
        )

        t2 = response.timestamp_ms

        rtt = t3 - t1

        offset = (
            t2
            -
            (
                t1
                + rtt / 2
            )
        )

        offsets.append(offset)

    return int(
        median(offsets)
    )

def clear_workflow(
    worker_ip,
    workflow_id
):

    channel = grpc.insecure_channel(
        f"{worker_ip}:50051"
    )

    stub = (
        messages_pb2_grpc
        .WorkerServiceStub(
            channel
        )
    )

    request = (
        messages_pb2
        .ClearWorkflowRequest(

            workflow_id=
            workflow_id
        )
    )

    return (
        stub.ClearWorkflow(
            request
        )
    )

def get_execution_log(
    worker_ip,
    workflow_id
):

    channel = grpc.insecure_channel(
        f"{worker_ip}:50051"
    )

    stub = (
        messages_pb2_grpc
        .WorkerServiceStub(
            channel
        )
    )

    response = stub.GetExecutionLog(

        messages_pb2
        .ExecutionLogRequest(

            workflow_id=
            workflow_id
        )
    )

    return json.loads(
        response.json_data
    )

def get_workflow_status(
    worker_ip,
    workflow_id
):

    channel = grpc.insecure_channel(
        f"{worker_ip}:50051"
    )

    stub = (
        messages_pb2_grpc
        .WorkerServiceStub(
            channel
        )
    )

    return stub.WorkflowStatus(

        messages_pb2
        .WorkflowStatusRequest(

            workflow_id=
            workflow_id
        )
    )


def main():

    workflow_id = (
        "workflow_001"
    )



    workflow_dir = (
        Path("results")
        / workflow_id
    )

    workflow_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        workflow_dir
        / "execution_log.json",
        "w"
    ) as f:

        json.dump(
            [],
            f,
            indent=4
        )

    

    mapping = (
        load_mapping()
    )

    with open(
        workflow_dir
        / "schedule.json",
        "w"
    ) as f:

        json.dump(
            mapping,
            f,
            indent=4
        )

    graph = load_dag(
        "dags/branching_dag.yaml"
    )

    tasks = (
        load_tasks()
    )["tasks"]

    workers = (
        load_workers()
    )

    print()
    print(
        "Cleaning artifacts..."
    )

    for worker in workers["workers"]:

        response = clear_workflow(

            worker["ip"],

            workflow_id
        )

        print(

            worker["id"],

            response.message
        )

    worker_lookup = (
        build_worker_lookup()
    )

    queues = (
        build_worker_queues(
            workflow_id,
            graph,
            mapping,
            tasks,
            workers
        )
    )

    for worker_id, queue in queues.items():

        print()
        print(
            f"=== {worker_id} ==="
        )

        for task in queue:

            print(
                task.task_id
            )

            print(
                task.command
            )

            print()

    print()
    print(
        "Uploading schedules..."
    )

    for worker_id, queue in (
        queues.items()
    ):

        worker_ip = (
            worker_lookup[
                worker_id
            ]["ip"]
        )

        response = (
            upload_schedule(
                worker_ip,
                workflow_id,
                queue
            )
        )

        print(
            worker_id,
            response.message
        )

    print()

    start_timestamp_ms = int(
        (
            time.time() + 10
        ) * 1000
    )

    print(
        "Workflow start:",
        start_timestamp_ms
    )

    worker_offsets = {}

    print()
    print("Clock validation")

    for worker in workers["workers"]:

        offset = measure_offset(
            worker["ip"]
        )

        worker_offsets[
            worker["id"]
        ] = offset

        print(
            "[OFFSET]",
            worker["id"],
            offset,
            "ms"
        )

        if abs(offset) > MAX_ALLOWED_OFFSET_MS:

            raise RuntimeError(

                f"{worker['id']} clock offset "

                f"too large: {offset} ms"

            )

    print()

    for worker in workers["workers"]:

        offset = worker_offsets[
            worker["id"]
        ]

        adjusted_start = (
            start_timestamp_ms
        )

        if abs(offset) > COMPENSATION_THRESHOLD_MS:

            adjusted_start = (

                start_timestamp_ms

                +

                offset

            )

            print(

                "[COMPENSATING]",

                worker["id"],

                offset,

                "ms"

            )

        else:

            print(

                "[SYNCED]",

                worker["id"],

                offset,

                "ms"

            )

        print(
            "[START]",
            worker["id"],
            adjusted_start
        )

        start_workflow(

            worker["ip"],

            workflow_id,

            adjusted_start,
            
            offset
        )

    print()
    print(
        "Workflow launched"
    )


    while True:

        all_done = True

        for worker in workers["workers"]:

            response = get_workflow_status(
                worker["ip"],
                workflow_id
            )

            if not response.completed:
                all_done = False

        if all_done:
            break

        time.sleep(1)

    combined_logs = []

    for worker in workers["workers"]:

        logs = get_execution_log(

            worker["ip"],

            workflow_id
        )

        combined_logs.extend(
            logs
        )

    combined_logs.sort(

        key=lambda entry:
        entry["scheduled_start"]
    )

    with open(

        workflow_dir
        / "execution_log.json",

        "w"

    ) as f:

        json.dump(

            combined_logs,

            f,

            indent=4
        )

    print()

    print(
        "[LOGS COLLECTED]",
        len(combined_logs),
        "entries"
    )

    print()

    for worker in workers["workers"]:

        logs = get_execution_log(

            worker["ip"],

            workflow_id
        )

        print(
            worker["id"],
            len(logs)
        )




if __name__ == "__main__":

    main()