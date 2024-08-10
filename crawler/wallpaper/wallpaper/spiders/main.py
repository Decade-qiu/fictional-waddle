import scrapy
from scrapy.http import Response
from wallpaper.items import WallpaperItem


class MainSpider(scrapy.Spider):
    name = "main"
    
    domain = "https://haowallpaper.com"
    url_template = "https://haowallpaper.com/?page={}"
    cur_page, max_page = 1, 2
    start_urls = [url_template.format(cur_page)]

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

    def img_parse(self, response):
        try:
            ex = '//img[@id="imgLoad"]'
            cover = response.xpath(ex)

            for img_el in cover:
                path = img_el.xpath('./@src').extract()
                name = img_el.xpath('./@alt').extract()
                item = WallpaperItem()
                item["path"] = path[0]
                item["name"] = name[0]
                yield item

        except Exception as e:
            import traceback
            print(e)
            print(traceback.format_exc())

    def parse(self, response):
        # if self.cur_page == 1:
        #     self.show_args(response)
        print("Paring url: ", response.url)

        try:
            ex = '//div[@class="homeContainer"]/div/div[1]/div[2]/a/@href'
            img_list = response.xpath(ex)

            print("number of images: ", len(img_list))
            for img in img_list:
                img_path = self.domain + img.extract()
                yield scrapy.Request(img_path, callback=self.img_parse)

            if self.cur_page < self.max_page:
                self.cur_page += 1
                yield scrapy.Request(self.url_template.format(self.cur_page), callback=self.parse)

        except Exception as e:
            import traceback
            print(e)
            print(traceback.format_exc())