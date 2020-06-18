from threading import Lock
from queue import Queue
from requests_html import HTMLSession
from concurrent.futures import ThreadPoolExecutor
from reppy.robots import Robots
from datetime import datetime
import time

start_time = datetime.now()



DOMAIN = 'ultramedstom.ru'
scaned_urls = set()
locker = Lock()

#robots = Robots.fetch(f'https://{DOMAIN}/robots.txt')

def worker(queue):
    session = HTMLSession()
    while True:
        if queue.qsize() == 0:
            sleep(10)
            if queue.qsize() == 0:
                break
        try:
            url = queue.get()
            #print ('Отправить запрос', url)
            resp = session.get(url)
            title = resp.html.xpath('//title/text()')[0].strip()
            #print(title)
            if DOMAIN in url:
                with locker:
                    with open ('t-th.csv', 'a') as f:
                       f.write(f'{url}\t{title}\n')
                print(title)
          
            for link in resp.html.absolute_links: 
                if link in scaned_urls:
                    continue
                elif DOMAIN not in link:
                    continue
                # else:
                # 	if robots.allowed(link, '*'):
                # 		queue.put(link)
                # 		with locker:
                # 			scaned_urls.add(link)
                else:
                    queue.put(link)
                    with locker:
                        scaned_urls.add(link)

        except Exception as e:
            print(type(e), e)
            


def main():
    qu = Queue()
    url = f'https://{DOMAIN}/'
    session = HTMLSession()
    resp = session.get(url)

    # for link in resp.html.absolute_links:
    # 	print(robots.allowed(link, '*'), link)
    # 	if robots.allowed(link, '*'):
    # 		qu.put(link)
    # 		scaned_urls.add(link)
    #print('Размер очереди:', qu.qsize())
    #print(link)

    for link in resp.html.absolute_links:
        qu.put(link)
        scaned_urls.add(link)

   
    with ThreadPoolExecutor(max_workers=20) as ex:
        for _ in range(20):
            ex.submit (worker, qu)
main() 

print(datetime.now() - start_time)  

