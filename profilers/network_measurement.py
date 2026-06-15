import json
import platform
import re
import subprocess


def measure_latency(ip, runs=10):
    """
    Measure worst-case latency.

    Returns:
        Maximum RTT observed across all ping packets
        from all runs.
    """

    count_flag = "-n" if platform.system() == "Windows" else "-c"

    worst_rtt = 0.0

    for run in range(runs):

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
    Measure worst-case bandwidth.

    Returns:
        Minimum average throughput observed
        across all iperf3 runs.
    """

    worst_bandwidth = float("inf")

    for run in range(runs):

        # TEMP DEBUG
        print(
            "[PROFILE] Starting bandwidth run {} to {}".format(
                run + 1,
                ip
            )
        )

        try:

            result = subprocess.check_output(
                [
                    "iperf3",
                    "-c",
                    ip,
                    "-J"
                ],
                universal_newlines=True,
                stderr=subprocess.STDOUT
            )

        except subprocess.CalledProcessError as e:

            # TEMP DEBUG
            print(
                "[PROFILE] FAILED bandwidth run {} to {}".format(
                    run + 1,
                    ip
                )
            )

            print(e.output)

            raise

        data = json.loads(result)

        bandwidth = (
            data["end"]["sum_received"]
            ["bits_per_second"]
            / 1_000_000
        )

        # TEMP DEBUG
        print(
            "[PROFILE] Finished bandwidth run {} to {} : {:.2f} Mbps".format(
                run + 1,
                ip,
                bandwidth
            )
        )

        worst_bandwidth = min(
            worst_bandwidth,
            bandwidth
        )

    return worst_bandwidth