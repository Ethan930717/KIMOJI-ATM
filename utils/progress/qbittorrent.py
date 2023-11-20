import qbittorrentapi
import requests
from utils.progress.config_loader import load_config
import logging
import time
import sys
import os
logger = logging.getLogger(__name__)

def download_torrent_file(torrent_url, save_path):
    try:
        response = requests.get(torrent_url)
        response.raise_for_status()
        with open(save_path, 'wb') as f:
            f.write(response.content)
        return True
    except Exception as e:
        logger.error(f"下载种子文件失败: {e}")
        return False

def add_torrent_to_qbittorrent(torrent_url, config_url, torrent_save_path, skip_checking=True, max_retries=3):
    # 配置文件路径
    config_url = os.path.join(config_url, 'config.yaml')
    config = load_config(config_url)

    # 下载种子文件
    if not download_torrent_file(torrent_url, torrent_save_path):
        logger.error("无法下载种子文件")
        sys.exit(1)

    # 初始化 qBittorrent 客户端
    qbt_client = qbittorrentapi.Client(
        host=config['qbittorrent']['url'],
        port=config['qbittorrent']['port'],
        username=config['qbittorrent']['username'],
        password=config['qbittorrent']['password']
    )

    try:
        # 登录
        qbt_client.auth_log_in()
    except Exception as e:
        logger.error(f"登录失败: {e}")
        return

    retries = 0
    while retries < max_retries:
        try:
            # 通过文件上传种子
            with open(torrent_save_path, 'rb') as f:
                qbt_client.torrents_add(
                    torrent_files=[f],
                    category='KIMOJI',
                    skip_checking=skip_checking
                )
            logger.info("种子添加成功,已为当前资源添加已发标记,小K收工啦")
            sys.exit(0)
        except Exception as e:
            retries += 1
            logger.warning(f"添加种子时发生错误: {e}")
            if retries >= max_retries:
                logger.error("达到最大重试次数，停止尝试，请手动添加种子,当前资源添加已发标记")
                sys.exit(1)
            logger.warning(f"正在尝试第 {retries} 次重试")
            time.sleep(5)  # 等待 5 秒后重试
