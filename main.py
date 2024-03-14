from manager import AlbumDownloader

if __name__ == "__main__":
    model = "鱼子酱fish"
    album = "姐妹花"
    url = "https://www.v2ph.com/album/z6e94o8a.html"
    downloader = AlbumDownloader(model, album, url)
    downloader.start()
