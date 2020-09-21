datalist = [{'path': 'c110110', 'code': 'P630_1005'}, {'path': 'c110110', 'code': 'P630_1004'},
            {'path': 'c110110', 'code': 'P630_1002'}, {'path': 'c110110', 'code': 'P630_1003'},
            {'path': 'c110110', 'code': 'P630_1001'}, {'path': 'varch-key', 'code': '他如何给'},
            {'path': 'varch-key', 'code': '4545'}, {'path': 'varch-key', 'code': 'tara'},
            {'path': 'varch-key', 'code': 'hellowhi'}, {'path': 'varch-key', 'code': '1299aging'},
            {'path': 'varch-key', 'code': '129097667'}, {'path': 'varch-key', 'code': '黑胡椒'},
            {'path': 'varch-key', 'code': 'wentogo'}, {'path': 'varch-key', 'code': '12'},
            {'path': 'varch-key', 'code': 'pim1295'}, {'path': 'varch-key', 'code': 'sogo'},
            {'path': 'varch-key', 'code': 'gogle'}, {'path': 'varch-key', 'code': '第一个商品'},
            {'path': 'varch-key', 'code': '大幅度'}, {'path': '新建一次类目', 'code': '23'},
            {'path': '4343', 'code': 'test129978'}, {'path': '4343', 'code': 'test3454'},
            {'path': '111aad', 'code': '6546456546546'}, {'path': '111aad', 'code': '53453453453454'},
            {'path': 't', 'code': '7834'}, {'path': 't', 'code': '565'}, {'path': 't', 'code': 'test32'},
            {'path': 't', 'code': '1299kill'}, {'path': '植物-key', 'code': '勿删测试商品'}, {'path': '植物-key', 'code': '1299'},
            {'path': '植物-key', 'code': '第二个商品'}, {'path': '植物-key', 'code': 'vuue'}, {'path': '植物-key', 'code': '721'},
            {'path': '植物-key', 'code': '切换类目测试挂件'}, {'path': 'varch-key', 'code': '535345345345'},
            {'path': 'varch-key', 'code': '56733gfh'}, {'path': '新建一次类目', 'code': 'pim12951'},
            {'path': '新建一次类目', 'code': 'pim129512'}, {'path': '4343', 'code': '我是商品'},
            {'path': 't', 'code': '4324234234234'}, {'path': 'code_622', 'code': 'pp123456'},
            {'path': 'code_622', 'code': 'P622_x002'}, {'path': 'code_622', 'code': '54'},
            {'path': 'code_622', 'code': '67'}, {'path': '植物-key', 'code': 'test123456'},
            {'path': '114514', 'code': 'spucodehaha'}]

from itertools import groupby

for k, g in groupby(datalist, key=lambda x: x['path']):  # 按path聚合
    print(k, list(g))
    # agglist = list(g)
    # print(dict({k: [i['code'] for i in agglist]}), len(agglist))
    # for i in list(g):
    #     print(k,i)
