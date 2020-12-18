# coding=utf8
from common.tool import ExcelTool
from configparser import RawConfigParser
import os, time, json, random
from pim.check import model
from pim.check import service
from itertools import groupby
from multiprocessing.dummy import Pool
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class Check():

    def __init__(self, filepath=None, inifile='./conf/topsports.ini'):
        self.logger = logging.getLogger(Check.__name__)
        self.__load_conf(inifile)
        if filepath:
            self.filepath = filepath
            self._setup()

    def _setup(self):
        '''
         1. get filerows from excel, and merge title and value row, merged rows like follows:
         [{
            "TS类目": "童鞋-儿童凉鞋-沙滩凉鞋",
            "TS类目ID": "TS030202",
            "平台类目": "母婴鞋服/童鞋/儿童凉鞋",
            "平台类目ID": 391185,
            "TS类目属性": "*商品名称",
            "TS类目属性ID": "itemName",
            "TS类目属性值": null,
            "TS类目属性值ID": null,
            "平台类目属性": "商品",
            "平台类目属性ID": null,
            "平台类目属性值": null,
            "平台类目属性值ID": null
        }]

         2. convert merged rows to task rows(cause different excel has different data), task rows refer to "self.items"

        '''
        # self.channel = const.CHANNEL  # 根据不同渠道，判断如何查商品（商品家接不同平台接口名称不同）
        self.filerows = self.__load_xlsx_file(self.filepath)
        self.items = self.__convert_items(self.filerows)
        self.logger.info('load file and convert item over, length of items is :{}'.format(len(self.items)))

    def __load_conf(self, inifile):
        ''' 加载配置文件，获取基础配置信息 '''
        self.conf = RawConfigParser()
        self.conf.optionxform = str
        self.conf.read(inifile, encoding='utf-8-sig')

        # 获取基础配置
        self.channel = self.conf.get('Common', 'channel')
        self.domain = self.conf.get('Host', 'ross')
        self.header_ross = dict(self.conf.items('headers_ross'))
        self.header_pim = dict(self.conf.items('headers_pim'))

        fieldmap = self.__get_field_mapping()

        # pim
        self.TITLE_SCHEMACODE = fieldmap.get('schemaCode')
        self.TITLE_SCHEMA_PATH = fieldmap['schemaPath']
        self.TITLE_PIM_KEY = fieldmap['attr']
        self.TITLE_PIM_KEY_NAME = fieldmap['attrName']
        self.TITLE_PIM_KEY_TYPE = fieldmap['attrType']
        self.TITLE_PIM_VCODE = fieldmap['valueId']
        self.TITLE_PIM_BRAND = fieldmap.get('brand')
        self.PIM_MULTIPLE = fieldmap.get('multiple')
        self.PIM_POSITION = fieldmap.get('position')

        # target title
        self.TITLE_TARGET_KEY = fieldmap['targetAttr']
        self.TITLE_TARGET_KEY_NAME = fieldmap['targetAttrName']
        self.TITLE_TARGET_TYPE = fieldmap['targetAttrType']
        self.TITLE_TARGET_VCODE = fieldmap['targetValueId']
        self.TITLE_TARGET_VALUE = fieldmap['targetValue']
        self.TITLE_TARGET_SCHEMACODE = fieldmap.get('targetSchemaCode')

        # 指定位置的参数
        self.SUB_POSITION = dict(self.conf.items('Position'))

        # print(json.dumps(self.fieldmap, ensure_ascii=False))

    def __get_field_mapping(self):
        if self.channel == 'TM':
            return dict(self.conf.items('TMFieldMapping'))
        elif self.channel == 'VIP':
            return dict(self.conf.items('VIPFieldMapping'))
        elif self.channel == 'JD':
            return dict(self.conf.items('JDFieldMapping'))
        else:
            raise KeyError(f"{self.channel} is not supported yet!")

    def __covert_row2item(self, row: dict):
        '''convert merged row to task item row, refer to "const.get_item_model()"'''
        item = model.get_item_model()
        item['origin']['schemaCode'] = row.get(self.TITLE_SCHEMACODE)
        item['origin']['schemaPath'] = row.get(self.TITLE_SCHEMA_PATH)
        item['origin']['key'] = row.get(self.TITLE_PIM_KEY)
        item['origin']['vcode'] = row.get(self.TITLE_PIM_VCODE)
        item['origin']['brand'] = row.get(self.TITLE_PIM_BRAND)
        # item['origin']['type'] = row.get(self.TITLE_PIM_KEY_TYPE)
        # item['origin']['position'] = row.get(self.PIM_POSITION)

        # target 赋值
        item['target']['schemaCode'] = row.get(self.TITLE_TARGET_SCHEMACODE)
        item['target']['key'] = row.get(self.TITLE_TARGET_KEY)
        item['target']['type'] = row.get(self.TITLE_TARGET_TYPE)
        item['target']['vcode'] = row.get(self.TITLE_TARGET_VCODE)
        item['target']['value'] = row.get(self.TITLE_TARGET_VALUE)
        return item

    def __convert_items(self, merged_file_rows):
        return [self.__covert_row2item(row) for row in merged_file_rows]

    def __load_xlsx_file(self, filepath):
        '''load file and merge row to dict'''
        ext = ExcelTool(filepath)
        ws = ext.get_active_worksheet()
        sheet_values = list(ext.get_sheet_values2(ws))
        filerows = list()
        for i in range(0, ws.max_row - 1):
            merged_row = ext.merge_list(sheet_values, idx_key_row=0, idx_value_row=i + 1)
            filerows.append(merged_row)

        # 过滤出 需要的数据
        filerows = filter(lambda x: x[self.TITLE_PIM_KEY] is not None, filerows)
        filerows = filter(lambda x: x[self.TITLE_PIM_VCODE] is not None, filerows)
        filerows = filter(lambda x: x[self.TITLE_TARGET_KEY] is not None, filerows)
        filerows = filter(lambda x: x[self.TITLE_TARGET_VCODE] is not None, filerows)
        return filerows

    def parser(self, taskitem):
        # 解析数据item数据，格式参考items.json
        schemacode, schemapath, key, vcode, _, position, brand = taskitem['origin'].values()
        target_sc, target_key, _, target_vcode, target_value = taskitem['target'].values()

        randomstr = random.randrange(1, 9999, step=1)
        pcode = self.generate_product_code(schemacode, key, randomstr=f'{vcode}_{randomstr}')  # 生成product_code
        sku1 = 'K1_{}'.format(pcode)
        sku2 = 'K2_{}'.format(pcode)
        taskitem['actual']['productCode'] = pcode

        # 获取滔博的商品参数
        payload = model.gen_ts_body(pcode, schemacode, skus=[sku1, sku2], schemaPath=schemapath, brand=brand)

        # 区分属性放到 p 还是 v
        if position == "SKU" or self.SUB_POSITION.get(key) == "SKU":
            self.set_value(payload['variants'][0]['properties'], key, vcode)
            position = 'SKU'
            taskitem['origin']['position'] = 'SKU'
        else:
            self.set_value(payload['master']['properties'], key, vcode)
            position = 'SPU'  ## 后续需要用到
            taskitem['origin']['position'] = 'SPU'

        # pim create and release product
        pimService = service.PimService(self.domain, self.header_pim)
        pimService.create_product(payload)
        pimService.release_product(pcode)

        # ross check
        rossService = service.RossService(self.domain, self.header_ross)

        if self.channel == 'TM':
            try:
                pid = rossService.get_product_id_tm(pcode, target_sc)  # 通过货号+类目 查询商品ID，查不到报错
                response = rossService.get_product_tm(pid, target_key)
                taskitem['actual']['schemaCode'] = target_sc
                taskitem['actual']['vcode'] = response.get('vcode')
                taskitem['actual']['value'] = response.get('value')
                taskitem['actual']['remark'] = response.get('remark')
            except Exception as e:
                taskitem['actual']['remark'] = str(e)
        elif self.channel == 'VIP':
            # 通过货品ID 到平台查询商品，查到商品后{"attributeId":"1665"} 找到属性对应数据
            try:
                response = rossService.get_product_vip(pcode, attrvalue=str(target_key), position=position)
                taskitem['actual']['schemaCode'] = response.get('schemaCode')
                taskitem['actual']['vcode'] = response.get('actual_vcode')
                taskitem['actual']['value'] = response.get('actual_value')
                taskitem['actual']['remark'] = response.get('remark')
            except Exception as e:
                taskitem['actual']['remark'] = str(e)
        else:
            response = rossService.get_jd_value(pcode, attrValue=str(target_key), position=position, skuValue1=sku1)
            taskitem['actual']['schemaCode'] = response.get('schemaCode')
            taskitem['actual']['vcode'] = response.get('vcode')
            taskitem['actual']['value'] = response.get('value')
            taskitem['actual']['remark'] = response.get('remark')
        self.logger.info(f'正在处理:{json.dumps(taskitem, ensure_ascii=False)}')
        report = model.Report(taskitem)
        return report.values()

    def parse_pim(self, taskitem):

        # 解析数据item数据，格式参考items.json
        schemacode, schemapath, key, vcode, _, position, brand = taskitem['origin'].values()
        target_sc, target_key, _, target_vcode, target_value = taskitem['target'].values()

        randomstr = random.randrange(1, 9999, step=1)
        pcode = self.generate_product_code(schemacode, key, randomstr=f'{vcode}_{randomstr}')  # 生成product_code
        sku1 = 'K1_{}'.format(pcode)
        sku2 = 'K2_{}'.format(pcode)
        taskitem['actual']['productCode'] = pcode

        # 获取滔博的商品参数
        payload = model.gen_ts_body(pcode, schemacode, skus=[sku1, sku2], schemaPath=schemapath, brand=brand)

        # 区分属性放到 p 还是 v
        if position == "SKU" or self.SUB_POSITION.get(key) == "SKU":
            self.set_value(payload['variants'][0]['properties'], key, vcode)
            taskitem['origin']['position'] = 'SKU'

        else:
            self.set_value(payload['master']['properties'], key, vcode)
            taskitem['origin']['position'] = 'SPU'  # 后续需要用到
        try:
            # pim create and release product
            pimService = service.PimService(self.domain, self.header_pim)
            pimService.create_product(payload)
            pimService.release_product(pcode)
        except Exception as e:
            taskitem['actual']['remark'] = str(e)
            self.logger.error(f'货品{pcode}创建发布过程中异常：{str(e)}')

        return taskitem

    def parse_ross(self, taskitem):

        # 解析数据item数据，格式参考items.json
        schemacode, schemapath, key, vcode, _, position, brand = taskitem['origin'].values()
        target_sc, target_key, _, target_vcode, target_value = taskitem['target'].values()
        pcode = taskitem['actual']['productCode']

        # ross check
        rossService = service.RossService(self.domain, self.header_ross)

        if self.channel == 'TM':
            try:
                pid = rossService.get_product_id_tm(pcode, target_sc)  # 通过货号+类目 查询商品ID，查不到报错
                taskitem['actual']['schemaCode'] = target_sc  # 能查到
                response = rossService.get_product_tm(pid, target_key)
                taskitem['actual']['vcode'] = response.get('vcode')
                taskitem['actual']['value'] = response.get('value')
                taskitem['actual']['remark'] = response.get('remark')
            except Exception as e:
                taskitem['actual']['remark'] = str(e)
        elif self.channel == 'VIP':
            # 通过货品ID 到平台查询商品，查到商品后{"attributeId":"1665"} 找到属性对应数据
            try:
                response = rossService.get_product_vip(pcode, attrvalue=str(target_key), position=position)
                taskitem['actual']['schemaCode'] = response.get('schemaCode')
                taskitem['actual']['vcode'] = response.get('vcode')
                taskitem['actual']['value'] = response.get('value')
                taskitem['actual']['remark'] = response.get('remark')
            except Exception as e:
                taskitem['actual']['remark'] = str(e)
        else:
            response = rossService.get_jd_value(pcode, attrValue=str(target_key), position=position)
            taskitem['actual']['schemaCode'] = response.get('schemaCode')
            taskitem['actual']['vcode'] = response.get('vcode')
            taskitem['actual']['value'] = response.get('value')
            taskitem['actual']['remark'] = response.get('remark')
        self.logger.info(f'正在处理:{json.dumps(taskitem, ensure_ascii=False)}')
        report = model.Report(taskitem)
        return report.values()

    @staticmethod
    def generate_product_code(schemaCode, key, randomstr):
        t = time.strftime("%m%d", time.localtime())
        return f'{schemaCode}_{t}_{key}_{randomstr}'

    @staticmethod
    def set_value(propertiesObj, key, value):
        for word in key.split('.'):
            obj = dict(propertiesObj).get(word, value)
            if isinstance(obj, (str, int, float, list)):  # 取出的值是基本数据类型
                propertiesObj[word] = value
            else:
                propertiesObj = obj


def main():
    now = lambda: time.time()

    # 拼接文件路径   放在files中的第一个文件会被执行
    filepath = os.path.abspath(os.path.join(os.path.dirname(__file__), 'files', os.listdir('files')[0]))
    ck = Check(filepath=filepath)

    # 多任务执行 可能导致队列阻塞，改成循环执行
    items = [ck.parse_pim(item) for item in ck.items]  ## 如需测试,可使用分片

    name = f'yougou_' + time.strftime('%m%d', time.localtime())

    # 将前半部分数据持久化
    with open(f'{name}.txt', mode='w', encoding='utf8') as file:
        file.write(json.dumps(items, ensure_ascii=False))

    ck.logger.info('pim 任务处理完成')

    # for i in range(0, 6):
    #     ck.logger.info('sleep for a while')
    #     time.sleep(10)
    # ck.logger.info('ross 任务开始')
    # pool = Pool(4)
    # reportlist = pool.map(ck.process_ross, items)
    # pool.close()
    # pool.join()
    # ck.logger.info('ross 任务处理完成')
    #
    # # 记录测试报告
    # ext = ExcelTool(f"../report/report_{name}.xlsx")
    # ext.append(sheetname=name, datas=model.Report().headers())  # 标题
    # for data in reportlist:
    #     ext.append(sheetname=name, datas=data)
    #
    # ext.save()
    # end = time.time()
    # ck.logger.info('report 完成')
    # ck.logger.info(f'time:{round(end - start, 2)}')


def main2():
    start = time.time()
    ck = Check()

    name = 'yougo'
    with open('yougou_1215.txt', encoding='utf8') as file:
        datas = file.read()
        items = json.loads(datas)

        ck.logger.info('ross 任务开始')
        pool = Pool()
        reportlist = pool.map(ck.parse_ross, items)
        pool.close()
        pool.join()
        ck.logger.info('ross 任务处理完成')

        # 记录测试报告
        ext = ExcelTool("../report/report_tm_1215.xlsx")
        sheetname = f'{name}_' + time.strftime('%m%d%H%M', time.localtime())
        ext.append(sheetname=sheetname, datas=model.Report().headers())  # 标题
        for data in reportlist:
            ext.append(sheetname=sheetname, datas=data)

        ext.save()
        end = time.time()
        ck.logger.info('report 完成')
        ck.logger.info(f'time:{round(end - start, 2)}')


if __name__ == '__main__':
    main2()
