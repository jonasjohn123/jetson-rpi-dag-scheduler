import json
from pathlib import Path

import matplotlib.pyplot as plt


WORKFLOW_ID = "workflow_001"

RESULTS_DIR = (
    Path("results")
    / WORKFLOW_ID
)

SCHEDULE_FILE = (
    RESULTS_DIR
    / "schedule.json"
)

EXECUTION_FILE = (
    RESULTS_DIR
    / "execution_log.json"
)


def load_schedule():

    with open(
        SCHEDULE_FILE,
        "r"
    ) as f:

        return json.load(f)


def load_execution():

    with open(
        EXECUTION_FILE,
        "r"
    ) as f:

        return json.load(f)


def plot_schedule(schedule):

    fig, ax = plt.subplots(
        figsize=(12, 5)
    )

    workers = {}

    y = 0

    for task_id, task in (
        schedule["schedule"].items()
    ):

        worker = task["worker"]

        if worker not in workers:

            workers[worker] = y
            y += 1

    for task_id, task in (
        schedule["schedule"].items()
    ):

        worker = task["worker"]

        start = task["start_ms"]

        duration = (
            task["finish_ms"]
            -
            task["start_ms"]
        )

        ax.barh(
            workers[worker],
            duration,
            left=start,
            height=0.4
        )

        ax.text(
            start + duration / 2,
            workers[worker],
            task_id,
            ha="center",
            va="center"
        )

    ax.set_yticks(
        list(workers.values())
    )

    ax.set_yticklabels(
        list(workers.keys())
    )

    ax.set_xlabel(
        "Time (ms)"
    )

    ax.set_title(
        "Planned HEFT Schedule"
    )

    plt.tight_layout()

    plt.show()


def plot_execution(execution):

    fig, ax = plt.subplots(
        figsize=(12, 5)
    )

    base_time = min(

        task["actual_start"]

        for task in execution
    )

    workers = {
        "laptop01": 0,
        "jetson01": 1,
        "rpi01": 2
    }

    mapping = {}

    with open(
        SCHEDULE_FILE,
        "r"
    ) as f:

        schedule = json.load(f)

    for task_id, task in (
        schedule["schedule"].items()
    ):

        mapping[task_id] = (
            task["worker"]
        )

    for task in execution:

        task_id = (
            task["task_id"]
        )

        worker = mapping[
            task_id
        ]

        y = workers[
            worker
        ]

        start = (
            task["actual_start"]
            -
            base_time
        )

        duration = (
            task["actual_finish"]
            -
            task["actual_start"]
        )

        idle = task[
            "idle_ms"
        ]

        ax.barh(
            y,
            duration,
            left=start,
            height=0.4
        )

        ax.barh(
            y,
            idle,
            left=start + duration,
            height=0.4,
            alpha=0.3
        )

        ax.text(
            start + duration / 2,
            y,
            task_id,
            ha="center",
            va="center"
        )

    ax.set_yticks(
        [0, 1, 2]
    )

    ax.set_yticklabels(
        [
            "laptop01",
            "jetson01",
            "rpi01"
        ]
    )

    ax.set_xlabel(
        "Time (ms)"
    )

    ax.set_title(
        "Actual Execution + Idle Time"
    )

    plt.tight_layout()

    plt.show()


def print_stats(execution):

    total_idle = sum(
        task["idle_ms"]
        for task in execution
    )

    makespan_actual = (

        max(
            task["actual_finish"]
            for task in execution
        )

        -

        min(
            task["actual_start"]
            for task in execution
        )
    )

    print()
    print(
        "Actual Makespan:",
        makespan_actual,
        "ms"
    )

    print(
        "Total Idle:",
        total_idle,
        "ms"
    )


def main():

    schedule = (
        load_schedule()
    )

    execution = (
        load_execution()
    )

    plot_schedule(
        schedule
    )

    plot_execution(
        execution
    )

    print_stats(
        execution
    )


if __name__ == "__main__":

    main()