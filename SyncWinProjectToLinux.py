# -*- coding: utf8 -*-

import os
import sys
import Config
import paramiko
from SshManager import FileLastModifyTime 
############
############
############
def WinDir2LinuxDir(winFilePath ,  winDirPath):
    (filepath,filename)=os.path.split(winFilePath)
    str = Config.RemoteRoot
    relativePath = winFilePath.replace(winDirPath ,  "")
    linuxrelativePath  = relativePath.replace("\\" ,  "/")
    str += Config.ProjectName
    str += linuxrelativePath
    return str

def SSHFileSync(FtpClient):
    entry = FileLastModifyTime.ReadFilesTime(Config.MeteData)
    szDir = Config.ProjectRoot + "\\" + Config.ProjectName
    fileNames = FileLastModifyTime.FindExtInDir(szDir ,  Config.SyncFileExt)
    fileModifyTimeMap = FileLastModifyTime.FilesLastModifyTime(fileNames)
    CmakeFileName = ""
    
    for file in fileModifyTimeMap:
        szPath = WinDir2LinuxDir(file ,  szDir)
       
        if file in entry:#上传修改过的文件
            if fileModifyTimeMap[file] > entry[file]:
                print "Modify:"  ,  file ,  szPath
                FtpClient.put(file ,  szPath)
                if file.find(Config.CMakeListFileName) != -1:
                    CmakeFileName = Config.CMakeListFileName
        else:#上传新增加的文件
            print "Upload New:" ,  file ,  szPath
            FtpClient.put(file ,  szPath)
            CmakeFileName =  Config.CMakeListFileName
                 
    for file in entry:#删除的文件
        szPath = WinDir2LinuxDir(file ,  szDir)
        if file not in fileModifyTimeMap:
            print "Delete:" ,  file ,  szPath
            FtpClient.remove(szPath)
            CmakeFileName =  Config.CMakeListFileName
        
    FileLastModifyTime.WriteFilesTime(Config.MeteData ,  fileModifyTimeMap)
    return CmakeFileName

def ChangeDir():
    exePath = os.path.split( os.path.realpath( sys.argv[0] ) )[0]
    os.chdir(exePath)

def main():
    if len(sys.argv) < 2:
        print "Useage:Commond [ProjectName=?] \n If no project name ,will use default project name in config file!"
    
    ChangeDir()
    Config.ReadCfg("config.ini")
    if len(sys.argv) == 2:
        Config.ProjectName = sys.argv[1]
        Config.MeteData = sys.argv[1]
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(Config.Server ,  username = Config.Username,  password = Config.Passwd)
    FtpClient = ssh.open_sftp()
    Cmake =  SSHFileSync(FtpClient)
    szShellCmd = Config.ShellCMD.replace("?" ,  Config.ProjectName)
    if Cmake == Config.CMakeListFileName:
        szShellCmd += "cmake .;make clean;make"
    else:
        szShellCmd +="make"
    print "Shell Command:" ,  szShellCmd    
    
    stdin ,  stdout ,  stderr = ssh.exec_command(szShellCmd)
    strlist = stdout.readlines()
    print "STDOUT:"
    for str in strlist:
        print str.decode("gbk")
    
    print "STDERR:"
    strErrlist = stderr.readlines(szShellCmd)
    for str1 in strErrlist:
        print str1

if __name__ == '__main__':
    main()
