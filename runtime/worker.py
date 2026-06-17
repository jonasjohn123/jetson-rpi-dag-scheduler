import grpc
from concurrent import futures

import subprocess
import time

import messages_pb2
import messages_pb2_grpc

from profilers.network_measurement import (
    measure_latency,
    measure_bandwidth
)

from runtime.task_queue import TaskQueue

from runtime.artifact_manager import (
    artifact_path
)

from runtime.worker_config import (
    get_worker_id
)


task_queue = TaskQueue()

WORKER_ID = get_worker_id()

class WorkerService(
    messages_pb2_grpc.WorkerServiceServicer
):

    def Ping(
        self,
        request,
        context
    ):

        return messages_pb2.PingResponse(
            worker_id=WORKER_ID
        )
    
    def GetTime(
        self,
        request,
        context
    ):

        return messages_pb2.TimeResponse(
            timestamp_ms=int(
                time.time() * 1000
            )
        )

    def MeasureLink(
        self,
        request,
        context
    ):

        latency = measure_latency(
            request.target_ip
        )

        bandwidth = measure_bandwidth(
            request.target_ip
        )

        return messages_pb2.LinkResponse(
            latency_ms=latency,
            bandwidth_mbps=bandwidth
        )

    def ProfileTask(
        self,
        request,
        context
    ):

        samples = []

        for _ in range(request.runs):

            start = time.perf_counter()

            subprocess.run(
                request.command,
                shell=True,
                check=True
            )

            elapsed_ms = (
                time.perf_counter() - start
            ) * 1000

            samples.append(elapsed_ms)

        return messages_pb2.TaskProfileResponse(
            mean_ms=sum(samples) / len(samples),
            min_ms=min(samples),
            max_ms=max(samples)
        )

    def ExecuteTask(
        self,
        request,
        context
    ):

        try:

            result = subprocess.run(
                request.command,
                shell=True,
                capture_output=True,
                universal_newlines=True,
                check=True
            )

            return messages_pb2.ExecuteTaskResponse(
                success=True,
                output=result.stdout
            )

        except subprocess.CalledProcessError as e:

            return messages_pb2.ExecuteTaskResponse(
                success=False,
                output=e.stderr
            )

    def UploadSchedule(
        self,
        request,
        context
    ):

        task_queue.load_schedule(
            request.workflow_id,
            request.tasks
        )

        return messages_pb2.UploadScheduleResponse(
            success=True,
            message="Schedule uploaded"
        )

    def StartWorkflow(
        self,
        request,
        context
    ):

        task_queue.start(
            request.start_timestamp_ms
        )

        return messages_pb2.StartWorkflowResponse(
            success=True,
            message="Workflow started"
        )

    def TransferArtifact(
    self,
    request_iterator,
    context
    ):

        workflow_id = None
        producer_task_id = None
        artifact_name = None

        first_chunk = True

        file_handle = None

        try:

            for request in request_iterator:

                if first_chunk:

                    workflow_id = (
                        request.workflow_id
                    )

                    producer_task_id = (
                        request.producer_task_id
                    )

                    artifact_name = (
                        request.artifact_name
                    )

                    path = artifact_path(
                        workflow_id,
                        producer_task_id,
                        artifact_name
                    )

                    path.parent.mkdir(
                        parents=True,
                        exist_ok=True
                    )

                    file_handle = open(
                        path,
                        "wb"
                    )

                    first_chunk = False

                file_handle.write(
                    request.data
                )

        finally:

            if file_handle:

                file_handle.close()

        return (
            messages_pb2
            .ArtifactTransferResponse(
                success=True,
                message="Artifact received"
            )
        )
subprocess.Popen(
    [
        "iperf3",
        "-s"
    ],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)


def serve():

    server = grpc.server(
        futures.ThreadPoolExecutor(
            max_workers=10
        )
    )

    messages_pb2_grpc.add_WorkerServiceServicer_to_server(
        WorkerService(),
        server
    )

    server.add_insecure_port(
        "[::]:50051"
    )

    server.start()

    print(
        "Worker server running on port 50051"
    )

    server.wait_for_termination()


if __name__ == "__main__":
    print(
        "[CLOCK]",
        int(time.time() * 1000)
    )

    serve()