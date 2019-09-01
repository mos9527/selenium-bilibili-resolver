'''
@Author: greats3an
@Date: 2019-08-26 21:29:24
@LastEditors: greats3an
@LastEditTime: 2019-08-31 20:16:16
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
print("\033[5mDUMPED!ASSETS COPIED TO YOUR CLIPBOARD.\033[0m\n")
clipboard.copy(cookies)
