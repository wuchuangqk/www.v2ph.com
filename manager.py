"""
下载记录
"""

import json
import os

from tools.util import now, p
from util import log, find

record_path = p("download.json")
save_path = 'img'

class Manager:
    def __init__(self, model, album):
        self._model = None
        self._album = None
        with open(record_path, "r", encoding="utf-8") as f:
            self._history = json.load(f)
        self._create(model, album)

    def _makedir(self, name):
        fold = p(f'{save_path}/{name}')
        if not os.path.exists(fold):
            os.mkdir(fold)
        
    def _save_history(self):
        """写入下载记录"""
        with open(record_path, "w", encoding="utf-8") as f:
            json.dump(self._history, f, indent=2, ensure_ascii=False)

    def _create(self, girl_name, gallery_name):
        """初始化模特和专辑"""
        album_template = {
            "name": gallery_name,
            "download_date": now(),
            "finish_date": None,
            "total_count": 0,
            "download_count": 0,
        }
        self._model = find(self._history, "name", girl_name)
        if self._model == None:
            log(f"新建模特：{girl_name}")
            log(f"新建专辑：《{gallery_name}》")
            self._album = album_template
            self._model = {
                "name": girl_name,
                "download_date": now(),
                "galleries": [self._album],
            }
            self._history.append(self._model)
            self._save_history()
            self._makedir(girl_name)
            self._makedir(f'{girl_name}/{gallery_name}')
        else:
            self._album = find(self._model["galleries"], "name", gallery_name)
            if self._album == None:
                log(f"新建专辑：《{gallery_name}》")
                self._album = album_template
                self._model["galleries"].append(self._album)
                self._save_history()
                self._makedir(f'{girl_name}/{gallery_name}')

    def save(self, name, binary):
        img = p(f'{save_path}/{self._model['name']}/{self._album['name']}/{name}')
        with open(img, "wb") as f:
            f.write(binary)
        self._album["download_count"] = self._album["download_count"] + 1
        if self._album["download_count"] == self._album["total_count"]:
            self._album["finish_date"] = now()
        self._save_history()

    def show_status(self):
        """专辑的下载状态"""
        is_all_downloaded = self._album["download_count"] == self._album["total_count"]
        is_download = self._album["total_count"] != 0 and is_all_downloaded
        status = "已完成" if is_download else "未完成"
        log(f'进度：{self._album["download_count"]}/{self._album["total_count"]}')
        log(f"状态：{status}")
        log(f'下载时间：{self._album["download_date"]}')
        log(f'完成时间：{self._album["finish_date"]}')

    def is_finish(self):
        """专辑是否已下载完成"""
        return self._album["finish_date"] != None

    def set_album_total(self, total):
        self._album['total_count'] = total
        self._save_history()
    
    def get_album_total(self):
        return self._album['total_count']