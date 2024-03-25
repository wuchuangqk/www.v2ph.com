from util import log
from history import Album
from account import account_manager, to_cookie_string
from download import dl_html, dl_img
from tools.util import p
import re
import os
from config import user_agent, save_path, html_cookies_key, img_cookies_key, host


def save_img(_path, binary):
    img = p(f"{save_path}/{_path}")
    with open(img, "wb") as f:
        f.write(binary)
    size = os.path.getsize(img) / (1024 * 1024)
    log(f"图片大小：{round(size, 3)}MB")


class AlbumDownloader:
    """基于专辑的下载方式"""

    def __init__(self, model_name, album_name, url):
        """
        :param model_name: 模特
        :param album_name: 专辑（套图）
        :param url: 专辑页面地址
        """
        self.album = Album(model_name, album_name, url)
        if url.find("?hl=zh-Hans") == -1:
            self.url = url + "?hl=zh-Hans"
        else:
            self.url = url
        self.page_index = 1
        self.page_total = 1
        self.headers = {
            "Cookie": "",
            "user-agent": user_agent,
            "Sec-Ch-Ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Microsoft Edge";v="122"',
        }
        self.img_headers = {
            "Cookie": "",
            "Referer": host,
            "user-agent": user_agent,
        }

    def _set_headers(self):
        account = account_manager()
        account.sub_visit_times()
        self.headers["Cookie"] = to_cookie_string(account.cookies, html_cookies_key)
        self.img_headers["Cookie"] = to_cookie_string(account.cookies, img_cookies_key)

    def _dl_page_imgs(self, html):
        '''下载本页图片'''
        img_tags = html.select(".photos-list .album-photo img")
        for i in range(len(img_tags)):
            img = img_tags[i]
            cur = (self.page_index - 1) * 10 + i + 1
            if cur <= self.album.donwload_count:
                continue
            log(f"下载进度：{cur}/{self.album.total_count}")
            name = img["alt"] + ".jpg"
            binary = dl_img(img["data-src"], self.img_headers)
            if binary == None:
                raise Exception("程序终止：下载图片失败")
            save_img(f"{self.album.model_name}/{self.album.album_name}/{name}", binary)
            self.album.increment()

    def _page(self):
        for i in range(self.page_index, self.page_total + 1):
            self.page_index = i
            log(f"页数：{self.page_index}/{self.page_total}")
            html = dl_html(f"{self.url}&page={self.page_index}", self.headers)
            if html == None:
                raise Exception("程序终止：下载页面失败")
            self._dl_page_imgs(html)

    def _index(self):
        """从首页开始下载"""
        log(f"专辑首页")
        html = dl_html(f"{self.url}&page={self.page_index}", self.headers)
        if html == None:
            raise Exception("程序终止：专辑首页获取失败")

        # 提取图片总数
        temp = html.select(".main-wrap .pt-2 .row .col-md-6")[0].select("dd")
        img_total = int(re.findall(r"\d+", temp[len(temp) - 1].text)[0])
        self.album.set_album_total(img_total)
        self.set_page_total(img_total)

        log(f"图片总数：{img_total}")
        log(f"页数：{self.page_index}/{self.page_total}")
        self._dl_page_imgs(html)

        if self.page_index < self.page_total:
            self.page_index += 1
            self._page()

    def set_page_total(self, img_total):
        page_total = int(img_total / 10)
        # 不够一页的要往后补一页
        if page_total == 0 or img_total % 10 > 0:
            page_total += 1
        self.page_total = page_total

    def set_page_index(self, donwload_count):
        page_index = int(donwload_count / 10)
        if page_index == 0 or page_index % 10 > 0:
            page_index += 1
        self.page_index = page_index

    def start(self):
        log("————————————————————下载开始————————————————————")
        self.album.show_status()
        if self.album.is_finish:
            log("————————————————————下载结束————————————————————")
            return

        self._set_headers()

        # 继续下载
        if self.album.donwload_count > 0:
            log("继续未完成的下载")
            # 通过总图片数，计算总页数
            self.set_page_total(self.album.total_count)
            # 通过已下载的图片数，计算应该从哪一页开始下
            self.set_page_index(self.album.donwload_count)
            self._page()
        else:
            # 新的下载
            self._index()
        log("————————————————————下载结束————————————————————")
