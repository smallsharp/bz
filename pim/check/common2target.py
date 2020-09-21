# coding=utf8
from common.tool import ExcelTool
import os
import json
import requests
from pim.check import const
import time
import urllib3
from itertools import groupby
import random
from retry import retry
from pim.check import service

urllib3.disable_warnings()

skipsheet = ['s10102-属性值', 's10101-属性值', 's10103-属性值', 's10106-属性', 's10107-属性值', 's10108-属性值', 'f101-属性值', 'f101-属性',
             's10201-属性值', 's10301-属性值']

channel = const.channel

# 获取
pimkey = const.fieldmap['pimkey']
pimkey_type = const.fieldmap['pimkey_type']
target_key = const.fieldmap['target_key']
target_type = const.fieldmap['target_type']
exp_target_vcode = const.fieldmap['exp_target_vcode']
exp_target_value = const.fieldmap['exp_target_value']


def loadfile(filepath, channel='TM'):
    ext = ExcelTool(filepath)
    # 遍历给定文件中，所有的sheet
    for sheetname in ext.sheetnames:
        # 过滤出 以属性结尾的sheet，并获取sheet中 每一行字段的 配置
        if not sheetname.endswith('属性') or sheetname in skipsheet:
            continue

        print("sheetname:{}".format(sheetname))
        schemaCode, subfix = sheetname.split('-')

        # 获取 sheetname 以属性值结尾的数据，并按key分组聚合
        sheetname2 = sheetname.replace('属性', '属性值')

        # 获取 属性值sheet 中各个属性的聚合数据
        options = get_key_options(ext, sheetname2, channel=channel)
        print(json.dumps(options, ensure_ascii=False))

        # 开始遍历 <属性sheet>
        for i in range(0, ext.getsheet(sheetname).max_row - 1):
            row = ext.get_dict_rows(sheetname, 0, index_valuerow=i + 1)

            # 使用<属性sheet>中，如下几个值
            pimkey = row[const.fieldmap['pimkey']]  # 属性键值
            pimkey_type = row[const.fieldmap['pimkey_type']]  # 属性类型
            target_key = row[const.fieldmap['target_key']]  # 终端 字段
            target_type = row[const.fieldmap['target_type']]  # 终端 字段类型

            # print(json.dumps(row, ensure_ascii=False))
            # 数据不全的不用处理
            if not target_key or not pimkey:
                continue

            print('pimkey_type:{},target_key:{}'.format(pimkey_type, target_key))

            seed = random.randrange(1, 9999, step=1)  # 随机数
            if channel == 'JD':
                if pimkey_type in ['MULTI_CHECK', 'SINGLE_CHECK']:

                    if not options.get(pimkey):
                        print('Warning:属性值sheet中没有匹配的选项值,schemaCode:{},key:{}'.format(schemaCode, pimkey))
                        continue

                    # 外层遍历pimkey，内层遍历对应的选项值 ['male','function','suitableScene']
                    print(options[pimkey].keys())
                    for vcode in options[pimkey].keys():
                        # 预期的天猫属性值code（属性sheet中：天猫属性值key 列）
                        exp_target_vcode = options[pimkey][vcode][const.fieldmap['exp_target_value']]  # 部分excel中，列位置不对应
                        exp_target_value = options[pimkey][vcode][const.fieldmap['exp_target_vcode']]

                        print(f'exp_target_vcode:{exp_target_vcode},exp_target_value:{exp_target_value}')

                        # 单选商品家"20532",多选商品家显示["20532"]   pim 选择型=>商品家：输入、单选、多选
                        exp_target_vcode = [exp_target_vcode] if target_type == 'MULTI_CHECK' else exp_target_vcode

                        # excel中 vcode填写不规范，需要特殊处理的场景
                        vcode = 'true' if vcode in ["TRUE", "=TRUE()"] else vcode
                        vcode = 'false' if vcode in ["FALSE", "=FALSE()"] else vcode
                        yield const.gen_pending_item(schemaCode, row, vcode=vcode, target_vcode=exp_target_vcode)

            elif channel == 'TM':
                if pimkey_type == '选择型':
                    # 属性sheet中有key，但是属性值 sheet中没有选项值，如sportSeries字段，options没有这个key报错
                    if not options.get(pimkey):
                        print('Warning:属性值sheet中没有匹配的选项值,schemaCode:{},key:{}'.format(schemaCode, pimkey))
                        continue
                    # 从属性值 sheet中, 遍历valuecode ['male','woman','unisex','child'] 等
                    for vcode in options[pimkey].keys():
                        # 预期的天猫属性值code（属性sheet中：天猫属性值key 列） 部分excel中，列位置不对应
                        exp_target_vcode = options[pimkey][vcode]['天猫属性值key']
                        # 区分单选、多选，单选商品家"20532",多选商品家显示["20532"]   pim 选择型=>商品家：输入、单选、多选
                        exp_target_vcode = [exp_target_vcode] if target_type == 'multiCheck' else exp_target_vcode

                        # excel中 vcode填写不规范，需要特殊处理的场景
                        vcode = 'true' if vcode in ["TRUE", "=TRUE()"] else vcode
                        vcode = 'false' if vcode in ["FALSE", "=FALSE()"] else vcode
                        yield const.gen_pending_item(schemaCode, row, vcode=vcode, target_vcode=exp_target_vcode)

                elif pimkey_type == '文本型':
                    yield const.gen_pending_item(schemaCode, row, vcode=str(seed), target_vcode=str(seed))
                else:
                    print('未知的类型：{}'.format(pimkey_type))
            else:
                raise Exception('unKnown channel:{}'.format(channel))


def get_key_options(ext: ExcelTool, sheetname, channel='TM'):
    '''
    遍历属性值结尾的sheet，并按"属性键值",即pim.key进行分组，
    :param ext:
    :param sheetname: 属性值结尾的sheet
    :return: 格式如下
            {
            "gender": {
                "male": {
                    "模型键值": "s1011707",
                    "属性键值": "gender",
                    "属性值键值": "male",
                    "属性值名称": "男子",
                    "规则": null,
                    "天猫字段": "prop_122216608",
                    "天猫属性值key": "20532",
                    "天猫属性值value": "男子",
                    "转换规则": null,
                    "备注": null
                },
                "woman": {
                    "模型键值": "s1011707",
                    "属性键值": "gender",
                    "属性值键值": "woman",
                    "属性值名称": "女子",
                    "规则": null,
                    "天猫字段": "prop_122216608",
                    "天猫属性值key": "20533",
                    "天猫属性值value": "女子",
                    "转换规则": null,
                    "备注": null
                }
            }
        }
    '''
    if not (sheet := ext.getsheet(sheetname)):
        print('ERROR：sheetname not found <{}>'.format(sheetname))
    key_options = {}
    rowlist = list()
    for i in range(0, sheet.max_row - 1):
        row = ext.get_dict_rows(sheetname, 0, index_valuerow=i + 1)
        rowlist.append(row)
    # 过滤属性键值为空的行
    rowlist = list(filter(lambda x: x['属性键值'] is not None, rowlist))

    print('channel:{}'.format(channel))
    rowlist = list(filter(lambda x: x['属性键值'] is not None, rowlist))
    print('len:{}'.format(len(list(rowlist))))

    for k, g in groupby(rowlist, key=lambda x: x['属性键值']):
        agglist = list(g)
        key_options[k] = {i['属性值键值']: i for i in agglist}
    # print(json.dumps(key_options, ensure_ascii=False))
    return key_options


def generate_report(schemaCode, exp_vcode_tm, act_vcode_tm, item, productCode):
    # 值必须完全相等，且不等于None
    success = '通过' if exp_vcode_tm == act_vcode_tm and exp_vcode_tm is not None else '失败'

    return schemaCode, item['key'], item['vcode'], item['key_tm'], productCode, str(exp_vcode_tm), str(
        act_vcode_tm), success


def handle(item):
    # {'schemaCode': 's1011701', 'key': 'sportSeries', 'type': '选择型', 'multiple': '否', 'positon': '商品', 'key_tm': 'prop_123272013', 'type_tm': 'singleCheck', 'vcode': 'Masterpin', 'vcode_tm': '26291494'}
    schemaCode = item['schemaCode']
    key = item['key']
    vcode = item['vcode']
    key_tm = item['key_tm']
    type_tm = item['type_tm']  # 天猫字段类型
    exp_vcode_tm = item['vcode_tm']  # 天猫字段值

    # 生成product_code
    product_code = generate_product_code(schemaCode, key, seed=vcode)

    # 组装pim创建商品的所需的body
    p_model = const.get_product(product_code, schemaCode)
    p_model['master']['properties'][key] = vcode

    # 创建商品
    service.create_product(p_model)
    # print('>>>>pim 创建商品成功')
    # 发布商品
    service.release_product(product_code)
    # print('>>>>pim 发布商品成功')

    # 获取商品家的 商品id
    pid = service.get_tm_pid(product_code)
    # 调用商品家详情接口 获取数据
    actual_vcode, actual_type = service.get_tm_value(pid, key_tm)
    r1 = exp_vcode_tm == actual_vcode
    r2 = type_tm == actual_type
    if r1 and r2:
        service.delete_design_product(pid)
        # print('>>>>商品家 删除商品成功')
        service.delete_pim_product(product_code)
        # print('>>>>pim 删除商品成功')
    else:
        print(f'对比结果:{r1},商品编码:{product_code},预期结果：{exp_vcode_tm},实际：{actual_vcode}')

    report = generate_report(schemaCode, exp_vcode_tm, actual_vcode, item, product_code)
    return report


def generate_product_code(schemaCode, key, seed):
    t = time.strftime("%m%d", time.localtime())
    return f'{schemaCode}_{t}_{key}|{seed}'


def main():
    print('start')
    start = time.time()
    filelist = os.listdir('files')

    title = ['schemaCode', '属性', '属性值code', '天猫属性', '商品编码', '预期的天猫属性值', '实际的天猫属性值', '结果']

    for index, filename in enumerate(filelist):
        print(f'开始解析文件：{filename}')
        filepath = os.path.abspath(os.path.join(os.path.dirname(__file__), './files/{}'.format(filename)))
        items = loadfile(filepath, channel=const.channel)
        print(json.dumps(list(items), ensure_ascii=False))
        print(f'解析文件完成：{filename}')
        reportlist = list()

        exception_num = 0
        for item in items:
            try:
                report = handle(item)
                reportlist.append(report)
                print(f'handle:{item["schemaCode"], {item["key"]}, {item["vcode"]}}')
            except Exception as e:
                exception_num += 1
                print('错误数：{}，详情：{}，异常：{}'.format(exception_num, item, e))
            if exception_num >= 10:
                # ExcelTool.write(reportlist, title=title, filename='report.xlsx', sheetname='sheet_{}'.format(index))
                break

        # ExcelTool.write(reportlist, title=title, filename='report31_1.xlsx', sheetname='sheet_{}'.format(index))
        # schemaCode, item['key'], item['vcode'], item['key_tm'], exp_vcode_tm, act_vcode_tm, success, productCode

    end = time.time()
    print("共耗时：", round(end - start, 2))


if __name__ == '__main__':
    main()
