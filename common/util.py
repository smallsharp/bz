def isnull(key, include_blank=False):
    '''
    isnull('')  # True
    isnull(None)  # True
    isnull(' ')  # False
    isnull([])
    isnull({})
    :param key:
    :param include_blank: 默认不计算空格，设置为True时，isnull(' ',include_blank=True)  # True
    :return:
    '''
    return not key or (key is None) or not str(key).strip() if include_blank else False


# print(isnull(" ", include_blank=True))
# print(isnull(" "))


if __name__ == '__main__':
    s1 = 'hello world'

    maps =  {
            "Unisex": "男女运动",
            "Men": "男子运动",
            "Junior": "儿童运动",
            "Youth": "儿童运动",
            "WOMEN": "女子运动",
            "BOYS": "男童运动",
            "Girls": "女童运动",
            "Infants": "婴童运动",
            "Kids": "儿童运动"
        }

    # print(s1.capitalize())
    # print(s1.title())
    # print(s1.upper())

    new_maps = dict()
    for k, v in maps.items():
        new_maps[k.upper()] = v

    print(new_maps)