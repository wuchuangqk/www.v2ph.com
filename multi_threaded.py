"""
多线程下载单个图集
"""
from statistics import mode
from bs4 import BeautifulSoup
import requests
import os
from datetime import datetime
import time
import json, sys, os
import cloudscraper
from lib.util import p, log

headers = {
    "cookie": "",
    "referer": "https://www.v2ph.com/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.188",
}
# 下载记录
download_history = []
# 模特名称
girl_name = "小岚"
# 写真集名称
gallery_name = "淑女抬脚"


def is_download():
    """是否下载过"""
    for girl in download_history:
        if girl["name"] == girl_name:
            for gallery in girl["galleries"]:
                if gallery["name"] == gallery_name:
                    return gallery["total_count"] == gallery["download_count"]
    return False


def start():
    global headers
    global download_history
    with open(p("cookie.txt"), "r") as f:
        headers["cookie"] = f.read()
    with open(p("download_history.json"), "r") as f:
        download_history = json.load(f)

    # 检查图集是否已下载完成
    if is_download():
        return log("%s:%s已下载，无需重复下载")


if __name__ == "__main__":
    start()
