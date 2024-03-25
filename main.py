from manager import AlbumDownloader

if __name__ == "__main__":
    model = "鱼子酱fish"
    album = "鱼子酱Fish – 内购无水印 小邹菊"
    url = "https://www.v2ph.com/album/z48xm5ez.html"
    downloader = AlbumDownloader(model, album, url)
    downloader.start()
