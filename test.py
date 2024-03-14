import cloudscraper, re
from bs4 import BeautifulSoup
from account import account_manager
scraper = cloudscraper.create_scraper(delay=10)


def test_img():
    url = "https://cdn.v2ph.com/photos/AD0Y12YCk1LmKeLQ.jpg"
    headers = {
        "Cookie": "frontend=cbe602772eb5083bf4a584a06d90d3a6; _gid=GA1.2.1037383153.1691043511; _ga_V96C605RT9=GS1.1.1691115885.1.0.1691115906.0.0.0; cf_clearance=ba7xrVkFrZfOGoPhL8sRDVuQNMEnVkFG69CeYUslpQY-1691137066-0-1-9f6def1.d73657f8.5ef78111-0.2.1691137066; frontend-rmu=1vuu2LzywPPe9AqoWrYkjQ4Hf9isQw%3D%3D; frontend-rmt=aAQnYYiTr%2FyoS%2FwLyX6H46JjF74loMWZ%2FC1MuIaYfpbRE1LgLQ1xO5%2FfdtOrd%2B%2Bk; _gat_UA-140713725-1=1; _ga=GA1.1.1256903320.1691043511; _ga_170M3FX3HZ=GS1.1.1691134993.7.1.1691137264.51.0.0",
        "Referer": "https://www.v2ph.com/",
    }
    req = scraper.get(url, headers=headers)
    print(req.status_code, req.text, req.content)
    with open("debug.jpg", "wb") as f:
        f.write(req.content)


def test_html():
    with open("debug.html", "r", encoding="utf-8") as f:
        html = BeautifulSoup(f.read(), "html.parser")
        temp1 = html.select(".main-wrap .pt-2 .row .col-md-6")[0].select("dd")
        img_total = int(re.findall(r"\d+", temp1[len(temp1) - 1].text)[0])
        print(img_total)


if __name__ == "__main__":
    account = account_manager()
    print(account.cookies)
