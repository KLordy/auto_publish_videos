import time
import pyautogui
import os

# 打开剪映
import pyperclip

os.system("open /Applications/VideoFusion-macOS.app")  # 根据你的剪映安装路径进行修改

# 等待剪映加载完成
time.sleep(5)  # 等待5秒

# 快捷键创建项目 alt + n
pyautogui.keyDown('command')
pyautogui.press('n')
pyautogui.keyUp('command')
time.sleep(2)

# 将指定内容复制到粘贴板中
text_to_copy = "/Users/zhonghao/video/youtube/Removing Ganglion Cysts 😨 [t-br1YIyyiQ].mp4"
pyperclip.copy(text_to_copy)

# 快捷键 alt + i 开始导入视频
pyautogui.keyDown('command')
pyautogui.press('i')
pyautogui.keyUp('command')
time.sleep(2)  # 等待1秒

# 快捷键 shift + alt + g 准备录入视频地址
pyautogui.keyDown('shift')
pyautogui.keyDown('command')
pyautogui.press('g')
pyautogui.keyUp('shift')
pyautogui.keyUp('command')
time.sleep(5)  # 等待1秒

# 点击删除键，先删除已有内容
pyautogui.press('backspace')
time.sleep(2)
# 粘贴对应内容
# 找到文本提示位置，鼠标移动过去
text_path = '/Users/zhonghao/my_project/python_rpa/finder_前往文件夹提示.jpg'
text_location = pyautogui.locateCenterOnScreen(text_path, confidence=0.8)
pyautogui.moveTo(text_location[0], text_location[1])
pyautogui.rightClick()

# 找到粘贴位置，并点击
paste_btn_path = '/Users/zhonghao/my_project/python_rpa/finder右键呼出_粘贴.jpg'
paste_button_location = pyautogui.locateCenterOnScreen(paste_btn_path, confidence=0.8)
pyautogui.click(paste_button_location)
time.sleep(5)  # 等待1秒
pyautogui.press('enter')

# 图像识别定位：finder的导入按钮
finder_load_btn = '/Users/zhonghao/my_project/python_rpa/finder导入键.jpg'
finder_button_location = pyautogui.locateCenterOnScreen(finder_load_btn, confidence=0.8)
pyautogui.click(finder_button_location)
time.sleep(2)  # 等待1秒

# 图像识别定位：'/Users/zhonghao/video/rpa/剪映_素材左上角.jpg' 位置
video_top_left_path = '/Users/zhonghao/my_project/python_rpa/剪映_第一个素材左上角.jpg'
material_location = pyautogui.locateCenterOnScreen(video_top_left_path, confidence=0.8)

# 鼠标向下移动x个像素距离，从而鼠标光标选中第一个素材
pyautogui.moveTo(material_location[0] + 20, material_location[1] + 50)  # 向下移动100个像素
time.sleep(1)
# 图像识别定位：用'/Users/zhonghao/video/rpa/加号按钮.jpg'识别到加入音轨按钮，并点击加号导入到音轨
add_button_location = pyautogui.locateCenterOnScreen('/Users/zhonghao/my_project/python_rpa/剪映_素材加到音轨按钮.jpg',
                                                     confidence=0.8)
pyautogui.click(add_button_location)
time.sleep(2)

# 找到工作区，鼠标移动过去，点击右键
time_path = '/Users/zhonghao/my_project/python_rpa/剪映_工作区选择.jpg'
time_channel_location = pyautogui.locateCenterOnScreen(time_path, confidence=0.9)
pyautogui.moveTo(time_channel_location[0] + 100, time_channel_location[1])
time.sleep(3)
# pyautogui.rightClick(time_channel_location)
pyautogui.rightClick()
time.sleep(2)

# 找到识别字幕按钮，点击
recog_subtitle_path = '/Users/zhonghao/my_project/python_rpa/剪映_识别字幕按钮.jpg'
subtitle_btn = pyautogui.locateCenterOnScreen(recog_subtitle_path, confidence=0.8)
# pyautogui.moveTo(subtitle_btn[0], subtitle_btn[1])
pyautogui.leftClick(subtitle_btn)
time.sleep(2)

# 循环判断是否完成转换，完成则继续下一步
subtitle_ongoing_path = '/Users/zhonghao/my_project/python_rpa/剪映_字幕识别进行中.jpg'
for i in range(1, 30):
    try:
        subtitle_status = pyautogui.locateCenterOnScreen(subtitle_ongoing_path, confidence=0.8)
        if subtitle_status:
            print('字幕识别进行中，继续等待')
            time.sleep(2)
        else:
            break
    except pyautogui.ImageNotFoundException:
        print('字幕识别完毕，捕获异常')
        break


# 定位到导出按钮
output_btn_path = '/Users/zhonghao/my_project/python_rpa/剪映_导出.jpg'
output_btn = pyautogui.locateCenterOnScreen(output_btn_path, confidence=0.8)
pyautogui.click(output_btn)
time.sleep(1)

# 定位到 '视频导出按钮'，鼠标移动到这里，然后下滑，找到字幕导出按钮
video_output_btn_path = '/Users/zhonghao/my_project/python_rpa/剪映_视频导出按钮.jpg'
video_output_btn = pyautogui.locateCenterOnScreen(video_output_btn_path, confidence=0.8)
print(f'video_output_btn -> {video_output_btn}')
pyautogui.moveTo(video_output_btn[0], video_output_btn[1])
time.sleep(1)

pyautogui.scroll(1)
# 找到  40*20
subtitle_output_btn_path = '/Users/zhonghao/my_project/python_rpa/剪映_字幕导出.jpg'
subtitle_output_btn = pyautogui.locateCenterOnScreen(subtitle_output_btn_path, confidence=0.8)
# 水平移动 20 + 10 像素
pyautogui.moveTo(subtitle_output_btn[0] - 30, subtitle_output_btn[1])
pyautogui.click()

# 找到最终导出按钮点击run
final_output_btn_path = '/Users/zhonghao/my_project/python_rpa/剪映_最终导出按钮.jpg'

