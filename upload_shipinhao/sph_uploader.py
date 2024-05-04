import asyncio
import re
from ctypes import Array
from datetime import datetime, date, timedelta

import requests
from apscheduler.schedulers.blocking import BlockingScheduler
from sqlalchemy import desc

from common.constant import TencentZoneTypes, VideoStatus
from model.model import get_session, ShipinhaoUserInfo, DownloadVideoInfo
from util.cookie_util import check_and_update_cookie
from util.file_util import get_account_file
from upload.tencent_uploader.main import TencentVideo
from util.file_util import create_missing_dirs

hhm_api = 'https://h.aaaapp.cn/posts'  # 单个帖子提取接口 (如果主页批量提取使用：https://h.aaaapp.cn/posts)
single_hhm_api = 'https://h.aaaapp.cn/single_post'
uid = '6171F623206DFD1E35A131BD2D9E74AC'  # 这里改成你自己的 userId
secret_key = '5eee27e8fc456f2b315ba9cf6a97c2ba'  # 这里改成你自己的 secretKey
base_video_url = '/Users/zhonghao/video/video_ai/'

# 用户提供的敏感词处理映射关系
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


def single_download(video_url):
    print('')


def fetch_videos(user_id):
    url = 'https://www.douyin.com/user/' + user_id
    params = {
        'userId': uid,
        'secretKey': secret_key,
        'url': url
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


def download_video(url, output_filename):
    try:
        # 发送HTTP GET请求来获取视频数据
        response = requests.get(url, stream=True)
        response.raise_for_status()  # 检查是否有错误发生
        # tmp_file = base_video_url + 'tmp.mp4'
        # 打开一个本地文件用于保存视频数据
        with open(output_filename, 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)

        # 使用ffmpeg将视频文件转换为所需格式（可选）
        # ffmpeg.input(tmp_file).output(output_filename).run(overwrite_output=True)

        print(f"视频已成功下载到 {output_filename}")
    except Exception as e:
        print(f"下载视频时发生错误: {e}")


def download_videos(new_videos):
    for video in new_videos:
        if video['resource_url']:
            download_video(video['resource_url'], video['video_path'])


def publish_video_to_shipinhao(video: DownloadVideoInfo, shipinhao_userinfo: ShipinhaoUserInfo, pub_time, session):
    deduplicated_video = video.deduplicated_video_path
    title = video.video_title
    tags = video.video_tags

    # 判断cookie是否有效，如果cookie无效，则需要用户扫码登录。
    cookie_valid = check_and_update_cookie(shipinhao_userinfo, handle=False)
    if cookie_valid:
        category = TencentZoneTypes.LIFESTYLE.value
        print('tags -> ', tags)
        account_file = get_account_file(shipinhao_userinfo.shipinhao_user_id)
        app = TencentVideo(title, deduplicated_video, tags, publish_date=pub_time, account_file=account_file,
                           category=category,
                           shipinhao_user_id=shipinhao_userinfo.shipinhao_user_id,
                           shipinhao_username=shipinhao_userinfo.shipinhao_username,
                           session=session)
        asyncio.run(app.main(), debug=True)


def scheduled_job():
    session = get_session()
    now = datetime.now()
    print('-------------- start scheduler time ', datetime.now(), '---------------')
    shipinhao_user_info: Array[ShipinhaoUserInfo] = session.query(ShipinhaoUserInfo).filter_by(machine_seq=1).all()
    current_pub_date = date.today()
    # 当前计划发布日期
    scheduler_pub_date = current_pub_date
    # 依据视频号id查询 user_bind_info，得到每个视频号需要监控的抖音用户id
    for shipinhao_info in shipinhao_user_info:
        user_id = shipinhao_info.shipinhao_user_id
        pub_num = shipinhao_info.pub_num
        latest_pub_time = shipinhao_info.latest_pub_time
        if not latest_pub_time:
            # 如果没有发布日期，则是初始化，则设置pub_time为2小时前，从而下面必然会触发发布。
            latest_pub_time = datetime.now() + timedelta(hours=-2)

        pub_gap = (datetime.now() - latest_pub_time).seconds
        if pub_gap < 3600:
            # 上一次发布时间在一小时内，则直接pass
            print(f'账号{shipinhao_info.shipinhao_username}上一次的视频发布时间为{latest_pub_time},间隔低于一小时，等待后续再发')
            continue

        # 查询已经发布视频数
        published_videos = session.query(DownloadVideoInfo).order_by(desc(DownloadVideoInfo.pub_time)).filter_by(
            target_pub_user_id=user_id, video_status=VideoStatus.PUBLISHED, pub_date=scheduler_pub_date).all()

        pubbed_num = len(published_videos)

        # 达到阈值
        if pubbed_num >= pub_num:
            print('视频号账号{}, 发布了超过{}个视频，暂停发布。'.format(user_id, len(published_videos)))
            continue

        # 检查用户cookie是否有效，如果无效则pass
        cookie_valid = asyncio.run(check_and_update_cookie(shipinhao_info, handle=True))

        if not cookie_valid:
            print('用户{}的cookie已经过期'.format(shipinhao_info.shipinhao_username))
            continue

        # 查询待发布的视频，按写入时间排序，写入时间约晚说明是约新的视频，更不容易被查重
        # 必须是15分钟以内创建下载的，因为下载后视频本身必须要时间去重，去重平均耗时3-5分钟，视频下载5分钟gap，则理论而言延迟会在10分钟以内
        # 10:00:00 作者发布视频； 10:03:00 下载好视频; 10:04开始剪辑去重； 10:07去重完毕；10:08开始上传
        max_create = datetime.now() - timedelta(minutes=10)
        deduplicated_videos = session.query(DownloadVideoInfo).order_by(desc(DownloadVideoInfo.create_time)).filter(
            DownloadVideoInfo.target_pub_user_id == user_id, DownloadVideoInfo.video_status == VideoStatus.DEDUPLICATED,
            DownloadVideoInfo.create_time >= max_create).all()

        if not deduplicated_videos:
            # 没有待发布的视频，则继续等待
            print(f'账号{shipinhao_info.shipinhao_username}最近十分钟内没有去重完毕待发布的视频，继续等待')
            continue
        pub_video = deduplicated_videos[0]
        pub_time = datetime(scheduler_pub_date.year, scheduler_pub_date.month, scheduler_pub_date.day, now.hour,
                            now.minute + 2)
        publish_video_to_shipinhao(pub_video, shipinhao_userinfo=shipinhao_info, pub_time=pub_time, session=session)
        # 发布成功，更新视频信息
        session.query(DownloadVideoInfo).filter_by(video_md5=pub_video.video_md5).update(
            {DownloadVideoInfo.video_status: VideoStatus.PUBLISHED, DownloadVideoInfo.pub_date: scheduler_pub_date,
             DownloadVideoInfo.update_time: now, DownloadVideoInfo.pub_time: pub_time})
        session.query(ShipinhaoUserInfo).filter_by(shipinhao_user_id=user_id).update(
            {ShipinhaoUserInfo.latest_pub_time: pub_time})

    session.commit()
    print('-------------- end scheduler time ', datetime.now(), '---------------\n\n')


if __name__ == '__main__':
    scheduler = BlockingScheduler()
    now = datetime.now()
    initial_execution_time = datetime.now().replace(hour=now.hour, minute=now.minute, second=now.second + 10, microsecond=0)
    scheduler.add_job(scheduled_job, 'interval', seconds=30, start_date=initial_execution_time)  # 每30分钟执行一次
    scheduler.start()
