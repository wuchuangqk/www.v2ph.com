from statistics import mode
from bs4 import BeautifulSoup
import requests
import os
from datetime import datetime
import time
import json,sys,os
import cloudscraper

def p(url):
    return os.path.join(sys.path[0], url)

scraper = cloudscraper.create_scraper(delay=10)
# 域名
host = "https://www.v2ph.com"
# 所有账户
account = []
# 下载记录
download_history = []

# 请求头
# headers = {"cookie": "", "referer": "https://www.v2ph.com/", "user-agent": ""}
headers = {
    "cookie": "frontend=cbe602772eb5083bf4a584a06d90d3a6; _gid=GA1.2.1037383153.1691043511; frontend-rmu=C3lcYeEoS5er8yWMIBucxy3zVYmCqw%3D%3D; frontend-rmt=tfiFLu1MQtqUq5ysTXwTpgCUBaMQm83p5MYkAzsaWO7Ys96qmwfIcbMCEd7WiFFj; cf_chl_2=5f54cf4b433dc2f; _ga_170M3FX3HZ=GS1.1.1691047233.2.1.1691049255.43.0.0; cf_clearance=EQm5jvwwYKdHsPWxakQtljeEDnoPw1bJgHZftz4996A-1691049256-0-1-3f22da01.6f4c090f.682385e1-250.2.1691049256; _ga=GA1.2.1256903320.1691043511; _gat_UA-140713725-1=1",
    "referer": "https://www.v2ph.com/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.188",
}
gat_ua = "_gat_UA-140713725-1=1"
user_agent = {
    "edge": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.188",
    "chrome": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 "
    "Safari/537.36",
}
# 下载记录
gallery_data = []
# 账户
user_data = {}


def dl_html(url):
    set_headers()
    start_time = time.time()
    try:
        # 发出请求
        # log(
        #     "请求地址：%s，使用账号：%s的cookie，本日剩余访问次数：%s"
        #     % (url, user_data["account"], user_data["visit_times"])
        # )
        res = scraper.get(
            url, headers=headers, timeout=(6.05, 30), allow_redirects=False
        )
        # 重定向
        if res.status_code == 302:
            return dl_html(host + res.headers["location"])
        # 设置编码
        res.encoding = "utf8"
        print(res.text)
        # 解析HTML
        doc = BeautifulSoup(res.text, "html.parser")
        end_time = time.time()
        log("请求地址：%s，用时%s秒" % (url, round(end_time - start_time, 3)))
        # 对doc进行分析，判断是否有效
        if not analysis(doc):
            return False
        # cookie可用，返回dom结构
        # print(doc)
        return doc
    except Exception as e:
        print(e)
        log("请求地址：%s 连接超时，用时：%s秒" % (url, round(time.time() - start_time, 3)))
        log(headers)
        return False


def dl_gallery_from_list(listUrl, path, model_name, user):
    global user_data
    user_data = user
    if not os.path.exists(path + model_name):
        log("为路径：%s创建目录" % path)
        os.mkdir(path)
    else:
        log("路径：%s已存在，跳过创建" % (path + model_name))
    log("开始下载页面：%s" % listUrl)
    doc = dl_html(listUrl)
    if not doc:
        return
    # 获取所有套图封面节点
    links = doc.select(".media-cover")
    index = 0
    length = len(links)
    log("log: 获取到%s个套图" % length)

    # 下载每一个套图
    for link in links:
        index = index + 1
        # 套图地址
        href = link["href"]
        # 套图名称
        name = link.select("img")[0]["alt"].strip()
        log("正在下载第%s/%s个套图(%s)" % (index, length, name))
        start_time = time.time()
        dl_gallery(host + href, name, path, model_name, user)
        end_time = time.time()
        log(
            "第%s/%s个套图(%s)下载完成，用时:%s秒"
            % (index, length, name, round(end_time - start_time, 3))
        )


def log(text):
    log_time = datetime.now().strftime("%H时%M分%S秒")
    print("log: %s %s" % (log_time, text))
    with open(p('../log.txt'), 'a', encoding='utf8') as f:
        f.write(time + ' ' + text + '\n')


# 检查cookie有效数


def check_effective():
    global account
    # 有效cookie
    effective = 0
    for item in account:
        if item["effective"] == 1:
            effective += 1
    return effective


def dl_gallery(url, girl_name, gallery_name):
    """
    下载图集
    url：图集地址
    name：图集名称
    path：下载路径
    """
    global user_data
    global gallery_data
    global download_history
    # user_data = account
    history = {
        'name': girl_name
    }

    girl_fold = p("../img/" + girl_name)
    if url.find("?hl=zh-Hans") == -1:
        url = url + "?hl=zh-Hans"

    # 检查是否创建了模特文件夹
    if not os.path.exists(girl_fold):
        log("为路径：%s创建目录" % girl_fold)
        os.mkdir(girl_fold)

    # 检查是否创建了图集文件夹
    gallery_fold = os.path.join(girl_fold, gallery_name)
    if os.path.exists(gallery_fold):
        # 查看是否是空文件夹，避免重复访问消耗次数
        files = os.listdir(gallery_fold)
        if len(files) == 0:
            log("套图名称：%s已存在，是空文件夹" % girl_name)
        else:
            log("套图名称：%s已下载完成，跳过下载" % girl_name)
            return
    else:
        log("为套图：%s创建文件夹" % girl_name)
        os.mkdir(gallery_fold)
    # 分析并下载第一页的图片
    doc = dl_html(url)
    if not doc:
        return
    # 提取总页数
    pagination = doc.select(".pagination .page-link")
    if len(pagination) == 0:
        log("套图(%s)需要开通VIP" % girl_name)
        return
    total_page = (
        pagination[len(pagination) - 1]["href"]
        .split("?")[1]
        .split("&")[0]
        .split("=")[1]
    )
    log("套图(%s) 共%s页" % (girl_name, total_page))
    log("下载第(%s/%s)页" % (1, total_page))
    dl_imgs(doc, gallery_fold)
    # 下载剩余图片
    for page_index in range(int(total_page)):
        # 跳过第一页
        if page_index == 0:
            continue
        log("正在下载第%s/%s页(%s)" % (page_index + 1, total_page, girl_name))
        doc = dl_html(url + "&page=" + str(page_index + 1))
        if not doc:
            return
        dl_imgs(doc, gallery_fold)
        log("第%s/%s页(%s)下载完成" % (page_index + 1, total_page, girl_name))
    # visit_times = user_data["visit_times"]
    # if visit_times > 0:
    #     user_data["visit_times"] = visit_times - 1
    # 添加到下载记录
    model = find_model(girl_name)
    if model:
        _gallery = find_gallery_by_model(girl_name, model)
        files = os.listdir(gallery_fold)
        if _gallery:
            # 更新图片数
            _gallery["count"] = len(files)
            _gallery["done"] = "yes" if len(files) > 0 else "no"
        else:
            # 新增图集
            model["count"] = model["count"] + 1
            model["gallery"].append(
                {
                    "girl_name": girl_name,
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "count": len(files),
                    "done": "yes" if len(files) > 0 else "no",
                }
            )
        save_gallery_data()


# 下载本页所有图片


def dl_imgs(doc, path):
    imgs = doc.select(".photos-list .album-photo img")
    index = 0
    length = len(imgs)
    log("获取到%s张图片" % length)
    for img in imgs:
        index += 1
        # 图片名称
        name = img["alt"] + ".jpg"
        _path = os.path.join(path, name)
        log("正在下载第%s/%s张图片(%s)" % (index, length, name))
        if os.path.exists(_path):
            log("第%s/%s张图片(%s)已下载，跳过此图片" % (index, length, name))
            continue
        start_time = time.time()
        src = img["data-src"]
        with open(_path, "wb") as f:
            try:
                # 设置超时时间(6.05=连接超时时间,30=读取超时时间)
                req = requests.get(src, headers=headers, timeout=(6.05, 30))
                f.write(req.content)
                end_time = time.time()
                size = os.path.getsize(_path) / (1024 * 1024)
                log(
                    "第%s/%s张图片(%s)下载完成，用时:%s秒，图片大小：%sMB"
                    % (
                        index,
                        length,
                        name,
                        round(end_time - start_time, 3),
                        round(size, 3),
                    )
                )
            except Exception as e:
                log(
                    "下载第%s/%s张图片(%s) 连接超时，用时：%s秒"
                    % (index, length, name, round(time.time() - start_time, 3))
                )


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


def mark_invalid(account_index):
    # 将账户的cookie标记为无效
    global account
    user_data["effective"] = 0
    with open(p("../account.json"), "w") as w:
        json.dump(account, w)
    log("账号：%s的cookie已被标记为无效" % user_data["account"])


def set_headers():
    global headers
    global user_data
    # cookie = user_data["cookie"]
    # if cookie.find(gat_ua) == -1:
    #     cookie = cookie + gat_ua
    # headers["cookie"] = cookie
    # headers["user-agent"] = user_agent[user_data["user_agent"]]


def get_visit_times(_account):
    global headers
    global user_data
    user_data = _account
    log("开始检查账户%s的可用次数" % _account["account"])
    try:
        set_headers()
        res = scraper.get(
            "https://www.v2ph.com/user/index", headers=headers, timeout=(6.05, 30)
        )
        # 设置编码
        res.encoding = "utf8"
        # 解析HTML
        doc = BeautifulSoup(res.text, "html.parser")
        if not analysis(doc):
            print(headers)
            return False
        print(res.text)
        print(doc)
        print(doc.select(".text-danger"))
        # span = doc.select(".text-danger")[0]
        # return span.text
    except Exception as e:
        print(e)
        log("检查账户%s的可用次数，连接超时" % _account["account"])
        return False


# 读取所有账户
def read_account():
    global account
    global user_data
    with open(p("../account.json"), "r") as f:
        account = json.load(f)
        user_data = account[0]
        # log('读取到%s个账户，开始分析账户本日可用访问次数' % (len(account)))
        # for item in account:
        #     times = get_visit_times(item)
        #     if not times:
        #         log('分析账户%s的可用次数失败' % item['account'])
        #     else:
        #         item['visit_times'] = int(times)
        #         log('账户%s的可用次数为%s' % (item['account'], item['visit_times']))
        # with open(p('../account.json'), 'w') as w:
        #     json.dump(account, w, indent=2)
        # account = account[4:]


def save_account(account):
    with open(p("../account.json"), "w") as w:
        json.dump(account, w, indent=2)


def gallery_exist(model_name, gallery_name):
    for model in gallery_data:
        if model["name"] == model_name:
            for gallery in model["gallery"]:
                if gallery["name"] == gallery_name:
                    return gallery
    return False


def read_gallery_data():
    """读取下载记录"""
    log("读取下载记录")
    global gallery_data
    with open(p("../gallery.json"), "r", encoding="utf-8") as r:
        gallery_data = json.load(r)
        log("下载记录读取完成")


def save_gallery_data():
    global gallery_data
    with open(p("../gallery.json"), "w", encoding="utf-8") as r:
        json.dump(gallery_data, r, indent=2, ensure_ascii=False)


def find_model(name):
    for m in gallery_data:
        if m["name"] == name:
            return m
    return False


def find_gallery_by_model(name, model):
    for item in model["gallery"]:
        if item["name"] == name:
            return item
    return False

def readLocalData():
    '''
    读取本地文件数据
    '''
    global download_history
    log("读取下载记录")
    with open(p("../download_history.json"), "r", encoding="utf-8") as r:
        download_history = json.load(r)
        log("下载记录读取完成")

# read_gallery_data()

if __name__ == "__main__":
    readLocalData()
    url = "https://www.v2ph.com/album/ax3e533z.html"
    dl_gallery(url=url, girl_name="小岚", gallery_name="淑女抬脚")
