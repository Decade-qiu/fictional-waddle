import time
import scrapy, re
from novel.items import NovelItem

class MainSpider(scrapy.Spider):
    name = "main"

    DOMAIN = "m.biquge365.net"
    INDEX = f"https://{DOMAIN}"
    SEARCH_URL = f"{INDEX}/waps.php"
    start_urls = [INDEX]

    MAX_CHAPTERS_PER_PAGE = 100
    novel_name, novel_author = ".+", "宅猪"

    process_time = 0

    def __init__(self, name = None, **kwargs):
        super().__init__(name, **kwargs)
        self.process_time = time.time()

    def closed(self, reason):
        print(f"Process time: {time.time()-self.process_time:.2f}s")

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
        novel_list = []
        for novel_a in novel_a_list:
            novel_name = novel_a.xpath("./text()").extract_first()
            novel_href = novel_a.xpath("./@href").extract_first()
            if re.match(self.novel_name, novel_name):
                novel_list.append((novel_name, novel_href))

        for name, href in novel_list:
            href = f"{self.INDEX}/{href}"
            print(f"Found novel: {name}-{self.novel_author}:{href}")

            request = scrapy.Request(
                url=href,
                callback=self.parse_novel_catalog,
                meta={"page": 1, "name": name},
            )
            yield request

    def parse_novel_catalog(self, response):
        name = response.meta.get("name")
        cur_page = response.meta.get("page")
        if cur_page == 1:
            pages = response.xpath("//*[@class='mululist']/div/text()")
            pages = pages.extract()[-1]
            last_page = re.findall(r"\d+", pages)[-1]
            print(f" {name} has {last_page} pages")
            for page in range(2, int(last_page)+1):
                url = f"{response.request.url[:-1]}_{page}/"
                request = scrapy.Request(
                    url=url,
                    callback=self.parse_novel_catalog,
                    meta={"page": page, "name": name},
                )
                yield request

        chapters = response.xpath("//*[@class='menu']/div[4]/div[2]/ul/li/a/@href")
        for idx, chapter in enumerate(chapters):
            url = f"{self.INDEX}{chapter}"
            request = scrapy.Request(
                url=url,
                callback=self.parse_novel_chapter,
                meta={"name": name, "index": cur_page*self.MAX_CHAPTERS_PER_PAGE+idx},
            )
            yield request

    def parse_novel_chapter(self, response):
        title = response.xpath('//div[@class="biaoti"]/text()')
        title = title.extract_first().strip()
        title = re.sub(r'\s+', ' ', title)
        content = response.xpath('//div[@id="txt"]/text()').extract()
        
        item = NovelItem()
        item["name"] = response.meta.get("name")
        item["title"] = title
        item["index"] = response.meta.get("index")
        item["content"] = "\t"+"\n".join(content).strip()
        yield item

    def parse(self, response):
        pass

if __name__ == "__main__":
    xxx = 111
    def sub_generator():
        global xxx
        xxx += 1
        yield 'a'
        yield 'b'
        yield 'c'
        xxx += 1

    def main_generator():
        print(xxx)
        yield from sub_generator()
        print(xxx)
        yield 'd'
        yield from sub_generator()
        print(xxx)

    gen = main_generator()
    for value in gen:
        print(value)