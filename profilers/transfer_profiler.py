import time
import yaml
import tempfile
import os

from statistics import median

from runtime.artifact_transfer import (
    send_artifact
)

from runtime.artifact_manager import (
    artifact_path
)


WORKERS_FILE = "configs/workers.yaml"

NETWORK_FILE = (
    "configs/network_profiles.yaml"
)

WORKFLOW_ID = (
    "transfer_profile"
)

TASK_ID = (
    "profiler"
)

FILE_SIZE_MB = 1

RUNS = 20

def create_test_file():

    path = artifact_path(

        WORKFLOW_ID,

        TASK_ID,

        "test.bin"
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
                FILE_SIZE_MB
                *
                1024
                *
                1024
            )
        )

def load_workers():

    with open(
        WORKERS_FILE,
        "r"
    ) as f:

        return yaml.safe_load(f)


def load_network():

    with open(
        NETWORK_FILE,
        "r"
    ) as f:

        return yaml.safe_load(f)
    
def profile_link(
    src_worker,
    dst_worker,
    dst_ip,
    bandwidth_mbps
):

    measurements = []

    theoretical_ms = (

        FILE_SIZE_MB
        * 8
        / bandwidth_mbps

    ) * 1000

    for _ in range(RUNS):

        start = time.time()

        send_artifact(

            workflow_id=
            WORKFLOW_ID,

            producer_task_id=
            TASK_ID,

            artifact_name=
            "test.bin",

            worker_ip=
            dst_ip
        )

        actual_ms = (

            time.time()
            - start

        ) * 1000

        overhead_ms = (

            actual_ms
            -
            theoretical_ms
        )

        measurements.append(
            overhead_ms
        )

    median_overhead = (
        median(measurements)
    )

    print(

        src_worker,
        "->",
        dst_worker,

        f"{median_overhead:.2f} ms"
    )

    return median_overhead


def main():

    create_test_file()

    workers = load_workers()

    network = load_network()

    links = network["links"]

    for src in links:

        for dst in links[src]:

            bandwidth = (

                links[src][dst]
                ["bandwidth_mbps"]
            )

            dst_ip = None

            for worker in (
                workers["workers"]
            ):

                if (
                    worker["id"]
                    ==
                    dst
                ):

                    dst_ip = (
                        worker["ip"]
                    )

                    break

            overhead = (
                profile_link(
                    src,
                    dst,
                    dst_ip,
                    bandwidth
                )
            )

            links[src][dst][
                "overhead_ms"
            ] = round(
                overhead,
                2
            )

    with open(
        NETWORK_FILE,
        "w"
    ) as f:

        yaml.safe_dump(
            network,
            f,
            sort_keys=False
        )

    print()
    print(
        "Transfer profiling complete."
    )


if __name__ == "__main__":

    main()
