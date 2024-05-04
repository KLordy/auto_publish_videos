import tempfile

import ffmpeg
import math
from pydub import AudioSegment
from pydub.silence import detect_silence
import os


def video_properties(input_path):
    probe = ffmpeg.probe(input_path)
    video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
    width = int(video_info['width'])
    height = int(video_info['height'])
    duration = float(video_info['duration'])
    avg_bitrate = int(video_info['bit_rate'])
    print('width {}, height {}, duration {}'.format(width, height, duration))
    return width, height, duration, avg_bitrate


def get_video_audio(input_path):
    stream = ffmpeg.input(input_path)
    audio = stream.audio
    return audio, stream


def save_stream_to_video(video_stream, audio_stream, output_path, target_bitrate=5000):
    stream = ffmpeg.output(video_stream, audio_stream, output_path, y='-y', vcodec='libx264', preset='medium',
                           crf=18, **{'b:v': str(target_bitrate) + 'k'}).global_args('-tag:v', 'hvc1')
    ffmpeg.run(stream)


# def merge_video_temperary(video_stream, audio_stream, target_bitrate=5000):
#     # 创建临时文件
#     temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
#     temp_file_path = temp_file.name
#
#     # 关闭临时文件，ffmpeg 输出流会自动写入到该临时文件中
#     temp_file.close()
#     stream = ffmpeg.output(video_stream, audio_stream, temp_file_path, y='-y', vcodec='libx264', preset='medium',
#                            crf=18, **{'b:v': str(target_bitrate) + 'k'}).global_args('-tag:v', 'hvc1')
#     ffmpeg.run(stream)
#     return temp_file_path


def images_to_video(image_paths, temp_dir, output_file, bit_rate):
    # image_path = os.path.join(temp_dir, f"frame_{i:05d}.png")
    input_pattern = os.path.join(temp_dir, 'frame_%05d.png')
    (
        ffmpeg.input(input_pattern, framerate=30)
            .output(output_file, y='-y', vcodec='libx265', preset='medium', crf=18,
                    **{'b:v': str(bit_rate) + 'k'}).global_args('-tag:v', 'hvc1')
            .run()
    )


def save_audio_stream(audio_stream, audio_path):
    stream = ffmpeg.output(audio_stream, audio_path, y='-y')
    ffmpeg.run(stream)


def save_video_stream(video_stream, output_path):
    stream = ffmpeg.output(video_stream, output_path, y='-y')
    ffmpeg.run(stream)


def process_with_watermark(video_stream, audio_stream, output_path):
    ffmpeg.output(video_stream, audio_stream, output_path, y='-y', vf='drawtext=text="Watermark Text":x=10:y=10').run()
    # ffmpeg.run(stream)


def fadein_video(input_stream, duration):
    stream = input_stream.filter('fade', type='in', duration=duration)
    return stream


def fadeout_video(input_stream, video_duration, fade_duration):
    start = video_duration - fade_duration
    stream = input_stream.filter('fade', type='out', start_time=start, duration=fade_duration)
    return stream


def save_stream_with_fadein(video_stream, audio_stream, output_path, duration):
    stream = ffmpeg.output(video_stream, audio_stream, output_path, y='-y', vf='fade=in:0:{}'.format(duration))
    ffmpeg.run(stream)


# tested
def rotate_video(video_stream, angle):
    angle_radians = math.radians(angle)
    # Apply the rotation using ffmpeg
    stream = video_stream.filter('rotate', angle_radians)
    return stream


def mirror_video(video_stream):
    video_stream = video_stream.filter('hflip')
    return video_stream


def adjust_video_properties(input_stream, saturation=1.0, brightness=1.0, contrast=10.):
    input_stream = input_stream.filter('eq', brightness=brightness, contrast=contrast, saturation=saturation)
    return input_stream


def crop_video(input_stream, width, height, crop_size):
    # 计算裁剪后的宽度和高度
    crop_width = width - 2 * crop_size
    crop_height = height - 2 * crop_size

    # 执行裁剪操作
    # return input_stream.filter('crop', crop_width, crop_height, crop_size, crop_size).filter('scale', width, height)
    return input_stream.filter('crop', crop_width, crop_height, crop_size, crop_size)


def add_pip_to_video(background_video, pip_video, output_video, opacity=1.0):
    # 创建输入流
    input_background = ffmpeg.input(background_video)
    input_pip = ffmpeg.input(pip_video)

    # 对画中画视频进行缩放和透明度调整
    pip_scaled = input_pip.filter('scale', 160, 120)
    pip_with_opacity = pip_scaled.filter('lut', u=opacity)

    # 使用 overlay 过滤器将画中画视频叠加到背景视频上
    output = ffmpeg.overlay(input_background, pip_with_opacity, x='W-w-10', y='H-h-10')

    # 输出到文件
    ffmpeg.output(output, output_video, shortest=None).run()


def add_watermark(input_stream, watermark_content, watermark_type='text', direction='right-top-to-bottom', duration=5):
    if direction == 'right-top-to-bottom':
        x_expr = "W-w"
        y_expr = "mod(t*H/{},H)".format(duration)
    elif direction == 'top-left-to-right':
        x_expr = "mod(t*W/{},W)".format(duration)
        y_expr = "0"
    elif direction == 'left-top-to-right-bottom':
        x_expr = "mod(t*W/{},W)".format(duration)
        y_expr = "mod(t*H/{},H)".format(duration)
    elif direction == 'bottom-left-to-right':
        x_expr = "mod(t*W/{},W)".format(duration)
        y_expr = "H-h"

    if watermark_type == 'text':
        input_stream = input_stream.filter('drawtext', text=watermark_content, x=x_expr, y=y_expr, fontsize=26,
                                           fontcolor='yellow', borderw=1, bordercolor='red',
                                           fontfile='/Users/zhonghao/data/github_fonts/Android-ttf-download/字体/隶书.ttf')
    elif watermark_type == 'image':
        watermark_stream = ffmpeg.input(watermark_content)
        input_stream = ffmpeg.overlay(input_stream, watermark_stream, x=x_expr, y=y_expr)
    elif watermark_type == 'video':
        watermark_stream = ffmpeg.input(watermark_content)
        watermark_stream = watermark_stream.filter_('trim', duration=10)
        input_stream = ffmpeg.overlay(input_stream, watermark_stream, x=x_expr, y=y_expr)

    return input_stream


def add_blurred_background(input_stream, width, height, top_percent=5, bottom_percent=5, y_percent=5, target_width=720,
                           target_height=1280):
    scale_width = f"iw*(100-{y_percent}*2)/100"
    scale_height = f"ih*(100-{top_percent}-{bottom_percent})/100"

    # scaled_video = input_stream.filter('scale', scale_width, scale_height)

    blurred_background = input_stream.filter('scale', 'iw/2', 'ih/2').filter('boxblur', 10).filter('scale',
                                                                                                   target_width,
                                                                                                   target_height)
    # pos_x = round(width * y_percent / 100)
    # pos_y = round(height * top_percent / 100)
    pos_x = (target_width - width) // 2
    pos_y = (target_height - height) // 2

    # output = ffmpeg.overlay(blurred_background, scaled_video, x=pos_x, y=pos_y)
    output = ffmpeg.overlay(blurred_background, input_stream, x=pos_x, y=pos_y)
    return output


def add_title(input_stream, title, line_num=10, title_position='top', title_gap=5):
    if title:
        title_x = 'w/2-text_w/2'
        if title_position == 'top':
            title_y = f'h*{title_gap}/100'
        else:
            title_y = f'h-h*{title_gap}/100-text_h'
        input_stream = input_stream.drawtext(text=title, x=title_x, y=title_y, fontsize=38, fontcolor='yellow',
                                             shadowcolor='black', shadowx=4, shadowy=4,
                                             fontfile='/Users/zhonghao/data/github_fonts/Android-ttf-download/字体/隶书.ttf',
                                             borderw=1, bordercolor='red')

        # if title_position == 'top':
        #     title_y = f'h*{title_gap}/100+text_h+10'
        # else:
        #     title_y = f'h-h*{title_gap}/100+10'
        # input_stream = input_stream.drawtext(text='第二行第二次添加测试', x=title_x, y=title_y, fontsize=38, fontcolor='yellow',
        #                                      shadowcolor='black', shadowx=4, shadowy=4,
        #                                      fontfile='/Users/zhonghao/data/github_fonts/Android-ttf-download/字体/隶书.ttf',
        #                                      borderw=1, bordercolor='red')

    return input_stream


def remove_silent_video(input_path, origin_duration, silence_thresh, min_silence_len, cut_ratio):
    audio = AudioSegment.from_file(input_path)
    # min_silence_len = 500  # 最小静默长度
    # silence_thresh = -20  # 静默阈值（dB）
    silence_ranges = detect_silence(audio, min_silence_len, silence_thresh)
    silence_ranges_in_seconds = [(start / 1000, end / 1000) for start, end in silence_ranges]

    # 初始化 FFmpeg 输入
    input_video = ffmpeg.input(input_path)
    if cut_ratio == 0:
        return input_video.audio, input_video.video, origin_duration

    # 分割视频和音频
    video_clips = []
    audio_clips = []
    last_t = 0
    final_duration = 0.0  # 用于计算最终视频时长
    for start, end in silence_ranges_in_seconds:
        print('silent size :', end - start)
        delete_duration = (end - start) * cut_ratio / 2  # 得到头尾删除时长
        new_start = start + delete_duration
        new_end = end - delete_duration

        # 添加静默片段前的视频和音频
        v_clip = input_video.video.trim(start=new_start, end=new_end).setpts('PTS-STARTPTS')
        a_clip = input_video.audio.filter_('atrim', start=new_start, end=new_end).filter_('asetpts', 'PTS-STARTPTS')
        video_clips.append(v_clip)
        audio_clips.append(a_clip)
        final_duration += (new_end - new_start)

        last_t = end

    # 添加最后一个静默片段后的视频和音频
    v_final_clip = input_video.video.trim(start=last_t).setpts('PTS-STARTPTS')
    a_final_clip = input_video.audio.filter_('atrim', start=last_t).filter_('asetpts', 'PTS-STARTPTS')
    video_clips.append(v_final_clip)
    audio_clips.append(a_final_clip)

    final_duration += origin_duration - last_t
    print(f"Final Duration: {final_duration} seconds")

    # 拼接视频和音频
    joined_video = ffmpeg.concat(*video_clips, v=1, a=0)
    joined_audio = ffmpeg.concat(*audio_clips, v=0, a=1)
    return joined_audio, joined_video, final_duration


def generate_srt(transcription, srt_path, max_chars_per_line=25):
    srt_content = ""
    sentences = []
    paragrah = "<speak><p>"
    for i, segment in enumerate(transcription["segments"]):
        start_time = segment["start"]
        end_time = segment["end"]
        text = segment["text"]

        # 处理换行
        lines = []
        while text:
            lines.append(text[:max_chars_per_line])
            text = text[max_chars_per_line:]

        # 转换时间格式为 hh:mm:ss,ms
        start_timestamp = f"{int(start_time // 3600):02}:{int(start_time % 3600 // 60):02}:{int(start_time % 60):02},{int(start_time % 1 * 1000):03}"
        end_timestamp = f"{int(end_time // 3600):02}:{int(end_time % 3600 // 60):02}:{int(end_time % 60):02},{int(end_time % 1 * 1000):03}"

        # 将文本和时间戳添加到 SRT 内容中
        content = '\n'.join(lines)
        srt_content += f"{i + 1}\n{start_timestamp} --> {end_timestamp}\n{content}\n\n"

        segment['duration'] = end_time - start_time
        sentences.append(segment)
        paragrah = paragrah + "<s>" + text + "</s>"
    paragrah = paragrah + "</p></speak>"
    # with open("/Users/zhonghao/PycharmProjects/video_ai/output/audio/result/large_transcription_specified_lang.srt",
    with open(srt_path, "w") as file:
        file.write(srt_content)
    return srt_content, sentences, paragrah


color_mapping = {
    'red': '0000FF',
    'green': '00FF00',
    'blue': 'FF0000',
    'yellow': '00FFFF',
    'white': 'FFFFFF',
    # 可以根据需要添加更多颜色
}


def add_subtitles(video_stream, subtitle_path, font_path, font_size, font_color_name):
    font_color_code = color_mapping.get(font_color_name.lower(), 'FFFFFF')  # 默认白色

    # output = video_stream.filter('subtitles', filename=subtitle_path,
    #                              force_style=f'FontName={font_path},FontSize={font_size},PrimaryColour=&H00{font_color_code},OutlineColour=&H00{border_color_code},BorderStyle=1,BorderW={borderw},BackColour=&H00000000')

    output = video_stream.filter('subtitles', filename=subtitle_path,
                                 force_style=f'FontName={font_path},FontSize={font_size},PrimaryColour=&H00{font_color_code}')
    return output
