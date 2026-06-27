import argparse
import json
import os

parser = argparse.ArgumentParser()

parser.add_argument("--persons")
parser.add_argument("--helmets")
parser.add_argument("--output")

args = parser.parse_args()


with open(args.persons) as f:
    persons = json.load(f)["persons"]

with open(args.helmets) as f:
    helmets = json.load(f)["helmet"]


status = "SAFE"

if helmets < persons:
    status = "UNSAFE"


os.makedirs(
    os.path.dirname(args.output),
    exist_ok=True
)

with open(args.output, "w") as f:

    f.write(
        f"Persons : {persons}\n"
        f"Helmets: {helmets}\n"
        f"Status : {status}\n"
    )

print(status)