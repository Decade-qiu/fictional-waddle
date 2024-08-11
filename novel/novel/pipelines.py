# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class NovelPipeline:
    def open_spider(self, spider):
        self.chapters = []
        self.length = 0

    def close_spider(self, spider):
        sorted_chapters = sorted(self.chapters, key=lambda x: x['index'])
        file_name = f"{spider.novel_name}_{spider.novel_author}.txt"
        with open(file_name, 'w', encoding='utf-8') as f:
            for chapter in sorted_chapters:
                f.write(f"{chapter['title']}\n{chapter['content']}\n\n")

    def process_item(self, item, spider):
        self.chapters.append(item)
        self.length += 1
        if self.length % 100 == 0:
            print(f"Processed {self.length} chapters")
        return item
