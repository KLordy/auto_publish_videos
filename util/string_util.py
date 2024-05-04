import hashlib


def split_and_get_last_id(homepage_or_video_url):
    split_result = homepage_or_video_url.rsplit('/', 1)
    user_id = split_result[-1]
    return user_id


def calculate_md5(input_string):
    # 创建一个MD5对象
    md5 = hashlib.md5()

    # 将输入字符串编码为UTF-8，并更新MD5对象
    md5.update(input_string.encode('utf-8'))

    # 获取MD5值的十六进制表示
    md5_value = md5.hexdigest()

    return md5_value
