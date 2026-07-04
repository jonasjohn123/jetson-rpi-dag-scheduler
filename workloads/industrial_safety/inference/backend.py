import platform


if platform.machine() == "aarch64":

    from .tensorrt_backend import infer

else:

    from .opencv_backend import infer