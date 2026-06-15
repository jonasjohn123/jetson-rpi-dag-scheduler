import grpc

import messages_pb2
import messages_pb2_grpc

from runtime.artifact_manager import (
    artifact_path
)


CHUNK_SIZE = 1024 * 1024


def generate_chunks(
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

        while True:

            chunk = f.read(
                CHUNK_SIZE
            )

            if not chunk:
                break

            yield (
                messages_pb2.ArtifactChunk(
                    workflow_id=workflow_id,
                    producer_task_id=producer_task_id,
                    artifact_name=artifact_name,
                    data=chunk
                )
            )


def send_artifact(
    workflow_id,
    producer_task_id,
    artifact_name,
    worker_ip
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
        stub.TransferArtifact(
            generate_chunks(
                workflow_id,
                producer_task_id,
                artifact_name
            )
        )
    )

    return response