import messages_pb2

from runtime.command_builder import (
    build_command
)


def build_worker_lookup(workers):

    lookup = {}

    for worker in workers["workers"]:

        lookup[
            worker["id"]
        ] = worker

    return lookup


def build_worker_queues(
    workflow_id,
    graph,
    mapping,
    tasks,
    workers
):

    worker_lookup = (
        build_worker_lookup(
            workers
        )
    )

    queues = {}

    schedule = (
        mapping["schedule"]
    )

    for task_id in schedule:

        schedule_info = (
            schedule[task_id]
        )

        worker_id = (
            schedule_info["worker"]
        )

        task_type = (
            graph.nodes[task_id]
            ["task_type"]
        )

        task_config = (
            tasks[task_type]
        )

        start_ms = (
            schedule_info["start_ms"]
        )

        finish_ms = (
            schedule_info["finish_ms"]
        )

        #
        # INPUTS
        #

        inputs = []

        predecessors = list(
            graph.predecessors(
                task_id
            )
        )

        for pred in predecessors:

            pred_task_type = (
                graph.nodes[pred]
                ["task_type"]
            )

            pred_outputs = (
                tasks[
                    pred_task_type
                ]["outputs"]
            )

            for artifact in pred_outputs:

                inputs.append(

                    messages_pb2.ArtifactInput(

                        producer_task_id=pred,

                        artifact_name=artifact
                    )
                )

        #
        # OUTPUTS
        #

        outputs = list(

            task_config[
                "outputs"
            ]
        )

        #
        # COMMAND
        #

        command = build_command(

            workflow_id=workflow_id,

            task_id=task_id,

            task_config=task_config,

            inputs=inputs
        )

        #
        # DESTINATIONS
        #

        destinations = []

        seen = set()

        successors = list(
            graph.successors(
                task_id
            )
        )

        for succ in successors:

            succ_worker = (

                schedule[
                    succ
                ]["worker"]
            )

            if (
                succ_worker
                ==
                worker_id
            ):
                continue

            succ_ip = (

                worker_lookup[
                    succ_worker
                ]["ip"]
            )

            for artifact in outputs:

                key = (
                    succ_worker,
                    artifact
                )

                if key in seen:
                    continue

                seen.add(key)

                destinations.append(

                    messages_pb2.ArtifactDestination(

                        worker_id=succ_worker,

                        worker_ip=succ_ip,

                        artifact_name=artifact
                    )
                )

        #
        # BUILD TASK
        #

        worker_task = (

            messages_pb2.WorkerTask(

                task_id=task_id,

                task_type=task_type,

                command=command,

                start_ms=start_ms,

                finish_ms=finish_ms,

                inputs=inputs,

                outputs=outputs,

                destinations=destinations
            )
        )

        if worker_id not in queues:

            queues[
                worker_id
            ] = []

        queues[
            worker_id
        ].append(
            worker_task
        )

    #
    # SORT TASKS
    #

    for worker_id in queues:

        queues[
            worker_id
        ].sort(

            key=lambda task:
            task.start_ms
        )

    return queues