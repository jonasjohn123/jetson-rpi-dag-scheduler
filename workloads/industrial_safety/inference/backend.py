from pathlib import Path


def is_jetson():

    return Path(
        "/etc/nv_tegra_release"
    ).exists()


if is_jetson():

    from .tensorrt_backend import infer

else:

    from .opencv_backend import infer