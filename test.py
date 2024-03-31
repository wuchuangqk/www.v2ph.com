import cloudscraper, re
from bs4 import BeautifulSoup
from account import account_manager, to_cookie_string
from download import dl_img, dl_html
from config import user_agent, img_cookies_key, sec_ch_ua, host
import json
from util import p

scraper = cloudscraper.create_scraper(delay=10)
account_path = p("data/account.json")
account_list = []

def test_img():
    img = dl_img(
        url='https://cdn.v2ph.com/photos/sQv4QTHri4Zq4rmi.jpg',
        headers={
            'cookie': to_cookie_string(account_list[0]['cookie'], img_cookies_key),
            "Referer": host,
            "user-agent": user_agent,
        },
    )
    print(img == None)


def test_html():
    with open("debug.html", "r", encoding="utf-8") as f:
        html = BeautifulSoup(f.read(), "html.parser")
        temp1 = html.select(".main-wrap .pt-2 .row .col-md-6")[0].select("dd")
        img_total = int(re.findall(r"\d+", temp1[len(temp1) - 1].text)[0])
        print(img_total)


def test_account():
    user_index = 'https://www.v2ph.com/user/index'
    headers = {
        # 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        # 'Accept-Encoding': 'gzip, deflate, br, zstd',
        # 'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        # 'Cache-Control': 'max-age=0',
        "Cookie": account_list[0]['cookie'],
        # "user-agent": user_agent,
        # "Sec-Ch-Ua": sec_ch_ua,
        # "Sec-Ch-Ua-Mobile": '?0',
        # 'Sec-Ch-Ua-Platform': '"Windows"',
        # 'Sec-Fetch-Dest': 'document',
        # 'Sec-Fetch-Mode': 'navigate',
        # 'Sec-Fetch-User': '?1',
        # 'Upgrade-Insecure-Requests': '1',
    }
    html = dl_html(user_index, headers=headers, debug=True)
    print(html == None)

if __name__ == "__main__":
    global account_list
    with open(account_path, "r") as f:
        account_list = json.load(f)
    test_account()
