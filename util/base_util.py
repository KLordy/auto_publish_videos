import base64
import re
import random


def ggffww_decode(a):
    a = a[16:]
    index = a.find("=")
    if index != -1:
        decoded_str = a[:index][::-1] + a[index:]
    else:
        decoded_str = a[::-1]

    return base64.b64decode(decoded_str).decode('utf-8')


def ggffww_encode(a):
    a = base64.b64encode(a.encode()).decode()
    index = a.find("=")
    random_str = base64.b64encode(str(random.random()).encode()).decode()[:16]
    if index != -1:
        return random_str + a[:index][::-1] + a[index:]
    else:
        return random_str + a[::-1]


def validate_url(url):
    # 检查 URL 格式是否符合要求
    pattern = r'^https?://(www\.)?[a-zA-Z0-9-]+(\.[a-zA-Z]{2,})+(\S*)?$'
    return re.match(pattern, url)


def encode_url(url):
    # 跳过前面的 16 个字符
    url = url[16:]

    # 判断是否包含等号
    index = url.find("=")
    if index != -1:
        encoded_str = url[:index][::-1] + url[index:]
    else:
        encoded_str = url[::-1]

    # Base64 编码
    encoded_str = base64.b64encode(encoded_str.encode('utf-8')).decode('utf-8')

    return encoded_str


def ggffww_encode2(s):
    # 跳过前面的 16 个字符
    encoded = base64.b64encode(s.encode('utf-8')).decode('utf-8')
    index = encoded.find("=")
    random_str = base64.b64encode(str(hash(s)).encode('utf-8')).decode('utf-8')[:16]
    if index != -1:
        return random_str + encoded[:index][::-1] + encoded[index:]
    else:
        return random_str + encoded[::-1]


if __name__ == "__main__":
    # MC4xMjEwNTQyNTAxMmQ6pkYo5ETJ9VNzBTWNpXOJh3SnJ3ZGlmU0JVdP1WTwVWRyomYO5Gb6BnThJVNPJ2RiR3MNhzd2JFdpVFe58VQBFUQCFkaMdHNT10LyV2c19SbvNmLulWe19GZuc3d39yL6MHc0RHa=
    # url -> https://www.douyin.com/user/MS4wLjABAAAA_9xUitRvw8M3tbGbO5RaNpzlnNbj2EepMmOuRtRiFgrgKxI9zMY0s5_ILNhbJzBc
    origin = 'https://www.douyin.com/user/MS4wLjABAAAA_9xUitRvw8M3tbGbO5RaNpzlnNbj2EepMmOuRtRiFgrgKxI9zMY0s5_ILNhbJzBc'
    d = ggffww_decode(
        "MC4zMzU2NTE3NTc5kVWmRTdSRGVGNEVBNnS5AVcy0SNzF0YQFDZWp3VQdzXTVTeDd3QwY1aBRXYFRmbrZjbzFzS3IjUYBFVxIlViFTQBFUQCFkaMdHNT10LyV2c19SbvNmLulWe19GZuc3d39yL6MHc0RHa=")
    print(d)
    # encoded_url = ggffww_encode(origin)
    # print('编码后的字符串：', encoded_url)
    #
    # decoded_url = ggffww_decode(encoded_url)
    # print('解码后的字符串：', decoded_url)
    # print('字符串对比：', encoded_url == decoded_url)
    #
    # if validate_url(origin):
    #     encoded_url = encode_url(origin)
    #     print("gpt编码后的URL:", encoded_url)
    #     print('gpt解码后：', ggffww_decode(encoded_url))
    # else:
    #     print("URL格式错误")
