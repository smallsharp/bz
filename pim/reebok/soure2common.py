import time
from pim.reebok.product import Prodcut
from pim.reebok.hub import Convert
from common.tool import GeneralTool
from common.tool import ExcelTool, CommonTool
from pim.reebok.const import integration
import re, json
from pim.reebok import const

model_source = const.get_model_source()


def verify_source_data(source_data, otherlist=None, shoelist=None):
    '''
    :param row: 对应源数据的一条数据
    :param otherlist: 非鞋类的类目数据
    :param shoelist: 鞋类的类目数据
    :return:
    '''
    MODEL_NO = source_data['MODEL_NO']  # src(MODEL_NO)——>model(productNo)
    BARCODE = source_data['BARCODE']  # src(BARCODE)——>model(barcode)
    MODEL_NAME = source_data['MODEL_NAME']  # src(MODEL_NAME )——>model(productName)
    DIVISION = source_data['DIVISION']
    YEAR = source_data['YEAR']  # src(year)——>model(launchInfo.year)
    SEASON_OF_TM = source_data['SEASON_OF_TM']  # src(SEASON_OF_TM)	model(launchInfo.season)
    LOCAL_PRODUCT_TYPE = source_data['LOCAL_PRODUCT_TYPE']
    CATEGORY = source_data['CATEGORY']
    ARTICLE_NO = source_data['ARTICLE_NO']
    SIZE = source_data['SIZE']
    GENDER = source_data['GENDER']

    # 根据源数据转化规则，生成期望得到的数据
    # expect_season = SEASON_OF_TM[2:]  # Q1,Q2,Q3,Q4
    # expect_gender = const.gender_rule.get(GENDER)
    # expect_platformCode = f'Reebok_CN_{ARTICLE_NO}_{SIZE}'  # 平台对接码platformCode=Reebok_CN+主档的ARTICLE_NO字段+主档的SIZE字段，并以“_”分隔符分隔

    # 没有货号的情况下，退出（数据问题）
    if not MODEL_NO:
        print("model_no is None,barcode is :{}".format(BARCODE))
        return

    product_info = Prodcut.find_product_info(product_code=MODEL_NO)

    # 详情接口出现异常，返回None，跳过
    if not product_info:
        print("teminated! find_product_info error,productCode is :{}".format(MODEL_NO))
        return

    # actual_platformCode = Prodcut.get_value_from_variant(BARCODE, 'platformCode', product_info)
    # report_platformCode = Prodcut.generate_error_report(expect_platformCode, actual_platformCode)

    # 从商品详情中获取 实际的schemacode
    actual_schemacode = Prodcut.get_schemacode(product_info)
    # 从Excel中 获取 预期的schemacode
    expect_schemacode = Prodcut.get_expect_schemacode(DIVISION, shoelist, otherlist, source=source_data)
    report = Prodcut.generate_error_report(expect_schemacode, actual_schemacode, source=source_data)

    if report['success'] is False:
        print(report)


def deal_with_ftw(collection, shoelist):
    faillist = []
    successlist = []
    # 遍历鞋类，使用 Excel中提供的关键字,只要MODEL_NAME中包含，则转换为对应的 预期schemacode
    for item in shoelist:
        keyword = item['keyword']
        exp_schemacode = item['schemacode']  # 预期的schemacode
        condition = {"sourceType": "reebok-erp", "sourceData.MODEL_NAME": re.compile("{}".format(keyword))}
        allrows = collection.find(condition)
        allrows = list(allrows)
        print(f'关键字：{keyword},共计查询到：{len(allrows)} 条数据')
        if len(allrows) == 0:
            print(f'没有可用源数据，使用模板数据，model_name使用：{keyword}')
            sourceData = Convert.source_demo
            # update sourceData
            sourceData['MODEL_NAME'] = keyword
            sourceData['DIVISION'] = 'FTW'

            response = Convert.hub_convert(Convert.source_demo)
            actual_schemacode = Convert.get_actual_schemacode(response)  # hub_convert 接口返回的schemacode
            if actual_schemacode == exp_schemacode:
                successlist.append(keyword)
            else:
                faillist.append({'keyword': keyword, 'schemacode': actual_schemacode, 'exp_schemacode': exp_schemacode})
                print(f'expect schemacode：{exp_schemacode},but found：{actual_schemacode}')
            print('-' * 100)

        else:
            # 多条的 取第一条（不是很妥）
            sourceData = allrows[0]['sourceData']
            # verify_source_data(sourceData, otherlist, shoelist)
            response = Convert.hub_convert(sourceData)
            actual_schemacode = Convert.get_actual_schemacode(response)  # hub_convert 接口返回的schemacode
            if actual_schemacode == exp_schemacode:
                successlist.append(keyword)
            else:
                faillist.append({'keyword': keyword, 'schemacode': actual_schemacode, 'exp_schemacode': exp_schemacode})
                print(f'exp_schemacode：{exp_schemacode},found：{actual_schemacode}')
            print('-' * 100)
            # break
    return successlist, faillist


def deal_with_other(collection, otherlist):
    faillist = []
    successlist = []

    for item in otherlist:
        exp_schemacode = item['schemacode']
        condition = {"sourceType": "reebok-erp", "sourceData.CATEGORY": item['category'],
                     "sourceData.LOCAL_PRODUCT_TYPE": item['local_product_type']}

        keyword = f"{item['category']} {item['local_product_type']}"  # 拼接关键字
        allrows = collection.find(condition)
        allrows = list(allrows)
        print(f"关键字：{keyword},共计查询到：{len(allrows)} 条数据")
        if len(allrows) == 0:
            print(f'没有可用源数据，使用模板数据，model_name使用：{keyword}')
            sourceData = Convert.source_demo
            # 更新soureceData
            sourceData['CATEGORY'] = item['category']
            sourceData['DIVISION'] = 'HW'
            sourceData['LOCAL_PRODUCT_TYPE'] = item['local_product_type']
            response = Convert.hub_convert(Convert.source_demo)
            actual_schemacode = Convert.get_actual_schemacode(response)  # hub_convert 接口返回的schemacode
            if actual_schemacode == exp_schemacode:
                successlist.append(keyword)
            else:
                faillist.append(
                    {'keyword': keyword, 'schemacode': actual_schemacode, 'exp_schemacode': exp_schemacode})
                print(f'expect schemacode：{exp_schemacode},but found：{actual_schemacode}')
            print('-' * 100)
        else:
            for row in allrows:
                sourceData = row['sourceData']
                # verify_source_data(sourceData, otherlist, shoelist)
                response = Convert.hub_convert(sourceData)
                actual_schemacode = Convert.get_actual_schemacode(response)  # hub_convert 接口返回的schemacode
                if actual_schemacode == exp_schemacode:
                    successlist.append(keyword)
                else:
                    faillist.append(
                        {'keyword': keyword, 'schemacode': actual_schemacode, 'exp_schemacode': exp_schemacode})
                    print(f'expect schemacode：{exp_schemacode},but found：{actual_schemacode},keyword:{keyword}')
                print('-' * 100)
                break
    return json.dumps(successlist), json.dumps(faillist)


def handle_title(collection):
    reportlist = []
    condition = {"sourceType": "reebok-erp", "catalog": "REEBOK"}
    # 去重后的MODEL_NAME
    all_modelname = collection.find(condition).distinct('sourceData.MODEL_NAME')
    all_modelname = list(all_modelname)

    print(f'共计查询到distinct modelname：{len(all_modelname)} 条数据')
    for index, modelname in enumerate(all_modelname):
        # 通过modelname 查询一条数据
        condition = {"sourceType": "reebok-erp", "sourceData.MODEL_NAME": modelname}
        row = collection.find_one(condition)
        source = row['sourceData']
        #### 需要统计modelname 是否全部覆盖了规则
        expect_title = Convert.get_expect_title(source)
        response = Convert.hub_convert(source)
        actual_title = Convert.get_value_from_response(response, 'title', positon='master')
        report = Prodcut.generate_error_report(expect_title, actual_title, source=source)
        # print(f'正在处理：{sourceData["BARCODE"]},modelname：{modelname},期望：{expect_title},实际：{actual_title}')
        if report:
            reportlist.append(report)

    ExcelTool.write(reportlist, ['MODEL_NO', 'BARCODE', 'DIVISION', 'KEYWORD', 'EXP_VALUE', 'ACT_VALUE'],
                    filename='report.xlsx', sheetname='title')


def handle_title_rule(rulelist):
    '''
    遍历标题规则
    '''
    # 规则1：性别字典
    gender_maps = CommonTool.get_maps('title-gender', rulelist)
    for gender in gender_maps:
        model_source['GENDER'] = gender
        exp_title = Convert.get_expect_title(model_source)
        response = Convert.hub_convert(model_source)
        actual_title = Convert.get_value_from_response(response, 'title')  # hub_convert 接口返回的schemacode
        if exp_title != actual_title:
            print(exp_title == actual_title)

    print('rule1 end......')

    # 规则2（FTW）:FTW类 modelName的转换逻辑，如MODEL_NAME的值不在下表中，则保留原MODEL_NAME
    modelname1_maps = CommonTool.get_maps('title_modelname1', rulelist)
    for k in modelname1_maps:
        model_source['DIVISION'] = 'FTW'
        model_source['MODEL_NAME'] = k
        exp_title = Convert.get_expect_title(model_source)
        response = Convert.hub_convert(model_source)
        actual_title = Convert.get_value_from_response(response, 'title')  # hub_convert 接口返回的schemacode
        if exp_title != actual_title:
            print(f"{exp_title == actual_title}, k={k},==>{exp_title}")

    print('rule2 end......')

    # 规则3:PRODUCT_TYPE的转换逻辑，PRODUCT_TYPE不在下表中就中文名称就转换为空
    product_type_maps = CommonTool.get_maps('title_product_type', rulelist)
    for k in product_type_maps:
        model_source['DIVISION'] = 'FTW'
        model_source['PRODUCT_TYPE'] = k
        exp_title = Convert.get_expect_title(model_source)
        response = Convert.hub_convert(model_source)
        actual_title = Convert.get_value_from_response(response, 'title')  # hub_convert 接口返回的schemacode
        if exp_title != actual_title:
            print(f"{k},==>{exp_title},actual:{actual_title}")

    print('rule3 end......')

    # 规则4:鞋类商品名称的转换逻辑，不在下表的转换中的，统一转化为【休闲鞋】
    product_type_maps = CommonTool.get_maps('title_modelname4', rulelist)
    for k1 in product_type_maps:
        model_source['DIVISION'] = 'FTW'
        model_source['MODEL_NAME'] = k1
        exp_title = Convert.get_expect_title(model_source)
        response = Convert.hub_convert(model_source)
        actual_title = Convert.get_value_from_response(response, 'title')  # hub_convert 接口返回的schemacode
        if exp_title != actual_title:
            print(f"{k1},==>{exp_title},actual:{actual_title}")

    print('rule4 end......')

    # 规则5:APP类 modelName的转换逻辑，如MODEL_NAME的值不在下表中，则保留MODEL_NAME
    product_type_maps = CommonTool.get_maps('title_modelname5', rulelist)
    for k1 in product_type_maps:
        model_source['DIVISION'] = 'APP'
        model_source['MODEL_NAME'] = k1
        exp_title = Convert.get_expect_title(model_source)
        response = Convert.hub_convert(model_source)
        actual_title = Convert.get_value_from_response(response, 'title')  # hub_convert 接口返回的schemacode
        if exp_title != actual_title:
            print(f"{k1},==>{exp_title},actual:{actual_title}")
    print('rule5 end......')

    # 规则6:服装配饰对应名称转换规则
    product_type_maps = CommonTool.get_maps('title_app', rulelist)
    for k1 in product_type_maps:
        CATEGORY, LOCAL_PRODUCT_TYPE = str(k1).split('_')
        model_source['DIVISION'] = 'APP'
        model_source['CATEGORY'] = CATEGORY
        model_source['LOCAL_PRODUCT_TYPE'] = LOCAL_PRODUCT_TYPE
        exp_title = Convert.get_expect_title(model_source)
        response = Convert.hub_convert(model_source)
        actual_title = Convert.get_value_from_response(response, 'title')  # hub_convert 接口返回的schemacode
        if exp_title != actual_title:
            print(f"{k1},==>{exp_title},actual:{actual_title}")
    print('rule6 end......')


def handle_schemacode():
    print('=====>>开始执行校验类目转换规则')
    start = time.time()
    collection = GeneralTool.get_collection(integration['sit']['uri'], integration['sit']['db'], 'p_source')
    reportlist = []

    # 鞋类的类目 和MODEL_NAME有直接关系，因此按MODEL_NAME 去重，然后使用该MODEL_NAME查到sourceData 入库验证
    # condition_ftw = {"catalog": "REEBOK", "sourceType": "reebok-erp", "sourceData.DIVISION": "FTW"}
    # modelnames = collection.find(condition_ftw).distinct('sourceData.MODEL_NAME')
    # modelnames = list(modelnames)
    # print(f'MODEL_NAME 总计：{len(modelnames)}条')
    #
    # for index, modelname in enumerate(modelnames):
    #     print(f'当前是第{index + 1}个，正在验证的MODEL_NAME:{modelname}')
    #     row = collection.find_one({"catalog": "REEBOK", "sourceType": "reebok-erp", "sourceData.MODEL_NAME": modelname})
    #     result = Prodcut.handle_source(row)
    #     if result:
    #         reportlist.append(result)

    # 非鞋类  使用CATEGORY+LOCAL_PRODUCT_TYPE 组合匹配类目
    condition_other = {"catalog": "REEBOK", "sourceType": "reebok-erp", "sourceData.DIVISION": {"$ne": "FTW"}}
    allrows = collection.find(condition_other)
    print(f'非鞋类总计源数据条数：{len(allrows := list(allrows))}')
    # allrows = list(allrows)

    keyword_list = list()
    for row in allrows:
        source = row['sourceData']
        CATEGORY = source['CATEGORY']
        LOCAL_PRODUCT_TYPE = source['LOCAL_PRODUCT_TYPE']
        keyword = f'{CATEGORY}_{LOCAL_PRODUCT_TYPE}'
        keyword_list.append(keyword)
    print(f"非鞋类的关键字CATEGORY_LOCAL_PRODUCT_TYPE，去重后总计：{len(set(keyword_list))}条")
    distinct_rows = list(set(keyword_list))
    for keyword in distinct_rows:
        CATEGORY, LOCAL_PRODUCT_TYPE = keyword.split('_')
        cdn = {"sourceType": "reebok-erp", "sourceData.CATEGORY": CATEGORY,
               "sourceData.LOCAL_PRODUCT_TYPE": LOCAL_PRODUCT_TYPE, "sourceData.DIVISION": {"$ne": "FTW"}}
        row = collection.find_one(cdn)
        report = Prodcut.handle_source(row)
        if report:
            reportlist.append(report)

    # pool = Pool(4)  # 实例化线程池
    # pool.map(Prodcut.handle_source, allrows)  # 开启线程池，get_down函数，list为可迭代对象
    # pool.close()
    # pool.join()
    end = time.time()
    print(f'总计错误数：{len(reportlist)}')

    if len(reportlist) > 0:
        ExcelTool.write(reportlist, ['MODEL_NO', 'BARCODE', 'DIVISION', 'KEYWORD', 'EXP_VALUE', 'ACT_VALUE'],
                        filename='report.xlsx', sheetname='schemaCode')
    print('类目转换规则校验结束<<=====')
    print("共耗时：", end - start)


if __name__ == '__main__':
    # handle_schemacode()

    collection = GeneralTool.get_collection(integration['sit']['uri'], integration['sit']['db'], 'p_source')
    handle_title(collection)
