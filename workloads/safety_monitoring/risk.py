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
    detections = json.load(f)

people = sum(
    1
    for d in detections
    if d["class"] == "person"
)

report = {

    "people_detected": people,

    "status":
        "ALERT"
        if people > 0
        else "SAFE"
}

os.makedirs(
    os.path.dirname(args.output),
    exist_ok=True
)

with open(
    args.output,
    "w"
) as f:

    json.dump(
        report,
        f,
        indent=4
    )

print("Risk assessment complete")