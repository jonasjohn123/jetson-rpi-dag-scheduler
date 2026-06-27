import argparse
import shutil
import os

parser = argparse.ArgumentParser()

parser.add_argument("--source")
parser.add_argument("--output")

args = parser.parse_args()

os.makedirs(
    os.path.dirname(args.output),
    exist_ok=True
)

shutil.copy(
    args.source,
    args.output
)

print("Frame captured")