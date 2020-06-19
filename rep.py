from reppy.robots import Robots
from requests_html import HTMLSession
from queue import Queue

#DOMAIN = 'jettools.ru'
DOMAIN = 'sterbrust.com'

robots = Robots.fetch(f'https://{DOMAIN}/robots.txt')


scaned_urls = set()

def main():
    qu = Queue()
    url = f'https://{DOMAIN}/'
    session = HTMLSession()
    resp = session.get(url)
    for link in resp.html.absolute_links:
     	#print(robots.allowed(link, 'GMbot'), link)

        if robots.allowed(link, '*'):
            qu.put(link)
            scaned_urls.add(link)
    
    if qu.qsize() > 0:
    	#tasks = []
        # for _ in range(2):
        # 	task = asyncio.Task(worker(qu))
        # 	tasks.append(task)
        # await asyncio.gather(*tasks)
        print('Размер очереди:', qu.qsize())

    else:
        for link in resp.html.absolute_links:
            qu.put(link)
            scaned_urls.add(link)
        print('Размер очереди 2:', qu.qsize())






    #print(link)

    #print(len(resp.html.absolute_links))
    # for s in robots.sitemaps:
    # 	print(s)




main()