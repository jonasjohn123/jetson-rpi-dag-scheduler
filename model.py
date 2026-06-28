from ultralytics import YOLO

model = YOLO("helmet.pt")
print(model.names)