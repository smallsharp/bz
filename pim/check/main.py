# coding=utf8
from common.tool import ExcelTool
import os
import time
import json
import random
from pim.check import const
from pim.check.const import *
# from pim.check.const import Report
from itertools import groupby
from pim.check import service
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

skipsheet = []


class Check():

    def __init__(self):
        self.logger = logging.getLogger(Check.__name__)
        self.__setup()

    def __setup(self):
        '''
         1. get filerows from excel, and merge title and other row, merged rows like follows:
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

         2. convert merged rows to task rows(cause different excel has different data), task rows refer to "self.__item"

        '''
        self.channel = const.CHANNEL  # 根据不同渠道，判断如何查商品（商品家接不同平台接口名称不同）
        self.filerows = self.load_vip_excel('./files/TS/vip_mapping.xlsx')
        self.items = self.__load_task_items(self.filerows)
        self.logger.info('load file over, length of items is :{}'.format(len(self.items)))

    @staticmethod
    def __covert_row2item(row: dict):
        '''
          convert merged row to task item row, refer to "const.get_item_model()"
        '''
        item = const.get_item_model()
        # origin 赋值
        item['origin']['schemaCode'] = row.get(TITLE_SCHEMACODE)
        item['origin']['schemaPath'] = row.get(TITLE_SCHEMA_PATH)
        item['origin']['key'] = row.get(TITLE_PIM_KEY)
        item['origin']['vcode'] = row.get(TITLE_PIM_VCODE)
        # item['origin']['type'] = self.row.get(TITLE_PIM_KEY_TYPE)
        # item['origin']['multiple'] = self.row.get(PIM_MULTIPLE)
        # item['origin']['position'] = self.row.get(PIM_POSITION)

        # target 赋值
        item['target']['schemaCode'] = row.get(TITLE_TARGET_SCHEMACODE)
        item['target']['key'] = row.get(TITLE_TARGET_KEY)
        item['target']['type'] = row.get(TITLE_TARGET_TYPE)
        item['target']['vcode'] = row.get(TITLE_TARGET_VCODE)
        item['target']['value'] = row.get(TITLE_TARGET_VALUE)
        return item

    def __load_task_items(self, merged_file_rows):
        return [self.__covert_row2item(row) for row in merged_file_rows]

    def load_vip_excel(self, filepath):
        '''
          load file and merge row to dict
        '''
        ext = ExcelTool(filepath)
        ws = ext.get_worksheet("唯品会全属性")
        sheet_values = list(ext.get_sheet_values2(ws))
        # print(json.dumps(sheet_values, ensure_ascii=False))
        filerows = list()
        for i in range(0, ws.max_row - 1):
            merged_row = ext.merge_list(sheet_values, idx_key_row=0, idx_value_row=i + 1)
            filerows.append(merged_row)

        # 过滤出 需要的数据
        # r1 = filter(lambda x: x[TITLE_PIM_KEY] is not None, rowlist)
        # r1 = filter(lambda x: x[TITLE_TARGET_KEY] is not None, r1)
        # r1 = filter(lambda x: x[TITLE_TARGET_VCODE] is not None, r1)
        # return list(r1)
        return filerows

    def parser(self, taskitem):

        # 解析数据item数据，格式参考task_items.json
        self.logger.info(f'正在解析:{taskitem}')
        # self.logger.info('正在处理==>>:{}'.format(json.dumps(taskitem, ensure_ascii=False)))
        # 序列解包
        schemaCode, schemaPath, key, vcode, _, _, position = taskitem['origin'].values()
        target_schema, target_key, _, target_vcode, target_value = taskitem['target'].values()

        # randomstr = random.randrange(1000, 9999, step=1)
        pcode = self.generate_product_code(schemaCode, key, randomstr=vcode)  # 生成product_code
        sku1 = 'K1_{}'.format(pcode)
        sku2 = 'K2_{}'.format(pcode)
        # 获取滔博的商品参数
        payload = const.gen_ts_body(pcode, schemaCode, schemaPath, skus=[sku1, sku2])
        taskitem['actual']['productCode'] = pcode

        # 区分属性放到master 还是 variants
        if position == "SKU" or const.SUB_POSITION.get(key) == "SKU":
            self.set_value(payload['variants'][0]['properties'], key, vcode)
            position = 'SKU'
        else:
            self.set_value(payload['master']['properties'], key, vcode)
            position = 'SPU'  ## 后续需要用到

        # 创建、发布商品
        service.create_product(payload)
        service.release_product(pcode)

        if self.channel == 'TM':
            pid = service.get_tm_pid(pcode)  # 获取商品家的 商品id
            actual_vcode, actual_type = service.get_tm_value(pid, target_key)
            remark = ''

        elif self.channel == 'VIP':
            # 通过货品ID 到平台查询商品，查到商品后{"attributeId":"1665"} 找到属性对应数据
            try:
                response = service.get_vip_value(pcode, attrvalue=str(target_key), position=position)
                taskitem['actual']['schemaCode'] = response.get('schemaCode')
                taskitem['actual']['vcode'] = response.get('actual_vcode')
                taskitem['actual']['value'] = response.get('actual_value')
                taskitem['actual']['remark'] = response.get('remark')
            except Exception as e:
                # 记录请求的异常
                taskitem['actual']['remark'] = str(e)
        else:
            # pid = service.get_jd_pid(pcode)
            # self.logger.info(f'position:{position}')
            response = service.get_jd_value(pcode, attrValue=str(target_key), position=position, skuValue1=sku1)
            taskitem['actual']['schemaCode'] = response.get('schemaCode')
            taskitem['actual']['vcode'] = response.get('vcode')
            taskitem['actual']['value'] = response.get('value')
            taskitem['actual']['remark'] = response.get('remark')

        report = Report(taskitem)
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

    def run(self):
        self.logger.info('start run')
        start = time.time()

        folder = "files/TS"
        filelist = os.listdir(folder)
        ext = ExcelTool()
        for index, filename in enumerate(filelist):
            # self.logger.info(f'开始解析文件：{filename}')
            filepath = os.path.abspath(os.path.join(os.path.dirname(__file__), './{}/{}'.format(folder, filename)))
            self.logger.info('load file:{}'.format(filepath))

            # 第一阶段,解析Excel
            filerows = self.load_vip_excel(filepath)
            self.logger.info('load file over, data length:{}'.format(len(filerows)))

            # 过滤不合规的数据【设置截取行】
            filerows = filter(lambda x: x[TITLE_PIM_KEY] is not None, filerows[8863:])
            filerows = filter(lambda x: x[TITLE_TARGET_KEY] is not None, filerows)
            filerows = list(filter(lambda x: x[TITLE_TARGET_VCODE] is not None, filerows))

            self.logger.info('filter file over, data length:{}'.format(len(filerows)))

            # 第二阶段，拼装可执行的格式化 task_item数据 ###todo
            for row in filerows:
                task = Task(row=row)
                self.items.append(task.item)

            filename = "report4.xlsx"
            ext.write_data(filename, f'report{index}', datas=Report().headers())  # 标题
            error_count = 0

            # 第三阶段
            self.logger.info(f'开始执行任务...')
            for taskitem in self.items:
                # print('正在解析：{}'.format(json.dumps(taskitem, ensure_ascii=False)))
                try:
                    report = self.parser(taskitem)
                    ext.write_data(filename, f'report{index}', list(report))
                except Exception as e:
                    error_count += 1
                    self.logger.error('Error：{}，detail==>>{}'.format(error_count, e))
                    # print(e.with_traceback())
                if error_count >= 3:
                    self.logger.error('Task Error：{}'.format(taskitem))
                    continue
        end = time.time()
        self.logger.info(f"共耗时：{round(end - start, 2)}")


if __name__ == '__main__':
    ck = Check()
    from multiprocessing.dummy import Pool
    # 实例化线程池
    pool = Pool(1)

    # Apply `func` to each element in `iterable`, collecting the results in a list that is returned.
    result = pool.map(ck.parser, ck.items)
    pool.close()
    pool.join()
