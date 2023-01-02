import signal

from flask import Flask, request
from flask_cors import CORS
from gevent.pywsgi import WSGIServer

from pyclashbot.bot import WorkerThread
from pyclashbot.utils.logger import Logger

app = Flask(__name__)
CORS(app, supports_credentials=True)

# Create global variable for thread
thread: WorkerThread | None = None
logger = Logger()


# Define route to start thread
@app.route("/start-thread", methods=["POST"])
def start_thread():
    try:
        global thread
        if request.json is not None and thread is None:
            selected_jobs: list = request.json["selectedJobs"]
            selected_accounts: int = request.json["selectedAccounts"]

            print(type(selected_jobs))
            print(type(selected_accounts))

            args = (selected_jobs, selected_accounts)

            thread = WorkerThread(logger, args)
            thread.start()

        # Return success response
        return {"status": "started", "message": "Thread started"}
    except Exception as err:
        return {"status": "failed", "message": f"Error: {err}"}


# Define route to stop thread
@app.route("/stop-thread", methods=["GET"])
def stop_thread():
    # Stop thread
    global thread, logger
    if thread is not None:
        thread.shutdown()
        thread = None
        logger = Logger()

    # Return success response
    return {"status": "stopped", "message": "Thread stopped"}


@app.route("/output")
def handle_output():
    # read the value of the mutex output on the thread object
    stats = logger.get_stats()
    if thread is not None and stats is not None:
        if logger.errored:
            return {"status": "errored", "message": f"Error: {stats['current_status']}"}
        return {
            "status": "running",
            "message": f"{stats['current_status']}",
            "statistics": stats,
        }
    return {"status": "stopped", "message": "No thread running", "statistics": {}}


@app.route("/heartbeat")
def heartbeat():
    return {"status": "listening", "message": "Server running"}


class SigTermException(Exception):
    pass


def sigterm_handler(_signo, _stack_frame):
    # Raises SystemExit(0):
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
        logger = Logger()
    print("Server shut down")
    exit(0)
