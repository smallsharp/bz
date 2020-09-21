import json
from common.tool import ExcelTool, GeneralTool
from pim.reebok.const import integration

if __name__ == '__main__':
    # 使用Excel中关键字，查询源数据，然后利用源数据调用HUB_CONVERT接口，对比生成的schemacode 和 预期的schemacode
    condition = {"sourceType": "reebok-erp", "sourceData.MODEL_NO": {"$ne": ""}}
    collection = GeneralTool.get_collection(integration['sit']['uri'], integration['sit']['db'], 'P_SOURCE_REEBOK')
    excel = ExcelTool('../../files/REEBOK类目标题转换规则.xlsx')
    shoelist = excel.get_schemalist_from_sheet('FTW', skiplines=1)
    # otherlist = excel.get_schemalist_from_sheet('OTHER', skip_lines=1)
    # otherlist = excel.get_values_from_sheet('OTHER', skip_lines=1)
    otherlist = excel.merge_dict('OTHER', 'xxx', '1,2', 4, 1)

    print(json.dumps(otherlist, ensure_ascii=False))

    # deal with shoelist
    # successlist, faillist = soure2common.deal_with_ftw(collection, shoelist)
    # print(json.dumps(successlist))
    # print(json.dumps(faillist))

    # successlist, faillist = soure2common.deal_with_other(collection, otherlist)
    # print(successlist)
    # print(faillist)

    # soure2common.deal_with_title(collection, 'APP')
    # soure2common.deal_with_title(collection, 'FTW')
    # soure2common.deal_with_title(collection)

    # {"sourceType": "reebok-erp", "sourceData.DIVISION": {$nin: ['APP', 'FTW']}}
    # deal_with_title('ACC')

    # print('start')
    # collection = GeneralTool.get_collection(integration['sit']['uri'], integration['sit']['db'], 'P_SOURCE_REEBOK')
    # condition = {"sourceType": "reebok-erp", "sourceData.MODEL_NO": {"$ne": ""}}
    # allrows = collection.find(condition)
    # allrows = list(allrows)
    # print(len(allrows))
    # start = time.time()
    # pool = Pool(4)  # 实例化线程池
    # pool.map(Prodcut.conver2common, allrows)  # 开启线程池，get_down函数，list为可迭代对象
    # pool.close()
    # pool.join()
    # end = time.time()
    # print('end')
    # print("共耗时：", end - start)
