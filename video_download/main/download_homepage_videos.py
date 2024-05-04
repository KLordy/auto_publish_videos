import configparser
import time
from datetime import datetime, date, timedelta
import random

from apscheduler.schedulers.blocking import BlockingScheduler

from common.constant import VideoStatus
from model.model import get_session, DownloadVideoInfo, ShipinhaoUserInfo, HomepageScanRecord
from util.file_util import download_video, calculate_video_md5
from util.reverse_download import free_download_by_cookie
from util.robot_util import send_feishu_msg
from util.string_util import split_and_get_last_id, calculate_md5

config = configparser.ConfigParser()
config.read('download_config.ini')

save_path = config['save_path']['save_path']
homepage_urls = config['homepage_urls']['urls'].strip().split('\n')
target_accounts = config['homepage_urls']['target_account'].strip().split('\n')
cookies = config['cookies']
init = config.getboolean('homepage_urls', 'init')


def process_homepage_download():
    random_int = random.randint(1, 90)
    print(f'-------------- start scheduler time with delay {random_int}, at {datetime.now()}---------------')
    # 随机休眠x秒，避免触发查询太过规律
    ck_idx = random.randint(1, 2)
    cookie_name = 'cookie' + str(ck_idx)
    cookie = cookies[cookie_name]
    time.sleep(random_int)
    session = get_session()
    # 遍历homepage_urls
    download_video_infos = []
    for i in range(len(homepage_urls)):
        time.sleep(3)
        target_account = target_accounts[i]
        homepage_url = homepage_urls[i]
        homepage_url_md5 = calculate_md5(homepage_url)
        print(f'{homepage_url}的md5值-> {homepage_url_md5}')
        # 查找homepage_url的上一次更新视频时间，判断是否继续爬取
        scan_result = session.query(HomepageScanRecord).filter_by(homepage_url_md5=homepage_url_md5).all()[0]
        latest_update_time = scan_result.latest_update_time
        next_scan_time = scan_result.next_scan_time
        if datetime.now() < next_scan_time:
            print(f'当前时间{datetime.now()}早于下次爬取时间{next_scan_time},继续休息一下吧。')
            continue
        if latest_update_time:
            update_gap = (datetime.now() - latest_update_time).seconds
            if update_gap < scan_result.gap_minutes * 60:
                print(
                    f'{homepage_url}暂停爬取，原因：上一次获取到用户更新时间为{latest_update_time}，间隔小于设置的{scan_result.gap_minutes}分钟，暂停爬取')
                continue

        # 依据 account_name 找到所属账号最后一次发布时间，如果在一小时以内，则该账号不进行爬取
        user_info = session.query(ShipinhaoUserInfo).filter_by(shipinhao_username=target_account).all()[0]
        latest_pub_time = user_info.latest_pub_time
        current = datetime.now()
        if current > latest_pub_time:
            diff = (current - latest_pub_time).seconds
            if diff < 1800:
                print(f'账号{target_account}上一次发布视频时间是{latest_pub_time}，时间在半小时以内，先休息一下不再爬取。')
                continue
        if user_info:
            target_account_id = user_info.shipinhao_user_id
        else:
            target_account_id = 'unknown'
            print(f'未找到{target_account}对应的用户信息，设置account_id为unknown，请检查配置文件download_config.ini')
        current_videos = free_download_by_cookie(homepage_url, cookie, homepage_url_md5)
        empty_cnt = scan_result.empty_cnt
        print('response video : ', current_videos)
        if len(current_videos) == 0:
            if empty_cnt > 3:
                send_feishu_msg(homepage_url + ' 视频解析为空, cookie ' + str(ck_idx))
                next_time = datetime.now() + timedelta(minutes=30)
                # 视频返回为空，先休息半小时
                print(f'{homepage_url}页面返回数据为空，我们先休息半小时后再来爬取')
                session.query(HomepageScanRecord).filter_by(homepage_url_md5=homepage_url_md5).update(
                    {HomepageScanRecord.next_scan_time: next_time})
            else:
                # 更新次数，连续超过3次空，则休息半小时。
                session.query(HomepageScanRecord).filter_by(homepage_url_md5=homepage_url_md5).update({HomepageScanRecord.empty_cnt: empty_cnt + 1})
        else:
            session.query(HomepageScanRecord).filter_by(homepage_url_md5=homepage_url_md5).update({HomepageScanRecord.empty_cnt: 0})
        user_id = split_and_get_last_id(homepage_url)
        existing_user_video_titles = session.query(DownloadVideoInfo.video_title).filter_by(
            source_platform_user_id=user_id).all()
        video_titles_set = {row[0] for row in existing_user_video_titles}
        for video_info in current_videos:
            video_id = video_info['id']
            title = video_info['text']
            if title not in video_titles_set:
                resource_url = video_info['resource_url']
                local_path = save_path + '/' + title + '.mp4'
                download_video(resource_url, local_path)
                md5 = calculate_video_md5(local_path)
                status = VideoStatus.PENDING
                if init:
                    status = VideoStatus.INIT
                video_info = DownloadVideoInfo(
                    video_md5=md5,
                    video_id=video_id,
                    target_pub_user_id=target_account_id,
                    target_pub_account=target_account,
                    video_title=title,
                    source_platform_user_id=user_id,
                    download_url=resource_url,
                    local_path=str(local_path),
                    video_status=status,  # 假设去重状态初始为'pending'
                    create_time=datetime.now(),
                    update_time=datetime.now(),
                    pub_date=date.today(),
                    pub_time=datetime.now()
                )
                download_video_infos.append(video_info)
                # 本次爬取到了新视频，则进行更新爬取频率信息
                session.query(HomepageScanRecord).filter_by(homepage_url_md5=homepage_url_md5).update(
                    {HomepageScanRecord.latest_update_time: datetime.now(),
                     HomepageScanRecord.next_scan_time: datetime.now() + timedelta(minutes=4)})
    session.add_all(download_video_infos)
    session.commit()
    print(f'-------------- end scheduler time {datetime.now()} ---------------\n\n')


if __name__ == '__main__':
    scheduler = BlockingScheduler()
    now = datetime.now()
    initial_execution_time = datetime.now().replace(hour=now.hour, minute=now.minute + 1, second=now.second,
                                                    microsecond=0)
    scheduler.add_job(process_homepage_download, 'interval', minutes=4, start_date=initial_execution_time)  # 每30分钟执行一次
    scheduler.start()
