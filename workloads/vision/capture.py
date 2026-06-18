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

time.sleep(2)

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
                5 * 1024 * 1024
            )
        )

print(
    "Capture complete"
)