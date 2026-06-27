import argparse
import json
import os

parser = argparse.ArgumentParser()

parser.add_argument(
    "--input",
    required=True
)

parser.add_argument(
    "--output",
    required=True
)

args = parser.parse_args()

with open(args.input) as f:
    report = json.load(f)

os.makedirs(
    os.path.dirname(args.output),
    exist_ok=True
)

with open(
    args.output,
    "w"
) as f:

    f.write("Industrial Safety Report\n")
    f.write("========================\n\n")
    f.write(
        f"People Detected : {report['people_detected']}\n"
    )
    f.write(
        f"Status          : {report['status']}\n"
    )

print("Report generated")