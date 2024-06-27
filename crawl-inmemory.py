import requests
from bs4 import BeautifulSoup
#pip install bs4


# TODO: refactor url to href

# TODO: reducing the number of links to crawl through
#       by filtering more throroughly for links that will
#       more likely give us the right result

# TODO: use numpy for faster list ops, or even redis for the queue

# TODO: create one BS object and reuse

class WebCrawler:
    def __init__(self, start_url, target_url):
        self.target_url = target_url
        self.current_url = start_url
        self.queue = [start_url]
        # maintain a set of visited sites
        # to avoid crawling over itself
        self.visited = set()
        self.run()

    def get_all_links(self, href): 
        domain = "https://wikipedia.org"
        # downloading html using requests
        try:
            response = requests.get(domain + href)
            if response.status_code == 200: # 200 means success
                soup = BeautifulSoup(response.text, "html.parser")
                return soup.find_all("a")
                # sometimes soup returns a None, which causes an error
                # thats why in try catch
        except Exception:
            return []

    # run the whole thing
    def run(self):
        while self.queue != []:
            if self.current_url == self.target_url:
                print("target url is found")
                return
            else:
                self.current_url = self.queue.pop(0)
                # pop returns the item at the index 0
                # and removes the item from the list
                self.visited.add(self.current_url)
                self.crawl(self.current_url)
                # wiki/Title --> Title
                print(self.current_url.split("/")[-1])
        print("target url was never found :(")



    # look through all of the links and add to the queue
    def crawl(self, url):
        if url == None or url == "":
            return
        else: 
            links = self.get_all_links(url)
            if links != []:
                for link in links:
                    ref = link.get("href")
                    if self.filter(ref):
                        self.queue.append(ref)

    # TODO: have a filter set of strings
    def filter(self, ref):
        return (ref is not None and 
            ref not in self.queue and 
            ref not in self.visited and 
            ref.startswith("/wiki/") and 
            not ref.startswith("/wiki/File:") and
            not ref.startswith("/wiki/Wikipedia:") and
            not ref.startswith("/wiki/Help:") and
            not ref.startswith("/wiki/Portal:"))




WebCrawler("/wiki/Star_Wars", "/wiki/Pokemon")
