'''
@Author: greats3an
@Date: 2019-08-25 07:57:37
@LastEditors: greats3an
@LastEditTime: 2019-09-01 10:32:33
@Description: file content
'''
'''Deprecated!'''
import os

path = r"@local/bilibili/"
#path to bilidownloader (e.g:/root/桌面/mitm/bili_mim/bilibili/ @local/bilibili)
#use @local to repensent parent directory
avlist = []


path = path.replace("@local", os.getcwd())

for folder in os.listdir(path):
    #遍历在该目录第一级下所有的文件/文件夹
    if not os.path.isfile(folder):
        print("Folder",folder)
        if("av" or "ep" in folder):
            video = None
            audio = None
            for file in os.listdir(path + folder):
                
                if "video" in file:
                    video = file
                    print("Video:",file)
                if "audio" in file:
                    audio = file
                    print("Audio",file)
            video = path + folder + "/" + video if not video == None else None
            audio = path + folder + "/" + audio if not audio == None else None
                                                #Lazy-rule of Python
            avlist.append({"video": video, "audio": audio})
            print('\n'*3)
for av in avlist:
    out_file = av["video"][:len(av["video"]) - 4] + ".mp4"
       

    if(av["audio"]) == None:
        #旧视频，单个文件
        cmd = ("ffmpeg -y -i \"" + av["video"]+"\" -c:v copy -c:a copy \""+out_file+"\"")
        print("Executing:\n    ", cmd)
        #input("Press any key to proceed.")
        os.system(cmd)
        pass
    else:
        #新视频，多个文件
        cmd = ("ffmpeg -y -i \""+av["video"]+"\" -i \"" +
               av["audio"]+"\" -c:v copy -c:a copy \""+out_file+"\"")
        print("Executing:\n    ", cmd)
        #input("Press any key to proceed.")
        os.system(cmd)
        pass

print("\n\nOperation Complete.")
