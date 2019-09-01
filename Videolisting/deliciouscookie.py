'''
@Author: greats3an
@Date: 2019-08-26 21:29:24
@LastEditors: greats3an
@LastEditTime: 2019-09-01 10:50:13
@Description: Fecthes cookies via Selenium
'''

from selenium import webdriver
import clipboard
import json
driver = webdriver.Chrome()

driver.get("http://www.bilibili.com")

input("When done,press Enter to save cookies.")

cookies = driver.get_cookies()
cookies = json.dumps(cookies).replace("false", "False").replace("true", "True").replace("},","},\n")
print("\033[5mCookies 已复制到剪贴板.\033[0m\n")
clipboard.copy(cookies)
