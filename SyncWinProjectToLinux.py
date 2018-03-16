# -*- coding: utf8 -*-

import os
import sys
import paramiko
import ConfigParser
import pickle
import sys
reload(sys)

sys.setdefaultencoding('utf-8')

g_Config = {}
def ReadCfg(cfgFilePath):
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
    g_Config["ShellCMD"] += " ;"


def FilesLastModifyTime(fileNames):
    filesModifyTime = {}
    for file in fileNames:
        filesModifyTime[file] = os.stat(file).st_mtime
    return filesModifyTime

def FindExtInDir(dirPath ,  exts):
    list = exts.split(',')
    fileNames = []
    dirs = []
    for dir  in os.walk(dirPath):
        if dir[0].find(g_Config["ProjectRoot"]+"/"+g_Config["ProjectName"]+"/.svn") == -1:
            linuxdir = dir[0][len(g_Config["ProjectRoot"]+"/"+g_Config["ProjectName"]+"/"):].replace("/" ,  "/")
            if linuxdir != '':
                dirs.append(g_Config["RemoteRoot"]+g_Config["ProjectName"]+'/'+linuxdir)
            for filename in dir[2]:
                sufix = os.path.splitext(filename)[1][1:]
                for ext in list:
                    if ext == sufix :
                        fullFilePath = dir[0] + "/" + filename
                        fileNames.append(fullFilePath);
    return fileNames , dirs;

    
def WriteFilesTime(path , fileModifyTimeMap):
    with open ( path , 'wb' ) as file : 
        pickle.dump( fileModifyTimeMap , file )

def ReadFilesTime(path):
    try:
        with open ( path , 'rb' ) as file: 
            entry = pickle.load(file)
    except IOError:
        return []
    else:
        return entry


def WinDir2LinuxDir(winFilePath ,  winDirPath):
    (filepath,filename)=os.path.split(winFilePath)
    str = g_Config["RemoteRoot"]
    relativePath = winFilePath.replace(winDirPath ,  "")
    linuxrelativePath  = relativePath.replace("/" ,  "/")
    str += g_Config["ProjectName"]
    str += linuxrelativePath
    return str

def SSHFileSync(ssh , FtpClient):
    entry = ReadFilesTime(g_Config["configFileName"]+"_"+g_Config["MeteData"])
    szDir = g_Config["ProjectRoot"] + "/" + g_Config["ProjectName"]
    fileNames , dirs = FindExtInDir(szDir ,  g_Config["SyncFileExt"])
    fileModifyTimeMap = FilesLastModifyTime(fileNames) 
    if len(entry) == 0 :
        for dir in dirs:
            command = "mkdir -p " + dir
            print command
            ssh.exec_command(command)

    CmakeFileName = ""
    
    for file in fileModifyTimeMap:
        szPath = WinDir2LinuxDir(file ,  szDir)
       
        if file in entry:#涓婁紶淇敼杩囩殑鏂囦欢
            if fileModifyTimeMap[file] > entry[file]:
                print "Modify:"  ,  file ,  szPath
                FtpClient.put(file ,  szPath)
                if file.find(g_Config["CMakeListFileName"]) != -1:
                    CmakeFileName = g_Config["CMakeListFileName"]
        else:#涓婁紶鏂板鍔犵殑鏂囦欢
            print "Upload New:" ,  file ,  szPath
            try:
                FtpClient.put(file ,  szPath)
            except:
                print file ,  szPath
            CmakeFileName =  g_Config["CMakeListFileName"]
                 
    for file in entry:#鍒犻櫎鐨勬枃浠�
        szPath = WinDir2LinuxDir(file ,  szDir)
        if file not in fileModifyTimeMap:
            print "Delete:" ,  file ,  szPath
            FtpClient.remove(szPath)
            CmakeFileName =  g_Config["CMakeListFileName"]
        
    WriteFilesTime(g_Config["configFileName"]+"_"+g_Config["MeteData"] ,  fileModifyTimeMap)
    return CmakeFileName

def ChangeDir():
    exePath = os.path.split( os.path.realpath( sys.argv[0] ) )[0]
    os.chdir(exePath)

def main():
    if len(sys.argv) < 3:
        print "Useage:Commond [config=?][ProjectName=?] \n"
        return 
    
    ChangeDir()
    g_Config["configFileName"] = sys.argv[1]
    try:
        ReadCfg(g_Config["configFileName"])
    except:
        print "read config error."
        return
    
    g_Config["ProjectName"] = sys.argv[2]
    g_Config["MeteData"] = sys.argv[2]
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(g_Config["Server"] , g_Config["ServerPort"] , username = g_Config["Username"],  password = g_Config["Passwd"])
    FtpClient = ssh.open_sftp()
    ##try:
    Cmake =  SSHFileSync(ssh , FtpClient)
    ##except:
    ##    print "SSHFileSync Failed."
    ##    return
    szShellCmd = g_Config["ShellCMD"].replace("?" ,  g_Config["ProjectName"])
    if Cmake == g_Config["CMakeListFileName"]:
        szShellCmd += "cmake .;make clean;make"
    else:
        szShellCmd +="make"
    print "Shell Command:" ,  szShellCmd    
    
    stdin ,  stdout ,  stderr = ssh.exec_command(szShellCmd)
    strlist = stdout.readlines()
    print "STDOUT:"
    for str in strlist:
        print str.decode("gb2312")
    
    print "STDERR:"
    strErrlist = stderr.read()
    print strErrlist.decode("gb2312")

if __name__ == '__main__':
    main()
