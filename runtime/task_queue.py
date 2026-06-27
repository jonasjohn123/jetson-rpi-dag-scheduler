import subprocess
import threading
import time

from runtime.artifact_manager import (
    artifact_exists
)

from runtime.artifact_transfer import (
    send_artifact
)

from runtime.execution_logger import (
    log_execution
)


class TaskQueue:

    def __init__(self):

        self.workflow_id = None

        self.tasks = []

        self.started = False

        self.completed = False

        self.failed = False

        self.worker_offset_ms = 0

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
        start_timestamp_ms,
        worker_offset_ms
    ):

        self.start_timestamp_ms = (
            start_timestamp_ms
        )

        self.worker_offset_ms = (
            worker_offset_ms
        )

        self.completed = False

        self.failed = False

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
        task,
        scheduled_start,
        actual_start
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

            print(
                "[ALLOCATED]",
                task.task_id,
                allocated_seconds * 1000,
                "ms"
            )

            subprocess.run(

                task.command,

                shell=True,

                check=True

                #,timeout=allocated_seconds

            )

            actual_finish = int(
                time.time() * 1000
            )

            idle_ms=max(
                0,
                scheduled_finish - actual_finish
            )

            actual_start_global = (

                actual_start

                -

                self.worker_offset_ms
            )

            actual_finish_global = (

                actual_finish

                -

                self.worker_offset_ms
            )

            log_execution(

                {
                    "workflow_id":
                        self.workflow_id,

                    "task_id":
                        task.task_id,

                    "scheduled_start":
                        scheduled_start,

                    "scheduled_finish":
                        scheduled_finish,

                    "worker_offset_ms":
                        self.worker_offset_ms,

                    "actual_start":
                        actual_start,

                    "actual_finish":
                        actual_finish,

                    "actual_start_global":
                        actual_start_global,

                    "actual_finish_global":
                        actual_finish_global,

                    "idle_ms":
                        idle_ms,

                    "delta_ms":
                        actual_finish
                        -
                        scheduled_finish
                }
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

            RUNTIME_SLACK_MS = 100

            if (
                actual_finish
                >
                scheduled_finish + RUNTIME_SLACK_MS
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
            print(
                "[TRANSFER]",
                task.task_id,
                destination.artifact_name,
                destination.worker_ip
            )

            transfer_start = time.time()

            response = send_artifact(

                workflow_id=self.workflow_id,

                producer_task_id=task.task_id,

                artifact_name=
                destination.artifact_name,

                worker_ip=
                destination.worker_ip

            )

            transfer_ms = (time.time() - transfer_start) * 1000

            if not response.success:

                print(
                    "[FAIL]",
                    task.task_id,
                    "artifact transfer failed"
                )

                return False
            print(
                "[TRANSFER COMPLETE]",
                task.task_id,
                destination.artifact_name,
                f"{transfer_ms:.2f} ms",
            )

        return True
    
    def is_completed(
        self
    ):

        return self.completed


    def is_failed(
        self
    ):

        return self.failed

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

            print(
                "[WAIT]",
                task.task_id,
                "now=",
                int(time.time() * 1000),
                "target=",
                scheduled_start
            )

            self.wait_until(
                scheduled_start
            )

            actual_start = int(
                time.time() * 1000
            )

            print(
                "[START]",
                task.task_id,
                actual_start,
                "delta=",
                actual_start - scheduled_start,
                "ms"
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

                self.failed = True

                return

            success = self.run_task(
                task,
                scheduled_start,
                actual_start
            )

            if not success:
                self.failed = True
                return

            success = self.verify_outputs(
                task
            )

            if not success:
                self.failed = True
                return

            success = self.transfer_outputs(
                task
            )

            if not success:
                self.failed = True
                return

            print(
                "[DONE]",
                task.task_id
            )

        self.completed = True
        print(
            "[WORKFLOW COMPLETE]"
        )