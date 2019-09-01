'''
@Author: greats3an
@Date: 2019-08-24 18:48:46
@LastEditors: greats3an
@LastEditTime: 2019-08-31 20:06:06
@Description:Finds chromedriver for the OS
'''
import os
import platform


'''
@description: Gets chromedriver path
@param None
@return: chromedriver
'''
def getDriver():
    system = platform.system()
    if "Windows" in system:
    #Windows
        return os.getcwd() + r"\chromedriver\chromedriver.exe"
    elif "Darwin" in system:
    #macOS
        return os.getcwd() + r"/chromedriver/chromedriver.app"
    else:
    #Linux
        return os.getcwd() + r"/chromedriver/chromedriver.bin"
