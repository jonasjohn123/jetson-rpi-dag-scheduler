import grpc

import messages_pb2
import messages_pb2_grpc


channel = grpc.insecure_channel(
    "192.168.10.2:50051"
)

stub = messages_pb2_grpc.WorkerServiceStub(
    channel
)

response = stub.Ping(
    messages_pb2.PingRequest()
)

print(response.worker_id)