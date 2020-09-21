# encoding:UTF-8
def yield_test(n):
    for i in range(n):
        yield call(i)
        print("i=", i)
        # 做一些其它的事情
        # print("do something.")
    print("end.")


def call(i):
    print(f'第{i}次yield')
    temp = {
        'id': i,
        'code': f'sku_{100 + i}'
    }
    return temp


print(list(yield_test(5)))
