import grpc

import messages_pb2
import messages_pb2_grpc


channel = grpc.insecure_channel(
    "192.168.10.2:50051"
)

stub = (
    messages_pb2_grpc
    .WorkerServiceStub(
        channel
    )
)

response = (
    stub.ProfileTransfer(

        messages_pb2
        .TransferProfileRequest(

            target_ip=
            "192.168.10.1",

            file_size_mb=1,

            runs=5
        )
    )
)

print(response)