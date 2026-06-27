from pathlib import PurePosixPath


def artifact_path(
    workflow_id,
    producer_task_id,
    artifact_name
):
    return str(
        PurePosixPath(
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

    command = task_config["command"]

    #
    # Replace input placeholders
    #
    command = command.replace(
        "{workflow}",
        workflow_id
    )

    for artifact in inputs:

        placeholder = (
            "{input:"
            + artifact.artifact_name
            + "}"
        )

        command = command.replace(

            placeholder,

            artifact_path(

                workflow_id,

                artifact.producer_task_id,

                artifact.artifact_name

            )

        )

    #
    # Replace output placeholders
    #

    for artifact in task_config["outputs"]:

        placeholder = (
            "{output:"
            + artifact
            + "}"
        )

        command = command.replace(

            placeholder,

            artifact_path(

                workflow_id,

                task_id,

                artifact

            )

        )

    return command