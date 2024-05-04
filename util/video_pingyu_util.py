import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from numpy.fft import fft2, ifft2, fftshift, ifftshift

from util.gradient_dedup import texture_synthesis, edge_blur
from video_dedup.config_parser import Config


def add_text_watermark(frame, text='Watermark', position=(50, 50), font_scale=5, thickness=3):
    """
    在频域上给单帧视频添加文字水印。
    :param frame: 单帧视频（灰度图像）。
    :param text: 水印文字。
    :param position: 文字水印的位置。
    :param font_scale: 字体大小。
    :param thickness: 字体粗细。
    :return: 添加了文字水印的视频帧。
    """
    # 使用傅里叶变换获取频域图像
    f = np.fft.fft2(frame)
    fshift = np.fft.fftshift(f)

    # 创建一个全黑的图像
    height, width = frame.shape[:2]

    # 创建一个全黑的图像
    watermark = np.zeros_like(frame)
    # 动态计算文字位置和大小
    text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)[0]
    position = (width - text_size[0]) // 2, (height - text_size[1]) // 2
    position2 = (width - 3 * text_size[0]) // 2, (height - 3 * text_size[1]) // 2
    # 在水印图像上添加文字
    cv2.putText(watermark, 'Buy it now.', position, cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), thickness)
    cv2.putText(watermark, 'Hello World', position2, cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), thickness)

    # 将水印图像的傅里叶变换添加到原始频域图像中
    watermark_f = np.fft.fft2(watermark)
    watermark_fshift = np.fft.fftshift(watermark_f)
    fshift_with_watermark = fshift + watermark_fshift * 0.02  # 调整水印强度

    # 逆傅里叶变换回时域
    f_ishift = np.fft.ifftshift(fshift_with_watermark)
    img_back = np.fft.ifft2(f_ishift)
    img_back = np.abs(img_back)

    return img_back.astype(np.uint8)


def phase_scrambling(frame, phase_shift=1):
    """
    对视频帧的频域数据进行相位打乱。
    :param frame: 单帧视频（灰度图像）。
    :param phase_shift: 相位偏移量。
    :return: 相位打乱后的视频帧。
    """
    # 傅里叶变换
    f = fft2(frame)
    fshift = fftshift(f)

    # 获取幅度和相位
    magnitude = np.abs(fshift)
    phase = np.angle(fshift)

    # 相位打乱
    phase = np.mod(phase + phase_shift, 2 * np.pi)

    # 重建频域图像
    fshift_scrambled = magnitude * np.exp(1j * phase)

    # 逆傅里叶变换
    f_ishift = ifftshift(fshift_scrambled)
    img_back = ifft2(f_ishift)
    img_back = np.abs(img_back)

    return img_back.astype(np.uint8)


def add_grid_text_watermarks(frame, text='Watermark', font_scale=0.5, thickness=1):
    """
    在频域上给单帧视频按4x4网格添加文字水印，每个网格添加一个水印。
    :param frame: 单帧视频（灰度图像）。
    :param text: 水印文字。
    :param font_scale: 字体大小。
    :param thickness: 字体粗细。
    :return: 添加了文字水印的视频帧。
    """
    # 使用傅里叶变换获取频域图像
    f = np.fft.fft2(frame)
    fshift = np.fft.fftshift(f)

    height, width = frame.shape[:2]
    watermark = np.zeros_like(frame)

    grid_size_x, grid_size_y = width // 4, height // 4

    # 在水印图像上的每个网格中心添加文字水印
    for i in range(4):
        for j in range(4):
            position = (i * grid_size_x + grid_size_x // 2, j * grid_size_y + grid_size_y // 2)
            cv2.putText(watermark, text, position, cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), thickness)

    # 将水印图像的傅里叶变换添加到原始频域图像中
    watermark_f = np.fft.fft2(watermark)
    watermark_fshift = np.fft.fftshift(watermark_f)
    fshift_with_watermark = fshift + watermark_fshift * 0.001  # 调整水印强度

    # 逆傅里叶变换回时域
    f_ishift = np.fft.ifftshift(fshift_with_watermark)
    img_back = np.fft.ifft2(f_ishift)
    img_back = np.abs(img_back)

    return img_back.astype(np.uint8)


def add_grid_text_watermarks_6x6(frame, text='Hello World, From JDB', font_scale=1, thickness=1):
    """
    在频域上给单帧视频按6x6网格添加文字水印，每个网格添加一个水印。
    :param frame: 单帧视频（灰度图像）。
    :param text: 水印文字。
    :param font_scale: 字体大小。
    :param thickness: 字体粗细。
    :return: 添加了文字水印的视频帧。
    """
    # 使用傅里叶变换获取频域图像
    f = np.fft.fft2(frame)
    fshift = np.fft.fftshift(f)

    height, width = frame.shape[:2]
    watermark = np.zeros_like(frame)

    grid_size_x, grid_size_y = width // 6, height // 6

    # 在水印图像上的每个网格中心添加文字水印
    for i in range(6):
        for j in range(6):
            position = (j * grid_size_x + grid_size_x // 3, i * grid_size_y + grid_size_y // 3)
            cv2.putText(watermark, text, position, cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), thickness)

    # 将水印图像的傅里叶变换添加到原始频域图像中
    watermark_f = np.fft.fft2(watermark)
    watermark_fshift = np.fft.fftshift(watermark_f)
    fshift_with_watermark = fshift + watermark_fshift * 0.01  # 调整水印强度

    # 逆傅里叶变换回时域
    f_ishift = np.fft.ifftshift(fshift_with_watermark)
    img_back = np.fft.ifft2(f_ishift)
    img_back = np.abs(img_back)

    return img_back.astype(np.uint8)


def add_chinese_watermarks(frame, text='好物推荐',
                           font_path='/Users/zhonghao/data/github_fonts/Android-ttf-download/字体/隶书.ttf', font_size=20):
    """
    在频域上给单帧视频按6x6网格添加中文文字水印。
    :param frame: 单帧视频（灰度图像）。
    :param text: 水印文字，支持中文。
    :param font_path: 中文字体的路径。
    :param font_size: 字体大小。
    :return: 添加了文字水印的视频帧。
    """
    height, width = frame.shape[:2]
    grid_size_x, grid_size_y = width // 6, height // 6

    # 将OpenCV图像转换为PIL图像
    frame_pil = Image.fromarray(frame)
    draw = ImageDraw.Draw(frame_pil)
    font = ImageFont.truetype(font_path, font_size)

    # 在每个网格中心添加中文水印
    for i in range(6):
        for j in range(6):
            position = (j * grid_size_x + grid_size_x // 3, i * grid_size_y + grid_size_y // 3)
            draw.text(position, text, font=font, fill=(255,))

    # 将PIL图像转换回OpenCV图像
    frame_with_text = np.array(frame_pil)

    # 使用傅里叶变换获取频域图像
    f = np.fft.fft2(frame_with_text)
    fshift = np.fft.fftshift(f)

    # 添加频域水印的其他步骤与之前相同...

    # 逆傅里叶变换回时域
    f_ishift = np.fft.ifftshift(fshift)
    img_back = np.fft.ifft2(f_ishift)
    img_back = np.abs(img_back)

    return img_back.astype(np.uint8)


def read_frames(video):
    if video.isOpened():
        ret, frame = video.read()
    else:
        ret = False
    frames = []
    while ret:
        ret, frame = video.read()
        if ret:
            frames.append(frame)
    return frames


def process_frame(frame, config: Config):
    new_frame = frame
    if config.enable_scrambling > 0:
        new_frame = phase_scrambling(frame, config.enable_scrambling)
    if config.enable_texture_syn:
        new_frame = texture_synthesis(new_frame)
    if config.enable_edge_blur:
        new_frame = edge_blur(new_frame)
    return new_frame
