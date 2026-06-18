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

    with open(
        input_file,
        "rb"
    ) as f:

        f.read()

time.sleep(3)

for output_file in args.output:

    directory = os.path.dirname(
        output_file
    )

    if directory:

        if not os.path.exists(
            directory
        ):

            os.makedirs(
                directory
            )

    with open(
        output_file,
        "wb"
    ) as f:

        f.write(
            os.urandom(
                3 * 1024 * 1024
            )
        )

print(
    "Branch B complete"
)