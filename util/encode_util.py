import base64
import random


def ggffww_encode(a):
    a = base64.b64encode(a.encode()).decode()
    index = a.find("=")
    random_str = base64.b64encode(str(random.random()).encode()).decode()[:16]
    if index != -1:
        return random_str + a[:index][::-1] + a[index:]
    else:
        return random_str + a[::-1]


# 示例用法
encoded_string = ggffww_encode("https://www.douyin.com/user/MS4wLjABAAAA5DTjH0fZcTBPdOsG6CkoeC4YtAT8uA92N-NvqHUjdAo")
print(encoded_string)
