from tools.util import p, now
import json
from util import log, today
from download import dl_html
from config import user_agent

account_path = p("data/account.json")
account_list = []
user_index = 'https://www.v2ph.com/user/index'

def to_cookie_string(cookies_str, key_list):
    cookies = {}
    items = cookies_str.split(";")
    for item in items:
        key, value = item.split("=")
        cookies[key.strip()] = value.strip()

    list = []
    for key in key_list:
        list.append(key + "=" + cookies[key])
    return ";".join(list)

def read_account():
    """读取账号列表"""
    global account_list
    with open(account_path, "r") as f:
        account_list = json.load(f)


def save_account():
    with open(account_path, "w") as w:
        json.dump(account_list, w, indent=2, ensure_ascii=False)


def check_account_times(account):
    """检查账号当日可用次数"""
    log(f'获取账号：{account['account']}今日可用次数')
    headers = {
        "Cookie": account["cookie"],
        "user-agent": user_agent,
        "Sec-Ch-Ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Microsoft Edge";v="122"',
        "Origin": "https://www.v2ph.com",
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": "https://www.v2ph.com/user/index?__cf_chl_tk=YuK9srWYxJqZl6exlbimcoqZqgmBUVwk6R35LYtTeAs-1710425425-0.0.1.1-1578"
    }
    html = dl_html(user_index, headers=headers)
    if html == None:
        raise Exception('程序终止：访问个人中心页面失败')
    account['visit_times'] = int(html.select(".text-danger")[0].text)
    account['date'] = today()
    save_account()
    log(f'账号{account['account']}今日可用次数：{account['visit_times']}')


def reset_visit_times():
    """重置每个账号的可用次数"""
    global account_list
    _today = today()
    for item in account_list:
        if item["date"] == None or item["date"] != _today:
            item["visit_times"] = 16
    save_account()

class Account():
    def __init__(self, account):
        self._account = account
        self.cookies = self._account['cookie']

    def sub_visit_times(self):
        self._account["date"] = today()
        self._account["visit_times"] -= 1
        save_account()

def account_manager() -> Account:
    account = None
    for item in account_list:
        if item["visit_times"] > 0:
            check_account_times(item)
            if item['visit_times'] > 0:
                account = item
                break
    if account == None:
        log("没有可用的账号")
        raise Exception('程序终止：没有可用的账号')
    return Account(account)
    

def init():
    global account_list
    read_account()
    reset_visit_times()
    save_account()


init()
