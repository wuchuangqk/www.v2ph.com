"""
多线程下载单个图集
"""
from statistics import mode
from bs4 import BeautifulSoup
import os
import time
import json, os, re
import cloudscraper
from lib.util import p, log, now
import concurrent.futures

scraper = cloudscraper.create_scraper()
# scraper = cloudscraper.create_scraper(delay=10)
headers = {
    "Cookie": "",
    # "referer": "https://www.v2ph.com/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.188",
    # "Accept-Language": "zh-CN,zh;q=0.9",
}
# 域名
host = "https://www.v2ph.com"
# 下载记录
download_history = []
# 模特名称
girl_name = "杨晨晨"
# 写真集名称
gallery_name = "杨晨晨sugar《高尔夫主题》 [秀人XIUREN] No.1874 写真集"
# 图集网页地址
page_url = "https://www.v2ph.com/album/XIUREN-1874"
# 图集保存的路径
gallery_fold = None
# 图集
gallery = None
is_stop = False
cookies = {}


def readCookies():
    global cookies
    with open(p("cookie.txt"), "r") as f:
        text = f.read()
        items = text.split(";")
        for item in items:
            key, value = item.split("=")
            cookies[key.strip()] = value.strip()


def toCookieString(key_list):
    list = []
    for key in key_list:
        list.append(key + "=" + cookies[key])
    return ";".join(list)


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
        with open(p("download_history.json"), "w", encoding="utf-8") as f:
            json.dump(download_history, f, indent=2, ensure_ascii=False)
    else:
        for item in girl["galleries"]:
            if item["name"] == gallery_name:
                gallery = item
                break
    return (girl, gallery)


def analysis(doc):
    # 请求被检查
    if doc.select("#challenge-error-text"):
        log("5秒盾")
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


def save_download_history():
    with open(p("download_history.json"), "w", encoding="utf-8") as f:
        json.dump(download_history, f, indent=2, ensure_ascii=False)


def download_other_page(url, sort, page_total):
    start_time = time.time()
    try:
        log("-->请求%s" % (url))
        res = scraper.get(url, headers=headers)
        # 重定向
        if res.status_code == 302:
            return download_other_page(host + res.headers["location"], sort)
        res.encoding = "utf-8"
        # 解析html
        html = BeautifulSoup(res.text, "html.parser")
        log("<--请求完成，用时%s秒" % (round(time.time() - start_time, 3)))

        # 对doc进行分析，判断是否有效
        if not analysis(html):
            return

        log("开始下载第%s/%s页" % (sort, page_total))
        img_links = get_link(html)
        download_img_manager(img_links)
        log("第%s/%s页下载完成" % (sort, page_total))
    except Exception as e:
        print(e)
        log("请求%s出错，用时%s秒" % (url, round(time.time() - start_time, 3)))


def get_link(html):
    # global img_links
    img_links = []
    imgs = html.select(".photos-list .album-photo img")
    for img in imgs:
        img_links.append({"name": img["alt"] + ".jpg", "src": img["data-src"]})
    return img_links


def download_img_task(link):
    """"""
    global headers
    global is_stop
    start_time = time.time()
    try:
        img_path = os.path.join(gallery_fold, link["name"])
        if os.path.exists(img_path):
            log("%s已下载完成，跳过！" % (link["name"]))
            return
        log("-->开始下载%s(%s)" % (link["name"], link["src"]))
        # 设置超时时间(6.05=连接超时时间,30=读取超时时间)
        # req = requests.get(link["src"], headers=headers, timeout=(6.05, 30))
        img_headers = {
            "Cookie": toCookieString(["cf_clearance", "_gid", "_ga", "_ga_170M3FX3HZ"]),
            "Referer": host,
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.188",
        }
        req = scraper.get(link["src"], headers=img_headers)
        if req.text.startswith("<!DOCTYPE html>"):
            is_stop = True
            raise Exception("5秒盾")
        with open(img_path, "wb") as f:
            f.write(req.content)
            # 更新已下载图片数量
            gallery["download_count"] = gallery["download_count"] + 1
            save_download_history()
        end_time = time.time()
        size = os.path.getsize(img_path) / (1024 * 1024)
        log(
            "<--下载完成，用时%s秒，图片大小%sMB"
            % (
                round(end_time - start_time, 3),
                round(size, 3),
            )
        )
    except Exception as e:
        print(e)
        log("<--下载出错，用时%s秒" % (round(time.time() - start_time, 3)))


def download_img_manager(img_links):
    """下载图片的任务"""
    # futures = []
    # with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    #     for link in img_links:
    #         future = executor.submit(
    #             download_img_task,
    #             link,
    #         )
    #         futures.append(future)

    # # 等待所有线程执行完毕
    # concurrent.futures.wait(futures)
    for link in img_links:
        if is_stop == False:
            download_img_task(link)


def download_first_page():
    """下载首页，分析页数、开启剩余页下载程序"""
    global page_url
    if page_url.find("?hl=zh-Hans") == -1:
        page_url = page_url + "?hl=zh-Hans"
    start_time = time.time()
    try:
        log("-->请求套图首页%s" % (page_url + "&page=1"))
        res = scraper.get(page_url + "&page=1", headers=headers)
        # 重定向
        if res.status_code == 302:
            return download_first_page(host + res.headers["location"])
        res.encoding = "utf-8"
        # 解析html
        html = BeautifulSoup(res.text, "html.parser")
        log("<--请求套图首页完成，用时%s秒" % (round(time.time() - start_time, 3)))
        with open("debug.html", "w", encoding="utf-8") as f:
            f.write(res.text)
        # 对doc进行分析，判断是否有效
        if not analysis(html):
            return

        # 提取图片总数
        temp1 = html.select(".main-wrap .pt-2 .row .col-md-6")[0].select("dd")
        img_total = int(re.findall(r"\d+", temp1[len(temp1) - 1].text)[0])
        gallery["total_count"] = img_total
        save_download_history()
        # 计算页数
        page_total = int(img_total / 10)
        b = img_total % 10
        if page_total == 0:
            page_total = 1
        if b > 0:
            page_total = page_total + 1
        log("共%s页，%s张图片" % (page_total, img_total))

        # 开始下载第一页的图片
        log("开始下载第%s/%s页" % (1, page_total))
        img_links = get_link(html)
        download_img_manager(img_links)
        log("第%s/%s页下载完成" % (1, page_total))
        # 下载剩余页面
        for page_index in range(int(page_total)):
            # 跳过第一页
            if page_index == 0:
                continue
            url = page_url + "&page=" + str(page_index + 1)
            download_other_page(url, page_index + 1, page_total)

    except Exception as e:
        print(e)
        log("请求套图首页出错，用时%s秒" % (round(time.time() - start_time, 3)))
        return False


def start():
    global headers
    global download_history
    global gallery_fold
    global gallery

    # with open(p("cookie.txt"), "r") as f:
    #     headers["cookie"] = f.read()
    readCookies()
    headers["cookie"] = toCookieString(["cf_clearance", "_gid", "_ga", "_ga_170M3FX3HZ",'frontend','frontend-rmu','frontend-rmt'])
    with open(p("download_history.json"), "r", encoding="utf-8") as f:
        download_history = json.load(f)

    girl, gallery = register()
    # 检查图集是否已下载完成
    if (not gallery["total_count"] == 0) and gallery["total_count"] == gallery[
        "download_count"
    ]:
        return log("{%s}%s已下载完成，无需重复下载" % (girl_name, gallery_name))
    log("------------开始下载------------")
    log("模特：%s" % (girl_name))
    log("套图：%s" % (gallery_name))
    # 创建文件夹
    model_fold = p("img/" + girl_name)
    if not os.path.exists(model_fold):
        os.mkdir(model_fold)
        log("创建模特文件夹:%s" % (girl_name))
    gallery_fold = os.path.join(model_fold, gallery_name)
    if not os.path.exists(gallery_fold):
        os.mkdir(gallery_fold)
        log("创建套图文件夹:%s" % (gallery_name))

    # 下载页面，分析页数和图片总数量
    download_first_page()


if __name__ == "__main__":
    start()
