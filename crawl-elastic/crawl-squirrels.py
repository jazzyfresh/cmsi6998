### NOTE: Required downgrading of sdks to work with Elasticsearch OSS
###     pip install --force-reinstall -v "numpy==1.26.4"
###     pip install --force-reinstall -v "elasticsearch==7.13.0"
### https://stackoverflow.com/questions/68762774/elasticsearchunsupportedproducterror-the-client-noticed-that-the-server-is-no
### https://stackoverflow.com/questions/78348773/how-to-resolve-np-float-was-removed-in-the-numpy-2-0-release-use-np-float64

import pandas
from elasticsearch import Elasticsearch


def write_to_elastic(es, index, document):
    es.index(index=index, body=document)


## Initialize Elasticsearch ##
# connecting to local elastic cluster
username = "elastic"
password = "elastic"

es = Elasticsearch(
    "http://localhost:9200",
    basic_auth=(username, password)
)

# verify connection
# print(es.info())


## Initialize Squirrels Elastic Index ##

# read squirrel data from file
df = pandas.read_csv("nyc_squirrels.csv")
# print(df)

# write each squirrel record as an elasticsearch document
squirrels = df.to_dict("records")
print("Writing squirrels to elasticsearch...", end="")
for squirrel in squirrels:
    write_to_elastic(es, "squirrels", squirrel)
    print(".", end="")
print("")
print(f"{len(squirrels)} written to elasticsearch.")
