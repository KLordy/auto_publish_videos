import random

from util.request_util import HttpRequester


def send_feishu_msg(msg):
    robot_url = "https://www.feishu.cn/flow/api/trigger-webhook/ccfa1ad0fe13ae045a41528c20fd3c667111"
    requester = HttpRequester()
    post_response = requester.post(robot_url, json={"user": msg},
                                   headers={"Content-Type": "application/json"})
    print('robot alert response: ', post_response)
    return post_response

