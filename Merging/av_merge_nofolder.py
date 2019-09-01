'''
@Author: greats3an
@Date: 2019-08-28 15:09:12
@LastEditors: greats3an
@LastEditTime: 2019-08-31 20:34:04
@Description: file content
'''
import os

#适用于文件形式为 av########_视频标题_(video|audio).(flv|mp4|m4a) 且不分文件夹的下载项

path = r"@local/bilibili/"
#一般不需要修改

#path to bilidownloader (e.g:/root/桌面/mitm/bili_mim/bilibili/ @local/bilibili)
#use @local to repensent parent directory
avlist = {}
path = path.replace("@local", os.getcwd())

for file in os.listdir(path):
    #遍历在该目录第一级下所有的文件/文件夹
    if("av" in file or "ep" in file):
        name = os.path.basename(file)
        id = name.split("_")[0]
        if not id in avlist.keys():
            avlist[id] = {"video":None,"audio":None}            
        if("_video" in file):avlist[id]["video"] = file
        elif("_audio" in file):avlist[id]["audio"] = file

print(avlist)
for key in avlist.keys():
    av = avlist[key]
    print("through:",av)
    filename = av["video"]
    out_file = path + filename[:len(filename) - 10] + ".mp4"
    
    if(av["audio"]) == None:
        #旧视频，单个文件
        cmd = ("ffmpeg -y -i \"" + path + av["video"]+"\" -c:v copy -c:a copy \""+out_file+"\"")
        print("Executing:\n    ", cmd)
        input("Press any key to proceed.")
        os.system(cmd)
        pass
    elif not av["video"] == None:
        #新视频，多个文件
        cmd = ("ffmpeg -y -i \""+ path +av["video"]+"\" -i \"" + path +
               av["audio"]+"\" -c:v copy -c:a copy \""+out_file+"\"")
        print("Executing:\n    ", cmd)
        input("Press any key to proceed.")
        os.system(cmd)
        pass

print("\n\nOperation Complete.")
