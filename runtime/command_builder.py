from pathlib import PathPosixPath


def artifact_path(
    workflow_id,
    producer_task_id,
    artifact_name
):

    return str(

        PathPosixPath(
            "artifacts",
            workflow_id,
            producer_task_id,
            artifact_name
        )

    )


def build_command(
    workflow_id,
    task_id,
    task_config,
    inputs
):

    command = (
        task_config["command"]
    )

    parts = [command]

    #
    # INPUTS
    #

    for artifact in inputs:

        parts.append(

            "--input"

        )

        parts.append(

            artifact_path(

                workflow_id,

                artifact.producer_task_id,

                artifact.artifact_name

            )
        )

    #
    # OUTPUTS
    #

    outputs = (
        task_config["outputs"]
    )

    for artifact in outputs:

        parts.append(

            "--output"

        )

        parts.append(

            artifact_path(

                workflow_id,

                task_id,

                artifact

            )
        )

    return " ".join(parts)