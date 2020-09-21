a = {
    "x": 1,
    "y": 2,
    "z": 3
}
b = {
    "x": 2,
    "w": 11,
    "z": 12
}
# print(a.items())
# dict_items([('x', 1), ('y', 2), ('z', 3)])

# print(a.keys(), b.keys())
# dict_keys(['x', 'y', 'z']) dict_keys(['x', 'w', 'z'])

# 查看两个字典共有的key
print(a.keys() & b.keys())
# >>>{'x', 'z'}
# 共有的key，不共有的value

samekeys = a.keys() & b.keys()

samekeydiffvalue = [{k: (a[k], b[k])} for k in samekeys if a[k] != b[k]]
print('相同key,不同value：', samekeydiffvalue)

# 查看字典a 和 字典b 的不共有的key
print(a.keys() ^ b.keys())
# >>>{'y', 'w'}

# 查看在字典a里面而不在字典b里面的key
print(a.keys() - b.keys())
# >>>{'y'}

# 查看字典a和字典b相同的 键值对
print(a.items() & b.items())

# 查看字典a和字典b不相同的 键值对
print(a.items() ^ b.items())


# {('x', 1)}

def list_diff_keys(dict1: dict, dict2: dict):
    '''

    :param dict1:
    :param dict2:
    :return:
    '''
    return dict1.keys() ^ dict2.keys()


def list_diff_keys2(dict1: dict, dict2: dict):
    return dict1.keys() - dict2.keys()


def list_same_keys_diff_value(dict1: dict, dict2: dict):
    return [{k: (a[k], b[k])} for k in dict1.keys() & dict2.keys() if dict1[k] != dict2[k]]


def list_same_keys(dict1: dict, dict2: dict):
    return dict1.keys() & dict2.keys()


def list_diff_items(dict1: dict, dict2: dict):
    return dict1.items() & dict2.items()


print(list_same_keys_diff_value(a, b))
