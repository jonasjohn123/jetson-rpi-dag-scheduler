import argparse
import os


parser = argparse.ArgumentParser()

parser.add_argument(
    "--output",
    action="append",
    default=[]
)

args = parser.parse_args()

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
        "wb"
    ) as f:

        f.write(
            os.urandom(
                1024 * 1024
            )
        )

print(
    "Generate complete"
)