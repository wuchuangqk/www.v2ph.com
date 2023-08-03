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
from lib.util import p, log, now

scraper = cloudscraper.create_scraper(delay=10)
headers = {
    "cookie": "",
    "referer": "https://www.v2ph.com/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.188",
}
# 域名
host = "https://www.v2ph.com"
# 下载记录
download_history = []
# 模特名称
girl_name = "小岚"
# 写真集名称
gallery_name = "淑女抬脚"
# 图集网页地址
page_url = "https://www.v2ph.com/album/ax3e533z.html"


def register():
    """登记"""
    global download_history
    girl = None
    gallery = None

    # 检查是否已登记
    for item in download_history:
        if item["name"] == girl_name:
            girl = item
            break

    # 未登记时，进行登记
    if girl == None:
        gallery = {
            "name": gallery_name,
            "download_date": now(),
            "total_count": 0,
            "download_count": 0,
        }
        girl = {"name": girl_name, "download_date": now(), "galleries": [gallery]}
        download_history.append(girl)
        with open(p("download_history.json"), "w", encoding="utf8") as f:
            json.dump(download_history, f, indent=2)
    else:
        for item in girl["galleries"]:
            if item["name"] == gallery_name:
                gallery = item
                break
    return (girl, gallery)


def analysis(doc):
    # 请求被检查
    if doc.select("#cf-wrapper"):
        log("请求被检查")
        return False
    # 需要登录
    if doc.select(".login-box-msg"):
        log("需要登录")
        return False
        # 需要登录
    if doc.select("#checkout"):
        log("访问次数达到上限")
        return False
    return True


def download_page(url):
    start_time = time.time()
    try:
        # log("开始下载页面:%s" % (url))
        res = scraper.get(
            url, headers=headers, timeout=(6.05, 30), allow_redirects=False
        )
        # 重定向
        if res.status_code == 302:
            return download_page(host + res.headers["location"])
        res.encoding = "utf8"
        # 解析html
        html = BeautifulSoup(res.text, "html.parser")
        # 请求被检查
        if html.select("#cf-wrapper"):
            log("请求被检查")
            return False
        # 需要登录
        if html.select(".login-box-msg"):
            log("需要登录")
            return False
        # 访问次数达到上限
        if html.select("#checkout"):
            log("访问次数达到上限")
            return False
        use_time = round(time.time() - start_time, 3)
        return (html, use_time)
    except Exception as e:
        print(e)
        use_time = round(time.time() - start_time, 3)
        log("下载页面出错，用时%s秒" % (use_time))
        return False


def download_page1(url):
    start_time = time.time()
    try:
        log("开始下载页面:%s" % (url))
        res = scraper.get(
            url, headers=headers, timeout=(6.05, 30), allow_redirects=False
        )
        # 重定向
        if res.status_code == 302:
            return download_page(host + res.headers["location"])
        res.encoding = "utf8"
        # 解析html
        html = BeautifulSoup(res.text, "html.parser")
        log("下载页面完成，用时%s秒" % (round(time.time() - start_time, 3)))

        # 对doc进行分析，判断是否有效
        if not analysis(html):
            return

        # 提取页数
        page_link = html.select(".pagination .page-link")
        if len(page_link) == 0:
            log("提取页数失败，套图(%s)可能需要开通VIP" % gallery_name)
            return
        page_count = (
            page_link[len(page_link) - 1]["href"]
            .split("?")[1]
            .split("&")[0]
            .split("=")[1]
        )
        log("共%s页" % (page_count))
        # log('开始下载剩余页面(1/10)')

        # return doc
    except Exception as e:
        print(e)
        log("下载页面出错，用时%s秒" % (round(time.time() - start_time, 3)))
        return False


def start():
    global headers
    global download_history
    with open(p("cookie.txt"), "r") as f:
        headers["cookie"] = f.read()
    with open(p("download_history.json"), "r", encoding="utf8") as f:
        download_history = json.load(f)

    girl, gallery = register()
    # 检查图集是否已下载完成
    if gallery["total_count"] == gallery["download_count"]:
        return log("%s-%s已下载完成，无需重复下载" % (girl_name, gallery_name))

    # 创建文件夹
    main_fold = p("img/" + girl_name)
    if not os.path.exists(main_fold):
        os.mkdir(main_fold)
        log("创建模特文件夹:%s" % (girl_name))
    sub_fold = os.path.join(main_fold, gallery_name)
    if not os.path.exists(sub_fold):
        os.mkdir(main_fold)
        log("创建套图文件夹:%s" % (girl_name))

    # 下载页面，分析页数和图片总数量


if __name__ == "__main__":
    start()
