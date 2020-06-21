from reppy.robots import Robots
from requests_html import HTMLSession
from queue import Queue
import aiohttp
import asyncio
from lxml import html
from aiofile import AIOFile
from datetime import datetime

start_time = datetime.now()

#DOMAIN = 'jettools.ru'
#DOMAIN = 'sterbrust.com'
#DOMAIN = 'ultramedstom.ru'
DOMAIN = 'wikimetall.ru'

url = f'https://{DOMAIN}/'
robots = Robots.fetch(f'https://{DOMAIN}/robots.txt')


scaned_urls = set()

async def worker(qu):
    async with aiohttp.ClientSession() as session:
        while qu.qsize() > 0:
            u = await qu.get()

            try:
                async with session.get(u) as response:
                    code = await response.text(errors='replace')

                tree = html.fromstring(code)
                tree.make_links_absolute(url)
                links = tree.xpath('//a/@href')
                links = set(links)

                title = tree.xpath('//title/text()')[0]

                print (title)

                async with AIOFile ('t-co.csv', 'a') as f:
                    await f.write(f'{u}\t{title}\n')

                for link in links:
                    if not link.startswith(url):
                        continue
                    elif link in scaned_urls:
                        continue
                    else:
                        if robots.allowed(link, '*'):
                            scaned_urls.add(link)
                            await qu.put(link)
                            print('Queue on scaning:', qu.qsize())
                            print('Scaned URL:', len(scaned_urls))



            except Exception as e:
                print(type(e), e)

async def worker_without_robots(qu):
    pass



async def main():
    try:
        async with aiohttp.ClientSession() as session:
            response = await session.get(url)
            code = await response.text()

        tree = html.fromstring(code)
        tree.make_links_absolute(url)
        links = tree.xpath('//a/@href')
        links = set(links)

        

        qu = asyncio.Queue()
        tasks = []

        for link in links:
            #print(robots.allowed(link, '*'), link)
            if robots.allowed(link, '*'):
                if link.startswith(url):
                    scaned_urls.add(link)
                    await qu.put(link)
        print('Размер очереди:', qu.qsize())

        if qu.qsize() <= 1:
            for link in links:
                if link.startswith(url):
                    scaned_urls.add(link)
                    await qu.put(link)
            print('Размер очереди 2:', qu.qsize())
            for _ in range(2):
                task = asyncio.Task(worker(qu))
                tasks.append(task)
            await asyncio.gather(*tasks)
        
        for _ in range(20):
            task = asyncio.Task(worker(qu))
            tasks.append(task)
        await asyncio.gather(*tasks) 
        
    except Exception as e:
        print(type(e), e)
loop = asyncio.get_event_loop()
loop.run_until_complete(main())

print(datetime.now() - start_time)  




        
    #     session = HTMLSession()
    #     resp = session.get(url)
    #     for link in resp.html.absolute_links:
    #         if robots.allowed(link, '*'):
    #             qu.put(link)
    #             scaned_urls.add(link)
        
    #     if qu.qsize() > 0:
    #         tasks = []
    #         for _ in range(2):
    #             task = asyncio.Task(worker(qu))
    #             tasks.append(task)

    #             await asyncio.gather(*tasks)
    #         print('Размер очереди:', qu.qsize())

    #     else:
    #         for link in resp.html.absolute_links:
    #             qu.put(link)
    #             scaned_urls.add(link)
    #         tasks = []
    #         for _ in range(2):
    #             task = asyncio.Task(worker_without_robots(qu))
    #             tasks.append(task)
    #         await asyncio.gather(*tasks)
    #         print('Размер очереди 2:', qu.qsize())
    






    #print(link)

    #print(len(resp.html.absolute_links))
    # for s in robots.sitemaps:
    # 	print(s)



