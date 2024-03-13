"""
下载程序
"""

from bs4 import BeautifulSoup
import time
import re
import cloudscraper
from util import log
from manager import Manager
import cookies

scraper = cloudscraper.create_scraper()
# scraper = cloudscraper.create_scraper(delay=10)
# cookie_manager = Cookies()
headers = {
    "Cookie": cookies.toCookieString(
        [
            "cf_clearance",
            "_gid",
            "_ga",
            "_ga_170M3FX3HZ",
            "frontend",
            "frontend-rmu",
            "frontend-rmt",
        ]
    ),
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0",
    "Sec-Ch-Ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Microsoft Edge";v="122"',
}
host = "https://www.v2ph.com"
img_headers = {
    "Cookie": cookies.toCookieString(["cf_clearance", "_gid", "_ga", "_ga_170M3FX3HZ"]),
    "Referer": host,
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0",
}
# 域名


class Download:
    def __init__(self, model, album, album_url):
        """
        :param model: 模特
        :param album: 专辑（套图）
        :param album_url: 专辑页面地址
        """
        self.model = model
        self.album = album
        if album_url.find("?hl=zh-Hans") == -1:
            self.album_url = album_url + "?hl=zh-Hans"
        else:
            self.album_url = album_url
        self.manager = Manager(model=self.model, album=self.album)
        self.page_num = 1

    def _inspect(self, doc):
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

    def _dl_html(self, url, debug=False):
        try:
            start_time = time.time()
            log(f"-->请求页面：{url}")
            res = scraper.get(url, headers=headers)
            # 重定向
            if res.status_code == 302:
                log(f"302重定向")
                return self._dl_html(host + res.headers["location"], debug)
            log(f"<--成功，用时{round(time.time() - start_time, 3)}秒")
            res.encoding = "utf-8"

            # 将页面保存到本地用于调试
            if debug:
                with open("debug.html", "w", encoding="utf-8") as f:
                    f.write(res.text)

            html = BeautifulSoup(res.text, "html.parser")
            if not self._inspect(html):
                return None
            return html
        except Exception as e:
            print(e)
            log(f"<--失败，用时{round(time.time() - start_time, 3)}秒")

    def _dl_img(self, url):
        try:
            start_time = time.time()
            log(f"-->请求图片：{url}")
            res = scraper.get(url, headers=img_headers)
            log(f"<--成功，用时{round(time.time() - start_time, 3)}秒")
            if res.text.startswith("<!DOCTYPE html>"):
                return None
            return res.content
        except Exception as e:
            print(e)
            log(f"<--失败，用时{round(time.time() - start_time, 3)}秒")

    def _img_queue(self, html):
        img_tags = html.select(".photos-list .album-photo img")
        for i in range(len(img_tags)):
            img = img_tags[i]
            cur = (self.page_num - 1) * 10 + i + 1
            log(f"下载进度：{cur}/{self.manager.get_album_total()}")
            name = img["alt"] + ".jpg"
            binary = self._dl_img(img["data-src"])
            self.manager.save(name, binary)

    def _dl_album(self):
        log(f"专辑首页")
        html = self._dl_html(f"{self.album_url}&page={self.page_num}", True)
        if html == None:
            return

        # 提取图片总数
        temp = html.select(".main-wrap .pt-2 .row .col-md-6")[0].select("dd")
        img_total = int(re.findall(r"\d+", temp[len(temp) - 1].text)[0])
        self.manager.set_album_total(img_total)

        # 计算页数（一页十张图片）
        page_total = int(img_total / 10)
        # 不够一页的要往后补一页
        if page_total == 0 or img_total % 10 > 0:
            page_total += 1

        log(f"图片总数：{img_total}")
        log(f"页数：{self.page_num}/{page_total}")
        self._img_queue(html)

        # 下载剩余页面
        for page_index in range(int(page_total)):
            # 跳过第一页
            if page_index == 0:
                continue
            self.page_num = page_index + 1
            log(f"页数：{page_index}/{page_total}")
            html = self._dl_html(f"{self.album_url}&page={self.page_num}")
            if html == None:
                return
            self._img_queue(html)

    def start(self):
        log("————————————————————下载开始————————————————————")
        log(f"模特：{self.model}")
        log(f"专辑：《{self.album}》")
        cookies.sub_visit_times()
        self.manager.show_status()
        if self.manager.is_finish():
            log("————————————————————下载结束————————————————————")
            return
        self._dl_album()
        log("————————————————————下载结束————————————————————")
