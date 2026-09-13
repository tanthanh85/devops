from datetime import datetime, timezone
import json
import os
import time
import uuid

from ansible.plugins.callback import CallbackBase
from audit import send


class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = "aggregate"
    CALLBACK_NAME = "audit_callback"
    CALLBACK_NEEDS_ENABLED = True

    def __init__(self):
        super().__init__()
        self.started = {}

    def _emit(self, action, outcome="unknown", **fields):
        event = {
            "@timestamp": datetime.now(timezone.utc).isoformat(),
            "event.id": str(uuid.uuid4()),
            "event.dataset": "network_cicd.audit",
            "event.category": "configuration",
            "event.type": "change",
            "event.action": action,
            "event.outcome": outcome,
            "ci.pipeline.id": os.getenv("CI_PIPELINE_ID", "local"),
            "ci.job.id": os.getenv("CI_JOB_ID", "local"),
            "deployment.environment": os.getenv("TARGET_ENVIRONMENT", "unknown"),
            **fields,
        }
        send(event)
        self._display.display("AUDIT_EVENT " + json.dumps(event, separators=(",", ":")))

    def v2_playbook_on_task_start(self, task, is_conditional):
        self.started[task._uuid] = time.perf_counter()
        self._emit("ansible_task_start", task_name=task.get_name())

    def _result(self, result, outcome, changed=False):
        task = result._task
        duration = round((time.perf_counter() - self.started.pop(task._uuid, time.perf_counter())) * 1000, 2)
        self._emit(
            "ansible_task_complete",
            outcome,
            task_name=task.get_name(),
            host=result._host.get_name(),
            changed=changed,
            duration_ms=duration,
        )

    def v2_runner_on_ok(self, result):
        self._result(result, "success", bool(result._result.get("changed", False)))

    def v2_runner_on_failed(self, result, ignore_errors=False):
        self._result(result, "failure")

    def v2_runner_on_unreachable(self, result):
        self._result(result, "failure")
