#!/bin/bash

cd /Users/jdahilig/cmsi6998
source env/bin/activate
export ELASTIC_PASSWORD="elastic"
python crawl.py &> crawl.log
