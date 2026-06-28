from pathlib import Path

import cv2


def infer(
    image,
    model_path
):
    model_path = Path(model_path)

    if not model_path.exists():
        raise FileNotFoundError(
            f"Model not found: {model_path}"
        )

    net = cv2.dnn.readNetFromONNX(
        str(model_path)
    )

    blob = cv2.dnn.blobFromImage(
        image,
        scalefactor=1 / 255.0,
        size=(640, 640),
        swapRB=True,
        crop=False
    )

    net.setInput(blob)

    outputs = net.forward()

    return outputs