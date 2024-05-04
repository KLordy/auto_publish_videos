import ffmpeg
from pydub import AudioSegment


def merge_and_adjust_volumes(origin_audio, bgm_audio, origin_duration, volume_a=1.0, volume_b=0.6):
    # 获取音频a的时长
    # probe = ffmpeg.probe(origin_audio_file)
    # duration_a = float(next(stream for stream in probe['streams'] if stream['codec_type'] == 'audio')['duration'])

    # 输入音频a和b，设置音量
    origin_audio = origin_audio.filter('volume', volume=volume_a)
    bgm_audio = bgm_audio.filter('volume', volume=volume_b)

    # 截取音频b以匹配音频a的时长
    audio_b_trimmed = bgm_audio.filter('atrim', duration=origin_duration)

    # 合并音频a和截取后的音频b
    merged_audio = ffmpeg.filter([origin_audio, audio_b_trimmed], 'amix', duration='first')

    return merged_audio


def read_ffmpeg_audio_from_file(audio_path):
    return ffmpeg.input(audio_path).audio


def adjust_audio_duration(input_audio_path, output_audio_path, target_duration_seconds):
    # 打开输入音频文件
    audio = AudioSegment.from_file(input_audio_path)

    # 计算当前音频的持续时间（秒）
    current_duration_seconds = len(audio) / 1000.0

    # 计算速率调整因子
    speed_factor = current_duration_seconds / target_duration_seconds

    # 根据速率调整因子来调整音频速率
    adjusted_audio = audio.speedup(playback_speed=speed_factor)

    # 保存调整后的音频
    adjusted_audio.export(output_audio_path, format="wav")


def merge_audio_files(input_files, output_file):
    # 初始化一个空的音频段
    merged_audio = AudioSegment.empty()

    # 合并音频文件
    for input_file in input_files:
        audio_segment = AudioSegment.from_file(input_file)
        merged_audio += audio_segment

    # 保存合并后的音频
    merged_audio.export(output_file, format="wav")


def merge_audio_files_with_pause(input_files, output_file, pause_duration_ms=200):
    # 初始化一个空的音频段
    merged_audio = AudioSegment.empty()

    # 合并音频文件
    for input_file in input_files:
        audio_segment = AudioSegment.from_file(input_file)

        # 在每个音频文件后插入静音段
        if len(merged_audio) > 0:
            pause_segment = AudioSegment.silent(duration=pause_duration_ms)
            merged_audio += pause_segment

        merged_audio += audio_segment

    # 保存合并后的音频
    merged_audio.export(output_file, format="wav")