import json

import grpc
from concurrent import futures

import subprocess
import time
import os
from statistics import median

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

from runtime.artifact_transfer import (
    send_artifact
)

import shutil
from pathlib import Path


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
    
    def ClearWorkflow(
        self,
        request,
        context
    ):

        path = (
            Path("artifacts")
            /
            request.workflow_id
        )

        if path.exists():

            shutil.rmtree(
                path
            )

        log_file = (
            Path("results")
            /
            request.workflow_id
            /
            "execution_log.json"
        )

        log_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            log_file,
            "w"
        ) as f:

            json.dump(
                [],
                f,
                indent=4
            )

        return (
            messages_pb2
            .ClearWorkflowResponse(

                success=True,

                message=
                "Artifacts cleared"
            )
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
    
    def ProfileTransfer(
        self,
        request,
        context
    ):

        workflow_id = "transfer_profile"

        task_id = "profiler"

        artifact_name = "test.bin"

        file_size_mb = request.file_size_mb

        runs = request.runs

        target_ip = request.target_ip

        measurements = []

        path = artifact_path(
            workflow_id,
            task_id,
            artifact_name
        )

        directory = os.path.dirname(
            path
        )

        if not os.path.exists(
            directory
        ):
            os.makedirs(
                directory
            )

        with open(
            path,
            "wb"
        ) as f:

            f.write(
                os.urandom(
                    file_size_mb
                    *
                    1024
                    *
                    1024
                )
            )

        for _ in range(runs):

            start = time.time()

            response = send_artifact(

                workflow_id=
                workflow_id,

                producer_task_id=
                task_id,

                artifact_name=
                artifact_name,

                worker_ip=
                target_ip
            )

            send_ms = (
                time.time() - start
            ) * 1000

            print(
                "[PROFILE SEND]",
                round(send_ms, 2),
                "ms"
            )

            if not response.success:

                return (
                    messages_pb2
                    .TransferProfileResponse(
                        success=False
                    )
                )

            transfer_ms = (

                time.time()
                -
                start

            ) * 1000

            send_ms = (
                time.time() - start
            ) * 1000

            print(
                "[PROFILE SEND]",
                round(send_ms, 2),
                "ms"
            )

            measurements.append(
                transfer_ms
            )

        return (
            messages_pb2
            .TransferProfileResponse(

                median_transfer_ms=
                median(
                    measurements
                ),

                success=True
            )
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
            request.start_timestamp_ms,
            request.worker_offset_ms
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

        network_time = 0
        write_time = 0

        try:

            for request in request_iterator:

                network_end = time.time()

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

                write_start = time.time()

                file_handle.write(
                    request.data
                )

                write_time += (
                    time.time()
                    - write_start
                )

                network_time += (
                    network_end
                    - previous_chunk_time
                ) if 'previous_chunk_time' in locals() else 0

                previous_chunk_time = time.time()

        finally:

            if file_handle:

                file_handle.close()

        print(
            "[NETWORK]",
            round(
                network_time * 1000,
                2
            ),
            "ms"
        )

        print(
            "[WRITE]",
            round(
                write_time * 1000,
                2
            ),
            "ms"
        )

        return (
            messages_pb2
            .ArtifactTransferResponse(
                success=True,
                message="Artifact received"
            )
        )
    
    def GetExecutionLog(
        self,
        request,
        context
    ):
            
        log_file = (
            Path("results")
            /
            request.workflow_id
            /
            "execution_log.json"
        )

        if not log_file.exists():

            return (
                messages_pb2
                .ExecutionLogResponse(
                    json_data="[]"
                )
            )

        with open(
            log_file,
            "r"
        ) as f:

            data = f.read()

        return (
            messages_pb2
            .ExecutionLogResponse(
                json_data=data
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