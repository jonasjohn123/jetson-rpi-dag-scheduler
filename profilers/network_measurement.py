import json
import platform
import re
import subprocess


def measure_latency(ip):

    count_flag = "-n" if platform.system() == "Windows" else "-c"

    result = subprocess.check_output(
        ["ping", count_flag, "5", ip],
        text=True
    )

    if platform.system() == "Windows":
        match = re.search(r"Average = (\d+)ms", result)
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


def measure_bandwidth(ip):

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
        data["end"]["sum_received"]
        ["bits_per_second"]
        / 1_000_000
    )