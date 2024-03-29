<!--
 * @Author: greats3an
 * @Date: 2019-09-01 10:50:49
 * @LastEditors: greats3an
 * @LastEditTime: 2019-09-01 10:52:40
 * @Description: file content
 -->
# selenium-bilibili-resolver
基于BeautifulSoup和Selenium的b站(bilibili.com)视频解析工具

## 依赖
***Chrome 浏览器 (76)***

    BeautifulSoup(bs4)

    lxml

    selenium

    requests

    mitmproxy   *可选*

    clipboard   *可选*

运行 'pip3 install -r Dependencies.txt' 安装上述依赖

*本git带 Windows/Linux/macOS 的 chromedriver 76*


## 设定
### 编辑Main.py开头部分SETTINGS内变量，可编辑的有:
    cookies 用 DeliciousCookie.py 获得Cookies后粘贴至此 (可选：视频清晰度会受影响)

    download_path 下载目录，用 @local 代替程序运行目录
    
    max_downloads 最大同时下载数

    chunk_size 下载区块大小

    vids 所有要解析的视频ID,格式如['av12345','ep12345']

    in_folder 是否将视频存放在单独的文件夹内（分P推荐打开)


## 注意
    b站现将新视频音视频分离，下载后，推荐运行 *Merging/av_merge_folder.py (in_folder 为 True） 或 av_merge_nofolder.py* 合并 
    
    番剧类(ss12345)(cv12345)不能解析。番剧可用 *Videolisting/web_cathcer.py* 手动获取视频(e.g.ep12345)ID后输入*Main.py*

---
## 截图
![image](https://github.com/greats3an/selenium-bilibili-resolver/blob/master/Screenshots/Screenshot_1.png)
![image](https://github.com/greats3an/selenium-bilibili-resolver/blob/master/Screenshots/Screenshot_2.png)
![image](https://github.com/greats3an/selenium-bilibili-resolver/blob/master/Screenshots/Screenshot_3.png)
![image](https://github.com/greats3an/selenium-bilibili-resolver/blob/master/Screenshots/Screenshot_4.png)
