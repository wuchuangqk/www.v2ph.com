from datetime import datetime
import time
from tools.util import p

log_path = p("./log/log.txt")


def log(text):
    log_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{log_time}]{text}")
    with open(log_path, "a", encoding="utf8") as f:
        f.write("[" + log_time + "]" + text + "\n")


def find(arr, key, value):
    for item in arr:
        if item[key] == value:
            return item
    return None


def today():
    """当前时间，yyyy-MM-dd HH:mm:ss"""
    localtime = time.localtime()
    return time.strftime("%Y-%m-%d", localtime)
