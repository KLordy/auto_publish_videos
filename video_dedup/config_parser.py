import configparser


class Config:
    def __init__(self):
        self.save_path = ''
        self.video_path = ''
        self.remove_finish = False
        self.reverse_angle = 0
        self.silent_db = -20
        self.silent_duration = 1000
        self.silent_ratio = 0.1
        self.mirror = False
        self.saturation = 1.0
        self.brightness = 0.0
        self.contrast = 1.0
        self.crop_size = 0
        self.watermark_text = ''
        self.watermark_type = 'text'
        self.watermark_direction = 'right-top-to-bottom'
        self.bgm_audio_path: str = ''
        self.srt_duration = 99999
        self.srt_font_color = 'yellow'
        self.blur_background = False
        self.blur_top_percent = 0
        self.blur_bottom_percent = 0
        self.blur_y_percent = 0
        self.top_title_text = ''
        self.top_title_gap = 0
        self.bottom_title_text = ''
        self.bottom_title_gap = 0
        self.fadein_duration = 0
        self.fadeout_duration = 0
        self.gauss_step = -1
        self.gauss_kernel = 29
        self.gauss_area_size = 200
        self.switch_frame_step = 10
        self.color_shift = False
        self.enable_scrambling = 1
        self.enable_texture_syn = False
        self.enable_edge_blur = False
        self.enable_sbc = False
        self.add_hzh = False
        self.hzh_factor = 0.1
        self.hzh_video_path = ''
        self.backup_path = ''
        self.write_db = False
        self.target_pub_user_id = ''
        self.external_dedup_video_path = ''
        self.data = ''


def read_dedup_config():
    config = Config()
    parser = configparser.ConfigParser()
    parser.read('dedup_config.ini')

    config.add_hzh = parser.getboolean('dedup_step', 'add_hzh')
    config.hzh_factor = parser.getfloat('dedup_step', 'hzh_factor')
    config.hzh_video_path = parser.get('dedup_step', 'hzh_video_path')

    config.save_path = parser.get('save_path', 'save_path')
    config.video_path = parser.get('video_path', 'video_path')
    config.external_dedup_video_path = parser.get('video_path', 'external_dedup_video_path')
    config.remove_finish = parser.getboolean('finish_step', 'remove_finish')
    config.target_pub_user_id = parser.get('finish_step', 'target_pub_user_id')
    config.write_db = parser.getboolean('finish_step', 'write_db')
    config.backup_path = parser.get('finish_step', 'backup_path')
    config.reverse_angle = parser.getint('dedup_step', 'reverse_angle')
    config.silent_db = parser.getfloat('dedup_step', 'silent_db')
    config.silent_duration = parser.getint('dedup_step', 'silent_duration')
    config.silent_ratio = parser.getfloat('dedup_step', 'silent_ratio')
    config.mirror = parser.getboolean('dedup_step', 'mirror')
    config.enable_sbc = parser.getboolean('dedup_step', 'enable_sbc')
    config.saturation = parser.getfloat('dedup_step', 'saturation')
    config.brightness = parser.getfloat('dedup_step', 'brightness')
    config.contrast = parser.getfloat('dedup_step', 'contrast')
    config.crop_size = parser.getint('dedup_step', 'crop_size')
    config.watermark_text = parser.get('dedup_step', 'watermark_text')
    config.watermark_type = parser.get('dedup_step', 'watermark_type')
    config.watermark_direction = parser.get('dedup_step', 'watermark_direction')
    config.bgm_audio_path = parser.get('dedup_step', 'bgm_audio_path')
    config.srt_duration = parser.getfloat('dedup_step', 'srt_duration')
    config.srt_font_color = parser.get('dedup_step', 'srt_font_color')
    config.blur_background = parser.getboolean('dedup_step', 'blur_background')
    config.blur_top_percent = parser.getfloat('dedup_step', 'blur_top_percent')
    config.blur_bottom_percent = parser.getfloat('dedup_step', 'blur_bottom_percent')
    config.blur_y_percent = parser.getfloat('dedup_step', 'blur_y_percent')
    config.top_title_text = parser.get('dedup_step', 'top_title_text')
    config.top_title_gap = parser.getfloat('dedup_step', 'top_title_gap')
    config.bottom_title_text = parser.get('dedup_step', 'bottom_title_text')
    config.bottom_title_gap = parser.getfloat('dedup_step', 'bottom_title_gap')
    config.fadein_duration = parser.getint('dedup_step', 'fadein_duration')
    config.fadeout_duration = parser.getint('dedup_step', 'fadeout_duration')
    config.gauss_step = parser.getint('dedup_step', 'gauss_step')
    config.gauss_kernel = parser.getint('dedup_step', 'gauss_kernel')
    config.gauss_area_size = parser.getint('dedup_step', 'gauss_area_size')
    config.switch_frame_step = parser.getint('dedup_step', 'switch_frame_step')
    config.color_shift = parser.getboolean('dedup_step', 'color_shift')
    config.enable_scrambling = parser.getint('dedup_step', 'enable_scrambling')
    config.enable_texture_syn = parser.getboolean('dedup_step', 'enable_texture_syn')
    config.enable_edge_blur = parser.getboolean('dedup_step', 'enable_edge_blur')
    config.data = parser.get('json_map', 'data')

    return config
