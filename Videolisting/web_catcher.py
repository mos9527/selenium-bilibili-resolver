'''
@Author: greats3an
@Date: 2019-08-28 14:59:21
@LastEditors: greats3an
@LastEditTime: 2019-08-30 16:37:11
@Description: Updates an array filled with video-ids(av) when the url is updated
'''
from selenium import webdriver
import clisheet
import clipboard
import json
import time

driver = webdriver.Chrome()

driver.get("http://www.bilibili.com")

prev_url = None
urls = []
while True:
    if not driver.current_url == prev_url:
        prev_url = driver.current_url
        if 'av' in prev_url or 'ep' in prev_url:
            urls.append(prev_url.split("/")[-1])
    print(urls)
    time.sleep(0.5)