import argparse
import os
import cv2

parser = argparse.ArgumentParser()

parser.add_argument(
    "--input",
    required=True
)

parser.add_argument(
    "--output",
    required=True
)

args = parser.parse_args()

image = cv2.imread(args.input)

if image is None:
    raise FileNotFoundError(args.input)

image = cv2.resize(
    image,
    (640, 640)
)

os.makedirs(
    os.path.dirname(args.output),
    exist_ok=True
)

cv2.imwrite(
    args.output,
    image
)

print("Resize complete")