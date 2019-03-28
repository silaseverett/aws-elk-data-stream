import webhoseio
import time
import re
from textblob import TextBlob
import datetime
import pytz
from dateutil import parser

from elasticsearch import Elasticsearch, RequestsHttpConnection
from elasticsearch.helpers import bulk
from elasticsearch.exceptions import ElasticsearchException
from requests_aws4auth import AWS4Auth
import boto3
import configwhose as cwh


def sentiment_analysis(web_doc):
    blob = TextBlob(web_doc['text'])
    sentiment_polarity = blob.sentiment.polarity
    if sentiment_polarity < 0:
        sentiment = "negative"
    elif sentiment_polarity <= 0.2:
                sentiment = "neutral"
    else:
        sentiment = "positive"
    return sentiment_polarity, sentiment
    
def get_web_doc(post):
    doc={}
    doc['id']=post['uuid']
    doc['author']=post['author']
    doc['text']=" ".join(post['text'].split()[:100])
    doc['published']=parser.parse(post['published']).replace(tzinfo=None) 
    doc['log_time']= datetime.datetime.now(datetime.timezone.utc) #parser.parse(post['published'])
    doc['language']=post['language']
    doc['url']=post['url']
    doc['facebook_likes']=post['thread']['social']['facebook']['likes']
    doc['facebook_shares']=post['thread']['social']['facebook']['shares']
    doc['polarity'],doc['sentiment']=sentiment_analysis(post)
    return doc

def check_indice_exists(index_name,es,mapping):
    
    if es.indices.exists(index_name):
        print ('index {} already exists'.format(index_name))
        try:
            es.indices.put_mapping(cwh.doc_type, cwh.doc_mapping, cwh.index_name)
        except ElasticsearchException as e:
            print('error putting mapping:\n'+str(e))
            print('deleting index {}...'.format(cwh.index_name))
            es.indices.delete(cwh.index_name)
            es.indices.create(cwh.index_name, body = {'mappings': mapping})
    else:
        print('index {} does not exist'.format(index_name))
        es.indices.create(index_name, body = {'mappings': mapping})
        

def load(es,posts):    
    
    mapping = {cwh.doc_type: cwh.doc_mapping}
    check_indice_exists(cwh.index_name, es, mapping)
    counter = 0
    bulk_data = []
    list_size = len(posts)
    for post in posts:
        web_doc = get_web_doc(post) 
        bulk_doc = {
            "_index": cwh.index_name,
            "_type": cwh.doc_type,
            "_id": web_doc['id'],
            "_source": web_doc
            }
        bulk_data.append(bulk_doc)
        counter+=1
        success=0
        if counter % cwh.bulk_chunk_size == 0 or counter == list_size:
            success, _ = bulk(es, bulk_data)
            bulk_data = []
    return success


def main():
    
    host = cwh.es_host
    region = cwh.region
    service = cwh.service
    credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service)

    es = Elasticsearch(
        hosts = [{'host': host, 'port': 443}],
        http_auth = awsauth,
        use_ssl = True,
        verify_certs = True,
        connection_class = RequestsHttpConnection
        )

    # start webhoseio producer
    webhoseio.config(token= cwh.token)
    query_params = cwh.query_params    
    output = webhoseio.query("filterWebContent", query_params)
    
    counter=0
    while True:
        posts=output['posts']
        success=load(es,posts)
        counter+=success
        print('ElasticSearch indexed {} total documents'.format(counter))
        time.sleep(50)
        output = webhoseio.get_next()
        
if __name__ == '__main__':
    main()         