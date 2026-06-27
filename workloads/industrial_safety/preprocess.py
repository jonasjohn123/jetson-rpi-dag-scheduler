import argparse
import cv2
import os

parser = argparse.ArgumentParser()

parser.add_argument("--input")
parser.add_argument("--output")

args = parser.parse_args()

img = cv2.imread(args.input)

img = cv2.resize(
    img,
    (640,640)
)

os.makedirs(
    os.path.dirname(args.output),
    exist_ok=True
)

cv2.imwrite(
    args.output,
    img
)

print("Preprocessing complete")