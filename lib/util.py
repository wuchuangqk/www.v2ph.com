import os, sys
from datetime import datetime


def p(url):
    return os.path.join(sys.path[0], url)


def log(text):
    log_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("[%s]%s" % (log_time, text))
    with open(p("./log/log.txt"), "a", encoding="utf8") as f:
        f.write("[" + log_time + "]" + text + "\n")


def now(time=False):
    if time:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return datetime.now().strftime("%Y-%m-%d")
