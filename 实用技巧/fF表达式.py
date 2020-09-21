name = 'likai'

print(f"{name}")  # likai
print(f"{name=}")  # name='likai'

print('name={}'.format(name))  # name=likai

a = 10
b = 20
res1 = F"a+b的值：{a + b}"  # a+b的值：30
c = F'{a+b}'
print(F'{c=}')

name = 'zhangs'
age = 20
res2 = F"姓名：{name}，年龄：{age}"  # 结果：姓名：zhangs，年龄：20
print(res2)

# 解析dict
one_dict = {'name': 'zhangs', 'age': 18, None: True}
res3 = F"姓名:{one_dict['name']}, 年龄:{one_dict['age']} ,None:{one_dict[None]}"
print(res3)

# 解析dict
one_list = [1, 2, 3, 'a', [1, 2, 3]]
res4 = F"列表值：{one_list[0]} {one_list[3]} {one_list[4][-1]}"
print(res4)

# 解析时间
import datetime

today = datetime.datetime.now()
print(today)  # 2020-06-12 10:51:51.192227
res6 = F"今天的日期:{today:%Y-%m-%d} {today:%H:%M:%S} "  # 今天的日期:2020-06-12 10:51:51
print(res6)

# 解析float
a = 1
b = 3
res1 = F"a/b浮点数值为:{float('%.5f' % (a / b))}"
print(res1)
