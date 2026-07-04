import cv2
import numpy as np

import tensorrt as trt

import pycuda.driver as cuda

import atexit


# -------------------------
# CUDA initialization
# -------------------------

cuda.init()

DEVICE = cuda.Device(0)

CTX = DEVICE.make_context()


# -------------------------
# TensorRT
# -------------------------

TRT_LOGGER = trt.Logger(
    trt.Logger.WARNING
)


CACHE = {}


def load_engine(engine_path):

    engine_path = str(engine_path)


    # reuse already loaded engines
    if engine_path in CACHE:

        return CACHE[engine_path]


    with open(engine_path, "rb") as f:

        runtime = trt.Runtime(
            TRT_LOGGER
        )

        engine = runtime.deserialize_cuda_engine(
            f.read()
        )


    context = engine.create_execution_context()


    CACHE[engine_path] = (
        engine,
        context
    )


    return CACHE[engine_path]



def infer(
    image,
    model_path
):

    # ONNX path -> TensorRT engine path

    engine_path = str(
        model_path
    ).replace(
        ".onnx",
        ".engine"
    )


    engine, context = load_engine(
        engine_path
    )


    # -------------------------
    # Preprocess
    # -------------------------

    blob = cv2.dnn.blobFromImage(

        image,

        scalefactor=1 / 255.0,

        size=(640, 640),

        swapRB=True,

        crop=False
    )


    input_data = np.ascontiguousarray(

        blob.astype(
            np.float32
        )

    )


    # YOLO output buffer

    output = np.empty(

        (1, 84, 8400),

        dtype=np.float32

    )


    # -------------------------
    # Allocate GPU memory
    # -------------------------

    d_input = cuda.mem_alloc(

        input_data.nbytes

    )


    d_output = cuda.mem_alloc(

        output.nbytes

    )


    bindings = [

        int(d_input),

        int(d_output)

    ]


    # -------------------------
    # Execute TensorRT
    # -------------------------

    CTX.push()


    try:

        cuda.memcpy_htod(

            d_input,

            input_data

        )


        context.execute_v2(

            bindings=bindings

        )


        cuda.memcpy_dtoh(

            output,

            d_output

        )


    finally:

        CTX.pop()


        # free GPU buffers

        d_input.free()

        d_output.free()


    return output



# -------------------------
# Shutdown cleanup
# -------------------------

def cleanup():

    CACHE.clear()

    CTX.detach()



atexit.register(
    cleanup
)