
import yaml
from pathlib import Path


TASKS_FILE = Path(
    "configs/tasks.yaml"
)

NETWORK_FILE = Path(
    "configs/network_profiles.yaml"
)


with open(TASKS_FILE, "r") as f:

    TASK_DATA = yaml.safe_load(f)


with open(NETWORK_FILE, "r") as f:

    NETWORK_DATA = yaml.safe_load(f)


def get_edge_data_size_mb(
    parent_task_type,
    child_task_type
):
    """
    Compute data transferred between two tasks.

    Data size is determined from:

        parent.outputs ∩ child.inputs

    Returns:
        float
            Size in MB.
    """

    parent = (
        TASK_DATA["tasks"]
        [parent_task_type]
    )

    child = (
        TASK_DATA["tasks"]
        [child_task_type]
    )

    outputs = set(
        parent.get(
            "outputs",
            []
        )
    )

    inputs = set(
        child.get(
            "inputs",
            []
        )
    )

    shared_files = (
        outputs & inputs
    )

    artifact_sizes = parent.get(
        "artifact_sizes_mb",
        {}
    )

    total_size = 0.0

    for filename in shared_files:

        total_size += (
            artifact_sizes.get(
                filename,
                0.0
            )
        )

    return total_size


def get_avg_comm_cost(
    parent_task_type,
    child_task_type
):
    """
    Average communication cost.

    Used during HEFT rank calculation.

    Formula:

        avg_latency
        +
        data_size / avg_bandwidth

    Returns:
        float
            Communication cost in ms.
    """

    data_size_mb = (
        get_edge_data_size_mb(
            parent_task_type,
            child_task_type
        )
    )

    latencies = []
    bandwidths = []

    links = (
        NETWORK_DATA["links"]
    )

    for src in links:

        for dst in links[src]:

            if src == dst:
                continue

            latencies.append(

                links[src][dst]
                ["latency_ms"]

                / 2.0
            )

            bandwidths.append(

                links[src][dst]
                ["bandwidth_mbps"]
            )

    if not bandwidths:

        return 0.0

    avg_latency_ms = (

        sum(latencies)
        / len(latencies)
    )

    avg_bandwidth_mbps = (

        sum(bandwidths)
        / len(bandwidths)
    )

    avg_bandwidth_MBps = (

        avg_bandwidth_mbps
        / 8.0
    )

    transfer_ms = (

        data_size_mb
        / avg_bandwidth_MBps

    ) * 1000.0

    return (

        avg_latency_ms
        + transfer_ms
    )


def get_actual_comm_cost(
    src_worker,
    dst_worker,
    parent_task_type,
    child_task_type
):
    """
    Actual communication cost.

    Used during processor selection.

    Formula:

        one_way_latency
        +
        data_size / bandwidth

    Returns:
        float
            Communication cost in ms.
    """

    if src_worker == dst_worker:

        return 0.0

    data_size_mb = (

        get_edge_data_size_mb(
            parent_task_type,
            child_task_type
        )
    )

    link = (

        NETWORK_DATA["links"]
        [src_worker]
        [dst_worker]
    )

    latency_ms = (

        link["latency_ms"]
        / 2.0
    )

    bandwidth_mbps = (

        link["bandwidth_mbps"]
    )

    bandwidth_MBps = (

        bandwidth_mbps
        / 8.0
    )

    transfer_ms = (

        data_size_mb
        / bandwidth_MBps

    ) * 1000.0

    return (

        latency_ms
        + transfer_ms
    )