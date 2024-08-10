# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymysql


class SpiderPipeline:
    fp = None

    # 重写父类的一个方法：该方法只在开始爬虫的时候被调用一次
    def open_spider(self, spider):
        print('开始爬虫......')
        self.fp = open('./houses.txt', 'w', encoding='utf-8')

    # 专门用来处理item类型对象
    # 该方法可以接收爬虫文件提交过来的item对象
    # 该方法每接收到一个item就会被调用一次
    def process_item(self, item, spider):
        house = "\n".join(item['houses'])
        self.fp.write(house+'\n')
        # 传递给下一个即将被执行的管道类
        return item  

    def close_spider(self, spider):
        print('结束爬虫！')
        self.fp.close()

# 管道文件中一个管道类对应将一组数据存储到一个平台或者载体中
class MysqlPipeline(object):
    conn = None
    cursor = None

    def open_spider(self, spider):
        self.conn = pymysql.Connect(
            host='127.0.0.1', port=3306, user='root', password='root123', db='spider', charset='utf8')
        print('持久化存储开始......')

    def process_item(self, item, spider):
        self.cursor = self.conn.cursor()

        try:
            self.cursor.execute(f'insert into house values("{item["houses"]}")')
            self.conn.commit()
        except Exception as e:
            print(e)
            self.conn.rollback()

        return item

    def close_spider(self, spider):
        self.cursor.close()
        self.conn.close()
        print('持久化存储结束......')