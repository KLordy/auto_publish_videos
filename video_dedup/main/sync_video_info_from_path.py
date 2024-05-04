# 入参提供路径，路径中视频信息同步到db中
import json
from datetime import datetime

from common.constant import VideoStatus
from model.model import DownloadVideoInfo, get_session
from util.file_util import get_mp4_files, calculate_video_md5
from video_dedup.config_parser import read_dedup_config

config = read_dedup_config()
external_dedup_video_path = config.external_dedup_video_path
target_pub_user_id = config.target_pub_user_id


def sync_info_from_path():
    video_files = get_mp4_files(external_dedup_video_path)
    result = []
    for i in range(0, len(video_files)):
        video_path = video_files[i]
        path = video_path['path']
        md5 = calculate_video_md5(path)
        video_name = video_path['file_name']
        print('开始处理: {}'.format(video_name))
        title = video_name.rsplit('.mp4', 1)[0]
        video_info = DownloadVideoInfo(
            video_id=md5,
            video_url='',
            target_pub_user_id=target_pub_user_id,
            video_title=title,
            deduplicated_video_path=path,
            video_status=VideoStatus.DEDUPLICATED,
            create_time=datetime.now(),
            update_time=datetime.now()
        )
        result.append(video_info)

    if result:
        session = get_session()
        session.add_all(result)
        session.commit()


if __name__ == '__main__':
    print('d -> ', config.data)
    d = json.loads(config.data)
    print('data -> ', d['a'])
