from bs4 import BeautifulSoup
import time
import cloudscraper
from util import log, p
from config import host
import brotli

scraper = cloudscraper.create_scraper(delay=10)


def _inspect(doc):
    # 请求被检查
    if doc.select("#challenge-error-text"):
        log("5秒盾")
        return False
    # 需要登录
    if doc.select(".login-box-msg"):
        log("需要登录")
        return False
    if doc.select("#checkout"):
        log("访问次数达到上限")
        return False
    return True


def dl_html(url, headers, debug=False):
    """下载网页"""
    try:
        log(f"-->请求页面：{url}")
        start_time = time.time()
        res = scraper.get(url, headers=headers)
        # 重定向
        if res.status_code == 302:
            log(f"302重定向")
            return dl_html(host + res.headers["location"], debug)
        log(f"<--成功，用时{round(time.time() - start_time, 3)}秒")
        res.encoding = "utf-8"
        # 将页面保存到本地用于调试
        if debug:
            with open(p("debug.html"), "w", encoding="utf-8") as f:
                f.write(res.text)

        html = BeautifulSoup(res.text, "html.parser")
        if not _inspect(html):
            return None
        return html
    except Exception as e:
        log(f"<--失败，用时{round(time.time() - start_time, 3)}秒")
        print(e)
        return None


def dl_img(url, headers):
    """下载图片"""
    try:
        log(f"-->请求图片：{url}")
        start_time = time.time()
        res = scraper.get(url, headers=headers)
        log(f"<--成功，用时{round(time.time() - start_time, 3)}秒")
        if res.text.startswith("<!DOCTYPE html>"):
            return None
        return res.content
    except Exception as e:
        log(f"<--失败，用时{round(time.time() - start_time, 3)}秒")
        print(e)
        return None
