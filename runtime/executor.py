import time
import json
import grpc
import yaml

import messages_pb2
import messages_pb2_grpc

from scheduler.dag_loader import load_dag

from runtime.queue_builder import (
    build_worker_queues
)

from statistics import median

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
    start_timestamp_ms
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
            start_timestamp_ms
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


def main():

    workflow_id = (
        "workflow_001"
    )

    mapping = (
        load_mapping()
    )

    graph = load_dag(
        "dags/test_dag.yaml"
    )

    tasks = (
        load_tasks()
    )["tasks"]

    workers = (
        load_workers()
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
    print("Clock offsets")

    for worker in workers["workers"]:

        offset = measure_offset(
            worker["ip"]
        )

        print(
            worker["id"],
            ":",
            offset,
            "ms"
        )

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

    for worker in workers["workers"]:

        adjusted_start = (

            start_timestamp_ms

            +

            worker_offsets[
                worker["id"]
            ]
        )

        print(
            "[START]",
            worker["id"],
            adjusted_start
        )

        start_workflow(

            worker["ip"],

            workflow_id,

            adjusted_start
        )

    print()
    print(
        "Workflow launched"
    )





if __name__ == "__main__":

    main()