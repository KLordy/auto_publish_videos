import os
import shutil
import time
from concurrent.futures import ThreadPoolExecutor

from util.ffmpeg_python_util import *
from util.file_util import *
from util.opencv_video_util import *
from util.video_pingyu_util import process_frame
from video_dedup.config_parser import Config
from util.audio_util import *
from util.model_util import whisper_model
import functools


def process_dedup_by_config(input_video, final_video_path, config: Config):
    time0 = time.time()
    # input_video = '/Users/zhonghao/PycharmProjects/video_ai/demo/shop_demo.mp4'
    # angle = 1  # 要翻转的角度
    # remove_silented_video = '/Users/zhonghao/PycharmProjects/video_ai/output/ffmpeg_python/transform_pipeline_remove_tmp.mp4'
    # output_video = '/Users/zhonghao/PycharmProjects/video_ai/output/ffmpeg_python/transform_pipeline_1.mp4'
    # ffmpeg_final_video = '/Users/zhonghao/PycharmProjects/video_ai/output/ffmpeg_python/transform_pipeline_2.mp4'

    width, height, origin_duration, bit_rate = video_properties(input_video)

    # 1. 先检测静默音频，并删除部分静默音频对应片段，获取到处理后的音频 & 视频
    audio_stream, video_stream, video_duration = remove_silent_video(input_video, origin_duration, config.silent_db,
                                                                     config.silent_duration, config.silent_ratio)

    # 2. 视频镜像
    if config.mirror:
        video_stream = mirror_video(video_stream)

    # 3. 视频旋转3度
    if config.reverse_angle > 0:
        video_stream = rotate_video(video_stream, config.reverse_angle)

    # 4. 调整亮度(默认不变值0)、对比度（默认不变值1）、饱和度（默认不变值1）
    if config.enable_sbc:
        video_stream = adjust_video_properties(video_stream, saturation=config.saturation, brightness=config.brightness,
                                               contrast=config.contrast)

    # 5. 裁剪视频
    if config.crop_size > 0:
        video_stream = crop_video(video_stream, width, height, config.crop_size)

    # 6. 添加文字 or 图片 or 视频水印
    if config.watermark_text != '':
        video_stream = add_watermark(video_stream, config.watermark_text, watermark_type=config.watermark_type,
                                     direction=config.watermark_direction, duration=video_duration)

    bgm_path = '/Users/zhonghao/PycharmProjects/video_ai/demo/bgm_silient.m4a'
    merged_audio = audio_stream
    if config.bgm_audio_path != '':
        print('config.bgm_audio_path -> ', config.bgm_audio_path)
        bgm_audio = read_ffmpeg_audio_from_file(config.bgm_audio_path.strip())
        merged_audio = merge_and_adjust_volumes(audio_stream, bgm_audio, video_duration)

    tt = time.time()
    print('step1 cost time ', tt - time0)

    # 8. 添加字幕 -- 对于视频时长太短的小视频，不需要加字幕 -- todo 对于本身就有字幕的，也不需要加字幕。
    audio_path_tmp = ''
    srt_path_tmp = ''
    if origin_duration > config.srt_duration:
        # 先存储音频文件到本地
        audio_path_tmp = get_temp_path('.mp3')
        save_audio_stream(audio_stream, audio_path_tmp)
        # 依据音频调用模型得到结果
        srt_result = whisper_model(audio_path_tmp)
        # 生成srt文件
        srt_path_tmp = get_temp_path('.srt')
        generate_srt(srt_result, srt_path_tmp)
        # 依据srt文件，在视频中加字幕
        font_path = '/Users/zhonghao/data/github_fonts/Android-ttf-download/字体/隶书.ttf'
        # todo 要对字体font颜色进行一下校验，防止拼写错误等问题
        video_stream = add_subtitles(video_stream, srt_path_tmp, font_path, 10, config.srt_font_color)

    # 初步持久化
    output_video_tmp = get_temp_path('.mp4')
    save_stream_to_video(video_stream, merged_audio, output_video_tmp, bit_rate)

    # 解析同步后的新视频原数据
    audio_stream, video_stream = get_video_audio(output_video_tmp)
    width, height, duration, avg_bit_rate = video_properties(output_video_tmp)

    # 9. 虚化背景
    if config.blur_background:
        video_stream = add_blurred_background(video_stream, width=width, height=height,
                                              top_percent=config.blur_top_percent,
                                              bottom_percent=config.blur_bottom_percent,
                                              y_percent=config.blur_y_percent)

    # 10. 添加title 和 description
    if config.top_title_text != '':
        video_stream = add_title(video_stream, title='日常百货好物分享',
                                 title_gap=config.top_title_gap, title_position='top')

    if config.bottom_title_text != '':
        video_stream = add_title(video_stream, title='点击头像橱窗同款哦',
                                 title_gap=config.bottom_title_gap, title_position='bottom')

    # 11. 视频淡入淡出
    if 0 < config.fadein_duration < duration:
        video_stream = fadein_video(video_stream, config.fadein_duration)

    if 0 < config.fadeout_duration < duration:
        video_stream = fadeout_video(video_stream, video_duration=duration, fade_duration=config.fadeout_duration)

    # ffmpeg处理结束
    ffmpeg_tmp = get_temp_path('.mp4')
    save_stream_to_video(video_stream, audio_stream, ffmpeg_tmp, bit_rate)
    time00 = time.time()
    print('opencv前耗时', (time00 - time0))
    # 12. opencv随机进行高斯模糊
    opencv_tmp = get_temp_path('.mp4')
    video_capture = opencv_read_video_from_path(ffmpeg_tmp)
    frames = read_frames(video_capture)
    if config.gauss_step > 0:
        frames = 每隔x帧随机选择一帧加随机模糊区域(frames, config.gauss_step, config.gauss_kernel, config.gauss_area_size)

    if config.switch_frame_step > 0:
        frames = switch_frames_with_step(frames, step=config.switch_frame_step)

    if config.color_shift:
        frames = adjust_colors(frames)

    if config.add_hzh:
        frames = huazhonghua_by_config(frames, config.hzh_factor, config.hzh_video_path)

    # 创建一个带有默认参数的函数
    if config.enable_scrambling > 0 or config.enable_texture_syn or config.enable_edge_blur:
        partial_process_frame = functools.partial(process_frame, config=config)
        with ThreadPoolExecutor(max_workers=5) as executor:
            frames = list(executor.map(partial_process_frame, frames))

    # 先将frames生成得到静音的视频
    frames_to_video(frames, opencv_tmp)

    # ffmpeg读取静音视频，用于后续和音频进行合并
    silent_audio, silent_video = get_video_audio(opencv_tmp)
    # 合并音频和视频
    save_stream_to_video(silent_video, merged_audio, final_video_path, bit_rate)

    time1 = time.time()
    print('视频去重耗时: {}, 视频时长：{}'.format(time1 - time0, origin_duration))
    if srt_path_tmp != '':
        os.remove(srt_path_tmp)
    if audio_path_tmp != '':
        os.remove(audio_path_tmp)
    if opencv_tmp:
        os.remove(opencv_tmp)
    if output_video_tmp:
        os.remove(output_video_tmp)
    if ffmpeg_tmp:
        os.remove(ffmpeg_tmp)


def get_mp4_files(folder_path):
    mp4_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".mp4"):
                path = os.path.join(root, file)
                mp4_files.append({"path": path, "file_name": file})
    return mp4_files


def frames_to_video_with_ffmpeg(frames, output_file, bit_rate):
    image_paths, temp_dir = save_frames_as_images(frames)
    images_to_video(image_paths, temp_dir, output_file, bit_rate)
    # 清理临时文件
    shutil.rmtree(temp_dir)
