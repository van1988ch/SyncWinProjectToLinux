SyncWinProjectToLinux
====
## 描述:
- 项目开发语言PYTHON。
- 项目功能在windows下面写代码，自动增量同步到linux机器上面，同时执行远程执行shell命令。
- 配合cmake，和make自动生成二进制代码。
- 自动目录生成

## 配置:
  配置文件可以可以指定多套.然后通过命令行来指定使用哪个配置文件来同步到不同的服务器
```
[global]
#远程服务器地址和端口
Server=192.168.1.5
ServerPort=22
#远程服务器账号密码
Username = ******
Passwd = ******
#本地项目根目录
ProjectRoot = /Users/****/Desktop/project
#远程LINUX项目目录
RemoteRoot = /home/****/Project2/
#默认同步项目名称(可以通过传参来指定)
ProjectName = *****
#需要同步的文件后缀
SyncFileExt=cpp,h,txt,c,xml,a,jar,class,c,cc
#指定cmake文件,或者是指定的bash 命令
CMakeListFileName = CMakeLists.txt
#文件更新后需要跳转到cmake的目录
ShellCMD=cd /home/*****/Project2/?/src
```

## 命令行:
python SyncWinProjectToLinux.py config.ini xxx
config.ini指定的配置文件上传到那个服务器
xxx 指定的配置文件ProjectRoot目录项目的项目目录

