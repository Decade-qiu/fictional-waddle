# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import os
import aiofiles
import asyncio
from twisted.internet import defer
from itemadapter import ItemAdapter

class NovelPipeline:
    def open_spider(self, spider):
        self.novels = {}

    def close_spider(self, spider):
        novel_author = spider.novel_author
        if not os.path.exists(novel_author):
            os.mkdir(novel_author)

        for name, items in self.novels.items():
            file_name = os.path.join(novel_author, f"{name}.txt")
            sorted_chapters = sorted(items, key=lambda x: int(x['index']))
            self.write_to_file(file_name, sorted_chapters)

    def write_to_file(self, file_name, sorted_chapters):
        # async with aiofiles.open(file_name, 'w', encoding='utf-8') as f:
        with open(file_name, 'w', encoding='utf-8') as f:
            for chapter in sorted_chapters:
                # print(f"Writing {chapter['title']} - {chapter['index']}")
                content = f"{chapter['title']}\n{chapter['content']}\n\n"
                f.write(content)

    def process_item(self, item, spider):
        name = item['name']
        if name not in self.novels:
            self.novels[name] = []
        self.novels[name].append(item)
        length = len(self.novels[name])
        if length % 100 == 0:
            print(f"Processed {length} chapters for {name}")
        return item