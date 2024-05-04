import cv2
import numpy as np


def gradient_noise(frame):
    """
    在梯度域中加入噪声。
    """
    # 计算x和y方向的梯度
    grad_x = cv2.Sobel(frame, cv2.CV_64F, 1, 0, ksize=3)
    grad_y = cv2.Sobel(frame, cv2.CV_64F, 0, 1, ksize=3)
    # 计算梯度的幅度
    magnitude = np.sqrt(grad_x ** 2 + grad_y ** 2)
    # 在梯度幅度上加入随机噪声
    noise = np.random.randn(*magnitude.shape) * 0.01  # 噪声强度
    magnitude_noisy = magnitude + noise
    # 用噪声幅度重建图像（这里简化处理，实际应用中需要更复杂的重建过程）
    frame_noisy = frame + magnitude_noisy.astype(np.uint8)
    return frame_noisy


def texture_synthesis(frame):
    """
    对视频帧进行简单的纹理修改。
    """
    # 生成一个简单的纹理图案
    texture = np.random.rand(*frame.shape[:2]) * 255
    texture = texture.astype(np.uint8)
    # 将纹理图案以低透明度叠加到原始帧上
    alpha = 0.02
    frame = cv2.addWeighted(frame, 1 - alpha, cv2.cvtColor(texture, cv2.COLOR_GRAY2BGR), alpha, 0)
    return frame


def edge_blur(frame):
    """
    对视频帧的边缘进行模糊处理。
    """
    # 使用Canny边缘检测找到边缘
    edges = cv2.Canny(frame, 100, 200)
    # 将边缘转换为mask
    mask = edges != 0
    # 对原始帧应用高斯模糊
    blurred_frame = cv2.GaussianBlur(frame, (3, 3), 0)
    # 只在边缘应用模糊效果
    frame[mask] = blurred_frame[mask]
    return frame
