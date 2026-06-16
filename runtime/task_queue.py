import subprocess
import threading
import time

from runtime.artifact_manager import (
    artifact_exists
)

from runtime.artifact_transfer import (
    send_artifact
)


class TaskQueue:

    def __init__(self):

        self.workflow_id = None

        self.tasks = []

        self.started = False

        self.start_timestamp_ms = None

        self.lock = threading.Lock()

    def load_schedule(
        self,
        workflow_id,
        tasks
    ):

        with self.lock:

            self.workflow_id = workflow_id

            self.tasks = sorted(
                tasks,
                key=lambda task:
                task.start_ms
            )

    def start(
        self,
        start_timestamp_ms
    ):

        self.start_timestamp_ms = (
            start_timestamp_ms
        )

        self.started = True

        thread = threading.Thread(
            target=self.run,
            daemon=True
        )

        thread.start()

    def wait_until(
        self,
        absolute_timestamp_ms
    ):

        while True:

            now_ms = int(
                time.time() * 1000
            )

            remaining = (
                absolute_timestamp_ms
                -
                now_ms
            )

            if remaining <= 0:
                return

            time.sleep(
                min(
                    remaining / 1000,
                    0.1
                )
            )

    def check_inputs(
        self,
        task
    ):

        for artifact in task.inputs:

            if not artifact_exists(

                self.workflow_id,

                artifact.producer_task_id,

                artifact.artifact_name

            ):

                return False

        return True

    def run_task(
        self,
        task
    ):

        allocated_seconds = (

            task.finish_ms
            -
            task.start_ms

        ) / 1000

        scheduled_finish = (

            self.start_timestamp_ms
            +
            int(task.finish_ms)

        )

        try:

            subprocess.run(

                task.command,

                shell=True,

                check=True

                #,timeout=allocated_seconds

            )

            actual_finish = int(
                time.time() * 1000
            )
            print(
                "[TIMING]",
                task.task_id,
                "scheduled:",
                scheduled_finish,
                "actual:",
                actual_finish,
                "delta:",
                actual_finish - scheduled_finish,
                "ms"
            )

            if (
                actual_finish
                >
                scheduled_finish
            ):

                print(
                    "[FAIL]",
                    task.task_id,
                    "missed deadline"
                )

                return False

            return True

        except subprocess.TimeoutExpired:

            print(
                "[FAIL]",
                task.task_id,
                "deadline exceeded"
            )

            return False

        except subprocess.CalledProcessError:

            print(
                "[FAIL]",
                task.task_id,
                "execution failed"
            )

            return False

    def verify_outputs(
        self,
        task
    ):

        for output in task.outputs:

            if not artifact_exists(

                self.workflow_id,

                task.task_id,

                output

            ):

                print(
                    "[FAIL]",
                    task.task_id,
                    "missing output:",
                    output
                )

                return False

        return True

    def transfer_outputs(
        self,
        task
    ):

        for destination in task.destinations:

            response = send_artifact(

                workflow_id=self.workflow_id,

                producer_task_id=task.task_id,

                artifact_name=
                destination.artifact_name,

                worker_ip=
                destination.worker_ip

            )

            if not response.success:

                print(
                    "[FAIL]",
                    task.task_id,
                    "artifact transfer failed"
                )

                return False

        return True

    def run(self):

        print(
            "[QUEUE]",
            self.workflow_id,
            "started"
        )

        for task in self.tasks:

            scheduled_start = (

                self.start_timestamp_ms
                +
                int(task.start_ms)

            )

            self.wait_until(
                scheduled_start
            )

            print(
                "[TASK]",
                task.task_id,
                "scheduled start reached"
            )

            if not self.check_inputs(
                task
            ):

                print(
                    "[FAIL]",
                    task.task_id,
                    "missing artifacts"
                )

                return

            success = self.run_task(
                task
            )

            if not success:
                return

            success = self.verify_outputs(
                task
            )

            if not success:
                return

            success = self.transfer_outputs(
                task
            )

            if not success:
                return

            print(
                "[DONE]",
                task.task_id
            )

        print(
            "[WORKFLOW COMPLETE]"
        )