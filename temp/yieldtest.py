# t = '牛仔裤' in '高腰妈咪牛仔裤'
# print(t)
#
# from faker import Faker
#
# fake = Faker()
# print(fake.name())
# print(fake.address())
#
# print(dir(fake))
#
# from datetime import datetime
#
# print(datetime.utcnow())
#
# info = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
#
# info = [i + 1 for i in info]
# print(info)


# def init_nums():
#     for i in range(10):
#         v = {"index": i, "sku": f'{100 + i}'}
#         yield v
#
#
# print(list(init_nums()))

dict1 = {
    "a": "x1",
    "b": "x2"
}

# dict1.pop('a')
dict1.popitem()
dict1.popitem()

print(dict1)

print("共耗时：{}秒".format(round(100.222, 2)))

time = '17Q1'

print(time[2:])

datas = [{'type': 'FTW', 'keyword': 'FURYLITE GW 休闲鞋'}, {'type': 'FTW', 'keyword': 'CL NYLON SLIM CORE 休闲鞋'},
         {'type': 'FTW', 'keyword': 'REEBOKZPUMP FUSION 2.5 VP 跑步鞋'}, {'type': 'FTW', 'keyword': 'FURYLITE GW 休闲鞋'},
         {'type': 'FTW', 'keyword': 'FURYLITE GW 休闲鞋'}, {'type': 'FTW', 'keyword': 'CL NYLON SLIM CORE 休闲鞋'},
         {'type': 'FTW', 'keyword': 'SUBLITE AUTHENTIC 4.0 跑步鞋'}, {'type': 'FTW', 'keyword': 'FURYLITE GW 休闲鞋'},
         {'type': 'FTW', 'keyword': 'CL NYLON SLIM CORE 休闲鞋'},
         {'type': 'FTW', 'keyword': 'REEBOKZPUMP FUSION 2.5 VP 跑步鞋'}]

print(len(datas))

from itertools import groupby

for k, g in groupby(datas, key=lambda x: x['keyword']):  # 按path聚合
    # print(k, list(g))
    agglist = list(g)
    print(dict({k: i['type'] for i in agglist}), len(agglist))
