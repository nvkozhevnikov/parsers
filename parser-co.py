import aiohttp
import asyncio
from lxml import html
from aiofile import AIOFile
from datetime import datetime
from reppy.robots import Robots

start_time = datetime.now()


url = 'https://rustan.ru/'
scaned_urls = set()

async def worker(q):
    async with aiohttp.ClientSession() as session:
        while q.qsize() > 0:
            u = await q.get()
            try:
                async with session.get(u) as response:
                    code = await response.text()

                tree = html.fromstring(code)
                tree.make_links_absolute(url)
                links = tree.xpath('//a/@href')
                links = set(links)

                title = tree.xpath('//title/text()')[0]

                print (title)

                #async with AIOFile ('t-co.csv', 'a', encoding="utf8") as f:
                	#await f.write(f'{u}\t{title}\n')

                for link in links:
                    if not link.startswith(url):
                        continue
                    elif link in scaned_urls:
                        continue
                    else:
                        scaned_urls.add(link)
                        await q.put(link)
            
            except Exception as e:
                print(type(e), e)



async def main():
    async with aiohttp.ClientSession() as session:
        response = await session.get(url)
        code = await response.text()
    tree = html.fromstring(code)
    tree.make_links_absolute(url)
    links = tree.xpath('//a/@href')
    links = set(links)

    qu = asyncio.Queue()

    for link in links:
    	if link.startswith(url):
    		scaned_urls.add(link)
    		await qu.put(link)
    #print(qu.qsize())

    tasks = []
    for _ in range(2):
        task = asyncio.Task(worker(qu))
        tasks.append(task)

    await asyncio.gather(*tasks)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())

print(datetime.now() - start_time)
	