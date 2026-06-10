import json
import platform
import re
import subprocess
from pathlib import Path

import yaml


WORKERS_FILE = Path("configs/workers.yaml")
NETWORK_PROFILE_FILE = Path("configs/network_profiles.yaml")


def load_workers():
    """
    Load worker definitions.

    Returns:
        list[dict]
    """

    with open(WORKERS_FILE, "r") as f:
        return yaml.safe_load(f)["workers"]


def get_local_worker(workers):
    """
    Find the worker entry corresponding to the machine
    running this profiler.

    Matching is done using hostname.

    Returns:
        dict
    """

    hostname = platform.node().lower()

    for worker in workers:

        if worker["host"].lower() == hostname:
            return worker

    raise RuntimeError(
        f"No worker entry found for hostname '{hostname}'."
    )


def get_latency(ip):
    """
    Measure average latency.

    Args:
        ip (str)

    Returns:
        float
            Average latency in ms.
    """

    count_flag = "-n" if platform.system() == "Windows" else "-c"

    result = subprocess.check_output(
        ["ping", count_flag, "5", ip],
        text=True
    )

    if platform.system() == "Windows":

        match = re.search(
            r"Average = (\d+)ms",
            result
        )

    else:

        match = re.search(
            r"=\s*[\d.]+/([\d.]+)/",
            result
        )

    if not match:
        raise RuntimeError(
            f"Unable to parse ping output for {ip}"
        )

    return float(match.group(1))


def get_bandwidth(ip):
    """
    Measure available bandwidth.

    Requires:
        iperf3 server running on destination node.

    Args:
        ip (str)

    Returns:
        float
            Mbps
    """

    result = subprocess.check_output(
        [
            "iperf3",
            "-c",
            ip,
            "-J"
        ],
        text=True
    )

    data = json.loads(result)

    return (
        data["end"]["sum_received"]["bits_per_second"]
        / 1_000_000
    )


def save_profiles(profile_data):
    """
    Save communication matrix.

    Args:
        profile_data (dict)
    """

    with open(NETWORK_PROFILE_FILE, "w") as f:

        yaml.dump(
            profile_data,
            f,
            default_flow_style=False,
            sort_keys=False
        )


def profile_network():
    """
    Build communication matrix.

    Assumptions:
    - Measurements are performed from the local node.
    - Links are symmetric.
    - Destination nodes are running iperf3 servers.

    Returns:
        dict
    """

    workers = load_workers()

    local_worker = get_local_worker(workers)

    local_id = local_worker["id"]

    profile_data = {
        "links": {}
    }

    profile_data["links"][local_id] = {}

    for worker in workers:

        worker_id = worker["id"]

        if worker_id == local_id:
            continue

        latency = get_latency(worker["ip"])

        bandwidth = get_bandwidth(worker["ip"])

        link_profile = {
            "bandwidth_mbps": round(
                bandwidth,
                2
            ),
            "latency_ms": round(
                latency,
                2
            )
        }

        profile_data["links"][local_id][worker_id] = (
            link_profile
        )

        profile_data["links"].setdefault(
            worker_id,
            {}
        )

        profile_data["links"][worker_id][local_id] = (
            link_profile.copy()
        )

    save_profiles(profile_data)

    return profile_data


if __name__ == "__main__":
    profile_network()