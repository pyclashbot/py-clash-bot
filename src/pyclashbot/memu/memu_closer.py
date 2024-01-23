import psutil


def list_running_processes():
    """
    Get the name and PID of every running process.
    """
    processes = []
    for process in psutil.process_iter(["pid", "name"]):
        processes.append({"pid": process.info["pid"], "name": process.info["name"]})
    return processes


def terminate_process_by_pid(pid):
    """
    Terminate a process given its PID.
    """
    try:
        process = psutil.Process(pid)
        process.terminate()  # Try terminating the process gracefully
        print(f"Terminated process {pid} - {process.name()}")
        return True
    except psutil.NoSuchProcess:
        print(f"No such process with PID {pid}")
        return False
    except psutil.AccessDenied:
        print(f"Access denied to terminate process {pid}")
        return False
    except Exception as e:
        print(f"Error terminating process {pid}: {e}")
        return False


def close_memuc_processes():
    processes = list_running_processes()

    bad_pid_list = []

    for process in processes:
        if "memuc.exe" in process["name"]:
            bad_pid_list.append(process["pid"])

    print(f"There are {len(bad_pid_list)} memu processes running")

    closes = []
    for pid in bad_pid_list:
        closes.append(terminate_process_by_pid(pid))

    successes = 0
    for c in closes:
        if c:
            successes += 1

    print(f"Successfully closed {successes} memu processes")


if __name__ == "__main__":
    pass
