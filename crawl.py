import os
import mechanicalsoup as ms
import redis
import configparser
from elasticsearch import Elasticsearch, helpers
from neo4j import GraphDatabase

class Neo4JConnector:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def add_links(self, page, links):
        with self.driver.session() as session: 
            session.execute_write(self._create_links, page, links)

    def flush_db(self):
        print("clearing graph db")
        with self.driver.session() as session: 
            session.execute_write(self._flush_db)
    
    @staticmethod
    def _create_links(tx, page, links):
        # because Redis stores strings as ByteStrings,
        # we must decode our url into a string of a specific encoding
        # for it to be valid JSON
        page = page.decode('utf-8')
        tx.run("CREATE (:Page { url: $page })", page=page)
        for link in links:
            tx.run("MATCH (p:Page) WHERE p.url = $page "
                   "CREATE (:Page { url: $link }) -[:LINKS_TO]-> (p)",
                   link=link, page=page)

    @staticmethod
    def _flush_db(tx):
        tx.run("MATCH (a) -[r]-> () DELETE a, r")
        tx.run("MATCH (a) DELETE a")




def write_to_elastic(es, url, html):
    # because Redis stores strings as ByteStrings,
    # we must decode our url into a string of a specific encoding
    # for it to be valid JSON
    url = url.decode('utf-8') 
    es.index(index='scrape', document={ 'url': url, 'html': html })

def crawl(browser, r, es, neo, url):
    # Download url
    print("Downloading url")
    browser.open(url)

    # Cache page to elasticsearch
    write_to_elastic(es, url, str(browser.page))

    # Parse for more urls
    print("Parsing for more links")
    a_tags = browser.page.find_all("a")
    hrefs = [ a.get("href") for a in a_tags ]

    # Do wikipedia specific URL filtering
    wikipedia_domain = "https://en.wikipedia.org"
    links = [ wikipedia_domain + a for a in hrefs if a and a.startswith("/wiki/") ]

    # Put urls in Redis queue
    # create a linked list in Redis, call it "links"
    print("Pushing links onto Redis")
    r.lpush("links", *links)

    # Add links to Neo4J graph
    # neo.add_links(url, links)

### MAIN ###

# Initialize Neo4j
neo = Neo4JConnector("bolt://localhost:7689", "neo4j", "db_is_awesom3")
neo.flush_db()

# Initialize Elasticsearch
# connecting to local elastic cluster
username = 'elastic'
password = os.getenv('ELASTIC_PASSWORD') # Value you set in the environment variable

es = Elasticsearch(
    "http://localhost:9200",
    basic_auth=(username, password)
)

# print(es.info())

# # connecting to elastic cloud
# es = Elasticsearch(
#   "https://a5bc75974ab14099ac0d65a603796367.us-west-1.aws.found.io:443",
#   api_key="U3Zna21aQUJsVkp6MUxEWlhXSzc6T2psQ0tDVG1RYkN1YTU0QWJpWDkxQQ=="
# )

# Initialize Redis
r = redis.Redis()
r.flushall()

# Initialize MechanicalSoup headless browser
browser = ms.StatefulBrowser()

# Add root url as the entrypoint to our crawl
start_url = "https://en.wikipedia.org/wiki/Redis"
r.lpush("links", start_url)

# Start crawl
while link := r.rpop("links"):
    crawl(browser, r, es, neo, link)

# Close connection to Neo4j
neo.close()
