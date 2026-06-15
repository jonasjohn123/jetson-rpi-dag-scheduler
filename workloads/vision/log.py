import argparse
import time


parser = argparse.ArgumentParser()

parser.add_argument(
    "--input",
    action="append",
    default=[]
)

parser.add_argument(
    "--output",
    action="append",
    default=[]
)

args = parser.parse_args()

for input_file in args.input:

    with open(
        input_file,
        "rb"
    ) as f:

        f.read()

time.sleep(1)

print(
    "Logging complete"
)