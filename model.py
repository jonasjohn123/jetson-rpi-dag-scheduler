from ultralytics import YOLO

model = YOLO("best.pt")

model.export(
    format="onnx",
    opset=11,
    simplify=False,
    dynamic=False,
    imgsz=640
)