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
        self.channel = CHANNEL  # 根据不同渠道，判断如何查商品（商品家接不同平台接口名称不同）
        self.task_items = []

    # def __get_task_item(self):
    #     # origin 赋值
    #     self.item['origin']['schemaCode'] = self.row.get(TITLE_SCHEMACODE)
    #     self.item['origin']['schemaPath'] = self.row.get(TITLE_SCHEMA_PATH)
    #     self.item['origin']['key'] = self.row.get(TITLE_PIM_KEY)
    #     self.item['origin']['vcode'] = self.row.get(TITLE_PIM_VCODE)
    #     # self.item['origin']['type'] = self.row.get(TITLE_PIM_KEY_TYPE)
    #     # self.item['origin']['multiple'] = self.row.get(PIM_MULTIPLE)
    #     # self.item['origin']['position'] = self.row.get(PIM_POSITION)
    #
    #     # target 赋值
    #     self.item['target']['schemaCode'] = self.row.get(TITLE_TARGET_SCHEMACODE)
    #     self.item['target']['key'] = self.row.get(TITLE_TARGET_KEY)
    #     self.item['target']['type'] = self.row.get(TITLE_TARGET_TYPE)
    #     self.item['target']['vcode'] = self.row.get(TITLE_TARGET_VCODE)
    #     self.item['target']['value'] = self.row.get(TITLE_TARGET_VALUE)

    def load_vip_excel(self, filepath):
        '''
        每个人给的模板都不一样，需要单独解析
        :param filepath:
        :return:
        '''
        ext = ExcelTool(filepath)

        # 获取sheet中的所有数据（包括第一行）
        sheet_values = ext.get_sheet_values("唯品会全属性", skiplines=0)
        rowlist = list()
        for i in range(0, ext.getsheet("唯品会全属性").max_row - 1):
            merged_row = ext.merge_list(sheet_values, idx_krow=0, idx_vrow=i + 1)
            rowlist.append(merged_row)

        # 过滤出 需要的数据
        # r1 = filter(lambda x: x[TITLE_PIM_KEY] is not None, rowlist)
        # r1 = filter(lambda x: x[TITLE_TARGET_KEY] is not None, r1)
        # r1 = filter(lambda x: x[TITLE_TARGET_VCODE] is not None, r1)
        # return list(r1)
        return rowlist

    def parser(self, taskitem):
        '''解析数据item数据，格式参考task_items.json'''
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

        taskitem['actual']['productCode'] = pcode

        # 获取商品家的 商品id
        if self.channel == 'TM':
            pid = service.get_tm_pid(pcode)
            # 调用商品家详情接口 获取数据
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

        print('taskItem:{}'.format(json.dumps(taskitem, ensure_ascii=False)))

        return report.values()

    def generate_product_code(self, schemaCode, key, randomstr):
        '''
        productCode 生成规则
        :param schemaCode:
        :param key:
        :param randomstr:
        :return:
        '''
        t = time.strftime("%m%d", time.localtime())
        return f'{schemaCode}_{t}_{key}_{randomstr}'

    def set_value(self, propertiesObj, key, value):
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
                self.task_items.append(task.item)

            filename = "report4.xlsx"
            ext.write_data(filename, f'report{index}', datas=Report().headers())  # 标题
            error_count = 0

            # 第三阶段
            self.logger.info(f'开始执行任务...')
            for taskitem in self.task_items:
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
    ck.run()
