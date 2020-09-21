'''
标题：
    SFTP链路下主档数据对比，比如ANF 包含4个文件，分别是：master，ins,upd,gtin

对比策略：
    1. 将源数据txt(数据有固定分隔符)转成csv格式，分隔符不变 =>data_csv
    2. 将源数据txt 放到stfp 服务器上,hub会读取，然后通过接口存入pim mongo =>data_mongo
    3. 读取data_csv , 读取data_mongo ,并遍历 文件中的对象
    4. 对比
        4.1 对比数据的条数是否一致，不一致的情况下退出并提示
        4.2 对比key是否一致，列出不一致的key
        4.3 对比同key不同值的数据，列出
'''
