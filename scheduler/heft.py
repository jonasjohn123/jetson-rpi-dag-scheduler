import json
from pathlib import Path

import networkx as nx

from scheduler.dag_loader import load_dag
from scheduler.profile_loader import load_profiles

from scheduler.cost_model import (
    get_avg_comm_cost,
    get_actual_comm_cost
)


def compute_ranks(
    graph,
    workers,
    exec_cost,
    comm_cost
):
    """
    Compute HEFT upward ranks.

    Args:
        graph (nx.DiGraph)
        workers (list[str])
        exec_cost (dict)
        comm_cost (dict)

    Returns:
        dict
    """

    n_workers = len(
        workers
    )

    avg_exec = {}

    for node in graph.nodes:

        task_type = graph.nodes[
            node
        ]["task_type"]

        avg_exec[node] = (
            sum(
                exec_cost[
                    task_type
                ][worker]

                for worker in workers
            )
            / n_workers
        )

    rank_cache = {}

    def rank_u(node):

        if node in rank_cache:

            return rank_cache[node]

        successors = list(
            graph.successors(node)
        )

        if not successors:

            rank_cache[node] = (
                avg_exec[node]
            )

            return rank_cache[node]

        max_successor = max(

            get_avg_comm_cost(

                graph.nodes[node][
                    "task_type"
                ],

                graph.nodes[succ][
                    "task_type"
                ]

            )

            + rank_u(succ)

            for succ in successors
        )

        rank_cache[node] = (
            avg_exec[node]
            + max_successor
        )

        return rank_cache[node]

    for node in graph.nodes:

        rank_u(node)

    return rank_cache


def schedule_heft(
    graph,
    workers,
    exec_cost,
    comm_cost,
    ranks
):
    """
    Schedule tasks using HEFT.
    """

    priority_order = sorted(
        ranks,
        key=ranks.get,
        reverse=True
    )

    worker_available = {
        worker: 0.0
        for worker in workers
    }

    task_result = {}

    for node in priority_order:

        task_type = graph.nodes[
            node
        ]["task_type"]

        best = None

        for worker in workers:

            ready_time = 0.0

            for parent in graph.predecessors(
                node
            ):

                parent_worker = (
                    task_result[parent]
                    ["worker"]
                )

                parent_finish = (
                    task_result[parent]
                    ["finish_ms"]
                )

                parent_task_type = (
                    graph.nodes[parent]
                    ["task_type"]
                )

                child_task_type = (
                    graph.nodes[node]
                    ["task_type"]
                )

                communication = (
                    get_actual_comm_cost(
                        parent_worker,
                        worker,
                        parent_task_type,
                        child_task_type
                    )
                )

                ready_time = max(
                    ready_time,
                    parent_finish
                    + communication
                )

            start_time = max(
                ready_time,
                worker_available[
                    worker
                ]
            )

            finish_time = (
                start_time
                + exec_cost[
                    task_type
                ][worker]
            )

            if (
                best is None
                or finish_time
                < best["finish_ms"]
            ):

                best = {
                    "worker":
                        worker,

                    "start_ms":
                        start_time,

                    "finish_ms":
                        finish_time
                }

        worker_available[
            best["worker"]
        ] = best["finish_ms"]

        task_result[node] = best

    makespan = max(

        result["finish_ms"]

        for result in task_result.values()
    )

    return (
        task_result,
        round(makespan, 2)
    )


if __name__ == "__main__":

    workers, exec_cost, comm_cost = (
        load_profiles()
    )

    graph = load_dag(
        "dags/test_dag.yaml"
    )

    ranks = compute_ranks(
        graph,
        workers,
        exec_cost,
        comm_cost
    )

    print("\nRanks\n")

    for node in sorted(
        ranks,
        key=ranks.get,
        reverse=True
    ):
        print(
            node,
            round(
                ranks[node],
                2
            )
        )

    schedule, makespan = (
        schedule_heft(
            graph,
            workers,
            exec_cost,
            comm_cost,
            ranks
        )
    )

    results_dir = Path(
    "results"
    )

    results_dir.mkdir(
        exist_ok=True
    )

    with open(
        results_dir / "mapping.json",
        "w"
    ) as f:

        json.dump(
            {
                "makespan_ms":
                    makespan,

                "schedule":
                    schedule
            },
            f,
            indent=4
        )

    print()

    print("Schedule")

    print()

    for node, info in (
        schedule.items()
    ):

        print(
            node,
            info
        )

    print()

    print(
        "Makespan:",
        makespan,
        "ms"
    )
