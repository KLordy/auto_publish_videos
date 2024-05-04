-- auto-generated definition
create database if not exists video_tools;

-- 切换库
use video_tools;

-- 建表
create table if not exists download_video_info
(
    video_md5               varchar(500) not null
        primary key,
    video_id                varchar(500) null comment '视频在平台上的视频id，如果是单视频下载则直接从视频链接解析id；如果是主页下载，则从返回结果解析id',
    video_url               text         null comment '视频观看地址',
    target_pub_user_id      text         null comment '视频发布的平台账号id',
    target_pub_account      text         null comment '计划发布的账号名称',
    download_url            text         null comment '视频高清下载地址，对应为哼哼猫的 resource_url',
    video_title             text         null comment '视频名称',
    source_platform_user_id text         null comment '视频所属用户所在平台的id，例如抖音用户id',
    video_tags              text         null comment '视频的表情，多个标签时通过#分隔',
    local_path              text         null comment '视频本地存储地址',
    deduplicated_video_path text         null comment '完成去重后的视频地址',
    video_status            varchar(50)  null comment '去重标签，下一步的去重任务完成去重后，将这里设置为done',
    pub_date                date         null comment '视频的发布日期',
    pub_time                datetime     null comment '视频的具体发布时间',
    create_time             datetime     null comment '记录插入时间',
    update_time             datetime     null comment '记录更新时间，主要是下游去重任务更新时间'
);


create table homepage_scan_record
(
    homepage_url_md5   varchar(500)   not null comment '视频主页地址md5',
    homepage_url       varchar(500)   null,
    gap_minutes        int default 60 not null comment '有视频更新后，多久之内不再监控该页面',
    next_scan_time     datetime       null comment '下一次爬取的时间',
    latest_update_time datetime       null comment '最后一次监测到视频更新的时间',
    empty_cnt          int default 0  not null comment '连续查询结果为空的次数',
    constraint homepage_scan_record_homepage_url_md5_uindex
        unique (homepage_url_md5)
)
    comment '记录某个主页的监控时间频率，如果某个用户主页更新视频后，x小时以内不再监控该页面。';


create table shipinhao_user_info
(
    shipinhao_user_id  varchar(200) not null
        primary key,
    shipinhao_username varchar(200) null,
    publish_hours      varchar(200) null comment '账号的每日发布时间规划：[8,9,12,18,19,20,21]',
    latest_pub_time    datetime     null comment '最后一次的发布时间',
    machine_seq        bigint       null comment '设置由哪台机器运行',
    cookies            text         null,
    pub_num            int          null,
    update_time        datetime     null
);

