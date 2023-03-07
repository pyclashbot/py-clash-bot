"""Server for handling API requests to interact witht the worker thread"""

import signal
from logging.config import dictConfig

from flask import Flask, request
from flask.logging import create_logger
from flask_cors import CORS
from gevent.pywsgi import WSGIServer

from pyclashbot.bot import WorkerThread
from pyclashbot.utils.logger import Logger

dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "formatter": "default",
            }
        },
        "root": {"level": "DEBUG", "handlers": ["console"]},
    }
)


class ThreadAPI:
    """Class for handling thread API requests."""

    def __init__(self):
        self.app = Flask(__name__)
        create_logger(self.app)
        CORS(self.app, supports_credentials=True)

        self.thread = None
        self.thread_logger = Logger()

        self.app.route("/start-thread", methods=["POST"])(self.start_thread)
        self.app.route("/stop-thread", methods=["GET"])(self.stop_thread)
        self.app.route("/toggle-pause-thread", methods=["GET"])(self.pause_thread)
        self.app.route("/output")(self.handle_output)
        self.app.route("/heartbeat")(self.heartbeat)

        signal.signal(signal.SIGTERM, self.sigterm_handler)

        self.http_server = WSGIServer(("127.0.0.1", 1357), self.app)

    def start_thread(self):
        """Starts the thread with the given args."""
        try:
            if request.json is not None and self.thread is None:
                selected_jobs: list = request.json["selectedJobs"]
                selected_accounts: int = int(request.json["selectedAccounts"])
                args = (selected_jobs, selected_accounts)
                self.app.logger.info(  # pylint: disable=no-member
                    "Starting thread with args: %s, of types: %s",
                    args,
                    list(map(type, args)),
                )
                self.thread = WorkerThread(self.thread_logger, args)
                self.thread.start()

            # Return success response
            return {"status": "started", "message": "Thread started"}
        except Exception as err:
            self.app.logger.warning(err)  # pylint: disable=no-member
            return {"status": "failed", "message": f"Error: {err}"}

    def stop_thread(self):
        """Stops the thread."""
        self.thread_logger = Logger()
        if self.thread is not None:
            self.thread.shutdown(kill=True)
        return {"status": "stopping", "message": "Stopping thread"}

    def pause_thread(self):
        """Pauses/resumes the thread."""
        if self.thread is not None:
            paused: bool = self.thread.toggle_pause()
            if paused:
                return {"status": "paused", "message": "Paused thread"}
            return {"status": "resumed", "message": "Resuming thread"}
        return {"status": "stopped", "message": "No thread running"}

    def handle_output(self):
        """Handles output requests."""
        if self.thread is not None:
            if self.thread.shutdown_flag.is_set() and not self.thread.is_alive():
                return {"status": "stopped", "message": "Idle"}
            stats = self.thread_logger.get_stats()
            if stats is not None:
                if self.thread_logger.errored:
                    self.stop_thread()
                    self.app.logger.warning(
                        "Thread errored: %s", stats["current_status"]
                    )
                    return {
                        "status": "errored",
                        "message": f"Error: {stats['current_status']}",
                    }
                if self.thread.shutdown_flag.is_set() and self.thread.is_alive():
                    stats[
                        "current_status"
                    ] = f"Waiting for: {stats['current_status']} to stop"
                return {
                    "status": "running",
                    "message": f"{stats['current_status']}",
                    "statistics": stats,
                }
        self.app.logger.info("No thread running")  # pylint: disable=no-member
        return {"status": "stopped", "message": "No thread running", "statistics": {}}

    def heartbeat(self):
        """Handles heartbeat requests."""
        return {"status": "listening", "message": "Server running"}

    def sigterm_handler(self, _signo, _stack_frame):
        """Handles SIGTERM signal."""
        self.stop_thread()
        self.http_server.stop()


if __name__ == "__main__":
    api = ThreadAPI()
    api.http_server.serve_forever()
