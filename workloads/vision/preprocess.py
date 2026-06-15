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

    os.makedirs(
        os.path.dirname(output_file),
        exist_ok=True
    )

    with open(
        output_file,
        "wb"
    ) as f:

        f.write(
            os.urandom(
                10 * 1024 * 1024
            )
        )

print(
    "Preprocess complete"
)