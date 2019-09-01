'''
@Author: greats3an
@Date: 2019-08-30 07:27:11
@LastEditors: greats3an
@LastEditTime: 2019-09-01 07:18:54
@Description: Classic screen-buffer based logging system
'''

import os
import platform
import threading
import time


class Logger():

    '''
    @description: Inits self with arguments given
    @param buffer_lines -> tuplet((LINE-MAX-COLUMNS,"LINE-DESCRIPTION"),...),Description format (replaces @desc with description given)
    @return: None
    '''
    def __init__(self,buffer_lines=((32,"default"),),desc_format="@desc==================================="):
        self.max_lines = [i[0] for i in buffer_lines]
        self.buffer_desc = [i[1] for i in buffer_lines]
        self.log_buffers = [[] for i in range(0,len(buffer_lines))]
        self.desc_format = desc_format
        self.logger_lock = threading.Lock()
        super(Logger,self).__init__()
        #self.run()
    '''
    @description: Clears shell in every os available (POSIX / WINDOWS)
    @param None
    @return: None
    '''
    def cls(self):
        if "Windows" in platform.system():
            os.system("cls")
        else:
            os.system("clear")
    '''
    @description: Clears a certain line in the buffers
    @param Line INDEX
    @return: None
    '''
    def clear(self,bufferindex):
        #Aquire a lock,then appends the data to avoid conflition
        with self.logger_lock:
            self.log_buffers[bufferindex] = []
    '''
    @description: Fits the log string into the buffer,and then print out the buffers
    @param Log string,bufferindex
    @return: None
    '''
    def log(self,*args,bufferindex):
        #Aquire a lock,then appends the data to avoid conflition
        with self.logger_lock:
            str_log = ''
            for arg in args:str_log += str(arg) + ' '
            str_log = str_log[:len(str_log)-1] + '\n'
            logs = str_log.split('\n')
            if len(self.log_buffers[bufferindex]) + len(logs) >= self.max_lines[bufferindex]:
                self.log_buffers[bufferindex] = self.log_buffers[bufferindex][len(self.log_buffers[bufferindex]) + len(logs) - self.max_lines[bufferindex]:len(self.log_buffers[bufferindex])]
                self.log_buffers[bufferindex]+=logs
            else:
                self.log_buffers[bufferindex]+=logs
            pass
            self.dolog()
    '''
    @description: Logs data onto screen with config given
    @param None
    @return: Ask stdout
    '''
    def dolog(self):
        self.cls()
        for i in range(0,len(self.log_buffers)):
            desc = self.desc_format.replace("@desc",self.buffer_desc[i])
            max_line = self.max_lines[i]
            print(desc)
            print(*self.log_buffers[i],sep='\n')
            print('\n' * (max_line - len(self.log_buffers[i])) ,end='')
