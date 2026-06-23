import grpc
import yaml
from pathlib import Path

import messages_pb2
import messages_pb2_grpc

TRANSFER_FILE = Path(
    "configs/transfer_profiles.yaml"
)

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

def save_transfer_profile(
    src,
    dst,
    size_mb,
    transfer_ms
):

    if TRANSFER_FILE.exists():

        with open(
            TRANSFER_FILE,
            "r"
        ) as f:

            data = yaml.safe_load(f)

            if data is None:

                data = {
                    "links": {}
                }

    else:

        data = {
            "links": {}
        }

    if src not in data["links"]:

        data["links"][src] = {}

    if dst not in data["links"][src]:

        data["links"][src][dst] = {}

    data["links"][src][dst][size_mb] = (
        transfer_ms
    )

    with open(
        TRANSFER_FILE,
        "w"
    ) as f:

        yaml.dump(
            data,
            f,
            sort_keys=False
        )

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

                transfer_ms = round(

                    response
                    .median_transfer_ms,

                    2
                )

                print(

                    size,

                    "MB :",

                    transfer_ms,

                    "ms"
                )

                save_transfer_profile(

                    source["id"],

                    target["id"],

                    size,

                    transfer_ms
                )
if __name__ == "__main__":

    main()