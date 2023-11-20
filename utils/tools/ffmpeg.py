import os
import subprocess
import requests
import logging
logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

def get_video_duration(file_path):
    try:
        result = subprocess.check_output(f"ffmpeg -i '{file_path}' 2>&1 | grep 'Duration'", shell=True, text=True)
        duration_str = result.split('Duration: ')[1].split(',')[0].strip()
        h, m, s = map(float, duration_str.split(':'))
        return int(h * 3600 + m * 60 + s)
    except subprocess.CalledProcessError:
        logger.error("获取视频时长失败")
        return None

def upload_to_chevereto(image_path,i):
    url = 'https://img.kimoji.club'
    api_key = 'chv_Qv3_df17c2e80aa516206778a352b3eff8b98bb80779924fa9d63acfd077c05d31fb6b0d443b7768550efc9be2cd02dcfe02ed4b0c72a0a1d32de328ae5aa8ac81c4'
    try_num = 0
    while try_num < 3:
        try:
            payload = {
                'key': api_key,
                'format': 'json',
            }
            files = {
                'source': open(image_path, 'rb')
            }
            response = requests.post(url + '/api/1/upload',files=files,data=payload)
            response.raise_for_status()
            image_url = response.json().get('image', {}).get('url')

            if image_url:
                logger.info(f"第{i}张图片上传成功: {image_url}")
                return f"[img]{image_url}[/img]"
            else:
                logger.warning(f"第{i}张图片上传失败，无返回链接")
                try_num += 1

        except requests.RequestException as e:
            logger.warning(f"第{i}张图片上传失败: {e}")
            try_num += 1

    logger.error(f"第{i}张图片连续三次上传失败")
    return None

def screenshot_from_video(file_path, folder_path, pic_num):
    logger.info('开始截图')
    duration = get_video_duration(file_path)
    if not duration:
        logger.error("无法获取视频时长")
        return

    start_time = 60
    end_time = duration - 60
    intervals = (end_time - start_time) // (pic_num + 1)
    image_paths = []  # 用于收集所有截图的路径

    for i in range(1, pic_num + 1):
        screenshot_time = start_time + i * intervals
        screenshot_name = f"{i}.jpg"
        screenshot_path = os.path.join(folder_path, screenshot_name)
        command = f"ffmpeg -y -ss {screenshot_time} -i '{file_path}' -frames:v 1 '{screenshot_path}' -loglevel error"

        try:
            subprocess.run(command, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            logger.info(f"第{i}张图片截图成功: {screenshot_path}")
            image_paths.append(screenshot_path)  # 添加路径到列表

        except subprocess.CalledProcessError:
            logger.error(f"第{i}张图片截图失败")

    # 上传所有截图并获取链接
    pic_urls = upload_images_and_get_links(image_paths)
    logger.info(f'获取bbcode代码:\n{pic_urls}')
    return pic_urls

def upload_images_and_get_links(image_paths):
    pic_urls = []
    for i, image_path in enumerate(image_paths, start=1):
        upload_result = upload_to_chevereto(image_path, i)
        if upload_result:
            pic_urls.append(upload_result)
    return '\n'.join(pic_urls)

# 示例调用
#file_path = '/Users/Ethan/Desktop/media/超级飞侠.Super.Wings.S10.2021.4K.WEB-DL.HEVC.AAC-CHDWEB/超级飞侠.Super.Wings.S10E01.2021.4K.WEB-DL.HEVC.AAC-CHDWEB.mp4'  # 视频文件路径
#folder_path = '/Users/Ethan/Desktop/media'  # 输出目录
#pic_num = 3  # 截图数量
#screenshot_from_video(file_path, folder_path, pic_num)
