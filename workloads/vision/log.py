import argparse
import os
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

    if os.path.exists(
        input_file
    ):

        with open(
            input_file,
            "rb"
        ) as f:

            f.read()

time.sleep(1)

print(
    "Logging complete"
)