#!/usr/bin/env python
# coding: utf-8

# # 运行配置

# ## 参数配置

abs_path = 'D:\\Documents\\vivo\\0621\\'
user_file='0621_douyin_user_info.xlsx'
video_file = '0621_douyin_video_info.xlsx'
brand_file = "VIVO品牌码表.xlsx"
comment_file = '0621_douyin_comment_info.xlsx'


# ## 索引配置

es_hosts = [{'host':'proj1', 'port':9200}]
index = "vivo_douyin_0621"
doc_type = "douyin"

fields = [
    "item_id|long",
    "user_item_id|long",
    "video_item_id|long",
    "keyword|string|words",
    "module|string|not_analyzed",
    "site|string|not_analyzed",
    "author|string|words",
    "title|string|words",
    "content|string|words",
    "like_count|long",
    "url|string|not_analyzed",
    "replies|long",
    "data_type|string|not_analyzed",
    "publish_date|long",
    "update_date|long",
    "sourceCrawlerId|long",
    "video_url|string|not_analyzed",
    "video_brand|string|not_analyzed",
    "video_content|string|words",
    "video_publish_date|long",
    "video_user_fans|long",
    "video_user_name|string|words",
    "video_user_register_id|string|not_analyzed"
]


# In[3]:

target_comment_sheet = "sheet0"

is_create_index = True


# # 运行程序

import sys
import os

sys.path.append("..")

import pandas as pd

from utils.timer import timer
from utils.excels import each_row, save_excel


Bytes_Per_Sec = 201953523 / 333.0

@timer
def read_excel(file, name=None, rows=None):
    """
    读取Excel
    
    默认读取所有sheet, 可以指定
    默认读取所有行, 可以指定: 指定小批量行数并不会节约时间
    读取200MB约350s
    """
    file_bytes = os.path.getsize(file)
    print("predict cost: %.5fs" % (file_bytes / Bytes_Per_Sec))
    return pd.read_excel(file, nrows=rows, sheet_name=name)


# ## 用户处理

user_sheet = read_excel(abs_path + user_file, "sheet0")
print(user_sheet.shape)

user_tags = {}
def user_parser(idx, key, row):
    user_tag = {}
    
    uid = row["uid"]
    name = row["user_name"]
    nick = row["register_id"]
    fans = row["fans_num"]
    
    user_tag["uid"] = uid
    user_tag["name"] = name
    user_tag["fans"] = fans
    user_tag["register_id"] = nick
    
    user_tags[uid] = user_tag
    
    return True
    
each_row(user_sheet, user_parser, 1000)


# In[9]:


print(len(user_tags))
for k, v in user_tags.items():
    print(k, v)
    break


# ## 视频处理

video_sheet = read_excel(abs_path + video_file, "sheet0")
print(video_sheet.shape)

brand_sheet = read_excel(abs_path + brand_file, "Sheet1")
print(brand_sheet.shape)


# In[12]:

brandKB = {}
def brand_parser(idx, key, row):
    brand_name = row['品牌'].strip()
    if brand_name not in brandKB:
        brandKB[brand_name] = set()
    
    if type(row['品牌产品']) is str:
        brand_type_name = row['品牌产品'].strip()
        if brand_type_name:
            brandKB[brand_name].add(brand_type_name)
    
    brand_keyword_str = row['关键词'].strip()
    if brand_keyword_str.startswith('#'):
        brandKB[brand_name].add(brand_keyword_str)
    else:
        for kw in brand_keyword_str.split(','):
            if type(kw) is str:
                brandKB[brand_name].add(kw)
    
    return True
                
each_row(brand_sheet, brand_parser)
print(len(brandKB))


# In[13]:


def kw_match(content, keywords, case_sensitive=True):
    """
    关键词匹配
    """
    for kw in keywords:
        # 大小写敏感
        if case_sensitive and kw in content:
            return True
        # 大小写不敏感
        if not case_sensitive and kw.lower() in content.lower():
            return True
    return False

def brand_match(content, kb):
    """
    品牌匹配
    """
    for key, value in kb.items():
        if kw_match(content, value, False):
            return key
    
    return None

# TEST CASE

print(brand_match("vivo", brandKB))
print(brand_match("#我才是实力自拍王", brandKB))
print(brand_match("vivo", brandKB))
print(brand_match("#华为", brandKB))
print(brand_match("小米Play", brandKB))
print(brand_match("小米play", brandKB))


# In[14]:


import time

def common_time_parse(origin):
    """
    时间处理
    """
    real_time = time.localtime() # 默认当前时间
    if type(origin) is str and len(origin) == 19:
        real_time = time.strptime(origin, "%Y-%m-%d %H:%M:%S")
    elif len(str(origin)) == 14:
        real_time = time.strptime(str(origin), "%Y%m%d%H%M%S")

    return real_time

# time.strftime(real_time, "%Y-%m-%d %H:%M:%S")

video_tags = {}
def video_parser(idx, key, row):
    video_tag = {}
    
    url = row['url']
    vid = url.split('/')[5]
    uid = row["user_item_id"]
    
    publish_date = time.strftime("%Y-%m-%d %H:%M:%S", common_time_parse(row["publish_date"]))
    title = row["title"]
    content = row['content']
    brand = ""
    if type(content) is str:
        brand = brand_match(content, brandKB)
        
    video_tag["vid"] = vid
    video_tag["url"] = url
    video_tag["publish_date"] = publish_date
    video_tag["title"] = title
    video_tag["content"] = content
    video_tag["brand"] = brand
       
    user_tag = {}
    if uid in user_tags:
        user_tag = user_tags[uid]
    else:
        print("user not exist: %s" % uid)
    for k, v in user_tag.items():
        video_tag["user_" + k] = v

    video_tags[vid] = video_tag
    return True
    
each_row(video_sheet, video_parser, 1000)
print(len(video_tags))

print(len(video_tags))
for k, v in video_tags.items():
    print(k)
    print(v)
    break


# ## 评论处理

comment_all_sheet = read_excel(abs_path + comment_file)
print(len(comment_all_sheet))
print(comment_all_sheet.keys())


# > 安全隔离带

from elasticsearch import Elasticsearch

from utils.elasticsearchs import pretty_print, create_index, insert_bulk

proj_es_17 = Elasticsearch(es_hosts)


# 1. 准备索引

if is_create_index:
    create_res = create_index(proj_es_17, index, doc_type, fields)
    print(create_res)
else:
    print("do not create index")


# 2. 写入数据

def flush(es, index, doc_type, data, size=3000, force=False):
    if not force:
        if len(data) < size:
            return False
        
    origin_size = len(data)
    success, info = insert_bulk(es, index, doc_type, data)
    data.clear()
    
    if success < origin_size:
        print(info)
        
    return True


# In[26]:


import math

comment_datas = {}
def comment_parser(idx, key, row):
    comment_data = {}

    # 1. origin info
    cid = row["item_id"]
    url = row["url"]
    vid = url.split('/')[5]

    comment_data["item_id"] = cid
    comment_data["url"] = url
    comment_data["video_item_id"] = vid
    comment_data["publish_date"] = int(time.mktime(common_time_parse(row["publish_date"])))
    comment_data["update_date"] = int(time.mktime(common_time_parse(row["update_date"])))
 
    same_keys = set(["user_item_id", 
                      "keyword", "module", "site",
                      "author", "title", "content",
                      "like_count", "replies", "data_type",
                      "sourceCrawlerId"])
    for k in same_keys:
        if type(row[k]) is float and math.isnan(row[k]):
            continue
        comment_data[k] = row[k]

    # 2. video info
    video_tag = video_tags[vid]
    comment_data["video_publish_date"] = int(time.mktime(common_time_parse(video_tag["publish_date"])))

    video_keys = set(["url", "brand", "content",
                     "user_fans", "user_name", "user_register_id"])
    for k in video_keys:
        if k in video_tag: # 有一个用户信息没抓到
            comment_data["video_" + k] = video_tag[k]

    # 3. store
    comment_datas[cid] = comment_data
    flush(proj_es_17, index, doc_type, comment_datas)
#     print("after insert: %d" % len(comment_datas))

    return True


# 选择需要处理的表单数据
comment_test_sheet = comment_all_sheet[target_comment_sheet]
print(comment_test_sheet.shape)

# TODO: 带上flush机制的each_row函数
# 逐行处理
each_row(comment_test_sheet, comment_parser, 5000)

# 最后的回收
# print("before %d" % len(comment_datas))
flush(proj_es_17, index, doc_type, comment_datas, force=True)
comment_datas.clear()
# print("after %d" % len(comment_datas))

# chunksize=4, csv才有
