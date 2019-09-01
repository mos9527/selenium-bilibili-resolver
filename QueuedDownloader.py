'''
@Author: greats3an
@Date: 2019-08-24 18:48:46
@LastEditors: greats3an
@LastEditTime: 2019-09-01 07:10:16
@Description: Mutil-threaded file downloader in pure python
'''

'''
message{} 消息体
message = {
    "id"                #下载线程的ID
    "stat"              #下载状态
    "headers"           #提供的Headers
    "overwrite"         #是否重写
    "url"               #下载链接
    "path"              #下载目录
    "length"            #文件长度
    "curr"              #已下载长度
    "extra"             #附加消息
}
'''

import os
import queue
import threading
import time
from pathlib import Path

import requests


'''
@description: Status-reporting class for emnurating stages of a downloading / downloaded file
@param None 
@return: None
'''
class QDStatus():
    STAT_INPROGRESS = 0
    STAT_OK = 1
    STAT_FILEERROR = 2
    STAT_OVERWRITEN = 3 
    STAT_REJECTED = 4
    STAT_UNKNOWN_ERR = 5
    '''
    @description: Translates Status-code into Human-Readable text
    @param code
    @return: Translated status-text
    '''
    def translate(self,code):return {self.STAT_INPROGRESS:"下载中",self.STAT_OK:"已完成",self.STAT_FILEERROR:"文件错误",self.STAT_OVERWRITEN:"已覆盖",self.STAT_REJECTED:"拒绝连接",self.STAT_UNKNOWN_ERR:"未知错误"}[code]

class QDUtils():
    '''
    @description: Translates filesize(in bytes) to a human readable format
    @param size
    @return: Translated filesize
    '''    
    def HRS(self,size):
        units=('B','KB','MB','GB','TB','PB')
        for i in range(len(units)-1,-1,-1):
            if size>=2*(1024**i):
                return str(round(size/(1024**i),2) )+' '+units[i]
    #获取可用的下载链接
    '''
    @description: Recursivly lable the filename to get a non-exsiting filepath
    @param filepath to the ideal file
    @return: Best filepath (non-exsisting)
    '''
    def get_download_path(self,file_path):
        #初始情况，文件不存在
        if(not os.path.exists(file_path)):
            return file_path
        else:
            #文件存在，进行标号
            file_root = os.path.split(file_path)[0]
            file_name_ext = os.path.basename(file_path)
            file_name = os.path.splitext(os.path.basename(file_name_ext))[0]
            file_ext = os.path.splitext(os.path.basename(file_name_ext))[1]
            if("_" in file_name):                 
                index = int(file_name.split("_")[-1]) + 1
                file_name = file_name.replace("_"+str(index - 1),"")
                return self.get_download_path(file_root + "/" + file_name + "_" + str(index) + file_ext)
            else:
                return self.get_download_path(file_root + "/" + file_name + "_1" + file_ext)
        
class QueuedDownloader(threading.Thread):

        #region MAIN
        '''
        @description: Inits threads,starts self to monitor download status
        @param callback Method,Max simultaneous download tasks,Download chunksize
        @return: None
        '''
        def __init__(self,callback=(lambda *x:print(*x,sep='\n')),max_thread=4,chunk_size=1024):
            self.max_thread = max_thread
            self.download_queue = queue.Queue()
            #填充线程池
            self.chunk_size = chunk_size
            self.callback = callback
            self.threads = [None for i in range(0,self.max_thread)]
            super(QueuedDownloader,self).__init__()
            self.start()
        '''
        @description: Monitor loop.Callbacks download stauts,Deleting dead threads.Dispatching download tasks in queue
        @param None
        @return: None
        '''
        def run(self):
            while True:
                #大循环逻辑:消费者/分解者拓扑
                if(not self.download_queue.empty() and None in self.threads):
                    #列表非空,下载池有空，对生产者进行消费
                    arg = self.download_queue.get()
                    #参数值
                    available_index = self.threads.index(None)
                    #寻出第一个空位，作为线程位置
                    dl_thread = threading.Thread(target=self.downloader,args=(available_index,))
                    #下载的线程，传参：id（个体在线程池中的位置）
                    dl_message = {
                        "id":available_index,
                        "stat":QDStatus.STAT_INPROGRESS,
                        "headers":arg["headers"],
                        "overwrite":arg["overwrite"],
                        "url":arg["url"],
                        "path":arg["path"],
                        "length":1,
                        "curr":0,
                        "extra":None}
                    #下载的附加参数，字典形式在Main thread间读写沟通
                    #具体参见message{}
                    self.threads[available_index] = {"thread":dl_thread,"message":dl_message}
                    #追加入列表
                    self.threads[available_index]["thread"].start()

                #一般情况———分解/监视任务：对已死亡（完成任务，出现Exception）的线程进行清理；对所有其他线程的状态进行汇报
                thread_stat = []
                for index in range(0,len(self.threads)):
                    if(self.threads[index] == None):
                        #空位，不动作
                        thread_stat.append(None)
                        pass
                    else:
                        #线程位，处理生存状态，进行状态汇报
                        message = self.threads[index]["message"]
                        thread_stat.append(message)                  
                        if(not self.threads[index]["thread"].is_alive()):
                            #线程死亡,清理工作
                            self.threads[index] = None

                self.callback(thread_stat)
                time.sleep(1)
        #endregion

        #region OPERATIONS
        '''
        @description: Gets how many available slots (None(s)) are there in the threads[]
        @param None
        @return: Number of None(s) in threads
        '''
        def get_availability(self):
            return [self.threads.count(None),self.download_queue.qsize()]

        '''
        @description: Queue a download task
        @param Download url,Download path,Do Overwriting,Custom headers
        @return: None
        '''
        def queue_download(self,url,path,overwrite=True,headers={"User-Agent":"Chrome/80.0.0000.000"}):
            self.download_queue.put({"overwrite":overwrite,"headers":headers,"url":url,"path":path})
            #加入下载队列
        #endregion 
        
        #region THREAD
        '''
        @description: Thread's workload.Downloads a file and updates download status
        @param Please refer to message{} description
        @return: None
        '''
        def downloader(self,arg):
            self_id = int(arg)
            chunk_size = self.chunk_size
            #线程自身id
            file_url = self.threads[self_id]["message"]["url"]
            file_path = self.threads[self_id]["message"]["path"]
            if(file_path == None or file_url == None):
                self.threads[self_id]["message"]["stat"] = QDStatus.STAT_FILEERROR
                self.threads[self_id]["message"]["extra"] = "Empty URL / Path!"
                return
            headers = self.threads[self_id]["message"]["headers"]
            do_overwrite = self.threads[self_id]["message"]["overwrite"]
            #下载链接，目录，信息头，是否重写
            dir_path = os.path.split(file_path)[0]
            try:
                os.makedirs(dir_path)
            except FileExistsError:
                pass  
            #补全路径
            file_path = file_path if do_overwrite else QDUtils().get_download_path(file_path)
            overwriten = os.path.exists(file_path)
            #递归法补全最佳文件名
            try:
                r = requests.get(file_url,headers=headers,stream=True)
                self.threads[self_id]["message"]["length"]  = int(r.headers['content-length'])
            except Exception as e:
                #其他情况
                self.threads[self_id]["message"]["stat"] = QDStatus.STAT_UNKNOWN_ERR
                self.threads[self_id]["message"]["extra"] = "Exception:" + str(e)
                return
            if not r.status_code == 200:
                    #服务器拒绝连接
                    self.threads[self_id]["message"]["stat"] = QDStatus.STAT_REJECTED
                    self.threads[self_id]["message"]["extra"] = "Rejected:" + str(r.status_code)
                    return 
            Path(file_path).touch()

            f = open(file_path,"wb")
            for chunk in r.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    self.threads[self_id]["message"]["curr"] += len(chunk)
                if self.threads[self_id]["message"]["curr"] >= self.threads[self_id]["message"]["length"]:break
            #流式下载内容
            f.flush()
            f.close()
            self.threads[self_id]["message"]["stat"] = QDStatus.STAT_OK if not overwriten else QDStatus.STAT_OVERWRITEN
            if overwriten:self.threads[self_id]["message"]["extra"] = "File Overwriten!"
            return
        #endregion
