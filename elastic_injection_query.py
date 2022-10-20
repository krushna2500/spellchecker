from elasticsearch import Elasticsearch
from elasticsearch.helpers import parallel_bulk, scan


def connect_elasticsearch():
    client = Elasticsearch(
        # Add your cluster configuration here!"sniff":To inspect the cluster state to get a list of nodes upon startup, periodically and/or on failure
        [{'host': '192.168.181.124', 'port': 9200}], maxsize=25,
        timeout=30, sniff_on_start=True,
        sniff_on_connection_fail=True,
        sniffer_timeout=60,
        sniff_timeout=10,
        max_retries=10
        # If your application is long-running consider turning on Sniffing to make sure the client is up to date on the cluster location.
    )  # allow up to 25 connections to each node

    if client.ping():
        print('Connected to ElasticSearch!!!!')
    else:
        print('ElasticSearch could not connect!!!!')
    # es = Elasticsearch(["host1", "host2"], maxsize=25)
    return client


# QUERY BUILDER
#..............
def create_query_nysiis(text):
    return  {"query":{
                "bool":{
                    "must":{
                    "match":{
                        "nysiis":{
                        "query":f"{text}"
                        }
                    }
                }
                }
            }}


def create_query_name_check(text):
    return  {"query":{
                "bool":{
                    "must":{
                    "match":{
                        "name":{
                        "query":f"{text}"
                        }
                    }
                }
                }
            }}


def create_query_eng_words(text):
    return  {"query":{
                "bool":{
                    "must":{
                    "match":{
                        "word":{
                        "query":f"{text}"
                        }
                    }
                }
                }
            }}


def create_query_fuzzy_elastic(text):
    return {
  "query": {
    "fuzzy": {
      "name":{
        "value": f"{text}",
        "fuzziness": "AUTO",
        "prefix_length": 1
      }
    }}
}



# MATCH AND RETURN RESULTS
#.........................
def matcher(client, trgt_index_name, nysiis_code):
    query_body = create_query_nysiis(nysiis_code)
    response = scan(client, query_body, index = trgt_index_name, preserve_order=True)
    return response

def matcher_name_check(client, trgt_index_name, name):
    query_body = create_query_name_check(name)
    response_name_check = scan(client, query_body, index = trgt_index_name, preserve_order=True)
    return response_name_check

def matcher_engword(client, trgt_index_name, word):
    query_body = create_query_eng_words(word)
    response = scan(client, query_body, index = trgt_index_name, preserve_order=True)
    return response


def matcher_fuzzy_elastic(client, trgt_index_name, name):
    query_body = create_query_fuzzy_elastic(name)
    response = scan(client, query_body, index = trgt_index_name, preserve_order=True)
    return response