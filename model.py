from ultralytics import YOLO

model = YOLO("yolov5nu.pt")

model.export(
    format="onnx",
    opset=11,
    simplify=False,
    imgsz=640
)