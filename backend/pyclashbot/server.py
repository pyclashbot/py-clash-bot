import signal
import sys
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


app = Flask(__name__)
create_logger(app)
CORS(app, supports_credentials=True)

# Create global variable for thread
thread: WorkerThread | None = None
thread_logger = Logger()


# Define route to start thread
@app.route("/start-thread", methods=["POST"])
def start_thread():
    try:
        global thread
        if request.json is not None and thread is None:
            selected_jobs: list = request.json["selectedJobs"]
            selected_accounts: int = int(request.json["selectedAccounts"])
            args = (selected_jobs, selected_accounts)
            app.logger.info(  # pylint: disable=no-member
                "Starting thread with args: %s, of types: %s",
                args,
                list(map(type, args)),
            )
            thread = WorkerThread(thread_logger, args)
            thread.start()

        # Return success response
        return {"status": "started", "message": "Thread started"}
    except Exception as err:
        app.logger.warning(err)  # pylint: disable=no-member
        return {"status": "failed", "message": f"Error: {err}"}


# Define route to stop thread
@app.route("/stop-thread", methods=["GET"])
def stop_thread():
    # Stop thread
    global thread, thread_logger
    if thread is not None:
        thread.shutdown(kill=True)

    # Return success response
    return {"status": "stopping", "message": "Stopping thread"}


# Define route to pause thread
@app.route("/toggle-pause-thread", methods=["GET"])
def pause_thread():
    # Pause thread
    global thread
    if thread is not None:
        paused: bool = thread.toggle_pause()
        if paused:
            return {"status": "paused", "message": "Paused thread"}
        return {"status": "resumed", "message": "Resuming thread"}
    return {"status": "stopped", "message": "No thread running"}


@app.route("/output")
def handle_output():
    global thread, thread_logger
    if thread is not None:
        if thread.shutdown_flag.is_set() and not thread.is_alive():
            return {"status": "stopped", "message": "Idle"}
        # read the value of the mutex output on the thread object
        stats = thread_logger.get_stats()
        if stats is not None:
            if thread_logger.errored:
                stop_thread()
                app.logger.warning("Thread errored: %s", stats["current_status"])
                return {
                    "status": "errored",
                    "message": f"Error: {stats['current_status']}",
                }
            if thread.shutdown_flag.is_set() and thread.is_alive():
                stats[
                    "current_status"
                ] = f"Waiting for: {stats['current_status']} to stop"
            return {
                "status": "running",
                "message": f"{stats['current_status']}",
                "statistics": stats,
            }
    app.logger.info("No thread running")  # pylint: disable=no-member
    return {"status": "stopped", "message": "No thread running", "statistics": {}}


@app.route("/heartbeat")
def heartbeat():
    return {"status": "listening", "message": "Server running"}


class SigTermException(Exception):
    pass


def sigterm_handler(_signo, _stack_frame):
    raise SigTermException


http_server = WSGIServer(("127.0.0.1", 1357), app)

try:
    signal.signal(signal.SIGTERM, sigterm_handler)
    http_server.serve_forever()
except (KeyboardInterrupt, SigTermException):
    print("Shutting down server")
    http_server.stop()
    if thread is not None:
        thread.shutdown()
        thread = None
        thread_logger = Logger()
    print("Server shut down")
    sys.exit(0)
