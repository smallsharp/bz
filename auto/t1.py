

from lxml import etree


with open("auto_unex_order_v1.35.jmx","r",encoding='utf-8') as f:
    content = f.read()

    html = etree.HTML(content)

    print(html.xpath('//elementProp'))