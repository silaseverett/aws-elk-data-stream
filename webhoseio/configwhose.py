# config for webhoseio.ipynb A

# webhoseio api token
token= <your_webhoseio_token_here>
# webhoseio query here using 'modi' for search term
query_params = {"q": "modi thread.country:IN"}

id_field = 'uuid'

# elasticsearch parameters
service = 'es'
es_host = <es_index_name> #without the https - get index from aws elasticsearch console
region = <aws_region> # e.g. us-west-1
es_port = 80
bulk_chunk_size = 100  #number of documents to index in a single bulk operation
index_name = 'webhose'
doc_type = 'web_doc'

#https://www.elastic.co/blog/strings-are-dead-long-live-strings
# https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping-date-format.html


doc_mapping = {



    'properties':
                    {'published': {
                                  'type': 'date'
                                  },
                     'log_time': {
                                  'type': 'date'
                                  },
                        'text': {
                                  'type': 'text',
                            "analyzer": "stop",
                                      "fielddata": True,
          "fielddata_frequency_filter": {
            "min": 0.001,
            "max": 0.1,
            "min_segment_size": 500
          },
                          'fields': {
                        'keyword': {
                          'type': 'keyword'
                                    }
                                  }
                                },
                    'language': {
                                  'type': 'keyword'
                              },

                     'author': {
                                  'type': 'text'
                     },
                     'url':   {
                                   'type':'text'
                     },
                     'facebook_likes': {
                                     'type':'integer'
                     },
                     'facebook_shares': {
                                     'type':'integer'
                     },
                     'sentiment': {
                                  'type': 'keyword'
                              }
                    }
                 }
