# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class WallpaperItem(scrapy.Item):
    # define the fields for your item here like:
    path = scrapy.Field()
    name = scrapy.Field()
    cid = scrapy.Field()