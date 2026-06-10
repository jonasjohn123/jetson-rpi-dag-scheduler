import grpc

import messages_pb2
import messages_pb2_grpc


channel = grpc.insecure_channel(
    "192.168.10.2:50051"
)

stub = messages_pb2_grpc.WorkerServiceStub(
    channel
)
"""
response = stub.Ping(
    messages_pb2.PingRequest()
)

print(response.worker_id)
"""

"""
response = stub.MeasureLink(
    messages_pb2.LinkRequest(
        target_ip="192.168.10.1"
    )
)

print(response.latency_ms)
print(response.bandwidth_mbps)
"""
response = stub.ProfileTask(
    messages_pb2.TaskProfileRequest(
        command="python workloads/synthetic/cpu_task.py",
        runs=5
    )
)

print("Mean:", response.mean_ms)
print("Min :", response.min_ms)
print("Max :", response.max_ms)