from sqlalchemy import create_engine, Column, String, Text, DateTime, Integer, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

Base = declarative_base()


class DownloadVideoInfo(Base):
    __tablename__ = 'download_video_info'
    video_md5 = Column(String(500), primary_key=True)
    video_id = Column(String(500))
    video_url = Column(Text)
    target_pub_user_id = Column(Text)
    target_pub_account = Column(Text)
    download_url = Column(Text)
    video_title = Column(Text)
    source_platform_user_id = Column(Text)
    video_tags = Column(Text)
    local_path = Column(Text)
    deduplicated_video_path = Column(Text)
    video_status = Column(String(50))
    pub_date = Column(Date)
    pub_time = Column(DateTime)
    create_time = Column(DateTime)
    update_time = Column(DateTime)


class ShipinhaoUserInfo(Base):
    __tablename__ = 'shipinhao_user_info'
    shipinhao_user_id = Column(String(200), primary_key=True)
    shipinhao_username = Column(String(200))
    publish_hours = Column(String(200))
    latest_pub_time = Column(DateTime)
    machine_seq = Column(Integer)
    cookies = Column(Text)
    pub_num = Column(Integer)
    update_time = Column(DateTime)


class HomepageScanRecord(Base):
    __tablename__ = 'homepage_scan_record'
    homepage_url_md5 = Column(String(500), primary_key=True)
    homepage_url = Column(String(500))
    gap_minutes = Column(Integer)
    empty_cnt = Column(Integer)
    latest_update_time = Column(DateTime)
    next_scan_time = Column(DateTime)


engine = create_engine('mysql+pymysql://root:root%40123@localhost:3306/video_tools')
Session = sessionmaker(bind=engine)


def get_session():
    return Session()


print(datetime.date.today())
