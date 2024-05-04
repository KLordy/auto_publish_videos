# 调用yt-dlp下载英文vtt字幕
# 读取db中待转录的视频
# 将vtt文件转换为srt文件  1
# 调用api翻译英文字幕
# 记录英文字幕每一句的范围  english_a -> [start, end]
# 中文字幕全文 text to speech 得到音频  chinese_total | chinese_a -> english_a -> [start, end]
# 调用阿里云 text to speech
# 依据音频调用whisper得到字幕
# 此时英文字幕a的时间范围和对应中文字幕的时间范围是不一致的，需要进行调整
# 将中文音频依据句子进行分割，同时英文字幕也进行分割
# 此时依据英文音频duration来逐句调整中文音频的时长，进行变速操作
# 合并所有的中文音频，得到最终音频
# 音频和视频进行合并