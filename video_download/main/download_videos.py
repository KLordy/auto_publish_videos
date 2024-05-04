# 调用 哼哼猫 or 其它第三方接口下载视频
# 入参依据配置文件来读取
import configparser

from common.constant import VideoStatus
from model.model import get_session, DownloadVideoInfo
from util.file_util import download_video
from util.reverse_url_download import single_download_url
from util.string_util import split_and_get_last_id

config = configparser.ConfigParser()
config.read('download_config.ini')

download_urls = config['download_urls']['urls'].strip().split('\n')
video_tags = config['video_tags']['tags']
target_account = config['target_account']['target_account']
save_path = config['save_path']['save_path']


def process_url_video_downloads():
    session = get_session()
    existing_video_ids = {url.video_url for url in session.query(DownloadVideoInfo.video_id).all()}
    download_video_infos = []
    for url in download_urls:
        video_id = split_and_get_last_id(url)
        if video_id not in existing_video_ids:
            # 逆向市面上付费下载软件的api接口 or github搜索douyin的XBogus相关算法自己部署服务，逆向付费软件自用即可，开源有风险，所以这里大家可以自行发挥。
            # response = requests.get(f'http://localhost:8081/video_download_info?url={url}')
            media = single_download_url(url)
            if media and media['resource_url']:
                resource_url = media['resource_url']
                # download_url = response.json().get('download_url')

                # 下载视频
                title = media['title']
                local_path = save_path + '/' + title + '.mp4'
                download_video(resource_url, local_path)

                # 保存记录到数据库
                video_info = DownloadVideoInfo(
                    video_url=url,
                    video_title=title,
                    video_id=video_id,
                    download_url=resource_url,
                    video_tags=video_tags,
                    local_path=str(local_path),
                    target_pub_account=target_account,
                    video_status=VideoStatus.PENDING  # 假设去重状态初始为'pending'
                )
                download_video_infos.append(video_info)
    session.add_all(download_video_infos)
    session.commit()
    # 通知任务完成
    # requests.post('http://some_notification_endpoint', data={'status': 'completed'})


if __name__ == '__main__':
    process_url_video_downloads()
