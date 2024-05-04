import json
import re

from model.model import get_session, HomepageScanRecord, ShipinhaoUserInfo
from util.base_util import ggffww_decode, ggffww_encode
from util.file_util import create_missing_dirs
from util.request_util import HttpRequester
from datetime import datetime, date, timedelta

from util.robot_util import send_feishu_msg

base_video_url = '/Users/zhonghao/video/video_ai/'
title_sensitive_word_mapping = {
    '抖音': '',
    '巨量引擎': '',
    '巨量算数': '',
    'Dou+': '',
    '抖+': '',
    '抖加': '',
    'DOU+': ''
}

tag_sensitive_word = ['抖音', '巨量引擎', '巨量算数', 'Dou+', 'Dou', '抖', '巨量']


def free_download_by_cookie(url, cookie, homepage_url_md5):
    encoded_url = ggffww_encode(url)
    requester = HttpRequester()
    post_url = "https://www.xxx.com/ajax.php?act=video&batch_web=1&version=1"

    # POST请求示例
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://www.xxx.com',
        'Cookie': cookie,
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive'
    }

    body = {
        'inputvalue': encoded_url
    }
    response_data = requester.post(post_url, data=body, headers=headers)
    print('resp -> ', response_data)
    resp_code = response_data['code']
    if resp_code == -110:
        msg = response_data['msg']
        session = get_session()
        session.query(HomepageScanRecord).filter_by(homepage_url_md5=homepage_url_md5).update(
            {HomepageScanRecord.next_scan_time: datetime.now() + timedelta(hours=12)})
        send_feishu_msg(f'被风控捕获异常，暂避风头12小时, {msg}')

    encoded_data = response_data['data']
    user_id = 'default'
    if encoded_data:
        data = json.loads(ggffww_decode(encoded_data))
        print(f'resp data -> {data}')
        posts = data['posts']
        if posts:
            username = user_id
            if 'username' in data.get('user', {}) and data['user']['username'] != '' and data['user'][
                'username'] is not None:
                username = data['user']['username']
            videos = []
            for post in posts:
                post['user_id'] = user_id
                # 将'medias'字段的值转换为字符串
                # 依据 user_id + username + text 拼接视频下载路径
                video_dir = base_video_url + username
                final_video_dir = video_dir + '/final/'
                create_missing_dirs(final_video_dir)
                video_title = post['text']
                if video_title == '':
                    video_title = '一定要看到最后哦！'
                # 对title进行处理，提取其中所有的 '#标签'，去除所有的#标签后的纯净title
                tags = re.findall(r'#\w+', video_title)
                filtered_tags = [tag.replace('#', '') for tag in tags if
                                 not any(word in tag for word in tag_sensitive_word)]

                clean_title = re.sub(r'#\w+ ', '', video_title)
                clean_title = re.sub(r'#\w+$', '', clean_title)

                for word, replacement in title_sensitive_word_mapping.items():
                    clean_title = clean_title.replace(word, replacement)
                post['text'] = clean_title
                post['tags'] = filtered_tags

                # 对敏感关键词进行替换： 抖音 -> 视频号；

                video_path = video_dir + '/' + post['text'] + '.mp4'
                dedup_video_path = final_video_dir + post['text'] + '.mp4'
                post['video_path'] = video_path
                post['dedup_video_path'] = dedup_video_path
                for media in post['medias']:
                    if media['media_type'] == 'video':
                        post['resource_url'] = media['resource_url']
                        post['preview_url'] = media['preview_url']
                        post['media_type'] = 'video'
                        post['medias'] = str(post['medias'])
                        videos.append(post)
                        break
            return videos

        else:
            return []
    else:
        return []
