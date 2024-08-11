import os
from time import sleep
from typing import Any, Iterable
import scrapy, json, gzip
from io import BytesIO
from scrapy.http import Response
from wallpaper.items import WallpaperItem
# from selenium import webdriver
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class MainSpider(scrapy.Spider):
    name = "main"
    
    driver = None
    domain = "https://haowallpaper.com"
    url_template = "https://haowallpaper.com/?page={}"
    cur_page, max_page = 1, 1
    start_urls = [url_template.format(cur_page)]

    cookies = {
        "userData": r"%7B%22code%22%3A%221822187946820800513%22%2C%22userName%22%3A%22%E4%BB%87%E5%BF%A0%E9%AA%8F%22%2C%22userImg%22%3A%2215346357045202240%22%2C%22token%22%3A%22861AE98F94E2782BAAD70906CB17DEDC%22%7D",
    }

    def __init__(self):
        edge_driver_path = r"C:\QZJ_APP\edgedriver-win64\msedgedriver.exe"
        service = Service(executable_path=edge_driver_path)
        # 创建 EdgeOptions 对象并设置无头模式
        options = Options()
        # options.add_argument('--headless')
        # options.add_argument('--disable-gpu') 
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])

        self.driver = webdriver.Edge(service=service, options=options)
        self.driver.maximize_window()
        self.driver.get(self.domain)
        for k, v in self.cookies.items():
            self.driver.add_cookie({"name": k, "value": v, "domain": "haowallpaper.com"})
        print("Driver initialized")

    def start_requests(self):
        # 携带相同cookiejar值的请求会共享cookie
        yield scrapy.Request(self.url_template.format(self.cur_page), callback=self.parse, meta={"cookiejar": 1}, cookies=self.cookies)

    def show_args(self, response: Response):
        print("URL:", response.url)
        print("Status Code:", response.status)
        print("Headers:", response.headers)
        request = response.request
        print("Request URL:", request.url)
        print("Request Method:", request.method)
        print("Request Headers:", dict(request.headers))
        print("Request Body:", request.body.decode('utf-8') if request.body else 'No body')
        print("Request Cookies:", request.cookies)
        print("Request Meta:", request.meta)
    
    def raw_img_parse(self, response):
        img_path = response.request.url
        try:
            # get cover image
            ex = '//img[@id="imgLoad"]'
            cover = response.xpath(ex)
            name = cover.xpath('./@alt').extract()[0]
            cover_path = cover.xpath('./@src').extract()[0]
            item = WallpaperItem()
            item["path"] = cover_path
            item["name"] = name
            item["cid"] = 0
            yield item

            # get raw image
            self.driver.get(img_path)
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/main/div[3]/div/div/div[1]/div[2]/div[2]/div[1]'))
            )
            element.click()
            sleep(1)
            for request in self.driver.requests:
                target = "https://haowallpaper.com/link/common/file/getFileUrlName"
                if request.response and request.url.startswith(target):
                    response_body = request.response.body
                    # 尝试解压缩数据
                    if request.response.headers.get('Content-Encoding') == 'gzip':
                        with gzip.GzipFile(fileobj=BytesIO(response_body)) as gz:
                            body = gz.read().decode('utf-8')
                    else:
                        body = response_body.decode('utf-8')
                    
                    # 解析 JSON 数据
                    data = json.loads(body)
                    file_url = data.get("data")
                    if not file_url: file_url = {"url": cover_path}
                    file_url = file_url.get("url")
                    print("Extracted URL: ", file_url)
                    yield scrapy.Request(file_url, callback=self.save_image, meta={'name': name})

        except Exception as e:
            import traceback
            print(e)
            print(traceback.format_exc())

    def save_image(self, response):
        name = response.meta['name']
        directory = './raw'
        if not os.path.exists(directory):
            os.makedirs(directory)
        file_path = os.path.join(directory, f'{name}.jpg')
        try:
            with open(file_path, 'wb') as f:
                f.write(response.body)
        except Exception as e:
            print(f"Failed to save image {name}: {e}")

    def parse(self, response: Response):
        # if self.cur_page == 1:
        #     self.show_args(response)
        print("Paring url: ", response.url)

        try:
            ex = '//div[@class="homeContainer"]/div/div[1]/div[2]/a/@href'
            img_list = response.xpath(ex)

            print("number of images: ", len(img_list))
            for img in img_list:
                img_path = self.domain + img.extract()
                yield scrapy.Request(img_path, callback=self.raw_img_parse, meta={"cookiejar": response.meta["cookiejar"]})

            if self.cur_page < self.max_page:
                self.cur_page += 1
                yield scrapy.Request(self.url_template.format(self.cur_page), callback=self.parse, meta={"cookiejar": response.meta["cookiejar"]})

        except Exception as e:
            import traceback
            print(e)
            print(traceback.format_exc())
            
    def closed(self, reason):
        self.driver.quit()
        print("Driver closed")