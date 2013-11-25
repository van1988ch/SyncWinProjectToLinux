# -*- coding: utf8 -*-
import os
import pickle


def FindExtInDir(dirPath ,  list):
    fileNames = []
    for dir  in os.walk(dirPath):
        for filename in dir[2]:
            sufix = os.path.splitext(filename)[1][1:]
            for ext in list:
                if ext == sufix :
                    fullFilePath = dir[0] + "\\" + filename
                    fileNames.append(fullFilePath);
    return fileNames;


def FilesLastModifyTime(fileNames):
    filesModifyTime = {}
    for file in fileNames:
        statinfo=os.stat(file)
        statinfo.st_mtime
        filesModifyTime[file] = statinfo.st_mtime
    return filesModifyTime
    
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
