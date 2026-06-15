import json
import platform
import re
import subprocess


def measure_latency(ip, runs=10):
    """
    Measure worst-case network latency.

    Method:
        - Execute ping multiple times.
        - Each ping sends 5 packets.
        - Extract RTT of every packet.
        - Return the largest RTT observed across all packets
          from all runs.

    Args:
        ip (str): Destination IP address.
        runs (int): Number of ping executions.

    Returns:
        float: Worst RTT in milliseconds.
    """

    count_flag = "-n" if platform.system() == "Windows" else "-c"

    worst_rtt = 0.0

    for _ in range(runs):

        result = subprocess.check_output(
            ["ping", count_flag, "5", ip],
            universal_newlines=True
        )

        if platform.system() == "Windows":

            matches = re.findall(
                r"time[=<]\s*(\d+)ms",
                result,
                re.IGNORECASE
            )

        else:

            matches = re.findall(
                r"time=([\d.]+)\s*ms",
                result
            )

        rtts = [float(x) for x in matches]

        if not rtts:
            raise RuntimeError(
                "Unable to parse ping output for {}".format(ip)
            )

        worst_rtt = max(
            worst_rtt,
            max(rtts)
        )

    return worst_rtt


def measure_bandwidth(ip, runs=10):
    """
    Measure worst-case network bandwidth.

    Method:
        - Execute iperf3 multiple times.
        - Each iperf3 run reports average throughput.
        - Return the minimum throughput observed.

    Args:
        ip (str): Destination IP address.
        runs (int): Number of iperf3 executions.

    Returns:
        float: Worst bandwidth in Mbps.
    """

    worst_bandwidth = float("inf")

    for _ in range(runs):

        result = subprocess.check_output(
            [
                "iperf3",
                "-c",
                ip,
                "-J"
            ],
            universal_newlines=True
        )

        data = json.loads(result)

        bandwidth = (
            data["end"]["sum_received"]["bits_per_second"]
            / 1_000_000
        )

        worst_bandwidth = min(
            worst_bandwidth,
            bandwidth
        )

    return worst_bandwidth