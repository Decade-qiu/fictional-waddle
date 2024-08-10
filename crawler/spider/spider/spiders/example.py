from scrapy.http.response import Response
import scrapy
from spider.items import SpiderItem


class ExampleSpider(scrapy.Spider):
    name = "example"
    # allowed_domains = ["example.com"]
    start_urls = ["https://bj.58.com/ershoufang/"]

    def parse(self, response: Response):
        name_list = response.xpath('//h3/text()')
        # print(name_list.extract())
        batch = 10
        for i in range(0, len(name_list), batch):
            name = name_list[i:i+batch]
            item = SpiderItem()
            item['houses'] = name.extract()
            yield item