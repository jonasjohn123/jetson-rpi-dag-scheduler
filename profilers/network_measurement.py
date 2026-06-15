import json
import platform
import re
import subprocess


def measure_latency(ip, runs=10):
    """
    Returns worst-case RTT (maximum RTT observed)
    across multiple ping executions.
    """

    count_flag = "-n" if platform.system() == "Windows" else "-c"

    worst_rtt = 0.0

    for _ in range(runs):

        result = subprocess.check_output(
            ["ping", count_flag, "5", ip],
            text=True
        )

        if platform.system() == "Windows":

            matches = re.findall(
                r"time[=<]\s*(\d+)ms",
                result,
                re.IGNORECASE
            )

            rtts = [float(x) for x in matches]

        else:

            matches = re.findall(
                r"time=([\d.]+)\s*ms",
                result
            )

            rtts = [float(x) for x in matches]

        if not rtts:
            raise RuntimeError(
                f"Unable to parse ping output for {ip}"
            )

        run_max = max(rtts)
        worst_rtt = max(worst_rtt, run_max)

    return worst_rtt


def measure_bandwidth(ip, runs=10):
    """
    Returns worst-case bandwidth
    (minimum bandwidth observed)
    across multiple iperf3 executions.
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
            text=True
        )

        data = json.loads(result)

        bandwidth = (
            data["end"]["sum_received"]
            ["bits_per_second"]
            / 1_000_000
        )

        worst_bandwidth = min(
            worst_bandwidth,
            bandwidth
        )

    return worst_bandwidth