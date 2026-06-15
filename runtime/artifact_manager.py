from pathlib import Path


ARTIFACT_ROOT = Path("artifacts")


def artifact_path(
    workflow_id,
    producer_task_id,
    artifact_name
):

    return (
        ARTIFACT_ROOT
        / workflow_id
        / producer_task_id
        / artifact_name
    )

def ensure_artifact_parent(
    workflow_id,
    producer_task_id,
    artifact_name
):

    artifact_path(
        workflow_id,
        producer_task_id,
        artifact_name
    ).parent.mkdir(
        parents=True,
        exist_ok=True
    )


def save_artifact(
    workflow_id,
    producer_task_id,
    artifact_name,
    data
):

    path = artifact_path(
        workflow_id,
        producer_task_id,
        artifact_name
    )

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(path, "wb") as f:

        f.write(data)

    return path


def load_artifact(
    workflow_id,
    producer_task_id,
    artifact_name
):

    path = artifact_path(
        workflow_id,
        producer_task_id,
        artifact_name
    )

    with open(path, "rb") as f:

        return f.read()


def artifact_exists(
    workflow_id,
    producer_task_id,
    artifact_name
):

    return artifact_path(
        workflow_id,
        producer_task_id,
        artifact_name
    ).exists()


def create_workflow_directory(
    workflow_id
):

    (
        ARTIFACT_ROOT
        / workflow_id
    ).mkdir(
        parents=True,
        exist_ok=True
    )


def save_artifact_stream(
    workflow_id,
    producer_task_id,
    artifact_name,
    chunks
):

    path = artifact_path(
        workflow_id,
        producer_task_id,
        artifact_name
    )

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(path, "wb") as f:

        for chunk in chunks:

            f.write(chunk)

    return path