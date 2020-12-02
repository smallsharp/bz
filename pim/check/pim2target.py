# coding=utf8
from common.tool import ExcelTool
import os
import time
import json
import random
from pim.check import const
from pim.check.const import *
from itertools import groupby
from pim.check import service
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

skipsheet = []


class Report(object):
    '''测试报告'''

    def __init__(self, **kwargs):
        self.schema = kwargs.get('schema')
        self.pimkey = kwargs.get('key')
        self.vcode = kwargs.get('vcode')
        self.target_key = kwargs.get('target_key')
        self.target_vcode = kwargs.get('target_value')
        self.actual_vcode = kwargs.get('actual_vcode')
        self.actual_valias = kwargs.get('actual_valias')
        self.target_schemaCode = kwargs.get('target_schemaCode')
        self.actual_schemaCode = kwargs.get('actual_schemaCode')
        self.target_schemaCode = kwargs.get('target_schemaCode')
        self.pcode = kwargs.get('pcode')
        self.result_schema = kwargs.get('result_schema')
        self.result_vcode = kwargs.get('result_vcode')
        self.remark = kwargs.get('remark')

    def get_keys(self):
        return list(self.__dict__.keys())

    def generate_report(self):
        # 值必须完全相等，且不等于None
        if isinstance(self.target_vcode, list) and isinstance(self.actual_vcode, list):
            self.target_vcode.sort()
            self.actual_vcode.sort()
        r1 = '通过' if self.target_vcode == self.actual_vcode else '失败'
        if r1 == '失败':
            r1 = '通过' if [self.vcode] == self.actual_valias else '失败'
            self.remark = f"{self.remark}code对比失败，value对比成功"
        r2 = '通过' if self.target_schemaCode == self.actual_schemaCode else '失败'
        self.result_vcode = r1
        self.result_schema = r2
        return self.__dict__


class Check():

    def __init__(self):
        self.logger = logging.getLogger(Check.__name__)
        self.logger.info('check init')
        self.channel = CHANNEL
        self.task_items = []

    def loadfile(self, filepath):
        ext = ExcelTool(filepath)
        for sheetname in ext.get_all_sheet():
            # 过滤出 以属性结尾的sheet
            if not sheetname.endswith('属性') or sheetname in skipsheet:
                continue
            self.logger.info('load sheet:{}'.format(sheetname))
            att_sheet_values = ext.get_sheet_values(sheetname, skiplines=0)  # 属性sheet_values

            sheetname2 = sheetname.replace('属性', '属性值')
            att_value_list = self.get_merged_rows(ext, sheetname2)  # 属性值对象 列表
            # 遍历 <属性sheet>
            for i in range(0, ext.getsheet(sheetname).max_row - 1):
                merged_row = ext.merge_list(att_sheet_values, idx_krow=0, idx_vrow=i + 1)
                # 跳过 pim.key|target.key is none
                if not merged_row[TITLE_PIM_KEY] or not merged_row[TITLE_TARGET_KEY]:
                    continue
                # 属性sheet中 使用到的字段
                schema = merged_row[TITLE_SCHEMACODE]
                pim_key = merged_row[TITLE_PIM_KEY]  # 属性键值
                pim_type = merged_row[TITLE_PIM_KEY_TYPE]  # 属性类型
                target_key = merged_row[TITLE_TARGET_KEY]  # 京东字段|天猫字段
                target_type = merged_row[TITLE_TARGET_TYPE]
                target_schema = merged_row[TITLE_TARGET_SCHEMACODE]  # 终端类目
                if pim_type == PIM_INPUT:
                    seed = random.randrange(1, 9999, step=1)
                    task = Task(schema, merged_row, vcode=str(seed), target_vcode=str(seed))
                    self.task_items.append(task.item)
                else:  # 选择型
                    # 再次过滤att_value_list 过滤出 属性值sheet.京东字段值==属性sheet.京东字段值
                    myrowlist = list(filter(lambda x: x[TITLE_TARGET_KEY] == target_key, att_value_list))
                    options = self.group_by(myrowlist, TITLE_PIM_KEY, TITLE_PIM_VCODE)  # 按pim.key聚合，key_options.json
                    if not options.get(pim_key):
                        self.logger.warning('属性值sheet中缺失选项值，key:{}'.format(pim_key))
                        continue
                    # pim 单选 ==>> target 单选和多选
                    if pim_type == PIM_SINGLE_CHECK and target_type in [TARGET_SINGLE_CHECK, TARGET_MULTI_CHECK]:
                        for vcode in options[pim_key].keys():  # vcode:['male','function','suitableScene']
                            # 属性值sheet中：京东属性值key、京东属性值value
                            target_vcode = options[pim_key][vcode][TITLE_TARGET_VCODE]
                            target_value = options[pim_key][vcode][TITLE_TARGET_VALUE]
                            # TM单选"20532",多选["20532"],JD 单选和多选 ["20532"]
                            if self.channel == 'TM':
                                target_vcode = [target_vcode] if target_type == 'MULTI_CHECK' else target_vcode
                            else:
                                target_vcode, target_value = [target_vcode], [target_value]
                            # excel中 vcode填写不规范，需要特殊处理的场景
                            vcode = 'true' if vcode in ["TRUE", "=TRUE()"] else vcode
                            vcode = 'false' if vcode in ["FALSE", "=FALSE()"] else vcode
                            task = Task(schema, merged_row, vcode, target_vcode, target_value, target_schema)
                            self.task_items.append(task.item)
                    elif pim_type == PIM_MULTI_CHECK and target_type == TARGET_SINGLE_CHECK:
                        for vcode in options[pim_key].keys():
                            # 属性值sheet中：京东属性值key、京东属性值value
                            target_vcode = options[pim_key][vcode][TITLE_TARGET_VCODE]
                            target_value = options[pim_key][vcode][TITLE_TARGET_VALUE]
                            # TM单选"20532",多选["20532"],JD 单选和多选 ["20532"]
                            if self.channel == 'TM':
                                target_vcode = [target_vcode] if target_type == 'MULTI_CHECK' else target_vcode
                            else:
                                target_vcode = [target_vcode]
                                target_value = [target_value]
                            # excel中 vcode填写不规范，需要特殊处理的场景
                            vcode = 'true' if vcode in ["TRUE", "=TRUE()"] else vcode
                            vcode = 'false' if vcode in ["FALSE", "=FALSE()"] else vcode
                            task = Task(schema, merged_row, vcode, target_vcode, target_value, target_schema)
                            self.task_items.append(task.item)
                    elif pim_type == PIM_MULTI_CHECK and target_type == TARGET_MULTI_CHECK:
                        vcode = list(options[pim_key].keys())
                        target_vcode = [item[TITLE_TARGET_VCODE] for item in options[pim_key].values()]
                        target_value = [item[TITLE_TARGET_VALUE] for item in options[pim_key].values()]
                        task = Task(schema, merged_row, vcode, target_vcode, target_value, target_schema)
                        self.task_items.append(task.item)
                    else:
                        self.logger.warning('未知的选择类型：{}'.format(pim_type))

    def load_vip_file(self, filepath):
        '''
        解析vip 数据模板
        :param filepath:
        :return:
        '''

        rowlist = list()
        ext = ExcelTool(filepath)

        # 获取sheet中的所有数据（包括第一行）
        sheet_values = ext.get_sheet_values("唯品会全属性", skiplines=0)

        for i in range(0, ext.getsheet("唯品会全属性").max_row - 1):
            merged_row = ext.merge_list(sheet_values, idx_krow=0, idx_vrow=i + 1)
            rowlist.append(merged_row)

        # 过滤出 需要的数据
        r1 = filter(lambda x: x[TITLE_PIM_KEY] is not None, rowlist)
        r1 = filter(lambda x: x[TITLE_TARGET_KEY] is not None, r1)
        r1 = filter(lambda x: x[TITLE_TARGET_VCODE] is not None, r1)

        return list(r1)

    def get_merged_rows(self, ext: ExcelTool, sheetname):
        '''遍历属性值结尾的sheet, 合并成dict的形式，然后追加到list中，需要过滤掉<pim key>为空, 或<京东字段|天猫字段> key为空'''
        if not (sheet := ext.getsheet(sheetname)):
            self.logger.error('ERROR：sheetname not found <{}>'.format(sheetname))
        rowlist = list()
        sheet_values = ext.get_sheet_values(sheetname, skiplines=0)
        for i in range(0, sheet.max_row - 1):
            dictrow = ext.merge_list(sheet_values, idx_krow=0, idx_vrow=i + 1)
            rowlist.append(dictrow)
        # self.logger.info('end merge')
        r1 = filter(lambda x: x[TITLE_PIM_KEY] is not None, rowlist)
        r1 = filter(lambda x: x[TITLE_TARGET_KEY] is not None, r1)
        return list(r1)

    def group_by(self, rowlist, title_key, title_value):
        key_options = {}
        for k, g in groupby(rowlist, key=lambda x: x[title_key]):
            agglist = list(g)
            key_options[k] = {i[title_value]: i for i in agglist}
        self.logger.info('group by options:{}'.format(json.dumps(key_options, ensure_ascii=False)))
        return key_options

    def parser(self, item):
        '''解析数据item数据，格式参考task_items.json'''
        self.logger.info('正在处理==>>:{}'.format(json.dumps(item, ensure_ascii=False)))
        # 序列解包
        schema, key, vcode, _, _, position = item['origin'].values()
        target_schema, target_key, _, _, target_value = item['target'].values()

        randomstr = random.randrange(1000, 9999, step=1)
        pcode = self.generate_product_code(schema, key, randomstr=randomstr)  # 生成product_code
        # sku1 = 'sku1_{}'.format(pcode)
        # sku2 = 'sku2_{}'.format(pcode)
        # pbody = const.gen_product_body(pcode, schema, channel=self.channel, skus=[sku1, sku2], brand=const.BRAND)

        reqbody = const.gen_ts_body(pcode, schema)

        # 区分属性放到master 还是 variants
        if position == "SKU" or const.SUB_POSITION.get(key) == "SKU":
            self.set_value(reqbody['variants'][0]['properties'], key, vcode)
            position = 'SKU'
        else:
            self.set_value(reqbody['master']['properties'], key, vcode)
            position = 'SPU'  ## 后续需要用到
        # 创建、发布商品
        self.logger.info(json.dumps(reqbody, ensure_ascii=False))
        service.create_product(reqbody)
        self.logger.info('productCode:{},创建成功'.format(pcode))

        service.release_product(pcode)
        # 获取商品家的 商品id
        if self.channel == 'TM':
            pid = service.get_tm_pid(pcode)
            # 调用商品家详情接口 获取数据
            actual_vcode, actual_type = service.get_tm_value(pid, target_key)
            remark = ''
        else:
            # pid = service.get_jd_pid(pcode)
            self.logger.info(f'position:{position}')
            response = service.get_jd_value(pcode, attrValue=str(target_key), position=position, skuValue1=sku1)
            actual_schema, b, actual_vcode, actual_valias, remark = response.values()

        #### 数据清理 todo
        rpt = Report()
        rpt.schema = schema
        rpt.pimkey = key
        rpt.vcode = vcode
        rpt.target_key = target_key
        rpt.target_vcode = target_value
        rpt.actual_vcode = actual_vcode
        rpt.actual_valias = actual_valias
        rpt.target_schemaCode = str(target_schema)
        rpt.actual_schemaCode = str(actual_schema)
        rpt.target_schemaCode = str(target_schema)
        rpt.pcode = pcode
        rpt.result_schema = None
        rpt.result_vcode = None
        rpt.remark = remark
        self.logger.info(
            f'pcode:{pcode},exp：{target_value},act：{actual_vcode},exp_schema:{target_schema},act_schema:{actual_schema}')
        myreport = rpt.generate_report()
        return myreport

    def generate_product_code(self, schemaCode, key, randomstr):
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
            # self.loadfile(filepath)
            filedata = self.load_vip_file(filepath)
            # print(json.dumps(filedata, ensure_ascii=False))
            self.logger.info('load file over')

            print(len(filedata))

            # 第二阶段，拼装task_item数据
            for item in filedata:
                # print(item)
                # print(item.get(TITLE_PIM_VCODE))
                task = Task()
                task.row = item
                task.schema = item.get(TITLE_SCHEMACODE)
                task.vcode = item.get(TITLE_PIM_VCODE)
                task.target_schema = item.get(TITLE_TARGET_SCHEMACODE)
                task.target_vcode = item.get(TITLE_TARGET_VCODE)
                task.target_vcode = item.get(TITLE_TARGET_VALUE)

                self.task_items.append(task.__get_task_item())

            # print(json.dumps(self.task_items[0], ensure_ascii=False))

            filename = "report.xlsx"
            # 标题
            ext.write_data(filename, f'report{index}', datas=Report().get_keys())
            error_count = 0
            self.logger.info(f'开始执行格式化数据..')

            # 第三阶段
            for item in self.task_items:
                try:
                    report = self.parser(item)
                    ext.write_data(filename, f'report{index}', list(report.values()))
                except Exception as e:
                    error_count += 1
                    self.logger.error('出现异常：{}，detail==>>{}'.format(error_count, e))
                    print(e.with_traceback())
                if error_count >= 3:
                    break
        end = time.time()
        self.logger.info(f"共耗时：{round(end - start, 2)}")


if __name__ == '__main__':
    ck = Check()
    ck.run()
