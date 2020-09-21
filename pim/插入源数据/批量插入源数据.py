# coding=utf-8

from datetime import datetime
from pymongo.errors import DuplicateKeyError
from common.tool import GeneralTool
from pim.check.const import integration
from multiprocessing.dummy import Pool
import time

now = datetime.utcnow()
collection = GeneralTool.get_collection(integration['sit']['uri'], integration['sit']['db'], 'p_source')


def generate_source_list(externalCode: int, sourceType, tenantCode='baozun', catalog='user'):
    for i in range(1, 50001):
        body = {
            "externalCode": f'PF{str(externalCode + i)}',
            "sourceType": sourceType,
            "sourceData": {
                "LIST_PRICE": "558",
                "UNIQUE_NAME_CN_BREAKOUT_IND": "N",
                "DEPT_NAME": "ANF MENS WOVENS",
                "SLEEVE_LGTH_CD_OVRRD": "长袖",
                "WEB_LONG_SKU": "125-125-0952-223",
                "UNIQUE_NAME_BREAKOUT_IND": "N",
                "LIST_PRICE_BREAKOUT_IND": "N",
                "SHORT_SKU": f'PF{str(externalCode + i)}',
                "OFP_MDL_SZ_MSR": "M",
                "BRAND_CODE": "ANF",
                "OFP_MDL_HT_MSR": "185.4 cm",
                "KIC_ID": "KIC_125-9806-0952-223",
                "UNIQUE_NAME_CN": "标识款亚麻衬衫",
                "CATEGORY": "男装 -> 上装 -> 衬衫 -> 亚麻衬衫",
                "WEB_COPY_DESC_BREAKOUT_IND": "N",
                "GTIN_NUMBER": "636233256",
                "CARE_INSTR_BLEACH_TXT": "仅允许非氯漂",
                "FLOOR_SET_CD": "Spring Break",
                "UNIQUE_NAME": "Icon Linen Shirt",
                "GENDER": "Mens",
                "CARE_INSTR_SPECIAL_TXT": "避免沾色, 穿着前先洗涤, 将衣物反面翻出",
                "PRODUCT_COLOR_ID": "4",
                "PRICE_TICKET_URL": "http://anf.scene7.com/is/image/anf/sku636233256-price-ticket-RMB",
                "NECKLN_STY_NAM": "有领",
                "COLLECTION_NUMBER": "248550",
                "SHORT_DESC_BREAKOUT_IND": "Y",
                "SELLING_YEAR_NUMBER": "2019",
                "SKU_CREATE_DATE": "21-NOV-18 12.00.00.000000 AM",
                "ORIGIN_CNTRY_CODE_BREAKOUT_IND": "N",
                "COLOR_DESCRIPTION_OR": "浅蓝色浸染",
                "CARE_INSTR_DRY_TXT": "低温翻转干燥",
                "CARE_INSTR_IRON_TXT": "如果需要可中温熨烫",
                "SHORT_DESCRIPTIONS": "经典版型",
                "COMPLIANCE_TAG_URL": "http://anf.scene7.com/is/image/anf/sku636233256-cn-comply-label",
                "STY_TYP_NAM": "纽扣式衬衫",
                "FIBER_CONTENT_DESCRIPTION_OR": "亚麻纤维",
                "ORIGIN_COUNTRY_CODE": "India",
                "FIBER_CONTENT_EXCLUSION_NAME": "装饰物除外",
                "FIBR_CNT_DESC_OR_BREAKOUT_IND": "Y",
                "CARE_INSTR_WASH_TXT": "冷水单独机洗",
                "FIT_TYP_CD_OVRRD": "Signature",
                "SIZE_DIMENSION_PRIMARY_CODE_OR": "M",
                "PDP_GROUPING": f'P{str(externalCode + i)}',
                "SIZE_CHART_ID": "tops (mens)",
                "WEB_COPY_DESCRIPTION": "经典纽扣式衬衫，采用轻盈透气的亚麻面料，配胸袋，饰有刺绣标识图样细节。",
                "CARE_INSTR_OTHER_TXT": "不可干洗"
            },
            "md5": f'md5_{str(externalCode + i)}',
            "isStore": False,
            "createTime": now,
            "updateTime": now,
            "operatorId": "likai",
            "logicDelete": 0,
            "tenantCode": tenantCode,
            "catalog": catalog
        }
        yield body


def insert(row: dict):
    print("正在操作：{}".format(row.get("externalCode")))
    try:
        collection.insert_one(row)  # print(x.inserted_id)
    except DuplicateKeyError:
        pass
        # conditon = {"externalCode": model.get("externalCode")}
        # mycol.update_one(conditon, {'$set', model})  # 整个model更新
    except Exception as e:
        raise Exception("数据新增异常：", row.get("externalCode"), e)


def main():
    start = time.time()

    sourcelist = generate_source_list(90700000, 'erp-anf-ins')

    pool = Pool(4)  # 实例化线程池
    pool.map(insert, sourcelist)  # 开启线程池，get_down函数，list为可迭代对象
    pool.close()
    pool.join()
    end = time.time()
    print("共耗时：{}秒".format(round(end - start)))


if __name__ == '__main__':
    main()
