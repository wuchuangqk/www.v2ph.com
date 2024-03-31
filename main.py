from manager import AlbumDownloader

if __name__ == "__main__":
    model = "鱼子酱fish"
    album = "鱼子酱Fish – 内购无水印 NO.4102 寂寞旅人咖啡馆"
    url = "https://www.v2ph.com/album/a877775z.html"
    downloader = AlbumDownloader(model, album, url)
    downloader.start()
