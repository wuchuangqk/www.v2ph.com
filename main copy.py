from lib.v2ph import dl_gallery, dl_gallery_from_list, get_visit_times, save_account
from datetime import datetime
from lib.util import p
import json

record = []
path = "img"
account = []


def read_account():
    global account
    with open(p("account.json"), "r") as f:
        account = json.load(f)
        print("读取到%s个账户" % len(account))


def get_account_by_name(name):
    for item in account:
        if item["account"] == name:
            return item
    return False


def check_account_times(name):
    global account
    """
    检查账号本日可用访问次数
    """
    item = get_account_by_name(name)
    if not item:
        print("没有找到账号%s" % name)
        return False
    times = get_visit_times(item)
    if not times:
        print("分析账户%s的可用次数失败" % item["account"])
        return False
    item["visit_times"] = int(times)
    print("账户%s的可用次数为%s" % (item["account"], item["visit_times"]))
    save_account(account)
    if item["visit_times"] == 0:
        print("该账号已用尽今日次数")
        return False
    return item


def print_record():
    """
    读取模特记录
    """
    global record

    with open(p("record.json"), "r", encoding="utf-8") as r:
        record = json.load(r)
        print(
            "选项     模特             模式            账号            地址                    记录日期"
        )
        for i, r in enumerate(record):
            mode = "套图合集" if r["mode"] == 1 else "单个套图"
            print(
                "%s       %s       %s      %s      %s      %s"
                % (i, r["name"], mode, r["account"], r["url"], r["record_date"])
            )


def start():
    print("读取账户")
    read_account()
    option = input("1、新模特 2、已记录模特")
    if option == "1":
        account_name = input("输入账号，如：love_0@qq.com => ").strip()
        # 分析账号可用访问次数
        user_data = check_account_times(account_name)
        if not user_data:
            return
        girl_name = input("输入模特名称，如：六味帝皇酱 => ").strip()
        mode = input("选择下载模式：1、套图合集 2、单个套图 no、退出 => ").strip()
        if mode == "1":
            url = input(
                "输入套图列表地址，如：https://www.v2ph.com/actor/364o89om.html?hl=zh-Hans => "
            ).strip()
            print(
                "模特名称：%s，下载路径%s，请求地址：%s"
                % (girl_name, path + girl_name, url)
            )
            ok = input("输入ok以确认 => ").strip()
            if ok == "ok":
                print("已启动下载程序：%s" % (datetime.now().strftime("%H时%M分%S秒")))
                dl_gallery_from_list(url, path, girl_name, user_data)
        elif mode == "2":
            url = input(
                "输入套图地址，如：https://www.v2ph.com/album/zo37594z.html?hl=zh-Hans => "
            ).strip()
            gallery = input("输入套图名称，如：六味帝皇酱 - 五一假日女友 => ").strip()
            print(
                "模特名称：%s，套图名称：%s，下载路径：%s，请求地址：%s"
                % (girl_name, gallery, path + girl_name, url)
            )
            ok = input("输入ok以确认 => ").strip()
            if ok == "ok":
                print("已启动下载程序：%s" % (datetime.now().strftime("%H时%M分%S秒")))
                dl_gallery(
                    url=url,
                    girl_name=girl_name,
                    gallery_name=gallery,
                    account=user_data,
                )
        elif mode == "test":
            dl_gallery_from_list(
                "https://www.v2ph.com/actor/nmxx879m.html?hl=zh-Hans", path + "豆瓣酱"
            )
        elif mode == "no":
            print("退出")
    elif option == "2":
        print_record()
        index = input("输入选项序号(no：退出)：=> ")
        if index == "no":
            return
        else:
            _index = int(index)
            girl_name = record[_index]["girl_name"]
            # 分析账号可用访问次数
            if not check_account_times(girl_name):
                return
            _mode = record[_index]["mode"]
            url = record[_index]["url"]
            gallery = record[_index]["gallery"]
            print(
                "模特名称：%s，套图名称：%s，下载路径：%s，请求地址：%s"
                % (girl_name, gallery, path + girl_name, url)
            )
            ok = input("输入ok以确认 => ").strip()
            if ok == "ok":
                print("已启动下载程序：%s" % (datetime.now().strftime("%H时%M分%S秒")))
                if _mode == 1:
                    dl_gallery_from_list(url, path + girl_name)
                elif _mode == 2:
                    dl_gallery(url, gallery, path + girl_name)


def test():
    print("读取账户")
    read_account()
    # 分析账号可用访问次数
    user_data = check_account_times("love_0@qq.com")
    if not user_data:
        return
    url = input("下载地址").strip()
    gallery = input("套图名称").strip()
    print("已启动下载程序：%s" % (datetime.now().strftime("%H时%M分%S秒")))
    dl_gallery(url, gallery, path, "米线线sama", user_data)


if __name__ == "__main__":
    start()
