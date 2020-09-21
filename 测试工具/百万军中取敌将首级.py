# coding=utf8
import csv
import sys

# sys.path.append('.')
from 测试工具.const import templist

if __name__ == '__main__':

    # templist = [{'name': 'likai', 'age': 22}, {'name': 'wangwei', 'sex': 'male'}]

    keys = []
    for temp in templist:
        keys.extend(temp.keys())
        # break

    csv.register_dialect('mydialect', delimiter='|', lineterminator='\n', doublequote=csv.QUOTE_NONNUMERIC)

    with open('./c3.csv', 'w', newline='', encoding='utf8') as fw:
        dict_writer = csv.DictWriter(fw, fieldnames=keys, dialect='mydialect')
        dict_writer.writeheader()
        dict_writer.writerows(templist)

        # with open('temp.txt', mode='w', encoding='utf8') as f:
        #     for key in keys:
        #         f.write(key + ",")
        #     for t in templist:
        #         f.write(','.join(t.values()) + '\n')

        # f1 = open('c3.csv', 'w', newline='')
