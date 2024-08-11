import scrapy, re
from novel.items import NovelItem

class MainSpider(scrapy.Spider):
    name = "main"

    DOMAIN = "m.biquge365.net"
    INDEX = f"https://{DOMAIN}"
    SEARCH_URL = f"{INDEX}/waps.php"
    start_urls = [INDEX]

    novel_name, novel_author = "帝尊", "宅猪"

    def start_requests(self):
        data = {
            "s": self.novel_author,
            "submit": "",
        }
        request = scrapy.FormRequest(
            url=self.SEARCH_URL,
            formdata=data,
            callback=self.parse_search_results,
        )
        yield request
    
    def parse_search_results(self, response):
        novel_a_list = response.xpath("//ul/li/span/a")
        name, href = None, None
        for novel_a in novel_a_list:
            novel_name = novel_a.xpath("./text()").extract_first()
            novel_href = novel_a.xpath("./@href").extract_first()
            if novel_name == self.novel_name or name == None:
                name, href = novel_name, novel_href
            elif len(novel_name) < len(name):
                name, href = novel_name, novel_href
        href = f"{self.INDEX}/{href}"
        print(f"Found novel: {name}-{self.novel_author}:{href}")

        request = scrapy.Request(
            url=href,
            callback=self.parse_novel_catalog,
            meta={"page": 1},
        )
        yield request

    def parse_novel_catalog(self, response):
        if response.meta.get("page") == 1:
            pages = response.xpath("//*[@class='mululist']/div/text()")
            pages = pages.extract()[-1]
            last_page = re.findall(r"\d+", pages)[-1]
            print(f" Found {last_page} pages")
            for page in range(2, int(last_page)+1):
                url = f"{response.request.url[:-1]}_{page}/"
                request = scrapy.Request(
                    url=url,
                    callback=self.parse_novel_catalog,
                )
                yield request

        chapters = response.xpath("//*[@class='menu']/div[4]/div[2]/ul/li/a/@href")
        for chapter in chapters:
            url = f"{self.INDEX}{chapter}"
            request = scrapy.Request(
                url=url,
                callback=self.parse_novel_chapter,
            )
            yield request

    def parse_novel_chapter(self, response):
        title = response.xpath('//div[@class="biaoti"]/text()')
        title = title.extract_first().strip()
        title = re.sub(r'\s+', ' ', title)
        chapeter_num = re.findall(r"\d+", title)
        if len(chapeter_num) > 0:
            chapeter_num = int(chapeter_num[0])
        else:
            chapeter_num = 1e9
        content = response.xpath('//div[@id="txt"]/text()').extract()
        
        item = NovelItem()
        item["title"] = title
        item["index"] = chapeter_num
        item["content"] = "\t"+"\n".join(content).strip()
        yield item

    def parse(self, response):
        pass
