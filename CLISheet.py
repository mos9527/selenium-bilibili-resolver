'''
@Author: greats3an
@Date: 2019-08-24 18:48:46
@LastEditors: greats3an
@LastEditTime: 2019-09-01 07:13:22
@Description: CLI(command-line-interface) based chart.Achieved with nothing but python itself
'''

import os
import unicodedata
class CreateSheet():
    '''
    @description: Converts halfwidth chars to full widths ones
    @param halfwidth 
    @return: 
    '''
    def half2full(self,s):
        if ord(s[0]) == 0:return s[:len(s) - 1]
        #prefix:不对开头为\0的字串反映且返回去除开头的结果
        offset = 65248
        s = s.replace(' ',chr(0x3000))
        for c in range(33,127):
            s = s.replace(chr(c),chr(c + offset))
        return s
    '''
    @description: Inits self with arguments given
    @param ContentTuplet() -> ("ROW NAME",ROW-WIDTH),...
    @return: None
    '''
    def __init__(self, *args, v_interper='\033[33m┃\033[0m', h_interper='\033[33m━━\033[0m', filler=' '):
        self.rows = [{"name": arg[0], "width":arg[1]} for arg in args]
        #传递设定（列头，列宽）
        self.v_interper = v_interper
        self.h_interper = h_interper
        self.filler = filler
        self.columns = []
    '''
    @description: Justify string to fit in certain length
    @param string to be justifed,length desired
    @return: Justifed string
    '''
    def jstr(self, string, length):
        string = str(string)
        if(len(string) <= length):
            return string.center(length, self.filler)
        #字串过长
        string = '>' + string[(len(string) - length) + 1:len(string)]
        return string
    '''
    @description: Modify a column's content
    @param ID of the column,ContentTuplet()->("PARAM NAME",VALUE),...
    @return: None
    '''
    def modify_line(self, pos, *args):
        widths = {}

        for row in self.rows:
            widths[row["name"]] = row["width"]

        for arg in args:
            if(arg[0] in self.columns[pos].keys()):
                width = widths[arg[0]]
                self.columns[pos][arg[0]] = self.jstr(str(arg[1]), width)
    '''
    @description: Add a new line
    @param ContentTuplet()->("PARAM NAME",VALUE),...
    @return: ID of the line
    '''
    def add_line(self, *args):

        new_column = {}
        widths = {}

        for row in self.rows:
            widths[row["name"]] = row["width"]
            new_column[row["name"]] = self.filler.center(
                widths[row["name"]], self.filler)

        for arg in args:
            if(arg[0] in new_column.keys()):
                width = widths[arg[0]]
                new_column[arg[0]] = self.jstr(str(arg[1]), width)

        self.columns.append(new_column)
        return len(self.columns) - 1
        #返回该行的位置
    '''
    @description: Deletes a line
    @param ID of the column 
    @return: None
    '''
    def remove_line(self, pos):
        self.columns[pos] = None
        #设该位置为空，仍保留表单位置连续性
    '''
    @description: Get a formated output in string
    @param None
    @return: Formated chart in string
    '''
    def get_output(self):
        width = 4
        for row in self.rows:
            width += row["width"]
        #最大宽度
        message = self.repeat(self.h_interper, width) + '\n' + self.v_interper
        for row in self.rows:
            message += self.half2full(row["name"].center(row["width"],
                                          self.filler)[:row["width"]]) + self.v_interper
        message += '\n' + self.repeat(self.h_interper, width) + '\n'
        #表头
        for column in self.columns:
            message += self.v_interper
            for row in self.rows:
                message += self.half2full(column[row["name"]]) + self.v_interper
            message += '\n' + self.repeat(self.h_interper, width) + '\n'
        #表内容
        return message
    '''
    @description: Repeats a character
    @param Character,Repeat-count
    @return: Repeated String
    '''
    def repeat(self, char, count):
        return char * count
