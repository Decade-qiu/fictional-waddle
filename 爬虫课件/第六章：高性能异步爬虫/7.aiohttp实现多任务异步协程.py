import asyncio
import time
import aiohttp

start = time.time()

urls = ['http://127.0.0.1:5000/bobo' for _ in range(10)]

async def get_page(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            page_text = await response.text()
            print(page_text)

async def main():
    tasks = [asyncio.create_task(get_page(url)) for url in urls]
    await asyncio.wait(tasks)

# 使用 asyncio.run() 来运行主协程
asyncio.run(main())
# 串行请求
# for url in urls:
#     asyncio.run(get_page(url))

end = time.time()
print('总耗时:', end-start)