import hashlib
import os
import tempfile
from pathlib import Path

import requests

from common.conf import BASE_DIR


def download_video(url, output_filename):
    try:
        # 发送HTTP GET请求来获取视频数据
        response = requests.get(url, stream=True)
        response.raise_for_status()  # 检查是否有错误发生
        # tmp_file = base_video_url + 'tmp.mp4'
        # 打开一个本地文件用于保存视频数据
        with open(output_filename, 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)

        # 使用ffmpeg将视频文件转换为所需格式（可选）
        # ffmpeg.input(tmp_file).output(output_filename).run(overwrite_output=True)

        print(f"视频已成功下载到 {output_filename}")
    except Exception as e:
        print(f"下载视频时发生错误: {e}")


def get_mp4_files(folder_path):
    mp4_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".mp4"):
                path = os.path.join(root, file)
                mp4_files.append({"path": path, "file_name": file})
    return mp4_files


def get_temp_path(suffix):
    temp_file = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    temp_file_path = temp_file.name

    # 关闭临时文件，ffmpeg 输出流会自动写入到该临时文件中
    temp_file.close()
    return temp_file_path


def calculate_video_md5(file_path):
    # 打开视频文件
    with open(file_path, 'rb') as file:
        # 创建一个 MD5 对象
        md5 = hashlib.md5()

        # 读取文件内容并更新 MD5 值
        for chunk in iter(lambda: file.read(4096), b''):
            md5.update(chunk)

    # 获取计算得到的 MD5 值并返回
    return md5.hexdigest()


def get_account_file(user_id):
    user_ck_path = "{}_account.json".format(user_id)
    account_file = Path(BASE_DIR / "cookies" / user_ck_path)
    return account_file


def create_missing_dirs(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"文件夹 {folder_path} 创建成功")
