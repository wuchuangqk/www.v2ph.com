from tools.util import p, now
import json
from util import log,today

cookie_path = p("cookie.txt")
account_path = p("account.json")
account_list = []
account = None
cookies = {}


def init():
    global account_list
    global account
    global cookies
    with open(account_path, "r") as f:
        account_list = json.load(f)
    reset_account()
    for item in account_list:
        if item["visit_times"] > 0:
            account = item
            break
    if account == None:
        return
    log(f'账号{account['account']}今日可用次数：{account['visit_times']}')
    items = account["cookie"].split(";")
    for item in items:
        key, value = item.split("=")
        cookies[key.strip()] = value.strip()


def toCookieString(key_list):
    list = []
    for key in key_list:
        list.append(key + "=" + cookies[key])
    return ";".join(list)


def sub_visit_times():
    account["date"] = today()
    account["visit_times"] -= 1
    save_account()


def save_account():
    with open(account_path, "w") as w:
        json.dump(account_list, w, indent=2, ensure_ascii=False)


def check_account():
    pass


def reset_account():
    """每天重置次数"""
    global account_list
    _today = today()
    for item in account_list:
        if item["date"] == None or item["date"] != _today:
            item["visit_times"] = 16
    save_account()


init()
