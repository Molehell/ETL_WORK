# -*- coding=utf-8 -*-
## 存在的问题： 无法识别多层嵌套，

from xml.etree.ElementTree import ElementTree,Element,SubElement,tostring
import re

# elemnt为传进来的Elment类，参数indent用于缩进，newline用于换行   
def prettyXml(element, indent, newline, level = 0): 
    # 判断element是否有子元素
    if element is not None:
        # 如果element的text没有内容      
        if element.text == None or element.text.isspace():     
            element.text = newline + indent * (level + 1)      
        #else:    
        #    element.text = newline + indent * (level + 1) + element.text.strip() + newline + indent * (level + 1)    
    # 此处两行如果把注释去掉，Element的text也会另起一行 
    else:     
        element.text = newline + indent * (level + 1) + element.text.strip() + newline + indent * level    
    temp = list(element) # 将elemnt转成list    
    for subelement in temp:    
        # 如果不是list的最后一个元素，说明下一个行是同级别元素的起始，缩进应一致
        if temp.index(subelement) < (len(temp) - 1):     
            subelement.tail = newline + indent * (level + 1)    
        else:  # 如果是list的最后一个元素， 说明下一行是母元素的结束，缩进应该少一个    
            subelement.tail = newline + indent * level   
        # 对子元素进行递归操作 
        prettyXml(subelement, indent, newline, level = level + 1)     

def read_xml(in_path):
    '''读取并解析xml文件
       in_path: xml路径
       return: ElementTree'''
    tree = ElementTree()
    tree.parse(in_path)
    return tree

def get_columns(node,columnList):
    if len(node) == 1 :
        field = node[0].text
        columnList.append(field.upper())
    elif len(node) == 2 :
        field = node[0].text+'.'+node[1].text         
        columnList.append(field.upper())

    return columnList

def get_columnList(node,SubEltroot):
    
    ## 指定 一级路径下的 selectlist 防止获取到其他地方
    path = 'selectStatement/atomSelectStatement/selectClause/selectList'
    
    _selectListElt = node.find(path)  
    selectItemElts = _selectListElt.findall('selectItem')    
    
    num = 1
    for selectItemElt in selectItemElts : 
        columnList = []
        
        ## 获取 所有字段 列表
        try:
            expressions = selectItemElt.find('expression').findall('.//expression')
        except AttributeError: 
            colAsSElt = SubElement(SubEltroot,'ColAs')
            colAsSElt.attrib = {'col_%s'%num:'*'}
            continue

        if len(expressions) == 0 :
            column = selectItemElt.findall('.//expression//identifier')
            columnList = get_columns(column,columnList)
        else :
            for exp in expressions :
                column = exp.findall('.//identifier')
                columnList = get_columns(column,columnList)
        
        columnList = list(set(columnList))

        ## 获取 字段别名
        try:
            fieldAlias = selectItemElt.find('identifier').text  ## 需要一个排错选项
        except AttributeError:
            fieldAlias = columnList[0].split('.')[-1]
        
        colAsSElt = SubElement(SubEltroot,'ColAs')
        colAsSElt.attrib = {'col_%s'%num:fieldAlias}

        for cols in columnList:
            tmpCol = SubElement(colAsSElt,'Col')
            tmpCol.text = cols


        logicCol = SubElement(colAsSElt,'logic')
        get_logic(selectItemElt.find('expression'),logicCol)

        num += 1

def get_formList(node,SubEltroot):

    fromElt = SubElement(SubEltroot,'From')

    fromClause = node.find('selectStatement//fromClause/fromSource')

    ## 主表
    atomjoinSource = fromClause.find('joinSource/atomjoinSource/tableSource')

    tableName = atomjoinSource.find('tableName/identifier').text
    try:
        tableNameAlias = atomjoinSource.find('identifier').text
    except AttributeError:
        tableNameAlias = tableName

    tableAsName = SubElement(fromElt,'tableAsName')
    tableAsName.text = tableNameAlias

    tableNameElt = SubElement(fromElt,'tableName')
    tableNameElt.text = tableName


    ## 取出 关联表
    joinTokens = fromClause.findall('joinSource/joinToken')
    joinSource = fromClause.findall('joinSource/joinSourcePart')
    joinExpres = fromClause.findall('joinSource/expression')
    
    for joinNum in range(len(joinTokens)) :
        ## 定义tree 一级目录
        joinElt = SubElement(SubEltroot,'Join')

        ## 关联方式
        tokens = SubElement(joinElt,'Jointoken')
        tokens.text = joinTokens[joinNum].text

        ## 关联table别名
        joinAs = joinSource[joinNum].findall('.//identifier')[-1].text
        jointableAsName = SubElement(joinElt,'tableAsName')
        jointableAsName.text = joinAs
        
        ## 关联table
        parserName = joinSource[joinNum].getchildren()[0].tag
        if parserName == 'subQuerySource' :
            jointableName = SubElement(joinElt,'tableExpession')
            joinSelect = SubElement(jointableName,'Select')
            selectState = joinSource[joinNum].find('.//regularBody')
            get_columnList(selectState,joinSelect)
            get_formList(selectState,jointableName)
        elif parserName == 'tableSource' :
            jointableName = SubElement(joinElt,'tableName')
            jointableName.text = joinSource[joinNum].find('.//tableName/identifier').text

        ## 关联逻辑
        joinLogic = SubElement(joinElt,'JoinOn')
        get_joinColumn(joinExpres[joinNum],joinLogic)
        
def get_joinColumn(node,SubEltroot):
    for expression in node.findall('.//expression') :  ##node.getchildren()
        columnList = []
        idents = expression.findall('.//identifier')
        if  len(idents) == 2: ## expression.tag == 'expression' and
            cols = idents[0].text + '.' + idents[1].text
            columnList.append(cols.upper())

        columnList = list(set(columnList))
        for column in columnList:
            colElt = SubElement(SubEltroot,'Col')
            colElt.text = column
    logicElt = SubElement(SubEltroot,'logic')
    get_logic(node,logicElt)

def get_logic(node,SubEltroot):
    logic = re.sub('\<\/?\w+\>','',tostring(node))
    logic = re.sub('\s\.\s','.',logic)
    logic = re.sub('\s\\(\s','(',logic)
    logic = re.sub('\sAS\s?$','',logic)
    SubEltroot.text = logic

def get_where(node,SubEltroot):
    whereClause = node.find('selectStatement/atomSelectStatement/whereClause/searchCondition/expression')
    if whereClause is not None :
        whereElt = SubElement(SubEltroot,'Where')
        get_joinColumn(whereClause,whereElt)


if __name__ == "__main__":

    #读取xml文件
    tree = read_xml("original.xml")
    tree2 = read_xml("original.xml")
    #生成美化后xml文件，由于会隐藏标点符号，只供给观察,可按情况取消
    prettytree = tree2.getroot()
    prettyXml(prettytree,'\t', '\n')
    tree2.write('prettytree.xml')

    #生成格式化后的xml文件
    createSElt = Element('CreateTable')
    ctaleSElt = SubElement(createSElt,'Ctable')

    ### 获取sql数据
    ## 定义 节点目录 createTableStatement 
    createTableStateEle = tree.find('.//createTableStatement')  

    #找出 创建表的表名
    createTableNameEle  = createTableStateEle.find('tableName')    ## return only Element
    createTableNameElts = createTableNameEle.findall('identifier') ## return a list
    
    if   len(createTableNameElts) == 1 : 
        createTableName = createTableNameElts[0].text
    elif len(createTableNameElts) == 2 : 
        createTableName = createTableNameElts[0].text + "." + createTableNameElts[1].text
    else : 
        createTableName = "Error!"

    #-记录表名
    ctaleSElt.text = createTableName.upper()
    
    ## 更新 节点目录  selectStatementWithCTE
    selectStateWithEle = createTableStateEle.find('.//selectStatementWithCTE')  
    
    ## 找到 全部 with 表 
    withClauseEle = selectStateWithEle.find('withClause')
    if withClauseEle is not None :
        for cteStatementEle in withClauseEle.findall('cteStatement'):
            
            tmpTableName = cteStatementEle.find('identifier').text

            #-记录临时表名
            tmptableSElt = SubElement(createSElt,'Tmptable')
            tmptablenameSElt = SubElement(tmptableSElt,'tableName')
            tmptablenameSElt.text = tmpTableName

            selectStateElt = cteStatementEle.find('.//regularBody')
            get_columnList(selectStateElt,tmptableSElt)
            get_formList(selectStateElt,tmptableSElt)
            get_where(selectStateElt,tmptableSElt)


    selectSElt = SubElement(createSElt,'Select')

    get_columnList(selectStateWithEle,selectSElt)
    get_formList(selectStateWithEle,createSElt)
    get_where(selectStateWithEle,createSElt)



    ##对生成后的xml美化
    newtree = ElementTree(createSElt)
    root = newtree.getroot()
    prettyXml(root,'\t', '\n')
    newtree.write('output.xml')
