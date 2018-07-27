#!/usr/bin/env python
# -*- coding: utf8 -*-

__author__ = 'van1988ch'

'''
主要用来同步本地的项目代码到支持ssh的远程目标主机上面,基于make,cmake编译项目
'''

import os
import sys
import paramiko
import ConfigParser
import platform

try:
    import cPickle as pickle
except ImportError:
    import pickle

reload(sys)

sys.setdefaultencoding('utf-8')

g_Config = {}
backslash = "/"
if platform.system() == "Windows":
    backslash = "\\";

def ReadCfg(cfgFilePath):
    '''加载配置文件
    '''
    config=ConfigParser.ConfigParser()
    config.read(cfgFilePath)
    g_Config["Server"] = config.get("global","Server")
    g_Config["ServerPort"] = int(config.get("global","ServerPort"))
    g_Config["Username"] = config.get("global","Username")
    g_Config["Passwd"] = config.get("global","Passwd")
    g_Config["ProjectRoot"] = config.get("global","ProjectRoot")
    g_Config["RemoteRoot"] = config.get("global","RemoteRoot")
    g_Config["ProjectName"] = config.get("global","ProjectName")
    g_Config["SyncFileExt"] = config.get("global","SyncFileExt")
    g_Config["MeteData"] = g_Config["ProjectName"]
    g_Config["CMakeListFileName"] = config.get("global","CMakeListFileName")
    g_Config["ShellCMD"] = config.get("global","ShellCMD")

def FindExtInDir(dirPath ,  exts):
    '''遍历整个目录,过滤.svn目录不同步
        记录所有的目录,如果项目初始化文件没有生成,则在远程重新生成一次目录
    '''
    splittags = exts.split(',')
    fileNames = {}
    dirs = []
    for dir  in os.walk(dirPath):
        if dir[0].find('{}/.svn'.format(g_Config["ProjectAbsolutePath"])) >= 0 or dir[0].find('{}/.git'.format(g_Config["ProjectAbsolutePath"]))>= 0:
            continue
        
        #所有的目录,为了初始化远程的目录做准备
        linuxdir = dir[0][len(g_Config["ProjectAbsolutePath"]+"/"):].replace(backslash , "/")
        if linuxdir:
            dirs.append('{}{}/{}'.format(g_Config["RemoteRoot"] , g_Config["ProjectName"] , linuxdir))

        #遍历所有文件,以及最新的更新时间
        for filename in dir[2]:
            sufix = os.path.splitext(filename)[1][1:]
            if sufix in splittags:
                fullFilePath = '{}{}{}'.format(dir[0] , backslash , filename)
                fileNames[fullFilePath] = os.stat(fullFilePath).st_mtime
                    
    return fileNames , dirs;

    
def WriteFilesTime(path , fileModifyTimeMap):
    '''将所有的同步过的文件记录一下时间,下次用来做增量同步
    '''
    with open ( path , 'wb' ) as file : 
        pickle.dump( fileModifyTimeMap , file )

def ReadFilesTime(path):
    '''读取所有的数据,用来做增量同步的时间比较
    '''
    try:
        with open ( path , 'rb' ) as file: 
            entry = pickle.load(file)
    except IOError:
        return {}
    else:
        return entry


def SourceSysDir2DestSysDir(winFilePath ,  winDirPath):
    '''生成远程系统的linux的路径
    '''
    (filepath,filename)=os.path.split(winFilePath)
    relativePath = winFilePath.replace(winDirPath ,  "")
    linuxrelativePath  = relativePath.replace(backslash , "/")
    return '{}{}{}'.format(g_Config["RemoteRoot"] , g_Config["ProjectName"] , linuxrelativePath)

def SSHFileSync(ssh , FtpClient):
    entry = ReadFilesTime(g_Config["pickle"])
    fileModifyTimeMap , dirs = FindExtInDir(g_Config["ProjectAbsolutePath"] ,  g_Config["SyncFileExt"])
    if len(entry) == 0 :
        for dir in dirs:
            command = "mkdir -p " + dir
            print command
            ssh.exec_command(command)

    CmakeFileName = ""
    
    for file in fileModifyTimeMap:
        szPath = SourceSysDir2DestSysDir(file ,  g_Config["ProjectAbsolutePath"])
       
        if file in entry:#上传修改过的文件
            if fileModifyTimeMap[file] > entry[file]:
                print "Modify:"  ,  file ,  szPath
                FtpClient.put(file ,  szPath)
                if file.find(g_Config["CMakeListFileName"]) != -1:
                    CmakeFileName = g_Config["CMakeListFileName"]
        else:#上传新加的文件
            print "Upload New:" ,  file ,  szPath
            try:
                FtpClient.put(file ,  szPath)
            except:
                print file ,  szPath
            CmakeFileName =  g_Config["CMakeListFileName"]
                 
    for file in entry:#删除的文件
        szPath = SourceSysDir2DestSysDir(file ,  g_Config["ProjectAbsolutePath"])
        if file not in fileModifyTimeMap:
            print "Delete:" ,  file ,  szPath
            try:
                FtpClient.remove(szPath)
            except IOError as removeerr:
                print "Delete failed:" , file , szPath
            CmakeFileName =  g_Config["CMakeListFileName"]
        
    WriteFilesTime(g_Config["pickle"] ,  fileModifyTimeMap)
    return CmakeFileName

def ChangeDir():
    '''修改程序执行目录,为了把序列号文件写入到那个目录和读配置文件的目录
    '''
    exePath = os.path.split( os.path.realpath( sys.argv[0] ) )[0]
    os.chdir(exePath)

def main():
    
    ChangeDir()
    try:
        ReadCfg(sys.argv[1])
    except:
        print "read config error."
        return
    
    dirpath = ""
    if len(sys.argv) > 3:
        dirpath = sys.argv[3]
    print dirpath
    g_Config["ProjectName"] = sys.argv[2]
    g_Config["MeteData"] = sys.argv[2]
    g_Config["pickle"] = sys.argv[1]+"_"+g_Config["MeteData"]
    g_Config["ProjectAbsolutePath"] = '{}/{}'.format(g_Config["ProjectRoot"], g_Config["ProjectName"])

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(g_Config["Server"] , g_Config["ServerPort"] , username = g_Config["Username"],  password = g_Config["Passwd"])
    FtpClient = ssh.open_sftp()
    ##try:
    Cmake =  SSHFileSync(ssh , FtpClient)
    ##except:
    ##    print "SSHFileSync Failed."
    ##    return

    szShellCmd = '{}{};{}'.format(g_Config["ShellCMD"].format(g_Config["ProjectName"]) , dirpath , "cmake .;make clean;make" if Cmake == g_Config["CMakeListFileName"] and Cmake=="CMakeLists.txt" else g_Config["CMakeListFileName"])

    print "Shell Command:" ,  szShellCmd 
    
    stdin ,  stdout ,  stderr = ssh.exec_command(szShellCmd)
    print "STDOUT:"
    strlist = stdout.read()
    print strlist.decode("utf8")
    
    print "STDERR:"
    strErrlist = stderr.read()
    print strErrlist.decode("utf8")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "Useage:Commond [config=?][ProjectName=?][dir=?] \n"
    elif sys.argv[1] == "rm":
        if len(sys.argv) < 4:
            print "Useage:Commond rm [config=?][ProjectName=?] \n"
        else:
            ChangeDir()
            path = './{}_{}'.format(sys.argv[2] , sys.argv[3])
            os.remove(path)
    else:
        main()
