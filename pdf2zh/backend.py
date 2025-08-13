import io
import json
import threading
import uuid
from typing import Any, Dict, Optional

from flask import Flask, request, send_file
from flask_cors import CORS

from pdf2zh import translate_stream
from pdf2zh.doclayout import ModelInstance

flask_app = Flask("pdf2zh")

# Enable CORS for frontend development/usage
CORS(flask_app, resources={r"/v1/*": {"origins": "*"}})


class InMemoryTask:
    def __init__(self, task_id: str) -> None:
        self.id = task_id
        self.state: str = "PENDING"
        self.info: Optional[Dict[str, int]] = None
        self.error: Optional[str] = None
        self.mono: Optional[bytes] = None
        self.dual: Optional[bytes] = None
        self.cancel_event = threading.Event()
        self.thread: Optional[threading.Thread] = None


_TASKS: Dict[str, InMemoryTask] = {}
_LOCK = threading.Lock()


def _run_task(task: InMemoryTask, stream: bytes, args: Dict[str, Any]) -> None:
    try:

        def progress_bar(t) -> None:
            with _LOCK:
                task.state = "PROGRESS"
                task.info = {"n": int(t.n), "total": int(t.total)}

        mono, dual = translate_stream(
            stream,
            callback=progress_bar,
            cancellation_event=task.cancel_event,
            model=ModelInstance.value,
            **args,
        )
        with _LOCK:
            task.mono = mono
            task.dual = dual
            task.state = "SUCCESS"
    except Exception as e:  # noqa: BLE001
        with _LOCK:
            task.error = str(e)
            # Distinguish cancel
            if task.cancel_event.is_set():
                task.state = "REVOKED"
            else:
                task.state = "FAILURE"


@flask_app.route("/v1/translate", methods=["POST"])
def create_translate_tasks():
    file = request.files["file"]
    stream = file.stream.read()
    args = json.loads(request.form.get("data") or "{}")

    task_id = str(uuid.uuid4())
    task = InMemoryTask(task_id)
    with _LOCK:
        _TASKS[task_id] = task

    worker = threading.Thread(target=_run_task, args=(task, stream, args), daemon=True)
    task.thread = worker
    worker.start()
    return {"id": task_id}


@flask_app.route("/v1/health", methods=["GET"])
def health_check():
    return {"status": "ok"}, 200


@flask_app.route("/v1/translate/<task_id>", methods=["GET"])
def get_translate_task(task_id: str):
    with _LOCK:
        task = _TASKS.get(task_id)
        if task is None:
            return {"error": "not found"}, 404
        state = task.state
        info = task.info
    if state == "PROGRESS":
        return {"state": state, "info": info}
    return {"state": state}


@flask_app.route("/v1/translate/<task_id>", methods=["DELETE"])
def delete_translate_task(task_id: str):
    with _LOCK:
        task = _TASKS.get(task_id)
        if task is None:
            return {"error": "not found"}, 404
        task.cancel_event.set()
        task.state = "REVOKED"
    return {"state": "REVOKED"}


@flask_app.route("/v1/translate/<task_id>/<file_format>")
def get_translate_result(task_id: str, file_format: str = "mono"):
    with _LOCK:
        task = _TASKS.get(task_id)
        if task is None:
            return {"error": "not found"}, 404
        if task.state != "SUCCESS" or task.mono is None or task.dual is None:
            return {"error": "task not finished"}, 400
        to_send = task.mono if file_format == "mono" else task.dual
    return send_file(io.BytesIO(to_send), "application/pdf")


if __name__ == "__main__":
    flask_app.run()
