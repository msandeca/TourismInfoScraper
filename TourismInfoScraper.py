#!/usr/bin/env python
# coding: utf-8

# In[417]:


import urllib.request
##import urlparse


# In[418]:


def download(url, user_agent='msc', num_retries=2):
    """Download function that includes user agent support"""
    print ('Downloading:', url)
    headers = {'User-agent': user_agent}
    request = urllib.request.Request(url, headers=headers)
    try:
        html = urllib.request.urlopen(request).read()
    except urllib.request.URLError as e:
        print ('Downloading:', e.reason)
        html = None
        if num_retries > 0:
            if hasattr(e, 'code') and 500 <= e.code < 600:
                # retry 5XX HTTP errors
                html = download(url, user_agent, num_retries-1)
    return html

    


# In[419]:


import itertools


# In[420]:


def iteration():
    max_errors = 5 # maximum number of consecutive download errors allowed
    num_errors = 0 # current number of consecutive download errors
    for page in itertools.count(1):
        url = 'http://example.webscraping.com/view/-{}'.format(page)
        html = download(url)
        if html is None:
            # received an error trying to download this webpage
            num_errors += 1
            if num_errors == max_errors:
                # reached maximum amount of errors in a row so exit
                break
            # so assume have reached the last country ID and can stop downloading
        else:
            # success - can scrape the result
            # ...
            num_errors = 0


# In[421]:


import urllib.robotparser as robotparser
import urllib.parse as parse


# In[422]:


def get_robots(url):
    """Initialize robots parser for this domain
    """
    rp = robotparser.RobotFileParser()
    rp.set_url(parse.urljoin(url, '/robots.txt'))
    rp.read()
    return rp


# In[423]:


from datetime import datetime


# In[424]:


class Throttle:
    """Throttle downloading by sleeping between requests to same domain
    """
    def __init__(self, delay):
        # amount of delay between downloads for each domain
        self.delay = delay
        # timestamp of when a domain was last accessed
        self.domains = {}
        
    def wait(self, url):
        domain = parse.urlparse(url).netloc
        last_accessed = self.domains.get(domain)

        if self.delay > 0 and last_accessed is not None:
            sleep_secs = self.delay - (datetime.now() - last_accessed).seconds
            if sleep_secs > 0:
                time.sleep(sleep_secs)
        self.domains[domain] = datetime.now()


# In[425]:


import re


# In[426]:


def get_links(html):
    """Return a list of links from html 
    """
    # a regular expression to extract all links from the webpage
    webpage_regex = re.compile('<a[^>]+href=["\'](.*?)["\']', re.IGNORECASE)
    # list of all links from the webpage
    #print(links)
    #return links
    htmltext = html.decode('utf-8')
    return webpage_regex.findall(htmltext)


# In[427]:


def normalize(seed_url, link):
    """Normalize this URL by removing hash and adding domain
    """
    link, _ = parse.urldefrag(link) # remove hash to avoid duplicates
    return parse.urljoin(seed_url, link)


# In[428]:


from urllib.parse import urlparse


# In[429]:


def same_domain(url1, url2):
    """Return True if both URL's belong to same domain
    """
    return urlparse(url1).netloc == urlparse(url2).netloc


# In[430]:


import os


# In[431]:


def link_crawler(seed_url, link_regex=None, delay=5, max_depth=-1, max_urls=-1, headers=None, user_agent='Student', proxy=None, num_retries=1):
    """Crawl from the given seed URL following links matched by link_regex
    """
    # the queue of URL's that still need to be crawled
    crawl_queue = queue.deque([seed_url])
    # the URL's that have been seen and at what depth
    seen = {seed_url: 0}
    # track how many URL's have been downloaded
    num_urls = 0
    rp = get_robots(seed_url)
    throttle = Throttle(delay)
    headers = headers or {}
    if user_agent:
        headers['User-agent'] = user_agent
    
    #Current directory where is located the script
    
    #currentDir = os.path.dirname(__file__)
    #filename = "TourismInfo.csv"
    #filePath = os.path.join(currentDir, filename)
    
    filePath = os.path.join(os.getcwd(), "TourismInfo.csv")
    
    ListaActividades = []
    cabecera=["Titulo", "Idioma", "Duración", "Puntuación"]
    ListaActividades.append(cabecera)
    
    while crawl_queue:
        url = crawl_queue.pop()

        #print('url:', url)
        # check url passes robots.txt restrictions
        if rp.can_fetch(user_agent, url):
            throttle.wait(url)
                   
            html = download(url, user_agent, num_retries)
            
            #print(url)
            #if re.search(r'/s/\b[\D]', ciudad, url) and not re.search('opiniones', url):
            if re.search(r'/sevilla/\b[\D]', url) and not re.search('opiniones', url): 
                #Se trata de una página que no es de enlace /número ni es de opiniones
                ListaActividades.append(scrape(html))
            
            links = []

            depth = seen[url]
            if depth != max_depth:
                # can still crawl further
                if link_regex:
                    # filter for links matching our regular expression
                    links.extend(link for link in get_links(html) if re.search(link_regex, link)
                                   and not re.search('opiniones', link))

                for link in links:
                    link = normalize(seed_url, link)
                    # check whether already crawled this link
                    if link not in seen:
                        seen[link] = depth + 1
                        # check link is within same domain
                        if same_domain(seed_url, link):
                            # success! add this new link to queue
                            crawl_queue.append(link)

            # check whether have reached downloaded maximum
            num_urls += 1
            if num_urls == max_urls:
                break
    
        else:
            print('Blocked by robots.txt:', url)
        
    #Procedemos a guardar el listado de actividades en un fichero CSV
    with open(filePath, 'w', newline='') as csvFile:
        writer = csv.writer(csvFile)
        for act in ListaActividades:
            writer.writerow(act)
    
    


# In[432]:


import queue as queue


# In[433]:


from bs4 import BeautifulSoup


# In[434]:


def scrape(html):
    soup = BeautifulSoup(html)
    
    #Titulo
    try:
        div = soup.find(attrs={'class':'a-title-activity'}) 
        titulo = div.text 
    except:
        titulo = 'sin titulo'
    
    #Idioma
    try:
        div = soup.find(attrs={'m-activity-detail m-activity-detail--language'})
        idioma = div.h3.img['alt']
    except:
        idioma = 'sin idioma'
    
    #Duración
    try:
        div = soup.find(attrs={'class':'m-activity-detail m-activity-detail--duration'}) 
        duracion = div.p.text  
    except:
        duracion = 'sin duracion'
        
    #Puntuación
    try:
        div = soup.find(attrs={'o-rating__title'})
        punt = div.text
    except:
        punt = 'sin puntuacion'
    
    
    actividad=[]
    actividad = [titulo, idioma, duracion, punt]
    
    #print(actividad)
    return actividad


# In[435]:


if __name__ == '__main__':
    #html = download('https://www.civitatis.com/es/sevilla/excursion-tanger/')
    #print (scrape(html))
    #link_crawler('https://www.civitatis.com/es/sevilla/', 'es/sevilla/', delay=0, num_retries=1, max_depth=2, user_agent='StudentCrawler')
    None
    


# In[436]:


if __name__ == '__main__':
    ciudad = 'sevilla'
    #link_crawler(ciudad, 'https://www.civitatis.com/es/%s/' % ciudad, 'es/%s/' % ciudad, delay=0, num_retries=1, max_depth=1, user_agent='StudentCrawler')
    link_crawler('https://www.civitatis.com/es/%s/' % ciudad, 'es/%s/' % ciudad, delay=0, num_retries=1, max_depth=4, user_agent='StudentCrawler')


# In[ ]:




