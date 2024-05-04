import base64

import requests
import random


class HttpRequester:
    def __init__(self):
        # 初始化时可以添加一些全局设置，例如超时时间、默认的请求头等
        self.session = requests.Session()

    def get(self, url, params=None, headers=None):
        """
        发送GET请求。

        :param url: 请求的URL
        :param params: 请求的参数，字典形式
        :param headers: 请求头，字典形式
        :return: 请求返回的结果
        """
        try:
            response = self.session.get(url, params=params, headers=headers)
            response.raise_for_status()  # 如果返回的状态码不是200，将抛出异常
            return response.text  # 或者response.json()，取决于你的需求
        except requests.RequestException as e:
            return str(e)

    def post(self, url, data=None, json=None, headers=None):
        """
        发送POST请求。

        :param url: 请求的URL
        :param data: 请求的数据，字典形式，用于form表单数据
        :param json: 请求的数据，字典形式，用于JSON数据
        :param headers: 请求头，字典形式
        :return: 请求返回的结果
        """
        try:
            response = self.session.post(url, data=data, json=json, headers=headers)
            response.raise_for_status()  # 如果返回的状态码不是200，将抛出异常
            return response.json()  # 或者response.json()，取决于你的需求
        except requests.RequestException as e:
            return str(e)


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


# 使用示例
if __name__ == "__main__":
    requester = HttpRequester()
    post_url = "https://www.xxx.com/ajax.php?act=video&batch_web=1&version=1"

    # POST请求示例
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://www.xxx.com',
        'Cookie': 'PHPSESSID=qh0hrf5tbfelmc2dlt43d1cc00; _ga=GA1.1.234159120.1704011845; cf_clearance=7y2.drC3iBr3u_B2RSbkjTTRJJSzr0_2qEYUYo3xv4c-1704108643-0-2-80f2808b.82482b03.d7f3df6b-0.2.1704108643; mysid=9977e58660a8c80421aa214f76c414be; user_token=9c5cMDAwMDAwMDAwMGY4MDhlOTJhZjVlMmFkMDgyMzM1NwkxNjc2OTMzM2MxMzcxYjFhMWI1M2NmMWM0ZGQwNTE1OQ; _ga_NVM5R0RWJE=GS1.1.1711867117.22.1.1711867225.0.0.0',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive'
    }

    body = {
        'inputvalue': 'MC43ODk3OTUxNzEwMmQ6pkYo5ETJ9VNzBTWNpXOJh3SnJ3ZGlmU0JVdP1WTwVWRyomYO5Gb6BnThJVNPJ2RiR3MNhzd2JFdpVFe58VQBFUQCFkaMdHNT10LyV2c19SbvNmLulWe19GZuc3d39yL6MHc0RHa='
    }
    # body = {
    #     'inputvalue': '=MmQ6pkYo5ETJ9VNzBTWNpXOJh3SnJ3ZGlmU0JVdP1WTwVWRyomYO5Gb6BnThJVNPJ2RiR3MNhzd2JFdpVFe58VQBFUQCFkaMdHNT10LyV2c19SbvNmLulWe19GZuc3d39yL6MHc0RHa'
    # }
    post_response = requester.post(post_url, data=body, headers=headers)
    data = post_response.get('data')
    print("POST Response:", data)
    print("POST Response:", ggffww_decode(data))

    # 原始data数据
    origin_data = ggffww_decode(data)
    # 正确encode的数据
    right_encoded_data = data
    # 测试的编码内容
    my_encoded = ggffww_encode(origin_data)
    print('正确编码长度：', len(right_encoded_data), ' / 测试编码长度：', len(my_encoded))
    print('正确编码：', right_encoded_data)
    print('测试编码：', my_encoded)
