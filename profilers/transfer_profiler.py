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

    sizes = [
        1,
        5,
        10
    ]

    for source in workers["workers"]:

        for target in workers["workers"]:

            if (
                source["id"]
                ==
                target["id"]
            ):
                continue

            print()
            print(
                "=" * 50
            )

            print(
                source["id"],
                "->",
                target["id"]
            )

            print(
                "=" * 50
            )

            for size in sizes:

                response = (
                    profile_transfer(

                        worker_ip=
                        source["ip"],

                        target_ip=
                        target["ip"],

                        file_size_mb=
                        size,

                        runs=5
                    )
                )

                print(

                    size,

                    "MB :",

                    round(

                        response
                        .median_transfer_ms,

                        2
                    ),

                    "ms"
                )

if __name__ == "__main__":

    main()