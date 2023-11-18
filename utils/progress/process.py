from utils.info.tmdb_id import search_tmdb
from utils.info.imdb_id import search_imdb
from utils.info.additional_ids import get_additional_ids,search_ids_from_imdb
from utils.progress.config_loader import find_media_folder
from utils.torrent.mktorrent import create_torrent
from utils.info.title import extract_title_info
from utils.info.tvdb_id import search_tvdb
from utils.tools.mediainfo import save_mediainfo_to_file
from utils.tools.bdinfo import generate_and_parse_bdinfo
from utils.tools import ffmpeg
import os
import sys
import logging
logger = logging.getLogger(__name__)

#寻找同名种子
def check_existing_torrent(torrent_dir, file_name):
    torrent_name = file_name + ".torrent"
    torrent_path = os.path.join(torrent_dir, torrent_name)
    if os.path.exists(torrent_path):
        return torrent_path  # 返回找到的种子文件路径
    return None  # 如果没有找到文件，则返回 None

#制作种子
def create_torrent_if_needed(file_dir, torrent_dir):
    file_name, action = find_media_folder(file_dir)
    if file_name:
        folder_path = os.path.join(file_dir, file_name)
        chinese_title, english_title, year, season, media, codec, audiocodec, maker = extract_title_info(file_name)
        tmdb_id, imdb_id, mal_id, tvdb_id = handle_media(chinese_title, english_title, year, season, media, maker)

        existing_torrent_path = check_existing_torrent(torrent_dir, file_name)
        if not existing_torrent_path:
            logger.warning(f"未找到同名种子，开始制作种子")
            create_torrent(folder_path, file_name, torrent_dir)
            torrent_path = os.path.join(torrent_dir, f"{file_name}.torrent")
            logger.info(f"种子文件已创建: {torrent_path}")
            return torrent_path, chinese_title, english_title, year, season, media, codec, audiocodec, maker, tmdb_id, imdb_id, mal_id, tvdb_id
        else:
            logger.info(f"找到同名种子：{existing_torrent_path}，跳过制种")
            return existing_torrent_path, chinese_title, english_title, year, season, media, codec, audiocodec, maker, tmdb_id, imdb_id, mal_id, tvdb_id
    else:
        logger.warning("没有找到合适的媒体文件夹")
        return None, None, None, None, None, None, None, None, None, None, None, None, None


#mediainfo/bdinfo解析
def process_media_directory(file_dir,pic_num,chinese_title, english_title, year, season, media, codec, audiocodec, maker):
    file_name, action = find_media_folder(file_dir)
    if file_name:
        folder_path = os.path.join(file_dir, file_name)
        logger.info(f'当前文件目录:{folder_path}')
         # 根据视频文件类型执行相应操作
        if action == "mediainfo":
            mediainfo_output_path = os.path.join(folder_path, "mediainfo.txt")
            media_info = save_mediainfo_to_file(folder_path, mediainfo_output_path)
            resolution, video_format, audio_format ,largest_video_file = save_mediainfo_to_file(folder_path, mediainfo_output_path)
            print(f"Mediainfo: \n{media_info}")
            if resolution and video_format and audio_format:
                print(
                    f"分析结果: \n分辨率: {resolution}, 视频格式: {video_format}, 音频格式: {audio_format}")
                pic_urls = ffmpeg.take_screenshots(largest_video_file,folder_path,pic_num)
            else:
                logger.error("无法获取 Mediainfo 分析结果，请检查视频文件是否损坏")
                exit()
        elif action == "bdinfo":
            logger.info("检测到原盘，开始使用bdinfo解析")
            formatted_summary, resolution, type = generate_and_parse_bdinfo(folder_path)
            if formatted_summary:
                logger.info("BDInfo 分析完成")
                print("输出快扫信息:")
                print(formatted_summary)
                pic_urls = ''
                logger.info("由于您上传的是原盘资源，发种机无法截图，请您在种子上传后手动上传截图")
            else:
                logger.error("BDInfo 分析失败或未找到有效文件，请检查文件是否正常")
                exit()
        else:
            logger.error("无法找到可解析的影片")
            exit()

    else:
        logger.warning("没有找到合适的媒体文件夹")



def handle_media(chinese_title, english_title, year, season, media, maker):
    item_type, tmdb_id, media_type, chinese_name, child = search_tmdb(english_title)
    imdb_id, mal_id, tvdb_id = None, None, None
    if tmdb_id != 0:
        imdb_id, mal_id = get_additional_ids(tmdb_id, item_type, english_title)
        tvdb_id = search_tvdb(english_title) if english_title else 0
    else:
        imdb_search_id, media_type = search_imdb(english_title, media)
        if imdb_search_id:
            tmdb_id, imdb_id, mal_id = search_ids_from_imdb(imdb_search_id, english_title, media_type)
            tvdb_id = search_tvdb(english_title) if english_title else 0
    print(f'最终结果:\nmedia_type:{media_type}\ntmdb:{tmdb_id}\nimdb:{imdb_id}\nmal:{mal_id}\ntvdb:{tvdb_id}')
    return tmdb_id, imdb_id, mal_id, tvdb_id

def handle_found_media(tmdb_id, item_type, media_type, chinese_title, english_title, child, year, season, maker):
    imdb_id, mal_id = get_additional_ids(tmdb_id, item_type, english_title)
    tvdb_id = search_tvdb(english_title) if english_title else 0
    logger.info(f'最终结果:\nmedia_type:{media_type}\ntmdb:{tmdb_id}\nimdb:{imdb_id}\nmal:{mal_id}\ntvdb:{tvdb_id}')


#chinese_title = "汪汪队"
#english_title="汪汪队"
#tmdb_id = "12225"
#year="2014"
#season= 1
#maker= "kimoji"
#handle_media(chinese_title, english_title, year, season, "series", maker)