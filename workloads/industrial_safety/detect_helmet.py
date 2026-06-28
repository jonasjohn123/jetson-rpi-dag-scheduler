import argparse
from pathlib import Path

import cv2

from workloads.industrial_safety.yolo_decoder import decode
import json

CLASS_NAMES = {
    0: "Hardhat",
    1: "NO-Hardhat"
}


MODEL = (
    Path(__file__).resolve().parents[2]
    / "models"
    / "helmet_detector.onnx"
)

def main():

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
        raise RuntimeError(
            "Cannot read image."
        )

    original_h, original_w = image.shape[:2]

    #
    # Load ONNX model
    #
    if not MODEL.exists():
        raise FileNotFoundError(
            f"Model not found: {MODEL}"
        )

    net = cv2.dnn.readNetFromONNX(
        str(MODEL)
    )
    #
    # Create blob
    #

    blob = cv2.dnn.blobFromImage(
        image,
        scalefactor=1 / 255.0,
        size=(640, 640),
        swapRB=True,
        crop=False
    )

    net.setInput(blob)

    outputs = net.forward()

    detections = decode(
        outputs,
        original_w,
        original_h,
        class_ids=[0,1]
    )

    for det in detections:
        det["class"] = CLASS_NAMES[det.pop("class_id")]

    Path(args.output).parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(args.output, "w") as f:

        json.dump(
            {
                "detections": detections
            },
            f,
            indent=4
        )

    print(f"Detected {len(detections)} helmets.")

    if detections:
        print(
            "Highest confidence:",
            max(d["confidence"] for d in detections)
        )


if __name__ == "__main__":

    main()