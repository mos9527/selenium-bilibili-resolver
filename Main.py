'''
@Description: Main program which does main things.RUN THIS!
@Author: greats3an
@Date: 2019-08-24 17:54:27
@LastEditTime: 2019-09-01 10:38:56
@LastEditors: greats3an
@Notes: The files were downloaded to ./bilibili/ by default
'''

import json
import os
import re
import signal
import threading
import time

import lxml
from bs4 import BeautifulSoup, SoupStrainer
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import BiliResolver
import CLISheet
import DriverLocater
import Logger
import QueuedDownloader

# region SETTINGS
# 用DeliciousCookie.py取得该cookie
cookies = []# 下载路径，用@local替代程序路径
download_path = "@local/bilibili/"
# 最大同时下载数
max_downloads = 8
# 下载分块大小
chunk_size = 10 * 1024  #分10KB一块
# 所有要解析的视频id e.g.['av######','av######']
vids = []
#下载的视频是否在单独的文件夹内（分P请启用）
in_folder = True
# endregion

# region UTILITY & CALLBACK
def callback(arg):
    # 下载端汇报下载情况
    for message in arg:
        if not message == None:
            downloader_sheet.modify_line(
                message["id"],
                ("STAT", QueuedDownloader.QDStatus(
                ).translate(message["stat"])),
                ("URL", message["url"]),
                ("PATH", message["path"]),
                ("SIZE", QueuedDownloader.QDUtils().HRS(message["length"])),
                ("CURR", QueuedDownloader.QDUtils().HRS(message["curr"])),
                ("%", round(message["curr"] / (message["length"]
                                               if not message["length"] == 0 else message["length"]) * 100, 1)),
                ("MESSAGE", message["extra"])
            )
    logger.clear(bufferindex=0)
    logger.log(downloader_sheet.get_output(), bufferindex=0)
    # 表格输出，输出至缓冲区0
    pass


def get_download_path(url, vid, affix):
    if(url == None):
        return None
    file_ext = None
    if(".m4s" in url):
        file_ext = ".m4s"
    if(".flv" in url):
        file_ext = ".flv"
    if(".mp4" in url):
        file_ext = ".mp4"
    affix = affix.replace("/", "_").replace("\\", "_")
    file_name = str(vid) + "_" + affix + file_ext
    if not in_folder:
        file_path = download_path.replace("@local", os.getcwd()) + file_name
    else:
        file_path = download_path.replace("@local", os.getcwd()) + "/" + str(vid) + "_" + affix[:len(affix)-6]  + "/" +  file_name
    return file_path


def resolve_and_download(driver, vid, cookies):
    bili_header = {
        "User-Agent": r"Mozilla/5.9 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
        "Origin": r"https://www.bilibili.com",
        "Referer": r"https://www.bilibili.com/video/av" + str(vid),
    }
    result = BiliResolver.resolve(driver, vid, cookies, log)
    if(result == None):
        log("Resolve failed!")
        return
    log("\033[33mData Resolved!\033[0m")
    for video in result:
        # 调遣下载任务
        path_video = get_download_path(
            video.video_url, vid, video.title + "_video")
        path_audio = get_download_path(
            video.audio_url, vid, video.title + "_audio")

        if not video.video_url == None:
            qd.queue_download(video.video_url, path_video, headers=bili_header)
        if not video.audio_url == None:
            qd.queue_download(video.audio_url, path_audio, headers=bili_header)

        info_sheet = CLISheet.CreateSheet(
            ("TITLE", 10), ("PLAYS", 8), ("DANMAKUS", 8), ("DESC", 20))
        info_sheet.add_line(("TITLE", video.title), ("PLAYS", video.plays),
                            ("DANMAKUS", video.danmakus), ("DESC", video.description))
        log(info_sheet.get_output())
# endregion

# region INIT
logger = Logger.Logger(((24, "Download Chart"), (24, "Debug Output")))
log = lambda *x: logger.log(*x, bufferindex=1)
# 调试输出，输出至缓冲区1
downloader_sheet = CLISheet.CreateSheet(("ID", 3), ("STAT", 5), ("URL", 10), (
    "PATH", 10), ("SIZE", 10), ("CURR", 10), ("%", 5), ("MESSAGE", 20), filler=' ')
for i in range(1, max_downloads + 1):
    downloader_sheet.add_line(("ID", i))
# 初始化下载调试表
# endregion

# region SELENIUM & DOWNLOADER
# 初始化webdriver,QueuedDownloader
driver_path = DriverLocater.getDriver()
# chromedriver 路径
opts = Options()
opts.add_argument("headless")
opts.add_argument("log-level=3")
# 无头模式，禁用日志
driver = webdriver.Chrome(executable_path=driver_path, options=opts)
driver.get("https://www.bilibili.com")
# QueuedDownloader
qd = QueuedDownloader.QueuedDownloader(
    callback=callback, max_thread=max_downloads, chunk_size=chunk_size)
# endregion

if __name__ == "__main__":
    log("\033[5m【Automatic Resolvant】", "In", len(vids), "Videos\033[0m")
    time.sleep(3)
    os.system("clear")
    for index in range(0, len(vids)):
        vid = vids[index]
        availablity = qd.get_availability()
        log("Avaiable threads:", availablity[0],
            "Tasks in queue", availablity[1])
        if(availablity[0] < 2 or availablity[1] > 0):
            log("\033[31mDownloader is BUSY,Waiting...\033[0m")
        while(availablity[0] < 2 or availablity[1] > 0):
            availablity = qd.get_availability()
            time.sleep(1)
        # 等待下载端资源充裕

        log("Resolving...", vid)
        resolve_and_download(driver, vid, cookies)
        log("Queued Download", index + 1, "/", len(vids))
        time.sleep(1)

    while True:
        availablity = qd.get_availability()
        log("Avaiable threads:",
            availablity[0], ".Remaining Tasks in queue", availablity[1])
        if(availablity[0] == max_downloads and availablity[1] == 0):
            break
        time.sleep(1)
    log("\033[0m\033[5m Download completed!")
    # 主线程任务完成
    driver.quit()
