import grpc
from concurrent import futures

import messages_pb2
import messages_pb2_grpc

import subprocess

from profilers.network_measurement import (
    measure_latency,
    measure_bandwidth
)


"""class WorkerService(
    messages_pb2_grpc.WorkerServiceServicer
):

    def Ping(self, request, context):

        return messages_pb2.PingResponse(
            worker_id="rpi01"
        )"""

class WorkerService(
    messages_pb2_grpc.WorkerServiceServicer
):

    def Ping(
        self,
        request,
        context
    ):

        return messages_pb2.PingResponse(
            worker_id="rpi01"
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

    server.wait_for_termination()


if __name__ == "__main__":
    serve()