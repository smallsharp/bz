import requests

import requests

url = "http://mid-platform-publish-platform-service-sit.cloud.bz/publish-platform/convertJs/hub-convert"

payload = {
    "UNIQUE_NAME_CN_BREAKOUT_IND": "N1",
    "SIZE_DIMENSION_SECONDARY_CODE_OR": "",
    "SLEEVE_LGTH_CD_OVRRD": "xxxx",
    "WEB_LONG_SKU": "f",
    "UNIQUE_NAME_BREAKOUT_IND": "UN1",
    "IMAGE_URL_OFP": "FFF",
    "WASH_PLNNR_CD_OVRRD": "SFSF",
    "OFP_MDL_HT_MSR": "203.9 cm",
    "CARE_INSTR_BLEACH_TXT": "CS",
    "UNIQUE_NAME": "UNIQUE_NAME028",
    "PRODUCT_COLOR_ID": "222",
    "NECKLN_STY_NAM": "NSN",
    "SHORT_DESC_BREAKOUT_IND": "SD",
    "SELLING_YEAR_NUMBER": "2021",
    "ORIGIN_CNTRY_CODE_BREAKOUT_IND": "NF1",
    "COLOR_DESCRIPTION_OR": "WHITE",
    "CARE_INSTR_DRY_TXT": "CDT",
    "SHORT_DESCRIPTIONS": "SSD",
    "COMPLIANCE_TAG_URL": "http://anf.scene7.com/is/image/anf/sku639861397-cn-comply",
    "IMAGE_URL_OFP_1": "121",
    "BTTMS_LGTH_CD": "BBB",
    "FIBER_CONTENT_DESCRIPTION_OR": "FCD",
    "ORIGIN_COUNTRY_CODE": "Cambodia11",
    "MEASUREMENTS": "M1",
    "SIZE_DIMENSION_PRIMARY_CODE_OR": "S2",
    "BTTMS_RISE_CD": "B3",
    "IMAGE_URL_TALL_1": "II",
    "SIZE_CHART_ID": "tops (mens)",
    "IMAGE_URL_ZOOM": "iii",
    "LIST_PRICE": "127",
    "DEPT_NAME": "ANF WOMENS KNITS",
    "CLSR_TYP_NAM": "c11",
    "BASE_INSEAM_MEASUREMENT": "b11",
    "LIST_PRICE_BREAKOUT_IND": "N22",
    "SHORT_SKU": "8528029",
    "OFP_MDL_SZ_MSR": "O1",
    "TMALL_LOAD_DATE": "TL1",
    "IMAGE_URL_TALL": "IU1",
    "BRAND_CODE": "ANF",
    "KIC_ID": "",
    "WEB_COPY_DESC_BREAKOUT_IND": "w2",
    "CATEGORY": "cc1",
    "UNIQUE_NAME_CN": "背心1",
    "GTIN_NUMBER": "ggg",
    "FLOOR_SET_CD": "Spring Break",
    "GENDER": "Guys",
    "CARE_INSTR_SPECIAL_TXT": "sp",
    "PRICE_TICKET_URL": "ff1",
    "COLLECTION_NUMBER": "290901",
    "SKU_CREATE_DATE": "2019-09-30",
    "CARE_INSTR_IRON_TXT": "ccc1",
    "STY_TYP_NAM": "",
    "IMAGE_URL_TALL_OFP_1": "xxf",
    "WASH_INSTRUCTIONS": "wwww",
    "FIBR_CNT_DESC_OR_BREAKOUT_IND": "Nxx",
    "FIBER_CONTENT_EXCLUSION_NAME": "fff",
    "CARE_INSTR_WASH_TXT": "ccc",
    "FIT_TYP_CD_OVRRD": "ftc",
    "IMAGE_URL_TALL_OFP": "123",
    "PDP_GROUPING": "304803-5",
    "WEB_COPY_DESCRIPTION": "舒适套头运动衫。",
    "CARE_INSTR_OTHER_TXT": "c1"
}
headers = {
    'tenantCode': 'baozun',
    'catalog': 'anf',
    'ruleCode': 'source-common-ins-upd',
    'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, json=payload)

print(response.text)
