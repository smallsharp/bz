# coding=utf8
from common.tool import ExcelTool
import os
import json
import requests
from pim.check import const
import time
from itertools import groupby
import random
from retry import retry
from pim.check import service

skipsheet = ['s10102-属性值', 's10101-属性值', 's10103-属性值', 's10106-属性', 's10107-属性值', 's10108-属性值', 'f101-属性值', 'f101-属性',
             's10201-属性值', 's10301-属性值']


class Check():

    def __init__(self, channel='JD'):
        self.channel = channel
        self.config = const
        # pim title
        self.title_pimkey = self.config.fieldmap['pimkey']
        self.tilte_pimkey_type = self.config.fieldmap['pimkey_type']
        self.title_pim_vcode = self.config.fieldmap['pim_vcode']
        self.title_schemaCode = self.config.fieldmap['schemaCode']
        self.pim_input = self.config.fieldmap['pimkey_input']
        self.pim_singlecheck = self.config.fieldmap['pimkey_single_check']
        self.pim_multicheck = self.config.fieldmap['pimkey_multi_check']
        # target title
        self.title_target_key = self.config.fieldmap['target_key']
        self.title_target_type = self.config.fieldmap['target_type']
        self.title_target_vcode = self.config.fieldmap['target_vcode']
        self.title_target_value = self.config.fieldmap['target_value']
        self.title_target_schemaCode = self.config.fieldmap['target_schemaCode']
        self.target_singlecheck = self.config.fieldmap['targetkey_single_check']
        self.target_multicheck = self.config.fieldmap['targetkey_multi_check']
        self.target_input = self.config.fieldmap['targetkey_input']

    def loadfile(self, filepath):
        ext = ExcelTool(filepath)
        # 遍历给定文件中，所有的sheet
        for sheetname in ext.sheetnames:
            # 过滤出 以属性结尾的sheet
            if not sheetname.endswith('属性') or sheetname in skipsheet:
                continue
            print("load sheet:{}".format(sheetname))
            sheetname2 = sheetname.replace('属性', '属性值')
            # 获取sheetname 对应的list，这里的数据虽然已经清理过，但是可能还不是最终可以使用的，后续还需要过滤一次
            rowlist = self.get_sheet_rows(ext, sheetname2)

            # 遍历 <属性sheet>,外层遍历pimkey
            for i in range(0, ext.getsheet(sheetname).max_row - 1):
                attrow = ext.get_dict_rows(sheetname, index_keyrow=0, index_valuerow=i + 1)
                # 数据不全的过滤掉
                if not attrow[self.title_pimkey] or not attrow[self.title_target_key]:
                    continue
                # print(json.dumps(attrow, ensure_ascii=False))
                schema = attrow[self.title_schemaCode]
                pimkey = attrow[self.title_pimkey]  # 属性键值
                pimkey_type = attrow[self.tilte_pimkey_type]  # 属性类型
                target_key = attrow[self.title_target_key]  # 京东字段|天猫字段
                target_schema = attrow[self.title_target_schemaCode]  # 终端类目
                target_type = attrow[self.title_target_type]
                if pimkey_type == self.pim_input:
                    seed = random.randrange(1, 9999, step=1)
                    yield const.gen_pending_item(schema, attrow, vcode=str(seed), target_vcode=str(seed))
                else:  # 选择型
                    # 再次过滤rowlist 过滤出 属性值sheet.京东字段值==属性sheet.京东字段值
                    myrowlist = list(filter(lambda x: x[self.title_target_key] == target_key, rowlist))
                    # 属性值sheet，去掉冗余数据，按pim.key聚合，格式见key_options.json
                    options = self.group_by(myrowlist, self.title_pimkey, self.title_pim_vcode)
                    print(json.dumps(options, ensure_ascii=False))
                    print('xxx' * 22)
                    if not options.get(pimkey):
                        print('warning:属性值sheet中没有{}的选项值'.format(pimkey))
                        continue
                    # pim 单选 ==>> target 单选和多选
                    if pimkey_type == self.pim_singlecheck and target_type in [self.target_singlecheck,
                                                                               self.target_multicheck]:
                        # vcode:['male','function','suitableScene']
                        for vcode in options[pimkey].keys():
                            # 属性值sheet中：京东属性值key、京东属性值value
                            target_vcode = options[pimkey][vcode][self.title_target_vcode]
                            target_value = options[pimkey][vcode][self.title_target_value]
                            # TM单选"20532",多选["20532"],JD 单选和多选 ["20532"]
                            if self.channel == 'TM':
                                target_vcode = [target_vcode] if target_type == 'MULTI_CHECK' else target_vcode
                            else:
                                target_vcode, target_value = [target_vcode], [target_value]
                            # print(f'{pimkey}:{pimcode} >> target_key:{target_key},vcode:{target_vcode},value:{target_value}')
                            # excel中 vcode填写不规范，需要特殊处理的场景
                            vcode = 'true' if vcode in ["TRUE", "=TRUE()"] else vcode
                            vcode = 'false' if vcode in ["FALSE", "=FALSE()"] else vcode
                            yield const.gen_pending_item(schema, attrow, vcode, target_vcode, target_value,
                                                         target_schema)
                    elif pimkey_type == self.pim_multicheck and target_type == self.target_singlecheck:
                        for vcode in options[pimkey].keys():
                            # 属性值sheet中：京东属性值key、京东属性值value
                            target_vcode = options[pimkey][vcode][self.title_target_vcode]
                            target_value = options[pimkey][vcode][self.title_target_value]
                            # TM单选"20532",多选["20532"],JD 单选和多选 ["20532"]
                            if self.channel == 'TM':
                                target_vcode = [target_vcode] if target_type == 'MULTI_CHECK' else target_vcode
                            else:
                                target_vcode = [target_vcode]
                                target_value = [target_value]
                            # print(f'{pimkey}:{pimcode} >> target_key:{target_key},vcode:{target_vcode},value:{target_value}')
                            # excel中 vcode填写不规范，需要特殊处理的场景
                            vcode = 'true' if vcode in ["TRUE", "=TRUE()"] else vcode
                            vcode = 'false' if vcode in ["FALSE", "=FALSE()"] else vcode
                            yield const.gen_pending_item(schema, attrow, vcode, target_vcode, target_value,
                                                         target_schema)
                    elif pimkey_type == self.pim_multicheck and target_type == self.target_multicheck:
                        vcode = list(options[pimkey].keys())
                        target_vcode = [i[self.title_target_vcode] for i in options[pimkey].values()]
                        target_value = [i[self.title_target_value] for i in options[pimkey].values()]
                        # print('key:{},keys:{},target_vcode:{},target_value:{}'.format(pimkey, pimcode, target_vcode,target_value))
                        yield const.gen_pending_item(schema, attrow, vcode, target_vcode, target_value, target_schema)
                    else:
                        print('eeee' * 30)

    def get_sheet_rows(self, ext: ExcelTool, sheetname):
        '''
        遍历属性值结尾的sheet，并按"属性键值",即pim.key进行分组，view key_options.json
        '''
        if not (sheet := ext.getsheet(sheetname)):
            print('ERROR：sheetname not found <{}>'.format(sheetname))
        rowlist = list()
        for i in range(0, sheet.max_row - 1):
            row = ext.get_dict_rows(sheetname, index_keyrow=0, index_valuerow=i + 1)
            rowlist.append(row)
        # 过滤<pim key>为空, 或<京东字段|天猫字段> key为空
        rowlist = list(filter(lambda x: x[self.title_pimkey] is not None, rowlist))
        rowlist = list(filter(lambda x: x[self.title_target_key] is not None, rowlist))
        # print('len:{}'.format(len(list(rowlist))))
        return rowlist

    def group_by(self, rowlist, title_key, title_value):
        key_options = {}
        for k, g in groupby(rowlist, key=lambda x: x[title_key]):
            agglist = list(g)
            # print(k, json.dumps(agglist, ensure_ascii=False))
            key_options[k] = {i[title_value]: i for i in agglist}
        # print(json.dumps(key_options, ensure_ascii=False))
        return key_options

    def generate_report(self, schemaCode, exp_target_vcode, act_target_vcode, item, productCode):
        # 值必须完全相等，且不等于None
        # success = '通过' if exp_target_vcode == act_target_vcode and exp_target_vcode is not None else '失败'
        if isinstance(exp_target_vcode, list) and isinstance(act_target_vcode, list):
            exp_target_vcode.sort()
            act_target_vcode.sort()
        success = '通过' if exp_target_vcode == act_target_vcode else '失败'
        return schemaCode, item['origin']['key'], item['origin']['vcode'], item['target']['key'], productCode, str(
            exp_target_vcode), str(
            act_target_vcode), success

    def parser(self, item):
        '''
        解析数据item数据，格式参考task_items.json
        '''
        print('正在处理....')
        print(json.dumps(item, ensure_ascii=False))
        schema = item['origin']['schemaCode']
        key = item['origin']['key']
        vcode = item['origin']['vcode']
        position = item['origin']['position']  # excel row position

        target_key = item['target']['key']  # 162843
        target_value = item['target']['value']  # 值对应的code
        target_schemaCode = item['target']['schemaCode']  # 天猫字段值

        # 生成product_code
        pcode = self.generate_product_code(schema, key, seed=vcode)
        skucode1 = 'sku1_{}'.format(pcode)
        skucode2 = 'sku2_{}'.format(pcode)
        # 组装pim创建商品的所需的body
        pbody = const.get_product(pcode, schema, channel=self.channel)
        # 参数位置配置
        backup_position = dict(const.conf.items('position'))
        # 区分属性放到master 还是 variants
        if position == "SKU" or backup_position.get(key) == "SKU":
            self.set_value(pbody['variants'][0]['properties'], key, vcode)
        else:
            self.set_value(pbody['master']['properties'], key, vcode)
            position = 'SPU'
        print(json.dumps(pbody, ensure_ascii=False))
        # 创建、发布商品
        service.create_product(pbody)
        print('商品:{},创建成功'.format(pcode))
        service.release_product(pcode)
        # 获取商品家的 商品id
        if self.channel == 'TM':
            pid = service.get_tm_pid(pcode)
            # 调用商品家详情接口 获取数据
            actual_vcode, actual_type = service.get_tm_value(pid, target_key)
        else:
            # pid = service.get_jd_pid(pcode)
            response = service.get_jd_value(pcode, attrValue=str(target_key), position=position, skuValue1=skucode1)
            actual_vcode = response.get('target_vcode')
            actual_schemaCode = response.get('schemaCode')

        r1 = target_value == actual_vcode
        # # r2 = target_schemaCode == actual_schemaCode
        # if r1:
        #     service.delete_design_product(pid)
        #     service.delete_pim_product(pcode)
        print(
            f'result:{r1},pcode:{pcode},exp：{target_value},act：{actual_vcode},act_schema:{actual_schemaCode},target_schema:{target_schemaCode}')
        report = self.generate_report(schema, target_value, actual_vcode, item, pcode)
        return report

    def generate_product_code(self, schemaCode, key, seed):
        t = time.strftime("%m%d", time.localtime())
        return f'{schemaCode}_{t}_{key}|{seed}'

    def set_value(self, propertiesObj, key, value):
        for word in key.split('.'):
            obj = dict(propertiesObj).get(word, value)
            if isinstance(obj, (str, int, float)):
                propertiesObj[word] = value
            else:
                propertiesObj = obj


def main():
    print('start')
    start = time.time()
    filelist = os.listdir('files')
    ck = Check(channel=const.channel)
    for index, filename in enumerate(filelist):
        print(f'开始解析文件：{filename}')
        filepath = os.path.abspath(os.path.join(os.path.dirname(__file__), './files/{}'.format(filename)))
        items = ck.loadfile(filepath)
        # print(json.dumps(list(items), ensure_ascii=False))
        print(f'解析文件完成：{filename}')
        reportlist = list()

        for item in items:
            exception_num = 0
            try:
                report = ck.parser(item)
                reportlist.append(report)
            except Exception as e:
                exception_num += 1
                print('错误数：{}，详情：{}，异常：{}'.format(exception_num, item, e))
                print(e.with_traceback())
            if exception_num >= 10:
                # ExcelTool.write(reportlist, title=title, filename='report.xlsx', sheetname='sheet_{}'.format(index))
                break
        print(reportlist)
        title = ['schemaCode', '属性', '属性值code', '终端KEY', '商品编码', '预期终端value', '实际终端value', '结果']
        ExcelTool.write(reportlist, title=title, filename='report_reebok.xlsx', sheetname='sheet_{}'.format(index))
    end = time.time()
    print("共耗时：", round(end - start, 2))


if __name__ == '__main__':
    main()
