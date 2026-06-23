import grpc
import yaml

import messages_pb2
import messages_pb2_grpc


def load_workers():

    with open(
        "configs/workers.yaml",
        "r"
    ) as f:

        return yaml.safe_load(f)


def profile_transfer(
    worker_ip,
    target_ip,
    file_size_mb=1,
    runs=5
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
        stub.ProfileTransfer(

            messages_pb2
            .TransferProfileRequest(

                target_ip=
                target_ip,

                file_size_mb=
                file_size_mb,

                runs=
                runs
            )
        )
    )

    return response


def main():

    workers = load_workers()

    laptop_ip = None
    rpi_ip = None

    for worker in workers["workers"]:

        if worker["id"] == "laptop01":

            laptop_ip = worker["ip"]

        elif worker["id"] == "rpi01":

            rpi_ip = worker["ip"]

    response = profile_transfer(

        worker_ip=laptop_ip,

        target_ip=rpi_ip,

        file_size_mb=1,

        runs=5
    )

    print()

    print(
        "Median transfer:",
        response.median_transfer_ms,
        "ms"
    )

    print(
        "Success:",
        response.success
    )


if __name__ == "__main__":

    main()