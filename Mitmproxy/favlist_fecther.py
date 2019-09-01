'''
@Author: greats3an
@Date: 2019-08-30 17:42:11
@LastEditors: greats3an
@LastEditTime: 2019-08-30 18:06:07
@Description: Interpes connection between a bilibili-client to the server when requesting a favlist of videos
@Printouts: Intercepted Video-IDs
'''
import mitmproxy
from mitmproxy import http,ctx
import json
import os
class HTTPInterper:
    def __init__(self):
        print("Interper ready to go.")

    def request(self, flow: mitmproxy.http.HTTPFlow):
        #请求事件        
        pass
    def http_connect(self, flow: mitmproxy.http.HTTPFlow):
        #连接事件
        pass
    
    def response(self, flow: mitmproxy.http.HTTPFlow):
        if("Access-Control-Allow-Origin" in flow.response.headers.keys() and flow.response.headers["Access-Control-Allow-Origin"] == r"https://space.bilibili.com"):
            flow_type = flow.response.headers["Content-Type"]
            flow_text = flow.response.get_text()
            if(flow_type==None or flow_text==None):return
            if("application/json" in flow_type and "medias" in flow_text):
                #拿到json
                data = json.loads(flow_text)
                vids = []
                for meida in data["data"]["medias"]:
                    vid = meida["id"]
                    title = meida["title"]
                    desc = meida["intro"]
                    misc = meida["cnt_info"]
                    print("av" + str(vid),title,desc,misc)
                    vids.append("av" + str(vid))
                print('\n' * 10,vids)

addons = [
    HTTPInterper()
]