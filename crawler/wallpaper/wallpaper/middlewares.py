# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter
import scrapy

class WallpaperDownloaderMiddleware:

    def process_request(self, request: scrapy.Request, spider):
        # cookies = {
        #     "userData": r"%7B%22code%22%3A%221822187946820800513%22%2C%22userName%22%3A%22%E4%BB%87%E5%BF%A0%E9%AA%8F%22%2C%22userImg%22%3A%2215346357045202240%22%2C%22token%22%3A%22861AE98F94E2782BAAD70906CB17DEDC%22%7D",
        # }
        # request.cookies.update(cookies)
        # 可以放在spider里面
        return None

    def process_response(self, request: scrapy.Request, response, spider):
        avatar = response.xpath('//div[@class="topDiv"]/img/@src')
        print("Avatar path: ", avatar[0].extract())
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass
