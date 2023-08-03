import os, json, sys
from datetime import datetime
import time
def p(url):
    return os.path.join(sys.path[0], url)

def log(text):
    log_time = datetime.now().strftime("%H时%M分%S秒")
    print("log: %s %s" % (log_time, text))
    with open(p('../log.txt'), 'a', encoding='utf8') as f:
        f.write(time + ' ' + text + '\n')