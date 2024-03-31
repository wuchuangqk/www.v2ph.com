from datetime import datetime
import time
import os
import sys
import threading

log_path = ''


def log(text):
    log_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{log_time}][{threading.current_thread().getName()}]{text}")
    with open(log_path, "a", encoding="utf8") as f:
        f.write("[" + log_time + "]" + text + "\n")


def find(arr, key, value):
    for item in arr:
        if item[key] == value:
            return item
    return None


def today():
    """当前时间，不带时分秒

    Returns:
        str: 当前时间
    """
    localtime = time.localtime()
    return time.strftime("%Y-%m-%d", localtime)


def now():
    '''当前时间，带时分秒'''
    localtime = time.localtime()
    return time.strftime('%Y-%m-%d %H:%M:%S', localtime)


def p(url):
    """以脚本所在位置为相对位置

    Args:
        url (str): 地址

    Returns:
        str: 相对位置
    """
    return os.path.join(sys.path[0], url)


def init():
    global log_path
    log_fold = p("log")
    if not os.path.exists(log_fold):
        os.mkdir('log')
    log_path = p("log/log.txt")


init()
