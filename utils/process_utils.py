import os


def is_other_running():
    pid = os.getpid()
    lines = os.popen("ps aux | grep python | grep youtube | grep updater | grep -v {}".format(pid)).readlines()
    return len(lines) > 0
