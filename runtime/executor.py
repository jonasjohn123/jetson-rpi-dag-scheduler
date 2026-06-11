import json


def load_schedule():

    with open(
        "results/mapping.json",
        "r"
    ) as f:

        return json.load(f)


def main():

    mapping = (
        load_schedule()
    )

    print()

    print(
        "Makespan:"
    )

    print(
        mapping[
            "makespan_ms"
        ]
    )

    print()

    print(
        "Task Mapping"
    )

    print()

    for node, info in (
        mapping[
            "schedule"
        ].items()
    ):

        print(
            node,
            "->",
            info[
                "worker"
            ]
        )


if __name__ == "__main__":

    main()