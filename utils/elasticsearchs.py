#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import json

from elasticsearch import Elasticsearch
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