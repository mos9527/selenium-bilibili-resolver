'''
@Author: greats3an
@Date: 2019-08-30 07:11:34
@LastEditors: greats3an
@LastEditTime: 2019-08-31 20:22:26
@Description: Using Seleium & BeautifulSoup to resolve the webpage with mutilple methods in order to get the actual download link
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

import CLISheet
import QueuedDownloader


'''
@description: Video struct,contains infomation and downloadable link to the video
@param -what-you-see-is-what-you-need-
@return: None
'''
class Video:
    def __init__(self,video_url='None',audio_url='None',title='None',description='None',plays=0,damamkus=0):
        self.video_url = video_url
        self.audio_url = audio_url
        self.title = title
        self.description = description
        self.plays = plays
        self.danmakus = damamkus
'''
@description: Utilty needed to resolve a video
@param ...
@return: ...
'''
class Utils:
    '''
    @description: Insertion sort which can be applied to both list object & dict() object
    @param array-like object,key (if used with a dictionary) 
    @return: Sorted array-like object
    '''
    def insertion_sort(self, arr, key=None):
        for i in range(0, len(arr) - 1):
            i = i
            for j in range(0, len(arr) - 1):
                # 插入排序：时间复杂度(n-1)^2.空间复杂度n
                if(key == None):
                    if arr[j] > arr[j+1]:
                        # 一项比下一项大
                        prev = arr[j]
                        arr[j] = arr[j+1]
                        arr[j+1] = prev
                        # 交换位置
                else:
                    if arr[j][key] > arr[j+1][key]:
                        # 一项比下一项大
                        prev = arr[j]
                        arr[j] = arr[j+1]
                        arr[j+1] = prev
                        # 交换位置

        return arr
    '''
    @description: Resloves video from JSON object
    @param JSON object,Logging function
    @return: Best-possible download-link to the video (or audio,or both)
    '''
    def resolve_videolink(self, data,log=lambda *x:print(*x)):
        def resolve_1(data):
            # 方法一（新）视频音视频分离
            video = {"link_vid": "", "link_aud": ""}
            audio_list = data["data"]["dash"]["audio"]
            video_list = data["data"]["dash"]["video"]
            video["link_aud"] = self.get_best_by_key(
                audio_list, "bandwidth")["base_url"]
            video["link_vid"] = self.get_best_by_key(
                video_list, "bandwidth")["base_url"]
            return video

        def resolve_2(data):
            # 方法二（旧）视频存储在一个.flv/.mp4里
            video = {"link_vid": "", "link_aud": ""}
            video["link_aud"] = None
            video_list = data["data"]["durl"]
            video["link_vid"] = self.get_best_by_key(video_list, "size")["url"]
            return video
        methods = [resolve_1, resolve_2]
        # 闭包数组，模块化处理链
        video = {"link_vid": "", "link_aud": ""}
        for method in methods:
            try:
                video = method(data)
                return video
            except Exception as err:
                log("ERROR: \033[31m",err,"\033[0m",method, "Failed to resolve link!")
                video = {"link_vid": "", "link_aud": ""}
    '''
    @description: Gets the value of a key in a dictionary which is larger than any other values
    @param Dictionary,Key
    @return: the largest value
    '''
    def get_best_by_key(self, data, key):
        return Utils().insertion_sort(data, key)[-1]
util = Utils()
'''
@description: Loads a bilibili videopage.Once loaded,returns its socure code
@param URL to the page
@return: It's soruce code
'''
def load_page(driver,url,cookies,log=lambda *x:print(*x)):
    for cookie in cookies:
        driver.add_cookie({
            'domain': cookie["domain"],
            'name': cookie["name"],
            'value': cookie["value"],
            'path': '/',
            'expires': None
        })
    #载入cookies
    driver.get(url)
    try:
        WebDriverWait(driver, 100).until(
            EC.presence_of_element_located((By.CLASS_NAME, "bb-comment "))
        )
        #bilibili视频，凡能够播放，评论div定会加载
    except Exception:
        log("\033[41mLoad Failed!\033[0m")
        return None
    return driver.page_source
'''
@description: Resolves a webpage,gets video infomation then returns
@param HTML Data
@return: VideoObject found in that page
'''
def resolve_page(soup,log=lambda *x:print(*x)):

    result = Video()
    try:
        result.title = soup.find("h1", "video-title").text  # 标题
        result.description = soup.find("div", id="v_desc").text  # 说明
    except Exception:
        log("\033[33mTitle / Description cannot be found!Using page title")
        result.title = soup.title.text
    try:
        playcount_pattern = re.compile(r"(?<=总播放数)\d*(?=\")")
        dm_pattern = re.compile(r"(?<=历史累计弹幕数)\d*(?=\")")
        video_info = str(soup.find_all("div", "video-data")[-1])
        result.danmakus = dm_pattern.findall(video_info)[-1]  # 弹幕数
        result.plays = playcount_pattern.findall(video_info)[-1]  # 播放量
    except Exception:
        log("\033[33mPlaycount / Danmakus cannot be found!Video may be /Bangumi/.\033[3m")
    #解析网页获取视频播放信息
    def resolve_1():
        video_script = None
        for script in soup.find_all("script"):            
            if "window.__playinfo__" in script.text:
                video_script = script.text
                video_script = video_script.replace("window.__playinfo__=", "")
                video_json = json.loads(video_script)
                # 使用beautifulsoup解析html,得出播放json
                video = util.resolve_videolink(video_json)
                return video
        raise Exception

    def resolve_2():
        video_src = soup.find_all("video")[-1]["src"]
        return {"link_vid": video_src, "link_aud": None}
    methods = [resolve_1, resolve_2]
    for method in methods:
        try:
            avInfo = method()
            result.video_url = avInfo["link_vid"]
            result.audio_url = avInfo["link_aud"]
            break
        except Exception as err:
            log("ERROR: \033[31m",err,"\033[0mMethod", method, "Failed to resolve Webpage!")
    #bilibili的老视频不用JSON储存，故用两种解析方式
    log("\033[0m\033[43mPage Resolved!\033[0m")
    return result
'''
@description: Core part.Where resloving begins!
@param Webdriver,Video ID(av######,ep#######),Logging method
@return: Resolved videolink
'''
def resolve(driver,vid, cookies,log=lambda *x:print(*x)):
    videos = []

    real_url = "https://www.bilibili.com/video/" + \
        str(vid) if "av" in str(
            vid) else "https://www.bilibili.com/bangumi/play/" + str(vid)
    # 一般视频链接与番剧，纪录片链接不同
    log("\033[43mFecthing soucre...Please wait...\033[0m")
    src = load_page(driver,real_url,cookies,log)
    if src==None:return None
    log("\033[32mPage Downloaded.Length is",
          QueuedDownloader.QDUtils().HRS(len(bytes(src, 'utf-8'))))
    #下载网页源代码
    soup = BeautifulSoup(src, features="lxml")
    # 使用bs4对象化网页内容
    log("Page loaded!")
    try:
        driver.find_element(By.ID,"multi_page")
        #不出现Exception则视频分p
        log("Video provided is in multiple episodes!")
        list_box = soup.find("ul","list-box")
        for child in list_box.children:
            #遍历所有子项
            title = child.a.get("title")
            url = "https://www.bilibili.com" + child.a.get("href")
            #子项指向的链接 e.g./video/av######/?p=n,载入后代入
            log("\033[35mResolving video",title,"\033[0m")
            soup_vid = BeautifulSoup(load_page(driver,url,cookies,log),features="lxml")
            video = resolve_page(soup_vid,log)
            video.title = title
            videos.append(video)
        return videos
    except Exception:
        log("Video is in form of signle part.")
        return [resolve_page(soup,log)]
