#!/usr/bin/env python
# coding: utf-8

import os
import sys
sys.path.append("..")

TAG = os.path.basename(__file__)

# name, id, count
p_left = ["王菲", 237422, 369832]
# p_right = ["谢霆锋", 237366, 276987]
# p_right = ["窦靖童", 237415, 66825]
p_right = ["吴青峰", 236417, 293369]

# 来源地址
index = "ds-hermes-v134"
doc_type = "7324873c1c_2874"
es_hosts = [{'host':'192.168.40.10', 'port':9210}]

# 写入地址
write_index = "offline-yili-news-v0"
write_doc_type = "news"
write_es_hosts = [{'host':'192.168.10.153', 'port':9203}]

import json
import time
import elasticsearch2
from utils.timer import timer
from utils.elasticsearchs import scroll_parse, pretty_print, create_index_with_prop, insert_bulk
from utils import Log

Log.info(TAG, "left profiler: %s" % pretty_print(p_left))
Log.info(TAG, "right profiler: %s" % pretty_print(p_right))

"""
读取ES中数据
"""
es_dao = elasticsearch2.Elasticsearch(es_hosts, timeout=300)

def profiler_parse(rows_result, profiler_key):
    def row_parser(idx, key, row):
        source = row['_source']
        
        content_id = source['pk'].split("|")[1]
        rows_result[content_id] = source

        return True

    query = {
      "query": {
        "term": {
          "profilers_name": profiler_key
        }
      }
    }
    
    scroll_parse(es_dao, index, doc_type, query, row_parser, batch_size=100)
    
# p_left reading    
origin_left_rows = {}
profiler_parse(origin_left_rows, p_left[0])
Log.info(TAG, "p_left size: %d, predict size: %d" % (len(origin_left_rows), p_left[2]))

# TODO
# if (len(origin_left_rows) != p_left[2]):
#     Log.error(TAG, "p_left id error, size not the same")
#     sys.exit(1)

# p_right reading    
origin_right_rows = {}
profiler_parse(origin_right_rows, p_right[0])
Log.info(TAG, "p_right size: %d, predict size: %d" % (len(origin_right_rows), p_right[2]))

# TODO
# if (len(origin_right_rows) != p_right[2]):
#     Log.error(TAG, "p_right id error, size not the same")
#     sys.exit(1)  


"""
合并数据
"""
origin_rows = {}
origin_rows.update(origin_left_rows)
origin_rows.update(origin_right_rows)

Log.info(TAG, "%d = left_%d + right_%d" % (len(origin_rows), len(origin_left_rows), len(origin_right_rows)))


"""
创建存储索引
"""
mapping_result = es_dao.indices.get_mapping(index=index, doc_type=doc_type)
write_prop = mapping_result[index]['mappings'][doc_type]['properties']

# import elasticsearch
# es_write = elasticsearch.Elasticsearch(write_es_hosts, timeout=300)
# create_response = create_index_with_prop(es_write, write_index, write_doc_type, write_prop)
# print(create_response)

"""
写入数据
"""
es_write = elasticsearch2.Elasticsearch(write_es_hosts, timeout=300)

def flush(es, index, doc_type, data, size=3000, force=False):
    if not force:
        if len(data) < size:
            return False
        
    origin_size = len(data)
    success, info = insert_bulk(es, index, doc_type, data)
    data.clear()
    
    print("current time: %.5f" % time.time())
    
    if success < origin_size:
        print(info, flush=True)
        
    return True

result_rows = {}
for k, v in origin_rows.items():
    key = "%d-%d|%s" % (p_left[1], p_right[1], k)
    v['profilers_name'] = "%s-%s" % (p_left[0], p_right[0])
    v['profilers_id'] = "%d-%d" % (p_left[1], p_right[1])
    v['pk'] = key
    v['id'] = key

    result_rows[key] = v
    flush(es_write, write_index, write_doc_type, result_rows)

flush(es_write, write_index, write_doc_type, result_rows, force=True)

