## Docker Compose
```
docker-compose up

# get all the docker containers and their ids
docker ps 

# connect a terminal session to the elasticsearch container
# as root user so you can install stuff
docker exec -u root -it <elastic_container_id> bash
```
### clear any existing containers
### if you do this, any ephemeral data will get wiped!
### make sure to persist your data (see below)
```
docker stop $(docker ps -aq)
docker rm $(docker ps -aq)
```

### make sure to set the elastic password environment variable in every new terminal!
```
export ELASTIC_PASSWORD="elastic"
export KIBANA_PASSWORD="kibana"

# double check that it worked
echo $ELASTIC_PASSWORD
echo $KIBANA_PASSWORD
```

### run your containers
```
docker run -p 127.0.0.1:9200:9200 -d --name elasticsearch --network elastic-net   -e ELASTIC_PASSWORD=$ELASTIC_PASSWORD   -e "discovery.type=single-node"   -e "xpack.security.http.ssl.enabled=false"   -e "xpack.license.self_generated.type=trial"   docker.elastic.co/elasticsearch/elasticsearch:8.14.2

docker run -p 127.0.0.1:5601:5601 -d --name kibana --network elastic-net   -e ELASTICSEARCH_URL=http://elasticsearch:9200   -e ELASTICSEARCH_HOSTS=http://elasticsearch:9200   -e ELASTICSEARCH_USERNAME=kibana_system   -e ELASTICSEARCH_PASSWORD=$KIBANA_PASSWORD   -e "xpack.security.enabled=false"   -e "xpack.license.self_generated.type=trial"   docker.elastic.co/kibana/kibana:8.14.2
```

### if your kibana is not yet ready, you can search using the commandline
```
export POST_TITLE="pokemon"
curl -u "elastic:elastic" -X GET "localhost:9200/scrape/_search?q=title:$POST_TITLE&pretty"
```


## persist data by mounting a volume
add the following flag into your docker run command for your elasticsearch container
replace `/Users/jdahilig/cmsi6998/data` with the global path of an existing `data/` directory
this is where all your data will be stored
```
-v /Users/jdahilig/cmsi6998/data:/usr/share/elasticsearch/data
```



