import onnx
from onnxsim import simplify


model = onnx.load(
    "models/helmet_detector.onnx"
)

# Make it compatible with old OpenCV
model.ir_version = 6

for node in model.graph.node:
    node.doc_string = ""

model, check = simplify(
    model
)

print("Simplify:", check)

onnx.save(
    model,
    "models/helmet_detector_fixed.onnx"
)