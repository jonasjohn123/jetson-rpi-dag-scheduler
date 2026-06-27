import argparse
import os
import json

import cv2

from ultralytics import YOLO

parser = argparse.ArgumentParser()

parser.add_argument(
    "--input",
    required=True
)

parser.add_argument(
    "--image_output",
    required=True
)

parser.add_argument(
    "--json_output",
    required=True
)

args = parser.parse_args()

model = YOLO("yolov8n.pt")

results = model(args.input)

result = results[0]

image = result.plot()

os.makedirs(
    os.path.dirname(args.image_output),
    exist_ok=True
)

cv2.imwrite(
    args.image_output,
    image
)

detections = []

for box in result.boxes:

    cls = int(box.cls[0])

    conf = float(box.conf[0])

    detections.append({

        "class": result.names[cls],

        "confidence": conf

    })

with open(
    args.json_output,
    "w"
) as f:

    json.dump(
        detections,
        f,
        indent=4
    )

print("Detection complete")