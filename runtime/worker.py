import grpc
from concurrent import futures

import messages_pb2
import messages_pb2_grpc


class WorkerService(
    messages_pb2_grpc.WorkerServiceServicer
):

    def Ping(self, request, context):

        return messages_pb2.PingResponse(
            worker_id="rpi01"
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