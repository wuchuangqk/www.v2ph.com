import os
import time
import json

path = 'cos/img/'
exclude = ['love']
gallery_data = []
with open('cos/gallery.json', 'r', encoding='utf-8') as r:
    gallery_data = json.load(r)


def find_model(name):
    for m in gallery_data:
        if m['name'] == name:
            return m
    return False


def find_gallery_by_model(name, model):
    for item in model['gallery']:
        if item['name'] == name:
            return item
    return False


# 模特
dirs = os.listdir(path)
for name in dirs:
    if name in exclude:
        continue
    # 文件夹创建时间
    t = os.path.getctime(path + name)
    date = time.strftime('%Y-%m-%d', time.localtime(t))
    # 套图
    gallerys = os.listdir(path + name)
    model = find_model(name)
    if not model:
        model = {'name': name, 'date': date,
                 'count': len(gallerys), 'gallery': []}
        gallery_data.append(model)
    else:
        # 更新套图数量
        model['count'] = len(gallerys)
    for galler in gallerys:
        # 图集下的所有图片
        if galler == 'desktop.ini':
            continue
        files = os.listdir(path + name + '/' + galler)
        t = os.path.getctime(path + name + '/' + galler)
        galler_date = time.strftime('%Y-%m-%d', time.localtime(t))
        _gallery = find_gallery_by_model(galler, model)
        if _gallery:
            # 更新图片数
            _gallery['count'] = len(files)
            _gallery['done'] = 'yes' if len(files) > 0 else 'no'
            continue
        # 新增图集
        model['gallery'].append({
            'name': galler,
            'date': galler_date,
            'count': len(files),
            'done': 'yes' if len(files) > 0 else 'no'
        })
with open('cos/gallery.json', 'w', encoding='utf-8') as r:
    json.dump(gallery_data, r, indent=2, ensure_ascii=False)
