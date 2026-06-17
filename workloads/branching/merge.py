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

total_size = 0

for input_file in args.input:

    with open(
        input_file,
        "rb"
    ) as f:

        total_size += len(
            f.read()
        )

time.sleep(2)

for output_file in args.output:

    directory = os.path.dirname(
        output_file
    )

    if directory:

        os.makedirs(
            directory,
            exist_ok=True
        )

    with open(
        output_file,
        "w"
    ) as f:

        f.write(
            f"Merged {total_size} bytes"
        )

print(
    "Merge complete"
)