from scrapy.http.response import Response
import scrapy


class ExampleSpider(scrapy.Spider):
    name = "example"
    # allowed_domains = ["example.com"]
    start_urls = ["https://bj.58.com/ershoufang/"]

    def parse(self, response: Response):
        li_list = response.xpath('//h3/text()')
        print(li_list.extract())
