import argparse
import os


parser = argparse.ArgumentParser()

parser.add_argument(
    "--output",
    required=True
)

args = parser.parse_args()

os.makedirs(
    os.path.dirname(
        args.output
    ),
    exist_ok=True
)

with open(
    args.output,
    "wb"
) as f:

    f.write(
        os.urandom(
            5 * 1024 * 1024
        )
    )

print(
    "Created:",
    args.output
)