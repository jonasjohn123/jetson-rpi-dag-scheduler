import argparse
import time
import json
import os

parser = argparse.ArgumentParser()

parser.add_argument("--input")
parser.add_argument("--output")

args = parser.parse_args()

time.sleep(1)

result = {
    "persons":2
}

os.makedirs(
    os.path.dirname(args.output),
    exist_ok=True
)

with open(args.output,"w") as f:
    json.dump(result,f)

print("Person detection complete")