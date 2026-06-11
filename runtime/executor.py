import json
import grpc
import yaml
import networkx as nx

import messages_pb2
import messages_pb2_grpc

from scheduler.dag_loader import load_dag


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


def execute_remote(
    worker_ip,
    command
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

    response = (
        stub.ExecuteTask(

            messages_pb2
            .ExecuteTaskRequest(
                command=command
            )
        )
    )

    return response


def main():

    mapping = (
        load_mapping()
    )

    graph = load_dag(
        "dags/test_dag.yaml"
    )

    tasks = (
        load_tasks()
    )["tasks"]

    worker_lookup = (
        build_worker_lookup()
    )

    execution_order = list(

        nx.topological_sort(
            graph
        )
    )

    print()

    print(
        "Execution Order:"
    )

    print(
        execution_order
    )

    print()

    for node in execution_order:

        schedule_info = (
            mapping[
                "schedule"
            ][node]
        )

        worker_id = (
            schedule_info[
                "worker"
            ]
        )

        task_type = (
            graph.nodes[node]
            ["task_type"]
        )

        command = (
            tasks[
                task_type
            ]["command"]
        )

        worker_ip = (
            worker_lookup[
                worker_id
            ]["ip"]
        )

        print(
            f"Executing {node}"
        )

        print(
            f"Task Type: {task_type}"
        )

        print(
            f"Worker: {worker_id}"
        )

        response = (
            execute_remote(
                worker_ip,
                command
            )
        )

        if response.success:

            print(
                "SUCCESS"
            )

            if response.output:

                print(
                    response.output
                )

        else:

            print(
                "FAILED"
            )

            print(
                response.output
            )

            return

        print()

    print(
        "Workflow Complete"
    )


if __name__ == "__main__":

    main()