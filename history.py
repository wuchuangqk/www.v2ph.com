from util import log, find, p, now
import json
import os
from config import save_path

history_list = []
history_path = p("data/download.json")


def create_fold(_path):
    fold = p(f"{save_path}/{_path}")
    if not os.path.exists(fold):
        os.mkdir(fold)


def read_history():
    global history_list
    with open(history_path, "r", encoding="utf-8") as f:
        history_list = json.load(f)


def save_history():
    """写入下载记录"""
    with open(history_path, "w", encoding="utf-8") as f:
        json.dump(history_list, f, indent=2, ensure_ascii=False)


class Album:
    def __init__(self, model_name, album_name, url):
        self._model = None
        self._album = None
        self.model_name = model_name
        self.album_name = album_name
        self.is_finish = False
        self.donwload_count = 0
        self.total_count = 0
        self._create_archive(url)

    def _create_archive(self, url):
        """初始化模特和专辑"""
        global history_list
        album_template = {
            "name": self.album_name,
            "url": url,
            "download_date": now(),
            "finish_date": None,
            "total_count": 0,
            "download_count": 0,
        }
        self._model = find(history_list, "name", self.model_name)
        if self._model == None:
            log(f"新建模特：{self.model_name}")
            log(f"新建专辑：《{self.album_name}》")
            self._album = album_template
            self._model = {
                "name": self.model_name,
                "homepage": None,
                "download_date": now(),
                "galleries": [self._album],
            }
            history_list.append(self._model)
            save_history()
            create_fold(self.model_name)
            create_fold(f"{self.model_name}/{self.album_name}")
        else:
            self._album = find(self._model["galleries"], "name", self.album_name)
            if self._album == None:
                log(f"新建专辑：《{self.album_name}》")
                self._album = album_template
                self._model["galleries"].append(self._album)
                save_history()
                create_fold(f"{self.model_name}/{self.album_name}")

        is_all_downloaded = self._album["download_count"] == self._album["total_count"]
        self.is_finish = self._album["total_count"] != 0 and is_all_downloaded
        self.donwload_count = self._album["download_count"]
        self.total_count = self._album["total_count"]

    def show_status(self):
        """专辑的下载状态"""
        status = "已完成" if self.is_finish else "未完成"
        log(f"模特：{self.model_name}")
        log(f"专辑：《{self.album_name}》")
        log(f'进度：{self._album["download_count"]}/{self._album["total_count"]}')
        log(f"状态：{status}")
        log(f'下载时间：{self._album["download_date"]}')
        log(f'完成时间：{self._album["finish_date"]}')

    def set_album_total(self, total):
        self.total_count = total
        self._album["total_count"] = total
        save_history()

    def increment(self):
        """递增已下载的图片数量"""
        self._album["download_count"] = self._album["download_count"] + 1
        if self._album["download_count"] == self._album["total_count"]:
            self._album["finish_date"] = now()
        save_history()


def init():
    read_history()


init()
