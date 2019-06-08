#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import json
import time

from utils.timer import timer

# from elasticsearch import Elasticsearch
# 避免引入, 避免引入版本冲突
# https://elasticsearch-py.readthedocs.io/en/master/
# es 7不兼容低版本的查询接口, es 7取消了doc_type
from elasticsearch.helpers import bulk


def pretty_print(value):
    """
    格式化输出json
    """
    return json.dumps(value, sort_keys=True, indent=2, separators=(',', ': '))


def lines_to_prop(lines, separator="|"):
    """
    转换字段配置为es属性
    
    eg: "vtype|short",
    eg: "metaGroup|string|not_analyzed",
    eg: "createdAt|long",
    eg: "nickname_analyse|string|words"
    """
    
    properties = {}
    for line in lines:
        parts = line.split(separator)
        
        # skip error fields
        if len(parts) < 2:
            continue
            
        field_name, field_type = parts[:2]
        others = parts[2:]
        
        field = {"type": field_type}
        if field_type == "string":
            analyzer = "not_analyzed"
            if len(others) > 0:
                analyzer = others[0]
            
            if analyzer == "not_analyzed":
                field["index"] = analyzer
                field["doc_values"] = True
            else:
                field["analyzer"] = analyzer
                
        properties[field_name] = field
    
    return properties
        

def create_index(connection, index, doc_type, fields, shards=5, replica=1, dynamic="strict"):
    """
    创建索引
    
    注: fields为字段配置简化行, 例如: "nickname_analyse|string|words"
    """
    
    properties = lines_to_prop(fields)
    
    body = {
        "settings": {
            "number_of_shards": shards,
            "number_of_replica": replica
        }, 
        "mappings": {
            doc_type: {
                "dynamic": dynamic,
                "properties": properties
            }
        }
    }
    print("index body: " + pretty_print(body))
    
    return connection.indices.create(index=index, body=body)
    
    
def delete_index(connection, index):
    """
    删除索引, 慎用
    """
    return connection.indices.delete(index)
    
    
def insert_one(connection, index, doc_type, id, data):
    """
    单条插入
    
    id: 数据唯一标识
    data: dict, 待插入数据, eg: {"type": 2, "name": "中华人民共和国"}
    """
    return connection.index(index=index, doc_type=doc_type, id=id, body=data)


def insert_bulk(connection, index, doc_type, datas):
    """
    批量插入
    
    datas: dict, 待插入数据, eg: {"id_1": {"type": 2, "name": "中华人民共和国"}, ...}
    """
    
    actions = []
    for k, v in datas.items():
        action = {
            "_index": index,
            "_type": doc_type,
            "_id": k,
            "_source": v
        }

        actions.append(action)
    print("action size: %d" % len(actions))
        
    return bulk(connection, actions, index=index, raise_on_error=False)


@timer
def scroll_parse(connection, index, doc_type, query, parser, batch_size=5, wait_time='3m'):
    """
    滚动查询全部数据
    
    注: 每次返回数量为 batch_size * shards
    """
    
    # init the scroll
    page = connection.search(index=index, doc_type=doc_type, body=query, size=batch_size, scroll=wait_time, search_type="scan")
    total_size = page['hits']['total']
    print("parsing: %s/%s, batch size: %d, query: %s" % (index, doc_type, batch_size, pretty_print(query)))
    
    # flag
    flag = True
    
    # scroll
    idx = 0
    sid = page['_scroll_id']
    length = 1 # 为了进入第一次循环
    while length > 0:
        # 真正获取数据
        page = connection.scroll(scroll_id=sid, scroll=wait_time)
        
        # 处理数据
        for hit in page['hits']['hits']:
            key = hit['_id']
            flag = parser(idx, key, hit)
            
            idx += 1
            if not flag:
                break
            
        # 准备下一轮循环
        sid = page['_scroll_id']
        length = len(page['hits']['hits'])
        
        print("# current size: %d, progress: %d/%d. At %.5f" % (length, idx, total_size, time.time()))
        if not flag:
            break
            
    return flag
