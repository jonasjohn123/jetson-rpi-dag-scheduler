import cv2
import numpy as np

PERSON_CONFIDENCE_THRESHOLD = 0.50
PERSON_NMS_THRESHOLD = 0.45

def decode(
    outputs,
    image_width,
    image_height,
    class_ids,
    confidence_threshold=PERSON_CONFIDENCE_THRESHOLD,
    nms_threshold=PERSON_NMS_THRESHOLD
):
    """
    Decode YOLOv8 ONNX output.

    Parameters
    ----------
    outputs : ndarray
        Shape (1,84,8400)

    class_ids : list
        COCO class indices to keep.

    Returns
    -------
    detections : list
    """

    predictions = outputs[0].T

    boxes = []
    scores = []

    x_factor = image_width / 640
    y_factor = image_height / 640

    for row in predictions:

        cx, cy, w, h = row[:4]

        class_scores = row[4:]

        best_class = None
        best_score = 0.0

        for cls in class_ids:

            score = float(class_scores[cls])

            if score > best_score:

                best_score = score
                best_class = cls

        if best_score < confidence_threshold:
            continue

        confidence = best_score

        x1 = (cx - w / 2) * x_factor
        y1 = (cy - h / 2) * y_factor

        width = w * x_factor
        height = h * y_factor

        boxes.append(
            [
                int(x1),
                int(y1),
                int(width),
                int(height)
            ]
        )

        scores.append(confidence)

    indices = cv2.dnn.NMSBoxes(
        boxes,
        scores,
        confidence_threshold,
        nms_threshold
    )

    detections = []

    if len(indices) == 0:
        return detections

    for idx in indices.flatten():

        x, y, w, h = boxes[idx]

        detections.append(
            {
                "bbox": [
                    x,
                    y,
                    x + w,
                    y + h
                ],
                "class_id": best_class,
                "confidence": round(
                    scores[idx],
                    4
                )
            }
        )

    return detections