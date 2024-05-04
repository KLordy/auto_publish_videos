###更新说明

- 20240504：初次更新，因为这个系统是完全自制自用的，而且因为和数据库进行交互，中间可能会存在部分内容在介绍中有所疏忽，如果有问题可以看最后的联系方式进行反馈，对应问题会定期同步更新文档。

###工作流程图
该项目主旨是完成一套全自动的视频采集 + 自动去重 + 自动上传的咔咔咔money printer system.

![github]("https://github.com/KLordy/blog_img/blob/main/20240501153309.png" "工作流")

###Feature
- [x] 定期自动采集视频数据
- [x] 视频自动下载
- [x] 自动批量去重
- [x] 视频号自动上传
- [x] cookie持久化到数据库
- [x] 飞书robot异常推送
- [ ] 抖音自动上传
- [ ] cookie独立更新

###Installation
- 安装mysql - 自行查阅资料
- 在mysql命令行中执行create_db.sql中代码进行db初始化建表
- 修改model.py中数据库连接信息： ``engine = create_engine('mysql+pymysql://root:root%40123@localhost:3306/video_tools')``
```shell
pip install -r requirements.txt
playwright install chromium firefox
```

###数据库表简介
![github]("https://github.com/KLordy/blog_img/blob/main/20240504172511.png" "mysql简介")

各个字段的介绍可以参考create_db.sql脚本，各个表的主要作用如下：
- download_video_info： 记录视频的状态
  - 'init'表示初始化下载的视频，不进行后续处理，避免初次启动时，对应up主主页历史视频被自动上传处理；
  - 'pending'表示视频已经下载好，可以进行后续的自动去重操作；
  - 'deduplicated'表示视频已经自动去重完毕；
  - 'published'表示视频已经自动上传完毕。

- shipinhao_user_info：主要记录视频号账户的cookie，以及限定账号的发布频率（频率过高可能会被风控判定为营销号出现0播、限流）
- homepage_scan_record：进行数据采集的用户爬取频率控制表，主要是通过时间纬度来进行限定，因为采用的是破解付费接口，所以这里对接口访问做了限流策略，避免被风控。

###任务配置说明

####视频下载采集任务配置介绍
process_homepage_download 和 download_videos 均读取download_config.ini配置，不过这个下载任务因为涉及破解第三方付费软件的采集下载接口，不宜进行开源，这部分内容需要各位自行补全；
或者如果没有开发能力的非技术人员，可以考虑直接自己先通过市面上的小程序或者免费的途径下载好需要下载的视频，然后统一存储到某个文件夹，然后使用后面的批量去重功能来进行视频导入。
对于有开发能力的技术同行，可以考虑自行破解或是购买相关接口来补全即可。

对于process_homepage_download任务的download_config.ini配置介绍如下： 
Key Point - 尤其注意init参数的说明
```ini
[homepage_urls] 
# 哪些用户主页视频需要进行数据采集
urls =
    https://www.douyin.com/user/MS4wLjABAAAA1bVR1TPXR27K1sn6kndEatAkV0CwCy5S_7PWzVd1PcAs5-2qP9JsATCFTdRu4fYY
    https://www.douyin.com/user/MS4wLjABAAAA5DTjH0fZcTBPdOsG6CkoeC4YtAT8uA92N-NvqHUjdAo

# 每个采集主页视频会上传到唯一的视频号账号中，这里必须和urls一一对应
target_account =
    佳佳好物推荐
    佳佳好物推荐

# 因为采集同步只上传最新视频，历史视频大概率已经被其它人搬运过，所以初次启动应用或者很长时间没有启动后，需要设置这里为true进行初次执行，表示是进行初始化，
# 设置为True执行完毕后，暂停任务，这里修改为False后重启，从而保证历史视频不会被搬运。
init = False

[cookies]
cookie1 = 'PHPSESSID=qh0hrf5tbfelmc2dlt43d1cc00; _ga=GA1.1.234159120.1704011845; cf_clearance=7y2.drC3iBr3u_B2RSbkjTTRJJSzr0_2qEYUYo3xv4c-1704108643-0-2-80f2808b.82482b03.d7f3df6b-0.2.1704108643; user_token=b122MDAwMDAwMDAwMGY4MDhlOTJhZjVlMmFkMDgyMzM1NwkxNjc2OTMzM2MxMzcxYjFhMWI1M2NmMWM0ZGQwNTE1OQ; mysid=ecdb745495f84ea785444b85254ccd1e; _ga_NVM5R0RWJE=GS1.1.1713833062.37.1.1713833063.0.0.0'
cookie2 = 'PHPSESSID=pe00fqjdenmljg20bk736746h3; _ga=GA1.1.1394971329.1712709141; mysid=77996ffd0687c4bb5b30af44f216764a; user_token=77c5MDAwMDAwMDAwMGY2NDk0ZWJjY2FmN2ZiNDc1MzU3MTIJOWFkYjFmNzIwMjJmMmRiZDI0YmE2MzI3NWRlMjA1Mjc; _ga_NVM5R0RWJE=GS1.1.1713833121.9.1.1713833122.0.0.0'

[save_path]
save_path = /Users/zhonghao/PycharmProjects/video_ai/output/download_video
```
以上配置的意思是：
- 任务会定期采集urls中配置的两个用户的主页视频数据，如果有新视频则会进行下载同步到download_video_info表中；
- 视频从哪个url解析到的，则上传到对应targe_account账号中；
- 配置了两个cookie，对应两个采集账号，每次会随机选取其中一个进行采集，避免被风控；
- 下载完毕的视频会存储到save_path路径下。

download_videos任务的download_config.ini配置如下：
```ini
[download_urls]
# 以下这些视频需要进行下载
urls =
    https://www.douyin.com/video/7339856213947010367
    https://www.douyin.com/video/7339860706549910834

# 这些作品的标签
[video_tags]
tags = 好物推荐

# 计划发布的账号名称，对应可以查到shipinhao_user_info表中用户
[target_account]
target_account = 佳佳好物推荐

# 下载的视频存储地址
[save_path]
save_path = /Users/zhonghao/PycharmProjects/video_ai/output/download_video
```

####自动去重任务配置介绍

dedup_video_from_db任务配置如下：
```ini
# 去重完毕后的视频存储地址
[save_path]
save_path = /Users/zhonghao/PycharmProjects/video_ai/wangdabao/f1

# 完成去重后原视频是否删除
[finish_step]
remove_finish = True
# 备份路径 - 视频删除的话会移动到这个路径做备份
backup_path = /Users/zhonghao/PycharmProjects/video_ai/wangdabao/backup

[dedup_step]
# 视频水平翻转角度，0表示不翻转，建议取值不超过3
reverse_angle = 1

# 是否启用画中画
add_hzh = True
# 画中画画面透明度
hzh_factor = 0.03
# 用于进行画中画的视频
hzh_video_path = /Users/zhonghao/PycharmProjects/video_ai/output/source/background.mp4

# 音频静默片段检测分贝阈值，-20 or -25 差不多属于人声无法听到部分，不要太大。
silent_db = -25
# 音频静默检测最低时长，单位毫秒，不建议太短，太短如果截取会导致声音正常停顿都没了，效果会导致说话非常非常快
silent_duration = 1000
# 检测到静默片段后，删除中间的多少时间，例如检测到1000ms的静默片段，这里设置0.5，则会删除中间的500ms，即 250-750 这个区间会被删除
# 这里选择删除中间部分是为了避免删除掉衔接的下一句话的开头，这个取值不建议太大，否则也会导致说话很快
# 这个值设置为0表示不检测和删除静默片段
silent_ratio = 0

# 视频进行镜像操作
mirror = False

# 饱和度、亮度、对比度三者开启的开关
enable_sbc = True
# 饱和度
saturation = 1.1
# 亮度
brightness = 0.1
# 对比度
contrast = 1.1

# 视频上下左右裁剪像素
crop_size = 10

# 水印文字：如果为''则表示不加水印
watermark_text =
# 水印类型，可以是文字、图片 or 视频，对应取值：text、image、video
watermark_type = 'text'
# 水印类型为image时，需要指定水印图片路径
watermark_image_path = ''
# 水印类型为video时，对应视频路径
watermark_video_path = ''
# 水印移动方向
# right-top-to-bottom：水印右侧从上往下移动
# top-left-to-right：水印顶上方从左往右移动  ->
# left-top-to-right-bottom：水印沿着左上和右下对角线移动
# bottom-left-to-right： 水印底部从左向右移动
watermark_direction = bottom-left-to-right

# 背景音频，如果设置为''则表示不加背景音频
bgm_audio_path = /Users/zhonghao/PycharmProjects/auto_publish_videos/bgm_silient.m4a

# 对于视频时长大于多少秒的视频才加字幕，对于一些十几秒的小视频，加字幕可能会全文文字堆积到一条字幕中，效果较差，因此加这个条件限制
# 如果不想给视频加字幕，这里取值可以设置一个非常非常大的取值
# 这里自动添加字幕使用了openai的whisper模型，如果需要自动加弹幕，需要下载相关model
srt_duration = 999999
# 字幕字体颜色：yellow, red, white, black等。
srt_font_color = 'yellow'


# 背景虚化开关，通过后续三个百分比参数，来调整画面
blur_background = True
# 视频上方虚化百分比
blur_top_percent = 2
# 下方虚化百分比
blur_bottom_percent = 2
# 左右两侧虚化百分比
blur_y_percent = 2


# 上方标题内容，如果取值为''则表示不加标题
top_title_text =
# 上方标题和顶部距离百分比
top_title_gap = 1
# 下方标题内容，默认取值'' 表示不加标题
bottom_title_text =
# 下方标题距离底部百分比
bottom_title_gap = 1


# 淡入时长，默认值0表示不设置淡入
fadein_duration = 0
# 淡出时长
fadeout_duration = 1

# 高斯模糊设置
# 每个多少帧设置一次模糊，如果不希望这个生效，可以设置0表示不做高斯模糊
gauss_step = 0
# 高斯模糊核，必须是单数，取值越小模糊程度越轻微
gauss_kernel = 0
# 高斯模糊尺寸
gauss_area_size = 0

# 每x帧为一组，对一组中的前两帧进行位置交换，实现打乱帧但是不影响观看，这里设置的值不能太小， 设置为0表示不生效
switch_frame_step = 10

# 配色方案调整，会将RGB变为临近色，可能会影响视觉效果，慎重使用
color_shift = False

# 频域相位打乱，设置0表示不开启 - 非常耗时的操作，预计为：耗时视频*4
enable_scrambling = 0
# 视频纹理修改
enable_texture_syn = True
# 边缘模糊处理
enable_edge_blur = True
```

####自动上传任务
任务主类sph_uploader，该任务完全读取来自download_video_info表中的deduplicated状态去重完毕的视频，上传到指定账号中，不存在ini配置文件。

###参考项目
https://github.com/dreammis/social-auto-upload
其中涉及h264不支持的问题，参考以上rep中提示，替换浏览器执行路径

###Communicate
探讨自动化上传、自动去重、自动剪辑、自动视频制作等内容，
可加v联系进群：KLordy
备注：github
