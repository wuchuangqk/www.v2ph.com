import cloudscraper

scraper = cloudscraper.create_scraper(delay=10)
url = "https://cdn.v2ph.com/photos/3XZRcX3PXr8qpa3K.jpg"
headers = {
    "cookie": "cf_clearance=0gmnQRIqFpnWSSZI2cNbsC_67PoCdoEJxlOPX2EPT2U-1691043508-0-1-3f22da01.a4391551.682385e1-250.2.1691043508; _gid=GA1.2.1037383153.1691043511; _gat_UA-140713725-1=1; _ga_170M3FX3HZ=GS1.1.1691043512.1.1.1691043515.57.0.0; _ga=GA1.1.1256903320.1691043511",
    "referer": "https://www.v2ph.com/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.188",
}
res = scraper.get(url, headers=headers, timeout=(6.05, 30), allow_redirects=False)
with open("tset.jpg", "wb") as f:
    f.write(res.content)
