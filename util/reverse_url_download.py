from datetime import datetime
import requests

from util.string_util import split_and_get_last_id
from util.file_util import create_missing_dirs
import re

hhm_api = 'https://h.xxx.cn/posts'
single_hhm_api = 'https://h.xxx.cn/single_post'
uid = 'asdz2123zdsfa2rf12'
secret_key = '5aaa27e8ffc459f2b315ba9cf6a97c2ba'
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


def single_download_url(video_url):
    params = {
        'userId': uid,
        'secretKey': secret_key,
        'url': video_url
    }
    r = requests.post(single_hhm_api, json=params, verify=False)
    response_data = r.json()
    print('response_data -> ', response_data)
    # title = response_data['text']
    if 'medias' in response_data.get('data', {}):
        data = response_data['data']
        title = data['text']
        medias = data['medias']
        media = medias[0]
        media['title'] = title
        if media and media['media_type'] == 'video':
            return media
    return {}


def fetch_homepage_videos(homepage_url):
    # url = 'https://www.douyin.com/user/' + user_id
    user_id = split_and_get_last_id(homepage_url)
    params = {
        'userId': uid,
        'secretKey': secret_key,
        'url': homepage_url
    }
    r = requests.post(hhm_api, json=params, verify=False)
    response_data = r.json()
    print('response: ', response_data, datetime.now())
    if 'posts' in response_data.get('data', {}):
        data = response_data['data']
        posts = data['posts']
        username = user_id
        if 'username' in data.get('user', {}) and data['user']['username'] != '':
            username = data['user']['username']
        videos = []
        for post in posts:
            post['user_id'] = user_id
            # 将'medias'字段的值转换为字符串
            # 依据 user_id + username + text 拼接视频下载路径
            video_dir = base_video_url + username
            # create_missing_dirs(video_dir)
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


if __name__ == '__main__':
    resp = fetch_homepage_videos('https://www.douyin.com/user/MS4wLjABAAAAFDufLNnG1giiaYBM2xsmWFHq1piPqW-0wH691m0eZ2w')
    print(resp)