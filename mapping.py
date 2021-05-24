# -*- coding: utf-8 -*-
import re

## 初始化常量
FIRST_TABLE_NUM = 1
OLD_TABLE_NUM = 1
NEW_TABLE_NUM = 7
TABLE_NAME_NUM = 0

OLD_COLUMN_NUM = 2
NEW_COL_NUM = 8
NEW_NAME_NUM = 9
NEW_TYPE_NUM = 10

class Mapping:
    
    def __init__(self,filename,sqlname):
        self.filename = filename
        self.sql = sqlname

    def test(self):
        self.mapping_create()

        with open(self.sql,'r') as f:
            read = f.read()
        sql_code_list = read.split(';')

        for i in range(len(sql_code_list)):
            
            sql_code = sql_code_list[i]
            print('### Checking No_%s SQL..'%(i+1))
            sql_code_init = self._sql_code_init(sql_code)
            self.table_check(sql_code_init)
            self.column_check(sql_code_init)
            self.mapping_check()
            #self.mapping_output()
            new_code = self.column_change(sql_code)
            print(new_code)
            
            print('### No_%s done!\n'%(i+1))

    def _sql_code_init(self,sql_str):
        '''
        初始化SQL语句，返回容易识别的SQL语言
        '''
        ## 清除 注释
        sql_str = re.sub(r'--.*\n','',sql_str)

        sql_code = sql_str.replace('\n',' ')
        
        sql_code_init = re.sub('\s\s*',' ',sql_code)
        
        print('## Initializing SQL code...')
        
        return sql_code_init

    def mapping_create(self,flags=0):
        """
        映射文档格式：flags=0
        self.mapping_dict = {
            old_table : [ new_table
                        , { old_col : [ new_col , new_name , new_type ]  }  ]
                        
        or  flags != 0

        self.mapping_dict = {
            new_table : [ table_name
                        , { col : [ col , name , type ]  }  ]
        }
        """
        self.mapping_dict = {}

        if flags == 0 :
            _TABLE_NUM = OLD_TABLE_NUM
            _COLUMN_NUM = OLD_COLUMN_NUM
            _FLAGES_TABLE_NUM = NEW_TABLE_NUM
        else :
            _TABLE_NUM = NEW_TABLE_NUM
            _COLUMN_NUM = NEW_COL_NUM  
            _FLAGES_TABLE_NUM = NEW_TABLE_NUM
            
        ## open mapping 
        with open(self.filename,'r') as f:
            tmp_list = f.readlines()

        ## 初始化 获取第一个表名
        tmp_dict = {}
        tmp_table = tmp_list[1].split(',')[_TABLE_NUM].upper()

        tmp_dict[tmp_table] = [1]

        ## 记录每个表名的位置
        for i in range(FIRST_TABLE_NUM,len(tmp_list)):
            tmp_old_table = tmp_list[i].split(',')[_TABLE_NUM].upper()
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
                column = tmp_list[i].split(',')[_COLUMN_NUM].upper()  
                ## 依次录入 新字段英文，中文，属性
                column_list.append(tmp_list[i].split(',')[NEW_COL_NUM].upper())
                column_list.append(tmp_list[i].split(',')[NEW_NAME_NUM])
                column_list.append(tmp_list[i].split(',')[NEW_TYPE_NUM].upper())
                ## 整合成字段字典
                ## { '字段1':[ '新字段','字段中文','属性' ],'字段2':[ '新字段','字段中文','属性' ]}
                column_dict[column] = column_list

            ## 录入 表名列表
            ## ['新表名',{ '字段1':[ '新字段','字段中文','属性' ]}]
            ## 或者 flages <> 0 '表名1': ['表中名',{ '字段1':[ '新字段','字段中文','属性' ]}]
            table_list.append(tmp_list[i].split(',')[_FLAGES_TABLE_NUM])
            table_list.append(column_dict)
            
            self.mapping_dict[key] = table_list

        print('#### mapping init done!!')

    def table_check(self,sql_str):
        """
        设别所有用到的table，并返回 表名字典，和表名排序
        表名字典 table_dict = {  table_name : as_name }
        表名排序 tab_set = [  table1,table2,table3]
        """
        ## find out all tables
        self.table_dict = {}   ## 保存使用到的表
        self.tab_set = []      ## 保存排序
        self.as_dict = {}      ## 保存对应关系
        table_search = re.search(r'FROM (\w*\s\w*) ',sql_str,re.I)
        if table_search :
            self.__table_init(table_search.group(1))
        else :
            print('## \033[1;31m The table name cannot be found, please check !! \033[0m  ')
            return

        slave_list = re.findall(r'JOIN (\w*\s\w*) ON',sql_str,re.I)
        for slaves in slave_list:
            self.__table_init(slaves)

        ## DEBUG TEST
        print('#### table dict done !!')

    def __table_init(self,table_str):
        ## init str of table 
        ## return dict of table 
        ## ps : {'A':'MASTER_TABLE','B':'SLAVE_TABLE'}
        tmp_list = []
        
        table_list = table_str.split(' ')
        for tables in table_list :
            if tables != '' :
                tmp_list.append(tables)
        self.table_dict[tmp_list[0]]=tmp_list[1]
        self.as_dict[tmp_list[1]]=tmp_list[0]
        self.tab_set.append(tmp_list[0])

    def column_check(self,sql_code):
        """
        字段级识别，返回 字段字典，排序，字段逻辑
        column_dict = { as : [ col1 , col2 ]  }
        col_set = [ as1,as2,as3 ]
        col_logic_list = [ logic1,logic2 ]
        """
        ## ps: { column1:[col1,col2,col3] }
        
        self.column_dict = {}    ## 保存字段
        self.col_set = []        ## 保存排序(别名)
        self.col_logic_list = []       ## 保存逻辑

        ## find out all columns
        column_codes = re.search(r'SELECT (.*) FROM ',sql_code,re.I)
        if column_codes :
            colnum_code = column_codes.group(1)
        else:
            print('# Failed to get column,please check  !')
            return
        
        ## section column for ','
        column_list = colnum_code.split(',')
        if len(column_list) == 1 :   ### 单字段判断
            return False

        ## 判断是否 函数中存在逗号，合并函数中逗号
        tmp_num = 0
        while tmp_num < len(column_list)-1 :
            if column_list[tmp_num].count('(') != column_list[tmp_num].count(')') :
                column_list[tmp_num] = column_list[tmp_num]+','+column_list[tmp_num+1]
                del column_list[tmp_num+1]
            else:
                tmp_num += 1   
        
        ## 每行字段设别
        for i in range(len(column_list)):
            self.__column_init(column_list[i])

    def __column_init(self,column_str):
        
        FUNCTIONS = ['null','case','when','then','is','not','else','end','as','int','string']
        ## 初始化 前后空格
        column_str = re.sub(r'^\s','',column_str)
        column_str = re.sub(r'\s$','',column_str)
        
        ## 判断 别名 字段
        columns_list = re.findall(r'\w*\.?\w+',column_str)
        
        if len(columns_list) == 1:                  ## 判断直接映射的情况
            col_as_name = column_str.split('.')[-1]
            
            self.column_dict[col_as_name]=columns_list
            self.col_set.append(col_as_name)
            self.col_logic_list.append(columns_list[0])
            return     
        else :
            col_as_name = columns_list[-1]

        self.col_set.append(col_as_name)

        ## 获取字段逻辑
        col_logic = re.sub(r'\s?(as)?(AS)? %s$'%col_as_name,'',column_str,re.I)
        self.col_logic_list.append(col_logic)

        ## 删除所有函数
        new_column_str = re.sub(r'\w+\(','',col_logic)

        ## 重新获取所有字段
        new_columns_list = re.findall(r'\w*\.?\w+',new_column_str)

        ## 去重
        columns_list_set = list(set(new_columns_list))

        finally_list = []

        ## 初步排除部分函数
        for i in range(len(columns_list_set)):
            try:
                float(columns_list_set[i])
            except:
                if columns_list_set[i].lower() not in FUNCTIONS:
                    finally_list.append(columns_list_set[i])

        ## 保存对应关系
        self.column_dict[col_as_name]=finally_list

    def mapping_check(self):
        """
        根据使用过的字段进行匹配
        返回 ： transform_dict = { col : [ table,[new_col,name,type]]}
        """
        ## 首先判断 表名 是否存在映射
        ## table_dict = { as_name : table_name }
        ##        self.mapping_dict = {
        ##    old_table : [ new_table
        ##                , { old_col : [ new_col , new_name , new_type ]  }  ]
        exist_table_list = []  
        exist_as_list = []     
        transform_dict = {}          ## 日后要用，大小写的问题要注意
        not_exist_col_dict = {}
        self.column_change_dict = {}

        normal_column_list = []      ##保存格式为 A.XXX 的字段，
        unnormal_column_list = []    ##保存格式为 XXX   的字段，且有正常映射

        mapping_tables = self.mapping_dict.keys()
        for table in list(set(self.table_dict.keys())) :
            if table.upper() in mapping_tables : 
                exist_table_list.append(table)
                exist_as_list.append(self.table_dict[table])
            else:
                print(" !! table:%s is not in mapping !!"%table)

        #print(exist_table_list)
        #print(exist_as_list)

        ## 初始化临时不存在的表名字段映射
        for i in list(set(self.table_dict.keys())) : 
            not_exist_col_dict[i.upper()] = []
        not_exist_col_dict['too_many_table']=[]
        not_exist_col_dict['not_in_table']=[]

        ## 然后 判断 所用到的字段 是否存在字典里
        ## column_dict = { as : [ col1 , col2 ]  }
        all_list = []
        for tmp_list in self.column_dict.values():
            all_list += tmp_list
        all_list = list(set(all_list))
        #print(all_list)
        
        for cols in all_list:
            tmp_col_list = cols.split('.')
            
            if len(tmp_col_list) == 2 :
                _as  = tmp_col_list[0].upper()                 ## 字段别名
                table_name = self.as_dict[_as].upper()         ## 表名
                normal_column  = tmp_col_list[1].upper()       ## 旧字段英文
                
                if table_name in exist_table_list :            ## 判断对应表名是否存在映射列表中
                    table = self.mapping_dict[table_name]
                    new_col_list = table[1].keys()            ## 映射列表
                    if normal_column in new_col_list:         ## 判断是字段否存在映射列表中
                        ## 录入转换后的 字段信息
                        transform_dict[cols]=[table[0],table[1][normal_column]]
                        normal_column_list.append(cols)  ## 录入到正常字段列表中，方便替换是直接使用
                    else:
                        not_exist_col_dict[table_name].append(cols)  
                        ## 字段不存在的
                else :
                    ### 表名 不存在的
                    transform_dict[cols] = [table_name,[normal_column,'','']]
                    not_exist_col_dict[table_name].append(normal_column)  
            else:
                ## 字段别名不存在的,
                not_exist_table = []
                unnormal_col = cols.upper()                  ## 旧字段英文(大写)
                ## 对所有存在表的字段进行判断
                for table in exist_table_list : 
                    new_col_list = self.mapping_dict[table][1].keys()  ## 映射列表
                    if unnormal_col in new_col_list:         ## 判断字段是否存在映射列表中
                        not_exist_table.append(table) 

                if not_exist_table == []:        ## 所有表都不存在这个字段的情况
                    not_exist_col_dict['not_in_table'].append(unnormal_col)
                elif len(not_exist_table) > 1 :  ## 这个字段存在两个表以上的情况
                    not_exist_col_dict['too_many_table'].append(unnormal_col)
                else:                            ## 若只有一个表存在这个字段，则保存
                    __tablename = self.mapping_dict[table][0]
                    print(table)
                    __colname   = self.table_dict[table].upper() + '.' + self.mapping_dict[table][1][unnormal_col][0]
                    __colzh     = self.mapping_dict[table][1][unnormal_col][1]
                    __coltype   = self.mapping_dict[table][1][unnormal_col][2]
                    transform_dict[cols]= [__tablename
                                          ,[__colname,__colzh,__coltype]]
                    unnormal_column_list.append(cols)

        ## 输出 not_exist_col_dict 中存在异常的字段
        for key in not_exist_col_dict.keys():
            if not_exist_col_dict[key] != [] :
                print("%s 中问题字段 %s"%(key.ljust(20),not_exist_col_dict[key]))

        self.transform_dict = transform_dict
        self.column_change_dict['normal'] = normal_column_list
        self.column_change_dict['unormal'] = unnormal_column_list
        self.column_change_dict['table'] = exist_table_list

    def mapping_output(self):

        for i in range(len(self.col_set)) :     
            as_col = self.col_set[i]
            col_list = self.column_dict[as_col]
            col_logic = self.col_logic_list[i]
            
            i = 0
            for cols in col_list :
                table_name = self.transform_dict[cols][0]
                col_name = self.transform_dict[cols][1][0]
                col_zh   = self.transform_dict[cols][1][1]
                col_type = self.transform_dict[cols][1][2]
                if i != 0 :
                    as_col = ' '
                    col_logic = ' '
                print("%s %s %s %s %s %s"%(as_col.ljust(10),table_name.ljust(15),col_name.ljust(15),col_zh.ljust(15),col_type.ljust(15),col_logic))
                i += 1

    def column_change(self,sql_code):
        for key in self.column_change_dict.keys():
            if key == 'table' :
                for table_name in self.column_change_dict[key]:
                    sql_code = re.sub(r" %s "%table_name," %s "%self.mapping_dict[table_name][0],sql_code)
            elif key == 'normal' :
                for column in self.column_change_dict[key]:
                    new_column = column.split('.')[0].upper() + '.' + self.transform_dict[column][1][0]
                    sql_code = re.sub(r"%s\b"%column,new_column,sql_code)
            elif key == 'unormal' :          ## 存在问题为 别名字段会被替换
                for unornam_col in self.column_change_dict[key]:
                    unornam_list = re.findall(r'[^\.\w]%s\b'%unornam_col,sql_code)
                    unornam_list = list(set(unornam_list))
                    for unornaml in unornam_list:
                        change_str = unornaml[0] + self.transform_dict[unornam_col][1][0]
                        if unornaml[0] == '+' :
                            unornaml = '\\' + unornaml
                        sql_code = re.sub(r"%s\b"%unornaml,"%s"%change_str,sql_code)
        
        return sql_code

a = Mapping('mapping.csv','init.sql')
a.test()
