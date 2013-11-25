# -*- coding: utf8 -*-

import ConfigParser
import sys

Server = "192.168.26.40"
Username = "fanzhenjun"
Passwd = "111111"
ProjectRoot = "D:\\Project" #本地项目目录
RemoteRoot =  "/home/fanzhenjun/Project/" #远程LINUX项目目录
ProjectName = "LevelDb" #项目名称
SyncFileExt = ["cpp" ,  "h" ,  "txt" ,"c", "xml"] #需要同步的文件扩展名
MeteData = ProjectName #记录上一次文件修改时间的元文件
CMakeListFileName = "CMakeLists.txt"
ShellCMD="cd /home/fanzhenjun/Project/? ;" #上传完成后执行的命令


def ReadCfg(cfgFilePath):
    config=ConfigParser.ConfigParser()
    config.read(cfgFilePath)
    Server = config.get("global","Server")
    Username = config.get("global","Username")
    Passwd = config.get("global","Passwd")
    ProjectRoot = config.get("global","ProjectRoot")
    ProjectName = config.get("global","ProjectName")
    ext = config.get("global","SyncFileExt")
    SyncFileExt = ext.split(',')
    MeteData = ProjectName;
    CMakeListFileName = config.get("global","CMakeListFileName")
    ShellCMD = config.get("global","ShellCMD")
    ShellCMD += " ;"

if __name__ == '__main__':    
    ReadCfg("config.ini")
