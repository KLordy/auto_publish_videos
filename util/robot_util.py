import random

from util.request_util import HttpRequester


def send_feishu_msg(msg):
    robot_url = "https://www.feishu.cn/flow/api/trigger-webhook/cfa1ad0fe13ae045a41528c20fd3c667"
    requester = HttpRequester()
    post_response = requester.post(robot_url, json={"user": msg},
                                   headers={"Content-Type": "application/json"})
    print('robot alert response: ', post_response)
    return post_response


if __name__ == "__main__":
    # POST请求示例
    # resp = send_feishu_msg('直播告警')
    # print("POST Response:", resp)
    from datetime import datetime, date, timedelta
    now = datetime.now()
    next = datetime.now() + timedelta(minutes=10)
    if next > now:
        print('good bigger')
    else:
        print('bad smaller')

