import yaml


with open(
    "configs/transfer_profiles.yaml",
    "r"
) as f:

    TRANSFER_DATA = (
        yaml.safe_load(f)
    )


def get_transfer_time_ms(
    src_worker,
    dst_worker,
    size_mb
):

    if src_worker == dst_worker:

        return 0.0

    profiles = (

        TRANSFER_DATA["links"]
        [src_worker]
        [dst_worker]
    )

    sizes = sorted(
        profiles.keys()
    )

    if size_mb <= sizes[0]:

        return profiles[
            sizes[0]
        ]

    # Extrapolation
    if size_mb >= sizes[-1]:

        s1 = sizes[-2]
        s2 = sizes[-1]

        t1 = profiles[s1]
        t2 = profiles[s2]

        slope = (
            (t2 - t1)
            /
            (s2 - s1)
        )

        return (
            t2
            +
            slope
            *
            (size_mb - s2)
        )

    # Interpolation
    for i in range(
        len(sizes) - 1
    ):

        s1 = sizes[i]
        s2 = sizes[i + 1]

        if s1 <= size_mb <= s2:

            t1 = profiles[s1]
            t2 = profiles[s2]

            ratio = (
                (size_mb - s1)
                /
                (s2 - s1)
            )

            return (
                t1
                +
                ratio
                *
                (t2 - t1)
            )

    return 0.0