from common.constant import VideoStatus
from model.model import DownloadVideoInfo, get_session
from util.file_util import get_mp4_files, calculate_video_md5
from video_dedup.config_parser import read_dedup_config
from video_dedup.video_dedup_by_config import process_dedup_by_config
import time
import shutil
from datetime import datetime
import uuid

config = read_dedup_config()
save_path = config.save_path
dedup_video_path = config.video_path
backup_path = config.backup_path
remove = config.remove_finish
write_db = config.write_db
target_pub_user_id = config.target_pub_user_id


def deduplicate_from_path():
    video_files = get_mp4_files(dedup_video_path)
    result = []
    for i in range(0, len(video_files)):
        video_path = video_files[i]
        path = video_path['path']
        md5 = calculate_video_md5(path)
        video_name = video_path['file_name']
        print('开始处理: {}'.format(video_name))
        title = video_name.rsplit('.mp4', 1)[0]
        dedup_path = save_path + '/' + video_name
        process_dedup_by_config(path, dedup_path, config)
        # 写入到db中
        if write_db:
            video_info = DownloadVideoInfo(
                video_md5=md5,
                target_pub_user_id=target_pub_user_id,
                video_title=title,
                deduplicated_video_path=dedup_path,
                video_status=VideoStatus.DEDUPLICATED,
                create_time=datetime.now(),
                update_time=datetime.now()
            )
            result.append(video_info)

        if remove:
            print('去重完毕，原始文件移动到backup_path配置的路径中：', path)
            shutil.move(path, backup_path)
    if result:
        session = get_session()
        session.add_all(result)
        session.commit()


if __name__ == '__main__':
    t1 = time.time()
    deduplicate_from_path()
    t2 = time.time()
    print('total cost time ', t2 - t1)
