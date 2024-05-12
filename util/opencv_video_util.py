import random

import cv2
import os
import numpy as np
import math
# from 测试2 import *
import tempfile


# opencv格式读取视频
def opencv_read_video_from_path(video_path):
    return cv2.VideoCapture(video_path)


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


def save_images(frames, base_dir):
    for i in range(len(frames)):
        # image_path = '{}/{}.jpg'.format(dirs, str(num))
        image_path = base_dir + '/{}.jpg'.format(str(i))
        cv2.imwrite(image_path, frames[i])


def save_frames_as_images(frames):
    # 创建临时目录来保存图片
    temp_dir = tempfile.mkdtemp()
    image_paths = []
    for i, frame in enumerate(frames):
        image_path = os.path.join(temp_dir, f"frame_{i + 1:05d}.png")
        cv2.imwrite(image_path, frame)
        image_paths.append(image_path)
    return image_paths, temp_dir


def read_images(image_folder, img_size=100):
    images = []
    frame_num = frame_size(image_folder)
    if 2 * img_size > frame_num:
        num = frame_num
    else:
        num = 2 * img_size

    for i in range(1, num):
        image_path = f"{image_folder}/{i}.jpg"
        image = cv2.imread(image_path)
        if image is not None:
            images.append(image)
    return images


def frame_size(video_folder):
    frame_num = 0
    for root, dirs, files in os.walk(video_folder):
        frame_num += len(files)
    return frame_num


# 随机打乱帧，例如每隔2帧互换，1/3互换；4/6互换；7/9互换
def rdm_frames(images, gap):
    image_size = len(images)
    steps = int(image_size / gap)
    for i in range(0, steps):
        start = i * gap
        end = start + (gap - 1)
        images[start], images[end] = images[end], images[start]
    return images


# 每gap帧内，随机删除一帧
def remove_frame(images, gap):
    # 30帧
    image_size = len(images)
    steps = int(image_size / gap)
    result = []
    for i in range(1, steps):
        start = (i - 1) * gap
        end = i * gap
        delete_frame = random.randint(start, end)
        for j in range(start, end):
            if j != delete_frame:
                result.append(images[j])
    return result


def huazhonghua(images, alpha_factor=0.05):
    switch_path = "/Users/zhonghao/PycharmProjects/video_ai/output/overlay_img"
    image_size = len(images)
    switch_frames = read_images(switch_path, img_size=image_size)
    change_size = len(switch_frames)
    # 30帧
    first_img = images[0]
    origin_height = first_img.shape[0]
    origin_width = first_img.shape[1]
    result = []
    for img in images:
        selected = random.randint(0, change_size - 1)
        selected_img = resize_img(switch_frames[selected], origin_width, origin_height)
        transparent_img = cv2.addWeighted(img, 1 - alpha_factor, selected_img, alpha_factor, 1)
        result.append(transparent_img)
    return result


def huazhonghua_by_config(images, alpha_factor=0.05, hzh_video='/Users/zhonghao/PycharmProjects/video_ai/output/source/background.mp4'):
    video_capture = opencv_read_video_from_path(hzh_video)
    hzh_frames = read_frames(video_capture)
    hzh_size = len(hzh_frames)

    first_img = images[0]
    origin_height = first_img.shape[0]
    origin_width = first_img.shape[1]

    result = []
    for img in images:
        selected = random.randint(0, hzh_size - 1)
        selected_img = resize_img(hzh_frames[selected], origin_width, origin_height)
        transparent_img = cv2.addWeighted(img, 1 - alpha_factor, selected_img, alpha_factor, 1)
        result.append(transparent_img)

    return result


# 改变图片的透明度
def change_img_transparent(img, alpha_factor):
    channel_size = int(img.shape[2])
    if channel_size == 3:
        # b_channel, g_channel, r_channel = cv2.split(img)
        # alpha_channel = np.ones(b_channel.shape, dtype=b_channel.dtype) * 255
        # alpha_channel[:, :(int(b_channel.shape[0]) * 2)] = alpha_num
        # res = cv2.merge((b_channel, g_channel, r_channel, alpha_channel))
        # return res
        # alpha_factor = 0.1
        image_with_alpha = (img * alpha_factor).astype(np.uint8)
        return image_with_alpha

    if channel_size == 4:
        return img


def set_video_codec():
    fourcc = cv2.VideoWriter_fourcc(*'X265')
    return fourcc


def create_video_writer(output_file, frame_rate, frame_size, video_codec):
    video_writer = cv2.VideoWriter(output_file, video_codec, frame_rate, frame_size)
    return video_writer


def write_images_to_video(video_writer, images):
    for image in images:
        video_writer.write(image)


def resize_img(image, width, height):
    size = (width, height)
    return cv2.resize(image, size)


def frames_to_video(frames, output_file):
    print('使用{}帧数据来生成视频'.format(str(len(frames))))
    video_codec = cv2.VideoWriter_fourcc(*'X264')
    shape = frames[0].shape
    size = (shape[1], shape[0])
    video_writer = cv2.VideoWriter(output_file, video_codec, 30, size)
    for image in frames:
        video_writer.write(image)
    video_writer.release()
    cv2.destroyAllWindows()


# def 每隔x帧随机选择一帧检测边缘进行膨胀(images, gap):
#     # 30帧
#     # image_size = len(images)
#     # steps = math.ceil(image_size / gap)
#     image_size = 10
#     steps = 5
#     result = []
#     for i in range(0, steps):
#         start = i * gap
#         end = (i + 1) * gap
#         if end > image_size:
#             end = image_size - 1
#         change_frame = random.randint(start, end)
#         for j in range(start, end + 1):
#             if j != change_frame:
#                 result.append(images[j])
#             else:
#                 # blured_img = 检测边缘进行膨胀(images[j], 100, 200, 3, 800, j, highlight_color=(0, 255, 0))
#                 blured_img = 检测边缘进行膨胀2(images[j], 50, 150, 111, 20, 500, j)
#                 result.append(blured_img)
#     return result


def 检测边缘进行膨胀(image, low_threshold, high_threshold, dilation_size, min_contour_area, idx,
             highlight_color=(0, 255, 0)):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 应用Canny边缘检测
    edges = cv2.Canny(gray_image, low_threshold, high_threshold)

    # 查找轮廓
    contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    # 过滤太小的轮廓
    filtered_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_contour_area]

    # 随机选择两个轮廓（如果存在的话）
    if len(filtered_contours) >= 8:
        selected_contours = random.sample(filtered_contours, 8)
    else:
        selected_contours = filtered_contours
    print('边缘膨胀： 第' + str(idx) + '帧，筛选出轮廓' + str(len(selected_contours)) + '个')
    # 创建一个空白图像来画选中的轮廓
    contour_img = np.zeros_like(edges)

    # 画出选中的轮廓
    cv2.drawContours(contour_img, selected_contours, -1, (255, 255, 255), thickness=cv2.FILLED)

    # 创建用于膨胀的核
    kernel = np.ones((dilation_size, dilation_size), np.uint8)

    # 对选中的轮廓边缘进行膨胀
    dilated_contours = cv2.dilate(contour_img, kernel, iterations=10)

    # 在原始图像上标记被修改的区域
    highlighted_image = image.copy()
    highlighted_image[dilated_contours != 0] = highlight_color

    combined = np.hstack((image, highlighted_image))
    return combined


def 每隔x帧随机选择一帧加随机模糊区域(images, gap, gauss_kernel, gauss_area_size):
    # 30帧
    image_size = len(images)
    # 57 / 20 = 3
    steps = math.ceil(image_size / gap)
    result = []
    print('开始处理{}帧模糊处理'.format(str(steps)))
    for i in range(0, steps):
        start = i * gap
        end = (i + 1) * gap
        if end >= image_size:
            end = image_size
        change_frame = random.randint(start, end)
        for j in range(start, end):
            if j != change_frame:
                result.append(images[j])
            else:
                print('模糊处理的帧', j)
                blured_img = random_gaussian_blur(images[j], area_size=gauss_area_size, kernel_size=gauss_kernel)
                result.append(blured_img)
    return result


def 随机模糊处理(image, num_regions, region_size, blur_degree, j):
    height, width = image.shape[:2]
    blurred_image = image.copy()
    roi_size = 0
    for _ in range(num_regions):
        x = np.random.randint(0, width - region_size[1])
        y = np.random.randint(0, height - region_size[0])
        roi = blurred_image[y:y + region_size[0], x:x + region_size[1]]
        blurred_roi = cv2.GaussianBlur(roi, (0, 0), blur_degree)
        roi_size = roi_size + 1
        blurred_image[y:y + region_size[0], x:x + region_size[1]] = blurred_roi

    print('处理高斯模糊{}'.format(j))
    return blurred_image


def random_gaussian_blur(frame, area_size=500, kernel_size=5):
    # frame = img.copy()
    # 获取图片尺寸
    height, width = frame.shape[:2]

    # 确保随机区域不会超出图片边界
    x = random.randint(0, width - area_size)
    y = random.randint(0, height - area_size)

    # 提取要模糊的区域
    roi = frame[y:y + area_size, x:x + area_size]

    # 应用高斯模糊
    blurred_roi = cv2.GaussianBlur(roi, (kernel_size, kernel_size), 0)

    # 将模糊后的区域放回原图
    frame[y:y + area_size, x:x + area_size] = blurred_roi

    return frame


def switch_frames_with_step(frames, step=5):
    """
    对给定的视频帧集合进行处理，根据指定的步长进行分组，然后在每组中交换最开始的两帧。
    :param frames: 原始视频帧集合。
    :param step: 分组的步长。
    :return: 位置调换后的新视频帧集合。
    """
    new_frames = frames.copy()  # 复制原始帧集合以避免修改原始数据

    # 根据步长遍历帧集合，进行指定位置的帧交换
    for i in range(0, len(frames), step):
        if i + 1 < len(frames):  # 确保有足够的帧进行交换
            new_frames[i], new_frames[i + 1] = new_frames[i], new_frames[i]

    return new_frames


def adjust_colors(images, max_shift=10):
    """
    自动调整图像的配色方案。
    :param images: 原始图像。
    :param max_shift: 颜色分量的最大随机偏移量。
    :return: 调整配色后的图像。
    """
    # 确保偏移量不会造成颜色分量超出有效范围[0, 255]
    adjusted_frames = []
    for i in range(0, len(images)):
        frame = images[i]
        adjusted_image = np.clip(frame + np.random.randint(-max_shift, max_shift + 1, frame.shape), 0, 255).astype(
            np.uint8)
        adjusted_frames.append(adjusted_image)

    return adjusted_frames
