# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline
import scrapy


class WallpaperPipeline:
    fp = None

    def open_spider(self, spider):
        self.fp = open("wallpaper.txt", "w", encoding="utf-8")

    def process_item(self, item, spider):
        self.fp.write(f"{item['name']} - {item['path']}\n")
        return item
    
    def close_spider(self, spider):
        self.fp.close()

class ImgPipeline(ImagesPipeline):
    # num = 0

    # def open_spider(self, spider):
    #     self.spiderinfo = self.SpiderInfo(spider)
    #     self.num = 0
    
    def get_media_requests(self, item, info):
        yield scrapy.Request(item['path'])

    def file_path(self, request, response=None, info=None, *, item=None):
        return f"{item['name']}.jpg"
    
    def item_completed(self, results, item, info):
        return item