# -*- coding: utf-8 -*-
'''
mapping ['表名'][1]['字段'][0] = 新字段

mapping ['表名'][1]['字段'][1] = 字段中文

mapping ['表名'][1]['字段'][2] = 属性

mapping ['表名'][0] = 新表名

所以mapping 的格式就是

dict {
        '表名1': ['新表名',{ '字段1':[ '新字段','字段中文','属性' ],'字段2':[ '新字段','字段中文','属性' ]}]
        ,'表名2':['新表名',{ '字段1':[ '新字段','字段中文','属性' ],'字段2':[ '新字段','字段中文','属性' ]}]
        }
'''

import codecs
import os

## 初始化常量
OLD_TABLE_NUM = 1
NEW_TABLE_NUM = 7

OLD_COLUMN_NUM = 2
NEW_COL_NUM = 8
NEW_NAME_NUM = 9
NEW_TYPE_NUM = 10
mapping_dict = {}


## open mapping 
with open('mapping.txt','r') as f:
    tmp_list = f.readlines()

## 初始化 获取第一个表名
tmp_dict = {}
tmp_table = tmp_list[1].split(';')[OLD_TABLE_NUM]

num_list = [1]
tmp_dict[tmp_table] = num_list


## 记录每个表名的位置
for i in range(1,len(tmp_list)):
    tmp_old_table = tmp_list[i].split(';')[OLD_TABLE_NUM]
    if tmp_table != tmp_old_table:
        ## 更新上一个旧表名的末尾数字
        tmp_dict[tmp_table].append(i-1)  

        ## 初始化，下一个旧表名的起始数字
        tmp_table = tmp_old_table        
        num_list = []
        tmp_dict[tmp_table] = num_list
        tmp_dict[tmp_table].append(i)    
    
    elif i == len(tmp_list)-1 :
        ## 末尾判断，更新最后一个旧表名的末尾数字
        tmp_dict[tmp_table].append(i)    


## mapping 格式输出
for key in tmp_dict.keys():
    ## 初始化 每种表名后续格式
    column_dict = {}
    table_list = []
    
    ## 根据临时dict获取 旧表名的 起始数字和末尾数字，进行加工
    for i in range(tmp_dict[key][0],tmp_dict[key][1]+1):
        ## 初始化&&获取当前字典英文
        column_list = []
        column = tmp_list[i].split(';')[OLD_COLUMN_NUM]  
        ## 依次录入 新字段英文，中文，属性
        column_list.append(tmp_list[i].split(';')[NEW_COL_NUM])
        column_list.append(tmp_list[i].split(';')[NEW_NAME_NUM])
        column_list.append(tmp_list[i].split(';')[NEW_TYPE_NUM])
        ## 整合成字段字典
        ## { '字段1':[ '新字段','字段中文','属性' ],'字段2':[ '新字段','字段中文','属性' ]}
        column_dict[column] = column_list

    ## 录入 表名列表
    ## ['新表名',{ '字段1':[ '新字段','字段中文','属性' ]}]
    table_list.append(tmp_list[i].split(';')[NEW_TABLE_NUM])
    table_list.append(column_dict)
    
    ## 录入成表名字典values
    ## '表名1': ['新表名',{ '字段1':[ '新字段','字段中文','属性' ]}]
    mapping_dict[key] = table_list

## 清空临时字段和列表
column_dict = table_list = column_list =''


print(mapping_dict['BI_2'][1]['age'][1])
        
