import grpc

import messages_pb2
import messages_pb2_grpc


channel = grpc.insecure_channel(
    "192.168.10.2:50051"
)

stub = (
    messages_pb2_grpc
    .WorkerServiceStub(channel)
)

response = (
    stub.ExecuteTask(

        messages_pb2
        .ExecuteTaskRequest(
            command="python --version"
        )
    )
)

print(
    response.success
)

print(
    response.output
)